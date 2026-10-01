# Sorted: parked work

Written 1 October 2026, at release v36. This is the list of things we decided to build later, why each one waits,
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
| 2 | Forwarding emails to a personal Sorted address | Built, switched off since v28 | A check that the forwarder really is the account owner, or drop it in favour of item 1 |
| 3 | WhatsApp | Not started | Baldwin: Meta business account, verification, a number, running costs |
| 4 | Share into Sorted from other apps | Not started | Accounts with email for everyone first (see below) |
| 5 | Share a case with roles | Database change written, not applied | Accept flow and notice text, after the pilot |
| 6 | The other party replies inside Sorted | Not started | Proof the consumer side works |
| 7 | Promise data and a public scoreboard | Not started | Enough real cases, a privacy decision, legal review |
| 8 | Predictions ("usually 5 days late") | Not started | Item 7 |
| 9 | Sorted for advisers | Not started | Proof the consumer side works |
| 10 | Charging per case | Not started | Pilot pass, own name and domain, terms, checkout |
| 11 | Name clearance and own domain | Not started | A UK trade mark search by an attorney (SORTED is crowded) |

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
2. In `supabase/functions/inbound-email`, add a branch for `case-` addresses. Keep the personal `log-` branch behind `FORWARDING_OFF`.
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

Get a UK trade mark search by an attorney before spending on brand. getsorted.uk was registered earlier. Move off
sorted-pilot.vercel.app before charging anyone.

## Smaller follow-ups noticed along the way

- **New steps aren't measured separately.** v33 to v36 record a confirmed suggestion as an ordinary "promise added".
  To measure whether the card helps, add step names such as `promise_from_sentence` and `promise_from_message` to the
  allowed list in the database and send them from `sug-yes`.
- **Checks still to do on real phones.**
  - Reading screenshots and PDFs over mobile data (first use downloads about 4 MB).
  - "Open in your email app" on iPhone.
  - Photos of paper letters, which are less reliable than screenshots.
- **Company list.** `PARTIES` in build30 is a fixed list. Add the names testers actually use.
