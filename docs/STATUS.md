# Sorted: current status

One page, kept current with every release (test 118 fails if the release or fingerprint here is out of date).
History and reasons live in `docs/PLAN.md`; how things work lives in `CLAUDE.md`.

## Production

- **Release:** v150 (9 October 2026)
- **Page fingerprint (sha1 of public/index.html):** 3bca8105a5a9279730e55064c43985dc48935acb
- **Site:** https://sorted-pilot.vercel.app, deployed by Vercel from `main`; `live-pilot` is kept level with `main`.
- **Database:** Supabase `boxrwcuhxmimayaxzywu` (London, free plan, no backups). Staging: `ujwanxqrefziuxwfzeaj`.
- **Migrations applied (live and staging):** up to 28 (`supabase/parked/28_reminder_path_v149.sql`).
- **Edge functions:** send-reminders v15, inbound-email v9, resend-events v2, originals-cleanup v3, email-stop v3,
  case-assistant v2 (switched off: no `anthropic_api_key` in Vault), vapid-init v1.

## The pilot in numbers (9 October 2026, counts only)

16 people with a case, 42 cases, 18 guests, 1 email account, 2 reminder rows, 0 reminders ever sent, 0 phones with
lock-screen reminders. v149 is the first release aimed at that last gap.

## Open, by priority

- **P1:** a reminder reaching guests (v149 adds the choice; measure `reminder_path_chosen` against dated cases).
- **P1, owner:** backups (the free plan has none), the terms checked by a lawyer, a short DPIA for Sorted itself.
- **P2:** the architecture extraction (attention first: Home, reminders and the case page asking one function), done
  subsystem by subsystem with the existing tests as characterisation tests and no intended change on screen.
- **P2, owner:** a real iPhone VoiceOver and Android TalkBack pass (`docs/PHONE_CHECK.md`).
- **P2:** pressure at 100 and 500 cases with long histories; IndexedDB before localStorage quotas bite.
- **P3:** a strict CSP without `'unsafe-inline'` (belongs inside the extraction); moving `pg_net` out of `public`.

## Done since v149

The CI gate (9 October 2026): actions and Playwright pinned, Dependabot, the staging suite running for real with a
grants matrix and cross-person checks, staging made level with live (`supabase/staging/02_parity_v149.sql`), and a
ruleset on `main` requiring a pull request with regression, WebKit, Firefox and staging green.

## Next approved change

The attention extraction, step 2. Step 1 (v150): `attention(t)` is the one record Home, the case page, quick
answers and the reminder question read during a draw; the old functions delegate to it. Step 2 moves the rules
themselves inside it (state, priority, why, the quick answer and the next step from one set of facts about the case),
with test 119 and the existing suite holding every answer still. No new features until the pilot shows dated
cases reaching their day with a working reminder.

## Permanent gates

77 (documents), 94 and 96 (dates and their source), 109 (check first), 115 (the garage), 116 (two obligations),
117 (the reminder choice), 118 (this page is current), 119 (one attention record).
