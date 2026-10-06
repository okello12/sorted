# Sorted: the plan from v114

Revision 3, 4 October 2026. The same plan is in the shared document
https://claude.ai/code/artifact/99787703-32e4-4bcc-81c6-d4904b03d8be; this file is the versioned copy. When they
differ, this file wins and the document is updated to match.

The standard for every case: after entering a problem, can someone see that Sorted understood it, knows what is still
uncertain, and has helped them move forward?

Every claim about Sorted's behaviour below names its evidence (a test, a function, a database job or configuration).
A claim marked **Unverified** is not published until it has evidence.

## How to start (for the next builder)

Implement this plan, starting with Phase 0. First confirm this file and its evidence references match the repository.
Fix the sign-out data loss (Phase 0.3) before any broader feature work. For every release: complete the local checks,
get passing CI on a pull request before merging, then verify the live version. After each phase, report what was
completed and what findings remain unresolved.

## Delivery order

1. Phase 0: release discipline, faster tests, and the sign-out data loss.
2. Phase 1: verify the technical claims; correct the public wording that is wrong today. No new marketing copy.
3. Phase 2: the shared case structure and five core journeys.
4. Phase 3: account, reminder, draft and sync controls (alongside Phase 2 where they don't touch the same code).
5. Phase 4: the fuller onboarding, FAQs and worked examples, describing only what Phases 2 and 3 made true.
6. Phase 5: real-use evidence, then a separate decision on platforms.

## Phase 0: release discipline, faster tests, sign-out

**0.1 The release gate.** A release is finished only when, in this order:

1. Built, with `EXPECT` pinned.
2. The full local suite is green.
3. Pushed to a branch, a pull request opened, and GitHub's required checks green (regression, WebKit, Firefox,
   staging). Today CI runs after the push to `main`, so a red check means production already has the change.
4. Merged to `main` and deployed by Vercel.
5. The live page checked: `SORTED_V` on sorted-pilot.vercel.app matches the release, and a short walk (start a case,
   confirm a promise, reload) works there.

**0.2 Faster tests, safely.** Parallel only after proving the files share nothing. Each file starts its own browser
context and localStorage (`tests/mock.js` keeps the mock database there), so they are expected to be independent. To
confirm: write each file's output to its own file, run every file twice in random order across six workers, compare
with a serial run. Anything shared (`tests/out/`, `tests/node_modules`, a fixed port, a temporary file) is fixed first.

**0.3 Sign-out never loses work.** Found while checking: signing out clears the local copy at once (`case "signout"` in
the page), so a change that hasn't reached the server (offline, or mid-save) is lost without a word. Fix:

- If changes are pending, sign-out stops and offers **Wait for saving**, **Stay signed in**, or an explicit
  **Discard changes** (which names how many).
- "Saved to your account" is shown only after the server confirms the save (the existing `save()` success path, after
  the conditional update returns the row). Otherwise "Saving" or "Saved on this phone, not yet sent".
- Tests: sign-out with a pending change (each of the three choices), sign-out while offline, sign-out mid-save.

## Phase 1: verify, and correct what is wrong today

| Claim | Evidence | Status |
| --- | --- | --- |
| Cases are stored in London | Supabase project `boxrwcuhxmimayaxzywu`, region eu-west-2 (checked through the API, 4 Oct 2026) | Configuration |
| A guest has a server account; only the browser that made it holds the key | Supabase anonymous sign-in, `anon-start`; tests 47, 61 | Tested |
| A guest's cases carry across when they add an email | `stash_carry()`, `claim_carry()`; test 61 | Tested |
| A guest account is deleted after 30 days without use | Job `sorted-anon-cleanup` (daily 03:37, live and staging since migration 15): deletes an anonymous user with no sign-in, no visit (`user_seen`, written by `touch_seen()` on each load), no case updated and no live promise in 30 days; cases go with it | Configuration (checked 4 Oct 2026 in `cron.job`); the rule checked on staging with `tests/live/guest_rule.sql` (daily opener kept, live promise kept, recent save kept, 31 days away deleted); the page's call tested (test 72); explained in the app (test 72) |
| Idle cases are deleted after 90 days | Job `sorted-retention-90d` (daily 03:17): not updated for 90 days, unless a promise is live | Configuration (checked 4 Oct 2026). The old "30 without an email" wording is gone (test 72) |
| Reminder emails are scheduled every 10 minutes | Job `sorted-send-reminders` `*/10 * * * *` (checked 4 Oct 2026); edge function `send-reminders` v10 | Scheduling verified. Arrival: recorded per reminder since v116 (below); **still unmeasured until Resend's delivery webhook is connected** |
| Reminder emails contain no case details | `send-reminders` source; test 72 checks the body is built from fixed copy, links and ids only | Tested |
| Photos and PDFs are read on the phone, never uploaded | `readPicture()`, `pdfToText()`; tests 10, 18, 22; CSP (test 13) | Tested |
| Changes made offline are saved later | Test 56 (failed save kept, saved once online); test 66 (two devices merged; deleted elsewhere); test 72 (an offline edit does not bring back a case deleted elsewhere); test 71 (sign-out with pending changes) | Tested for these cases |
| Helper links: anyone with the link, read-only, until switched off or 30 days without a change; deleted after 90 | `get_share()`; job `shares-retention`; tests 60, 61; staging suite | Tested |
| Usage records hold no case content | `pilot_events`: step name, case and promise ids, small props; tests 31, 51, 60 | Tested. Not anonymous (account id and case id): the notice now says so (test 72) |

**Reminder delivery evidence (built in v116).** Migration 15 adds `submitted_at`, `delivered_at`, `bounced_at`,
`delivery_status` and `delivery_detail` to `reminders`; `send-reminders` v10 writes `submitted_at` before the Resend
call and `sent_at` with `provider_id` on acceptance; the new edge function `resend-events` takes Resend's delivery,
bounce, failure, delay and complaint webhooks (Svix-signed with the Vault secret `resend_events_secret`) and writes
them against the reminder by `provider_id`, keeping only the bounce classification, never an address;
`pilot_health().delivery` reports due, handed over, accepted, delivered, bounced, delayed, unknown after an hour, the
median lateness and arrival, and whether any webhook has ever arrived; the numbers page shows it. **Still to do, by
Baldwin:** in Resend, add a webhook endpoint for `https://boxrwcuhxmimayaxzywu.supabase.co/functions/v1/resend-events`
with the events delivered, bounced, failed, delivery_delayed and complained, and put its signing secret in Vault as
`resend_events_secret`. Until then the Delivery row says arrival is unmeasured.

**Reminder delivery evidence (the rule).** Accepting an email measures sending, not arrival. Record per reminder: the scheduled
time, the time it was submitted to Resend, Resend's acceptance (`provider_id`), and delivery, bounce or failure events
from Resend's webhooks where available. Until that data supports a timing claim, the wording stays: "Sorted sends an
email at the time it shows. When it arrives depends on email, and it can be late or not arrive."

**Guest deletion: a rule to define, not just reword (done in v116; the evidence is in the table above).** Someone who opens Sorted regularly would expect their cases to
stay. Before this rule is described or relied on:

1. Define activity: opening Sorted while signed in as the guest (the page refreshes the session, which updates
   `last_sign_in_at` only on a new sign-in, not on a return visit, so this needs a lightweight "seen" timestamp written
   on load), saving a case, or a live promise.
2. Change `sorted-anon-cleanup` to use that definition.
3. Test the exceptions on staging with a real guest account: opened daily with no edits; a live promise; no visit for 31
   days.
4. Explain it in the app before it applies: "Without an email, your cases are deleted after 30 days in which you don't
   open Sorted."

**Wording to correct now (done in v116, pinned by test 72):**

- "Sorted keeps nothing you delete" (terms): untrue, usage records remain. Use the deletion answer below.
- "Nobody running it reads your cases" (About): use the privacy notice's wording everywhere (technical access as any
  operator has; not used to read cases).
- "The official page is always right and Sorted is not": "Check the relevant authority's current guidance before
  acting. Links and guidance can change."
- Guest copy is about access, not loss: "Your cases are saved on Sorted's servers, but without an email only this
  browser can open them."
- "Step records" become "usage records without case content", never "anonymous".

**Deletion, answered coherently (the terms, Help and the Undo banner say this since v116).**

*Deleting one case.* It is removed from the database straight away, with its helper link (which stops working) and its
unsent reminders (`case-del`; test 12). For two minutes Home offers Undo. During that time the only copy is in the open
page on this phone: **closing or refreshing the page, or tapping anything else, ends recovery**, and the app says so
next to Undo. Undo saves it back as a new copy without the helper link (test 69). Usage records mentioning the case id
(no content) remain up to 12 months (`pilot-events-retention`). Emails already sent stay in your inbox.
Proven in test 72: another device that was offline with an edit does not bring the deleted case back when it reconnects
(`saveConflict()` removes it locally when the row is gone).

*Deleting your account.* Everything goes straight away: cases, helper links, reminders, replies, notes, company-outcome
contributions and usage records (`delete_my_account()`; cascades). No Undo. Emails already sent stay in your inbox.

*Backups.* Supabase free plan, no restorable backups (`docs/RECOVERY.md`). **Unverified:** Supabase's internal retention
on the free plan and Resend's log retention; quote both providers' published terms.

## Phase 2: every case understands, asks and moves forward

One structure, collected a little at a time:

1. The matter.
2. **The outcome wanted**: a purpose, not an action ("Find out whether the credit check is complete", not "Contact the
   dealer"). Proposed from the first sentence, confirmed or changed. Questions, messages and next steps aim at it.
3. Who is involved, each with their own references.
4. What has happened.
5. Whose turn it is: yours, theirs, or both as separate actions.
6. A confirmed deadline, kept apart from a follow-up date you chose.
7. The next action.

At the top of every case, "What Sorted understood": short, editable, uncertain things shown as questions.

The Ford journey, and every journey like it:

1. Ask what decides whose turn it is: "Are you waiting for the credit check result, or have they asked you for
   something?"
2. Turn the answer into a next step towards the outcome: a message to the dealer, recording what they asked for, or a
   follow-up.
3. Carry what's known forward: the dealer's name fills "Who are you contacting?", correctable.
4. A real title, "Ford dealer: credit check", editable, the person's words kept.
5. Buttons say what happens: "Save follow-up reminder"; "Choose a date" beside 3 days, a week, 2 weeks.
6. "What were you planning to do next?" becomes optional, or "What would you like help with?" used at once.
7. A case that is clearly the person's own task becomes their own step, not "get the call ready".

Five complete journeys with end-to-end tests: repair (begun in v113), refund, parking notice (type established first),
renewal, dealer and finance. Then the other categories. An unrecognised situation gets the general organiser.

## Phase 3: account, reminders, drafts and sync

- Sync state on every case and on Home (builds on 0.3); tests for an interrupted save, two devices, deletion while
  another device is offline, reload with pending changes.
- Account, Settings and Help as three separate views with a selected tab.
- An email reminders switch in Settings with destination and state (`set_email_optout(on)` for the signed-in person;
  `email_optouts` exists and `send-reminders` honours it). Per-case controls stay.
- The reminder's send time shown where it is set, with the time zone, and the cautious delivery wording above.
- "Usage records" with an on/off control showing its state and what is recorded.
- Export: "Download my cases", "Copy to clipboard", contents and format explained.
- A restrained red "Delete my account" with a confirmation built from the account deletion answer.
- Email and case count in ordinary text; "Pilot numbers" (admin-only already) in an Owner section.
- Drafts kept until Start ("Continue draft"); correct the kind of case, whose turn it is or Sorted's reading without
  starting again; several people and several open actions per case; generic actions at any stage; extracted text
  reviewed before it drives a date, reminder or message.

## Phase 4: onboarding, FAQs and examples

Only now, each statement checked against Phases 1 to 3 and pinned by a test:

- One description everywhere: "Life admin has a habit of piling up. Sorted helps you keep it moving." with the
  examples, and "Keep the details, messages, references, deadlines and next steps together." Examples only for
  journeys that work end to end.
- "How it works" in three steps and one worked example labelled Example.
- The full FAQ with the evidenced answers from Phase 1 (reminders: Home, email and calendar separately; photos and PDFs:
  keep your original, check what was read; helper links: anyone with the link, forwardable, read-only, how long, how to
  stop; guests: access depends on the original browser, and the activity rule once defined).
- About: the short version; no employer names, phone or personal email.
- Separate pages with stable addresses and version dates: About, Help & FAQs, Privacy notice, Terms of use, Contact
  support.

## Phase 5: real use, then platforms

Elapsed time alone triggers nothing. The signals, read over at least four weeks with targets set before inviting people:

- People complete cases (finished with an outcome, not abandoned).
- They return to follow up when a promise falls due (Due Return Rate, `pilot_metrics()`).
- They understand reminders (no support questions about where reminders went; reminder links used).
- They manage without explanation (the newcomer questions in `docs/PHONE_CHECK.md`, and no hand-holding in support).
- They come back for a second matter.

Platforms are a separate technical assessment after those signals: whether a store app adds anything over the
installed web app; Apple's minimum-functionality review; Google's target API level, web route for account deletion and
closed testing; privacy declarations matching the processors exactly; screenshots, age rating, support contact, review
account. A native wrapper is one possible route, not readiness.

## Decisions only Baldwin can make

- A domain and a support address.
- Whether to keep "reply within 10 working days" and "30 days' notice before closing".
- Supabase Pro for backups.
- A lawyer's read of the terms and privacy notice.
- Targets for the usage signals.
- Whether and when to pay for app-store developer accounts.

## Progress

**Phase 0 (v114 and v115, 4 October 2026).**

- 0.1 The gate is in place and has been used: v114 and the two live-check fixes each went through a pull request
  (#19, #20, #21) whose checks were green before the merge; v115 likewise. The `staging` job now runs on pull requests
  too, and is **skipped** (shown as skipped, with a warning) until the staging secrets exist, never passed without
  running. The CI job `live` (`tests/live/verify_live.py`) runs after each push to `main`: it waits until the live page
  is byte for byte that commit's build, then walks it as a throwaway guest.
  **Live result for v114:** green on the third attempt, 8 checks, 12:29 UTC: the live page was the v114 build; a guest
  started a case, confirmed a promise, saw "Saved to your account", reloaded and found it; the account deleted itself.
  The first two attempts failed on the check itself (it read `SORTED_V` and `sb` as globals; the page keeps them in a
  closure), and their clean-up silently did nothing, leaving two guest accounts behind.
  **Clean-up outcome:** with Baldwin's approval, the two accounts from those runs (`ea3116de…`, created 11:46:02
  UTC, and `d9883f0c…`, 12:11:55 UTC; both anonymous, no email, one case each created inside the run's window, three
  usage records each, no shares or reminders) were deleted on 4 October with their cases and usage records; a check
  afterwards found no user, case, usage record or orphaned reminder for either id. A third guest account created at
  12:05 UTC did not come from a check run and was left untouched.
  **Hardened since (v115):** the walk requires "Saved to your account", reads the case from the server with the guest's
  own session, clears the local copy before the reload, deletes through Account and proves the account and case are
  gone from the server; a cut-short run's guest is deleted by a step that always runs; the `live` job is never cancelled
  by a later push.
  **Still to do, by Baldwin (the repository API refuses these from here):** GitHub branch protection on `main`
  requiring `regression`, `engines (webkit)` and `engines (firefox)` (Settings > Branches, or Rules); the two staging
  secrets. Until then the gate is followed by hand.
- 0.2 Isolation proven on v113: every file's output kept separately (`tests/runner.py`), one serial run and two runs
  six at a time in different random orders (seeds 11 and 29). All 72 files green in all three; the only differences
  were random case ids in two messages and one timing (60-case Home 1.14s serial, 1.85s parallel, inside its
  budget). Nothing was shared: generated images and PDFs have names unique to their file, `tests/out/index.html` and
  `reader.html` are only read, there are no ports. Serial 22 minutes, six at a time about 6. CI runs four at a time
  (7 minutes on GitHub).
- 0.3 Sign-out keeps unsaved work (build114, test 71). Live since 12:00 UTC on 4 October.
- Also in v115: the two moderate axe findings (no h1 on a guided start; h3 straight after h1 on the promise card) are
  fixed in both themes and test 65 now fails if they return.
- Staging (from Phase 1's evidence table, brought forward): `shares_drop_helper` with its trigger, `remove_helper`
  and `drop_outcome` were applied on 4 October; Supabase's tooling refused the remaining functions and the jobs without
  a person's confirmation. The rest of `01_run_by_hand.sql` and anonymous sign-in are Baldwin's (docs/STAGING.md).

**Outstanding findings after Phase 0:** branch protection and staging secrets (above); the staging suite has never run
(no secrets); reminder arrival still unmeasured (Phase 1); usage records linkable (Phase 1); guest deletion rule
(Phase 1).

**Phase 1 (v116, 4 October 2026).**

- The evidence table above is checked against the live project (region, every `cron.job`, the function versions) and
  each row says what was verified and how.
- Reminder delivery is now recorded end to end (migration 15, `send-reminders` v10, `resend-events` v1, the Delivery
  row on the numbers page). Arrival stays unmeasured until Baldwin connects Resend's webhook (above).
- The guest activity rule is defined (sign-in, a visit, a case saved, a live promise), applied on live and staging,
  checked on staging with `tests/live/guest_rule.sql` (rolled back, nothing left), and explained in the app.
- Every wrong sentence is replaced and pinned (test 72): deletion as it works, technical access rather than "nobody",
  guidance can change, guest copy about access, "usage records" (not anonymous) instead of "step records", reminders
  sent on time but arrival not promised. The Undo banner says a refresh ends the chance. Email footers no longer say
  "research pilot" (`send-reminders` v10, `inbound-email` v6).
- Still open from Phase 1: Supabase's and Resend's retention terms on their free plans (quote both before a backups
  claim is published); the staging suite has still never run (no secrets).

**Phase 2 (v117, 4 October 2026).**

- The shared structure is on every case as "What Sorted understood" (`uCard`): the matter, the outcome wanted, who is
  involved with their references, whose move it is, their date kept apart from a follow-up you chose, the next
  action. Uncertain things are questions (whose move; what you'd like to come out of this); nothing changes until
  confirmed; both can be changed later.
- The Ford journey works as the plan asked (test 73): the dealer's name is kept and carried into the call form; the
  case is "Dealer ford: credit check"; "Whose move is it?" with three answers; "Save a follow-up reminder" with
  "Choose a date", a follow-up that is your own step and never their promise; "They’ve asked me for something" keeps
  your step rather than a call script; the planning question can be skipped. The outcome wanted is proposed only
  where Sorted can say it honestly (a notice, a repair, money, a benefit, a promise, a no-date call) and otherwise
  asked.
- Five journeys walked end to end in test 73: repair, refund, parking, renewal, dealer and finance; plus an
  unrecognised sentence through the general organiser. The older journey tests (22, 23, 36, 47, 51, 63) still pass.
- Migration 16 adds the step names `turn_recorded` and `goal_recorded` (codes only).
- Not done in Phase 2, carried to Phase 3: several people with their own references inside one case (today a second
  party is a second case, linked by name), several open actions at once, and editing the matter in place (rename
  covers the title).

**Phase 3, part 1 (v118, 4 October 2026).** Account, Settings and Help & About are three views with a selected tab.
Settings has the email reminders switch for every case (state, destination, UK time, arrival not promised; migration
17 `set_email_optout`), appearance, usage records with their state, and an Owner section for the admin. The case
lists the dates and times its emails go. Export is "Download my cases" and "Copy to clipboard" with the contents
explained; "Delete my account" is restrained until tapped and confirms with the deletion answer. Home shows the sync
state while something is pending or the phone is offline (test 74; the staging suite checks the switch's permissions).

**Phase 3, part 2 (v119, 4 October 2026).** Drafts are kept on this phone until Start: a reload refills the box, a
tap on Home keeps the open form, and a closed Home offers "Continue draft" or "Discard it"; nothing reaches the server
until Start. The kind of case can be corrected in place (someone else owes the next move, something needs fixing, your
own task) without starting again, keeping the words, messages and history (test 75). Extracted text from a photo or
PDF was already placed in the box for review before "Read it" or "Start" (`ocrDone`; tests 10, 18, 22), so no date,
reminder or message is driven by it until the person has seen it and the proposal card is confirmed.
Carried forward (not built): several people with their own references in one case, and several open actions at once.
Today a second party is a second case, and one promise or step is open at a time; the plan's Phase 2 structure holds
the rest. These are the first items for a Phase 3 follow-up once real use shows they are needed.

**Phase 4 (v120, 4 October 2026).** One description everywhere (the landing page, a newcomer's Home, Help). "How it
works" in three steps and one worked example labelled Example, on the public site and in the app. The full FAQ (29
questions), each answer written from what Sorted does and the ones that matter pinned by test 76; the bracketed
questions in the draft copy are answered with verified facts (photos and PDFs read on the phone and reviewed first;
cases on Supabase in London with a copy on the phone; a guest's key in the browser; offline changes kept and sent
later; who can access what; free; a reply within 10 working days). Separate pages with stable addresses and a date:
`#about`, `#how`, `#help`, `#privacy`, `#terms`, `#contact`, all in the footer. The hero and footer no longer say
"nobody reads" or "30 without an email". Not done: a real domain for those addresses (Baldwin's decision) and a
lawyer's read of the terms and notice.

**Phase 5 (prepared, 4 October 2026).** Nothing to build until real use. The five signals are already measured, so the
only missing inputs are the targets and the invitations:

| Signal | Where it is measured | Target (Baldwin) |
| --- | --- | --- |
| People complete cases (finished with an outcome, not abandoned) | `pilot_metrics().endings` (`case_closed` codes) against cases started | |
| They return when a promise falls due | Due Return Rate in `pilot_metrics()` (`promise_due_return`) | |
| They understand reminders | `pilot_health().delivery` once the Resend webhook is connected; `promise_due_return` with `src=email`; no support questions about where reminders went | |
| They manage without explanation | the three newcomer questions in `docs/PHONE_CHECK.md`; "Report a problem" and support emails | |
| They come back for a second matter | `second_case_started` in `pilot_metrics()` | |

Before inviting people: branch protection on `main`; the staging secrets and the rest of `01_run_by_hand.sql`;
Resend's delivery webhook; a domain and support address (the pages at `#about`, `#how`, `#help`, `#privacy`, `#terms`
and `#contact` take the domain as it is); the lawyer's read of the terms and privacy notice; the targets above; then
the phone check in `docs/PHONE_CHECK.md` on a real iPhone and Android phone. Four weeks of use against the targets,
then the separate platform assessment the plan describes.

## Remediation (the hardening report of 4 October 2026)

The report's findings are taken in its order: the Phase A stop-ship items first, the PCN failure first of all; then
Phase B (the fact ledger and obligations), Phase C (first-use checks with real people, Baldwin's) and Phase D (the
hostile journey tests). Each item is listed here with its evidence once done.

**A1. Photo and document intake (v121, done).** A read is evidence, never a fact: Tesseract's text goes through
`docAssess()` (quality, notice terms, usable fields) and then a review, "Check the notice", with every field editable;
nothing becomes a case fact until "These are right, continue". A bad read says "We couldn’t read this photo clearly.
Your case hasn’t been changed." with Retake photo, Choose another file and Enter the details manually, and no
Continue; retail text in the notice flow is "not a notice" and never a refund case; partial reads show what was found
and leave the rest blank. The "8 characters is a read" rule is gone. Status is its own live region on the screen.
Copy: "Sorted tries to read the notice. Check the details before continuing." Usage records: the six `document_*`
steps (migration 18, live and staging), codes and counts only. Evidence: test 77, test 22 step 5, test 18.

**A2. One local clean-up (v122, done).** `clearLocalUserData()` is the one place that removes what Sorted keeps on this
phone for a person (the copy of cases and moves, drafts, carried copies, a shared-in text, the step queue, start choices,
per-case notes, anything read from a photo). Called at sign-out, account deletion, the move from a guest to an email
account, draft expiry (the draft is removed, not ignored), a failed photo read, and from Settings ("Remove the copy from
this phone"). Evidence: test 78.

**A3. Kind changes keep knowledge (v122, done).** The old kind's answers go dormant on the case (`t.kept`) and return if
the person comes back to that kind; promises, references, facts, counts, goal, whose move and history are never touched.
Evidence: test 79.

**A7. No jurisdiction before it is known (v122, done).** Moving home asks "Where is your new home?" first; until it is
answered, the GP, licence, voting and council steps show no link and say to say where. Evidence: test 64.

**A8. Ordinary navigation (v122, done).** Account, Settings and Help & About are a plain `nav` with `aria-current`; no
ARIA tabs. Evidence: tests 74 and 65.

**A9. Trust wording (v122, done).** "Sorted doesn’t turn an uncertain suggestion into a confirmed fact until you confirm
it." replaces "nothing on a case changes without your tap"; "hold them to it" and "holds them to" are gone. Evidence: test 72.

**A4. Whose move is it now? (v123, done).** Mine, Theirs or Both, asked again at any time from What Sorted understood;
an answer that conflicts with an open step of yours is never applied silently: Sorted asks whether to keep the step as
well or mark it no longer needed; their promise is never touched by the answer. Evidence: test 80, test 73.

**A6. The landing hierarchy (v123, done).** "They said Tuesday. Sorted remembers Tuesday.", then "Keep the details,
promises, deadlines and next steps of life’s unfinished business in one place. Sorted shows what needs you, what you’re
waiting for and when to follow up.", the kinds of matter, one primary button above the fold. Evidence: test 80, test 44.

**A5 / Phase B. The fact ledger (v124, done).** Every detail has a row with where it came from, when, its status and
what it replaced. Nothing silently disappears; a reading or suggestion is never confirmed without the person; a thing
ruled out is recorded as ruled out. Older cases gain a ledger on opening without anything else changing. Shown on the
case page and in the adviser pack. Evidence: test 81.

**Phase D. Hostile journeys (v124, done).** Parking (bad photo → manual → challenge → rejection), repair (safety stop →
missed appointment → new date → kind changed and back), two moves in two nations. Refund cycle: test 47; two devices:
test 66. Evidence: test 82.

**Phase C (first-use checks with real people) is Baldwin's**, with `docs/PHONE_CHECK.md`.

**A10. Staging as a real gate.** Last, because a missing staging environment then makes every release red until the
staging secrets exist.

## The remaining-pages review (4 October 2026, evening)

**v125 (signed in).** Unfinished work is kept: a next-step or other case form keeps its words when you leave it, the
case or reload, and offers them back. Moving home keeps answers after a missing date. Case pickers (a shared-in
message, a forwarded email) list every open case with a search. Deletion says what Undo does. A new parking case no
longer opens call preparation. A case leads with its status and one next step; the first response and What Sorted
understood follow the action. The document door says "Start with your document", keeps the choice and shows the
first-page limit for scanned PDFs; a failed read shows one set of choices; manual PCN entry is a form. A previous error
no longer blocks a second submit of the notice form. Evidence: tests 83, 77, 82.

**v126 (public pages).** The landing page leads with "Keep everyday admin moving." and the everyday problems, one
main action ("Start with your problem", carried through sign-in to the box for your own words), "See an example", three
common problems, one labelled worked example, and the full catalogue (six ways in, 32 examples, life moments) behind
"Browse more". No more "Tue 14:00–16:00" sample. Help: questions first, in four groups. How it works: shorter, example
kept. About: why Sorted exists first. Contact: a copyable address and what to do if no email app opens. Privacy points
at Account and Settings. Terms describe all of Sorted. Evidence: tests 84, 44, 76.

**v127 (Baldwin's iPhone, 21:45).** Taking a photo of a PCN did nothing: the camera hides the page, and on return
Sorted redrew (to keep dates current), replacing the file box before the photo arrived. Now nothing redraws while a
picker is open, the box carries its own handler, big camera photos are scaled before reading, a start choice survives
the email sign-in link, the box heading no longer shows a leftover "What did they promise?", and the parking screen has
one photo button. Evidence: test 85, which fails on v126.

**v128 (files in and out).** Saving the adviser pack, all cases or a calendar reminder used to drop the file link
after one second (before an iPhone's "Download?" answer), said "Downloaded" before anything was, and often did nothing
from the Home Screen app. Now a phone uses its share sheet ("Save to Files", or the calendar), a computer downloads
with the link kept for a minute, and the message is honest. A photo from Files or Google Drive with no type is read by
its name, and an iPhone HEIC photo is converted on the phone where Safari can open it. Evidence: test 86.

**v129 (the navigation note).** One app shell: Home · + New · Cases · More at the bottom of every signed-in screen,
the place marked; the top bar the logo plus Back on deeper screens; Cases with search and counts; More holding Account,
Settings, Help and the public pages; a refresh keeps the case, Cases or More; "<Who> said they would Nothing" never
shown; the guest note one compact card. Evidence: test 87 and the twelve journeys in it.

**v130 (the quick actions note).** Updating reality should be easier than ignoring the app. Home leads with "N things
need a quick answer" and each one is answered where it is: the obvious answer in one tap (then "Is this case finished
now?", or the playbook's own question such as "Has all of it arrived?"); "Not yet" records the miss and opens the chase
with the reference already in it; "New date" asks only for the date (the old promise is replaced and kept in the
history, the case waits again); "Later" (Tonight, Tomorrow morning, This weekend, or a day) is an attention promise:
the case leaves the top of Home for a Later section until then, the real deadline is shown and never moved, an option
after the deadline says so, and any real update ends it. "Something changed" and "Can’t do this now" sit on every open
case, with choices that fit a refund, a parking notice, a repair or anything else. A parking notice due within a week
offers Pay (the hand-checked official page), Review options and Later; back from paying Sorted asks "Did you finish
paying…?"; Yes records the payment with an optional confirmation number, and a card number is refused. Evidence: test
88. Not yet: answers inside the reminder emails themselves stay Yes and No (build71), and "Later" is not yet read by
`send-reminders`; it creates no extra emails, but a reminder already set for a deadline still comes, and the sheet says so.

**v131 (Baldwin's iPhone after v130).** Safari's back arrow was greyed out inside Sorted: v129 wrote each place
(`#case-<id>`, `#cases`, `#more`, `#move-<id>`) with `replaceState`, so moving between places made no history and the
phone's Back and swipe did nothing ("I can't move away from this site"). Now `navHash()` pushes each place and a
`popstate` listener opens it again, so Back goes case → Home and Cases → the case, and Forward works. "+ New" writes
its place too. An older title "<Who> said they would nothing" reads "Waiting for <Who>" wherever the title shows
(`case75TitleParts()`; v129 had only fixed `home54Title()`). Evidence: `tests/engine_nav.py`, a touch-phone tap walk
(iPhone 13 in WebKit, Firefox and Chromium on GitHub) through Open this case, the bar's Home, the top Home, Cases,
More, New, Back and Forward, and test 87. A returning Home with the ways in folded ended in a blank gap under the
one case, so it felt like the only place to go: it now shows "+ Start something new" and "See all my cases" there. In the bar, New was a filled violet tile and so looked like the
selected place while Home's mark was faint: the current place is now the only filled item, violet with a line above
it, and New is a round + with a plain label. A finished case now leads with "Done, back to Home" and "+ Start something new"
above the recap, and an older title "<Who> said they would <Typed words>" reads "<Who>: <Typed words>" (`title131()`).

**v132 (reopening a finished case).** Reopen was hidden under Tools for this case. The finished card now asks "Need
it again?" with Reopen this case (everything kept: history, messages, references, dates; the history notes how it had
ended) and Save the full record (the adviser pack, to copy, download or print for evidence), and says finished cases
stay under Done in Cases for 90 days after the last change, or 30 without an email. Evidence: test 87.

**v133 (reminders that reach people).** Reminders were email only, and a guest had none at all. Now a phone can say yes
once ("Get reminders on this phone", in Settings and offered once a case has a date): the page registers
`public/sw.js` (shows a notification, opens the case, caches nothing), subscribes with Sorted's public VAPID key and
saves the push address with `push_save()` (migration 19: `push_subs`, private, only the big browser push services;
`push_state()`, `push_drop()`). `send-reminders` v11 sends each due reminder to those phones as well as by email, so a
guest gets reminders too; the message is fixed words, the case link and, after the time, Yes and Not yet buttons, never
what the case is; a phone the push service has forgotten is removed. The after email also offers "Choose when Sorted
reminds you" (Later) and "They gave a new date? Add it". On an iPhone this needs Sorted on the Home Screen (iOS 16.4
and later), and the page says how. A guest is asked once for an email when a case first has a date. Evidence: test 89,
`tests/webpush_check.mjs` (RFC 8291's example) and `tests/fn/send_reminders_check.mjs` (the function run in Node,
decrypting the push it sends). The private key is `vapid_private_jwk` in Vault; the public key is `VAPID_PUB` in the page.

**v134 (getting things in).** Forwarding comes back, as `docs/LATER.md` item 2 asked, without trusting the sender: each
person has a secret address (`my_inbound_address()`, `log-<16 hex>@<inbound domain>`, already in the database), shown
in Settings with Copy and "Get a new address" (`inbound_address_new()`, migration 20: the old address stops at once).
`inbound-email` v7 stores what arrives there for that person, unassigned, at most 30 a day; Home shows it as "An email
came to your Sorted address from <website>" with the existing case picker. Android: the manifest gains icons and a
`share_target` (`/?st=&sx=&su=`), which `grabShared()` reads like the iPhone Shortcut's `#new=`. An iPhone Home Screen
icon (`/icon-180.png`). The privacy notice describes forwarding and lock-screen reminders. Evidence: test 90 and
`tests/fn/inbound_check.mjs` (inbound-email run in Node).

**v135 (keeping the original documents).** For evidence, the record of what was said isn't enough. A case's "What's
happened" now has "Documents kept with this case" with "Keep a document with this case": the file goes unchanged to
the private storage bucket `originals` under `<user>/<case>/` (migration 21: private, 10 MB, images and PDFs, 200 a
person, each person only in their own folder, no updates), listed with date and size, opened through a 5-minute signed
link, removed after a second tap, with a history line each way. A daily job (`sorted-originals-cleanup` →
`originals-cleanup`) removes files whose case has gone. The privacy notice says so. Free plan storage is 1 GB in all.
Evidence: test 91 and `tests/fn/originals_check.mjs`.

**v136 (a simpler first visit, and what only Baldwin can do).** A newcomer's Home now leads only with the ways in and
the box: "Planning something bigger? Moving home" moves below the ideas fold, and the guest note waits until there is a
case to keep. `docs/OWNER_CHECKLIST.md` lists, in order: approving the Supabase changes for v133 to v135, Supabase Pro
for backups, a name search and domain, a lawyer's read, the real-phone check, and what was already open. Evidence:
test 92.

**v137 (the review of 5 October 2026).** Six points from Baldwin's review. (1) An open case leads with one "Now" card:
what happened ("Currys promised it by Friday 9 October. That time has passed."), who acts next ("Next: tell Sorted
whether Currys did it", or "Waiting for Currys: nothing for you to do until …"), and "Add what they just said",
"Something changed" and "Can’t do this now"; the promise or step card with the one main button follows, then Sorted's
reading, the history, the ledger and documents. (2) An old reminder or notification (Yes, No, Later or New date) for a
promise or step that has since moved on changes nothing, says what happened since ("you recorded that Currys did it",
"the date changed: Amazon now say …") and shows the case as it is. (3) The public page's "Try an example": four steps
of a refund that hasn't arrived (what you type, Friday passes, "Not yet" in the history, the follow-up quoting the
order number), with "It arrived" as the other ending; nothing saved, no sign-in. (4) "Add what they just said" on
every open case (the existing paste box: a message, a screenshot or a PDF, read and proposed, confirmed by a tap); the
guest note says "Keep your cases if you lose this phone." (5) "Send this summary" under Tools: the issue, what was
promised, what happened, the reference and "What I’m asking for now" (prefilled, theirs to change), previewed, then
Copy or Share; Sorted sends nothing. (6) A helper link can carry "What I’m asking them to do" (`t.helpAsk`, in the
card as `q`); the helper sees it first and replies with their name; the reply comes back under "You asked: …" to keep
or remove. Saving a request with a link switches replies on. No server changes. Evidence: test 93.

**v138 (the date model, 6 October 2026).** Reproduced on v137 before the fix: "by the end of the week" became a firm
"By Friday 9 October", "by the weekend" a firm Saturday, "Thursday or Friday" a firm Thursday, and "within 15 working
days" a bare "By Tuesday 27 October". Every promise now records how precise its date is (`prec`: day, window, approx,
calc, none, notice), their words for it (`phrase`) and whether the day is the person's own check day (`chk`); a
promise without `prec` is from before v138 and says so. Their words always come first and Sorted's reading is marked
"about"; "Choose when to check" sets the person's own day without touching their words. "Check the app" is a next
action. The record's notice line shows only on notices (Baldwin's export, 5 October). Not built yet, on purpose: the
five objects as separate tables. The source field on other facts already exists in the ledger (v124). Two date bugs
the Tuesday run of the suite found are fixed too: "on Tuesday … but nobody turned up" said on that Tuesday is already
missed, and a correction or a move naming only a weekday ("I meant Wednesday", "They moved it to Thursday") is read in
the week of the date it changes (`corrBase()`). Evidence: test 94, and tests 09 and 62 on any weekday.

**v139 (downloads with documents, from Baldwin's WhatsApp test on 5 October).** "Download my cases" left the kept
documents behind. With documents kept it is now one .zip made on the phone: the written record and a numbered folder per
case with its documents unchanged; each record names its documents and where they are in the download. A case's
"Download it" does the same for one case. Nothing kept means one text file, as before. A document that can't be fetched
or would take the download past 60 MB is left out and named with the reason. On a phone the file waits behind "Save or
share it", because a share sheet needs a fresh tap. No server changes (the private bucket's own-folder read rule already
allows the download). Evidence: test 95.

**v140 (the second walkthrough, 6 October).** A duration is counted from when they told you: "last Wednesday … within
five working days" is read from that Wednesday, not today, and because it isn't clear whether Wednesday itself counts,
the case shows what they said, when you were told, Sorted's two readings and "Which should Sorted use?" (either day, or
"I'm not sure", which opens the check day). There is no confirmed deadline until a tap; until then Sorted waits until
the later day. A told sentence on its own ("That was last Wednesday.") counts, and "would take 3 to 5 working days" is a
calculation like "within". The words and the date are said apart ("The words are from the message you pasted. The date
is Sorted's working"), never "Found in the message" for a worked-out date. The case and Home read one next action
(`nextStepText()` now has the open step, the date choice and "check their app" in the same order as the Now card).
"Shop name not in front of me" is not a name. A half-written reminder survives the Home button (it used to clear the
form before it could be kept) and Home says it was kept. A guest's case says "Saved to Sorted. You can reopen this case
on this browser. Add an email to open it on another device." Not changed: "Still not there" on a refund still opens the
chase, as the quick answers (v130) designed; asking first is a separate decision. Evidence: test 96.

**v141 (the full audit, 6 October).** Five reviewers went through the reader, the life of a case, saving and sync, the
server, and wording and navigation; about 120 findings were reproduced and the real ones fixed in one layer. The worst:
a date said "yesterday" next to a future day became yesterday and already missed; morning and 24-hour times became the
evening; a company's own payment promise was thrown away as a demand on you; a pasted "the refund arrived" became a new
promise; the next step said "get the call ready" after a promise closed; the two-device merge kept only a few kinds of
change and brought back removed messages; a guest's moves were lost when adding an email; forwarding never showed
because its function had been revoked; and the 90-day clean-up would delete a case whose only due thing was your own
step or a renewal. Server: migration 23 (live and staging), `email-stop` v2, `send-reminders` v12. Not done, and why:
kept documents of a guest who adds an email still sit under the guest's folder (moving them needs a service-role
function; until then they can be removed by the nightly clean-up); the Android share target still sends shared text in
the URL (POST needs a service worker registered at load); the CSP still allows the whole jsDelivr host; reminders sharing
a case, kind and minute still collide on the unique key; `case-assistant` has no global daily cap (it isn't live until
its key is in Vault); `tests/` doesn't check the committed page, because `public/index.html` is not committed (Vercel
builds it). Evidence: tests 97 to 100.

**v142 (the rest of the audit, 6 October).** The six things v141 left are done. A guest's kept documents now follow
their cases to the email account: `claim_carry()` records the move and `originals-cleanup` moves the files straight
away, and the nightly clean-up leaves them alone until then. Android shares arrive through the service worker and the
page's # part, never in an address a server sees. The CSP names the jsDelivr paths Sorted uses. Two reminders due at
the same minute no longer collide. The assistant has a daily ceiling across everyone and a lower limit for guests.
Reminder emails have a visible "Stop all reminder emails" link that asks once in the app before stopping anything.
And "said yesterday it would come tomorrow" is today. Evidence: test 101 and `tests/fn/sw_share_check.mjs`.

**Still to verify on the tester's phone:** the original photograph that produced the gibberish, read through the
current build.

## Where things stand after v120

Done: Phases 0 to 4, each released through a pull request with green checks and verified on the live site by the
`live` job (v114 to v120), then the remediation items above as they are released (v121 onwards).

Outstanding, for Baldwin: branch protection; staging (secrets, anonymous sign-in, `01_run_by_hand.sql`); the Resend
delivery webhook and `resend_events_secret`; a domain and support address; the lawyer; Supabase Pro (backups);
Supabase's and Resend's retention terms quoted before any backups claim; targets; app-store accounts (Phase 5).

Outstanding, for the next builder: several people with their own references in one case and several open actions
at once (Phase 3 follow-up, when use shows the need); the staging suite's first real run once the secrets exist;
`docs/PHONE_CHECK.md` on real phones before a wider release.
