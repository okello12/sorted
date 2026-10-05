-- Sorted v134: forwarding comes back, to a secret address per person. my_inbound_address() already gives each person
-- one (log-<16 hex>@<inbound domain>, made on first ask); this adds a way to replace it, so an address that got out
-- stops working at once. The old address row is deleted; emails already received stay until used or 30 days pass.
-- Apply to live and staging.
create or replace function public.inbound_address_new() returns text
language plpgsql security definer set search_path to '' as $$
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  delete from public.inbound_addresses where user_id = auth.uid();
  return public.my_inbound_address();
end $$;
revoke all on function public.inbound_address_new() from public, anon;
grant execute on function public.inbound_address_new() to authenticated;
