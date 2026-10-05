-- Sorted v133: reminders on the lock screen (Web Push).
-- A phone that says yes to notifications saves its push subscription here. send-reminders sends each due reminder to
-- the person's phones as well as by email. The push message carries no case details, only which case to open.
-- One phone belongs to one account: saving a subscription removes the same phone from any other account.
-- Only the big browser push services are accepted, so Sorted never posts to an address someone typed in.
-- Apply to live and staging.

create table if not exists public.push_subs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  endpoint text not null unique check (length(endpoint) between 20 and 1000),
  p256dh text not null check (length(p256dh) between 60 and 120),
  auth text not null check (length(auth) between 16 and 40),
  created_at timestamptz not null default now(),
  last_ok_at timestamptz,
  fails int not null default 0
);
alter table public.push_subs enable row level security;
-- No policies and no grants: the app goes through the functions below, send-reminders uses the service role.
revoke all on public.push_subs from public, anon, authenticated;

alter table public.reminders add column if not exists push_sent_at timestamptz;
alter table public.reminders add column if not exists push_detail text check (push_detail is null or length(push_detail) <= 40);

create or replace function public.push_save(p_endpoint text, p_p256dh text, p_auth text) returns int
language plpgsql security definer set search_path to '' as $$
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  if p_endpoint !~ '^https://(fcm\.googleapis\.com|android\.googleapis\.com|updates\.push\.services\.mozilla\.com|web\.push\.apple\.com|[a-z0-9-]+\.notify\.windows\.com|[a-z0-9.-]+\.push\.apple\.com)/' then
    raise exception 'unknown push service';
  end if;
  delete from public.push_subs where endpoint = p_endpoint;
  insert into public.push_subs (user_id, endpoint, p256dh, auth) values (auth.uid(), p_endpoint, p_p256dh, p_auth);
  if (select count(*) from public.push_subs where user_id = auth.uid()) > 10 then
    delete from public.push_subs where id in (select id from public.push_subs where user_id = auth.uid() order by created_at limit 1);
  end if;
  return (select count(*)::int from public.push_subs where user_id = auth.uid());
end $$;

create or replace function public.push_drop(p_endpoint text) returns int
language plpgsql security definer set search_path to '' as $$
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  delete from public.push_subs where user_id = auth.uid() and (p_endpoint is null or endpoint = p_endpoint);
  return (select count(*)::int from public.push_subs where user_id = auth.uid());
end $$;

-- Whether this phone's subscription is saved for the signed-in account, and whether sending is switched on.
create or replace function public.push_state(p_endpoint text) returns jsonb
language plpgsql security definer set search_path to '' as $$
begin
  if auth.uid() is null then return jsonb_build_object('ready', false, 'mine', false, 'count', 0); end if;
  return jsonb_build_object(
    'ready', exists (select 1 from vault.decrypted_secrets where name = 'vapid_private_jwk'),
    'mine', exists (select 1 from public.push_subs where user_id = auth.uid() and endpoint = p_endpoint),
    'count', (select count(*) from public.push_subs where user_id = auth.uid()));
end $$;

revoke all on function public.push_save(text, text, text) from public, anon;
revoke all on function public.push_drop(text) from public, anon;
revoke all on function public.push_state(text) from public, anon;
grant execute on function public.push_save(text, text, text) to authenticated;
grant execute on function public.push_drop(text) to authenticated;
grant execute on function public.push_state(text) to authenticated;
