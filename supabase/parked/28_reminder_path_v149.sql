-- v149. Live and staging. A usage record for the reminder path a person chose for a dated case: a code only
-- (props.how: email, calendar, phone or none), so the pilot can see what share of dated cases have any reminder at all.
alter table public.pilot_events drop constraint pilot_events_name_check;
alter table public.pilot_events add constraint pilot_events_name_check check (name = any (array[
  'case_started','baseline_action_recorded','promise_created','email_added_at_promise','promise_due_return','outcome_kept',
  'outcome_missed','outcome_rescheduled','chase_used','new_promise_after_miss','case_closed','recap_copied','second_case_started',
  'moment_created','moment_item','moment_opened','turn_recorded','goal_recorded','document_read_started','document_read_succeeded',
  'document_read_partial','document_read_failed','document_review_confirmed','document_manual_fallback','reminder_path_chosen']::text[]));
