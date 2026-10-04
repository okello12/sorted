-- Sorted v116 (docs/PLAN.md Phase 1): reminder delivery evidence, and a definition of guest activity.
-- Applied to live and staging on the day of the v116 release (see the Applied rows in CLAUDE.md).
--
-- 1. Reminder delivery. Resend accepting an email is not arrival. Each reminder now records: when it was due
--    (send_at, already there), when it was handed to Resend (submitted_at), Resend's acceptance (sent_at and
--    provider_id, already there), and what Resend's webhooks later say (delivered_at, bounced_at, delivery_status,
--    delivery_detail). The edge function resend-events writes the last four through reminder_delivery_event(),
--    service role only. pilot_health() gains a 'delivery' block. Never an address, never case words.
-- 2. Guest activity. Opening Sorted while signed in now writes a "seen" time (touch_seen(), at most once an hour),
--    and the guest clean-up job counts that as activity alongside a sign-in, a case saved in 30 days or a live promise.

alter table public.reminders
  add column if not exists submitted_at timestamptz,
  add column if not exists delivered_at timestamptz,
  add column if not exists bounced_at timestamptz,
  add column if not exists delivery_status text,
  add column if not exists delivery_detail text;
alter table public.reminders drop constraint if exists reminders_delivery_detail_len;
alter table public.reminders add constraint reminders_delivery_detail_len check (delivery_detail is null or char_length(delivery_detail) <= 80);
create index if not exists reminders_provider_id_idx on public.reminders (provider_id) where provider_id is not null;

create or replace function public.reminder_delivery_event(p_provider_id text, p_event text, p_at timestamptz, p_detail text default null)
returns boolean language plpgsql security definer set search_path to '' as $$
declare n int;
begin
  if p_provider_id is null or char_length(p_provider_id) > 80 then return false; end if;
  if p_event = 'email.delivered' then
    update public.reminders set delivered_at = coalesce(delivered_at, p_at), delivery_status = 'delivered', delivery_detail = null where provider_id = p_provider_id;
  elsif p_event in ('email.bounced', 'email.failed') then
    update public.reminders set bounced_at = coalesce(bounced_at, p_at), delivery_status = case when p_event = 'email.bounced' then 'bounced' else 'failed' end, delivery_detail = left(p_detail, 80) where provider_id = p_provider_id;
  elsif p_event = 'email.delivery_delayed' then
    update public.reminders set delivery_status = coalesce(delivery_status, 'delayed'), delivery_detail = left(p_detail, 80) where provider_id = p_provider_id and delivered_at is null;
  elsif p_event = 'email.complained' then
    update public.reminders set delivery_status = 'complained' where provider_id = p_provider_id;
  else
    return false;
  end if;
  get diagnostics n = row_count;
  return n > 0;
end $$;
revoke all on function public.reminder_delivery_event(text, text, timestamptz, text) from public, anon, authenticated;
grant execute on function public.reminder_delivery_event(text, text, timestamptz, text) to service_role;

-- The webhook function records its own problems under the source 'webhook' (kind only: bad signature, no secret, unknown event).
alter table public.ops_errors drop constraint if exists ops_errors_source_check;
alter table public.ops_errors add constraint ops_errors_source_check check (source = any (array['auth','inbound','assistant','scores','page','save','reminder','share','webhook']));

-- Guest activity -------------------------------------------------------------------------------------------------------

create table if not exists public.user_seen (
  user_id uuid primary key references auth.users(id) on delete cascade,
  seen_at timestamptz not null default now()
);
alter table public.user_seen enable row level security;
revoke all on table public.user_seen from public, anon, authenticated;

create or replace function public.touch_seen() returns void language plpgsql security definer set search_path to '' as $$
begin
  if auth.uid() is null then return; end if;
  insert into public.user_seen (user_id, seen_at) values (auth.uid(), now())
  on conflict (user_id) do update set seen_at = now() where public.user_seen.seen_at < now() - interval '1 hour';
end $$;
revoke all on function public.touch_seen() from public, anon;
grant execute on function public.touch_seen() to authenticated, service_role;

-- A guest (anonymous account) is deleted after 30 days in which none of these happened: a sign-in, opening Sorted
-- signed in (seen_at), a case saved, or a promise still live.
select cron.schedule('sorted-anon-cleanup', '37 3 * * *', $$
  delete from auth.users u
  where u.is_anonymous
    and coalesce(u.last_sign_in_at, u.created_at) < now() - interval '30 days'
    and coalesce((select s.seen_at from public.user_seen s where s.user_id = u.id), u.created_at) < now() - interval '30 days'
    and not exists (select 1 from public.tasks t where t.user_id = u.id
                    and (t.updated_at > now() - interval '30 days' or public.sorted_case_live(t.data)))
$$);
-- An account with an email and no cases: 12 months without a sign-in or a visit.
select cron.schedule('sorted-idle-accounts', '7 4 * * *', $$
  delete from auth.users u
  where not coalesce(u.is_anonymous, false)
    and coalesce(u.last_sign_in_at, u.created_at) < now() - interval '12 months'
    and coalesce((select s.seen_at from public.user_seen s where s.user_id = u.id), u.created_at) < now() - interval '12 months'
    and not exists (select 1 from public.tasks t where t.user_id = u.id)
    and lower(coalesce(u.email, '')) not in (select lower(email) from public.pilot_admins)
$$);

-- Health: delivery evidence for the last 7 days ---------------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.pilot_health()
 RETURNS jsonb
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO ''
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
    'delivery', (select jsonb_build_object(
       'scheduled_7d', count(*) filter (where send_at > now() - interval '7 days'),
       'submitted_7d', count(*) filter (where submitted_at > now() - interval '7 days'),
       'accepted_7d', count(*) filter (where sent_at > now() - interval '7 days' and provider_id is not null),
       'delivered_7d', count(*) filter (where delivered_at > now() - interval '7 days'),
       'bounced_7d', count(*) filter (where bounced_at > now() - interval '7 days'),
       'delayed_7d', count(*) filter (where delivery_status = 'delayed' and sent_at > now() - interval '7 days'),
       'unknown_7d', count(*) filter (where sent_at > now() - interval '7 days' and sent_at < now() - interval '1 hour' and delivered_at is null and bounced_at is null),
       'late_minutes_median', (select percentile_cont(0.5) within group (order by extract(epoch from (sent_at - send_at))/60) from public.reminders where sent_at > now() - interval '7 days'),
       'arrival_minutes_median', (select percentile_cont(0.5) within group (order by extract(epoch from (delivered_at - sent_at))/60) from public.reminders where delivered_at > now() - interval '7 days'),
       'webhook_seen', exists (select 1 from public.reminders where delivered_at is not null or bounced_at is not null))
       from public.reminders),
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
end $function$;
