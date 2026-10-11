# Sorted: current status

One page, kept current with every release (test 118 fails if the release or fingerprint here is out of date).
History and reasons live in `docs/PLAN.md`; how things work lives in `CLAUDE.md`.

## Production

- **Release:** v168 (11 October 2026): from the external audit, every repair goes through the product safety rules
  (now `ps-3`: hedged, past and paused danger never cleared), and a model read from an unclear photo is doubted with
  Retake photo first, or not offered at all. Security advisories reviewed (`docs/SECURITY_ADVISORIES.md`). v167, from
  Baldwin's heating case, tapping "Something else" on a repair no longer
  wipes its name, and a repair saved with no name is named from its words. v166, from his vacuum cleaner walk: a product
  case asks only the safety question first, and the label can be photographed on the case. v165 asked for the label after a photo of the machine. v164, live
  since PR 77, retired Sorted's own repair checks, added ten makers and the Phase 1.5 audit fixes (`docs/PHASE1_5_AUDIT.md`).
- **Page fingerprint (sha1 of public/index.html):** 3c66c6198e514a7584b448810b6a05f9fb151178
- **Site:** https://sorted-pilot.vercel.app, deployed by Vercel from `main`; `live-pilot` is kept level with `main`.
- **Database:** Supabase `boxrwcuhxmimayaxzywu` (London, free plan, no backups). Staging: `ujwanxqrefziuxwfzeaj`.
- **Migrations applied (live and staging):** up to 28 (`supabase/parked/28_reminder_path_v149.sql`), and 30
  (`supabase/parked/30_product_steps_v163.sql`, the product step names; staging and live, 10 October 2026, through
  `apply_migration`). 29 (pg_net's schema) is still parked.
- **Edge functions:** send-reminders v15, inbound-email v9, resend-events v2, originals-cleanup v3, email-stop v3,
  case-assistant v2 (switched off: no `anthropic_api_key` in Vault), vapid-init v1.

## The pilot in numbers (9 October 2026, counts only)

16 people with a case, 42 cases, 18 guests, 1 email account, 2 reminder rows, 0 reminders ever sent, 0 phones with
lock-screen reminders. v149 is the first release aimed at that last gap.

## Open, by priority

- **P1:** a reminder reaching guests (v149 adds the choice; measure `reminder_path_chosen` against dated cases).
- **P1, owner:** backups (the free plan has none), the terms checked by a lawyer, a short DPIA for Sorted itself.
- **P2, owner:** a real iPhone VoiceOver and Android TalkBack pass (`docs/PHONE_CHECK.md`).
- **P2:** IndexedDB for the copy on this phone, if accounts grow past a few hundred long cases (v159 keeps unsent edits
  when storage is full; test 125 measures 100 and 500 cases).
- **P3, owner (one Run):** `supabase/parked/29_pg_net_schema_v158.sql` moves `pg_net` out of `public` (staging, then
  live, between reminder kicks). The connector's apply was cancelled; it needs the SQL editor's Run.

## Done since v149

v158 (10 October): the script policy has no `'unsafe-inline'`; the page's inline scripts are listed by hash
(`node tools/csp_hashes.js` after every build; test 124 fails otherwise). v159: a full phone copy keeps unsent edits
(test 125). v160: the ways-in cards take their accessible name from what they show (axe-core 4.14's label-in-name
rule; Dependabot's axe update can merge once this is in). Dependabot leaves the pinned readers and database library alone; old pull requests 18, 33 and 44 closed.

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
117 (the reminder choice), 118 (this page is current), 119 (one attention record), 120 (one saving record), 121 (the same writes as before), 122 (the same merges as before), 123 (the same reads as before), 124 (strict script policy), 125 (scale).
