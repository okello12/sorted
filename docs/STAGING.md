# Staging

A second Supabase project with the same structure as live and no real data, so the server contract can be tested
without touching anyone's cases.

| | Live | Staging |
|---|---|---|
| Project | `boxrwcuhxmimayaxzywu` (London) | `ujwanxqrefziuxwfzeaj` (London), created 4 October 2026 |
| Plan | Free | Free |
| Data | Real people's cases | None kept: the suite makes two throwaway accounts and deletes them |
| Secrets in Vault | All of them | None (reminders, replies and the assistant stay off) |
| Edge functions | Deployed | Not deployed (the suite does not need them) |

## What is on it

`supabase/staging/00_schema.sql` is the whole structure, taken from the live catalogue after migration 13: tables,
indexes, row level security, grants, functions, triggers and the retention jobs. On 4 October 2026 everything in it
except the parts that delete rows was applied through the Supabase API. The rest is in
`supabase/staging/01_run_by_hand.sql` (six functions, one trigger, the retention jobs), because Supabase's tooling asks
a person to confirm statements that delete. **Still to do, once, by the person running Sorted:**

1. Open the staging project > SQL editor, paste `supabase/staging/01_run_by_hand.sql`, run it.
2. Authentication > Sign In / Providers: switch on **Anonymous sign-ins** (and Email, as on live).
3. In GitHub (okello12/sorted > Settings > Secrets and variables > Actions) add two repository secrets:
   `SORTED_STAGING_URL` = `https://ujwanxqrefziuxwfzeaj.supabase.co` and `SORTED_STAGING_ANON_KEY` = the staging
   project's publishable key (Project settings > API keys). The publishable key is the one the page ships with, so it
   is not secret in the way the service key is; it still goes in a GitHub secret, not in a file or a chat.

Until step 3 is done the `secrets-check` job in CI **fails** with "Staging: NOT READY" on every pull request and push
(since v124's follow-up, remediation A10), and the `staging` job doesn't run. A release is not ready until staging has
run; it is never reported as passed without running.

Migration 15 (`15_delivery_seen_v116.sql`) is fully applied on staging (4 October 2026). Progress on step 1 (the same day, through the Supabase API): `shares_drop_helper` with its trigger, `remove_helper`
and `drop_outcome` are on staging. Supabase's tooling refused the rest without a person's confirmation, so still to run
in the SQL editor from `01_run_by_hand.sql`: `delete_my_account`, `stash_carry`, `claim_carry`, the `revoke` and
`grant` lines, and the retention jobs. Running the whole file again is safe (`create or replace`; `cron.schedule`
replaces a job of the same name).

## The live suite

`tests/live/staging.py`. It refuses to run against the live project. It checks:

- two anonymous accounts are different people; one cannot read, change, delete or plant a case for the other;
- an update only lands when the record's revision is the one that device last saved (the two-device rule from v109);
- step records, errors, totals and admin tables cannot be read by a signed-in person; the numbers and health are admin only;
- a share link opens for anyone with the token and for nobody else, is counted, and stops the moment it is switched off;
- the page can report an error with no account, and unknown sources are ignored;
- company totals take only companies on the fixed list, and Undo drops an outcome;
- deleting an account leaves nothing behind;
- the real page, pointed at staging, saves a real case and brings it back after a reload.

Run it by hand with the two variables set, or from GitHub: Actions > Sorted regression CI > Run workflow. It also runs
after each push to `main` when the secrets exist. From this workspace the staging project is not reachable (the
network allows only package registries and GitHub), so the CI job is the normal way to run it.

## Keeping staging level with live

Each new migration in `supabase/parked/` is applied to staging as well as live, in the same release. If they drift,
drop the staging schema and apply `00_schema.sql` and `01_run_by_hand.sql` again (nothing on staging is worth keeping).
