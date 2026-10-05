const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='02e30a06a2140fd6f9863627b437cc6cfc592551')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v134: forwarding to a secret address per person, Android share, a Home Screen icon, and the privacy notice for
// forwarding and lock-screen reminders. ----
R("  S.inboundAddr=null;S.inbox=[];return;   /* forwarding is off (v28) and its addresses are gone; see docs/LATER.md item 2 */\n",
  "  /* v134: forwarding is back, to a secret address per person (log-<16 hex>@…). Anyone who has the address can send to it,\n     so every email is a suggestion: you choose the case, start one, or remove it. Get a new address any time. */\n");
R("<strong>You forwarded an email from '+from+'.</strong> Add this promise to",
  "<strong>An email came to your Sorted address from '+from+'.</strong> Add it to");
R("<strong>You forwarded an email from '+from+'.</strong> Which case is it for?",
  "<strong>An email came to your Sorted address from '+from+'.</strong> Which case is it for?");
R("function grabShared(){\n",
  "function grabShared(){\n  /* v134: Android's share sheet (the manifest's share_target) opens /?st=title&sx=text&su=link */\n  try{var q0=new URLSearchParams(location.search),p0=[q0.get(\"st\"),q0.get(\"sx\"),q0.get(\"su\")].filter(Boolean);\n    if(p0.length){var t0=p0.join(\"\\n\").replace(/\\r/g,\"\").trim().slice(0,4000);history.replaceState(null,\"\",location.pathname);if(t0){S.sharedIn=t0;try{sessionStorage.setItem(\"sorted.sharedIn\",t0)}catch(e){}return true}}}catch(e){}\n");
R("<meta name=\"apple-mobile-web-app-title\" content=\"Sorted\">",
  "<meta name=\"apple-mobile-web-app-title\" content=\"Sorted\"><link rel=\"apple-touch-icon\" href=\"/icon-180.png\">");
R("Forwarding other emails into Sorted is switched off.",
  "You can also forward emails to your own Sorted address, found in Account under Settings. They are received by Resend and kept for 30 days, until you add them to a case or remove them. Anyone who has that address can send to it, so Sorted shows each email as a suggestion for you to accept or remove, and you can get a new address at any time; the old one then stops working.");
R("Sorted emails you a reminder link when something is due, unless you turn it off for that case; the email doesn’t include case details.",
  "Sorted emails you a reminder link when something is due, unless you turn it off for that case; the email doesn’t include case details. If you switch on reminders on a phone, Sorted keeps that phone’s notification address, issued by Apple, Google, Mozilla or Microsoft, and sends each reminder through that company’s push service, encrypted. The notification doesn’t say what the case is. Switching reminders off on the phone, or deleting your account, deletes that address.");
R("h+=pushBlock(\"settings\");",
  "h+=pushBlock(\"settings\");h+=forwardBlock();");
R("function loadInbox(){",
  "function forwardBlock(){\n  if(!S.inboundAddr)return \"\";\n  return '<section class=\"sheet stack-s fwd134\"><p class=\"h3\">Forward emails to Sorted</p><p>Forward an email from a company to your own Sorted address. It arrives on Home as a suggestion: you choose its case, start one, or remove it.</p><label class=\"f\"><span class=\"sr-only\">Your Sorted address</span><input id=\"fwd-addr\" class=\"mono\" readonly value=\"'+esc(S.inboundAddr)+'\"></label><div class=\"row eq\"><button class=\"btn primary\" data-a=\"fwd-copy\">Copy the address</button><button class=\"btn\" data-a=\"fwd-new\">Get a new address</button></div><p class=\"muted\" style=\"margin:0;font-size:15px\">Only you see what arrives. Anyone who has the address can send to it, so if it gets out, get a new one: the old one stops working straight away. Emails wait up to 30 days.</p></section>';\n}\nfunction loadInbox(){");
R("    case \"push-on\":",
  "    case \"fwd-copy\":{var fa=$(\"#fwd-addr\");if(fa){try{navigator.clipboard.writeText(fa.value).then(function(){toast(\"Copied.\")},function(){fa.select();toast(\"Select it and copy.\")})}catch(e){fa.select()}}break}\n    case \"fwd-new\":sb.rpc(\"inbound_address_new\").then(function(r){if(r&&r.data){S.inboundAddr=r.data;render();toast(\"New address ready. The old one no longer works.\")}else toast(\"Couldn’t make a new address. Try again later.\")},function(){toast(\"Couldn’t make a new address. Try again later.\")});break;\n    case \"push-on\":");
R("select(\"id,subject,body,received_at\")",
  "select(\"id,subject,body,received_at,from_domain\")");
R("from=mi.party?esc(mi.party):\"someone\"",
  "from=mi.party?esc(mi.party):it.from_domain?esc(it.from_domain):\"someone\"");
R("var SORTED_V=\"v133\"",
  "var SORTED_V=\"v134\"");
fs.writeFileSync('public/index.html',s);
const EXPECT='8ef4ed6d80ad86438215354c8f4ec621fbbaeb17';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v134 ok',h(s),s.length);
