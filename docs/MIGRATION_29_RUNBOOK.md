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
| Objects outside pg_net that depend on it | 0 | 0 |
| Sorted's callers of pg_net | `sorted_kick_reminders`, `sorted_kick_originals`, `sorted_kick_moves`: each names `net.http_post` in full, runs with an empty `search_path`, and is looked up when it runs (so not dropped with the extension) | the same three |
| Cron jobs that reach pg_net | `sorted-send-reminders` (every 10 minutes) and `sorted-originals-cleanup` (03:27), both through a kick function. No cron command calls `net.*` directly | none of the kick jobs are scheduled on staging |
| Reminders due and unsent in the next hour | 0 | not applicable (no data) |
| Grants on `net.http_post` | execute for PUBLIC, granted by `supabase_admin` | default |
| Supabase's event trigger that grants pg_net access when it is created | `issue_pg_net_access` present | present |

What the drop loses: pg_net's queue, which the script requires to be empty, and its log of past responses
(`net._http_response`, 37 rows on live, which pg_net prunes by itself). Sorted reads neither. Reminders are claimed in
`public.reminders` before sending, so a reminder is never lost with pg_net's log.

## How the script protects itself

- One transaction, with `lock_timeout` 5 s and `statement_timeout` 60 s. Postgres runs extension DDL transactionally,
  so any failed check rolls everything back and the extension stays where it was.
- It refuses to run if: pg_net is missing, already moved or somewhere unexpected; the version to be created differs
  from the installed one; anything is queued; any object outside pg_net depends on it; or a kick function is missing.
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
