-- Sorted staging: the whole database structure, taken from the live project's catalogue on 4 October 2026 (after
-- migration 13). Structure only: no rows, no secrets. Apply to an empty Supabase project, then:
--   1. enable anonymous sign-in and email sign-in in Authentication settings (not possible from SQL);
--   2. add Vault secrets only if you want reminders or the assistant on staging (they are off without them);
--   3. deploy the edge functions if you need them (the live suite in tests/live does not).
-- Parts of this file that delete rows (six functions, one trigger, the retention jobs) are repeated in 01_run_by_hand.sql,
-- because Supabase's tooling asks a person to confirm deleting statements. On 4 October 2026 everything except those was
-- applied to ujwanxqrefziuxwfzeaj through the Supabase API; 01_run_by_hand.sql is still to run.
-- The one deliberate difference from live: sorted_kick_reminders() calls this project's own send-reminders URL,
-- set by the STAGING_REF placeholder below. Everything else is the same as live.

create extension if not exists pgcrypto with schema extensions;
create extension if not exists "uuid-ossp" with schema extensions;
create extension if not exists pg_net;
create extension if not exists pg_cron;
create extension if not exists supabase_vault;

-- Tables -------------------------------------------------------------------------------------------------------------

create table public.tasks (
  id text primary key check (char_length(id) >= 8 and char_length(id) <= 64),
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  data jsonb not null check (pg_column_size(data) <= 100000),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index tasks_user_idx on public.tasks (user_id);

create table public.shares (
  token text primary key check (char_length(token) >= 24),
  task_id text not null unique references public.tasks(id) on delete cascade,
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  card jsonb not null,
  updated_at timestamptz not null default now(),
  notes_on boolean not null default false
);
create index shares_user_idx on public.shares (user_id);

create table public.reminders (
  id uuid primary key default gen_random_uuid(),
  task_id text not null references public.tasks(id) on delete cascade,
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  kind text not null check (kind = any (array['before','after','start'])),
  send_at timestamptz not null,
  promise_id text,
  sent_at timestamptz,
  cancelled_at timestamptz,
  created_at timestamptz not null default now(),
  cancel_reason text,
  provider_id text,
  helper_sent_at timestamptz,
  claimed_at timestamptz,
  unique (task_id, kind, send_at)
);
create index reminders_due_idx on public.reminders (send_at) where sent_at is null and cancelled_at is null;
create index reminders_user_idx on public.reminders (user_id);

create table public.helpers (
  task_id text primary key references public.tasks(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  email text not null check (char_length(email) >= 5 and char_length(email) <= 254),
  inviter_name text not null check (char_length(inviter_name) >= 1 and char_length(inviter_name) <= 40),
  status text not null default 'pending' check (status = any (array['pending','confirmed','stopped'])),
  token text not null unique,
  invited_at timestamptz not null default now(),
  invite_sent_at timestamptz,
  confirmed_at timestamptz,
  stopped_at timestamptz
);
create index helpers_user_idx on public.helpers (user_id);

create table public.inbound_addresses (
  user_id uuid primary key references auth.users(id) on delete cascade,
  token text not null unique,
  created_at timestamptz not null default now()
);

create table public.inbound_items (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  subject text,
  body text,
  received_at timestamptz not null default now(),
  used_at timestamptz,
  task_id text references public.tasks(id) on delete cascade,
  from_domain text
);
create index inbound_items_task_idx on public.inbound_items (task_id) where task_id is not null;
create index inbound_items_user on public.inbound_items (user_id, received_at desc);

create table public.email_optouts (
  user_id uuid primary key references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);

create table public.pilot_events (
  id bigint generated always as identity primary key,
  actor uuid not null default auth.uid(),
  name text not null check (name = any (array['case_started','baseline_action_recorded','promise_created','email_added_at_promise','promise_due_return','outcome_kept','outcome_missed','outcome_rescheduled','chase_used','new_promise_after_miss','case_closed','recap_copied','second_case_started','moment_created','moment_item','moment_opened','turn_recorded','goal_recorded','document_read_started','document_read_succeeded','document_read_partial','document_read_failed','document_review_confirmed','document_manual_fallback'])),
  case_id text check (char_length(case_id) <= 40),
  promise_id text check (char_length(promise_id) <= 40),
  props jsonb not null default '{}'::jsonb check (pg_column_size(props) <= 1000),
  at timestamptz not null default now()
);
create index pilot_events_actor on public.pilot_events (actor, at);
create index pilot_events_case on public.pilot_events (case_id);

create table public.pilot_admins (email text primary key);

create table public.pilot_carry (
  token text primary key,
  anon_uid uuid not null,
  created timestamptz not null default now()
);

create table public.ops_errors (
  id bigint generated always as identity primary key,
  source text not null check (source = any (array['auth','inbound','assistant','scores','page','save','reminder','share'])),
  kind text not null check (char_length(kind) <= 40),
  at timestamptz not null default now(),
  detail text check (detail is null or char_length(detail) <= 200),
  build text check (build is null or char_length(build) <= 60)
);
create index ops_errors_at on public.ops_errors (source, at desc);

create table public.helper_invite_log (
  id bigserial primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  at timestamptz not null default now()
);
create index helper_invite_log_user_at on public.helper_invite_log (user_id, at);

create table public.helper_suppress (
  email_sha text primary key,
  at timestamptz not null default now()
);

create table public.assistant_usage (
  user_id uuid not null references auth.users(id) on delete cascade,
  day date not null default current_date,
  n integer not null default 0,
  primary key (user_id, day)
);

create table public.promise_outcomes (
  id bigserial primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  promise_id text not null check (char_length(promise_id) <= 40),
  party text not null check (party = any (array['Currys','Amazon','Argos','John Lewis','AO','eBay','IKEA','Apple','Samsung','Dyson','Boots','Tesco','Sainsbury’s','Asda','BT','Virgin Media','Sky','EE','O2','Vodafone','British Gas','Octopus Energy','OVO','EDF','E.ON','Thames Water','Royal Mail','Evri','DPD','DHL','Ryanair','easyJet','HMRC','DVLA'])),
  outcome text not null check (outcome = any (array['kept','missed'])),
  via text check (via is null or via = any (array['phone','email','account','letter','app'])),
  at timestamptz not null default now(),
  unique (user_id, promise_id)
);

create table public.case_mail (
  task_id text primary key references public.tasks(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  token text not null unique,
  created_at timestamptz not null default now()
);

create table public.case_notes (
  id uuid primary key default gen_random_uuid(),
  task_id text not null references public.tasks(id) on delete cascade,
  author text not null check (char_length(author) >= 1 and char_length(author) <= 40),
  body text not null check (char_length(body) >= 1 and char_length(body) <= 1000),
  created_at timestamptz not null default now()
);
create index case_notes_task_idx on public.case_notes (task_id);

create table public.share_opens (
  task_id text primary key references public.tasks(id) on delete cascade,
  opens integer not null default 0,
  open_days integer not null default 0,
  first_at timestamptz,
  last_at timestamptz
);

-- Row level security on every table -------------------------------------------------------------------------------

alter table public.tasks enable row level security;
alter table public.shares enable row level security;
alter table public.reminders enable row level security;
alter table public.helpers enable row level security;
alter table public.inbound_addresses enable row level security;
alter table public.inbound_items enable row level security;
alter table public.email_optouts enable row level security;
alter table public.pilot_events enable row level security;
alter table public.pilot_admins enable row level security;
alter table public.pilot_carry enable row level security;
alter table public.ops_errors enable row level security;
alter table public.helper_invite_log enable row level security;
alter table public.helper_suppress enable row level security;
alter table public.assistant_usage enable row level security;
alter table public.promise_outcomes enable row level security;
alter table public.case_mail enable row level security;
alter table public.case_notes enable row level security;
alter table public.share_opens enable row level security;

create policy "own tasks: read" on public.tasks for select to authenticated using (user_id = (select auth.uid()));
create policy "own tasks: add" on public.tasks for insert to authenticated with check (user_id = (select auth.uid()));
create policy "own tasks: change" on public.tasks for update to authenticated using (user_id = (select auth.uid())) with check (user_id = (select auth.uid()));
create policy "own tasks: delete" on public.tasks for delete to authenticated using (user_id = (select auth.uid()));

create policy "own shares: read" on public.shares for select to authenticated using (user_id = (select auth.uid()));
create policy "own shares: add" on public.shares for insert to authenticated with check (user_id = (select auth.uid()) and exists (select 1 from public.tasks t where t.id = shares.task_id and t.user_id = (select auth.uid())));
create policy "own shares: change" on public.shares for update to authenticated using (user_id = (select auth.uid())) with check (user_id = (select auth.uid()) and exists (select 1 from public.tasks t where t.id = shares.task_id and t.user_id = (select auth.uid())));
create policy "own shares: delete" on public.shares for delete to authenticated using (user_id = (select auth.uid()));

create policy "own reminders select" on public.reminders for select to authenticated using (user_id = (select auth.uid()));
create policy "own reminders insert" on public.reminders for insert to authenticated with check (user_id = (select auth.uid()) and exists (select 1 from public.tasks t where t.id = reminders.task_id and t.user_id = (select auth.uid())));
create policy "own reminders delete" on public.reminders for delete to authenticated using (user_id = (select auth.uid()));

create policy "own helpers: read" on public.helpers for select to authenticated using (user_id = (select auth.uid()));

create policy "own inbound: read" on public.inbound_items for select to authenticated using (user_id = (select auth.uid()));
create policy "own inbound: mark" on public.inbound_items for update to authenticated using (user_id = (select auth.uid())) with check (user_id = (select auth.uid()));
create policy "own inbound: delete" on public.inbound_items for delete to authenticated using (user_id = (select auth.uid()));

create policy "own optout: read" on public.email_optouts for select to authenticated using (user_id = (select auth.uid()));

create policy pilot_events_insert on public.pilot_events for insert to authenticated with check (actor = (select auth.uid()));

create policy case_mail_own_read on public.case_mail for select to authenticated using (user_id = (select auth.uid()));

create policy case_notes_owner_read on public.case_notes for select to authenticated using (exists (select 1 from public.tasks t where t.id = case_notes.task_id and t.user_id = (select auth.uid())));
create policy case_notes_owner_delete on public.case_notes for delete to authenticated using (exists (select 1 from public.tasks t where t.id = case_notes.task_id and t.user_id = (select auth.uid())));

-- Grants (RLS does the real work; these are the least the page needs) ----------------------------------------------

revoke all on all tables in schema public from anon, authenticated;
grant select, insert, update, delete on public.tasks to authenticated;
grant select, insert, update, delete on public.shares to authenticated;
grant select, insert, update, delete on public.reminders to authenticated;
grant select, delete on public.inbound_items to authenticated;
grant select on public.email_optouts to authenticated;
grant insert on public.pilot_events to authenticated;
grant select on public.helpers to authenticated;
grant select on public.case_mail to authenticated;
grant select, delete on public.case_notes to authenticated;
grant usage on all sequences in schema public to authenticated;
grant all on all tables in schema public to service_role;
grant usage, select on all sequences in schema public to service_role;

-- Functions ---------------------------------------------------------------------------------------------------------

create or replace function public.touch_updated_at() returns trigger language plpgsql set search_path to '' as $$
begin new.updated_at := now(); return new; end $$;

create or replace function public.try_ts(t text) returns timestamptz language plpgsql stable set search_path to '' as $$
begin return t::timestamptz; exception when others then return null; end $$;

create or replace function public.sorted_case_live(d jsonb) returns boolean language sql stable set search_path to '' as $$
  select exists (
    select 1 from jsonb_array_elements(case when jsonb_typeof(d->'promises') = 'array' then d->'promises' else '[]'::jsonb end) p
    where jsonb_typeof(p) = 'object' and p->>'status' = 'open'
      and ( (p->>'dueAt' is not null and coalesce(public.try_ts(p->>'dueAt'), now() - interval '31 days') > now() - interval '30 days')
         or (p->>'dueAt' is null and coalesce(public.try_ts(p->>'loggedAt'), now() - interval '31 days') > now() - interval '30 days') ))
$$;

create or replace function public.is_pilot_admin() returns boolean language sql stable security definer set search_path to '' as $$
  select exists(select 1 from public.pilot_admins a where lower(a.email)=lower(coalesce(auth.jwt()->>'email','')) and coalesce(auth.jwt()->>'email','')<>'');
$$;

create or replace function public.sorted_secret(p_name text) returns text language sql security definer set search_path to '' as $$
  select decrypted_secret from vault.decrypted_secrets where name = p_name limit 1
$$;

create or replace function public.email_reminders_ready() returns boolean language sql stable security definer set search_path to '' as $$
  select exists (select 1 from vault.decrypted_secrets where name = 'resend_api_key' and coalesce(decrypted_secret,'') <> '')
     and exists (select 1 from vault.decrypted_secrets where name = 'reminder_from' and coalesce(decrypted_secret,'') like '%@%')
$$;

create or replace function public.sorted_kick_reminders() returns bigint language sql security definer set search_path to '' as $$
  select net.http_post(
    url := 'https://STAGING_REF.supabase.co/functions/v1/send-reminders',
    headers := jsonb_build_object('Content-Type','application/json','x-cron-secret',(select decrypted_secret from vault.decrypted_secrets where name='sorted_cron_secret')),
    body := '{}'::jsonb,
    timeout_milliseconds := 20000)
$$;

create or replace function public.pilot_events_cap() returns trigger language plpgsql security definer set search_path to '' as $$
begin
  if (select count(*) from public.pilot_events where actor = new.actor and at > now() - interval '1 hour') >= 200 then return null; end if;
  return new;
end $$;

create or replace function public.reminders_cap() returns trigger language plpgsql security definer set search_path to '' as $$
begin
  if (select count(*) from public.reminders where task_id = new.task_id and sent_at is null and cancelled_at is null) >= 12 then raise exception 'too many reminders'; end if;
  if (select count(*) from public.reminders where user_id = new.user_id and created_at > now() - interval '1 day') >= 80 then raise exception 'too many reminders today'; end if;
  if new.send_at > now() + interval '400 days' then raise exception 'bad time'; end if;
  return new;
end $$;

create or replace function public.shares_drop_helper() returns trigger language plpgsql security definer set search_path to '' as $$
begin delete from public.helpers where task_id = old.task_id; return old; end $$;

create or replace function public.get_share(p_token text) returns table(card jsonb, updated_at timestamptz) language sql stable security definer set search_path to '' as $$
  select s.card, s.updated_at from public.shares s
  where s.token = p_token and char_length(p_token) >= 24 and s.updated_at > now() - interval '30 days';
$$;

create or replace function public.share_seen(p_token text) returns void language plpgsql security definer set search_path to '' as $$
declare tid text;
begin
  if p_token is null or char_length(p_token) < 24 then return; end if;
  select s.task_id into tid from public.shares s where s.token = p_token and s.updated_at > now() - interval '30 days';
  if tid is null then return; end if;
  insert into public.share_opens as o (task_id, opens, open_days, first_at, last_at) values (tid, 1, 1, now(), now())
  on conflict (task_id) do update set opens = o.opens + 1,
    open_days = o.open_days + case when (o.last_at at time zone 'Europe/London')::date < (now() at time zone 'Europe/London')::date then 1 else 0 end,
    last_at = now();
end $$;

create or replace function public.delete_my_account() returns void language plpgsql security definer set search_path to '' as $$
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  delete from public.pilot_events where actor = auth.uid();
  delete from auth.users where id = auth.uid();
end $$;

create or replace function public.stash_carry() returns text language plpgsql security definer set search_path to '' as $$
declare tok text;
begin
  if auth.uid() is null or coalesce((auth.jwt()->>'is_anonymous')::boolean,false) is not true then return null; end if;
  delete from public.pilot_carry where created < now() - interval '1 day' or anon_uid = auth.uid();
  tok := encode(extensions.gen_random_bytes(24),'hex');
  insert into public.pilot_carry(token, anon_uid) values (tok, auth.uid());
  return tok;
end $$;

create or replace function public.claim_carry(p_token text, p_pairs jsonb default '[]'::jsonb) returns boolean language plpgsql security definer set search_path to '' as $$
declare a uuid; pr jsonb;
begin
  if auth.uid() is null or coalesce((auth.jwt()->>'is_anonymous')::boolean,false) then return false; end if;
  delete from public.pilot_carry where token = p_token and created > now() - interval '1 day' returning anon_uid into a;
  if a is null or a = auth.uid() then return false; end if;
  if jsonb_typeof(p_pairs) = 'array' then
    for pr in select * from jsonb_array_elements(p_pairs) limit 200 loop
      update public.pilot_events set case_id = pr->>1 where actor = a and case_id = pr->>0 and char_length(pr->>1) <= 40;
    end loop;
  end if;
  update public.pilot_events set actor = auth.uid() where actor = a;
  delete from auth.users where id = a and is_anonymous;
  return true;
end $$;

create or replace function public.report_auth_error(p_kind text) returns void language plpgsql security definer set search_path to '' as $$
begin
  if p_kind not in ('link_expired','link_invalid','send_failed','code_failed','anon_failed','anon_slow') then return; end if;
  if (select count(*) from public.ops_errors where source = 'auth' and kind = p_kind and at > now() - interval '1 hour') >= 100 then return; end if;
  insert into public.ops_errors(source, kind) values ('auth', p_kind);
end $$;

create or replace function public.report_page_error(p_source text, p_kind text, p_detail text, p_build text) returns void language plpgsql security definer set search_path to '' as $$
begin
  if p_source is null or p_source not in ('page','save','reminder','share') then return; end if;
  if (select count(*) from public.ops_errors where source in ('page','save','reminder','share') and at > now() - interval '1 hour') >= 300 then return; end if;
  insert into public.ops_errors(source, kind, detail, build)
    values (p_source, left(coalesce(p_kind,'error'), 40), left(coalesce(p_detail,''), 200), left(coalesce(p_build,''), 60));
end $$;

create or replace function public.claim_due_reminders(p_limit integer default 50) returns setof public.reminders language sql security definer set search_path to '' as $$
  update public.reminders set claimed_at = now()
  where id in (select id from public.reminders
               where sent_at is null and cancelled_at is null
                 and (claimed_at is null or claimed_at < now() - interval '5 minutes')
                 and send_at between now() - interval '30 minutes' and now()
               order by send_at limit p_limit for update skip locked)
  returning *;
$$;

create or replace function public.claim_helper_invites(p_limit integer default 20) returns setof public.helpers language sql security definer set search_path to '' as $$
  update public.helpers set invite_sent_at = now()
  where task_id in (select task_id from public.helpers
                    where status = 'pending' and invite_sent_at is null and invited_at > now() - interval '1 day'
                    limit p_limit for update skip locked)
  returning *;
$$;

create or replace function public.helper_respond(p_token text, p_action text) returns text language plpgsql security definer set search_path to '' as $$
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
end $$;

create or replace function public.invite_helper(p_task_id text, p_email text, p_name text) returns text language plpgsql security definer set search_path to '' as $$
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
end $$;

create or replace function public.remove_helper(p_task_id text) returns void language sql security definer set search_path to '' as $$
  delete from public.helpers where task_id = p_task_id and user_id = auth.uid();
$$;

create or replace function public.my_inbound_address() returns text language plpgsql security definer set search_path to '' as $$
declare uid uuid := auth.uid(); dom text; tok text;
begin
  if uid is null then return null; end if;
  select decrypted_secret into dom from vault.decrypted_secrets where name = 'inbound_domain';
  if coalesce(dom,'') = '' or not exists (select 1 from vault.decrypted_secrets where name = 'resend_webhook_secret' and coalesce(decrypted_secret,'') <> '') then return null; end if;
  select token into tok from public.inbound_addresses where user_id = uid;
  if tok is null then
    tok := 'log-' || encode(extensions.gen_random_bytes(8), 'hex');
    insert into public.inbound_addresses(user_id, token) values (uid, tok) on conflict (user_id) do nothing;
    select token into tok from public.inbound_addresses where user_id = uid;
  end if;
  return tok || '@' || dom;
end $$;

create or replace function public.case_reply_address(p_task_id text) returns text language plpgsql security definer set search_path to '' as $$
declare uid uuid := auth.uid(); dom text; tok text; onv text;
begin
  if uid is null or p_task_id is null then return null; end if;
  select decrypted_secret into onv from vault.decrypted_secrets where name = 'case_replies_on';
  if coalesce(onv,'') <> 'yes' then return null; end if;
  select decrypted_secret into dom from vault.decrypted_secrets where name = 'inbound_domain';
  if coalesce(dom,'') = '' then return null; end if;
  if not exists (select 1 from public.tasks where id = p_task_id and user_id = uid) then return null; end if;
  select token into tok from public.case_mail where task_id = p_task_id;
  if tok is null then
    tok := 'case-' || encode(extensions.gen_random_bytes(10), 'hex');
    insert into public.case_mail(task_id, user_id, token) values (p_task_id, uid, tok) on conflict (task_id) do nothing;
    select token into tok from public.case_mail where task_id = p_task_id;
  end if;
  return tok || '@' || dom;
end $$;

create or replace function public.add_share_note(p_token text, p_author text, p_body text) returns text language plpgsql security definer set search_path to 'public' as $$
declare s record; n int;
begin
  select token, task_id, notes_on, updated_at into s from public.shares where token = p_token;
  if s.token is null or s.updated_at < now() - interval '30 days' then return 'gone'; end if;
  if not s.notes_on then return 'off'; end if;
  if char_length(trim(coalesce(p_author,''))) = 0 or char_length(trim(coalesce(p_body,''))) = 0 then return 'empty'; end if;
  select count(*) into n from public.case_notes where task_id = s.task_id and created_at > now() - interval '1 day';
  if n >= 10 then return 'limit'; end if;
  insert into public.case_notes(task_id, author, body) values (s.task_id, left(trim(p_author), 40), left(trim(p_body), 1000));
  return 'ok';
end $$;

create or replace function public.assistant_take(p_user uuid, p_limit integer) returns boolean language plpgsql security definer set search_path to 'public' as $$
declare v int;
begin
  insert into public.assistant_usage(user_id, day, n) values (p_user, current_date, 1)
  on conflict (user_id, day) do update set n = public.assistant_usage.n + 1
  returning n into v;
  return v <= p_limit;
end $$;

create or replace function public.record_outcome(p_promise text, p_party text, p_outcome text, p_via text) returns void language plpgsql security definer set search_path to 'public' as $$
begin
  if auth.uid() is null then return; end if;
  insert into public.promise_outcomes(user_id, promise_id, party, outcome, via)
  values (auth.uid(), left(p_promise, 40), p_party, p_outcome, nullif(p_via, ''))
  on conflict (user_id, promise_id) do update set outcome = excluded.outcome, via = excluded.via, at = now();
exception when check_violation then return;
end $$;

create or replace function public.drop_outcome(p_promise text) returns void language sql security definer set search_path to 'public' as $$
  delete from public.promise_outcomes where user_id = auth.uid() and promise_id = left(p_promise, 40);
$$;

create or replace function public.company_scores() returns table(party text, kept integer, missed integer, people integer, by_via jsonb) language sql stable security definer set search_path to 'public' as $$
  with o as (select * from public.promise_outcomes where at > now() - interval '12 months'),
  t as (select o.party, count(*) filter (where outcome = 'kept')::int kept, count(*) filter (where outcome = 'missed')::int missed, count(distinct user_id)::int people from o group by o.party),
  v as (select x.party, jsonb_object_agg(x.via, jsonb_build_object('kept', x.k, 'n', x.n)) by_via
        from (select o.party, o.via, count(*) filter (where o.outcome = 'kept')::int k, count(*)::int n from o where o.via is not null group by o.party, o.via having count(*) >= 5) x
        group by x.party)
  select t.party, t.kept, t.missed, t.people, coalesce(v.by_via, '{}'::jsonb)
  from t left join v using (party)
  where t.kept + t.missed >= 5 and t.people >= 3;
$$;

create or replace function public.pilot_health() returns jsonb language plpgsql stable security definer set search_path to '' as $$
declare j jsonb; rjob record; other text[]; http record;
begin
  if not public.is_pilot_admin() then raise exception 'not allowed'; end if;
  select d.start_time, d.status into rjob from cron.job_run_details d join cron.job c on c.jobid=d.jobid
    where c.jobname='sorted-send-reminders' order by d.start_time desc limit 1;
  select array_agg(c.jobname) into other from cron.job c
    where c.active and c.jobname <> 'sorted-send-reminders'
      and (select d.status from cron.job_run_details d where d.jobid=c.jobid order by d.start_time desc limit 1) not in ('succeeded','running','starting');
  select r.status_code, r.created, r.timed_out,
    (r.content like '%"skipped"%' or r.content like '%"error"%') as bad_body
    into http from net._http_response r where r.content like '%"stale"%' order by r.created desc limit 1;
  j := jsonb_build_object(
    'now', now(),
    'scheduler', jsonb_build_object('last_run', rjob.start_time, 'last_status', rjob.status,
       'http_status', http.status_code, 'http_at', http.created, 'http_timed_out', coalesce(http.timed_out,false),
       'http_bad', coalesce(http.bad_body,false), 'daily_failed', coalesce(to_jsonb(other), '[]'::jsonb)),
    'reminders', (select jsonb_build_object(
       'overdue', count(*) filter (where sent_at is null and cancelled_at is null and send_at < now() - interval '15 minutes'),
       'failed_7d', count(*) filter (where (cancel_reason like 'send failed%' or cancel_reason = 'stale') and coalesce(cancelled_at, send_at) > now() - interval '7 days'),
       'last_failed', max(coalesce(cancelled_at, send_at)) filter (where cancel_reason like 'send failed%' or cancel_reason = 'stale'),
       'sent_7d', count(*) filter (where sent_at > now() - interval '7 days')) from public.reminders),
    'auth', (select jsonb_build_object('count_7d', count(*) filter (where at > now()-interval '7 days'), 'last', max(at),
       'system_24h', count(*) filter (where at > now()-interval '24 hours' and kind in ('send_failed','anon_failed','anon_slow')),
       'user_24h', count(*) filter (where at > now()-interval '24 hours' and kind in ('link_expired','link_invalid','code_failed')),
       'kinds', coalesce((select jsonb_object_agg(k, n) from (select kind k, count(*) n from public.ops_errors where source='auth' and at > now()-interval '7 days' group by kind) x), '{}'::jsonb))
       from public.ops_errors where source='auth'),
    'inbound', (select jsonb_build_object('count_7d', count(*) filter (where at > now()-interval '7 days'), 'last', max(at),
       'system_24h', count(*) filter (where at > now()-interval '24 hours' and kind in ('no_secret','fetch_failed','store_failed','exception')),
       'kinds', coalesce((select jsonb_object_agg(k, n) from (select kind k, count(*) n from public.ops_errors where source='inbound' and at > now()-interval '7 days' group by kind) x), '{}'::jsonb),
       'last_stored', (select max(received_at) from public.inbound_items))
       from public.ops_errors where source='inbound'),
    'page', (select jsonb_build_object('count_24h', count(*) filter (where at > now()-interval '24 hours'), 'count_7d', count(*) filter (where at > now()-interval '7 days'), 'last', max(at),
       'kinds', coalesce((select jsonb_object_agg(k, n) from (select source||' '||kind k, count(*) n from public.ops_errors where source in ('page','save','reminder','share') and at > now()-interval '7 days' group by 1) x), '{}'::jsonb))
       from public.ops_errors where source in ('page','save','reminder','share')));
  return j;
end $$;

create or replace function public.pilot_metrics(include_admins boolean default false) returns jsonb language plpgsql stable security definer set search_path to '' as $$
declare r jsonb;
begin
  if not public.is_pilot_admin() then raise exception 'not allowed'; end if;
  with admins as (
    select u.id from auth.users u join public.pilot_admins a on lower(a.email)=lower(u.email)
  ), e as (
    select * from public.pilot_events where include_admins or actor not in (select id from admins)
  ), started as (
    select distinct case_id from e where name='case_started'
  ), promised as (
    select distinct case_id from e where name='promise_created' and case_id in (select case_id from started)
  ), pc as (
    select case_id, promise_id, (props->>'matures_at')::timestamptz as mat from e where name='promise_created' and props ? 'matures_at'
  ), matured_p as (
    select pc.* from pc where pc.mat < now() and not exists (
      select 1 from e x where x.promise_id=pc.promise_id and x.name in ('outcome_kept','outcome_missed','outcome_rescheduled') and x.at < pc.mat)
  ), matured as (select distinct case_id from matured_p),
  ret as (
    select case_id, min(at) as first_ret from e where name='promise_due_return' group by case_id
  ), returned as (select case_id, first_ret from ret where case_id in (select case_id from matured)),
  acted as (
    select distinct r.case_id from returned r join e x on x.case_id=r.case_id and x.at>=r.first_ret
      and x.name in ('outcome_kept','outcome_missed','outcome_rescheduled','chase_used','new_promise_after_miss','case_closed')
  ), closed_after as (
    select distinct a.case_id from acted a join e x on x.case_id=a.case_id and x.name='case_closed'
  ), missed as (
    select case_id, promise_id, at from e where name='outcome_missed'
  ), recovered as (
    select m.promise_id from missed m where exists(select 1 from e x where x.case_id=m.case_id and x.at>=m.at and x.name in ('chase_used','new_promise_after_miss','outcome_rescheduled'))
  ), firstclose as (
    select actor, min(at) as at from e where name='case_closed' group by actor
  ), second as (
    select f.actor from firstclose f where exists(select 1 from e x where x.actor=f.actor and x.name='case_started' and x.at>f.at)
  ), lag as (
    select extract(epoch from (r.at - m.mat))/3600.0 as h from e r join matured_p m on m.promise_id=r.promise_id where r.name='promise_due_return'
  ), anonp as (
    select count(*) filter (where name='promise_created' and (props->>'anon')::boolean) as anon_promises,
           count(*) filter (where name='email_added_at_promise') as emails_added from e
  ), counts as (
    select name, count(*) as total, count(*) filter (where at>now()-interval '7 days') as week from e group by name
  ), endings as (
    select props->>'end' as k, count(*) as n from e
    where name='case_closed' and props->>'end' in ('refunded','repaired','cancelled','other','own') group by 1
  ), mom_items as (
    select props->>'item' as item, props->>'choice' as choice, count(*) as n from e where name='moment_item' group by 1,2
  ), mom_tracked as (
    select case_id, count(*) filter (where props->>'choice' in ('case','link')) as tracked from e where name='moment_item' and coalesce(props->>'item','')<>'share' group by case_id
  ), mom_shared as (
    select distinct case_id from e where name='moment_item' and props->>'item'='share' and props->>'choice'='link'
  )
  select jsonb_build_object(
    'generated_at', now(),
    'include_admins', include_admins,
    'people', (select count(distinct actor) from e),
    'funnel', jsonb_build_object(
      'started', (select count(*) from started),
      'promised', (select count(*) from promised),
      'matured', (select count(*) from matured),
      'returned', (select count(*) from returned),
      'acted', (select count(*) from acted),
      'closed', (select count(*) from closed_after),
      'closers', (select count(*) from firstclose),
      'second', (select count(*) from second)),
    'miss', jsonb_build_object('missed', (select count(distinct promise_id) from missed), 'recovered', (select count(distinct promise_id) from recovered),
      'partly', (select count(*) from e where name='outcome_missed' and props->>'partly'='true')),
    'endings', coalesce((select jsonb_object_agg(k, n) from endings), '{}'::jsonb),
    'moments', jsonb_build_object(
      'created', (select count(*) from e where name='moment_created'),
      'people', (select count(distinct actor) from e where name='moment_created'),
      'returned', (select count(distinct case_id) from e where name='moment_opened'),
      'with_a_case', (select count(*) from mom_tracked where tracked>=1),
      'with_two_or_more', (select count(*) from mom_tracked where tracked>=2),
      'items', coalesce((select jsonb_object_agg(item, ch) from (select item, jsonb_object_agg(choice, n) as ch from mom_items group by item) z), '{}'::jsonb)),
    'sharing', jsonb_build_object(
      'moves_shared', (select count(*) from mom_shared),
      'moves_opened', (select count(*) from mom_shared m join public.share_opens o on o.task_id=m.case_id where o.opens>0),
      'moves_opened_two_days', (select count(*) from mom_shared m join public.share_opens o on o.task_id=m.case_id where o.open_days>=2),
      'links_opened', (select count(*) from public.share_opens where opens>0),
      'links_opened_two_days', (select count(*) from public.share_opens where open_days>=2)),
    'return_hours_median', (select percentile_cont(0.5) within group (order by h) from lag),
    'email', (select to_jsonb(anonp) from anonp),
    'counts', coalesce((select jsonb_object_agg(name, jsonb_build_object('total',total,'week',week)) from counts), '{}'::jsonb)
  ) into r;
  return r;
end $$;

-- Who may call what ---------------------------------------------------------------------------------------------------

revoke all on all functions in schema public from public, anon, authenticated;
grant execute on function public.get_share(text), public.share_seen(text), public.helper_respond(text,text), public.add_share_note(text,text,text), public.report_auth_error(text), public.report_page_error(text,text,text,text) to anon, authenticated;
grant execute on function public.delete_my_account(), public.stash_carry(), public.claim_carry(text,jsonb), public.invite_helper(text,text,text), public.remove_helper(text), public.email_reminders_ready(), public.is_pilot_admin(), public.pilot_metrics(boolean), public.pilot_health(), public.record_outcome(text,text,text,text), public.drop_outcome(text), public.company_scores(), public.case_reply_address(text) to authenticated;
grant execute on all functions in schema public to service_role;

-- Triggers ------------------------------------------------------------------------------------------------------------

create trigger tasks_touch before update on public.tasks for each row execute function public.touch_updated_at();
create trigger shares_touch before update on public.shares for each row execute function public.touch_updated_at();
create trigger shares_drop_helper after delete on public.shares for each row execute function public.shares_drop_helper();
create trigger pilot_events_cap before insert on public.pilot_events for each row execute function public.pilot_events_cap();
create trigger reminders_cap before insert on public.reminders for each row execute function public.reminders_cap();

-- Retention jobs (the same as live) -----------------------------------------------------------------------------------

select cron.schedule('sorted-send-reminders', '*/10 * * * *', $$select public.sorted_kick_reminders()$$);
select cron.schedule('sorted-retention-90d', '17 3 * * *', $$delete from public.tasks where updated_at < now() - interval '90 days' and not public.sorted_case_live(data)$$);
select cron.schedule('sorted-inbound-cleanup', '17 3 * * *', $$delete from public.inbound_items where received_at < now() - interval '30 days'$$);
select cron.schedule('pilot-events-retention', '17 3 * * *', $$delete from public.pilot_events where at < now() - interval '12 months'$$);
select cron.schedule('ops-errors-retention', '27 3 * * *', $$delete from public.ops_errors where at < now() - interval '90 days'$$);
select cron.schedule('sorted-anon-cleanup', '37 3 * * *', $$delete from auth.users u where u.is_anonymous and coalesce(u.last_sign_in_at, u.created_at) < now() - interval '30 days' and not exists (select 1 from public.tasks t where t.user_id = u.id and (t.updated_at > now() - interval '30 days' or public.sorted_case_live(t.data)))$$);
select cron.schedule('shares-retention', '47 3 * * *', $$delete from public.shares where updated_at < now() - interval '90 days'$$);
select cron.schedule('pilot-carry-cleanup', '57 3 * * *', $$delete from public.pilot_carry where created < now() - interval '1 day'$$);
select cron.schedule('sorted-idle-accounts', '7 4 * * *', $$delete from auth.users u where not coalesce(u.is_anonymous, false) and coalesce(u.last_sign_in_at, u.created_at) < now() - interval '12 months' and not exists (select 1 from public.tasks t where t.user_id = u.id) and lower(coalesce(u.email, '')) not in (select lower(email) from public.pilot_admins)$$);
select cron.schedule('sorted-assistant-usage', '47 4 * * *', $$delete from public.assistant_usage where day < current_date - 30$$);
select cron.schedule('sorted-outcomes-retention', '57 4 * * *', $$delete from public.promise_outcomes where at < now() - interval '12 months'$$);
select cron.schedule('sorted-notes-retention', '17 5 * * *', $$delete from public.case_notes where created_at < now() - interval '90 days'$$);
