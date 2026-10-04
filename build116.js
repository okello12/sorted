const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='c4025e5524fd39afc2bfa75dc4845e32b99d8045')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v116 (Phase 1): wording corrected to what Sorted really does (deletion, access, official links, guest
// accounts, usage records, reminder arrival); opening Sorted counts as guest activity (touch_seen); the numbers
// page shows delivery evidence. ----
R("var SORTED_V=\"v115\"",
  "var SORTED_V=\"v116\"");
R("S.tasks=cacheRead();momSplit();momPendingBoot();giRestore();S.booting=false;render();openPending();checkEmailReady();loadInbox();sendEvents();",
  "S.tasks=cacheRead();momSplit();momPendingBoot();giRestore();S.booting=false;render();openPending();checkEmailReady();loadInbox();sendEvents();try{sb.rpc(\"touch_seen\").then(function(){},function(){})}catch(e){}");
R("Links to official pages are checked by hand and dated, but the page at the other end can change; the official page is always right and Sorted is not.</p>",
  "Links to official pages are checked by hand and dated, but links and guidance can change. Check the relevant authority’s current guidance before acting.</p>");
R("<p><strong>Reminders are best efforts.</strong> Sorted tries to email you when something is due. Email can fail or be late, and a reminder isn’t a guarantee that you won’t miss a deadline. Keep your own note of anything that matters, such as a court or tribunal date.</p>",
  "<p><strong>Reminders are best efforts.</strong> Sorted sends an email at the time it shows. When it arrives depends on email, and it can be late or not arrive. A reminder isn’t a guarantee that you won’t miss a deadline. Keep your own note of anything that matters, such as a court or tribunal date.</p>");
R("<p><strong>Your cases are yours.</strong> You can copy or download them, and delete a case or your whole account at any time. Deleting is immediate and can’t be undone. Sorted keeps nothing you delete.</p>",
  "<p><strong>Your cases are yours.</strong> You can copy or download them, and delete a case or your whole account at any time. Deleting a case removes it from Sorted’s servers straight away, with its helper link and any unsent reminders; for two minutes Home offers Undo, and closing or refreshing the page ends that. Usage records about the case (its id and the steps you used, never its content) stay for up to 12 months. Deleting your account removes everything at once, usage records included, with no Undo. Emails Sorted has already sent stay in your inbox.</p>");
R("Sorted keeps your cases in London to hold them and remind you. Nobody running Sorted reads them. It records which steps you use, without case details. Idle cases are deleted after 90 days, or 30 if you haven’t added an email, unless a promise on them is still pending. You can copy or delete everything at any time.</p>",
  "Sorted keeps your cases in London to hold them and remind you. The person running it has technical access to the database, as with any online service, and doesn’t use it to read your cases. It keeps usage records (which steps you use, with no case content). Idle cases are deleted after 90 days, unless a promise on them is still pending. Without an email, your cases are deleted after 30 days in which you don’t open Sorted. You can copy or delete everything at any time.</p>",2);
R("It also keeps step records, explained below, to learn whether Sorted works.</p>",
  "It also keeps usage records, explained below, to learn whether Sorted works.</p>");
R("Sorted’s own numbers come only from step records, which hold no case details.",
  "Sorted’s own numbers come only from usage records, which hold no case content.");
R("If you haven’t added an email, your cases are deleted after 30 days away.",
  "Without an email, your cases are deleted after 30 days in which you don’t open Sorted (opening it signed in, saving a case or a live promise all count).");
R("Sorted emails you a reminder link when something is due, unless you turn it off for that case; the email doesn’t include case details.",
  "Sorted emails you a reminder link when something is due, unless you turn it off for that case; the email doesn’t include case details. Sorted records whether its email provider accepted, delivered or bounced each reminder, never the address or the case.");
R("Turning off step records on a phone also stops this.</p>",
  "Turning off usage records on a phone also stops this.</p>");
R("It keeps step records because it has a legitimate interest in learning whether Sorted works, and you can turn them off.",
  "It keeps usage records because it has a legitimate interest in learning whether Sorted works, and you can turn them off. They hold your account id and case ids with the steps you used, so they are not anonymous; they hold no case content, and go with your account when you delete it.");
R("<p><strong>Your cases are private.</strong> Nobody running Sorted reads them, unless you ask for help with one or the law requires it. Sorted’s own numbers come only from usage records, which hold no case content. The person running Sorted has technical access to the database, as with any online service, and doesn’t use it to open cases otherwise.",
  "<p><strong>Your cases are private.</strong> The person running Sorted has technical access to the database, as with any online service, and doesn’t use it to open cases, unless you ask for help with one or the law requires it. Sorted’s own numbers come only from usage records, which hold no case content.");
R("Step records are linked to your account but hold no case details.",
  "Usage records are linked to your account (your account id and the case ids) but hold no case content.");
R("It asks only for what it needs, nobody running it reads your cases, and you can copy or delete everything at any time.</p>",
  "It asks only for what it needs, the person running it has technical access as any online service does and doesn’t use it to read your cases, and you can copy or delete everything at any time.</p>");
R("'Nobody running Sorted reads your case content.'",
  "'The person running Sorted doesn’t use his access to read your cases.'");
R("For your step records or anything else Sorted holds, email",
  "For your usage records or anything else Sorted holds, email");
R("<p class=\"h3\">Step records</p><p>'+(noSteps()?\"Sorted isn’t recording which steps you use on this phone.\":\"Sorted records which steps you use, such as “promise added”, without any case details. It helps show whether Sorted works.\")+'</p><button class=\"btn\" data-a=\"steps-toggle\">'+(noSteps()?\"Record my steps again\":\"Don’t record my steps\")+'</button>",
  "<p class=\"h3\">Usage records</p><p>'+(noSteps()?\"Sorted isn’t recording which steps you use on this phone.\":\"Sorted records which steps you use, such as “promise added”, with your account id and the case id but no case content. It helps show whether Sorted works. These go when you delete your account.\")+'</p><button class=\"btn\" data-a=\"steps-toggle\">'+(noSteps()?\"Record my usage again\":\"Don’t record my usage\")+'</button>");
R("<p><strong>Without an email, only this phone can open your cases.</strong> They’re saved on Sorted’s servers, but if you clear this browser or change phone, they can’t be recovered. Add your email to keep them and get reminders.</p>",
  "<p><strong>Without an email, only this phone can open your cases.</strong> They’re saved on Sorted’s servers, but only this browser holds the key: clear it or change phone and they can’t be opened again. They’re also deleted after 30 days in which you don’t open Sorted. Add your email to open them anywhere and get reminders.</p>");
R("<span>Saved to an account only this phone can open. Add an email for reminders, and to get your cases back if you lose the phone.</span>",
  "<span>Saved on Sorted’s servers, to an account only this phone can open. Add an email for reminders, and to open your cases anywhere.</span>");
R("[\"How do reminders work?\",\"When a promise falls due, the case moves to the top of Home and asks what happened. If you’ve added an email, Sorted emails you as well. You can add the date to your own calendar from the case. Reminders are best efforts, so keep your own note of anything critical, such as a tribunal date.\"],",
  "[\"How do reminders work?\",\"When a promise falls due, the case moves to the top of Home and asks what happened. If you’ve added an email, Sorted sends an email at the time it shows; when it arrives depends on email, and it can be late or not arrive. You can add the date to your own calendar from the case, which uses your calendar’s own alerts. Keep your own note of anything critical, such as a tribunal date.\"],");
R("[\"What if I lose my phone?\",\"With an email, sign in on any phone or computer and your cases are there. Without one, only the phone you started on can open them.\"],",
  "[\"What if I lose my phone?\",\"With an email, sign in on any phone or computer and your cases are there. Without one, your cases are on Sorted’s servers but only the browser you started in can open them, so a lost phone or a cleared browser means they can’t be opened again. Check Account to see whether an email is linked.\"],\n  [\"What happens when I delete a case or my account?\",\"A deleted case leaves Sorted’s servers straight away, with its helper link and any unsent reminders. For two minutes Home offers Undo; closing or refreshing the page, or tapping anything else, ends that. Usage records about the case (its id and the steps you used, never its content) stay for up to 12 months. Deleting your account removes everything at once, usage records included, with no Undo. Emails Sorted has already sent stay in your inbox.\"],");
R("<p><strong>Deleted “'+esc(home54Title(u.t))+'”.</strong>'+(u.t.shareToken?' Its helper link is off.':'')+'</p><button class=\"link\" data-a=\"del-undo\" style=\"align-self:flex-start\">Undo</button></div>'}",
  "<p><strong>Deleted “'+esc(home54Title(u.t))+'”.</strong>'+(u.t.shareToken?' Its helper link is off.':'')+' Undo works for two minutes, on this page only: closing or refreshing it, or tapping anything else, ends that.</p><button class=\"link\" data-a=\"del-undo\" style=\"align-self:flex-start\">Undo</button></div>'}");
R("  var pe=H.page||{};rows.push([pe.count_24h>=20?\"red\":(pe.count_24h?\"amber\":\"ok\"),\"Errors\",",
  "  var dv=H.delivery||{};if(H.delivery){var dvt=(dv.scheduled_7d||0)+\" due, \"+(dv.submitted_7d||0)+\" handed to Resend, \"+(dv.accepted_7d||0)+\" accepted, \"+(dv.delivered_7d||0)+\" delivered, \"+(dv.bounced_7d||0)+\" bounced\"+(dv.delayed_7d?\", \"+dv.delayed_7d+\" delayed\":\"\")+(dv.unknown_7d?\", \"+dv.unknown_7d+\" with no delivery news after an hour\":\"\")+\" in 7 days.\"+(dv.late_minutes_median!=null?\" Handed over a median \"+Math.round(dv.late_minutes_median)+\" min after due.\":\"\")+(dv.arrival_minutes_median!=null?\" Delivered a median \"+Math.round(dv.arrival_minutes_median)+\" min after acceptance.\":\"\")+(dv.webhook_seen?\"\":\" No delivery or bounce event has ever arrived: Resend’s webhook isn’t set up yet, so arrival is unmeasured.\");rows.push([dv.bounced_7d||(dv.unknown_7d&&dv.webhook_seen)?\"amber\":\"ok\",\"Delivery\",dvt])}\n  var pe=H.page||{};rows.push([pe.count_24h>=20?\"red\":(pe.count_24h?\"amber\":\"ok\"),\"Errors\",");
fs.writeFileSync('public/index.html',s);
const EXPECT='812b6917dfdfb01d49df66b5e0bdc3fe118d9656';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v116 ok',h(s),s.length);
