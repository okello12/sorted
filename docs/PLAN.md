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
| Cases are stored in London | Supabase project `boxrwcuhxmimayaxzywu`, region eu-west-2 | Configuration |
| A guest has a server account; only the browser that made it holds the key | Supabase anonymous sign-in, `anon-start`; tests 47, 61 | Tested |
| A guest's cases carry across when they add an email | `stash_carry()`, `claim_carry()`; test 61 | Tested |
| A guest account is deleted after 30 days without use | Job `sorted-anon-cleanup` (daily 03:37): deletes an anonymous user whose **last sign-in** (or creation) is over 30 days old, unless a case was updated in 30 days or a promise is live; cases go with it | Configuration. Not acceptable as is: see below |
| Idle cases are deleted after 90 days | Job `sorted-retention-90d`: not updated for 90 days, unless a promise is live | Configuration. "30 without an email" in older copy only happens through guest deletion |
| Reminder emails are scheduled every 10 minutes | Job `sorted-send-reminders` `*/10 * * * *`; edge function `send-reminders` v9 | Scheduling only. **Unverified: when emails arrive** |
| Reminder emails contain no case details | `send-reminders` source | Code; add a test on the email body |
| Photos and PDFs are read on the phone, never uploaded | `readPicture()`, `pdfToText()`; tests 10, 18, 22; CSP (test 13) | Tested |
| Changes made offline are saved later | Test 56 (failed save kept, saved once online); test 66 (two devices merged; deleted elsewhere) | Tested for these cases only |
| Helper links: anyone with the link, read-only, until switched off or 30 days without a change; deleted after 90 | `get_share()`; job `shares-retention`; tests 60, 61; staging suite | Tested |
| Usage records hold no case content | `pilot_events`: step name, case and promise ids, small props; tests 31, 51, 60 | Tested. **Not anonymous**: each holds the account id and case id |

**Reminder delivery evidence.** Accepting an email measures sending, not arrival. Record per reminder: the scheduled
time, the time it was submitted to Resend, Resend's acceptance (`provider_id`), and delivery, bounce or failure events
from Resend's webhooks where available. Until that data supports a timing claim, the wording stays: "Sorted sends an
email at the time it shows. When it arrives depends on email, and it can be late or not arrive."

**Guest deletion: a rule to define, not just reword.** Someone who opens Sorted regularly would expect their cases to
stay. Before this rule is described or relied on:

1. Define activity: opening Sorted while signed in as the guest (the page refreshes the session, which updates
   `last_sign_in_at` only on a new sign-in, not on a return visit, so this needs a lightweight "seen" timestamp written
   on load), saving a case, or a live promise.
2. Change `sorted-anon-cleanup` to use that definition.
3. Test the exceptions on staging with a real guest account: opened daily with no edits; a live promise; no visit for 31
   days.
4. Explain it in the app before it applies: "Without an email, your cases are deleted after 30 days in which you don't
   open Sorted."

**Wording to correct now:**

- "Sorted keeps nothing you delete" (terms): untrue, usage records remain. Use the deletion answer below.
- "Nobody running it reads your cases" (About): use the privacy notice's wording everywhere (technical access as any
  operator has; not used to read cases).
- "The official page is always right and Sorted is not": "Check the relevant authority's current guidance before
  acting. Links and guidance can change."
- Guest copy is about access, not loss: "Your cases are saved on Sorted's servers, but without an email only this
  browser can open them."
- "Step records" become "usage records without case content", never "anonymous".

**Deletion, answered coherently.**

*Deleting one case.* It is removed from the database straight away, with its helper link (which stops working) and its
unsent reminders (`case-del`; test 12). For two minutes Home offers Undo. During that time the only copy is in the open
page on this phone: **closing or refreshing the page, or tapping anything else, ends recovery**, and the app says so
next to Undo. Undo saves it back as a new copy without the helper link (test 69). Usage records mentioning the case id
(no content) remain up to 12 months (`pilot-events-retention`). Emails already sent stay in your inbox.
Test to add: another device that was offline with the case open must not bring the deleted case back when it
reconnects (today `saveConflict()` removes it locally when the row is gone; prove it for an edit made offline).

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

**Phase 0 (v114, 4 October 2026).**

- 0.1 The gate is in place. Releases go through a pull request; the `staging` job now runs on pull requests too
  (it passes with a note until the staging secrets exist); the new CI job `live` (`tests/live/verify_live.py`) runs
  after each push to `main`, waits until the live page is byte for byte that commit's build, then walks it with a
  throwaway guest account that deletes itself. Not done: GitHub branch protection that *forces* the checks before a
  merge. That is a repository setting, left for Baldwin to approve.
- 0.2 Isolation proven on v113: every file's output kept separately (`tests/runner.py`), one serial run and two runs
  six at a time in different random orders (seeds 11 and 29). All 72 files green in all three; the only differences
  were random case ids in two messages and one timing (60-case Home 1.14s serial, 1.85s parallel, inside its
  budget). Nothing was shared: generated images and PDFs have names unique to their file, `tests/out/index.html` and
  `reader.html` are only read, there are no ports. Serial 22 minutes, six at a time about 6. CI runs four at a time.
- 0.3 Sign-out keeps unsaved work (build114, test 71).
