# "Add to Sorted" from the iPhone share sheet

Since v40, opening `https://sorted-pilot.vercel.app/#new=<text>` fills Sorted's case box with that text. Nothing is saved
until the person presses Start. The text sits after the `#`, which browsers never send to a server, and the page removes
it from the address bar as soon as it has read it.

## Make the Shortcut (once, on an iPhone)

1. Open the **Shortcuts** app and tap **+**.
2. Tap the shortcut's name at the top and call it **Add to Sorted**.
3. Tap the **ⓘ** (details) button and switch on **Show in Share Sheet**. Under share sheet types, keep **Text** and **URLs**.
4. Back in the editor, add the action **URL Encode**. Its input should be **Shortcut Input**.
5. Add the action **Text** and type `https://sorted-pilot.vercel.app/#new=` then insert the **URL Encoded Text** variable right after it.
6. Add the action **Open URLs** (its input is the Text from step 5).
7. Tap **Done**.

Try it: in Messages or Mail, select the company's message, tap **Share**, then **Add to Sorted**. Sorted opens with the
message in the box. Check it, take out anything it doesn't need, and press Start.

## Share it with testers

In Shortcuts, long-press **Add to Sorted** → **Share** → **Copy iCloud Link**. Send testers that link. They tap it, then
**Add Shortcut**.

## Limits

- iPhone only. Android's share sheet can't send to a web page without an installed app (see `docs/LATER.md`, item 4).
- Very long messages are cut to 4,000 characters before they reach the box.
- If the person isn't signed in, the text waits on that phone (in the browser tab) until they start.
