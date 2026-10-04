-- Sorted v117 (Phase 2): two more step names for the shared case structure, codes only.
-- turn_recorded  props {turn: theirs | yours | both}   whose move the person said it was
-- goal_recorded  props {own: true | false}             the outcome wanted was kept (own words, or Sorted's proposal)
-- Applied to live and staging on 4 October 2026.
alter table public.pilot_events drop constraint if exists pilot_events_name_check;
alter table public.pilot_events add constraint pilot_events_name_check check (name = any (array[
  'case_started','baseline_action_recorded','promise_created','email_added_at_promise','promise_due_return',
  'outcome_kept','outcome_missed','outcome_rescheduled','chase_used','new_promise_after_miss','case_closed',
  'recap_copied','second_case_started','moment_created','moment_item','moment_opened',
  'turn_recorded','goal_recorded']));
