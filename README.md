# Sorted pilot

This repository is the code behind **https://sorted-pilot.vercel.app** (release v69, 2 October 2026).
Start with `CLAUDE.md` (how it's built, tested and deployed) and `docs/LATER.md` (parked work and why).
The earlier Grok-built prototype is kept on the branch `grok-prototype`.

## How the site is built

The site is one HTML file. `index.src.html` is the original page; each `buildN.js` applies one release's changes
to it in order, and checks the result against a fingerprint so a wrong step fails the build rather than shipping.
`feat*.js` hold larger blocks of code that some layers insert. `h/*.bin` are the parts of an early hero image.

```
node all.js          # runs build.js, build7.js … build52.js in order
# → public/index.html, sha1 c41e1c1c9caf74b0471dbe46f997658109dca348 for v123
sh tests/run.sh      # builds, then runs every walkthrough test
```

Vercel runs the same command (`node all.js`, output directory `public`) on every push to `main`. `public/art/` holds the illustrations and `public/fonts/` the lettering (Atkinson Hyperlegible, SIL Open Font License).

## Backend (Supabase, London)

- `supabase/schema_snapshot.sql`: tables, access rules, functions and scheduled jobs, copied from the live
  project on 1 October 2026, with grants, constraints, indexes and policies. Structure only. No rows and no secrets.
- `supabase/functions/`: the three edge functions as deployed: `send-reminders` (runs every 10 minutes),
  `inbound-email` (Resend webhook for forwarded emails, switched off since v28; forwarding addresses removed 2 October 2026) and `email-stop` (one-click unsubscribe).

`supabase/parked/` holds database changes that are written but not applied, including the backend
half of the v37 audit (`03_audit_fixes_v37.sql`), which is waiting for approval.

Keys and addresses live in Supabase Vault and are read by name. The Supabase key in the page is the public
publishable key, which is safe to ship because every table is protected by row level security.

## What the pilot measures

Step records in `pilot_events` hold a step name from a fixed list, IDs and a time, never case text.
`pilot_metrics()` computes Due Return Rate, Miss Recovery Rate and Second Situation Rate from them, and
`pilot_health()` reports whether the reminder clock, reminders, sign-in and inbound email are working.
Both are readable only by pilot admins.
