const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='3e58d6591727a785cdd28487657f6d3f6bff7ca1')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,90));s=s.split(a).join(b)}
// ---- v55: tighten the spotlight after testing the visual polish on a real iPhone. ----

// The page already says Needs you. Do not repeat Your move inside the spotlight.
R(`<span class="home44-state">Your move</span>`,``);

// Use the promise wording to make the outcome question more human when the old reader only says "Did it happen?".
R(`function home44Spot(t){`,String.raw`function home55Question(p,q){
  var original=q&&q[0]?String(q[0]):"Did it happen?";
  if(!/^Did it happen\??$/i.test(original))return original;
  var said=String(p&&p.said||"").toLowerCase(),party=String(p&&p.party||"").trim();
  if(/\b(refund|reimburse|credit|payment|money|transfer|payout)\b/.test(said))return "Did the money arrive?";
  if(/\b(call back|callback|ring back|get back|reply|respond|response|contact you|update you)\b/.test(said))return "Did they get back to you?";
  if(/\b(parcel|package|delivery|deliver|replacement|shipment)\b/.test(said))return "Did it arrive?";
  if(/\b(repair|repaired|fix|fixed)\b/.test(said))return "Did they fix it?";
  if(/\b(engineer|appointment|visit|attend|turn up|come round|come out)\b/.test(said))return "Did they turn up?";
  if(party){
    var generic=/^(letting agent|landlord|engineer|council|insurer|bank|garage|retailer|seller|courier)$/i.test(party);
    return "Did "+(generic?"the "+party.toLowerCase():party)+" do what they said?";
  }
  return "Did they do what they said?";
}
function home44Spot(t){`);
R(`    h+='<p class="home44-question">'+esc(q[0])+'</p>';`,`    var hq=home55Question(p,q);h+='<p class="home44-question">'+esc(hq)+'</p>';`);

// Keep the time easy to scan and move the reference onto its own quieter line.
R(`    h+='<p class="home44-meta">'+esc(who)+' · '+esc(whenText(p))+(p.ref?' · Ref '+esc(p.ref):'')+'</p>';`,`    h+='<div class="home55-meta"><p class="home55-meta-main">'+esc(who)+' · '+esc(whenText(p))+'</p>'+(p.ref?'<p class="home55-ref">Ref '+esc(p.ref)+'</p>':'')+'</div>';`);

R(`</style>\n\n</head>`,String.raw`/* v55 spotlight refinement */
.home44-spot{padding:14px 16px;gap:10px;box-shadow:0 8px 20px rgba(20,23,38,.06)}
.home44-spot-top{padding-left:3px}
.home44-question{padding-left:3px;margin-top:1px}
.home44-actions{gap:7px;padding-left:3px}
.home44-details{margin-top:1px;opacity:.78}
.home55-meta{padding-left:3px;display:flex;flex-direction:column;gap:2px;color:var(--ink-2)}
.home55-meta-main{font-family:inherit;font-size:15px;line-height:1.35;letter-spacing:0;overflow-wrap:anywhere}
.home55-ref{font-family:var(--mono);font-size:13px;line-height:1.3;color:var(--ink-2);opacity:.82}
/* The headline already says the number. Turn the graphic badge into a simple decorative dot. */
.home54-count{min-width:12px;width:12px;height:12px;padding:0;font-size:0;border-width:2px;right:3px;bottom:3px}
.home54-count:after{content:"";position:absolute;inset:-5px;border:1px solid color-mix(in srgb,var(--lav) 42%,transparent);border-radius:50%}
@media (max-width:520px){
  .home44-spot{padding:13px 14px;gap:9px}
  .home55-meta-main{font-size:14px}
  .home55-ref{font-size:12px}
}
</style>

</head>`);

fs.writeFileSync('public/index.html',s);
const EXPECT='e85685844d0348a06ba6852123ec0cb1100d77dd';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v55 ok',h(s),s.length);
