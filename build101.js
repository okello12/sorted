const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='71073c67b75d5e7933395eb812cdb0e39c569d02')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v101: "The screen is broken": the thing named is kept (thingOf), so the first response says "Your screen isn't
// working" and "What is it?" is filled in. A start choice carried over a page load opens its own questions, and is
// forgotten once a case starts. ----
R("else if(!/washing machine/i.test(t.said))t.fix.item=\"\";",
  "else if(!/washing machine/i.test(t.said))t.fix.item=thingOf(t.said);");
R("U.push((t.fix&&t.fix.item?(/damp|mould/i.test(t.fix.item)?\"There’s damp or mould\":t.fix.item+(/^(?:window|door)$/i.test(t.fix.item)?\" needs fixing\":\" isn’t working\")):\"Something isn’t working\")+",
  "U.push((t.fix&&t.fix.item?(/damp|mould/i.test(t.fix.item)?\"There’s damp or mould\":\"Your \"+itemSay(t.fix.item)+(/^(?:window|door)$/i.test(t.fix.item)?\" needs fixing\":/s$/i.test(t.fix.item)&&!/ss$/i.test(t.fix.item)?\" aren’t working\":\" isn’t working\")):\"Something isn’t working\")+");
R("  S.tasks=cacheRead();momSplit();momPendingBoot();S.booting=false;",
  "  S.tasks=cacheRead();momSplit();momPendingBoot();giRestore();S.booting=false;");
R("t.frNew=true;var pb98=pbFor(t);",
  "giForget();t.frNew=true;var pb98=pbFor(t);");
R("function momLatest(){",
  "/* v101: the thing someone says is broken (\"The screen is broken\", \"my fridge door won't close\"), kept so Sorted\n   doesn't ask \"What is it?\" with an empty box. */\nvar THING_RE=/\\b(?:my|the|our|a|an)\\s+((?:[a-z]+\\s+){0,2}?[a-z]+?)\\s+(?:is|are|has|have|was|keeps?|won't|wont|will not|doesn't|does not|isn't|is not|stopped|broke|cracked|smashed|died|packed up|not working)\\b/i;\nvar THING_NOT=/^(?:landlord|council|engineer|company|shop|seller|agent|agency|they|it|thing|things|problem|issue|repair|repairs|man|guy|owner|neighbour|plumber|electrician|technician|builder|bathroom|kitchen|bedroom|hallway|lounge|room|flat|house|home|place|one|order|parcel|refund|money|bill|account|claim)$/i;\nfunction thingOf(x){var m=THING_RE.exec(String(x||\"\").replace(/[’‘]/g,\"'\"));if(!m)return \"\";var w=m[1].trim().toLowerCase();if(THING_NOT.test(w.split(/\\s+/).pop())||THING_NOT.test(w.split(/\\s+/)[0]))return \"\";return w.charAt(0).toUpperCase()+w.slice(1)}\nfunction itemSay(it){var x=String(it||\"\");return /^(?:[A-Z]{2,}|TV)\\b/.test(x)?x:x.charAt(0).toLowerCase()+x.slice(1)}\n/* a start choice carried over a page load (the landing page, the installed app) opens its own questions */\nfunction giRestore(){var k=\"\",carry=\"\";try{k=sessionStorage.getItem(\"sorted.cap82\")||\"\";carry=sessionStorage.getItem(\"sorted.carry82\")||\"\";sessionStorage.removeItem(\"sorted.carry82\")}catch(e){}\n  if(!carry){if(k&&!(S.draft&&S.draft.gk))giForget();return}  /* a reload restores saved work only, never a half-done start */\n  if(k&&(GI[k]||k===\"document\"||k===\"other\")&&!(S.draft&&S.draft.gk)&&S.view.name===\"home\"){S.draft=Object.assign({},S.draft||{},{gk:k});S.composeOpen=true}}\nfunction giForget(){try{sessionStorage.removeItem(\"sorted.cap82\");sessionStorage.removeItem(\"cap90.choice\")}catch(e){}try{if(window.__cap87reset)window.__cap87reset();if(window.__cap90reset)window.__cap90reset()}catch(e){}}\nfunction momLatest(){");
R("S.draft={gk:GI[ck]||ck===\"document\"||ck===\"other\"?ck:null};var cx95=",
  "S.draft={gk:GI[ck]||ck===\"document\"||ck===\"other\"?ck:null};if(!S.user){try{sessionStorage.setItem(\"sorted.carry82\",\"1\")}catch(z){}}var cx95=");
fs.writeFileSync('public/index.html',s);
const EXPECT='911a1f0bacdf3bf1b5bf2216149f651feac5f2d2';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v101 ok',h(s),s.length);
