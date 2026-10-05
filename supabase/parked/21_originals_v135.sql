-- Sorted v135: keep the original documents (photos, screenshots, PDFs) with a case, only when the person taps
-- "Keep a document with this case". A private storage bucket, one folder per person and case:
-- originals/<user id>/<case id>/<time>-<file name>. Only the owner can add, open (through a link that lasts 5 minutes)
-- or remove their files; nobody else, and no public links. 10 MB a file, 200 files a person, images and PDFs only.
-- A file goes when its case goes: the daily job sorted-originals-cleanup asks the originals-cleanup function to remove
-- files whose case no longer exists (deleted by the person, by the retention rules, or with the account).
-- Apply to live and staging (the cleanup job only on live, where the cron secret exists).

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('originals', 'originals', false, 10485760,
        array['image/jpeg','image/png','image/webp','image/heic','image/heif','application/pdf'])
on conflict (id) do update set public = false, file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists "originals: own read" on storage.objects;
drop policy if exists "originals: own add" on storage.objects;
drop policy if exists "originals: own remove" on storage.objects;
create policy "originals: own read" on storage.objects for select to authenticated
  using (bucket_id = 'originals' and (storage.foldername(name))[1] = (select auth.uid())::text);
create policy "originals: own add" on storage.objects for insert to authenticated
  with check (bucket_id = 'originals'
    and (storage.foldername(name))[1] = (select auth.uid())::text
    and exists (select 1 from public.tasks t where t.id = (storage.foldername(name))[2] and t.user_id = (select auth.uid()))
    and (select count(*) from storage.objects o where o.bucket_id = 'originals' and (storage.foldername(o.name))[1] = (select auth.uid())::text) < 200);
create policy "originals: own remove" on storage.objects for delete to authenticated
  using (bucket_id = 'originals' and (storage.foldername(name))[1] = (select auth.uid())::text);

-- Files whose case has gone (names only, never what is in them). For the cleanup function, which uses the service role.
create or replace function public.originals_orphans(p_limit int) returns table(name text)
language sql security definer set search_path to '' as $$
  select o.name from storage.objects o
  where o.bucket_id = 'originals' and o.created_at < now() - interval '1 hour'
    and not exists (select 1 from public.tasks t where t.id = split_part(o.name, '/', 2) and t.user_id::text = split_part(o.name, '/', 1))
  order by o.created_at limit greatest(1, least(p_limit, 1000))
$$;
revoke all on function public.originals_orphans(int) from public, anon, authenticated;
grant execute on function public.originals_orphans(int) to service_role;

create or replace function public.sorted_kick_originals() returns bigint
language sql security definer set search_path to '' as $$
  select net.http_post(
    url := 'https://boxrwcuhxmimayaxzywu.supabase.co/functions/v1/originals-cleanup',
    headers := jsonb_build_object('Content-Type','application/json','x-cron-secret',(select decrypted_secret from vault.decrypted_secrets where name='sorted_cron_secret')),
    body := '{}'::jsonb,
    timeout_milliseconds := 20000)
$$;
revoke all on function public.sorted_kick_originals() from public, anon, authenticated;

-- Live only:
-- select cron.schedule('sorted-originals-cleanup', '27 3 * * *', $$select public.sorted_kick_originals()$$);
