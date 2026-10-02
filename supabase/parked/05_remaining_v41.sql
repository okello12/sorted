-- The rest of the v37 audit (2 October 2026): helper protections, tidy-ups and idle-account deletion.
-- Chosen by Baldwin; paste into the Supabase SQL editor (project boxrwcuhxmimayaxzywu) and run as one script.
-- Release v41 already tells people about the stop list and idle-account deletion, so the notice is not behind this.
-- Safe to run more than once. It reads no case content. It deletes the 9 unused forwarding addresses (forwarding has
-- been off since v28) and schedules two clean-up jobs.

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

-- 3. Shares: changing a share also checks the case is yours
alter policy "own shares: change" on public.shares
  with check ((user_id = (select auth.uid())) and exists (select 1 from public.tasks t where t.id = shares.task_id and t.user_id = (select auth.uid())));

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
