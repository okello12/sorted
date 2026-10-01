-- Reliability fixes (2 October 2026). Chosen by Baldwin; the apply step from Claude's session came back "cancelled",
-- so this is ready to paste into the Supabase SQL editor (project boxrwcuhxmimayaxzywu) and run as one script.
-- Safe to run more than once. It changes structure only; it reads no case content.
-- After it has run, deploy send-reminders v8 (supabase/functions/send-reminders/index.v8.ts) so the claim step is used.

-- 1. One malformed date can't break the nightly retention job
create or replace function public.try_ts(t text) returns timestamptz language plpgsql stable set search_path to '' as $$
begin return t::timestamptz; exception when others then return null; end $$;
revoke execute on function public.try_ts(text) from public, anon, authenticated;
create or replace function public.sorted_case_live(d jsonb) returns boolean language sql stable set search_path to '' as $$
  select exists (
    select 1 from jsonb_array_elements(case when jsonb_typeof(d->'promises') = 'array' then d->'promises' else '[]'::jsonb end) p
    where jsonb_typeof(p) = 'object' and p->>'status' = 'open'
      and ( (p->>'dueAt' is not null and coalesce(public.try_ts(p->>'dueAt'), now() - interval '31 days') > now() - interval '30 days')
         or (p->>'dueAt' is null and coalesce(public.try_ts(p->>'loggedAt'), now() - interval '31 days') > now() - interval '30 days') ))
$$;

-- 2. Reminders are claimed before sending, so two runs can't send the same email; sensible caps
alter table public.reminders add column if not exists claimed_at timestamptz;
create or replace function public.reminders_cap() returns trigger language plpgsql security definer set search_path to '' as $$
begin
  if (select count(*) from public.reminders where task_id = new.task_id and sent_at is null and cancelled_at is null) >= 12 then raise exception 'too many reminders'; end if;
  if (select count(*) from public.reminders where user_id = new.user_id and created_at > now() - interval '1 day') >= 80 then raise exception 'too many reminders today'; end if;
  if new.send_at > now() + interval '400 days' then raise exception 'bad time'; end if;
  return new;
end $$;
revoke execute on function public.reminders_cap() from public, anon, authenticated;
drop trigger if exists reminders_cap on public.reminders;
create trigger reminders_cap before insert on public.reminders for each row execute function public.reminders_cap();

create or replace function public.claim_due_reminders(p_limit int default 50) returns setof public.reminders
language sql security definer set search_path to '' as $$
  update public.reminders set claimed_at = now()
  where id in (select id from public.reminders
               where sent_at is null and cancelled_at is null
                 and (claimed_at is null or claimed_at < now() - interval '5 minutes')
                 and send_at between now() - interval '30 minutes' and now()
               order by send_at limit p_limit for update skip locked)
  returning *;
$$;
revoke execute on function public.claim_due_reminders(int) from public, anon, authenticated;
grant execute on function public.claim_due_reminders(int) to service_role;

create or replace function public.claim_helper_invites(p_limit int default 20) returns setof public.helpers
language sql security definer set search_path to '' as $$
  update public.helpers set invite_sent_at = now()
  where task_id in (select task_id from public.helpers
                    where status = 'pending' and invite_sent_at is null and invited_at > now() - interval '1 day'
                    limit p_limit for update skip locked)
  returning *;
$$;
revoke execute on function public.claim_helper_invites(int) from public, anon, authenticated;
grant execute on function public.claim_helper_invites(int) to service_role;

-- 3. Size and rate limits
alter table public.tasks drop constraint if exists tasks_data_size;
alter table public.tasks add constraint tasks_data_size check (pg_column_size(data) <= 100000) not valid;
alter table public.tasks validate constraint tasks_data_size;
create or replace function public.pilot_events_cap() returns trigger language plpgsql security definer set search_path to '' as $$
begin
  if (select count(*) from public.pilot_events where actor = new.actor and at > now() - interval '1 hour') >= 200 then return null; end if;
  return new;
end $$;
revoke execute on function public.pilot_events_cap() from public, anon, authenticated;
drop trigger if exists pilot_events_cap on public.pilot_events;
create trigger pilot_events_cap before insert on public.pilot_events for each row execute function public.pilot_events_cap();
create or replace function public.report_auth_error(p_kind text) returns void language plpgsql security definer set search_path to '' as $function$
begin
  if p_kind not in ('link_expired','link_invalid','send_failed','code_failed','anon_failed','anon_slow') then return; end if;
  if (select count(*) from public.ops_errors where source = 'auth' and kind = p_kind and at > now() - interval '1 hour') >= 100 then return; end if;
  insert into public.ops_errors(source, kind) values ('auth', p_kind);
end $function$;
