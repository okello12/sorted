const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='dc53dae5aaaae14cac1d57881bdc7e9cfca465a3')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+String(a).slice(0,70));s=s.split(a).join(b)}
// ---- v11: one way in, notice not consent, measure the case loop ----
const FEAT4=fs.readFileSync('feat4.js','utf8');
R("\n/* ---------- render & events ---------- */","\n"+FEAT4+"\n/* ---------- render & events ---------- */");

// 1. the sentence box is the only visible way in
R(`  h+='<details class="more"><summary class="muted" style="font-size:15px">Other ways to start</summary><div class="stack-s" style="margin-top:10px">'+startBtn("fix","Something’s broken","Check it safely, then claim, repair or replace")+startBtn("call","I need to contact someone","Get ready, then keep what they promise")+startBtn("renew","Something needs renewing","Passport, MOT, visa and more: know when to start")+'</div></details>';\n`,``);

// 2. a notice, not a consent tick
const NOTICE=`'<p>By continuing, you’re taking part in the Sorted pilot.</p><button type="button" class="link" data-a="privacy" style="text-align:left">'+(d.showPrivacy?"Hide":"Read")+' how Sorted handles your data</button>'+(d.showPrivacy?privacyBlock():"")`;
{const a=s.indexOf("function consentBox(d){\n  return ");const b=s.indexOf("\n}",a);if(a<0)throw new Error('consentBox');s=s.slice(0,a)+"function consentBox(d){\n  return "+NOTICE+";"+s.slice(b)}
{const a=s.indexOf(`  h+='<button type="button" data-a="consent" role="checkbox"`);const b=s.indexOf(`  if(d.showPrivacy)h+=privacyBlock();\n`,a);if(a<0||b<0||b-a>1500)throw new Error('signin consent');
 s=s.slice(0,a)+"  h+="+NOTICE+";\n"+s.slice(b+`  if(d.showPrivacy)h+=privacyBlock();\n`.length)}
R(`case "anon-start":if(!d.consent){d.err="Tick the box to say you’re happy to take part.";render();break}d.err="";`,`case "anon-start":d.err="";`);
R(`    if(!d.consent){d.err="Tick the box to say you’re happy to take part.";render();return}\n`,``);
R(`data:{pilot_consent_at:nowIso()}`,`data:{pilot_notice_at:nowIso()}`,2);
R(`Emails you forward to your Sorted address are kept for 30 days, then deleted.</p>`,`Emails you forward to your Sorted address are kept for 30 days, then deleted.</p><p>To learn whether the pilot works, Sorted also records which steps you use, such as “promise added” or “case finished”, without any case details. These records are deleted after 12 months, or straight away if you delete your account.</p>`);

// 3. measurement
R(`S.view={name:"new",mode:cm};S.draft={step:"baseline",title:ctitle,baseline:""};`,`S.view={name:"new",mode:cm};S.draft={step:"baseline",title:ctitle,baseline:"",fromCase:true};`);
R(`  S.tasks.unshift(t);save();\n`,`  S.tasks.unshift(t);save();trackStart(t,d);\n`);
R(`    if(d.replaces){var old=t.promises.filter(function(x){return x.id===d.replaces})[0];if(old&&old.status==="open"){old.status="replaced";old.closedAt=nowIso();log(t,"They changed the date. It was "+whenText(old)+".")}}`,
  `    var pmiss=!!recentMiss(t);\n    if(d.replaces){var old=t.promises.filter(function(x){return x.id===d.replaces})[0];if(old&&old.status==="open"){old.status="replaced";old.closedAt=nowIso();log(t,"They changed the date. It was "+whenText(old)+".");track("outcome_rescheduled",t,{promise_id:old.id,after_due:phase(old)==="check"})}}`);
R(`    var autoEm=defaultEmail(t);\n`,`    trackPromise(t,pr,pmiss);\n    var autoEm=defaultEmail(t);\n`);
R(`t.promises.push(lpr);t.board="waiting";`,`t.promises.push(lpr);t.board="waiting";track("promise_created",t,{promise_id:lpr.id,matures_at:maturesAt(lpr),src:"letter",has_ref:!!lpr.ref});`);
R(`case "kept":if(t){var p=openPromise(t);p.status="kept";p.closedAt=nowIso();`,`case "kept":if(t){var p=openPromise(t);p.status="kept";p.closedAt=nowIso();track("outcome_kept",t,{promise_id:p.id});`);
R(`case "missed":if(t){var q=openPromise(t);q.status="missed";q.closedAt=nowIso();`,`case "missed":if(t){var q=openPromise(t);q.status="missed";q.closedAt=nowIso();track("outcome_missed",t,{promise_id:q.id});`);
R(`    t.call={who:who,ask:ask,via:via};\n`,`    t.call={who:who,ask:ask,via:via};\n    if(chasing)track("chase_used",t,{promise_id:recentMiss(t).id,via:via});\n`);
R(`t.board="done";t.outcome="Fixed with a safe check";`,`t.board="done";t.outcome="Fixed with a safe check";trackClosed(t);`);
R(`if(v==="fixed"){t.board="done";t.outcome="Working again";`,`if(v==="fixed"){t.board="done";t.outcome="Working again";trackClosed(t);`);
R(`    t.board="done";t.outcome="Renewed"+`,`    t.board="done";trackClosed(t);t.outcome="Renewed"+`);
R(`    t.board="done";t.outcome=out;log(t,"Finished: "+out);`,`    t.board="done";t.outcome=out;trackClosed(t);log(t,"Finished: "+out);`);
R(`case "recap-copy":if(t)copy(recapText(t),"Recap copied");break;`,`case "recap-copy":if(t){copy(recapText(t),"Recap copied");track("recap_copied",t,{via:"copy"})}break;`);
R(`case "recap-share":if(t){var rtx=recapText(t);`,`case "recap-share":if(t){var rtx=recapText(t);track("recap_copied",t,{via:"share"});`);
R(`var ct=S.view.id?task(S.view.id):null;if(ct){defaultEmail(ct);ct._dirty=true}`,`var ct=S.view.id?task(S.view.id):null;if(ct){defaultEmail(ct);ct._dirty=true;var cop=openPromise(ct);if(cop)track("email_added_at_promise",ct,{promise_id:cop.id,anon:true})}`);
R(`  go({name:"task",id:t.id,panel:null});\n}`,`  S.retSrc=src||null;go({name:"task",id:t.id,panel:null});\n}`);
R(`  else if(v.name==="task")html=viewTask();`,`  else if(v.name==="task"){dueReturn();html=viewTask()}\n  else if(v.name==="pilot")html=S.isAdmin?viewPilot():viewHome();`);
R(`openPending();checkEmailReady();loadInbox();`,`openPending();checkEmailReady();loadInbox();sendEvents();sb.rpc("is_pilot_admin").then(function(r){S.isAdmin=!!(r&&r.data===true);if(S.view.name==="data")render()},function(){});`);
R(`window.addEventListener("online",function(){save()});`,`window.addEventListener("online",function(){save();sendEvents()});`);
R(`    case "consent":`,`    case "pilot":if(S.isAdmin){if(S.view.name!=="pilot")go({name:"pilot"});loadPilot()}break;\n    case "pilot-mine":S.pilot=S.pilot||{};S.pilot.mine=!S.pilot.mine;loadPilot();break;\n    case "consent":`);
R(`  h+='<section class="sheet stack"><div class="stack-s"><p class="h3">A copy of your data</p>`,`  if(S.isAdmin)h+='<button class="btn block" data-a="pilot">Pilot numbers</button>';\n  h+='<section class="sheet stack"><div class="stack-s"><p class="h3">A copy of your data</p>`);

fs.writeFileSync('public/index.html',s);
const EXPECT='35dee41e03cf8879e379c3c340f3106a22cbd7c3';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v11 ok',h(s),s.length);
