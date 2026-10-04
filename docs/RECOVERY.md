# Backups and recovery: what exists today

Written 4 October 2026. Read this before promising anyone that their cases are safe.

## What exists

- The database is one Supabase project (`sorted-pilot`, London) on the **free plan**. The free plan has **no automatic
  backups** and no point-in-time recovery. If the database were lost or corrupted, the cases in it would be gone.
- Every phone keeps its own copy of its owner's cases in the browser (`localStorage`). That copy is written on every
  change and read when the server can't be reached. It is a copy for one person, on one device, not a backup of the
  service: a cleared browser or a lost phone loses it, and nobody else can read it.
- Deleting a case or an account is immediate and server-side, by design. There is no undo and the privacy notice says so.
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
