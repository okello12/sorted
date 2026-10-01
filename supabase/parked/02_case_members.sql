-- PARKED, NOT APPLIED. See docs/LATER.md, item "Share a case with roles".
-- A helper is invited by email to ONE case. Roles: 'view' (sees the case) or 'note' (can add a note).
-- Helpers never edit the case record itself; their notes live in case_notes and the owner's app shows them.
create table if not exists public.case_members (
  task_id text not null references public.tasks(id) on delete cascade,
  owner_id uuid not null references auth.users(id) on delete cascade,
  email text not null check (position('@' in email) > 1),
  member_id uuid references auth.users(id) on delete cascade,      -- set when they accept, signed in with that email
  role text not null default 'view' check (role in ('view','note')),
  invited_at timestamptz not null default now(),
  accepted_at timestamptz,
  removed_at timestamptz,
  primary key (task_id, email)
);
create table if not exists public.case_notes (
  id uuid primary key default gen_random_uuid(),
  task_id text not null references public.tasks(id) on delete cascade,
  author_id uuid not null references auth.users(id) on delete cascade,
  body text not null check (char_length(body) between 1 and 2000),
  created_at timestamptz not null default now()
);
alter table public.case_members enable row level security;
alter table public.case_notes enable row level security;
-- owner manages members; a member sees their own membership
create policy case_members_owner on public.case_members for all to authenticated
  using (owner_id = (select auth.uid())) with check (owner_id = (select auth.uid()));
create policy case_members_self_read on public.case_members for select to authenticated
  using (member_id = (select auth.uid()) and removed_at is null);
-- notes: owner and accepted 'note' members can read; only accepted 'note' members (or the owner) can add
create policy case_notes_read on public.case_notes for select to authenticated using (
  exists (select 1 from public.tasks t where t.id = task_id and t.user_id = (select auth.uid()))
  or exists (select 1 from public.case_members m where m.task_id = case_notes.task_id and m.member_id = (select auth.uid()) and m.accepted_at is not null and m.removed_at is null));
create policy case_notes_add on public.case_notes for insert to authenticated with check (
  author_id = (select auth.uid()) and (
    exists (select 1 from public.tasks t where t.id = task_id and t.user_id = (select auth.uid()))
    or exists (select 1 from public.case_members m where m.task_id = case_notes.task_id and m.member_id = (select auth.uid()) and m.role = 'note' and m.accepted_at is not null and m.removed_at is null)));
-- Still to design before applying: the accept flow (RPC that sets member_id when the signed-in email matches),
-- what a 'view' member sees (reuse the share card, not the raw case), notice text, and the invite email.
