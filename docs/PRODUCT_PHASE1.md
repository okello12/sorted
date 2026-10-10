# Something I own isn’t working: Phase 1 of the product-photo specification

Written 10 October 2026, before any code. The full specification (product photo, official troubleshooting, resolution
route) is Baldwin’s product brief of 10 October. This file is the build plan for its first phase and the rules the
later phases inherit. When code and this file disagree, fix one of them in the same release.

## What Phase 1 delivers

A person whose own thing has stopped working can start a repair case from a photo of its label, or by typing what it
is. Sorted reads the label on the phone, shows what it read as candidates, and records nothing as a fact until the
person says it is right. Then, on the same repair case:

1. the deterministic safety decision, before anything else is offered;
2. the product: brand, model, kind of product, serial number (masked), each with its status and where it came from;
3. purchase details (shop, date) from the person or a receipt photo, confirmed the same way;
4. a hand-checked link to the maker’s UK support page, saying plainly that Sorted has **found the page, not checked
   its instructions**;
5. “Best next step”, worked out from confirmed facts only, with its reason and the other routes beneath;
6. “Have these ready” and a prepared phone script and email draft, through the existing contact engine.

Not in Phase 1: fetching manuals, reading PDFs, matching symptoms to official topics, step-by-step troubleshooting,
exact-model or region matching against a source, a server retrieval function. The architecture below leaves room for
them; nothing in Phase 1 pretends they exist.

## Architecture

**Modules, not another behavioural patch.** The product logic lives in plain files under `src/product/`:

| File | Holds | Phase |
| --- | --- | --- |
| `product.js` | The product record inside a case: fields, statuses (candidate, confirmed, corrected, unknown), sources (user, label_photo, receipt), masking, history of every value | 1 |
| `product-intake.js` | Reading candidates from on-device OCR text of a label or receipt; never confirms anything | 1 |
| `product-safety.js` | `decide()` → a SafetyDecision with `rule_version`; deterministic rules only | 1 |
| `manufacturers.js` | The controlled registry: canonical name, aliases, regions, official domains, hand-checked UK support and contact pages, `CHECKED` date | 1 |
| `resolution-route.js` | `route()` → recommended route, reason, alternatives, source basis, from confirmed facts only | 1 |
| `product-guidance.js`, `troubleshooting-session.js`, `src/services/official-guidance.js` | Retrieval results, sessions and steps | 2 and later |

They are pure: no DOM, no `S`, no saving, no network. Node tests (`tests/product/*.mjs`) run the same bytes the page
runs. `tools/inline_modules.js`, the last step of `all.js`, puts them into the page at one marker inserted by
build161, in a fixed order, and checks each file’s sha1 and the final page sha1 against `src/manifest.json`. So the
byte-for-byte release rule still holds: a module change is a manifest change, reviewed and pinned like a layer.
The legacy layers stay as they are and keep running first; the page code that renders the product cards (thin glue)
is in build161 and later layers, and calls the modules through one object, `Product`.

**One case, no repair universe.** The product is `t.prod` on the existing repair case (`t.mode` "fix"). It is case
content (`tasks.data`): saved, merged, retained, exported and deleted with the case, under the same rules and the
same promise that nobody running Sorted reads it. It survives a change of kind. Flow of truth is one way:
confirmed values in `t.prod` are written into the fields the repair engine already reads (`t.fix.item`,
`t.fix.model`, `t.fix.seller`, `t.fix.age`) by one function, `prodApply(t)`, on every save, so `callDefaults()`,
`haveReady()`, `advice()`, the ledger, the pack and Home keep reading what they read today. Nothing writes the other
way. The fact ledger (`lgSync`) gains rows of type `product` and `purchase` from `t.prod`: a candidate is `read` by
`photo`, a confirmed value is `confirmed` by `you`, a corrected one supersedes the read row, which stays.

Promises, your own steps, whose move, attention, reminders, corrections, chases and finishing are the normal core.
The product flow creates no promise and no step on its own. “Prepare contact” sets who you are contacting (one tap,
recorded like any party) and opens the existing message form; what they then say goes through the ordinary reader.

## The journey in Phase 1

1. The repair door (“What needs repairing?”) leads with **Something I own isn’t working**: Take a photo of the label,
   Choose a photo, or Tell Sorted instead (the existing form, unchanged). A photo of the product itself, without a
   readable label, gives at most a brand candidate and asks for the label or the model; it never yields a model.
2. **Check what Sorted read**: brand, model, serial (••••6789), and the kind of product to choose. Looks right, or
   Change (each field editable). Nothing is a fact until then. Type the model, Show me where to look, Continue
   without it are always there.
3. **What’s happening?** in the person’s words, kept as said, plus the existing safety question.
4. The case starts. The safety decision is made from the product class and the words before anything else shows.
5. On the case: the product card, purchase details (type them or photograph the receipt; confirm), the support card
   and Best next step with Have these ready and Prepare contact.

## Migrations

| Migration | What | Where |
| --- | --- | --- |
| `30_product_steps_v163.sql` | `pilot_events` step names: `product_flow_started`, `product_candidate_found`, `product_read_failed`, `product_confirmed`, `purchase_confirmed`, `safety_stopped`, `official_support_shown`, `resolution_route_shown`, `contact_prepared`. Props are codes and counts only (source, kind, route, how many rules matched) | Staging first, then live, before v163 (the release that records them; v161 and v162 hold them back with `PROD_TRACK161=false`) |

No new table. The product, the safety decision and purchase details are case content, so they already have row
level security, retention, deletion, export and the two-device merge. A separate table would need all of those again
and would be a second source of truth. Phase 2’s retrieval service will need its own migration (a cache of retrieval
records with source URL, title, model, region, retrieved time and an unavailable flag; no case content), designed then.

## Privacy

- Labels and receipts are read on the phone by the same Tesseract build as notices. No photo leaves the phone to
  identify a product; the photo itself is not stored unless the person keeps it as a document, as today.
- The raw OCR text is not saved in the case; only the candidate values are, and only once the person continues.
- The full serial number is case content, kept in `t.prod` only. Everywhere else it is masked (••••6789): the case
  page (Show and Copy on demand), Home, Cases, the ledger, the history, the helper’s shared link, the summary, the
  adviser pack, the assistant’s context (`aiContext`), error reports (`errText`), usage records, notifications and
  URLs. The full value goes out only when the person chooses: Show, Copy, or “Add the full serial number to the
  message” in the prepared contact. The adviser pack and “Download my cases” show it masked too.
- Sorted’s reference reader can take a serial typed in the person’s words for a case reference (found by test 129).
  Once the product holds that serial, the reading is dropped from the reference, the title and the ledger.
- A serial candidate the person rejects or corrects is kept masked in the ledger, never in full.
- Usage records carry codes only: never a brand, model, serial, retailer, date or the person’s words.
- The privacy notice and Help gain one sentence each: labels and receipts are read on the phone, and serial numbers are
  shown masked.
- The existing number masking (cards, bank, NI) may hide a long all-digit serial before Sorted sees it. That is the
  safe failure; the person can type it.

## Safety boundaries

`Product.safety.decide({category, words, answers})` is deterministic, versioned (`RULE_VERSION`) and runs before
any support link or route. Results, in order of strength: `STOP_USE`, `PROFESSIONAL_ONLY`,
`OFFICIAL_INFORMATION_ONLY`, `SAFE_EXTERNAL_CHECKS`. False positives are acceptable.

- **STOP_USE**: sparking, smoke, burning or a burning smell, gas or fumes, a carbon monoxide alarm, a swollen or
  damaged battery, exposed or damaged wiring or mains cable, scorch marks, abnormal heat, water near the plug,
  socket or electrics. Reuses `DANGER`, `DANGER_MORE`, `DANGER_HOT`, `DANGER_WET`, `DANGER_URGENT` and adds the
  product words. Shows the existing safety screen; no support link is presented as a fix, only the maker’s contact.
- **PROFESSIONAL_ONLY**: gas appliances and boilers, anything needing internal mains or high-voltage access,
  microwaves beyond the outside, a car’s brakes, steering, airbags, fuel or high-voltage system, anything under a car.
- **OFFICIAL_INFORMATION_ONLY**: cars otherwise, fridges and freezers, unknown kinds of product.
- **SAFE_EXTERNAL_CHECKS**: mains appliances in the Phase 1 categories (washing machines, dishwashers, tumble
  dryers, vacuum cleaners, printers, routers, coffee machines) with no danger words. In Phase 1 this still offers no
  steps: it only allows Phase 2 to offer manufacturer-approved external checks later.
- Negations are honoured (“no burning smell”) with the existing `DANGER_NO` and `DANGER_NEG`.
- The decision is stored on the case with its rules, version and time, and re-made when the words change.
- A product case never shows Sorted’s own washing-machine checks (`CHECKS`), because they are not the maker’s.
  The manual repair path keeps them unchanged; whether to retire them is Baldwin’s decision (below).

## Honesty rules for the copy

- “Sorted found Bosch’s UK support page. It hasn’t read Bosch’s instructions for your problem.” Never “checked”,
  “verified the instructions” or “Bosch says”.
- A route reason uses confirmed facts only and names its source; no legal conclusion. Unknown purchase details are
  said to be unknown.
- A brand with no registry entry gets no link: “Sorted doesn’t have a checked support page for Acme yet.”

## Tests (permanent, before release)

| File | Covers |
| --- | --- |
| `tests/product/*.mjs` (run by `126_product_units.py`) | intake: clear label, blurred or empty read, partial label, wrong OCR model, brand only, no model, two model numbers, serial with S/N, SN, Serial No; never a model from a product photo; masking; statuses and history; registry lookups by alias; every safety word, negation, class rule and rule version; routes for retailer, manufacturer, repairer, unknown purchase, no registry entry, safety overrides |
| `127_product_journey.py` | the door through the page: label photo (real Tesseract image), candidates, Looks right, Change keeping the original, manual entry, Continue without it, receipt confirm and correct, wrong OCR date, no receipt, support card wording, Best next step, Have these ready, Prepare contact into the message form, refresh mid-flow, offline (no link fetched, nothing pretended) |
| `128_product_safety.py` | sparking, burning smell, smoke, gas, swollen battery, exposed cable, water near electrics, overheating, brake problem, boiler problem: each bypasses the support card and route; the decision and version saved |
| `129_product_privacy.py` | the serial masked on every surface (Home, Cases, case, ledger, history, share card, summary, pack, assistant context, error report, usage records, calendar file, URLs, reminder rows) and in full only after Show, Copy or the deliberate include |
| `130_product_core.py` | contact creates no promise; a reply proposes one; confirming it is the normal core (whose move, attention, Home agrees with the case, share and export agree, correction, reschedule, missed promise) |
| `tests/live/staging.py` | the product step names accepted by staging; a walk that saves a product case against staging and reads back a masked serial in the ledger |

The whole regression suite runs after each stage.

## Release gates for this feature

1. Each stage: layers built with `EXPECT` pinned, the manifest pinned, `tools/csp_hashes.js` run, the complete
   `sh tests/run.sh` green.
2. Migration 30 applied to staging, then live, before the release that records the new step names.
3. One pull request for Phase 1, kept open (not merged) until every stage is in, with regression, webkit, firefox
   and staging green, and tests 126 to 130 green. Merging to `main` is the production deploy, so it waits for that.
4. Every manufacturer and retailer link opened and read on the `CHECKED` date; recheck within 90 days (gate G8).
5. After merge, `live` green.

## Stages

| Stage | Contents | Behaviour change |
| --- | --- | --- |
| 0 | This plan; the module folder, manifest, `tools/inline_modules.js`; the pure modules with unit tests | None on the page |
| 1 | build161: the door, label read and confirmation, manual entry, `t.prod`, `prodSync161` (one way into `t.fix`), ledger rows, history, masked serial on every surface, safety decision | The new path |
| 2 | build162: purchase details and receipt, registry support card, Best next step, Have these ready, Prepare contact | The rest of the path |
| 3 | Migration 30, build163 switches the step names on, the staging walk, docs | Usage records |

## Decisions for Baldwin

1. Sorted’s own washing-machine checks in the manual repair path are not the maker’s. Phase 1 hides them on product
   cases only. Retire them everywhere, label them as Sorted’s general checks, or keep them?
2. The ways in stay six; the new path is the first choice inside the repair door. A seventh way in changes Home.
3. Which manufacturers first. Phase 1 starts with makers of the seven categories that have UK support pages.
