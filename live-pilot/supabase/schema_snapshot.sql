-- Sorted pilot: database snapshot of project boxrwcuhxmimayaxzywu (Supabase, eu-west-2 London)
-- Taken 30 September 2026 from the live project. Structure only: no rows, no secrets.
-- Secrets (Resend keys, webhook secret, cron secret, sender address, inbound domain) live in Supabase Vault
-- and are read by name through public.sorted_secret(); they are never in this repository.

-- Tables (public schema)

-- email_optouts: user_id uuid, created_at timestamp with time zone
-- helpers: task_id text, user_id uuid, email text, inviter_name text, status text, token text, invited_at timestamp with time zone, invite_sent_at timestamp with time zone, confirmed_at timestamp with time zone, stopped_at timestamp with time zone
-- inbound_addresses: user_id uuid, token text, created_at timestamp with time zone
-- inbound_items: id uuid, user_id uuid, subject text, body text, received_at timestamp with time zone, used_at timestamp with time zone
-- ops_errors: id bigint, source text, kind text, at timestamp with time zone
-- pilot_admins: email text
-- pilot_carry: token text, anon_uid uuid, created timestamp with time zone
-- pilot_events: id bigint, actor uuid, name text, case_id text, promise_id text, props jsonb, at timestamp with time zone
-- reminders: id uuid, task_id text, user_id uuid, kind text, send_at timestamp with time zone, promise_id text, sent_at timestamp with time zone, cancelled_at timestamp with time zone, created_at timestamp with time zone, cancel_reason text, provider_id text, helper_sent_at timestamp with time zone
-- shares: token text, task_id text, user_id uuid, card jsonb, updated_at timestamp with time zone
-- tasks: id text, user_id uuid, data jsonb, created_at timestamp with time zone, updated_at timestamp with time zone
-- RLS is enabled on every table. inbound_addresses, pilot_admins, pilot_carry and ops_errors have no client policies (server-side only).

-- Row level security policies

create policy "own optout: read" on public.email_optouts for SELECT to authenticated using ((user_id = ( SELECT auth.uid() AS uid)));
create policy "own helpers: read" on public.helpers for SELECT to authenticated using ((user_id = ( SELECT auth.uid() AS uid)));
create policy "own inbound: delete" on public.inbound_items for DELETE to authenticated using ((user_id = ( SELECT auth.uid() AS uid)));
create policy "own inbound: mark" on public.inbound_items for UPDATE to authenticated using ((user_id = ( SELECT auth.uid() AS uid))) with check ((user_id = ( SELECT auth.uid() AS uid)));
create policy "own inbound: read" on public.inbound_items for SELECT to authenticated using ((user_id = ( SELECT auth.uid() AS uid)));
create policy pilot_events_insert on public.pilot_events for INSERT to authenticated with check ((actor = auth.uid()));
create policy "own reminders delete" on public.reminders for DELETE to authenticated using ((user_id = auth.uid()));
create policy "own reminders insert" on public.reminders for INSERT to authenticated with check (((user_id = auth.uid()) AND (EXISTS ( SELECT 1 FROM tasks t WHERE ((t.id = reminders.task_id) AND (t.user_id = auth.uid()))))));
create policy "own reminders select" on public.reminders for SELECT to authenticated using ((user_id = auth.uid()));
create policy "own shares: add" on public.shares for INSERT to authenticated with check (((user_id = ( SELECT auth.uid() AS uid)) AND (EXISTS ( SELECT 1 FROM tasks t WHERE ((t.id = shares.task_id) AND (t.user_id = ( SELECT auth.uid() AS uid)))))));
create policy "own shares: change" on public.shares for UPDATE to authenticated using ((user_id = ( SELECT auth.uid() AS uid))) with check ((user_id = ( SELECT auth.uid() AS uid)));
create policy "own shares: delete" on public.shares for DELETE to authenticated using ((user_id = ( SELECT auth.uid() AS uid)));
create policy "own shares: read" on public.shares for SELECT to authenticated using ((user_id = ( SELECT auth.uid() AS uid)));
create policy "own tasks: add" on public.tasks for INSERT to authenticated with check ((user_id = ( SELECT auth.uid() AS uid)));
create policy "own tasks: change" on public.tasks for UPDATE to authenticated using ((user_id = ( SELECT auth.uid() AS uid))) with check ((user_id = ( SELECT auth.uid() AS uid)));
create policy "own tasks: delete" on public.tasks for DELETE to authenticated using ((user_id = ( SELECT auth.uid() AS uid)));
create policy "own tasks: read" on public.tasks for SELECT to authenticated using ((user_id = ( SELECT auth.uid() AS uid)));

-- Functions

CREATE OR REPLACE FUNCTION public.claim_carry(p_token text, p_pairs jsonb DEFAULT '[]'::jsonb)
 RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path TO ''
AS $function$
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
end $function$;

CREATE OR REPLACE FUNCTION public.delete_my_account()
 RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path TO ''
AS $function$
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  delete from public.pilot_events where actor = auth.uid();
  delete from auth.users where id = auth.uid();
end $function$;

CREATE OR REPLACE FUNCTION public.email_reminders_ready()
 RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path TO ''
AS $function$
  select exists (select 1 from vault.decrypted_secrets where name = 'resend_api_key' and coalesce(decrypted_secret,'') <> '')
     and exists (select 1 from vault.decrypted_secrets where name = 'reminder_from' and coalesce(decrypted_secret,'') like '%@%')
$function$;

CREATE OR REPLACE FUNCTION public.get_share(p_token text)
 RETURNS TABLE(card jsonb, updated_at timestamp with time zone) LANGUAGE sql STABLE SECURITY DEFINER SET search_path TO ''
AS $function$
  select s.card, s.updated_at from public.shares s
  where s.token = p_token and char_length(p_token) >= 24 and s.updated_at > now() - interval '30 days';
$function$;

CREATE OR REPLACE FUNCTION public.helper_respond(p_token text, p_action text)
 RETURNS text LANGUAGE plpgsql SECURITY DEFINER SET search_path TO ''
AS $function$
declare r public.helpers;
begin
  if p_token is null or char_length(p_token) < 40 then return 'unknown'; end if;
  select * into r from public.helpers where token = p_token;
  if not found then return 'unknown'; end if;
  if p_action = 'yes' and r.status = 'pending' then
    update public.helpers set status = 'confirmed', confirmed_at = now() where token = p_token; return 'confirmed';
  elsif p_action = 'stop' then
    update public.helpers set status = 'stopped', stopped_at = now() where token = p_token; return 'stopped';
  end if;
  return r.status;
end $function$;

CREATE OR REPLACE FUNCTION public.invite_helper(p_task_id text, p_email text, p_name text)
 RETURNS text LANGUAGE plpgsql SECURITY DEFINER SET search_path TO ''
AS $function$
declare uid uuid := auth.uid(); em text := lower(btrim(p_email)); nm text := btrim(p_name); cur public.helpers;
begin
  if uid is null then raise exception 'not signed in'; end if;
  if not exists (select 1 from public.shares s where s.task_id = p_task_id and s.user_id = uid) then raise exception 'share the task first'; end if;
  if em !~ '^[^\s@]+@[^\s@]+\.[^\s@]+$' or char_length(em) > 254 then raise exception 'bad email'; end if;
  if nm = '' or char_length(nm) > 40 or nm ~ '[@/<>:]|https?|www\.|\.[a-z]{2,}' then raise exception 'bad name'; end if;
  if (select count(*) from public.helpers h where h.user_id = uid and h.invited_at > now() - interval '1 day') >= 5 then raise exception 'too many invites today'; end if;
  select * into cur from public.helpers h where h.task_id = p_task_id;
  if found and cur.email = em and cur.status in ('pending','confirmed') then return cur.status; end if;
  if found and cur.email = em and cur.status = 'stopped' then raise exception 'they said stop'; end if;
  insert into public.helpers (task_id, user_id, email, inviter_name, status, token, invited_at)
  values (p_task_id, uid, em, nm, 'pending', encode(extensions.gen_random_bytes(24), 'hex'), now())
  on conflict (task_id) do update set email = excluded.email, inviter_name = excluded.inviter_name, status = 'pending',
    token = excluded.token, invited_at = now(), invite_sent_at = null, confirmed_at = null, stopped_at = null;
  perform public.sorted_kick_reminders();
  return 'pending';
end $function$;

CREATE OR REPLACE FUNCTION public.is_pilot_admin()
 RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path TO ''
AS $function$
  select exists(select 1 from public.pilot_admins a where lower(a.email)=lower(coalesce(auth.jwt()->>'email','')) and coalesce(auth.jwt()->>'email','')<>'');
$function$;

CREATE OR REPLACE FUNCTION public.my_inbound_address()
 RETURNS text LANGUAGE plpgsql SECURITY DEFINER SET search_path TO ''
AS $function$
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
end $function$;

CREATE OR REPLACE FUNCTION public.pilot_health()
 RETURNS jsonb LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path TO ''
AS $function$
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
       from public.ops_errors where source='inbound'));
  return j;
end $function$;

CREATE OR REPLACE FUNCTION public.pilot_metrics(include_admins boolean DEFAULT false)
 RETURNS jsonb LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path TO ''
AS $function$
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
    'miss', jsonb_build_object('missed', (select count(distinct promise_id) from missed), 'recovered', (select count(distinct promise_id) from recovered)),
    'return_hours_median', (select percentile_cont(0.5) within group (order by h) from lag),
    'email', (select to_jsonb(anonp) from anonp),
    'counts', coalesce((select jsonb_object_agg(name, jsonb_build_object('total',total,'week',week)) from counts), '{}'::jsonb)
  ) into r;
  return r;
end $function$;

CREATE OR REPLACE FUNCTION public.remove_helper(p_task_id text)
 RETURNS void LANGUAGE sql SECURITY DEFINER SET search_path TO ''
AS $function$
  delete from public.helpers where task_id = p_task_id and user_id = auth.uid();
$function$;

CREATE OR REPLACE FUNCTION public.report_auth_error(p_kind text)
 RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path TO ''
AS $function$
begin
  if p_kind not in ('link_expired','link_invalid','send_failed','code_failed','anon_failed','anon_slow') then return; end if;
  if (select count(*) from public.ops_errors where source='auth' and at > now() - interval '1 hour') >= 300 then return; end if;
  insert into public.ops_errors(source, kind) values ('auth', p_kind);
end $function$;

CREATE OR REPLACE FUNCTION public.shares_drop_helper()
 RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path TO ''
AS $function$
begin delete from public.helpers where task_id = old.task_id; return old; end $function$;

CREATE OR REPLACE FUNCTION public.sorted_case_live(d jsonb)
 RETURNS boolean LANGUAGE sql STABLE SET search_path TO ''
AS $function$
  select exists (
    select 1 from jsonb_array_elements(coalesce(d->'promises','[]'::jsonb)) p
    where p->>'status' = 'open'
      and ( (p->>'dueAt' is not null and (p->>'dueAt')::timestamptz > now() - interval '30 days')
         or (p->>'dueAt' is null and coalesce((p->>'loggedAt')::timestamptz, now() - interval '31 days') > now() - interval '30 days') ))
$function$;

CREATE OR REPLACE FUNCTION public.sorted_kick_reminders()
 RETURNS bigint LANGUAGE sql SECURITY DEFINER SET search_path TO ''
AS $function$
  select net.http_post(
    url := 'https://boxrwcuhxmimayaxzywu.supabase.co/functions/v1/send-reminders',
    headers := jsonb_build_object('Content-Type','application/json','x-cron-secret',(select decrypted_secret from vault.decrypted_secrets where name='sorted_cron_secret')),
    body := '{}'::jsonb,
    timeout_milliseconds := 20000)
$function$;

CREATE OR REPLACE FUNCTION public.sorted_secret(p_name text)
 RETURNS text LANGUAGE sql SECURITY DEFINER SET search_path TO ''
AS $function$
  select decrypted_secret from vault.decrypted_secrets where name = p_name limit 1
$function$;

CREATE OR REPLACE FUNCTION public.stash_carry()
 RETURNS text LANGUAGE plpgsql SECURITY DEFINER SET search_path TO ''
AS $function$
declare tok text;
begin
  if auth.uid() is null or coalesce((auth.jwt()->>'is_anonymous')::boolean,false) is not true then return null; end if;
  delete from public.pilot_carry where created < now() - interval '1 day' or anon_uid = auth.uid();
  tok := encode(extensions.gen_random_bytes(24),'hex');
  insert into public.pilot_carry(token, anon_uid) values (tok, auth.uid());
  return tok;
end $function$;

CREATE OR REPLACE FUNCTION public.touch_updated_at()
 RETURNS trigger LANGUAGE plpgsql SET search_path TO ''
AS $function$
begin new.updated_at := now(); return new; end $function$;

-- Scheduled jobs (pg_cron)

-- ops-errors-retention      [27 3 * * *]  delete from public.ops_errors where at < now() - interval '90 days'
-- pilot-events-retention    [17 3 * * *]  delete from public.pilot_events where at < now() - interval '12 months'
-- shares-retention          [47 3 * * *]  delete from public.shares where updated_at < now() - interval '90 days'
-- sorted-inbound-cleanup    [17 3 * * *]  delete from public.inbound_items where received_at < now() - interval '30 days'
-- sorted-send-reminders     [*/10 * * * *] select public.sorted_kick_reminders()
-- sorted-retention-90d      [17 3 * * *]
--   delete from public.tasks where updated_at < now() - interval '90 days' and not public.sorted_case_live(data)
-- sorted-anon-cleanup       [37 3 * * *]
--   delete from auth.users u
--   where u.is_anonymous
--     and coalesce(u.last_sign_in_at, u.created_at) < now() - interval '30 days'
--     and not exists (select 1 from public.tasks t where t.user_id = u.id
--                     and (t.updated_at > now() - interval '30 days' or public.sorted_case_live(t.data)))
