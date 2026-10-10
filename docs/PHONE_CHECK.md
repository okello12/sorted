# Before a wider release: 20 minutes on a real phone

The test suite runs in Chromium, and GitHub also walks the page through Safari's engine (WebKit) and Firefox. None of
that is an iPhone in someone's hand. Do this on a real phone before inviting people who aren't testers. Tick each line.

## iPhone, Safari, and the Home Screen app

1. Open https://sorted-pilot.vercel.app in Safari. Share → Add to Home Screen. Open it from the Home Screen.
2. Start a case: "Sky said an engineer would come Tuesday between 8 and 12, ref AB123". Confirm the promise.
3. Lock the phone for a minute. Unlock and reopen the app. The case is still there, no blank page.
4. Tap Home in the bar. Tap the case. Swipe back from the left edge. You land on Home, not a blank page.
5. Turn the phone sideways and back. Nothing is cut off and nothing scrolls sideways.
6. Settings → Accessibility → Display & Text Size → Larger Text, drag to the largest. Reopen Sorted. Home and the case are
   readable, buttons can be tapped, nothing scrolls sideways. Put the size back.
7. Settings → Accessibility → VoiceOver → on. Swipe right through Home and the case page. Every button and link is read
   out with a name that makes sense ("Copy a link for someone helping you", not "button"). The promise card reads the
   date. Turn VoiceOver off (triple-click the side button if it's set up, or ask Siri).
8. Switch the phone to Dark Mode (Control Centre or Settings → Display). Everything is readable.
9. Turn on Airplane Mode. Mark the promise as "They came". Turn Airplane Mode off. The bar says it's saving, then the
   change is there after a reload.
10. Open a share link you sent yourself in WhatsApp. It opens the case, read-only.

## Android, Chrome

1. Open the site in Chrome. Menu → Add to Home screen (or Install app). Open it from the Home screen.
2. Repeat steps 2 to 5 above, using the Android back gesture.
3. Settings → Accessibility → Font size, largest. Repeat step 6.
4. Settings → Accessibility → TalkBack → on. Repeat step 7. Turn it off (volume keys held together, if set up).
5. Repeat steps 8 to 10.

## Something I own isn't working (Phase 1.5, 15 minutes, iPhone and Android)

Use real appliances at home. Never photograph a card, a bank letter or anything with someone else's details on it.

1. New → Something's broken → Take a photo. Photograph the rating label of a washing machine, fridge or dishwasher
   (inside the door or on the back) straight on, in normal light. Sorted says "Label read" and shows the make, the model
   and the serial as ••••1234. Compare the model letter by letter with the label. Note any letter it got wrong.
2. Do it again at an angle, in dim light, and with the flash on (glare). Note what Sorted read each time, or that it
   said it couldn't read the photo. A wrong model must be one you can correct before Start.
3. Photograph the appliance itself, not its label. Sorted may give the make, or ask for the label ("Now photograph the
   label", with where it usually is). It must never show a model.
4. Tap Show and Hide on the serial. Tap Start. On the case, check Home, Cases and the case page never show the serial
   in full; Show and Copy work on the case.
5. On the purchase step, photograph a till receipt or an order confirmation on screen (your own, with nothing
   sensitive on it). Check the shop and the date it read, change one, and press Next. The Best next step must use
   what you confirmed.
6. Type "there's a burning smell" as what's happening. Sorted must stop: the safety screen, no support page offered
   as a fix.
7. Turn on Airplane Mode and take a label photo. If the reader has been used before on this phone it may still read the
   photo, since it works on the phone; if not, Sorted must say it couldn't read it and offer typing. Either way nothing
   is saved until Start.
8. Open the maker's support link on the case. It must open the maker's own UK page.

## If something fails

Write down the step number, the phone and its OS version, and what happened. Nothing else is needed. That goes in
`docs/LATER.md` or straight into a fix.

## With three people who have never seen Sorted (10 minutes each)

The screenshots show whether the first screen is clear. They cannot show whether someone understands it. Hand the person
your phone, signed out, on the first screen. Say nothing about what Sorted is. Ask, in this order, and write down what
they say in their own words:

1. "What would you use Sorted for?"
2. "How would you start tracking a repair someone promised?"
3. "What would you expect Sorted to do next?"

Then let them try question 2 for real and watch where they hesitate. Three people who answer 1 and 2 without help are
evidence that the first screen is doing its job. One person who can't is a finding, in `docs/LATER.md` with their words.
