-- v163. Live and staging. Usage records for the product journey (docs/PRODUCT_PHASE1.md): step names only, with props
-- that are codes and counts (source, kind of product, route, how many rules matched). Never a brand, model, serial,
-- shop, date, OCR text or the person's words. The page records these only from v163, after this is applied.
alter table public.pilot_events drop constraint pilot_events_name_check;
alter table public.pilot_events add constraint pilot_events_name_check check (name = any (array[
  'case_started','baseline_action_recorded','promise_created','email_added_at_promise','promise_due_return','outcome_kept',
  'outcome_missed','outcome_rescheduled','chase_used','new_promise_after_miss','case_closed','recap_copied','second_case_started',
  'moment_created','moment_item','moment_opened','turn_recorded','goal_recorded','document_read_started','document_read_succeeded',
  'document_read_partial','document_read_failed','document_review_confirmed','document_manual_fallback','reminder_path_chosen',
  'product_flow_started','product_candidate_found','product_read_failed','product_confirmed','purchase_confirmed',
  'safety_stopped','official_support_shown','resolution_route_shown','contact_prepared']::text[]));
