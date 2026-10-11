# Supabase security advisories: what each one means for Sorted

Reviewed 11 October 2026 on live (`boxrwcuhxmimayaxzywu`), after the external audit. Re-run `get_advisors` (security)
after every migration and compare it with this page. The review read function definitions and grants only. It never
read case content.

## Needs action

| Advisory | What to do | Who |
|---|---|---|
| `pg_net` installed in `public` | Run `supabase/parked/29_pg_net_schema_v158.sql` in the SQL editor: staging first, then live, between reminder kicks (STATUS P3) | Baldwin (one Run) |

## Reviewed and intended

**SECURITY DEFINER functions callable without signing in (6).**
- `get_share`, `share_seen`, `helper_respond` and `add_share_note` are the helper link. Each one works only with the
  link's secret token, and a switched-off link stops working.
- `report_page_error` and `report_auth_error` take error codes only. They are capped (300 an hour) and never take case words.

**SECURITY DEFINER functions callable when signed in (26).** Every one does one of these:
- reads `auth.uid()` and acts only on the caller's own rows: `claim_carry`, `stash_carry`, `case_reply_address`,
  `delete_my_account`, `drop_outcome`, `record_outcome`, `inbound_address_new`, `my_inbound_address_get`,
  `invite_helper`, `remove_helper`, `push_save`, `push_drop`, `push_state`, `set_email_optout`, `touch_seen`;
- checks the admin list (`pilot_health`, `pilot_metrics`) through `is_pilot_admin()`, which matches the signed-in
  email from the session (anonymous guests have none);
- returns only totals with a minimum of 5 promises from 3 people (`company_scores`), or a yes or no about whether
  email is set up (`email_reminders_ready`);
- or is one of the token and error-code functions above.

Server-only functions (`claim_due_reminders`, `doc_moves_pending`, `originals_under`, `push_vapid_init`,
`sorted_secret` and the others) can't be called by either role.

**Tables with row level security and no policies (13).** These tables are reached only by server functions and the
service role, never by the page directly. No policy means nobody can read or write them through the API.

**"Anonymous access policies" (tasks, reminders, shares, inbound items, case mail and notes, helpers, email
opt-outs, kept documents).** Sorted's guests are anonymous sign-ins on purpose. Every one of these policies limits a
row to its own `auth.uid()`, and the staging suite's grants matrix checks that one person can't reach another
person's rows. `cron.job` and `cron.job_run_details` are Supabase's own defaults.

**Leaked password protection.** Doesn't apply: Sorted signs people in with emailed codes only (`signInWithOtp`,
`verifyOtp`). There are no passwords.

## Small hardening, not urgent

`add_share_note`, `company_scores`, `drop_outcome` and `record_outcome` set `search_path=public`, where the rest set
it empty and name their schemas. This is safe as it is, because `public` holds only Sorted's own objects. Move them to
an empty path the next time one of them is changed.
