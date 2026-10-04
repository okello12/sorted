-- Sorted staging, part 2: the six functions whose bodies delete rows, the trigger that uses one, and the retention
-- jobs. Supabase's tooling asks a person to confirm any statement that deletes, so this part is run by hand in the
-- SQL editor of the staging project (Database > SQL editor), once, after 00_schema.sql. Replace STAGING_REF first if
-- your project is not ujwanxqrefziuxwfzeaj. Nothing here touches the live project.

create or replace function public.shares_drop_helper() returns trigger language plpgsql security definer set search_path to '' as $$
begin delete from public.helpers where task_id = old.task_id; return old; end $$;

create or replace function public.delete_my_account() returns void language plpgsql security definer set search_path to '' as $$
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  delete from public.pilot_events where actor = auth.uid();
  delete from auth.users where id = auth.uid();
end $$;

create or replace function public.stash_carry() returns text language plpgsql security definer set search_path to '' as $$
declare tok text;
begin
  if auth.uid() is null or coalesce((auth.jwt()->>'is_anonymous')::boolean,false) is not true then return null; end if;
  delete from public.pilot_carry where created < now() - interval '1 day' or anon_uid = auth.uid();
  tok := encode(extensions.gen_random_bytes(24),'hex');
  insert into public.pilot_carry(token, anon_uid) values (tok, auth.uid());
  return tok;
end $$;

create or replace function public.claim_carry(p_token text, p_pairs jsonb default '[]'::jsonb) returns boolean language plpgsql security definer set search_path to '' as $$
declare a uuid; pr jsonb;
begin
  if auth.uid() is null or coalesce((auth.jwt()->>'is_anonymous')::boolean,false) then return false; end if;
  delete from public.pilot_carry where token = p_token and created > now() - interval '1 day' returning anon_uid into a;
  if a is null or a = auth.uid() then return false; end if;
  if jsonb_typeof(p_pairs) = 'array' then
    for pr in select * from jsonb_array_elements(p_pairs) limit 200 loop
      update public.pilot_events set case_id = pr->>1 where actor = a and case_id = pr->>0 and char_length(pr->>1) <= 40;
    end loop;
  end if;
  update public.pilot_events set actor = auth.uid() where actor = a;
  delete from auth.users where id = a and is_anonymous;
  return true;
end $$;

create or replace function public.remove_helper(p_task_id text) returns void language sql security definer set search_path to '' as $$
  delete from public.helpers where task_id = p_task_id and user_id = auth.uid();
$$;

create or replace function public.drop_outcome(p_promise text) returns void language sql security definer set search_path to 'public' as $$
  delete from public.promise_outcomes where user_id = auth.uid() and promise_id = left(p_promise, 40);
$$;

revoke all on function public.shares_drop_helper(), public.delete_my_account(), public.stash_carry(), public.claim_carry(text,jsonb), public.remove_helper(text), public.drop_outcome(text) from public, anon, authenticated;
grant execute on function public.delete_my_account(), public.stash_carry(), public.claim_carry(text,jsonb), public.remove_helper(text), public.drop_outcome(text) to authenticated;
grant execute on function public.shares_drop_helper(), public.delete_my_account(), public.stash_carry(), public.claim_carry(text,jsonb), public.remove_helper(text), public.drop_outcome(text) to service_role;

create trigger shares_drop_helper after delete on public.shares for each row execute function public.shares_drop_helper();

-- Retention jobs (the same as live) -----------------------------------------------------------------------------------

select cron.schedule('sorted-send-reminders', '*/10 * * * *', $$select public.sorted_kick_reminders()$$);
select cron.schedule('sorted-retention-90d', '17 3 * * *', $$delete from public.tasks where updated_at < now() - interval '90 days' and not public.sorted_case_live(data)$$);
select cron.schedule('sorted-inbound-cleanup', '17 3 * * *', $$delete from public.inbound_items where received_at < now() - interval '30 days'$$);
select cron.schedule('pilot-events-retention', '17 3 * * *', $$delete from public.pilot_events where at < now() - interval '12 months'$$);
select cron.schedule('ops-errors-retention', '27 3 * * *', $$delete from public.ops_errors where at < now() - interval '90 days'$$);
select cron.schedule('sorted-anon-cleanup', '37 3 * * *', $$delete from auth.users u where u.is_anonymous and coalesce(u.last_sign_in_at, u.created_at) < now() - interval '30 days' and not exists (select 1 from public.tasks t where t.user_id = u.id and (t.updated_at > now() - interval '30 days' or public.sorted_case_live(t.data)))$$);
select cron.schedule('shares-retention', '47 3 * * *', $$delete from public.shares where updated_at < now() - interval '90 days'$$);
select cron.schedule('pilot-carry-cleanup', '57 3 * * *', $$delete from public.pilot_carry where created < now() - interval '1 day'$$);
select cron.schedule('sorted-idle-accounts', '7 4 * * *', $$delete from auth.users u where not coalesce(u.is_anonymous, false) and coalesce(u.last_sign_in_at, u.created_at) < now() - interval '12 months' and not exists (select 1 from public.tasks t where t.user_id = u.id) and lower(coalesce(u.email, '')) not in (select lower(email) from public.pilot_admins)$$);
select cron.schedule('sorted-assistant-usage', '47 4 * * *', $$delete from public.assistant_usage where day < current_date - 30$$);
select cron.schedule('sorted-outcomes-retention', '57 4 * * *', $$delete from public.promise_outcomes where at < now() - interval '12 months'$$);
select cron.schedule('sorted-notes-retention', '17 5 * * *', $$delete from public.case_notes where created_at < now() - interval '90 days'$$);
