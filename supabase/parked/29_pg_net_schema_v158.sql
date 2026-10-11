-- Migration 29: pg_net out of the public schema (Supabase's security advisor: extension_in_public).
-- Rewritten 11 October 2026 after the release assurance dossier, before it was ever applied. The runbook with the
-- preflight evidence is docs/MIGRATION_29_RUNBOOK.md. Read it first.
--
-- What it does: pg_net can't be moved with ALTER EXTENSION ... SET SCHEMA (it isn't relocatable), so it is dropped and
-- created again with the extensions schema as its home. Its own objects (net.http_post, the request queue, the
-- response table) live in the net schema before and after. Sorted's only callers, sorted_kick_reminders,
-- sorted_kick_originals and sorted_kick_moves, name net.http_post in full with an empty search_path and are looked up
-- when they run, so they are not dropped and need no change. The full dependency walk of 11 October 2026 found 41
-- objects on both staging and live: 28 members and 12 of their own parts (toast tables, indexes, composite types,
-- column defaults, a check), all in net or pg_toast. Nothing outside pg_net depends on it.
--
-- What it loses: pg_net's own request queue and its log of past responses (net._http_response, which pg_net prunes by
-- itself). The script refuses to run unless the queue is empty, so no request in flight is lost.
--
-- Safety: everything runs in one transaction. Any failed check raises an error and rolls the whole thing back, so the
-- extension is either moved and checked, or left exactly as it was. Run it outside a reminder kick (the kick runs at
-- minutes ending in 0; run at a minute ending in 3 to 7).
begin;
set local lock_timeout = '5s';
set local statement_timeout = '60s';

do $pre$
declare v_schema text; v_ver text; v_queue bigint; v_foreign int;
begin
  select n.nspname, e.extversion into v_schema, v_ver
    from pg_extension e join pg_namespace n on n.oid = e.extnamespace where e.extname = 'pg_net';
  if v_schema is null then raise exception 'preflight: pg_net is not installed'; end if;
  if v_schema = 'extensions' then raise exception 'preflight: pg_net is already in extensions, nothing to do'; end if;
  if v_schema <> 'public' then raise exception 'preflight: pg_net is in %, expected public', v_schema; end if;
  if (select default_version from pg_available_extensions where name = 'pg_net') <> v_ver then
    raise exception 'preflight: the version that would be created (%) differs from the installed one (%)',
      (select default_version from pg_available_extensions where name = 'pg_net'), v_ver;
  end if;
  select count(*) into v_queue from net.http_request_queue;
  if v_queue > 0 then raise exception 'preflight: % request(s) still queued; wait a minute and run again', v_queue; end if;
  -- Every object that depends, directly or through others, on pg_net (all of pg_depend, no class excluded). Each one
  -- that isn't a member of the extension must be one of its own parts, in the net or pg_toast schema. Any object
  -- elsewhere, or of a kind this check can't place, refuses the migration. (DROP EXTENSION without CASCADE would also
  -- refuse; this check says why before anything is attempted.)
  with recursive ext as (select oid from pg_extension where extname = 'pg_net'),
  members as (select classid, objid from pg_depend where refclassid = 'pg_extension'::regclass and refobjid = (select oid from ext) and deptype = 'e'),
  closure(classid, objid, objsubid, depth) as (
    select d.classid, d.objid, d.objsubid, 1 from pg_depend d where d.refclassid = 'pg_extension'::regclass and d.refobjid = (select oid from ext)
    union
    select d.classid, d.objid, d.objsubid, c.depth + 1 from pg_depend d join closure c on d.refclassid = c.classid and d.refobjid = c.objid where c.depth < 10
  ),
  nm as (select distinct classid, objid, objsubid from closure c where not exists (select 1 from members m where m.classid = c.classid and m.objid = c.objid)),
  sch as (select case classid
      when 'pg_class'::regclass then (select relnamespace::regnamespace::text from pg_class where oid = objid)
      when 'pg_type'::regclass then (select typnamespace::regnamespace::text from pg_type where oid = objid)
      when 'pg_proc'::regclass then (select pronamespace::regnamespace::text from pg_proc where oid = objid)
      when 'pg_attrdef'::regclass then (select k.relnamespace::regnamespace::text from pg_attrdef a join pg_class k on k.oid = a.adrelid where a.oid = objid)
      when 'pg_constraint'::regclass then (select connamespace::regnamespace::text from pg_constraint where oid = objid)
      when 'pg_rewrite'::regclass then (select k.relnamespace::regnamespace::text from pg_rewrite r join pg_class k on k.oid = r.ev_class where r.oid = objid)
      when 'pg_trigger'::regclass then (select k.relnamespace::regnamespace::text from pg_trigger t join pg_class k on k.oid = t.tgrelid where t.oid = objid)
      when 'pg_policy'::regclass then (select k.relnamespace::regnamespace::text from pg_policy p join pg_class k on k.oid = p.polrelid where p.oid = objid)
      else 'unclassified' end s from nm)
  select count(*) into v_foreign from sch where s is null or s not in ('net', 'pg_toast');
  if v_foreign > 0 then raise exception 'preflight: % object(s) outside pg_net depend on it; see the runbook', v_foreign; end if;
  if (select count(*) from pg_proc where proname in ('sorted_kick_reminders', 'sorted_kick_originals', 'sorted_kick_moves')) <> 3 then
    raise exception 'preflight: the three kick functions are not all present';
  end if;
  raise notice 'preflight passed: pg_net % in public, queue empty, no outside dependents', v_ver;
end
$pre$;

drop extension pg_net;
create extension pg_net with schema extensions;

do $post$
declare v_schema text; v_ver text;
begin
  select n.nspname, e.extversion into v_schema, v_ver
    from pg_extension e join pg_namespace n on n.oid = e.extnamespace where e.extname = 'pg_net';
  if v_schema is distinct from 'extensions' then raise exception 'postcheck: pg_net is in %, expected extensions', v_schema; end if;
  if to_regprocedure('net.http_post(text,jsonb,jsonb,jsonb,integer)') is null then raise exception 'postcheck: net.http_post is missing'; end if;
  if to_regclass('net.http_request_queue') is null then raise exception 'postcheck: the request queue is missing'; end if;
  if not has_function_privilege('postgres', 'net.http_post(text,jsonb,jsonb,jsonb,integer)', 'execute') then
    raise exception 'postcheck: postgres can no longer call net.http_post';
  end if;
  if (select count(*) from pg_proc where proname in ('sorted_kick_reminders', 'sorted_kick_originals', 'sorted_kick_moves')) <> 3 then
    raise exception 'postcheck: a kick function went missing';
  end if;
  raise notice 'postcheck passed: pg_net % in extensions, net.http_post callable, kick functions present', v_ver;
end
$post$;

commit;
