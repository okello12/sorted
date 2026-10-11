# Backups and recovery: what exists today

Written 4 October 2026. Read this before promising anyone that their cases are safe.

## What exists

- The database is one Supabase project (`sorted-pilot`, London) on the **free plan**. The free plan has **no automatic
  backups** and no point-in-time recovery. If the database were lost or corrupted, the cases in it would be gone.
- Every phone keeps its own copy of its owner's cases in the browser (`localStorage`). That copy is written on every
  change and read when the server can't be reached. It is a copy for one person, on one device, not a backup of the
  service: a cleared browser or a lost phone loses it, and nobody else can read it.
- Deleting a case is server-side, with a 2-minute Undo on Home (since v112). After that it is gone. Deleting an
  account is immediate. (Corrected 11 October 2026: this line used to say there was no undo.)
- The code and the database structure are in git (`supabase/schema_snapshot.sql` and `supabase/parked/`), so an empty
  service can be rebuilt. The data cannot.

## Recovery point and time, honestly

- Recovery point: none for the service. A person's own phone holds their cases as of their last change.
- Recovery time: a rebuild of an empty service from git is about an hour. There is no way to restore cases.

## What a paid service needs

1. The Supabase Pro plan (daily backups, 7 days kept) and, before any launch, the point-in-time recovery add-on.
2. A restore demonstrated once into a separate project, with the time it took written here.
3. A weekly export of `tasks` to encrypted storage the operator controls, so the service does not depend on one supplier
   for both the data and its backup. The export holds case content, so it must be encrypted at rest and listed in the
   privacy notice as a copy kept for recovery.
4. An incident note: who is told, where it is written up, and what people are told if cases are lost.

Until 1 and 2 are done, release gate G5 in the assurance review is not met.

## The decision Baldwin needs to make (11 October 2026, for the release assurance dossier)

Wider release is blocked until one of these is in place **and a restore has been shown to work**. They aren't
exclusive. Option A plus a monthly run of Option B is the strongest.

| | A. Supabase Pro plan | B. Encrypted copy you hold |
|---|---|---|
| What | Daily backups kept 7 days, restorable from the dashboard. Point-in-time recovery is a paid add-on | A nightly `pg_dump` of the live database, encrypted with a key only you hold, kept outside Supabase |
| Cost | The Pro plan's monthly fee (check Supabase's pricing page) | Nothing extra; a GitHub Actions job |
| Protects against | Database failure or corruption | That, plus losing access to the Supabase account or project |
| Recovery point | Up to 24 hours (minutes with point-in-time recovery) | Up to 24 hours |
| What you must do | Upgrade the project in the dashboard (a payment Sorted's engineer can't make) | Add the database connection string as a GitHub secret, and make an `age` key pair, keeping the private half offline. Neither may be pasted into chat |
| Privacy | Inside Supabase, already in the notice | A new copy of case content, encrypted. The privacy notice must say it exists, where it is and how long it is kept |

## Restore drill (the evidence the dossier asks for)

Run once before a wider release, then every quarter. Counts only: nobody reads a case.

1. Restore into a **new, separate project** (Option A: dashboard restore into a new project; Option B: decrypt and
   load into a fresh Supabase project or a local Postgres). Never into live, and never into staging, whose permissions
   CI checks.
2. Compare row counts per table, and the newest `updated_at`, with live at the time of the backup.
3. Check the newest case's `data->>'rev'` matches, by count of matching ids. Don't open its content.
4. Write here: the date, which backup, how long the restore took (the recovery time) and how old the backup was
   (the recovery point).
5. Delete the restored project.

Until a drill is written here, release gate G5 is not met.
