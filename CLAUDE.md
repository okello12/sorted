# Working on Sorted

Read this first. Then `docs/LATER.md` for what is parked and why.

## What Sorted is

A UK research pilot at https://sorted-pilot.vercel.app, run by Baldwin Thompson-Addo (contact kofiniiakwei@gmail.com).
Sorted is the place a problem goes when someone else owes you the next move. The core object is the **promise**: who
said what, by when, with which reference. Home shows only Needs you, Waiting and Done. The north star is Due Return
Rate: do people come back to the same case when a promise falls due?

## Rules that don't bend

- **Sorted's assistant sends a case to Anthropic only when the person taps it.** The privacy notice says so. Never call the model from anywhere else, never log what is sent or returned.
- **No person running the pilot reads case content.** Never select case content (`tasks.data`, `inbound_items.body`,
  `shares.card`) from the database. Counts, timestamps and definitions only. Only `send-reminders` and the retention
  jobs touch `tasks.data`, automatically. The privacy notice promises this.
- **Not a to-do app.** Sorted is not where your tasks live. It is where an unresolved problem lives when somebody else
  owes you the next move. No areas, projects, tags, checklists or repeating to-dos. Your own moves exist only inside a
  case, in service of the promise (the "Remind me to do something" link on a case).
  One exception is under test since v99: the **Moving home** container groups cases and lists your own steps with an
  official link, "Done already" and "Not relevant". Those steps never get reminders, chase states or their own cases.
  Anything someone else owes you is a normal case. Measure it before adding another life moment.
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
Only `main` builds on Vercel (`git.deploymentEnabled` in `vercel.json`). Branch pushes and `live-pilot` make no
preview builds, because the account has a daily build limit and QA pushes used it up on 2 October 2026. Test locally
with `sh tests/run.sh`, not with preview deploys. If a production build is ever rate-limited, redeploy the `main` commit
through the Vercel API (`create_deployment` with `gitSource`) once the limit clears, rather than pushing again.
The old manual route (Vercel API `create_deployment` with files by sha1) still works if Git deploys ever stop.

## How it is tested

`sh tests/run.sh` from the repository root. It needs Python 3 with Playwright and Chromium, plus Node.

- The page runs against `tests/mock.js`, a stand-in for Supabase that keeps its database in localStorage, so tests never touch real data.
- The screenshot and PDF readers are served from `tests/node_modules`, the same versions the live site loads from jsDelivr.
- Every test file must end with `ERRORS []` and `FAILS []`.
- GitHub Actions runs `.github/workflows/ci.yml` on every pull request to `main` and after pushes to `main`; it runs the complete regression suite and checks the generated app is committed.
- Tests 08 to 11 build dates relative to today (`tests/dates.py`), so they don't go stale. All tests run on London time
  (`dates.py` and `run.sh` set `TZ`), so a run near midnight on a UTC machine doesn't compare two different days.
- `14_promise_stress.py` holds every sentence from the stress tests (false promises and real ones), run through the UI.
- `18_intake.py` covers every way into an existing case, including a real screenshot read by Tesseract.
- `44_guided_start.py` checks each start choice asks its own questions (promise, chase, call, broken), creates nothing until Start, turns the answers into one sentence for the normal reader, "I have a letter" leads with the photo button, "Pcn" alone asks for the notice, and "your own words" or "Choose something else" go back.
- `47_after_start.py` checks the first response on the eight hard examples (PCN, landlord damp, Currys refund, washing machine, council tax letter, passport, Aviva callback, BT broadband), that a demand on you is never their promise, renewals, a clean "Something else", and one case the whole way: promise, waiting, due, missed, chase, new promise, kept, done; and since v93 a typed renewal (no call form, a reminder to renew by its date) and a case with no date (ask for one).
- `48_name_only.py` checks a name alone ("From hmrc", "Got a letter from the council") asks what they sent and creates nothing, a few more words carry on normally, Start again carries on with the case named after them, an honest first response and a message that asks what it's about, and that real sentences are never asked.
- `49_explore.py` checks the broader door examples, the 32-example strip (each opens its flow and creates nothing), "See all and search" (no sideways scroll), that each example opens its flow with its question, placeholders and choice set (refund, landlord repair, parking, HMRC letter, council, passport, subscription), the line and fold on Home after a first case, and "Need help with something else?" on a finished case.
- `50_discovery.py` checks the Home line fits the last case (HMRC: letters, fines and forms; refund: complaints, subscriptions, deliveries), the search (DVLA, my landlord, Amazon refund, parcel, school application, and a miss offering "Tell Sorted what happened"), the case health line (missed date, days waiting, no reference) and one-tap endings that keep your own words.
- `51_partly_playbooks_moments.py` checks "Only partly" (what's outstanding, the chase, the step record, no company score), the refund, insurance claim and HMRC playbooks, the closing code, a promise with no company, a shared parking notice (what it looks like; understand, reply, remember once confirmed), and life moments (moving home, new baby; nothing created until Start).
- `52_moving_home.py` checks Moving home: four questions and nothing saved until the button, only what applies, Needs you and Coming up by date, official links, no percentages, Done already, Not relevant and Undo with no reminders, a case started inside it (normal promise, linked both ways, a tracked case with its ref), linking an existing case, a missed promise moving to Needs you, changing answers, and delete keeping cases.
- `53_pressure_core.py`, `54_pressure_moving_home.py` and `55_pressure_scale_accessibility.py` are the pressure tests from the unmerged `pressure-v99-20261003` branch (PR 17), kept unchanged as regression protection: hostile HTML, double submits, long text, corrupt cache, 320 to 430px, standalone Home and Refresh, several moves, 60 cases, keyboard, 125% text and dark mode. 54 still prints a FINDING because it looks for the life moments chip inside the first-visit chooser, which cap90 hides; the first-visit entry is `mom-start`, checked in 56.
- `56_unfinished_flows.py` checks the installed app's Home from a move, a case, the chase form and after Back and Forward; Moving home before any case, refresh before saving, a double tap, the same date again; typed text then Home; refresh mid-start; switching start choice; triple taps on Start; one move per case; a failed save kept and saved once when back online; and coming back from the background.
- `57_named_thing.py` checks a choice on the landing page opens its own questions after sign-in, a reload mid-start doesn't bring them back, "The screen is broken" (Screen kept, "Your screen isn't working", "What is it?" filled in, safety question still asked), Home after a case doesn't reopen the questions, and `thingOf()` on seven wordings.
- `58_semantic_memory.py` checks that what the person said survives: 20 things (known and unknown, "flux capacitor") in 12 wordings each keep the thing; promises keep who, ref, amount and window; typos and shorthand ("washine machine wont drain", "landlord sed engineer tuesday"); negation ("It's not the boiler. The thermostat is broken."); "said he would come but didn't" is a missed promise; danger words trigger and "no smoke or burning smell" does not; and in the interface: no blank "What is it?", "Which one?" for a screen, HMRC already filled in, and a missed promise recognised even when the broken door was chosen (the doors are hints). `tests/make_reader.js` also exposes `thingOf`, `looksUnsafe` and `typoFix`.
- `43_case_fixes.py` checks your own step on the Home spotlight with its button, the GOV.UK link on an existing renewal step, that a typed renewal is not turned into a to-do, "Ref" needing a digit, and complaint names.
- `40_visual_contrast.py` checks, in light and dark mode, that headings, rows, links and the case Ref meet 4.5 to 1 contrast, Needs you and Waiting have their own colours, the main button doesn't loop an animation, the landing examples match, and nothing scrolls sideways. Run it after any styling change.
- `39_ui_fixes.py` checks a promise that isn't a visit says "Due today" without "Show this" or "It didn't" before its time, the reference shows once, Home rows line up, and step 2 shows the name and Ref.
- `36_repair_playbook.py` checks the repair playbook: after a visit it asks if it's fixed, counts visits and no-shows, shows the refund right for something bought and the formal route after 2 visits, proposes the outcome, and leaves other cases as they were.
- `35_found.py` checks "Came in" on Home: replies and notes from any case, newest first, no words shown, each opens its case, and handled ones go at once.
- `34_reply_kinds.py` checks `readers.mjs` is fresh from the page, the kind of reply for each sample, that the reply email carries only the kind (no case, sender or words), and the return and notice on the page.
- `33_email_answers.py` checks Yes and No from a reminder email: recorded only after a fresh load, the chase ready after No, Undo restores the case and the totals, an old link changes nothing, your own step, and sign-in keeping the answer.
- `31_scores.py` checks only company, outcome and channel are sent, never for people or with step records off, and the totals' wording.
- `32_replies_notes.py` covers the case address in Cc, a reply shown as a proposal (add, or not about this case), and helper notes (switch, send, keep, off).
- `30_assistant.py` checks the assistant sends nothing until tapped, says what it sends, never changes the case on its own, and explains errors.
- `29_escalation.py` checks the next formal step by sector and that it only shows once a case has gone round.
- `28_case_tools.py` checks moving a message, hand-offs and your history with a company.
- `27_pack.py` checks the adviser pack's sections, saved questions, copy, the downloaded file and print view.
- `26_response.py` checks replies: acknowledgement changes nothing, a rejection is proposed with their reasons and the point they skipped, cancellation finishes, "No" leaves it.
- `25_builder.py` checks the challenge builder writes only what was ticked and confirmed, flags missing evidence, and keeps the sent text.
- `24_routes.py` checks the official pages for each kind of notice, stage and region.
- `23_playbook.py` walks a council case from ticket to tribunal deadline to paid, plus a private charge and a cancelled one, with dates relative to today.
- `22_case_facts.py` covers parking notices end to end: typed, pasted, a photo read by Tesseract, change, remove, confirm, a later Notice to Owner.
- `17_corpus.py` runs `tests/corpus.py` (374 sentences and messages, plus parking notices with every expected fact, including messy real-world writing with exact
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
| Edge functions | `case-assistant` v1 (Claude via the Anthropic API; key `anthropic_api_key` and optional `assistant_model` in Vault; 40 a day per person through `assistant_take`; checks the user itself, so verify_jwt is off; stores no case text), `send-reminders` v9 (every 10 minutes from pg_cron; claims each reminder before sending; an "after" reminder has Yes and No answer links, never case details), `inbound-email` v5 (signature first, To and Cc, `case-` replies only when the Vault secret `case_replies_on` is `yes`; personal forwarding stays off; since v72 it emails the owner the kind of reply, read by `readers.mjs`, which `tools/make_server_reader.js` writes from the page's `RS_NO`, `RS_YES`, `RS_ACK`. Regenerate it whenever those change. Deploy `index.ts` and `readers.mjs` together), `email-stop` |
| Step records | `pilot_events` (a fixed step name, IDs and a time) |
| Metrics | `pilot_metrics()` and `pilot_health()`, admin only |
| Retention jobs | Cases 90 days idle (30 without an email), unless a promise is live; helper links stop working after 30 days and are deleted after 90; inbound items 30 days; `ops_errors` 90 days; anonymous accounts 30 days idle; email accounts with no cases 12 months without a sign-in (not pilot admins); carry tokens 1 day; step records 12 months |
| Applied 2 Oct 2026 | `supabase/parked/04_reliability_v39.sql`: safe date parsing in retention, reminder claiming, reminder and case-size caps |
| Applied 2 Oct 2026 | `supabase/parked/05_remaining_v41.sql`: helper invite log and stop list, forwarding addresses removed, narrower grants, faster policies, carry and idle-account clean-up |
| Applied 2 Oct 2026 | `supabase/parked/06_assistant_v68.sql`: assistant usage counts, the 40-a-day gate and assistant error-source logging. The edge function is deployed; it remains intentionally unavailable until `anthropic_api_key` exists in Vault |
| Applied 2 Oct 2026 | `supabase/parked/07_scores_v69.sql`: privacy-preserving company outcome totals and retention |
| Applied 2 Oct 2026 | `supabase/parked/08_replies_notes_v70.sql`: case reply addresses, `case_replies_on=yes`, inbound case routing and helper notes |
| Applied 2 Oct 2026 | `supabase/parked/09_answers_v71.sql`: `drop_outcome()` for Undo from reminder-email answers |
| Applied 3 Oct 2026 | `supabase/parked/10_endings_v98.sql`: `pilot_metrics()` adds `endings` (case_closed `end` codes) and `miss.partly`. No new tables or columns |
| Applied 3 Oct 2026 | `supabase/parked/11_moments_v99.sql`: step names `moment_created`, `moment_item`, `moment_opened`; `pilot_metrics()` adds `moments` (created, people, returned, with a case, with two or more, item choices). No new tables |
| Schema | `supabase/schema_snapshot.sql`, structure only |
| Parked changes | `supabase/parked/` also contains the source SQL for migrations already applied. Do not rerun 04–11 just because the files remain in that folder; check the Applied rows above and the Supabase migration history first |

## Where things are in the page code

| Feature | Location |
|---|---|
| Reading the first sentence: company, reference, item, how long | `caseFacts()` and `PARTIES`, `BENEFITS`, `ITEMS` (build30 to build32) |
| Promise from a sentence | `suggestPromise()` (build33, rules tightened in build39, build43, build49 and build50: `PNEG`, `PTENT`, `PTMSG`, `PINFO`, `PIMP`, `PSAIDDO`, `PDAY`, `PCHG`, `pWhenOk`, `pTwo`, `pNamed`, `pChanged`, `pNorm`) |
| Which reader the start box uses | `readCase()` (build50): one function for typed sentences, pasted messages and short notifications |
| Bringing something into an existing case | `intakeRead()` and `evidence()` (build51): the paste panel and "Add to that case" both use them; the history line says where it came from (a screenshot, a PDF, shared from another app) |
| "What they sent" on a case | `evidenceBlock()`, `evidenceOf()`, `EVRE` (build52): read from the history lines, newest first, three shown | |
| Promise from a pasted message | `sugFromMessage()` (build34) |
| The card | `sugCard()` and the `sug-yes`, `sug-edit` and `sug-no` actions |
| Screenshots and photos | `readPicture()` and `readImage()` (Tesseract, on the phone) |
| PDFs | `pdfToText()` (pdf.js with `isEvalSupported:false`) |
| Matching a message to an existing case | `matchCase()` (build36) |
| Chasing message wording | `callDefaults()` |
| The case page | `viewTask()`, rebuilt in build57 and build58 around the next move: `moveCard()`, `case56Evidence()`, `case56Timeline()`, `case56Sharing()`, `case56ReminderFold()`, `case56More()`; build59 only checks the final fingerprint |
| Deleting one case | `case-del` action (build37) |
| "Sorted can't see what needs sorting" | `caseSignal()`, `vagueBlock()` (build39) |
| Accessibility pass after each render | `a11yPass()` (build37) |
| Home: spotlight case, Waiting rows, Also open, Done | `viewHome()`, `home44Spot()`, `home44Row()`, `home44Section()` (build44 to build48; the old `viewHomeLegacy()` is unused) |
| Share into Sorted (`/#new=<text>`, the Apple Shortcut) | `grabShared()` (build40); "Where does this go?" picker `shareBlock()`, `intakeAdd()` (build53); setup in `docs/SHARE_SHORTCUT.md` |
| Case names | `shortTitle()`; a message whose first line would be cut off or is a pleasantry is named from the company and topic by `namedTitle()` and `caseTopic()` (build56), and confirming a promise keeps that name |
| Home display titles | `home54Title()` (build54), also used by the share picker (build56) |
| Home spotlight question | `home55Question()` (build55); since build56 it also replaces the generic "Did they come?" and "Has the money arrived?" with the wording that fits |
| Case facts (resolution engine, release 1) | `pcnRead()` reads a parking notice on the phone (council PCN, Notice to Owner, TfL, private charge); `cfIn()` turns it into proposed facts with a source, from `evidence()` and case creation; `cfCheck()` asks "Are they right?", `cfBlock()` shows confirmed Case facts, `cfEdit()` changes or removes one (build60). Stored in `t.cf.f[key]` as `{v, iso, how, src, at, st}` with `st` proposed, confirmed or rejected. `pRec()` strips record lines ("Date of contravention: …") before the promise reader sees them |
| Parking playbook (release 2) | `pkStage()`, `pkDates()` (worked out on the safe side from confirmed facts; a date on the notice or one you set wins), `pkCard()`, `pkPanel()` (sent, rejected, paid, change a date), `pkDatesBlock()` (Dates that matter, What you sent). Waiting on them is an ordinary promise with `src:"parking"`; the "Remind me 2 days before" move has `src:"parking"` and sits inside the card (build61). State in `t.pk`: `stage`, `subs`, `dates`, `rejectedOn`, `rejFrom`, `ntoSeen` |
| Official routes (release 3) | `RT` registry and `RT_CHECKED` (build62): kind of notice, stage, region (London by borough name or TfL, England and Wales, Scotland and Northern Ireland folded), official link, purpose. `rtFor()` picks them, `rtBlock()` shows "Where to do it". Hand-checked; recheck every link before changing `RT_CHECKED`. Never generated |
| Challenge builder (release 4) | `BD_GROUNDS`, `BD_EVID`, `bdDraft()` (writes only from ticked reasons, the person's own words and confirmed facts; returns what it used), `bdCheck()` (completeness, never a chance of winning), `bdPanel()` (`pkbuild`, `pkdraft`) (build63). Answers kept in `t.pk.build`; "I've sent it" carries the exact text into the proof form |
| Response reader (release 5) | `rsRead()` classifies a reply (rejected, cancelled, acknowledgement) with `RS_NO`, `RS_YES`, `RS_ACK`; pulls their reasons; compares with `t.pk.build` (`RS_TOPIC`) to list points their reply skips; spots a re-offered reduced price. `rsIn()` proposes it as `t.pk.resp`, `rsCard()` asks, `rs-yes` moves the stage, `rsBlock()` keeps it on the case (build64). Decision letters skip the notice reader unless they are a Notice to Owner or Keeper (`RS_NOTICE`) |
| Adviser pack and export (release 6) | `packData()`, `packText()`, `packView()`, `packLink()` (build65): summary, dates, what happened in order, what they say, what you say, evidence, your questions (`t.packQs`). Copy, download as a .txt made on the phone, or print (print CSS shows only `.pack-doc`). Works for every case |
| Move a message, hand-offs, your history (build66) | `mvPanel()`, `ev-move`, `ev-move-to`, `ev-move-new`, `intakeQuiet()`; hand-offs `HO_RE`, `hoName()`, `hoRead()`, `hoIn()`, `hoCard()`, `hoLine()`, stored in `t.holder` and quoted by `callDefaults()`; `memWith()`, `memBlock()` from your own cases on the phone only |
| Escalation route (build67) | `XR` table and `XR_CHECKED`: energy, telecoms (6 weeks since Ofcom's change), finance, social housing, letting agents, private landlords, councils, water (CCW only; the next water scheme is in flux), Royal Mail, DWP, HMRC, shops and couriers. `xrFor()` picks the sector, `xrRound()` decides it has gone round, `xrBlock()` shows "If they still don't sort it" folded. Recheck every link and rule before changing `XR_CHECKED` |
| Sorted's assistant (build68) | `aiContext()` (the case, capped at 9,000 characters), `aiRun()` calls the `case-assistant` edge function only when tapped; `aiPanel()` (`aiexplain`, `aiask`), `aiImproveBox()` in the challenge builder, `aiIntro()` the first-time notice. Nothing in the case changes unless the person uses the text. Tests use `functions.invoke` in `tests/mock.js` (`__aiMode` for errors) |
| Company scores (build69) | `SC_PARTIES` (the fixed list from `PARTIES`), `recordOutcome()` on kept and missed (not parking, not examples, not with step records off), `loadScores()`, `scoreBlock()`. Server: `promise_outcomes`, `record_outcome()`, `company_scores()` (5 promises from 3 people minimum) in `07_scores_v69.sql`. Never case text |
| Replies and helper notes (build70) | `loadCaseExtras()` (the case address, unused replies by `task_id`, notes), `cmCard()` (a reply as a proposal: add it, or not about this case), `notesBlock()` (keep or remove), `helperNoteForm()` on the helper page; the mailto adds the case address in Cc; the notes switch is `notes-toggle` in Sharing. Server: `case_mail`, `case_reply_address()`, `case_notes`, `add_share_note()` in `08_replies_notes_v70.sql` |
| Answers from the reminder email (build71) | `?task=…&src=email&ans=yes|no&p=<promise or step id>`; `openPending()` waits for a fresh load, then `ansApply()` presses the case's own button (`kept`, `missed`, `move-done`, or `move-rebook` for Not yet, which records nothing); `ansBanner()` says what was recorded with `ans-undo`, which restores the case from a snapshot and calls `drop_outcome`. Parking promises get no answer links |
| Reply notifications (build72) | `?task=…&src=reply` counts as a return in `openPending()`; the email itself is sent by `inbound-email` `notify()` (no email for an acknowledgement, after opting out, or more than once in 6 hours per case) |
| "Came in" on Home (build73) | `loadFound()` (ids, case, sender's website or helper's name, time; never the words), `foundBlock()` above Needs you, `foundDrop()` when a reply or note is added or removed |
| Playbooks (build74) | `PB` registry, one format per kind of case: `on(t)` recognises it, `stages` (label, `head`, `body`, `acts` that either `go` to a stage or run an existing action, `enter`), `events` for kept and missed. `pbFor()`, `pbEvent()` (called from `kept` and `missed`), `pbCard()`, `pbGo()`, action `pb-go`. State in `t.pb` (`id`, `stage`, `visits`, `noShows`). Parking is registered with `own:true` and keeps its `pk*` cards; repairs (`PB_VISIT`) is written only in the format. `xrRound()` also counts a repair still not fixed after 2 visits. The Citizens Advice link was checked on `PB_CHECKED`. To add a kind of case, add an entry to `PB` and a test |
| Small UI fixes (build78) | `pVisit()` decides if a promise is someone turning up; only then does the due-now card offer "Show this" and "It didn't". `phaseTitle()` says "Due today" for a by-date that isn't a visit. The promise badge, spotlight and row details skip a reference already under the title (`case75HeaderRef`, `case75TitleParts`). Home row columns are set in `main .home44-row` rules |
| Colour meanings (build80) | Violet (`--violet`, links via `--carbon`) is for actions only; Needs you is warm orange (`--warm`, text `--warm-ink`); Waiting is yellow (`--yellow-edge`, text `--wait-ink`); the case Ref uses `--ref-ink`. Each has a dark-mode value. The top bar's full-width band is `.bar:before` (a box-shadow, so nothing scrolls sideways) |
| Case fixes (build83) | The Home spotlight for your own step shows its words and date with a button (`home-move`, which presses the case's `move-done`); `doOfficial()` adds the GOV.UK link to an existing renewal step from `OFFICIAL`; `case75TitleParts()` only reads a reference that contains a digit; `TOPICS` names complaints from "complained" too |
| Guided starts (build91) | `GI` (questions per choice), `giKind()` reads `S.draft.gk`, set when a `[data-cap82]` choice is tapped; `giForm()` replaces the blank box for promise, chase, call and fix; the `gi` submit builds one sentence with `giText()` and resubmits the normal `case` form, so the reader, promise card and playbooks are unchanged. "document" keeps the box with a big photo button. `PKSHORT` and `pkShortBlock()` ask for the notice when someone types only "PCN" or "parking ticket". Actions `gi-back`, `gi-own`, `pk-short-go` |
| First response and two-question starts (build92) | `frCard()` after `+hoLine(t)` on a new case (`t.frNew`, set in `newTask`, cleared by `fr-ok`, by leaving the case in `go()`, or once a promise or step exists): What I understand, What to do next, What Sorted will remember, Better not to. `frParty()` names the council from the text; `frDeadline()` with `PDEMAND` (a demand on you: `readCase` returns no promise for it) offers `fr-remind`; `FR_RENEW` spots a typed renewal without making it a to-do. `GI` asks two questions at most (renew: what and when, then a dated step to confirm); "Something else" is only the box, with `gi-back` (`giStored()`). `namedTitle()` names councils and council tax; a known repair item skips "What is it?" |
| Typed renewals and no-date cases (build93) | `frRenewOnly()` (a typed renewal with no promise or facts): no call form, `doIdleCard()` once the first response is put away, and `fr-renew` proposes "Renew my … before it runs out" by the expiry date via `frRenewWhat()` and `moveDraft()`. `FR_NODATE`: no date yet, so What to do next is "Ask … for a date"; the general `callDefaults()` message now ends with a question (a date for the engineer, what you need to pay for a demand, or what happens next and by when) |
| Only a name (build94) | `psOnly()` (a party from `caseFacts()` plus only filler words in `PS_FILL`, no digits): `psShortBlock()` asks what they sent, with a photo button; pressing Start again with the same words carries on (`d.skipPs`). The case is named after them (`psName()`, plus "letter", "email" from `psNoun()`), the first response says Sorted doesn't know yet what it's about, and `callDefaults()` asks what it's about. `psSay()` keeps "the council" in sentences |
| What else Sorted is for (build95) | `EX` (12 examples: label, the start choice `gk`, and its question `h`, placeholders `ph`, values `val`, a ticked `item`, a sentence ending `add`, a box start `box`, or `go` straight to a block), `EX_ORDER`, `EX_THEMES`; `window.SortedExamples` feeds "Things people use Sorted for" in the chooser script's `panel()`. Chips carry only `data-cap95`; their listener presses the matching `.cap82-card` door with `window.__ex95` set (read by the v91 click listener into `S.draft.ex`, then `giForm()` and the `gi` submit), or, with no door on the page, opens Home with the draft set. `ex95Also()` (Home, 1 to 3 cases), `ex95Explore()` (the Home fold), `ex95Next()` (a finished case, first 3 done). The six doors' `desc` lines list broader examples |
| Discovery, search, case health, endings (build96) | `exKind()` and `EX_ALSO` fit the Home line to the newest case (official, money, repair) with 3 examples, skipping its own (`exAlsoFor()`); `EX_KW` and `exFind()` power the search in the Home fold (`exSearchBox()`, `#ex-search`, `exFoundHtml()`; no match offers `ex-own`, the box with what was typed); `healthLine()` under the case title (missed date, deadline within 7 days, days waiting or open, no reference after 2 days; two at most; not while the first response or a proposal shows); `DONE_KINDS` and `done-kind` fill "How did it end?" in one tap, keeping your own words |
| More examples (build97) | `EX` grows to 32 (boiler, faulty item, leak, broadband, flight, callback, builder, garage, deposit, council tax, benefits, bank, phone, energy bill, job, school place, MOT, licence, car tax, TV licence), each with `EX_KW` search words; `EX_THEMES` has nine parts of life; the strip is two rows (`grid-auto-flow:column`) with "Swipe for more" and, on Home, "See all 32 and search" (`ex-all` opens `#cap95-explore`). `ex95Explore()` shows from the first visit, but not while a start question or block is open |
| Partly, playbooks, endings, life moments (build98) | "Only partly" (`data-p="partly"`, `partlyForm()`, form `partly`): the promise closes as missed with `partly` and `left`, `outcome_missed` carries `partly:true`, no company score, the chase says what is still outstanding, `pbEvent(t,"partly")`. Playbooks `refund` (arrived, part, late after 2 misses), `claim` (decided, declined with the ombudsman route) and `hmrc` (`first:"read"` set in `newTask`: owe, send, wait, unsure); `pbCard()` acts take `p` for a panel. `endCode()` and `DONE_CODES`: `case_closed` sends `end` as a code only (`t.endKind`). `PROLE` lets `readCase()` read "The engineer will…" with no company; `sugCard()` then asks who said it. `shareLooks()` says what a shared item looks like; `fr-pk` (understand, reply, remember) on a parking case once its details are confirmed. `MOMENTS` (moving home, new baby, buying a car, a new job) with their own `EX` entries (`mv_`, `bb_`, `car_`, `job_`), `momentsBlock()` in the fold, `ex-moment` chips under the strip. Each moment starts separate cases: no groups, no checklist |
| Moving home container (build99) | A tasks row with `kind:"moment"` (`type`, `title`, `date`, `ans` tenure/council/car/bb, `items[k]` {st: done, irrelevant, case; `caseId`}, `seen`), kept in `S.moments` by `momSplit()` at load, cached and saved with the cases but never in `S.tasks`. `MV_ITEMS` (own steps with `MV_LINK` official links, checked `MV_CHECKED`; case steps with an `EX` key), shown only if `on(ans)`; `momRows()` groups Needs you, Waiting, Coming up (from `momFrom()`, passive), Done, Not relevant. `viewMoment()`, `viewMomentNew()` (form `mom`), `momHomeBlock()` on Home, `momLine()` on a case. Actions `mom-new`, `mom-edit`, `mom-open`, `mom-done`, `mom-irr`, `mom-undo`, `mom-case` and `mom-other` (set `S.pendingMom`, then `momAttach()` in `newTask` links the new case, 30 minutes), `mom-link`, `mom-unlink`, `mom-del` (keeps cases). Step records `moment_created`, `moment_item`, `moment_opened`, codes only |
| Hardening (build100) | `goHome()` (exposed as `window.SortedHome`, called by the installed app's Home button in the cap87 script): clears the draft, `composeOpen`, `S.pendingMom`, the stored start choice and the cap87/cap90 remembered choices (`window.__cap87reset`, `window.__cap90reset`), then shows Home with one history entry (`replaceState` to `#start`). `momStartEntry()` ("Planning something bigger? Moving home") sits under the chooser from the first visit, only when no move exists; `mom-start` opens the latest move or the questions. `momPendingBoot()` carries a life moment chosen on the landing page through sign-in (`sorted.moment`). `momDetach()` keeps a case in one move only; `momRows()` trusts `c.momentId`; the same move date opens the existing move. `tests/mock.js` `__failWrites` makes case saves fail for tests |
| The thing named, and carried choices (build101) | `thingOf()` (`THING_RE`, `THING_NOT`) keeps the thing in "The screen is broken" as `t.fix.item` when `ITEMS` doesn't know it, so the first response says "Your screen isn't working" (`itemSay()`) and "What is it?" is filled in; rooms, people and orders are never things. `giRestore()` at load opens a start choice made on the landing page before sign-in (`sorted.carry82`, set by the v91 click listener when there is no user); any other reload clears a leftover choice, so a refresh restores saved work only; `giForget()` in `newTask` clears it and the cap87/cap90 remembered choices once a case starts. `tests/make_reader.js` also exposes `thingOf` |
| Semantic memory (build102) | `TYPOS` and `typoFix()` (whole-word fixes for common misspellings and shorthand) run first in `caseFacts()`, `readCase()`, `psOnly()` and `thingOf()`; `notMention()` drops "it's not the X" before items are matched; `THING_MORE` and `THING_FILL` catch more ways of naming a thing ("Screen cracked", "cracked my screen", "problem with my printer", "X no longer works"); `DANGER_NO` strips negated danger words and `DANGER_HOT` adds a hot plug or socket in `looksUnsafe()`; `PMISS` reads "but they didn't"; the repair step asks "What's happening with the …?" when the thing is known, and "You mentioned a screen. Which one?" with chips for a screen; `frCard()` says a promise was missed when there is no date. Rule: clarification is fine, repetition is not |
| Saving (one save at a time) | `save()` with `_saving` and `_again` (build37) |
