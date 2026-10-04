-- Sorted v121 (remediation, Phase A item 1): step names for reading a photo or PDF of a notice. Codes only: never the
-- text read, never a PCN number.
-- document_read_started     props {expect: pcn | any | document, pdf: bool}
-- document_read_succeeded   props {expect, fields: n}                   the expected fields found (0 outside the notice flow)
-- document_read_partial     props {expect, fields: n}                   some found, the rest left blank for the person
-- document_read_failed      props {expect, words: n, conf: n} or {expect, reason: notpcn}
-- document_review_confirmed props {expect, fields: n, changed: n}      "These are right, continue"; changed = fields the person edited
-- document_manual_fallback  props {expect}                              "Enter the details manually"
-- Applied to live and staging on 4 October 2026.
alter table public.pilot_events drop constraint if exists pilot_events_name_check;
alter table public.pilot_events add constraint pilot_events_name_check check (name = any (array[
  'case_started','baseline_action_recorded','promise_created','email_added_at_promise','promise_due_return',
  'outcome_kept','outcome_missed','outcome_rescheduled','chase_used','new_promise_after_miss','case_closed',
  'recap_copied','second_case_started','moment_created','moment_item','moment_opened',
  'turn_recorded','goal_recorded',
  'document_read_started','document_read_succeeded','document_read_partial','document_read_failed',
  'document_review_confirmed','document_manual_fallback']));
