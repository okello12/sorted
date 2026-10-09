-- v146. Live and staging. inbound-email v9 keeps the id of each email it has handled, so a webhook Resend delivers twice
-- (Svix retries the same message after a timeout or a 5xx) stores one suggestion, not two. The key is Resend's
-- email_id (or the Svix message id when there is none): an opaque id, never an address or any words. Rows older than
-- 7 days are removed by the function itself. Service role only: RLS on, no policies, no grants.
-- Without this migration inbound-email v9 carries on as v8 did (the insert fails and it doesn't deduplicate).
create table if not exists public.inbound_seen (
  key text primary key check (length(key) between 1 and 120),
  at timestamptz not null default now()
);
alter table public.inbound_seen enable row level security;
revoke all on table public.inbound_seen from public, anon, authenticated;
create index if not exists inbound_seen_at on public.inbound_seen (at);
