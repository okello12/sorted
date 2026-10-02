-- Sorted v69: company scores. Run this once in the Supabase SQL editor.
-- When someone records that a promise was kept or missed, the page sends only: a company name from Sorted's fixed list,
-- kept or missed, and how they contacted them. Never case text. Nobody can read the rows; company_scores() returns
-- totals only, and only for a company with at least 5 promises from at least 3 different people.
create table if not exists public.promise_outcomes (
  id bigserial primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  promise_id text not null check (char_length(promise_id) <= 40),
  party text not null check (party in ('Currys','Amazon','Argos','John Lewis','AO','eBay','IKEA','Apple','Samsung','Dyson','Boots','Tesco','Sainsbury’s','Asda','BT','Virgin Media','Sky','EE','O2','Vodafone','British Gas','Octopus Energy','OVO','EDF','E.ON','Thames Water','Royal Mail','Evri','DPD','DHL','Ryanair','easyJet','HMRC','DVLA')),
  outcome text not null check (outcome in ('kept','missed')),
  via text check (via is null or via in ('phone','email','account','letter','app')),
  at timestamptz not null default now(),
  unique (user_id, promise_id)
);
alter table public.promise_outcomes enable row level security;  -- no policies: nobody reads rows directly
revoke all on public.promise_outcomes from anon, authenticated;

create or replace function public.record_outcome(p_promise text, p_party text, p_outcome text, p_via text)
returns void language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is null then return; end if;
  insert into public.promise_outcomes(user_id, promise_id, party, outcome, via)
  values (auth.uid(), left(p_promise, 40), p_party, p_outcome, nullif(p_via, ''))
  on conflict (user_id, promise_id) do update set outcome = excluded.outcome, via = excluded.via, at = now();
exception when check_violation then return;  -- not a company on the fixed list: nothing is stored
end $$;
revoke all on function public.record_outcome(text, text, text, text) from public, anon;
grant execute on function public.record_outcome(text, text, text, text) to authenticated;

create or replace function public.company_scores()
returns table(party text, kept int, missed int, people int, by_via jsonb)
language sql stable security definer set search_path = public as $$
  with o as (select * from public.promise_outcomes where at > now() - interval '12 months'),
  t as (select o.party, count(*) filter (where outcome = 'kept')::int kept, count(*) filter (where outcome = 'missed')::int missed, count(distinct user_id)::int people from o group by o.party),
  v as (select x.party, jsonb_object_agg(x.via, jsonb_build_object('kept', x.k, 'n', x.n)) by_via
        from (select o.party, o.via, count(*) filter (where o.outcome = 'kept')::int k, count(*)::int n from o where o.via is not null group by o.party, o.via having count(*) >= 5) x
        group by x.party)
  select t.party, t.kept, t.missed, t.people, coalesce(v.by_via, '{}'::jsonb)
  from t left join v using (party)
  where t.kept + t.missed >= 5 and t.people >= 3;
$$;
revoke all on function public.company_scores() from public, anon;
grant execute on function public.company_scores() to authenticated;

-- outcomes are deleted after 12 months, and straight away with the account (on delete cascade)
select cron.schedule('sorted-outcomes-retention', '57 4 * * *', $$delete from public.promise_outcomes where at < now() - interval '12 months'$$)
where not exists (select 1 from cron.job where jobname = 'sorted-outcomes-retention');
