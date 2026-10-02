const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='f6089c442879405b3c124315d5e0befac2ce98e2')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v75: consolidate the case UI around the live case state. Keep the current move first, fold the record and tools,
// keep a confirmed promise above email setup, add context to replies, and make parking / research prompts fit the case. ----
R('var PLANS=["Not sure yet","Try to fix it myself","Call someone","Leave it for now"];',
`var PLANS=["Not sure yet","Try to fix it myself","Call someone","Leave it for now"];
function planChoices(mode,title){
  var x=String(title||"").toLowerCase();
  if(mode==="fix")return ["Not sure yet","Try a safe check","Contact whoever is responsible","Leave it for now"];
  if(mode==="renew")return ["Not sure yet","Check the official renewal route","Check what I need first","Leave it for now"];
  if(mode==="do")return ["Not sure yet","Do it now","Check the deadline","Leave it for now"];
  if(/refund|money|payment|chargeback|repay/.test(x))return ["Not sure yet","Ask where the refund is","Contact them","Leave it for now"];
  return ["Not sure yet","Contact them","Check what they’ve already said","Leave it for now"];
}`);
R('if(t.mode!=="do"&&t.baseline)track("baseline_action_recorded",t,{choice:PLANS.indexOf(t.baseline)>=0?t.baseline:"own words"});',
  'if(t.mode!=="do"&&t.baseline)track("baseline_action_recorded",t,{choice:planChoices(t.mode,t.title).indexOf(t.baseline)>=0?t.baseline:"own words"});');
R('    h+=\'<div class="chips" role="group" aria-label="Quick answers">\';\n    PLANS.forEach(function(p){h+=\'<button type="button" class="chip" data-a="plan" data-v="\'+esc(p)+\'" aria-pressed="\'+(d.baseline===p)+\'">\'+esc(p)+\'</button>\'});\n    h+=\'</div>\';\n    h+=\'<label class="f">Or in your own words<textarea id="f-baseline" name="baseline" rows="3">\'+(PLANS.indexOf(d.baseline)<0?esc(d.baseline):"")+\'</textarea></label>\';',
`    var choices=planChoices(mode,d.title);
    h+='<div class="chips" role="group" aria-label="Quick answers">';
    choices.forEach(function(p){h+='<button type="button" class="chip" data-a="plan" data-v="'+esc(p)+'" aria-pressed="'+(d.baseline===p)+'">'+esc(p)+'</button>'});
    h+='</div>';
    h+='<label class="f">Or in your own words<textarea id="f-baseline" name="baseline" rows="3">'+(choices.indexOf(d.baseline)<0?esc(d.baseline):"")+'</textarea></label>';`);
R(`function anonNote(){
  if(!S.user||S.user.email||!S.tasks.length)return "";
  return '<div class="note stack-s"><p><strong>Without an email, only this phone can open your cases.</strong> They’re saved on Sorted’s servers, but if you clear this browser or change phone, they can’t be recovered. Add your email to keep them and get reminders.</p><button class="link" data-a="go-claim-home" style="align-self:flex-start">Add my email</button></div>';
}`,
`function anonNote(){
  if(!S.user||S.user.email||!S.tasks.length)return "";
  if(S.anonWarnFull===undefined){var seen=false;try{seen=localStorage.getItem("sorted.anonWarnSeen")==="1";if(!seen)localStorage.setItem("sorted.anonWarnSeen","1")}catch(e){}S.anonWarnFull=!seen}
  if(S.anonWarnFull)return '<div class="note stack-s"><p><strong>Without an email, only this phone can open your cases.</strong> They’re saved on Sorted’s servers, but if you clear this browser or change phone, they can’t be recovered. Add your email to keep them and get reminders.</p><button class="link" data-a="go-claim-home" style="align-self:flex-start">Add my email</button></div>';
  return '<div class="case75-email-slim"><span>This phone only. Add an email for reminders and recovery.</span><button class="link" data-a="go-claim-home">Add email</button></div>';
}`);
R(`  var h='<section class="sheet stack" id="claim"><div class="stack-s"><p class="eyebrow">Keep this safe</p><h2 class="h2">'+(day?"Want me to hold this until "+esc(day)+"?":"Keep your cases safe")+'</h2><p>Add your email and Sorted will remind you when it matters. It also keeps your cases if you lose or change your phone.</p></div>';`,
`  var h='<section class="sheet stack" id="claim"><div class="stack-s"><p class="eyebrow">Keep this safe</p><h2 class="h2">'+(p?"Add email reminders?":day?"Want me to hold this until "+esc(day)+"?":"Keep your cases safe")+'</h2><p>'+(p?"This promise is already saved. Add your email and Sorted can remind you, and you can recover your cases on another phone.":"Add your email and Sorted will remind you when it matters. It also keeps your cases if you lose or change your phone.")+'</p></div>';`);
R(`+'<button class="btn primary block" type="submit">'+(day?"Hold it for me":"Add my email")+'</button></form>';`,
  `+'<button class="btn primary block" type="submit">'+(p?"Add my email":day?"Hold it for me":"Add my email")+'</button></form>';`);
R('function home44Spot(t){',
`function case75TitleParts(t){
  var x=String(t.title||"").replace(/^\\s*TEST:\\s*/i,"").trim();
  x=x.replace(/\\s+(?:today|tomorrow)(?:\\s+by\\s+.+)?$/i,"").trim();
  var m=/^(.*?)[\\s]*[·•]\\s*([A-Z0-9][A-Z0-9-]{3,})$/i.exec(x),ref="";
  if(m){x=m[1].trim();ref=m[2]}
  if(x.length>48)x=x.slice(0,47).replace(/\\s+\\S*$/,"")+"…";
  return {title:x||"Untitled case",ref:ref};
}
function case75HeaderRef(t){
  var z=case75TitleParts(t);if(z.ref)return z.ref;var p=openPromise(t);if(p&&p.ref)return p.ref;
  var f=t&&t.cf&&t.cf.f&&t.cf.f.ref;if(f&&f.st==="confirmed")return f.v;
  return t&&t.facts&&t.facts.ref?t.facts.ref:"";
}
function case75PromiseContext(t){
  var a=(t&&t.promises)||[],p=openPromise(t);if(!p&&a.length)p=a[a.length-1];if(!p)return "";
  var lab=p.src==="parking"?"Sorted was waiting for":"They said";
  return '<div class="case75-promise-context"><p class="case56-overline">What Sorted was holding</p><p><strong>'+esc(lab+": "+p.said)+'</strong></p><p class="mono">'+esc(whenText(p))+(p.ref?' · Ref '+esc(p.ref):'')+'</p></div>';
}
function case75Group(title,note,body,cls){
  if(!body)return "";return '<details class="case75-group '+(cls||"")+'"><summary><span class="case75-group-copy"><strong>'+esc(title)+'</strong><small>'+esc(note)+'</small></span></summary><div class="case75-group-body stack">'+body+'</div></details>';
}
function case75ParkingPending(t){return !!(t&&t.cf&&t.cf.later&&cfProposed(t).length&&!pkOn(t))}
function case75ParkingPendingCard(t){
  var n=cfProposed(t).length;
  return '<section class="case56-next case75-parking-pending"><div class="case56-next-head"><p class="case56-overline">Parking notice</p><h2 class="h2">Check the notice details when you’re ready</h2></div><p>Sorted found '+n+' detail'+(n===1?'':'s')+'. Nothing counts until you confirm it.</p><button class="btn primary block" data-a="cf-show">Check the details</button></section>';
}
function case75Group(title,note,body,cls){
  if(!body)return "";return '<details class="case75-group '+(cls||"")+'"><summary><span class="case75-group-copy"><strong>'+esc(title)+'</strong><small>'+esc(note)+'</small></span></summary><div class="case75-group-body stack">'+body+'</div></details>';
}
function case75Secondary(t,s){
  loadScores();loadCaseExtras(t);var happened="",tools="",m=t.promises.filter(function(x){return x.status==="missed"});
  if(m.length){happened+='<section class="stack-s"><h2 class="h3">Promises they didn’t keep</h2>';m.forEach(function(x){happened+='<p class="missed"><s>'+esc(x.said)+'</s><br><span class="mono">'+esc(whenText(x))+(x.ref?" · "+esc(x.ref):"")+'</span> · '+esc(x.party||"")+'</p>'});happened+='</section>'}
  if(s!=="done")happened+=rsBlock(t)+pkDatesBlock(t);
  happened+=memBlock(t)+cfBlock(t)+case56Evidence(t,s)+case56Timeline(t);
  tools+=staleCal(t,s)+lettersBlock(t,s);
  if(t.mode==="fix"&&t.fix.step==="done"&&s!=="done")tools+='<section class="stack-s"><button class="link" data-a="summary" style="align-self:flex-start">'+(S.view.panel==="summary"?"Hide the summary":"Copy a summary for whoever fixes it")+'</button>'+(S.view.panel==="summary"?'<textarea class="copybox" id="sumtext" readonly>'+esc(repairerSummary(t))+'</textarea><button class="btn primary block" data-a="copy-summary">Copy summary</button>':"")+'</section>';
  if(s!=="done")tools+=rtBlock(t);
  tools+=xrBlock(t)+scoreBlock(t);
  if(s!=="done"&&!openMove(t)&&t.mode!=="do")tools+='<section class="stack-s"><button class="link" data-a="panel" data-p="move" style="align-self:flex-start">Remind me to do something</button></section>';
  tools+=packLink(t)+case56Sharing(t)+case56More(t,s);
  return case75Group("What’s happened","Messages, dates and timeline",happened,"case75-happened")+case75Group("Tools for this case","Advice, sharing and controls",tools,"case75-tools");
}
function home44Spot(t){`);
R(`  h+='<div class="home44-spot-top"><div><h2 class="home44-spot-title" id="home44-spot-title">'+esc(home54Title(t))+'</h2></div></div>';`,
`  var ht=case75TitleParts(t);h+='<div class="home44-spot-top"><div><h2 class="home44-spot-title" id="home44-spot-title">'+esc(ht.title)+'</h2>'+(ht.ref?'<span class="case75-row-ref">Ref '+esc(ht.ref)+'</span>':'')+'</div></div>';`);
R(`function home44Row(t,kind){
  var p=openPromise(t),s=state(t),meta=home44Meta(t),note="",badge="";`,
`function home44Row(t,kind){
  var p=openPromise(t),s=state(t),meta=home44Meta(t),note="",badge="",ht=case75TitleParts(t);`);
R(`  return '<button class="home44-row '+kind+'" data-a="open" data-id="'+t.id+'"><span class="home44-row-copy"><span class="home44-row-title">'+esc(home54Title(t))+'</span><span class="home44-row-meta">'+esc(meta)+'</span>'+(note?'<span class="home44-row-note">'+esc(note)+'</span>':'')+'</span>'+(badge?'<span class="home44-pill">'+esc(badge)+'</span>':'<span></span>')+'<span class="home44-chevron" aria-hidden="true">›</span></button>';`,
`  return '<button class="home44-row '+kind+'" data-a="open" data-id="'+t.id+'"><span class="home44-row-copy"><span class="home44-row-title">'+esc(ht.title)+'</span>'+(ht.ref?'<span class="case75-row-ref">Ref '+esc(ht.ref)+'</span>':'')+'<span class="home44-row-meta">'+esc(meta)+'</span>'+(note?'<span class="home44-row-note">'+esc(note)+'</span>':'')+'</span>'+(badge?'<span class="home44-pill">'+esc(badge)+'</span>':'<span></span>')+'<span class="home44-chevron" aria-hidden="true">›</span></button>';`);
R(`  h+='<section class="hero"><p class="eyebrow">They said Tuesday. Sorted remembers Tuesday.</p><h1 class="h1">Life gets messy.<br><em>Sorted keeps up.</em></h1><p class="lede">One calm place for problems where someone else owes you the next move. You don’t have to keep remembering whether they got back to you.</p><p class="pilot-line">A UK research pilot. You can start without an account. Your cases stay private, and idle cases are deleted after 90 days (30 if you haven’t added an email).</p>'+('<a class="btn primary" href="#start" style="align-self:flex-start">Get something sorted →</a>'+'<img class="hero-art" src="/art/hero-case.webp" width="640" height="410" alt="A case folder with a washing machine, a clock and a phone" fetchpriority="high">')+'</section>'+landingExamples();`,
`  h+='<section class="hero"><p class="eyebrow">Life gets messy. Sorted keeps up.</p><h1 class="h1">They said Tuesday.<br><em>Sorted remembers Tuesday.</em></h1><p class="lede">One calm place for problems where someone else owes you the next move. You don’t have to keep remembering whether they got back to you.</p><p class="pilot-line">A UK research pilot. You can start without an account. Your cases stay private, and idle cases are deleted after 90 days (30 if you haven’t added an email).</p>'+('<a class="btn primary" href="#start" style="align-self:flex-start">Get something sorted →</a>'+'<img class="hero-art" src="/art/hero-case.webp" width="640" height="410" alt="A case folder with a washing machine, a clock and a phone" fetchpriority="high">')+'</section>'+landingExamples();`);
R('  var s=state(t),p=openPromise(t);',
  '  var s=state(t),p=openPromise(t),tp=case75TitleParts(t),href=case75HeaderRef(t);');
R(`  h+='<section class="stack-s"><p class="eyebrow">'+({yours:"Needs you",waiting:"Waiting",waitdue:"Waiting",due:"Needs you",upcoming:"Coming up",done:"Done"}[s])+'</p><h1 class="h1 case56-title">'+esc(home54Title(t))+'</h1>'+hoLine(t)+'</section>'+ansBanner(t);`,
`  h+='<section class="stack-s"><p class="eyebrow">'+({yours:"Needs you",waiting:"Waiting",waitdue:"Waiting",due:"Needs you",upcoming:"Coming up",done:"Done"}[s])+'</p><h1 class="h1 case56-title">'+esc(tp.title)+'</h1>'+(href?'<p class="case75-title-ref mono">Ref '+esc(href)+'</p>':'')+hoLine(t)+'</section>'+ansBanner(t);`);
R("  if(cmc)return h+cmc+'</main>';", "  if(cmc)return h+cmc+case75Secondary(t,s)+'</main>';" );
R("  if(hoc)return h+hoc+'</main>';", "  if(hoc)return h+hoc+case75Secondary(t,s)+'</main>';" );
R("  if(rsc)return h+rsc+'</main>';", "  if(rsc)return h+rsc+case75Secondary(t,s)+'</main>';" );
R('  h+=cfc;', '  if(!case75ParkingPending(t))h+=cfc;');
R('  else if(S.view.panel==="claim"){h+=claimBlock(t)}', '  else if(S.view.panel==="claim"){if(p)h+=promiseCard(t,p);h+=claimBlock(t)}');
R(`  }else if(!p&&S.view.panel!=="call"&&S.view.panel!=="promise"&&S.view.panel!=="done"&&pbCard(t)){
    h+=pbCard(t);
  }else if(t.mode==="fix"&&t.fix.step!=="done"){`,
`  }else if(!p&&S.view.panel!=="call"&&S.view.panel!=="promise"&&S.view.panel!=="done"&&pbCard(t)){
    h+=pbCard(t);
  }else if(case75ParkingPending(t)){
    h+=case75ParkingPendingCard(t);
  }else if(t.mode==="fix"&&t.fix.step!=="done"){`);
R(`  if(s!=="done"&&!mv&&!S.view.panel&&t.mode!=="do")h+='<button class="link" data-a="panel" data-p="move" style="align-self:flex-start">Remind me to do something</button>';
`, '');
R(`  if(S.view.panel==="done")h+=doneForm(t);
  h+=staleCal(t,s);
  var m=t.promises.filter(function(x){return x.status==="missed"});
  if(m.length){h+='<section class="stack-s"><h2 class="h3">Promises they didn’t keep</h2>';m.forEach(function(x){h+='<p class="missed"><s>'+esc(x.said)+'</s><br><span class="mono">'+esc(whenText(x))+(x.ref?" · "+esc(x.ref):"")+'</span> · '+esc(x.party||"")+'</p>'});h+='</section>'}

  h+=lettersBlock(t,s);
  if(t.mode==="fix"&&t.fix.step==="done"&&s!=="done")h+='<section class="stack-s"><button class="link" data-a="summary" style="align-self:flex-start">'+(S.view.panel==="summary"?"Hide the summary":"Copy a summary for whoever fixes it")+'</button>'+(S.view.panel==="summary"?'<textarea class="copybox" id="sumtext" readonly>'+esc(repairerSummary(t))+'</textarea><button class="btn primary block" data-a="copy-summary">Copy summary</button>':"")+'</section>';

  if(s!=="done")h+=rsBlock(t)+rtBlock(t)+pkDatesBlock(t);
  loadScores();loadCaseExtras(t);
  h+=xrBlock(t);
  h+=scoreBlock(t);
  h+=memBlock(t);
  h+=cfBlock(t);
  h+=case56Evidence(t,s);
  h+=case56Timeline(t);

  h+=packLink(t);
  h+=case56Sharing(t);
  h+=case56More(t,s);`,
`  if(S.view.panel==="done")h+=doneForm(t);
  if(!S.view.panel)h+=case75Secondary(t,s);`);
R(`  return '<section class="sheet stack cm-card" aria-labelledby="cmh"><div class="stack-s"><p class="eyebrow">Their reply</p><h2 class="h2" id="cmh">A reply came in'+(x.from_domain?' from '+esc(x.from_domain):'')+'</h2><p class="muted" style="font-size:15px">Received '+esc(stampLabel(x.received_at))+'. Check it’s genuine before you rely on it: anyone can send an email.</p></div>'+(x.subject?'<p class="h3" style="margin:0">'+esc(x.subject)+'</p>':'')+'<p class="ev-text cm-body">'+esc(bd.length>600?bd.slice(0,597)+"…":bd)+'</p><button class="btn primary block" data-a="cm-add" data-id="'+esc(x.id)+'">Add it to the case</button><button class="btn block" data-a="cm-drop" data-id="'+esc(x.id)+'">It’s not about this case</button>'+(l.length>1?'<p class="muted" style="font-size:14px;margin:0">'+(l.length-1)+' more after this one.</p>':'')+'</section>';`,
`  return '<section class="sheet stack cm-card" aria-labelledby="cmh"><div class="stack-s"><p class="eyebrow">Their reply</p><h2 class="h2" id="cmh">A reply came in'+(x.from_domain?' from '+esc(x.from_domain):'')+'</h2><p class="muted" style="font-size:15px">Received '+esc(stampLabel(x.received_at))+'. Check it’s genuine before you rely on it: anyone can send an email.</p></div>'+case75PromiseContext(t)+(x.subject?'<p class="h3" style="margin:0">'+esc(x.subject)+'</p>':'')+'<p class="ev-text cm-body">'+esc(bd.length>600?bd.slice(0,597)+"…":bd)+'</p><button class="btn primary block" data-a="cm-add" data-id="'+esc(x.id)+'">Add it to the case</button><button class="btn block" data-a="cm-drop" data-id="'+esc(x.id)+'">It’s not about this case</button>'+(l.length>1?'<p class="muted" style="font-size:14px;margin:0">'+(l.length-1)+' more after this one.</p>':'')+'</section>';`);
R('  h+=rsDetail(r);', '  h+=case75PromiseContext(t)+rsDetail(r);');
R('.pb-card p{margin:0}', `.pb-card p{margin:0}
.case75-title-ref{margin:0;font-size:14px;color:var(--ink-2)}
.case75-row-ref{display:block;font-family:var(--mono);font-size:13px;color:var(--ink-2);margin-top:2px}
.case75-email-slim{display:flex;gap:12px;align-items:center;justify-content:space-between;border:1px solid var(--rule);border-radius:8px;padding:8px 12px;font-size:14px;color:var(--ink-2)}
.case75-email-slim .link{min-height:36px;padding:4px 0;flex:none}
.case75-promise-context{border-left:3px solid var(--carbon);background:var(--carbon-soft);padding:10px 12px;border-radius:0 6px 6px 0;display:flex;flex-direction:column;gap:4px}
.case75-promise-context p{margin:0}
.case75-group{border-top:1px solid var(--rule)}
.case75-group>summary{list-style:none;cursor:pointer;min-height:58px;padding:13px 2px;display:flex;align-items:center;justify-content:space-between;gap:12px}
.case75-group>summary::-webkit-details-marker{display:none}
.case75-group>summary:after{content:"+";font-size:24px;line-height:1;color:var(--ink-2)}
.case75-group[open]>summary:after{content:"−"}
.case75-group-copy{display:flex;flex-direction:column;gap:2px;text-align:left}
.case75-group-copy strong{font-size:18px}
.case75-group-copy small{font-size:14px;color:var(--ink-2);font-weight:400}
.case75-group-body{padding:4px 0 16px}
.case75-group-body>.case56-section,.case75-group-body>.stack-s,.case75-group-body>.pk-dates,.case75-group-body>.cf-facts,.case75-group-body>.rs-block{padding-top:14px;border-top:1px solid var(--rule)}
.case75-parking-pending p{margin:0}`);
fs.writeFileSync('public/index.html',s);
const EXPECT='8c72bc97ccfe09fdc30c4f25f2751c735623a1b2';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v75 ok',h(s),s.length);
