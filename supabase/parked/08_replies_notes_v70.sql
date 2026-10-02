-- Sorted v70: replies come back into the case, and helpers can add notes. Run this once in the Supabase SQL editor.
-- Part 1 is the prepared 01_case_reply_structure.sql, unchanged. Part 2 switches replies on. Part 3 is helper notes.

-- PART 1: case reply addresses
create table if not exists public.case_mail (
  task_id text primary key references public.tasks(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  token text not null unique,
  created_at timestamptz not null default now()
);
alter table public.case_mail enable row level security;
drop policy if exists case_mail_own_read on public.case_mail;
create policy case_mail_own_read on public.case_mail for select to authenticated using (user_id = (select auth.uid()));

alter table public.inbound_items add column if not exists task_id text references public.tasks(id) on delete cascade;
alter table public.inbound_items add column if not exists from_domain text;
create index if not exists inbound_items_task_idx on public.inbound_items(task_id) where task_id is not null;

create or replace function public.case_reply_address(p_task_id text)
returns text language plpgsql security definer set search_path to ''
as $$
declare uid uuid := auth.uid(); dom text; tok text; onv text;
begin
  if uid is null or p_task_id is null then return null; end if;
  select decrypted_secret into onv from vault.decrypted_secrets where name = 'case_replies_on';
  if coalesce(onv,'') <> 'yes' then return null; end if;
  select decrypted_secret into dom from vault.decrypted_secrets where name = 'inbound_domain';
  if coalesce(dom,'') = '' then return null; end if;
  if not exists (select 1 from public.tasks where id = p_task_id and user_id = uid) then return null; end if;
  select token into tok from public.case_mail where task_id = p_task_id;
  if tok is null then
    tok := 'case-' || encode(extensions.gen_random_bytes(10), 'hex');
    insert into public.case_mail(task_id, user_id, token) values (p_task_id, uid, tok) on conflict (task_id) do nothing;
    select token into tok from public.case_mail where task_id = p_task_id;
  end if;
  return tok || '@' || dom;
end $$;
revoke all on function public.case_reply_address(text) from public, anon;
grant execute on function public.case_reply_address(text) to authenticated;

-- PART 2: switch case replies on (not a credential: a yes/no flag read by name)
select vault.create_secret('yes', 'case_replies_on', 'Sorted: case reply addresses on')
where not exists (select 1 from vault.secrets where name = 'case_replies_on');

-- PART 3: helper notes. The owner chooses per case whether the helper link can add notes.
alter table public.shares add column if not exists notes_on boolean not null default false;
create table if not exists public.case_notes (
  id uuid primary key default gen_random_uuid(),
  task_id text not null references public.tasks(id) on delete cascade,
  author text not null check (char_length(author) between 1 and 40),
  body text not null check (char_length(body) between 1 and 1000),
  created_at timestamptz not null default now()
);
create index if not exists case_notes_task_idx on public.case_notes(task_id);
alter table public.case_notes enable row level security;
drop policy if exists case_notes_owner_read on public.case_notes;
create policy case_notes_owner_read on public.case_notes for select to authenticated
  using (exists (select 1 from public.tasks t where t.id = task_id and t.user_id = (select auth.uid())));
drop policy if exists case_notes_owner_delete on public.case_notes;
create policy case_notes_owner_delete on public.case_notes for delete to authenticated
  using (exists (select 1 from public.tasks t where t.id = task_id and t.user_id = (select auth.uid())));

-- A helper with the link adds a note. Only if the owner switched notes on, the link is live, and at most 10 a day.
create or replace function public.add_share_note(p_token text, p_author text, p_body text)
returns text language plpgsql security definer set search_path = public as $$
declare s record; n int;
begin
  select token, task_id, notes_on, updated_at into s from public.shares where token = p_token;
  if s.token is null or s.updated_at < now() - interval '30 days' then return 'gone'; end if;
  if not s.notes_on then return 'off'; end if;
  if char_length(trim(coalesce(p_author,''))) = 0 or char_length(trim(coalesce(p_body,''))) = 0 then return 'empty'; end if;
  select count(*) into n from public.case_notes where task_id = s.task_id and created_at > now() - interval '1 day';
  if n >= 10 then return 'limit'; end if;
  insert into public.case_notes(task_id, author, body) values (s.task_id, left(trim(p_author), 40), left(trim(p_body), 1000));
  return 'ok';
end $$;
revoke all on function public.add_share_note(text, text, text) from public;
grant execute on function public.add_share_note(text, text, text) to anon, authenticated;

-- notes nobody kept are deleted after 90 days, like helper links
select cron.schedule('sorted-notes-retention', '17 5 * * *', $$delete from public.case_notes where created_at < now() - interval '90 days'$$)
where not exists (select 1 from cron.job where jobname = 'sorted-notes-retention');
