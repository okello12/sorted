-- The guest deletion rule (migration 15), checked on STAGING inside a transaction that is never committed.
-- Four guests who all signed in 40 days ago: 1 opens Sorted daily (seen yesterday), 2 has a live promise,
-- 3 has been away 31 days, 4 saved a case 10 days ago. Expected: only 3 would be deleted.
-- Run in the staging SQL editor (or through the Supabase API) and read the result; the rollback leaves nothing behind.
-- Last run: 4 October 2026 on ujwanxqrefziuxwfzeaj: 1 false, 2 false, 3 true, 4 false.
begin;
insert into auth.users (id, instance_id, aud, role, is_anonymous, created_at, updated_at, last_sign_in_at) values
 ('aaaaaaaa-0000-4000-8000-000000000001','00000000-0000-0000-0000-000000000000','authenticated','authenticated',true, now()-interval '40 days', now()-interval '40 days', now()-interval '40 days'),
 ('aaaaaaaa-0000-4000-8000-000000000002','00000000-0000-0000-0000-000000000000','authenticated','authenticated',true, now()-interval '40 days', now()-interval '40 days', now()-interval '40 days'),
 ('aaaaaaaa-0000-4000-8000-000000000003','00000000-0000-0000-0000-000000000000','authenticated','authenticated',true, now()-interval '40 days', now()-interval '40 days', now()-interval '40 days'),
 ('aaaaaaaa-0000-4000-8000-000000000004','00000000-0000-0000-0000-000000000000','authenticated','authenticated',true, now()-interval '40 days', now()-interval '40 days', now()-interval '40 days');
insert into public.user_seen (user_id, seen_at) values ('aaaaaaaa-0000-4000-8000-000000000001', now() - interval '1 day'), ('aaaaaaaa-0000-4000-8000-000000000003', now() - interval '31 days');
insert into public.tasks (id, user_id, data, updated_at) values
 ('ruleb0000001','aaaaaaaa-0000-4000-8000-000000000002', jsonb_build_object('id','ruleb0000001','title','t','board','waiting','promises',jsonb_build_array(jsonb_build_object('id','p1','status','open','dueAt',(now()+interval '5 days')))), now()-interval '40 days'),
 ('ruled0000001','aaaaaaaa-0000-4000-8000-000000000004', jsonb_build_object('id','ruled0000001','title','t','board','yours','promises','[]'::jsonb), now()-interval '10 days');
select right(u.id::text,1) as guest,
  (u.is_anonymous
    and coalesce(u.last_sign_in_at, u.created_at) < now() - interval '30 days'
    and coalesce((select s.seen_at from public.user_seen s where s.user_id = u.id), u.created_at) < now() - interval '30 days'
    and not exists (select 1 from public.tasks t where t.user_id = u.id
                    and (t.updated_at > now() - interval '30 days' or public.sorted_case_live(t.data)))) as would_be_deleted
from auth.users u where u.id::text like 'aaaaaaaa-%' order by 1;
rollback;
