-- Sorted v137: the Web Push signing key is made inside Supabase by the vapid-init function, so nobody sees or types
-- it. push_vapid_init() stores it in Vault once (service role only) and never replaces an existing key.
-- Apply to live only (staging has no push key).
create or replace function public.push_vapid_init(p_jwk text) returns boolean
language plpgsql security definer set search_path to '' as $$
begin
  if exists (select 1 from vault.secrets where name = 'vapid_private_jwk') then return false; end if;
  perform vault.create_secret(p_jwk, 'vapid_private_jwk', 'Web Push signing key for Sorted, made inside Supabase by vapid-init');
  return true;
end $$;
revoke all on function public.push_vapid_init(text) from public, anon, authenticated;
grant execute on function public.push_vapid_init(text) to service_role;
