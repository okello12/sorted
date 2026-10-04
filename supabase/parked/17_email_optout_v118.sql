-- Sorted v118 (Phase 3): an email reminders switch in Settings. The table email_optouts already holds the people who
-- stopped all reminder emails through the link at the bottom of an email (email-stop); this lets a signed-in person
-- switch it off and on from the app. send-reminders already honours the table.
-- Applied to live and staging on 4 October 2026.
create or replace function public.set_email_optout(p_off boolean) returns boolean language plpgsql security definer set search_path to '' as $$
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  if p_off then
    insert into public.email_optouts (user_id) values (auth.uid()) on conflict (user_id) do nothing;
  else
    delete from public.email_optouts where user_id = auth.uid();
  end if;
  return p_off;
end $$;
revoke all on function public.set_email_optout(boolean) from public, anon;
grant execute on function public.set_email_optout(boolean) to authenticated, service_role;
