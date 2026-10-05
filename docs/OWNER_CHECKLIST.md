# What only Baldwin can do

Things Sorted needs that cost money, need a person's judgement, or need your approval. In order of what matters most
before more people use Sorted. Updated 5 October 2026 (v137).

## 1. Approve the server changes for v133 to v135

The app updates for lock-screen reminders, forwarding and kept documents need these on Supabase. Claude applies them
when you approve the prompts. Nothing here touches case content. v133 to v137 are built and tested on pull request 42
and are released together once these are in place (v137 itself needs no server change). On 5 October the approval
for migration 19 came back "cancelled" four times, so nothing has been applied yet: say "go ahead with Supabase" in a
session where you can approve the prompts as they appear.

| Change | Live | Staging |
|---|---|---|
| Migration 19 `push_subs`, `push_save/drop/state` (`supabase/parked/19_push_v133.sql`) | yes | yes |
| Vault secret `vapid_private_jwk` (the notification signing key; never shown) | yes | no |
| Deploy `send-reminders` v11 (with `webpush.ts`) | yes | no |
| Migration 20 `inbound_address_new()` (`supabase/parked/20_forwarding_v134.sql`) | yes | yes |
| Deploy `inbound-email` v7 | yes | no |
| Migration 21 bucket `originals` and its rules (`supabase/parked/21_originals_v135.sql`) | yes | yes |
| Deploy `originals-cleanup` v1, then schedule `sorted-originals-cleanup` (27 3 * * *) | yes | no |

Forwarding also needs Resend inbound mail on the `inbound_domain` already set for case replies; nothing new there.

## 2. Backups: Supabase Pro

The project is on the free plan: no backups (`docs/RECOVERY.md`). Pro (about $25 a month) adds daily backups kept for
7 days, and more storage for kept documents (the free plan has 1 GB in all). Before anyone relies on Sorted for
evidence, this matters more than any feature. Supabase dashboard > Organization > Billing.

## 3. A name and a domain

`sorted-pilot.vercel.app` looks temporary to the people Sorted asks to trust it with their problems. "Sorted" is a
crowded name (`docs/LATER.md` item 11): a UK trade mark search by an attorney first, then a domain. Once you have one,
Claude adds it in Vercel, updates `SITE` in the functions and the CSP, and points email at it.

## 4. A lawyer's read of the terms and the privacy notice

The terms are version 1 and say they haven't been checked by a lawyer. The privacy notice now also covers lock-screen
reminders, forwarding to a secret address and kept documents. A short read by someone who does UK consumer and data
protection work. Your own DPIA entry should cover the push services (Apple, Google, Mozilla, Microsoft) and stored
documents.

## 5. The real-phone check

`docs/PHONE_CHECK.md`: 20 minutes on an iPhone with VoiceOver and an Android phone with TalkBack. Add for v133 to v135:

- Add Sorted to the Home Screen.
- Switch on "Get reminders on this phone".
- Make a case due in a few minutes and see the notification on the lock screen.
- Forward an email to your Sorted address.
- Share a message into Sorted on Android.
- Keep a photo with a case, then open it.

## 6. Still open from before

- Staging secrets and `supabase/staging/01_run_by_hand.sql` (`docs/STAGING.md`).
- The Resend webhook secret `resend_events_secret`.
- Branch protection on `main`.
