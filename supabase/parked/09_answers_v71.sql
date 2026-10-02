-- Sorted v71: Undo for an answer given from a reminder email. Run after 07_scores_v69.sql, in the Supabase SQL editor.
-- It removes only the signed-in person's own row for that one promise from the company totals. Nothing else.
create or replace function public.drop_outcome(p_promise text)
returns void language sql security definer set search_path = public as $$
  delete from public.promise_outcomes where user_id = auth.uid() and promise_id = left(p_promise, 40);
$$;
revoke all on function public.drop_outcome(text) from public, anon;
grant execute on function public.drop_outcome(text) to authenticated;
