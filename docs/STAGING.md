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
a person to confirm statements that delete. All of it is now done (9 October 2026): `01_run_by_hand.sql`, anonymous
sign-ins switched on, the GitHub secrets added, and `02_parity_v149.sql`, which the first full run asked for (staging was
missing `delete_my_account` and `stash_carry`, and anonymous callers could reach `drop_outcome`, `remove_helper` and
`shares_drop_helper`; live was right throughout).

The `staging` job is required on every pull request. A `secrets-check` job fails when neither the secrets nor
`tests/live/staging_target.json` (the staging URL and its publishable key, public by design) are there, so it can never
pass without running. `staging.py` checks the URL and key it is given and falls back to that file when a secret is
malformed; it never prints either.

## The live suite

`tests/live/staging.py`. It refuses to run against the live project. It checks:

- two anonymous accounts are different people; one cannot read, change, delete or plant a case for the other;
- an update only lands when the record's revision is the one that device last saved (the two-device rule from v109);
- step records, errors, totals and admin tables cannot be read by a signed-in person; the numbers and health are admin only;
- a share link opens for anyone with the token and for nobody else, is counted, and stops the moment it is switched off;
- the page can report an error with no account, and unknown sources are ignored;
- company totals take only companies on the fixed list, and Undo drops an outcome;
- every function that is service-only or signed-in-only refuses the wrong caller, so staging's grants match live's;
- a second person can't use the first person's reply address, helper invite, push address, reminders, kept documents
  or a made-up carry token, and a case far over the size cap is refused;
- deleting an account leaves nothing behind;
- the real page, pointed at staging, saves a real case and brings it back after a reload, then deletes its guest.

Run it by hand with the two variables set, or from GitHub: Actions > Sorted regression CI > Run workflow. It runs on every pull request
and after each push to `main`. From this workspace the staging project is not reachable (the
network allows only package registries and GitHub), so the CI job is the normal way to run it.

## Keeping staging level with live

Each new migration in `supabase/parked/` is applied to staging as well as live, in the same release. If they drift,
drop the staging schema and apply `00_schema.sql` and `01_run_by_hand.sql` again (nothing on staging is worth keeping).
