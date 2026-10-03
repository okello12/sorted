-- v104: show your move to someone you live with. The existing helper link (shares) points at the move's own tasks row,
-- so no change to shares. New: share_opens, counts only (how many opens, on how many London days, first and last time),
-- keyed by the shared row and deleted with it. Nothing about who opened it. share_seen() is called once per page load of
-- a link; it counts only while the link works. Opens by the owner testing their own link are counted too.
-- pilot_metrics() gains 'sharing'. Moving home share step records reuse moment_item (item 'share', choice link, copy,
-- whatsapp, off), so the step name list is unchanged; 'with_a_case' now ignores them.
create table if not exists public.share_opens(
  task_id text primary key references public.tasks(id) on delete cascade,
  opens integer not null default 0,
  open_days integer not null default 0,
  first_at timestamptz,
  last_at timestamptz
);
alter table public.share_opens enable row level security;
revoke all on public.share_opens from anon, authenticated;
create or replace function public.share_seen(p_token text)
 returns void
 language plpgsql
 volatile security definer
 set search_path to ''
as $function$
declare tid text;
begin
  if p_token is null or char_length(p_token) < 24 then return; end if;
  select s.task_id into tid from public.shares s where s.token = p_token and s.updated_at > now() - interval '30 days';
  if tid is null then return; end if;
  insert into public.share_opens as o (task_id, opens, open_days, first_at, last_at) values (tid, 1, 1, now(), now())
  on conflict (task_id) do update set opens = o.opens + 1,
    open_days = o.open_days + case when (o.last_at at time zone 'Europe/London')::date < (now() at time zone 'Europe/London')::date then 1 else 0 end,
    last_at = now();
end $function$;
revoke all on function public.share_seen(text) from public;
grant execute on function public.share_seen(text) to anon, authenticated;
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
end $function$;
