# Sorted: parked work

Written 1 October 2026, at release v36. Updated at v38 after the full audit, and on 2 October 2026 (items 17 and 18). This is the list of things we decided to build later, why each one waits,
and what is already prepared. Read this before starting any of them.

## The rule for every new feature

Does it help Sorted **understand, advance, remember or resolve** an unfinished case? If not, don't build it.
Sorted proposes, the person confirms: nothing about a case changes without a tap from its owner.

## The gate before most of this

The six-week tester pilot decides whether Sorted continues (brief: the "Sorted pilot: tester brief" doc).
Pass mark: at least 10 of 30 testers record a real promise, and at least half of those come back to the same case
around the due date. Most items below should wait for that result.

## Summary

| # | Item | Status | Blocked on |
|---|---|---|---|
| 1 | Replies come back into the case | Database change written, not applied | Approval to apply it, then about a day of work |
| 2 | Forwarding emails to a personal Sorted address | Switched off since v28; addresses removed 2 Oct 2026 | A check that the forwarder really is the account owner, or drop it in favour of item 1 |
| 3 | WhatsApp | Not started | Baldwin: Meta business account, verification, a number, running costs |
| 4 | Share into Sorted from other apps | iPhone done in v40 (Apple Shortcut); Android not started | Android needs an installed app or a manifest (see below) |
| 5 | Share a case with roles | Database change written, not applied | Accept flow and notice text, after the pilot |
| 6 | The other party replies inside Sorted | Not started | Proof the consumer side works |
| 7 | Promise data and a public scoreboard | Not started | Enough real cases, a privacy decision, legal review |
| 8 | Predictions ("usually 5 days late") | Not started | Item 7 |
| 9 | Sorted for advisers | Not started | Proof the consumer side works |
| 10 | Charging per case | Not started | Pilot pass, own name and domain, terms, checkout |
| 11 | Name clearance and own domain | Not started | A UK trade mark search by an attorney (SORTED is crowded) |
| 12 | Escalation route | Not started | Pilot result; wording reviewed so it never reads as legal advice |
| 13 | Organisation memory | Not started | Item 7's privacy decision; enough real cases |
| 14 | Family and helper view | Not started | Item 5 (roles), then design |
| 15 | Evidence timeline | Partly there: since v51 every message added to a case is kept with its source | Pilot result; storage and retention decision for files |
| 16 | "Passed between companies" | Not started | Pilot result |
| 17 | Formal cases: parking, then debt, then court admin | Release 1 of 6 done in v60: case facts with a source, confirmed by the person | Releases 2 to 6 below; the boundary checks before debt and court |
| 18 | Case assistant (reads, explains, drafts) | Not started | A privacy decision: today nothing leaves the phone except what you save |

## 1. Replies come back into the case

**Goal.** When someone emails a company from a case, the company's reply lands in that case and Sorted offers any
new date as the promise, the same card used for pasted messages (v34).

**Design.**
- Each case gets its own address, `case-<20 random hex>@<inbound domain>`.
- v36's "Open in your email app" button adds that address in **Cc**, so a company's "reply all" reaches Sorted.
- The `inbound-email` function stores the reply with the case id and the sender's domain only, never the full address.
- The app shows it inside that case as a proposal: "From their email (currys.co.uk). Check it's genuine before you say yes."
- Forged mail can only ever create a proposal the owner must confirm. Links in it are never made clickable.

**Prepared.** `supabase/parked/01_case_reply_structure.sql` holds the table `case_mail`, two new columns on
`inbound_items`, and `case_reply_address(task_id)`. That function returns nothing unless the Vault secret
`case_replies_on` is `yes`, so applying it changes nothing visible.

**To switch on.**
1. Apply the SQL.
2. In `supabase/functions/inbound-email`:
   - Verify the webhook signature first, for every message.
   - Move the `FORWARDING_OFF` check inside the `log-` branch, after the signature check. Today it returns before
     anything else, which would also block `case-` replies.
   - Loop over every address in `to` and `cc`, not just the first `to`, because a reply-all can list the case address anywhere.
   - Add the branch for `case-` addresses.
3. Build the app side:
   - Fetch `case_reply_address` when a case opens.
   - Add `cc=` to the mailto.
   - Show items with a `task_id` in that case, not in the Home inbox. The current inbox wording says "You forwarded", which would be wrong.
4. Update the privacy notice: Resend receives replies, and they are kept 30 days.
5. Set `case_replies_on` to `yes`.

**Test.** A reply with a new date becomes a card in the right case. A reply to an unknown address is dropped.
Deleting the case deletes its address and items.

## 2. Forwarding to a personal Sorted address

Switched off in v28 (`FORWARDING_OFF = true` in `inbound-email`, and `forwardHint()` returns nothing).

The reason: it trusts that an email "from" the account owner really came from them, and email senders can be faked.
Either add a sender check (DKIM and SPF results for the forwarder's domain) or retire it once item 1 exists. Item 1 is
the better product, because companies reply to the case directly.

## 3. WhatsApp

**Needs Baldwin first.**
- A Meta business account and business verification.
- A phone number for the WhatsApp Business Platform.
- Approved message templates for reminders, since Sorted cannot start a conversation without one.
- A budget for per-conversation charges.

**Design.**
- A webhook edge function receives forwarded messages and runs the same extraction as `sugFromMessage` (move that
  logic into a shared module both the page and the function can use).
- It replies "Add this to your British Gas case? Yes / No".
- Reminders go out as a template message quoting the promise.
- **Privacy.** Meta becomes a processor, so this needs a DPIA and notice changes.

## 4. Share into Sorted from other apps

Only Android supports sharing into a web app (a `share_target` in a web app manifest). iPhones do not.

The catch: adding a manifest with `display: standalone` makes "Add to Home Screen" on iPhone open Sorted as a
separate app with separate storage. Anyone without an email would lose sight of their cases.

Revisit when every user has an email account, because cases then sync by account and storage no longer matters.

## 5. Share a case with roles

**Prepared.** `supabase/parked/02_case_members.sql`: `case_members` (roles `view` and `note`) and `case_notes`,
with row level security.

**Principle.** A helper never edits the case record. They see a share card and can add a note, which the owner sees in the history.

**Still to design.**
- The accept flow: they sign in with the invited email, and an RPC sets `member_id`.
- The invite email.
- Notice text.
- How notes appear in the case history.

Today's view-only link and helper email nudges already cover "a second person sees the promise".

## 6. The other party replies inside Sorted

Kept out on purpose: it makes Sorted responsible for delivery, identity, disputes and abuse. Screenshots, PDFs and
item 1 give most of the benefit.

If revisited, the light version is a one-time link a landlord can use to propose a date. It arrives as a proposal the
owner confirms, never as a change.

## 7. Promise data and a public scoreboard

**Goal.** "Currys pays refunds on time X% of the time, median delay N days", from real case journeys.

**Needs.**
- **A privacy decision.** Step records currently hold no case details, and the notice promises that. Adding the company
  name, taken only from the fixed company list in `PARTIES`, never free text, means changing the notice and asking people.
- **Enough data.** Minimum sample sizes before any number is shown (for example 50 promises per company and type).
- **Rigour.** Method notes, matching company names, fraud protection, a correction process, and legal review before publishing anything.

## 8. Predictions

Only after item 7 has credible data. Use it to improve the plan ("Sorted will check with you at 13:00"), never to
predict failure ("they probably won't come").

## 9. Sorted for advisers

A light view for Citizens Advice style advisers, housing officers and carers, invited by the person who owns the case.
Builds on item 5. Possible business revenue later.

## 10. Charging per case

Start free. Test a one-off price to "keep this case on watch until it's sorted" (try £4.99, £7.99, £9.99), offered
right after the first real promise is recorded.

Needs: pilot pass, item 11, terms, a refund policy, Stripe checkout, and a support address.

## 11. Name clearance and own domain

SORTED is a crowded name:
- Sorted Holdings Limited (parcel delivery software, sorted.com) has SORTED marks covering software.
- There is a Sorted AI reminders app.
- **Sorted³ - Calendar Notes Tasks** (StaySorted Limited) is on the UK App Store: a calendar, tasks and notes app, free
  with a £14.99 PRO upgrade, 4.7 from 902 ratings, last updated October 2024. It is the closest clash: same store,
  same category (Productivity), overlapping purpose (tasks and reminders). Shipping an iPhone app called "Sorted"
  next to it is the riskiest version of this name. Whether StaySorted holds registered marks is for the attorney's search.

Get a UK trade mark search by an attorney before spending on brand. getsorted.uk was registered earlier. Move off
sorted-pilot.vercel.app before charging anyone.

## 12. Escalation route

**Goal.** When a case has gone round more than once, Sorted shows the next formal step, as information, not advice:
"You've chased them twice and the date has passed. Most companies have a formal complaints process. After 8 weeks, or
a final response, you can usually go to the Ombudsman for that sector."

**Design.**
- Triggered by facts Sorted already holds: number of missed promises, chases sent, weeks since the first contact.
- A small fixed table of sectors and their routes (energy, telecoms, financial services, housing, councils), with the
  official link and the waiting period, written and dated by a person. No generated legal text.
- The step is offered, never pushed. "Keep chasing" stays the default.
- Say what Sorted doesn't know, the pattern from the benefits and housing notes.

**Needs.** The sector table checked against each Ombudsman's own pages, a review date on it, and wording that can't be
read as legal advice.

## 13. Organisation memory

**Goal.** Practical knowledge about a company, learned across cases: the channel that worked, the department, what
their reference numbers look like. "People reached British Gas fastest through webchat."

**Design.**
- Only from the fixed company list (`PARTIES`), never free text. Only counts and categories, never case content.
- Shown as a hint inside a case, with how many cases it's based on and a minimum sample before anything shows.
- The person's own past cases with that company come first ("Last time you used reference BG-…").

**Needs.** The same privacy decision as item 7, because it pools behaviour across users. Notice changes first.

## 14. Family and helper view

**Goal.** Manage a problem for someone else, such as a parent, together:
"Mum's boiler · British Gas said Friday 8–12 · Baldwin contacted them · Nothing needs either of you until Friday 12:00."

**Design.** Builds on item 5 (roles). One case shared with named people, each sees who did what last, and Sorted's one
next step is the same for everyone. Still one case at a time: "share this problem, not your whole life".

**Needs.** Item 5's accept flow, consent from the person the case is about, and notice text about acting for someone.

## 15. Evidence timeline

**Goal.** Everything that proves what happened, in order, with where each fact came from: "From their message (photo
of the letter)", "You wrote", "Sorted read this date". Exportable as one page for a complaint or the Ombudsman.

**Already there.** Case history, "In your words", screenshots and PDFs read on the phone, pasted messages, the recap.
Since v51 every message brought into a case (pasted, a screenshot, a PDF, shared from another app, or matched from the
start box) is kept in the history with where it came from, even when it has no date.

**Intake, next slices (in order).**
1. ~~Show evidence lines in the case as their own small block ("What they sent")~~ Done in v52.
2. ~~Share straight into a chosen case from the Shortcut~~ Done in v53: a shared message asks "Where does this go?", with the likely case first.
3. Let the person correct which case a message belongs to after it was added.
4. Only then, keeping original files (see below).

**Still to do.** Keep the original files (today only the text is kept, and only up to 300 characters), mark each
line's source, and an export page. Storing files is a real privacy and cost step: decide retention, size limits and
where files live before building.

## 16. "Passed between companies"

**Goal.** When responsibility moves (retailer → courier → manufacturer, landlord → agent → contractor), the case shows
who has it now and who said it was someone else's job: "Currys said it's DPD's problem (Tue 3 Oct)."

**Design.** A promise or note can name a hand-off. The case title follows the current holder, and the chase quotes the
hand-off ("You told me on 3 October that DPD were responsible"). Uses the existing party detection.

**Needs.** Pilot evidence that hand-offs are common enough to justify it.

## 17. Formal cases: parking, then debt, then court admin

**Goal.** Cases with a notice, a reference, several dates that mean different things, and a formal process: council
PCNs and private parking charges first, then debts and payment plans, then simple court and tribunal administration.
These are pure Sorted: another party, a reference, deadlines, evidence, and a cost to losing the thread.

**Design.**
- **Typed deadlines.** One case holds several dates, each with its meaning: discount ends, challenge deadline, payment
  due, evidence due, hearing. Each is checked against "Check the official source", never assumed.
- **A facts block** for these cases only: what it is, reference, amount, stage, next deadline, who has the ball.
  Read from the notice (photo or PDF, on the phone), shown as "I found these details. Are they right?", and only
  saved once the person confirms each fact.
- **Stages, not just promises.** Notice received, challenge sent, waiting, decision, next stage. A rejection letter
  moves the case to the next stage and makes the new deadline the important thing.
- **Proof of submission.** What was sent, when, where, the confirmation number and the exact text. The case then
  waits on them: "Challenge sent 8 Oct, ref ABC123. You can put this down until 5 Nov."
- **Official route, specific to the case.** The right body's own appeal, payment or complaint page. Hand-written
  and dated, like the renewals table and item 12, never generated.
- **Drafts from confirmed facts.** A challenge, dispute or breakdown request built from a fixed template, the facts
  the person confirmed and the grounds they choose, in their own words. No invented facts.
- **For your adviser.** A one-page summary, chronology, deadlines, documents and the questions the person wants
  answered. Takes the evidence timeline (item 15) further.
- No "Legal" section on Home. The case screen adapts to the kind of case.

**Boundaries to settle before building (to be checked, not assumed).**
- **Advice.** Sorted organises and drafts what the person decides. It doesn't say whether to pay, challenge, plead
  or settle, or that an appeal will succeed. High-stakes matters (criminal, family, immigration) get "Sorted can keep
  your dates and documents together. It can't tell you what legal position to take."
- **Debt.** Advising someone on their specific debts and recommending a course of action may be FCA-regulated debt
  counselling. Check with a regulatory lawyer first. Until then Sorted records what was agreed and points to free
  debt advice (MoneyHelper, StepChange, Citizens Advice); it doesn't suggest a debt solution.
- **Offence data.** Council PCNs are civil, but court cases can involve criminal offence data, which UK GDPR
  (Article 10) and the DPA 2018 treat separately. Needs a DPIA entry and notice text before Sorted holds it.
- **Process tables.** Council and private parking routes differ (councils: representations, then the tribunal;
  private operators: the operator, then POPLA or the IAS). Each entry needs a source and a review date.

**Order.** Parking first: easy to understand, highly structured, time-sensitive and common. One reusable resolution
engine, with parking as its first playbook (Baldwin's plan of 2 October 2026), in six releases:
1. ~~Case facts and provenance~~ Done in v60. A parking notice (typed, pasted, shared, a photo or a PDF, all read on
   the phone) becomes proposed facts, each with where it came from; nothing counts until the person confirms it.
   A later letter only asks about what is new or different, and shows what it said before.
2. ~~Parking playbook~~ Done in v61: stages (notice, challenge sent, waiting, rejected, Notice to Owner, formal
   challenge, appeal, finished), dates that say what they mean, worked out on the safe side from confirmed facts,
   proof of what was sent, and waiting on them through the usual promise engine.
3. ~~Official routes~~ Done in v62: a hand-checked registry (council site via GOV.UK, TfL, GOV.UK guides, London
   Tribunals, Traffic Penalty Tribunal, Scotland, Northern Ireland, POPLA, IAS, Citizens Advice), checked 2 Oct 2026.
4. ~~Challenge builder~~ Done in v63: tick what's true (with your own words), a draft from that and confirmed facts
   only, "Uses 6 confirmed details and 2 things you told Sorted", a completeness check, copy, and the exact text kept
   when you say you've sent it.
5. ~~Response reader~~ Done in v64: a reply is read for what kind of decision it is, their reasons, what it skips
   from your challenge and evidence, and a re-offered reduced price; proposed, then confirmed, then the stage moves.
6. Adviser pack: summary, chronology, deadlines, evidence and questions, as one page to copy or download.
AI is for extraction, classification, explanation and drafting only, and waits for item 18's privacy decision.
Releases 1 to 4 work on the phone without it.

## 18. Case assistant

**Goal.** An assistant that works inside the case it is in, not a chat bubble: explain a letter in plain English
("This is a Notice to Owner, a later stage than the ticket"), say what changed, ask the questions that matter,
list points that may be relevant and let the person confirm which are true, compare a rejection with the original
challenge ("Their reply doesn't address the receipt you sent"), check a draft for contradictions and missing
evidence, and write the follow-up when a promised date passes.

**Rule.** Sorted may suggest. The person confirms. It never invents facts, never submits anything on its own, never
says someone is liable, and never promises an outcome. It separates what the document says from its own reading.

**Needs, in order.**
1. **A privacy decision.** Today screenshots and PDFs are read on the phone and "Nothing is uploaded". An assistant
   means sending case content to a model provider. That needs a DPIA, a processor agreement, changes to the notice,
   and probably a per-case opt-in ("Let Sorted's assistant read this case").
2. The advice boundary from item 17, built into the prompts and tested against a corpus, like the promise reader.
3. Item 17's structure first. The assistant is far more useful, and safer, when the case already has confirmed facts,
   typed deadlines and stages to work from.

## Backend fixes from the v37 audit (all applied 2 October 2026)

`supabase/parked/03_audit_fixes_v37.sql` is the database half of the v37 audit. It was offered three times and cancelled at
approval each time, so it has **not** been applied.

On 2 October Baldwin chose the reliability part and ran `supabase/parked/04_reliability_v39.sql` himself in the SQL
editor. `send-reminders` v8 (claims reminders and helper invites before sending) went live straight after.
The rest (helper protections, tidy-ups, idle-account deletion) followed the same night as `05_remaining_v41.sql`,
after release v41 put the two new rules in the privacy notice. **The whole audit is now applied.** Nothing in v37's page depends on it. Apply it only with Baldwin's go-ahead.

What it does:
- **Helper emails.** A log and a suppression list, so one case can't be used to email a stranger repeatedly, and
  someone who says no is never emailed again (`invite_helper`, `helper_respond`).
- **Caps.** Per-case reminder limit, per-account step record limit, and a size limit on `tasks.data`.
- **No double sends.** `claimed_at` with `claim_due_reminders` and `claim_helper_invites`, so two cron runs can't send the same email.
- **Robustness.** `try_ts()`, so one malformed date can't break `sorted_case_live` and the retention job.
- **Clean-up.**
  - Revokes `my_inbound_address` and empties `inbound_addresses`.
  - Narrows table grants and revokes `net` access from app roles.
  - Caps `report_auth_error` per kind.
- **Speed.** `(select auth.uid())` in policies, and indexes on `helpers.user_id` and `reminders.user_id`.
- **Retention.**
  - `pilot-carry-cleanup`.
  - `sorted-idle-accounts`: deletes email accounts idle for 12 months, except pilot admins. The notice would need a line before this runs.

When it is applied, also:
- switch `send-reminders` to `claim_helper_invites` and `claim_due_reminders` (reset `invite_sent_at` to null if a send fails);
- add two lines to the notice: a stopped helper's address is kept as a one-way hash so they're never emailed again, and an
  account with an email but no cases is deleted after 12 months without a sign-in.

## Residual risks we chose to accept for the pilot

- **pdf.js 3.11.174** has a known flaw that `isEvalSupported:false` blocks. Upgrade to pdf.js 4 or later when there is time.
- **An old personal email address is still in git history.** It was removed from the current files. Removing it from
  history needs `git filter-repo` and a force push to both branches. Baldwin's call.
- **The new security headers** (`vercel.json`) are tested in Chromium. Check screenshots and PDFs once on a real iPhone.

## Where Sorted fits (use-case map, 2 October 2026)

**Thesis.** Organisations have case-management systems; the individual has screenshots, Notes, email and memory. Sorted is
the individual's own side of the case: anything unresolved, involving another party, that you may need to wait on,
remember, prove, chase, escalate or close.

**Heuristics for "this belongs in Sorted".** Someone gave you a reference number. Someone said "3 to 5 working days" or
"we'll call you back". An appointment was missed. Responsibility moves between organisations (retailer, courier,
manufacturer). Evidence builds up over time. It might need escalating.

**Already strong today:** refunds, deliveries, repairs and landlords, utilities and telecoms, engineer visits,
benefits and council chases, missed appointments.

**Good next areas, same machinery:** insurance claims, travel refunds and lost luggage, garages, job applications,
complaints and escalation (company, then Ombudsman), deposits, marketplace disputes, helping a parent.

**Careful areas.** Health administration, immigration, legal matters, bereavement and fraud recovery fit the shape but
carry special-category or highly sensitive data. Sorted's notice already asks people to leave health details out.
Keep these out of the pilot's examples; revisit only with a DPIA and notice changes.

**Out of scope (unchanged).** Groceries, habits, calendar events, medication reminders, birthdays, generic to-dos.

**Ideas that build on what exists:** items 12 to 16 above (escalation route, organisation memory, family and helper
view, evidence timeline, passed between companies).

## Lessons from Things 3 (looked at 2 October 2026)

Things 3 (Cultured Code) is an iPhone to-do app: £9.99 one-off, 4.8 from about 4,300 UK ratings, No. 2 in Productivity.
It tracks what **you** have to do. Sorted tracks what **someone else** owes you, so we copy its habits, not its scope.

| | Things 3 | Sorted |
|---|---|---|
| Core object | Your to-do | Their promise: who, what, by when, reference |
| Home | Today, Upcoming, Anytime, Someday | Needs you, Waiting, Done |
| Getting things in | Quick Entry anywhere, share sheet, Siri, widgets, Mail to Things | Type, paste, screenshot or PDF, inside the page only |
| Dates | "When" (when you'll do it) and "Deadline" kept apart | Their due time, plus Sorted's check-in after it |
| When it slips | Nothing happens; it moves to overdue | Asks if it happened, drafts the chase quoting their words |
| Sharing | None | Helper link and nudges |
| Platforms | Apple only, separate purchases | Any phone with a browser |
| Price | One-off, no subscription | Free pilot; per-case price idea (item 10) |

**Worth borrowing.**
- **Capture from anywhere.** Things is a daily habit because adding takes two seconds from any app. Sorted can get part of
  this on iPhone without a native app: an Apple Shortcut in the share sheet that opens
  `sorted-pilot.vercel.app/#new=<text>`. The text goes in the fragment (after `#`), which browsers never send to the
  server, so it can't land in Vercel's logs. The page fills the case box and waits for the person to press Start;
  it never creates a case by itself. Built in v40; the Shortcut steps are in `docs/SHARE_SHORTCUT.md`.
- **Restraint.** Things shows few lists and little chrome. Keep Home to three states.
- **One-off price as a reference.** People pay £10 once for calm and reliability, so a per-case price must feel clearly
  worth more than a whole to-do app.

**The best clue on its App Store page.** A UK reviewer made their own "Waiting for" area in Things by hand. Things has
no idea of another person's outstanding obligation, so users bolt one on. That state is Sorted's whole product.

**Positioning.** Things answers "What do I need to do?" Sorted answers "What's happening with that problem?" The relief is
specific: you don't have to keep remembering whether they got back to you.

**Not borrowing.** Projects, areas, tags, checklists, repeating to-dos. They turn Sorted into a to-do list, which the
pilot rules already rule out.

## Smaller follow-ups noticed along the way

- **Measuring the card.** Since v38 a confirmed suggestion's `promise_created` step carries `src` = `sentence` or
  `message` in `props`. `pilot_metrics()` doesn't split by it yet.
- **Checks still to do on real phones.**
  - Reading screenshots and PDFs over mobile data (first use downloads about 4 MB).
  - "Open in your email app" on iPhone.
  - Photos of paper letters, which are less reliable than screenshots.
- **Company list.** `PARTIES` in build30 is a fixed list. Add the names testers actually use.
