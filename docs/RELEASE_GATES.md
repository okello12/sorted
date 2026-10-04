# Release gates and where each one stands

From the commercial assurance review of 4 October 2026. Update the status column when something changes. A gate is
met only with evidence that can be pointed at: a test file, a document, a dated check.

| Gate | Condition | Status on 4 Oct 2026 | Evidence or what is missing |
| --- | --- | --- | --- |
| G1 | Zero P0, zero open P1 | Not met | OPS-01, OPS-02 closed in v109 (test 66); OPS-03 closed in code (staging project and live suite, `docs/STAGING.md`) but the suite has not run yet. Open: LEGAL-01 (terms written, not yet checked by a lawyer), A11Y-01 (no real-phone check), COPY-01 (the domain is still sorted-pilot) |
| G2 | Page errors reported and reviewed weekly; under 1 per 100 sessions | Partly | Reporting exists since v109 (`report_page_error`, the Errors row on the numbers page). No readings yet |
| G3 | Terms, privacy notice and complaints route published and linked from every page | Partly | All three on the data page and the footer since v109. The terms say "not yet checked by a lawyer" |
| G4 | The live suite passes on staging on every release | Partly | Staging project `ujwanxqrefziuxwfzeaj` with the live structure; `tests/live/staging.py`; CI job `staging` after each push to main. Three steps for the person running Sorted remain (`docs/STAGING.md`): run `01_run_by_hand.sql`, switch on anonymous sign-in, add the two GitHub secrets. No green run yet |
| G5 | A restore demonstrated once, recovery point written down | Not met | Free plan, no backups. See `docs/RECOVERY.md` |
| G6 | Two-device conflict merged or warned, with a test | Met | v109 `saveConflict()` and `mergeInto()`; test 66 |
| G7 | The phone checklist passed on one iPhone and one Android, dated | Not met | `docs/PHONE_CHECK.md` not yet run |
| G8 | Every official link rechecked within 90 days of release | Met | `MV_CHECKED` 4 Oct 2026; `RT_CHECKED`, `XR_CHECKED`, `PB_CHECKED`, `UK_BH_CHECKED` in the page |
| G9 | Due Return Rate from at least 50 matured promises by people who are not the founder | Not met | Measured by `pilot_metrics()`; no reading yet |

Stages, from the review: founder testing is open; closed external testing with about 50 people is open once G2 has
readings; paid beta needs G1 to G6; public beta G1 to G8; launch G1 to G9.
