-- v158: pg_net out of the public schema (Supabase's security advisor: extension_in_public). pg_net can't be moved with
-- ALTER EXTENSION ... SET SCHEMA (it isn't relocatable), so it is dropped and created again in the extensions schema.
-- Its functions live in the net schema either way, and the kick functions call net.http_post by name when they run, so
-- nothing that uses it changes. A request already queued at that moment is lost; the reminder kick runs every 10 minutes
-- and claims each reminder before sending, so the next run sends anything that was waiting. Apply between kicks
-- (not on a :x0 minute). Staging first, then live.
drop extension if exists pg_net;
create extension pg_net with schema extensions;
