-- PARKED, NOT APPLIED. See docs/LATER.md, item "Replies come back into the case".
-- Each case gets its own reply address (case-<random>@<inbound domain>), so a company's reply lands in that case
-- as a suggestion the person confirms. Stays OFF until the Vault secret 'case_replies_on' = 'yes'.
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
