# Working on Sorted

Read this first. Then `docs/LATER.md` for what is parked and why.

## What Sorted is

A UK research pilot at https://sorted-pilot.vercel.app, run by Baldwin Thompson-Addo (contact kofiniiakwei@gmail.com).
Sorted is the place a problem goes when someone else owes you the next move. The core object is the **promise**: who
said what, by when, with which reference. Home shows only Needs you, Waiting and Done. The north star is Due Return
Rate: do people come back to the same case when a promise falls due?

## Rules that don't bend

- **No person running the pilot reads case content.** Never select case content (`tasks.data`, `inbound_items.body`,
  `shares.card`) from the database. Counts, timestamps and definitions only. Only `send-reminders` and the retention
  jobs touch `tasks.data`, automatically. The privacy notice promises this.
- **Not a to-do app.** Sorted is not where your tasks live. It is where an unresolved problem lives when somebody else
  owes you the next move. No areas, projects, tags, checklists or repeating to-dos. Your own moves exist only inside a
  case, in service of the promise (the "Remind me to do something" link on a case).
- **Sorted proposes, the person confirms.** Nothing about a case changes without a tap from its owner.
- **Keep advice thin and honest.** Say what Sorted doesn't know (the benefits and housing notes are the pattern). No legal advice.
- **Secrets live in Supabase Vault.** Read them by name. Never paste keys into code, chat or commits.
- **Copy style.** Plain British English, short sentences, no em dashes.

## How the page is built

One HTML file. `index.src.html` is the original. `build.js`, then `build7.js` up to the latest `buildN.js`, each apply
one release's changes in order (`node all.js` runs them).

Each layer:
- checks the sha1 of its input against the previous release;
- applies exact-count replacements with `R(old, new, count)`, so a missing or duplicated anchor fails the build;
- checks its output sha1 against `EXPECT`.

So a release only ships if its output is byte-for-byte the version that was tested.

To make a change, add `buildN+1.js` with the previous output sha as its base and `EXPECT=''`. Add it to `all.js`, build
and test, then pin `EXPECT` to the new sha.

## How it is deployed

Since 2 October 2026 the Vercel project `sorted-pilot` (team my-data-vault) **is linked to GitHub**: every push to `main`
on okello12/sorted builds and deploys to production (sorted-pilot.vercel.app) automatically. Treat a push to `main` as a
release. Build and run `sh tests/run.sh` before pushing, and pin `EXPECT` first.

Vercel runs `node all.js` with output directory `public` (settings in `vercel.json`). If any layer's fingerprint check
fails, the build fails and production stays on the last good deploy.

`vercel.json` holds the security headers, including the Content Security Policy. If the page starts loading anything
from a new origin (a script, font, API or image host), add it to the CSP there and rerun `tests/13_csp.py`.

Work on a branch and merge to `main` when it's ready; keep `live-pilot` level with `main` after each release.
The old manual route (Vercel API `create_deployment` with files by sha1) still works if Git deploys ever stop.

## How it is tested

`sh tests/run.sh` from the repository root. It needs Python 3 with Playwright and Chromium, plus Node.

- The page runs against `tests/mock.js`, a stand-in for Supabase that keeps its database in localStorage, so tests never touch real data.
- The screenshot and PDF readers are served from `tests/node_modules`, the same versions the live site loads from jsDelivr.
- Every test file must end with `ERRORS []` and `FAILS []`.
- Tests 08 to 11 build dates relative to today (`tests/dates.py`), so they don't go stale. All tests run on London time
  (`dates.py` and `run.sh` set `TZ`), so a run near midnight on a UTC machine doesn't compare two different days.
- `14_promise_stress.py` holds every sentence from the stress tests (false promises and real ones), run through the UI.
- `17_corpus.py` runs `tests/corpus.py` (374 sentences and messages, including messy real-world writing with exact
  date checks) straight through `readCase()`, on a test-only copy of the page that exposes the reader
  (`tests/make_reader.js` writes `tests/out/reader.html`; production is untouched). Add new language there.
  The rule: no commitment from another party, no promise card. Instructions, information, conditionals and maybes are not commitments.

## Pinned versions

The screenshot and PDF readers load fixed versions with integrity hashes. Change them together, in three places:
- the page: `OCRV` (Tesseract 5.1.1, build35) and `PDFV` (pdf.js 3.11.174, build36); English data `@tesseract.js-data/eng` 1.0.0;
- `tests/package.json` and `tests/package-lock.json`;
- the routes in the tests that serve those files.

The database library (`@supabase/supabase-js` 2.117.2, build38) also has an integrity hash. To change its version, update
the URL and hash in a new layer and the version in `tests/package.json`; `12_audit_fixes.py` checks the hash against the
npm file. Tests swap in `tests/mock.js` for it, so `run.sh` serves a copy of the page without that one hash
(`tests/out/index.html`). The fonts are served from `public/fonts/`, so nothing loads from Google.

`isEvalSupported:false` in `pdfToText()` must never be removed. It is what protects pdf.js 3 from CVE-2024-4367.
Upgrading to pdf.js 4 or later is the longer-term fix (it ships as ES modules, so the loader changes).

## Backend

Supabase project `boxrwcuhxmimayaxzywu` (London). Row level security is on every table.

| Area | What's there |
|---|---|
| Edge functions | `send-reminders` v8 (every 10 minutes from pg_cron; claims each reminder before sending), `inbound-email` (off since v28), `email-stop` |
| Step records | `pilot_events` (a fixed step name, IDs and a time) |
| Metrics | `pilot_metrics()` and `pilot_health()`, admin only |
| Retention jobs | Cases 90 days idle (30 without an email), unless a promise is live; helper links stop working after 30 days and are deleted after 90; inbound items 30 days; `ops_errors` 90 days; anonymous accounts 30 days idle; email accounts with no cases 12 months without a sign-in (not pilot admins); carry tokens 1 day; step records 12 months |
| Applied 2 Oct 2026 | `supabase/parked/04_reliability_v39.sql`: safe date parsing in retention, reminder claiming, reminder and case-size caps |
| Applied 2 Oct 2026 | `supabase/parked/05_remaining_v41.sql`: helper invite log and stop list, forwarding addresses removed, narrower grants, faster policies, carry and idle-account clean-up |
| Schema | `supabase/schema_snapshot.sql`, structure only |
| Parked changes | `supabase/parked/`, written but not applied |

## Where things are in the page code

| Feature | Location |
|---|---|
| Reading the first sentence: company, reference, item, how long | `caseFacts()` and `PARTIES`, `BENEFITS`, `ITEMS` (build30 to build32) |
| Promise from a sentence | `suggestPromise()` (build33, rules tightened in build39, build43, build49 and build50: `PNEG`, `PTENT`, `PTMSG`, `PINFO`, `PIMP`, `PSAIDDO`, `PDAY`, `PCHG`, `pWhenOk`, `pTwo`, `pNamed`, `pChanged`, `pNorm`) |
| Which reader the start box uses | `readCase()` (build50): one function for typed sentences, pasted messages and short notifications | |
| Promise from a pasted message | `sugFromMessage()` (build34) |
| The card | `sugCard()` and the `sug-yes`, `sug-edit` and `sug-no` actions |
| Screenshots and photos | `readPicture()` and `readImage()` (Tesseract, on the phone) |
| PDFs | `pdfToText()` (pdf.js with `isEvalSupported:false`) |
| Matching a message to an existing case | `matchCase()` (build36) |
| Chasing message wording | `callDefaults()` |
| The case page's single next step | `viewTask()` |
| Deleting one case | `case-del` action (build37) |
| "Sorted can't see what needs sorting" | `caseSignal()`, `vagueBlock()` (build39) |
| Accessibility pass after each render | `a11yPass()` (build37) |
| Home: spotlight case, Waiting rows, Also open, Done | `viewHome()`, `home44Spot()`, `home44Row()`, `home44Section()` (build44 to build48; the old `viewHomeLegacy()` is unused) |
| Share into Sorted (`/#new=<text>`, the Apple Shortcut) | `grabShared()` (build40); setup in `docs/SHARE_SHORTCUT.md` |
| Saving (one save at a time) | `save()` with `_saving` and `_again` (build37) |
