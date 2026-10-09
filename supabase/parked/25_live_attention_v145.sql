-- v145 (audit pass 3, area C). Live and staging. A person presses Run in the SQL editor (or apply_migration).
-- Retention: since v143 a check day the person chose, a "Later" and a parking deadline reminder live in t.att, and a
-- Later also in t.snooze, not in the promise. sorted_case_live() didn't look at them, so a case whose only date was a
-- check day or a Later more than 90 days after its last change was removed by the idle clean-up before that day came
-- (and send-reminders then cancelled the reminder as "task gone"). A live attention item (not done, not cancelled)
-- with its day in the last 30 days or later, or a Later that hasn't ended, now keeps the case, as an open promise does.
-- Everything else is exactly as migration 23 left it. Read by the retention jobs only (no grants), as before.
-- Without this migration the page works as before; only the idle clean-up keeps removing such cases.
create or replace function public.sorted_case_live(d jsonb)
returns boolean language sql stable set search_path = '' as $$
  select
    exists (
      select 1 from jsonb_array_elements(case when jsonb_typeof(d->'promises') = 'array' then d->'promises' else '[]'::jsonb end) p
      where jsonb_typeof(p) = 'object' and p->>'status' = 'open'
        and ( (p->>'dueAt' is not null and coalesce(public.try_ts(p->>'dueAt'), now() - interval '31 days') > now() - interval '30 days')
           or (p->>'dueAt' is null and coalesce(public.try_ts(p->>'loggedAt'), now() - interval '31 days') > now() - interval '30 days') ))
    or exists (
      select 1 from jsonb_array_elements(case when jsonb_typeof(d->'moves') = 'array' then d->'moves' else '[]'::jsonb end) m
      where jsonb_typeof(m) = 'object' and m->>'status' = 'open' and m->>'dueAt' is not null
        and coalesce(public.try_ts(m->>'dueAt'), now() - interval '31 days') > now() - interval '30 days')
    or (jsonb_typeof(d->'renew') = 'object' and coalesce(public.try_ts(d->'renew'->>'expiry'), now() - interval '1 day') > now())
    or (jsonb_typeof(d->'deadline') = 'object' and coalesce(public.try_ts(d->'deadline'->>'iso'), now() - interval '1 day') > now())
    or (d->>'kind' = 'moment' and coalesce(public.try_ts(d->>'date'), now() - interval '31 days') > now() - interval '30 days')
    -- v145: the person's own attention (t.att: check, snooze, remind) and a Later that hasn't ended
    or (coalesce(d->>'board', '') <> 'done' and exists (
      select 1 from jsonb_array_elements(case when jsonb_typeof(d->'att') = 'array' then d->'att' else '[]'::jsonb end) a
      where jsonb_typeof(a) = 'object' and a->>'done' is null and a->>'cancelled' is null
        and coalesce(public.try_ts(a->>'at'), now() - interval '31 days') > now() - interval '30 days'))
    or (coalesce(d->>'board', '') <> 'done' and jsonb_typeof(d->'snooze') = 'object'
        and coalesce(public.try_ts(d->'snooze'->>'until'), now() - interval '1 day') > now())
$$;
revoke all on function public.sorted_case_live(jsonb) from public, anon, authenticated;
