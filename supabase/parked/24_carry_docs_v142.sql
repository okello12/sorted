-- v142. Live and staging.
-- 1. A guest's kept documents follow their cases to the email account. claim_carry() records the move (old and new
--    user, and any case ids the page changed) before it deletes the guest, and asks originals-cleanup to move the files
--    straight away. Until the move is done, and for a day after it, the nightly clean-up leaves those files alone.
create table if not exists public.doc_moves (
  id bigserial primary key,
  from_uid uuid not null,
  to_uid uuid not null,
  pairs jsonb not null default '[]'::jsonb,
  created timestamptz not null default now(),
  done_at timestamptz,
  tries int not null default 0
);
alter table public.doc_moves enable row level security;
revoke all on public.doc_moves from public, anon, authenticated;

create or replace function public.sorted_kick_moves() returns bigint
language sql security definer set search_path = '' as $$
  select net.http_post(
    url := 'https://boxrwcuhxmimayaxzywu.supabase.co/functions/v1/originals-cleanup',
    headers := jsonb_build_object('Content-Type','application/json','x-cron-secret',(select decrypted_secret from vault.decrypted_secrets where name='sorted_cron_secret')),
    body := '{"moves_only":true}'::jsonb,
    timeout_milliseconds := 20000)
$$;
revoke all on function public.sorted_kick_moves() from public, anon, authenticated;

create or replace function public.claim_carry(p_token text, p_pairs jsonb default '[]'::jsonb)
returns boolean language plpgsql security definer set search_path = '' as $$
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
  if exists (select 1 from storage.objects o where o.bucket_id = 'originals' and o.name like a::text || '/%') then
    insert into public.doc_moves(from_uid, to_uid, pairs) values (a, auth.uid(), case when jsonb_typeof(p_pairs) = 'array' then p_pairs else '[]'::jsonb end);
    begin perform public.sorted_kick_moves(); exception when others then null; end;
  end if;
  delete from auth.users where id = a and is_anonymous;
  return true;
end $$;
revoke all on function public.claim_carry(text, jsonb) from public, anon;
grant execute on function public.claim_carry(text, jsonb) to authenticated;

-- For originals-cleanup (service role): the moves waiting, the files under one person's folder, and marking a move.
create or replace function public.doc_moves_pending(p_limit int default 20)
returns table(id bigint, from_uid uuid, to_uid uuid, pairs jsonb) language sql security definer set search_path = '' as $$
  update public.doc_moves m set tries = m.tries + 1
  where m.id in (select d.id from public.doc_moves d where d.done_at is null and d.tries < 20 and d.created > now() - interval '14 days' order by d.id limit greatest(1, least(p_limit, 100)))
  returning m.id, m.from_uid, m.to_uid, m.pairs
$$;
create or replace function public.originals_under(p_uid uuid)
returns table(name text) language sql stable security definer set search_path = '' as $$
  select o.name from storage.objects o where o.bucket_id = 'originals' and o.name like p_uid::text || '/%' order by o.name limit 2000
$$;
create or replace function public.doc_move_done(p_id bigint) returns void language sql security definer set search_path = '' as $$
  update public.doc_moves set done_at = now() where id = p_id
$$;
revoke all on function public.doc_moves_pending(int) from public, anon, authenticated;
revoke all on function public.originals_under(uuid) from public, anon, authenticated;
revoke all on function public.doc_move_done(bigint) from public, anon, authenticated;
grant execute on function public.doc_moves_pending(int), public.originals_under(uuid), public.doc_move_done(bigint) to service_role;

create or replace function public.originals_orphans(p_limit integer)
returns table(name text) language sql security definer set search_path = '' as $$
  select o.name from storage.objects o
  where o.bucket_id = 'originals' and o.created_at < now() - interval '1 hour'
    and not exists (select 1 from public.tasks t where t.id = split_part(o.name, '/', 2) and t.user_id::text = split_part(o.name, '/', 1))
    and not exists (select 1 from public.doc_moves m where
          (m.done_at is null and m.created > now() - interval '14 days' and m.from_uid::text = split_part(o.name, '/', 1))
       or (m.done_at > now() - interval '1 day' and m.to_uid::text = split_part(o.name, '/', 1)))
  order by o.created_at limit greatest(1, least(p_limit, 1000))
$$;

-- 2. Two reminders on one case due at the same minute (their promise and your step) no longer collide: one row per
--    promise or step. The old (task_id, kind, send_at) key is dropped once the v142 page is live.
create unique index if not exists reminders_task_kind_send_promise_key on public.reminders (task_id, kind, send_at, promise_id) nulls not distinct;

-- 3. The assistant: a ceiling of 500 answers a day across everyone, as well as each person's own limit.
create or replace function public.assistant_take(p_user uuid, p_limit integer)
returns boolean language plpgsql security definer set search_path = 'public' as $$
declare v int;
begin
  if (select coalesce(sum(n), 0) from public.assistant_usage where day = current_date) >= 500 then return false; end if;
  insert into public.assistant_usage(user_id, day, n) values (p_user, current_date, 1)
  on conflict (user_id, day) do update set n = public.assistant_usage.n + 1
  returning n into v;
  return v <= p_limit;
end $$;
