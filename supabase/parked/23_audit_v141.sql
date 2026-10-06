-- v141 (the full audit of 6 October 2026). Live and staging.
-- 1. Forwarding: my_inbound_address() was revoked from authenticated in migration 05 and never granted back, so the
--    page's call failed and the forwarding card never showed. A read-only getter is granted instead: it returns the
--    existing address, '' when forwarding is ready but this person has none yet (the page offers "Get my address",
--    which calls inbound_address_new()), or null when forwarding isn't set up. Nothing is created on page load.
create or replace function public.my_inbound_address_get()
returns text language plpgsql stable security definer set search_path = '' as $$
declare uid uuid := auth.uid(); dom text; tok text;
begin
  if uid is null then return null; end if;
  select decrypted_secret into dom from vault.decrypted_secrets where name = 'inbound_domain';
  if coalesce(dom,'') = '' or not exists (select 1 from vault.decrypted_secrets where name = 'resend_webhook_secret' and coalesce(decrypted_secret,'') <> '') then return null; end if;
  select token into tok from public.inbound_addresses where user_id = uid;
  if tok is null then return ''; end if;
  return tok || '@' || dom;
end $$;
revoke all on function public.my_inbound_address_get() from public, anon;
grant execute on function public.my_inbound_address_get() to authenticated;

-- 2. Retention: a case is "live" (never removed for being idle) while anything on it is still due, not only an open
--    promise: your own open step with a date in the last 30 days or later, a renewal whose expiry hasn't passed, a
--    deadline on you (v141 t.deadline) that hasn't passed, or a Moving home record whose move date is still ahead.
--    Read by the retention jobs only (no grants), as before.
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
$$;
revoke all on function public.sorted_case_live(jsonb) from public, anon, authenticated;

-- 3. A shared card can't be used as file hosting.
alter table public.shares drop constraint if exists shares_card_size;
alter table public.shares add constraint shares_card_size check (pg_column_size(card) <= 100000) not valid;
