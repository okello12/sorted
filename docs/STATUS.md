# Sorted: current status

One page, kept current with every release (test 118 fails if the release or fingerprint here is out of date).
History and reasons live in `docs/PLAN.md`; how things work lives in `CLAUDE.md`.

## Production

- **Release:** v157 (10 October 2026)
- **Page fingerprint (sha1 of public/index.html):** 9f8919295dc6329bf154210b1b5bfd00a3a208cd
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

The attention extraction is finished (v150 to v153). `attention(t)` and its rules (`att151*`, `att152*`) are the only
place that decides state, priority, why a case leads, the quick answer, the next step, your own deadline, Later and
the reminder day; the old names are one-line calls to them and the old bodies are gone. Test 119 compares every field
with the page as it was at v152 (`tests/make_ref152.js`) on 1,872 variations. Saving and merging between devices is next, the same way. Step 1 (v154): `syncState(x)` and `syncOf(t)` answer
"where is this record saved?" for `syncText`, `syncAll`, `pendingRecs` and sign-out, checked by test 120 against the
v153 page on every flag combination. Step 2 (v155): the write path's decisions are
named and in one place (`savePlan155`, `saveOutcome155`, `conflictKind155`, `retryNeed155`, `retryDelay155`, with the
wrappers round `save()` and `retryPlan()` folded into `savePrep155` and `retryNeed155`); test 121 tells the same saving
story on v154 and compares every write and the final records. Step 3 (v156): the merge's decisions are a pure
function, `mergeRec156(mine, server, base, kind)`, and `mergeInto` applies it; test 122 compares it with v155 on 3,000
generated three-way changes. The read side (v157): `readKind157` decides what a copy read from the server means
(redel, revive, skip, gone, new, own, merge, adopt) and `ap143` acts on it, with the v145 wrappers folded in; test 123
applies 1,458 combinations of phone state and server copy on v156 and on this page. The saving extraction is done.

## Permanent gates

77 (documents), 94 and 96 (dates and their source), 109 (check first), 115 (the garage), 116 (two obligations),
117 (the reminder choice), 118 (this page is current), 119 (one attention record), 120 (one saving record), 121 (the same writes as before), 122 (the same merges as before), 123 (the same reads as before).
