# Working on Sorted

Read this first. Then `docs/LATER.md` for what is parked and why.

## What Sorted is

A UK research pilot at https://sorted-pilot.vercel.app, run by Baldwin Thompson-Addo (contact kofiniiakwei@gmail.com).
Sorted is the place a problem goes when someone else owes you the next move. The core object is the **promise**: who
said what, by when, with which reference. Home shows only Needs you, Waiting and Done. The north star is Due Return
Rate: do people come back to the same case when a promise falls due?

## Rules that don't bend

- **Nobody running the pilot reads cases.** Never select case content (`tasks.data`, `inbound_items.body`, share cards)
  from the database. Counts, timestamps and definitions only. The privacy notice promises this.
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

Vercel project `sorted-pilot` (team my-data-vault) is **not** linked to Git. Pushing to GitHub does not deploy.

Deploys go through the Vercel API (`create_deployment`):
- Files already uploaded are referenced by sha1 and size.
- New layers go inline.
- Settings: `buildCommand: node all.js`, `outputDirectory: public`, `framework: null`, `target: production`.

If a layer's fingerprint check fails, the deploy fails rather than shipping something untested.

After deploying, commit and push to both `live-pilot` and `main` on okello12/sorted.

## How it is tested

`sh tests/run.sh` from the repository root. It needs Python 3 with Playwright and Chromium, plus Node.

- The page runs against `tests/mock.js`, a stand-in for Supabase that keeps its database in localStorage, so tests never touch real data.
- The screenshot and PDF readers are served from `tests/node_modules`, the same versions the live site loads from jsDelivr.
- Every test file must end with `ERRORS []` and `FAILS []`.

## Backend

Supabase project `boxrwcuhxmimayaxzywu` (London). Row level security is on every table.

| Area | What's there |
|---|---|
| Edge functions | `send-reminders` (every 10 minutes from pg_cron), `inbound-email` (off since v28), `email-stop` |
| Step records | `pilot_events` (a fixed step name, IDs and a time) |
| Metrics | `pilot_metrics()` and `pilot_health()`, admin only |
| Retention jobs | Cases 90 days idle (30 without an email), unless a promise is live; shares 90 days; step records 12 months |
| Schema | `supabase/schema_snapshot.sql`, structure only |
| Parked changes | `supabase/parked/`, written but not applied |

## Where things are in the page code

| Feature | Location |
|---|---|
| Reading the first sentence: company, reference, item, how long | `caseFacts()` and `PARTIES`, `BENEFITS`, `ITEMS` (build30 to build32) |
| Promise from a sentence | `suggestPromise()` (build33) |
| Promise from a pasted message | `sugFromMessage()` (build34) |
| The card | `sugCard()` and the `sug-yes`, `sug-edit` and `sug-no` actions |
| Screenshots and photos | `readPicture()` and `readImage()` (Tesseract, on the phone) |
| PDFs | `pdfToText()` (pdf.js with `isEvalSupported:false`) |
| Matching a message to an existing case | `matchCase()` (build36) |
| Chasing message wording | `callDefaults()` |
| The case page's single next step | `viewTask()` |
