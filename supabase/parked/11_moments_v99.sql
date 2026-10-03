-- v99: Moving home, the first life moment. Three new step names, codes only:
--   moment_created (type, tenure, council, car, bb, days to the move), moment_item (type, item code, choice:
--   done, irrelevant, case, link, undo), moment_opened (type; once a day, after the first day).
-- pilot_metrics() gains a 'moments' block. No new tables or columns; the container itself is a tasks row.
alter table public.pilot_events drop constraint pilot_events_name_check;
alter table public.pilot_events add constraint pilot_events_name_check check (name = any (array['case_started','baseline_action_recorded','promise_created','email_added_at_promise','promise_due_return','outcome_kept','outcome_missed','outcome_rescheduled','chase_used','new_promise_after_miss','case_closed','recap_copied','second_case_started','moment_created','moment_item','moment_opened']));
create or replace function public.pilot_metrics(include_admins boolean default false)
 returns jsonb
 language plpgsql
 stable security definer
 set search_path to ''
as $function$
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
    select case_id, count(*) filter (where props->>'choice' in ('case','link')) as tracked from e where name='moment_item' group by case_id
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
    'return_hours_median', (select percentile_cont(0.5) within group (order by h) from lag),
    'email', (select to_jsonb(anonp) from anonp),
    'counts', coalesce((select jsonb_object_agg(name, jsonb_build_object('total',total,'week',week)) from counts), '{}'::jsonb)
  ) into r;
  return r;
end $function$;
