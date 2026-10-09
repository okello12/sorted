-- v149, STAGING only. The first full staging run (9 October) found staging had drifted from live: delete_my_account()
-- and stash_carry() were missing, and drop_outcome(), remove_helper() and shares_drop_helper() could be called without
-- signing in. Live was correct throughout. This brings staging level with live; the staging suite's grants matrix now
-- keeps the two in step.
create or replace function public.delete_my_account()
returns void language plpgsql security definer set search_path to '' as $function$
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  delete from public.pilot_events where actor = auth.uid();
  delete from auth.users where id = auth.uid();
end $function$;
create or replace function public.stash_carry()
returns text language plpgsql security definer set search_path to '' as $function$
declare tok text;
begin
  if auth.uid() is null or coalesce((auth.jwt()->>'is_anonymous')::boolean,false) is not true then return null; end if;
  delete from public.pilot_carry where created < now() - interval '1 day' or anon_uid = auth.uid();
  tok := encode(extensions.gen_random_bytes(24),'hex');
  insert into public.pilot_carry(token, anon_uid) values (tok, auth.uid());
  return tok;
end $function$;
revoke all on function public.delete_my_account() from public, anon;
grant execute on function public.delete_my_account() to authenticated;
revoke all on function public.stash_carry() from public, anon;
grant execute on function public.stash_carry() to authenticated;
revoke execute on function public.drop_outcome(text) from public, anon;
revoke execute on function public.remove_helper(text) from public, anon;
revoke execute on function public.shares_drop_helper() from public, anon, authenticated;
