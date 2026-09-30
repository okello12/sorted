# Sorted pilot

This repository is the code behind **https://sorted-pilot.vercel.app** as deployed on 29 September 2026 (release v27).
The earlier Grok-built prototype is kept under the git tag `grok-prototype`.

## How the site is built

The site is one HTML file. `index.src.html` is the original page; each `buildN.js` applies one release's changes
to it in order, and checks the result against a fingerprint so a wrong step fails the build rather than shipping.
`feat*.js` hold larger blocks of code that some layers insert. `h/*.bin` are the parts of an early hero image.

```
node all.js          # runs build.js, build7.js … build27.js in order
# → public/index.html, sha1 cc73c485a42ae702aebe2564a6cfdb4701485346 for v27
```

Vercel runs the same command (`node all.js`, output directory `public`). `public/art/` holds the illustrations.

## Backend (Supabase, London)

- `supabase/schema_snapshot.sql`: tables, access rules, functions and scheduled jobs, copied from the live
  project on 30 September 2026. Structure only. No rows and no secrets.
- `supabase/functions/`: the three edge functions as deployed: `send-reminders` (runs every 10 minutes),
  `inbound-email` (Resend webhook for forwarded emails) and `email-stop` (one-click unsubscribe).

Keys and addresses live in Supabase Vault and are read by name. The Supabase key in the page is the public
publishable key, which is safe to ship because every table is protected by row level security.

## What the pilot measures

Step records in `pilot_events` hold a step name from a fixed list, IDs and a time, never case text.
`pilot_metrics()` computes Due Return Rate, Miss Recovery Rate and Second Situation Rate from them, and
`pilot_health()` reports whether the reminder clock, reminders, sign-in and inbound email are working.
Both are readable only by pilot admins.
