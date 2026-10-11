# Phase 1.5 audit: Something I own isn't working

10 October 2026, on v163 (live) and the fixes in v164. It was asked for before Phase 2: automated troubleshooting doesn't
start until Baldwin has reviewed these findings. The plan is in `docs/PRODUCT_PHASE1.md`.

Each area below has what was tested, what was found, what changed, and what is still open. The evidence is the test files:
`126_product_units.py` (with `tests/product/safety_corpus.mjs`), `127` to `130`, and the new
`131_phase15_audit.py`.

## Decisions applied in v164 (Baldwin, 10 October 2026)

1. **Sorted no longer writes physical repair instructions.**
   - The washing-machine "Try these safe checks" step is retired for every repair, not only product cases.
   - The repair questions, every safety warning and existing case history stay. A case that already answered checks
     keeps those answers. They still appear as "What you tried" in its messages and pack.
   - A case saved at the old checks step now opens at the decision, so no case loses its place.
   - The plan chip "Try a safe check" is now "Look up the maker's own guidance". The landing slide no longer mentions checks.
   - Impact was checked without reading anyone's case. Nothing else in the page reads the checks step; test 107 moved
     to product details.
2. **The six ways in stay.** Navigation is not touched.
3. **Ten more makers.**
   - Added: Samsung, Hotpoint, Indesit, Hoover, AEG, Electrolux, Philips, HP, Epson and Canon.
   - Two separate checks fetched each link on 10 October 2026, and each one is the maker's own UK page.
   - Whirlpool is left out: its UK repair site names no owner.
   - For Indesit, only indesit.co.uk is linked. Its repair-booking site is a separate domain that names no owner.

## Findings

### Real-phone OCR

- **Tested:** test 131 renders a rating label and damages it the way a phone camera does, then reads each version with
  the real Tesseract: tilted, sheared, JPEG at quality 30, low resolution, blurred, glare, grey on silver, noise, and a
  full-size 4032 px photo. The damage is made in the browser, so the test needs no image library. It runs the same on
  every machine.
- **Result:** the model was read exactly from the clean, sheared, compressed, glare, grey and full-size photos.
- **Finding:** four of the ten photos (tilted, low resolution, blurred and noisy) produced a *wrong* model. Examples:
  WGG244ZC6P, WGG244ZCGBI0L and WGG2442CGBO1 for WGG244ZCGB. A wrong model is only a candidate, and the person must
  accept it before Start.
- **Fix:** the review used to ask for a check only when the model had no label beside it. Now every model read from a
  photo, single or a choice of several, says "Check it letter by letter against the label. A photo can turn a Z into a
  2." A variant after a slash (`/01`) is removed when the slash is read.
- **Earlier finding (fixed in v161):** OCR reads "S/N" as "SIN". Both are recognised.
- **Rule for Phase 2:** never treat a model as exact for guidance unless the person confirmed it or typed it. A confirmed
  model can still be mistyped, so exact-model guidance should show the model it matched, for the person to compare.
- **Still open:** these photos are simulated. A real iPhone and a real Android phone are still needed. That is the new
  section in `docs/PHONE_CHECK.md`.

### The first real-phone try (Baldwin's iPhone, 10 October 2026, fixed in v165)

- **What happened:** Baldwin photographed the appliance itself, not its rating label. Sorted said "Sorted couldn’t read
  that photo", and the line under it repeated the message. It felt like a failed scan, which the specification says it
  must not.
- **Why:** Sorted reads words on the phone. It doesn't recognise a machine from its shape, and it shouldn't: that would
  mean sending the photo to a remote model, which the privacy design rules out.
- **Fix:** a photo with no make, model or serial now says "Now photograph the label". It explains that Sorted reads the
  words on a label, not the machine. It also:
  - says where the label usually is for each kind of thing;
  - lets the person say what it is;
  - offers "Photograph the label", "Choose a photo", typing, or "Continue without the label".
  - The message is said once.

### A walk through a vacuum cleaner case (Baldwin's iPhone, 10 October 2026, fixed in v166)

- **Repeated question:** the case asked again what it is and what's happening, with washing-machine chips. Fixed: a
  product case's first step is only the safety question, with an optional detail.
- **Dead end:** started without the label, the product said "Not known yet" three times with no way forward. Fixed: the
  case offers "Photograph the label". The read is candidates to accept, change or turn down.
- **Layout:** the details were an unstyled list. They are rows now.
- **Title:** "My vacuum cleaner: It's not working" keeps the capital: those are the person's own words, kept as typed.

### A heating case (Baldwin's iPhone, 10 October 2026, fixed in v167)

- **What happened:** an ordinary repair case named "Heating or hot water" showed "What is it, and what's it doing?"
  with "What is it?" empty, and asked the general safety question instead of the gas one.
- **Why:** every way of starting a repair names the thing. On the case, "Something else" was already the choice shown,
  and tapping it again set the name to empty.
- **Fix:** "Something else" keeps the case's own name. A repair saved with no name is named again from the person's
  words. A name the person types still wins (test 133).
- **Server check, 11 October 2026 (counts only):** no page errors reported since 9 October.

### The external audit (11 October 2026, fixed in v168)

An independent audit of the repository, CI and backend (not a phone session) asked for four things before Phase 2.

- **OCR wrong models:**
  - Every model read from a photo is now checked. The check uses the reader's confidence in the whole photo, plus the
    model's own shape: lower-case letters inside it, or an O, I or L beside a 0 or 1.
  - A doubtful model says "Sorted isn't sure it read the model correctly" and puts Retake photo first.
  - Under 60 the photo is too unclear, and Sorted offers no model at all.
  - In the ten audit photos, all four wrong models are now doubted, and the noisiest photo offers none. One correct read
    (sheared) is doubted too, which is a warning, not a refusal (test 131).
- **Safety wording (rules `ps-3`):**
  - A negation never clears danger that is past, paused or only hedged ("not sparking any more but it did earlier",
    "I don't think it's smoking, but it smells strange").
  - New rules: electrical and hot-plastic smells, crackling or buzzing sockets and switches, discoloured sockets, cut
    cables, hedged gas and rotten eggs, carbon monoxide signs and symptoms, tyres and dashboard safety lights, and a
    consumer unit that keeps tripping.
  - Ordinary repairs with no product now go through the same rules as well as the page's own danger words.
  - The corpus is 114 descriptions (`tests/product/safety_corpus.mjs`). Test 134 runs them through the page.
- **Security advisories:** reviewed in `docs/SECURITY_ADVISORIES.md`. Every flagged function is intended. `pg_net` still
  needs Baldwin's one Run (migration 29).
- **Still Baldwin's:** backups and a tested restore, the DPIA and legal review, and the real-phone VoiceOver and
  TalkBack journeys. The audit's verdict stands: conditionally ready for the closed pilot, not yet for a wider release.

### Unknown models

- **Tested:** a photo of the product with no label gives at most the make. It never gives a model.
- **Tested:** two models on a label are offered as a choice. Typing works with no photo, and "Continue without it"
  keeps the make with no model invented.
- **Tested:** an unknown maker gets no link and an honest line ("Sorted doesn't have a checked support page for Acme
  yet"). The route goes to the shop or a repairer.
- **Result:** no failures.

### Serial privacy

- **Tested:** the full serial is stored once, in the case's product record.
- **Tested:** it is masked or absent on Home, Cases, the case page (until Show), the ledger, the history, the helper's
  link and stored card, the pack, the summary, the assistant (context, text and question), error reports, usage
  records, reminder rows, the address bar and "Download my cases". It goes into the prepared message only through
  "Add the full serial number to the message".
- **Finding (fixed in v161):** a serial typed in the person's own words was taken as the case reference and shown on
  Home. It is now dropped from the reference, the title and the ledger once the product holds it.
- **Finding (fixed in v164):** two devices editing different product details used to name a false conflict. A
  bookkeeping counter and an update time on the product record differed between the devices. Both are gone. The
  ledger now recognises each detail by type, value and time. Product details merge key by key, and a real conflict is
  named "product detail" (test 107).
- **Accepted:** the person's own words keep what they typed on the case page. Sorted doesn't rewrite them. The phone's
  copy of the case holds the full serial, like every other case detail, and is removed at sign-out.

### Receipt confirmation

- **Tested:** a receipt photo gives the shop and the date as candidates. They reach nothing (not the repair fields, not
  the route) until "Looks right" or Next.
- **Tested:** a date read wrong and then typed differently is a correction, with the reading kept and the ledger row
  replaced. The route then uses the corrected date (test 131).
- **Tested:** a month-first date is never read and is said so. Two dates are offered, not chosen. A future date is
  refused.
- **Result:** no failures.

### Dangerous symptoms

- **Tested:** `tests/product/safety_corpus.mjs` holds 63 everyday descriptions: 34 that must stop, 13 that must go to a
  qualified person, and 16 that must not stop.
- **Finding (fixed, rules now `ps-2`):** "there was a flash and a bang" and "smell of petrol" were not stopped. Both are
  now caught.
- **How old cases change:** a decision made under `ps-1` is made again on the next save. The old decision is kept in
  `safetyWas`.
- **Tested:** the page's own danger words still stop too. Negation clears only what it governs.
- **Accepted:** the page's older reader stops "no burning smell or smoke" (a false positive). False positives are
  acceptable here.

### Failed photo reading

- **Tested:** a blurred label, a 12 px image, a text file and a HEIC photo the browser can't open each end with a clear
  message and a way out (retake, choose another, type). Nothing is saved.
- **Tested:** a refresh before Start keeps nothing.
- **Result:** no failures.

### Official link accuracy

- **Tested:** every registry link is https and on one of that maker's own domains, inside its UK path where it has one
  (unit tests, which also refuse look-alike and suffix-trick domains and non-UK paths).
- **Tested:** each page was opened and read on 10 October 2026 (`ProductMakers.CHECKED`). Recheck within 90 days
  (gate G8).
- **Still open:** pages change. There is no automatic link check yet, because these sites block simple robots. Rechecking
  them by hand every quarter is the control.

### The whole journey

- **Tested** (tests 130 and 131): photo or typing → confirmed product → safety → purchase → Best next step → Prepare
  contact (no promise made) → their reply proposed → confirmed as an ordinary promise.
- **Tested:** Home, the pack and the helper's link agree. The visit is missed and recorded against the shop. The chase
  is about the washing machine with no serial. The product survives the miss and a change of kind.
- **Result:** no failures.

## What Baldwin needs to do before Phase 2

1. Run the new section of `docs/PHONE_CHECK.md` on an iPhone and an Android phone, with real labels and a real receipt.
2. Review this file and say whether Phase 2 (official guidance) can be designed.

## Rules Phase 2 keeps

- Official guidance, or no guided troubleshooting.
- Safety comes first and is deterministic.
- The normal Sorted core stays the authority for facts, obligations, plans, responsibility, reminders and history.
