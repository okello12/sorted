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

## If something fails

Write down the step number, the phone and its OS version, and what happened. Nothing else is needed. That goes in
`docs/LATER.md` or straight into a fix.
