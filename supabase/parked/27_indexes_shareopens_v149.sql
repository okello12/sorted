-- v149 (hardening). Live and staging.
-- 1. Indexes the Supabase performance adviser asked for: the delete-my-account cascade and the per-person lookups use
--    case_mail.user_id and push_subs.user_id.
create index if not exists case_mail_user_id_idx on public.case_mail (user_id);
create index if not exists push_subs_user_id_idx on public.push_subs (user_id);
-- 2. A share link refreshed twenty times is not twenty opens. An open counts once per link per 30 minutes; the days it
--    was opened on (open_days), first_at and last_at are kept as before. No fingerprinting: the token only.
create or replace function public.share_seen(p_token text)
returns void language plpgsql security definer set search_path to '' as $function$
declare tid text;
begin
  if p_token is null or char_length(p_token) < 24 then return; end if;
  select s.task_id into tid from public.shares s where s.token = p_token and s.updated_at > now() - interval '30 days';
  if tid is null then return; end if;
  insert into public.share_opens as o (task_id, opens, open_days, first_at, last_at) values (tid, 1, 1, now(), now())
  on conflict (task_id) do update set
    opens = o.opens + case when o.last_at < now() - interval '30 minutes' then 1 else 0 end,
    open_days = o.open_days + case when (o.last_at at time zone 'Europe/London')::date < (now() at time zone 'Europe/London')::date then 1 else 0 end,
    last_at = now();
end $function$;
