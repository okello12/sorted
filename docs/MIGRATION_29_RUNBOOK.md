# Migration 29 runbook: pg_net out of the public schema

Written 11 October 2026, in answer to the release assurance dossier (section 5). The migration is
`supabase/parked/29_pg_net_schema_v158.sql`. It has **not** been applied anywhere. Its status is BLOCKED until steps 1 to
3 below are signed off.

## Why it matters, and how much

Supabase's security advisor flags `pg_net` installed in `public` (WARN, lint 0014). pg_net's working objects already
live in their own `net` schema. Only the extension's registration sits in `public`. Moving it is housekeeping that
clears the advisory. It doesn't close a known hole: nothing in `public` is reachable through it that isn't reachable
today. A wider release doesn't depend on it. A tidy advisor list does.

## Preflight evidence (read-only, 11 October 2026, both projects)

| Check | Live (`boxrwcuhxmimayaxzywu`) | Staging (`ujwanxqrefziuxwfzeaj`) |
|---|---|---|
| pg_net installed version and schema | 0.20.4 in `public` | 0.20.4 in `public` |
| Version `create extension` would install | 0.20.4 (the same) | 0.20.4 (the same) |
| Requests waiting in `net.http_request_queue` | 0 | 0 |
| Objects outside pg_net that depend on it (full recursive walk of `pg_depend`, no class excluded; see below) | 0 | 0 |
| Sorted's callers of pg_net | `sorted_kick_reminders`, `sorted_kick_originals`, `sorted_kick_moves`: each names `net.http_post` in full, runs with an empty `search_path`, and is looked up when it runs (so not dropped with the extension) | the same three |
| Cron jobs that reach pg_net | `sorted-send-reminders` (every 10 minutes) and `sorted-originals-cleanup` (03:27), both through a kick function. No cron command calls `net.*` directly | none of the kick jobs are scheduled on staging |
| Reminders due and unsent in the next hour | 0 | not applicable (no data) |
| Grants on `net.http_post` | execute for PUBLIC, granted by `supabase_admin` | default |
| Supabase's event trigger that grants pg_net access when it is created | `issue_pg_net_access` present | present |

What the drop loses: pg_net's queue, which the script requires to be empty, and its log of past responses
(`net._http_response`, 37 rows on live, which pg_net prunes by itself). Sorted reads neither. Reminders are claimed in
`public.reminders` before sending, so a reminder is never lost with pg_net's log.

## Final preflight for the staging approval (11 October 2026, after Baldwin's conditions)

Baldwin approved a staging-only rehearsal on four conditions. No production change, no deployment and no automatic
promotion. Each condition, as checked:

1. **The staging cases are disposable.**
   - Staging holds 3 case records. This page wrongly said "no data"; corrected.
   - Checked by metadata only, never content. Each belongs to an anonymous account with no email address, created on
     9 October between 21:23 and 21:32 UTC, while the staging suite was being set up. They are leftovers from runs
     that didn't reach their clean-up.
   - Staging has 4 users, all anonymous. It has never had an email account.
   - The migration doesn't touch `tasks`.
   - **Met.**
2. **A complete dependency check.**
   - The first preflight left four kinds of object out of its count. It is replaced by a recursive walk of every
     object that depends on pg_net, directly or through others, with nothing excluded.
   - Each object that isn't a member of the extension is placed by its schema. Anything outside `net` or `pg_toast`,
     or of a kind the check can't place, refuses the migration.
   - Result, identical on staging and live: 41 objects. 28 are members. 12 are pg_net's own parts: 4 in `pg_toast`
     (two storage tables and their indexes) and 8 in `net` (an index, two composite types and two of their columns,
     two column defaults and a check). **None** are outside.
   - The script now runs this walk.
   - Rehearsed locally, it refuses an outside view, an outside function taking a pg_net type, an outside table with a
     pg_net column, and an outside foreign key to pg_net's queue. It still passes a clean run.
   - `DROP EXTENSION` without CASCADE would also refuse in each of those cases. The walk says why before anything is
     tried.
   - **Met.**
3. **Staging can be rebuilt.**
   - **Partly met.** No permanent test data is needed: the suite makes its own accounts each run and deletes them.
   - The files to rebuild staging exist, but a rebuild from them has never been run end to end:
     `supabase/staging/00_schema.sql` (structure as of migration 13), `01_run_by_hand.sql`, `02_parity_v149.sql`,
     then the parked migrations applied to staging since (15 to 21, 23 to 28 and 30).
   - What is proven is narrower:
     - the change itself can be undone (below);
     - a fingerprint of staging taken before the change can show that nothing but pg_net's registration moved.
   - Fingerprint before (11 October 2026, read-only):

     | Part | Count | Hash |
     |---|---|---|
     | Functions in `public` and `storage` (body, grants, security and settings) | 64 | `032e94f108a8fd3f7b8aaa9d6551dbc1` |
     | Tables and views (columns, grants, row level security) | 30 | `4b28d2becc9dc774aed3c7c1577e4cf7` |
     | Policies | 23 | `75e58ef7fe48c81d8ebd665a9cadc804` |
     | Triggers | 14 | `6cf0874c08f39cdc10dabdbb747e0474` |
     | Cron jobs | 2 | `81d22c26dd72d3b6ae2c9aa2f649167f` |
     | Extensions | 7 | pg_net@0.20.4 in public; the others unchanged |

   - Why it matters: staging is a required check on every pull request. If staging broke and couldn't be repaired,
     releases would stop until it was. That makes a rebuild worth proving, but this change has a two-line undo.
4. **Run on staging, then verify.** Waiting on Baldwin's decision about condition 3.

## How the script protects itself

- One transaction, with `lock_timeout` 5 s and `statement_timeout` 60 s. Postgres runs extension DDL transactionally,
  so any failed check rolls everything back and the extension stays where it was.
- It refuses to run if: pg_net is missing, already moved or somewhere unexpected; the version to be created differs
  from the installed one; anything is queued; the full dependency walk finds any object outside `net` or `pg_toast`,
  or one it can't place; or a kick function is missing.
- After the move, it checks: pg_net is in `extensions` at the same version, `net.http_post` and the queue exist,
  `postgres` can call `net.http_post`, and all three kick functions are present. A failure rolls back.

## Rehearsal done here (11 October 2026)

On a local Postgres 16 with a stand-in extension of the same shape. The stand-in is not pg_net. It proves the
script's guards and rollback, not pg_net's internals.

| Case | Result |
|---|---|
| A request still queued | Refused at preflight; pg_net still in `public` |
| A view outside pg_net depending on its queue | Refused at preflight |
| Clean run | Preflight and postcheck passed, committed; pg_net in `extensions`, version 0.20.4 |
| The kick function after the move | Queued its request through `net.http_post` |
| A second run | Refused: "already in extensions, nothing to do" |

## The steps, in order

1. **Approve the staging rehearsal** (Baldwin). Staging holds no data and no secrets. Its "restore" is a rebuild from
   `supabase/staging/00_schema.sql`, so no snapshot is needed.
2. **Staging rehearsal** (engineering, after step 1):
   1. Rerun the preflight queries above.
   2. Apply the script.
   3. Check the advisor no longer lists pg_net.
   4. Call `net.http_post` once against staging's own `send-reminders` URL and see a response row appear.
   5. Rerun the staging suite (CI job `staging`).
   6. Write the results here.
   If it fails: the transaction has rolled back. If staging is left odd, rebuild it from `00_schema.sql`.
3. **Production gate** (Baldwin). Proceed only after:
   - the staging rehearsal has passed;
   - the backup decision in `docs/RECOVERY.md` is made;
   - a window is chosen: a quiet hour, at a minute ending in 3 to 7, so it isn't at a reminder kick.
   Then:
   1. Rerun the preflight, which must show 0 queued and 0 dependents.
   2. Apply the script through the SQL editor (Run) or `apply_migration`.
   3. Within 10 minutes, check `sorted-send-reminders` ran and `net._http_response` has a new row with status 200
      (the status code only, never a body).
   4. Watch reminder delivery in `pilot_health()` for a day.
4. **Rollback**:
   - If the script fails, it has already rolled back.
   - If something goes wrong after it commits, run `drop extension pg_net; create extension pg_net with schema
     public;` in one transaction. The same preflight and postcheck apply, with the schemas swapped. Nothing else
     depends on the extension, so a backup isn't needed to undo it.
