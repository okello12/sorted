-- Sorted v68: the case assistant's daily limit. Run this once in the Supabase SQL editor.
-- Holds only a person's id, a date and a count. No case text, no questions, no answers.
create table if not exists public.assistant_usage (
  user_id uuid not null references auth.users(id) on delete cascade,
  day date not null default current_date,
  n int not null default 0,
  primary key (user_id, day)
);
alter table public.assistant_usage enable row level security;  -- no policies: only the service role can touch it
revoke all on public.assistant_usage from anon, authenticated;

create or replace function public.assistant_take(p_user uuid, p_limit int)
returns boolean language plpgsql security definer set search_path = public as $$
declare v int;
begin
  insert into public.assistant_usage(user_id, day, n) values (p_user, current_date, 1)
  on conflict (user_id, day) do update set n = public.assistant_usage.n + 1
  returning n into v;
  return v <= p_limit;
end $$;
revoke all on function public.assistant_take(uuid, int) from public, anon, authenticated;
grant execute on function public.assistant_take(uuid, int) to service_role;

-- counts are deleted after 30 days
select cron.schedule('sorted-assistant-usage', '47 4 * * *', $$delete from public.assistant_usage where day < current_date - 30$$)
where not exists (select 1 from cron.job where jobname = 'sorted-assistant-usage');

-- let the assistant log failures (a kind and a time only)
alter table public.ops_errors drop constraint if exists ops_errors_source_check;
alter table public.ops_errors add constraint ops_errors_source_check check (source = any (array['auth','inbound','assistant','scores']));
