-- Audit fixes, 1 October 2026 (release v37). NOT YET APPLIED: cancelled at the approval step on 1 Oct 2026. Apply when ready (see docs/LATER.md, "Backend fixes waiting for approval").

-- 1. Helper invites: one log per invite (not per case), a lasting "they said stop", owner and email account required
create table if not exists public.helper_invite_log(id bigserial primary key, user_id uuid not null references auth.users(id) on delete cascade, at timestamptz not null default now());
create index if not exists helper_invite_log_user_at on public.helper_invite_log(user_id, at);
create table if not exists public.helper_suppress(email_sha text primary key, at timestamptz not null default now());
alter table public.helper_invite_log enable row level security;
alter table public.helper_suppress enable row level security;
revoke all on public.helper_invite_log, public.helper_suppress from anon, authenticated;

create or replace function public.invite_helper(p_task_id text, p_email text, p_name text)
returns text language plpgsql security definer set search_path to ''
as $function$
declare uid uuid := auth.uid(); em text := lower(btrim(p_email)); nm text := btrim(p_name); cur public.helpers;
begin
  if uid is null then raise exception 'not signed in'; end if;
  if coalesce((auth.jwt()->>'is_anonymous')::boolean, false) then raise exception 'add your email first'; end if;
  if not exists (select 1 from public.tasks t where t.id = p_task_id and t.user_id = uid) then raise exception 'not your case'; end if;
  if not exists (select 1 from public.shares s where s.task_id = p_task_id and s.user_id = uid) then raise exception 'share the task first'; end if;
  if em !~ '^[^\s@]+@[^\s@]+\.[^\s@]+$' or char_length(em) > 254 then raise exception 'bad email'; end if;
  if nm = '' or char_length(nm) > 40 or nm ~ '[@/<>:]|https?|www\.|\.[a-z]{2,}' then raise exception 'bad name'; end if;
  if exists (select 1 from public.helper_suppress where email_sha = encode(extensions.digest(em, 'sha256'), 'hex')) then raise exception 'they said stop'; end if;
  select * into cur from public.helpers h where h.task_id = p_task_id;
  if found and cur.email = em and cur.status in ('pending','confirmed') then return cur.status; end if;
  if found and cur.email = em and cur.status = 'stopped' then raise exception 'they said stop'; end if;
  if (select count(*) from public.helper_invite_log where user_id = uid and at > now() - interval '1 day') >= 5 then raise exception 'too many invites today'; end if;
  insert into public.helper_invite_log(user_id) values (uid);
  insert into public.helpers (task_id, user_id, email, inviter_name, status, token, invited_at)
  values (p_task_id, uid, em, nm, 'pending', encode(extensions.gen_random_bytes(24), 'hex'), now())
  on conflict (task_id) do update set email = excluded.email, inviter_name = excluded.inviter_name, status = 'pending',
    token = excluded.token, invited_at = now(), invite_sent_at = null, confirmed_at = null, stopped_at = null;
  perform public.sorted_kick_reminders();
  return 'pending';
end $function$;

create or replace function public.helper_respond(p_token text, p_action text)
returns text language plpgsql security definer set search_path to ''
as $function$
declare r public.helpers;
begin
  if p_token is null or char_length(p_token) < 40 then return 'unknown'; end if;
  select * into r from public.helpers where token = p_token;
  if not found then return 'unknown'; end if;
  if p_action = 'yes' and r.status = 'pending' then
    update public.helpers set status = 'confirmed', confirmed_at = now() where token = p_token; return 'confirmed';
  elsif p_action = 'stop' then
    update public.helpers set status = 'stopped', stopped_at = now() where token = p_token;
    insert into public.helper_suppress(email_sha) values (encode(extensions.digest(r.email, 'sha256'), 'hex')) on conflict do nothing;
    return 'stopped';
  end if;
  return r.status;
end $function$;

-- 2. Reminders: a cap per case and per day, a sane send time, and rows claimed before sending (no double emails)
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

-- 3. Shares: changing a share also checks the case is yours
alter policy "own shares: change" on public.shares
  with check ((user_id = (select auth.uid())) and exists (select 1 from public.tasks t where t.id = shares.task_id and t.user_id = (select auth.uid())));

-- 4. Retention can't be broken by one malformed date
create or replace function public.try_ts(t text) returns timestamptz language plpgsql stable set search_path to '' as $$
begin return t::timestamptz; exception when others then return null; end $$;
revoke execute on function public.try_ts(text) from public, anon, authenticated;
create or replace function public.sorted_case_live(d jsonb) returns boolean language sql stable set search_path to '' as $$
  select exists (
    select 1 from jsonb_array_elements(case when jsonb_typeof(d->'promises') = 'array' then d->'promises' else '[]'::jsonb end) p
    where p->>'status' = 'open'
      and ( (p->>'dueAt' is not null and coalesce(public.try_ts(p->>'dueAt'), now() - interval '31 days') > now() - interval '30 days')
         or (p->>'dueAt' is null and coalesce(public.try_ts(p->>'loggedAt'), now() - interval '31 days') > now() - interval '30 days') ))
$$;

-- 5. Forwarding is off: stop handing out forwarding addresses and remove the ones made
revoke execute on function public.my_inbound_address() from authenticated;
delete from public.inbound_addresses;

-- 6. Narrower grants (row level security still applies on top)
revoke truncate, trigger, references on public.tasks, public.shares, public.reminders, public.inbound_items from anon, authenticated;
revoke all on public.tasks, public.shares, public.reminders, public.inbound_items from anon;
revoke insert, update on public.inbound_items from authenticated;
grant update (used_at) on public.inbound_items to authenticated;
revoke execute on all functions in schema net from anon, authenticated;
revoke usage on schema net from anon, authenticated;

-- 7. Abuse limits: step records per hour, case size, auth error reports per kind
create or replace function public.pilot_events_cap() returns trigger language plpgsql security definer set search_path to '' as $$
begin
  if (select count(*) from public.pilot_events where actor = new.actor and at > now() - interval '1 hour') >= 200 then return null; end if;
  return new;
end $$;
revoke execute on function public.pilot_events_cap() from public, anon, authenticated;
drop trigger if exists pilot_events_cap on public.pilot_events;
create trigger pilot_events_cap before insert on public.pilot_events for each row execute function public.pilot_events_cap();
alter table public.tasks drop constraint if exists tasks_data_size;
alter table public.tasks add constraint tasks_data_size check (pg_column_size(data) <= 100000) not valid;
alter table public.tasks validate constraint tasks_data_size;
create or replace function public.report_auth_error(p_kind text) returns void language plpgsql security definer set search_path to '' as $function$
begin
  if p_kind not in ('link_expired','link_invalid','send_failed','code_failed','anon_failed','anon_slow') then return; end if;
  if (select count(*) from public.ops_errors where source = 'auth' and kind = p_kind and at > now() - interval '1 hour') >= 100 then return; end if;
  insert into public.ops_errors(source, kind) values ('auth', p_kind);
end $function$;

-- 8. Speed: evaluate auth.uid() once per query; index foreign keys
alter policy "own reminders select" on public.reminders using (user_id = (select auth.uid()));
alter policy "own reminders delete" on public.reminders using (user_id = (select auth.uid()));
alter policy "own reminders insert" on public.reminders with check ((user_id = (select auth.uid())) and exists (select 1 from public.tasks t where t.id = reminders.task_id and t.user_id = (select auth.uid())));
alter policy pilot_events_insert on public.pilot_events with check (actor = (select auth.uid()));
create index if not exists helpers_user_idx on public.helpers(user_id);
create index if not exists reminders_user_idx on public.reminders(user_id);

-- 9. Clean-up: expired carry tokens daily; accounts with an email, no cases and no sign-in for 12 months
select cron.schedule('pilot-carry-cleanup', '57 3 * * *', $$delete from public.pilot_carry where created < now() - interval '1 day'$$);
select cron.schedule('sorted-idle-accounts', '7 4 * * *', $$
  delete from auth.users u
  where not coalesce(u.is_anonymous, false)
    and coalesce(u.last_sign_in_at, u.created_at) < now() - interval '12 months'
    and not exists (select 1 from public.tasks t where t.user_id = u.id)
    and lower(coalesce(u.email, '')) not in (select lower(email) from public.pilot_admins)
$$);
