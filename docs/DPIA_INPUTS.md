# DPIA inputs: what Sorted does with data, from the code

Written 11 October 2026, for the release assurance dossier (section 2). This page holds facts the code and
configuration can establish. It isn't a DPIA, and it makes no legal judgement: lawful bases, transfer mechanisms and
sign-off belong to the controller and a privacy professional. Rows marked **To confirm** need someone with access to
the supplier's dashboard or contract. Sources are named so each line can be checked. No case content was read to write
this.

## 1. Who and what

- **Controller as the site states it:** "run by Baldwin Thompson-Addo in London, for people aged 18 and over in the
  UK" (Help & About, and the terms in the page). No company is named. **Open for the controller:** a legal entity or
  sole trader, a service address, and whether a DPO is required.
- **People whose data is processed:**
  - account holders: guests (anonymous sign-ins) and email accounts;
  - helpers who open a shared link;
  - third parties named in cases or in documents people add (companies' staff, landlords, engineers);
  - senders of emails forwarded to a person's Sorted address.
- **Not asked for, but may arrive in free text or photos:** health, money, children, offences. Sorted masks bank, card,
  sort code, IBAN, NI and passport numbers read from photos before they reach a case (build145 C, test 112), and serial
  numbers everywhere except a deliberate Show or Copy (build161, test 129). It does nothing to special-category words
  people type themselves.

## 2. Where data goes

| Recipient | What it receives | When | Where it says so | Notes |
|---|---|---|---|---|
| **Supabase** (database, auth, storage, edge functions) | Everything saved: cases (`tasks.data`), reminders, shares and helper notes, forwarded emails, kept documents (bucket `originals`), push addresses, usage records (codes and ids), error reports (codes, quoted words removed) | On every save | Privacy notice: "Supabase stores your cases on servers in London" | Project in London. **To confirm:** Supabase's own support and log access, and where its sub-processors run |
| **Vercel** | The page itself. Request logs hold IP address, user agent and the address asked for, including `?task=<case id>&ans=…` from reminder links. The part after `#` (case ids in `#case-…`) is never sent | Every visit | Named in the notice ("Vercel hosts the website") | Static site, no server code on Vercel. **To confirm:** log retention on this plan, and region |
| **jsDelivr** (CDN) | The visitor's IP address and user agent when the browser fetches the database library, Tesseract (photo reading) and pdf.js. No case data: photos and PDFs are read on the phone | First use of each library | **Not named in the privacy notice.** Gap for the solicitor | Versions pinned with integrity hashes (CLAUDE.md, Pinned versions) |
| **Resend** (email) | Reminder emails: recipient address, fixed wording, links with case and promise ids, never case words (test 72, `send-reminders`). Sign-in codes if Supabase Auth uses Resend's SMTP. Forwarded emails and case replies arrive through Resend (inbound webhook) | Per reminder, per forwarded email | Named ("Resend sends Sorted’s emails"; replies "received by Resend and kept for 30 days") | US company. **To confirm:** the account's data region, and which SMTP Supabase Auth uses for codes |
| **Push services** (Apple, Google, Mozilla, Microsoft) | An encrypted message (RFC 8291) the service can't read: fixed wording, a case id link and answer links. The service also sees the phone's push address and when messages are sent | Per reminder, when a person turns lock-screen reminders on | Named ("issued by Apple, Google, Mozilla or Microsoft") | Payload built in `send-reminders` (`msg`: `t`, `b`, `u`, `g`, answers) |
| **Anthropic** (assistant) | The case, capped at 9,000 characters, with serials scrubbed | Only when the person taps the assistant | Named, with "doesn’t use it to train its models" | **Switched off:** no `anthropic_api_key` in Vault |
| **GitHub** | Code only. CI walks the live site as a throwaway guest and deletes it | Each release | None needed | No user data |

The notice says "All four are US companies, so your data may be processed in the US under their data protection
terms". The mechanism (UK IDTA, the UK Addendum, or the UK Extension to the Data Privacy Framework) isn't named.
That is for the solicitor.

## 3. What stays on the phone

Browser storage, never sent anywhere by itself. All of it is removed at sign-out and on account deletion by
`clearLocalUserData()` (test 78), except the appearance setting.

| Key | Holds | How long |
|---|---|---|
| `sorted.cache.<user>` | A copy of the person's cases, for speed and offline use | Until sign-out |
| `sorted.draft.<user>`, `sorted.form.*` | Half-written words | 7 days, or sign-out |
| `sorted.evq`, `sorted.oq145.<user>` | Usage records and outcomes waiting to be sent | Until sent |
| `sorted.gone.<user>`, `sorted.redel.<user>`, `sorted.wids.<user>` | Ids of deleted cases and write ids (no content) | Short-lived bookkeeping |
| `sorted.carry`, `sorted.carrytok`, `sorted.carry82`, `sorted.cap82`, `sorted.moment` | A guest's cases on their way to an email account; a start choice carried through sign-in | One hour to one day |
| `sorted.sharedIn` | Words shared into Sorted from another app, until placed | Until used |
| `sorted.theme`, `sorted.nudge133`, `sorted.aiSeen`, `sorted.nosteps` | Appearance, "asked once" flags, the usage-records switch | Kept |
| Supabase's own `sb-…` key | The sign-in session | Until sign-out |

There are **no cookies**: the page never sets `document.cookie`, and there are no analytics or advertising tools. The
storage above is what the service needs, plus the appearance setting and "asked once" flags. Whether any of it needs
consent under PECR regulation 6 is for the solicitor. The likely answer is "strictly necessary", apart from the usage
records, which have their own switch.

## 4. How long things are kept

From the retention jobs (pg_cron on live, 11 October 2026) and the edge functions.

| Data | Kept | Mechanism |
|---|---|---|
| A case | 90 days after its last change, unless something is still live: a promise, a dated step, a renewal before expiry, a deadline on you, a Moving home date, an attention item or Later | `sorted-retention-90d`, `sorted_case_live()` (migrations 23 and 25) |
| A guest account | 30 days with no sign-in, no visit, no case saved and no live promise | `sorted-anon-cleanup` |
| An email account with no cases | 12 months without a sign-in or visit (not admins) | `sorted-idle-accounts` |
| Kept documents | Removed daily once their case has gone | `sorted-originals-cleanup` |
| Helper links | Stop working after 30 days, deleted after 90 | `shares-retention` |
| Helper notes | **To confirm** the exact period | `sorted-notes-retention` |
| Forwarded emails and replies | 30 days, or until added or removed | `sorted-inbound-cleanup` |
| Usage records | 12 months | `pilot-events-retention` |
| Company outcome totals | **To confirm** the exact period | `sorted-outcomes-retention` |
| Error reports | 90 days | `ops-errors-retention` |
| Assistant usage counts | **To confirm** the exact period | `sorted-assistant-usage` |
| Carry tokens | 1 day | `pilot-carry-cleanup` |
| Backups | None exist (free plan) | `docs/RECOVERY.md` |
| Copies at Resend, Vercel and the push services | **To confirm** | Their own retention |

## 5. People's rights, as built

| Right | How | Test |
|---|---|---|
| Access and portability | Account > "Download my cases": every case, with kept documents as a .zip | 95 |
| Correction | Edit or "Correct a detail" on any case. Old values stay in the case history, labelled | 62 |
| Erasure | Delete a case (2-minute Undo, then gone from the server). Delete the account (server and phone) | 69, 78, live check |
| Objection to usage records | Settings switch. Records stop at once | 31 |
| Withdrawing a share | Switch the helper link off | 60 |
| Stopping emails | Settings, a per-case switch, and the stop link in every email | 74, 101 |

Not built: a way to answer a subject access request about someone who isn't a user but is named in a case. Their data
sits only inside the account holder's case, which nobody running Sorted reads. The controller needs a written answer
for that request.

## 6. Already-written facts to correct

- `docs/RECOVERY.md` said deletion had "no undo". Since v112 there is a 2-minute Undo. Corrected on 11 October 2026.
- The privacy notice doesn't name jsDelivr (section 2). For the solicitor's redline, not changed here.
