const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='3139a5a5c3b18d7b335f1851483870c63d2c301d')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+String(a).slice(0,70));s=s.split(a).join(b)}
// ---- v13: case artwork, one image per moment, always decorative ----
const ART=`
/* ---------- case artwork: decorative only; status, dates and controls stay as text ---------- */
var ART_SIZE={"hero-case":[640,410],"state-waiting":[420,273],"state-needs-you":[320,218],"state-missed":[300,197],"state-done":[400,353],"hold-up-pack":[280,235],"share-one-case":[440,223],"context-appliance":[260,189],"context-housing":[260,171],"context-refund":[260,214],"context-renewal":[260,215],"context-deadline":[260,191]};
function art(name,cls,eager){var z=ART_SIZE[name];return '<img class="art art-'+cls+'" src="/art/'+name+'.webp" width="'+z[0]+'" height="'+z[1]+'" alt="" aria-hidden="true" decoding="async"'+(eager?' fetchpriority="high"':' loading="lazy"')+' onerror="this.remove()">'}
function artFamily(text,mode){
  var s=String(text||"").toLowerCase();
  if(mode==="renew")return "renewal";
  if(/\\b(landlord|letting|tenan|rent\\b|heating|boiler|radiator|damp|mou?ld|council|housing|flat\\b|roof|hot water)/.test(s))return "housing";
  if(/\\b(refund|money back|charged|overcharged|order|delivery|parcel|compensation|return(ed)?\\b)/.test(s))return "refund";
  if(mode==="do"||/\\b(deadline|submit|application|apply|form\\b|bursary|tax return|by (monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow))/.test(s))return "deadline";
  if(mode==="fix")return "appliance";
  return "";
}
`;
R("\n/* ---------- render & events ---------- */",ART+"\n/* ---------- render & events ---------- */");
R(`.hero-art{display:block;width:100%;max-width:440px;height:auto;margin:4px auto 0}`,`.hero-art{display:block;width:100%;max-width:440px;height:auto;margin:4px auto 0}
.art{display:block;height:auto;max-width:100%;pointer-events:none;user-select:none;-webkit-user-select:none}
.art-hero{width:100%;max-width:300px;margin:0 auto}
.art-done{width:200px;margin:0 auto}
.art-state{width:180px;margin:0 auto}
.art-mini{width:130px;margin:0 auto}
.art-context{width:120px;margin:0}
.art-group{width:84px;margin:0 0 2px}
.art-share{width:220px;margin:0 auto}`);

// 1. first visit: the hero sits above the sentence box, only while there are no cases
R(`  h+=caseEntry();`,`  if(!S.tasks.length)h+=art("hero-case","hero",true);\n  h+=caseEntry();`);
// 2. understood: one broad family beside the interpretation
R(`    h+='<div class="stack-s"><h1 class="h2">What were you planning to do next?</h1>`,`    var fam=artFamily(d.title,mode);if(fam||d.title)h+='<div class="stack-s">'+(fam?art("context-"+fam,"context"):"")+(d.title?'<p class="h3">'+esc(d.title)+'</p>':"")+'</div>';\n    h+='<div class="stack-s"><h1 class="h2">What were you planning to do next?</h1>`);
// 3. all waiting
R(`    if(!yours.length&&held)h+='<section class="calm stack-s"><p class="h2">Nothing needs you right now.</p>`,`    if(!yours.length&&held)h+='<section class="calm stack-s">'+art("state-waiting","hero")+'<p class="h2">Nothing needs you right now.</p>`);
// 4. waiting section header, only when the calm panel isn't already showing it
R(`    h+=group("Waiting",waiting);`,`    h+=group("Waiting",waiting,yours.length?art("state-waiting","group"):"");`);
R(`function group(title,list){`,`function group(title,list,pic){`);
R(`  var h='<section class="group"><div class="group-h">`,`  var h='<section class="group">'+(pic||"")+'<div class="group-h">`);
// 5. needs you: the window has ended
R(`    h+='<p>The time has passed. Tell Sorted what happened.</p>`,`    h+=art("state-needs-you","state")+'<p>The time has passed. Tell Sorted what happened.</p>`);
// 6. missed: a small accent over the chase
R(`<p class="eyebrow">'+(m?"Chasing a missed promise":ch(via).prep)+'</p>`,`'+(m?art("state-missed","mini"):"")+'<p class="eyebrow">'+(m?"Chasing a missed promise":ch(via).prep)+'</p>`);
// 7. done
R(`'<section class="sheet stack"><div class="stack-s"><p class="eyebrow">Finished</p>`,`'<section class="sheet stack">'+art("state-done","done")+'<div class="stack-s"><p class="eyebrow">Finished</p>`);
// 8. show this: small art beside the launch, gone once the pack opens
R(`    h+='<button class="btn primary block" data-a="panel" data-p="hold">Show this</button>`,`    h+=art("hold-up-pack","mini")+'<button class="btn primary block" data-a="panel" data-p="hold">Show this</button>`);
// 9. share one case: in the explanation before the link exists
R(`  h+='<button class="btn block" data-a="share">'`,`  if(!t.shareToken)h+=art("share-one-case","share")+'<p class="h3">Share this case only.</p>';\n  h+='<button class="btn block" data-a="share">'`);
// 10. landing
R(`<img class="hero-art" src="/sorted-hero.webp" width="600" height="395" alt="A washing machine, a calendar and a phone" fetchpriority="high">`,`<img class="hero-art" src="/art/hero-case.webp" width="640" height="410" alt="A case folder with a washing machine, a clock and a phone" fetchpriority="high">`);

fs.writeFileSync('public/index.html',s);
const EXPECT='9a8bbc6cec58b19825563d49ed8a6ec12e6df4c4';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v13 ok',h(s),s.length);
