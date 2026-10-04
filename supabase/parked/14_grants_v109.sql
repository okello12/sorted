-- v109: the anon role had full table privileges on case_mail and case_notes (row level security kept it out, but
-- nothing else did). Take them away; the page reads both only when signed in, and the server functions are
-- security definer. Applied to live on 4 October 2026. Staging's 00_schema.sql grants the narrow set from the start.
revoke all on table public.case_mail from anon;
revoke all on table public.case_notes from anon;
