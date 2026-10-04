-- v109: errors the operator can see. ops_errors gains a short detail and a build; four new sources (page, save,
-- reminder, share) written by report_page_error(), which anyone signed in (including anonymously) can call: the kind
-- of error, the first line of its message with quoted words removed, the screen and the build. Never case text.
-- Capped at 300 an hour across those sources. pilot_health() gains a 'page' block. Rows older than 90 days are already
-- deleted by the ops_errors retention job.
alter table public.ops_errors add column if not exists detail text, add column if not exists build text;
alter table public.ops_errors drop constraint if exists ops_errors_source_check;
alter table public.ops_errors add constraint ops_errors_source_check check (source = any (array['auth','inbound','assistant','scores','page','save','reminder','share']));
alter table public.ops_errors drop constraint if exists ops_errors_detail_len;
alter table public.ops_errors add constraint ops_errors_detail_len check (detail is null or char_length(detail) <= 200);
alter table public.ops_errors drop constraint if exists ops_errors_build_len;
alter table public.ops_errors add constraint ops_errors_build_len check (build is null or char_length(build) <= 60);
create or replace function public.report_page_error(p_source text, p_kind text, p_detail text, p_build text)
 returns void
 language plpgsql
 volatile security definer
 set search_path to ''
as $function$
begin
  if p_source is null or p_source not in ('page','save','reminder','share') then return; end if;
  if (select count(*) from public.ops_errors where source in ('page','save','reminder','share') and at > now() - interval '1 hour') >= 300 then return; end if;
  insert into public.ops_errors(source, kind, detail, build)
    values (p_source, left(coalesce(p_kind,'error'), 40), left(coalesce(p_detail,''), 200), left(coalesce(p_build,''), 60));
end $function$;
revoke all on function public.report_page_error(text,text,text,text) from public;
grant execute on function public.report_page_error(text,text,text,text) to anon, authenticated;

-- pilot_health() gains a 'page' block (errors reported by the page in the last 24 hours and 7 days, by source and kind).
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
