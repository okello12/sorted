const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='e85685844d0348a06ba6852123ec0cb1100d77dd')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,90));s=s.split(a).join(b)}
function P(a,b,x){const i=s.indexOf(a),j=i<0?-1:s.indexOf(b,i+a.length);if(i<0||j<0)throw new Error('range '+i+'/'+j+': '+a);s=s.slice(0,i)+x+s.slice(j)}
function C(a,b,x){const i=s.indexOf(a),j=i<0?-1:s.indexOf(b,i+a.length);if(i<0||j<0)throw new Error('range '+i+'/'+j+': '+a);s=s.slice(0,i)+x+s.slice(j+b.length)}
// ---- v56: case detail is the story and the next move, not the application's audit log. ----

// Shared presentation helpers. All existing actions and stored case data stay unchanged.
R(`function viewTask(){`,String.raw`function case56Event(e){var em=EVRE.exec(e.label||"");return em?Object.assign({},e,{label:"Added "+em[1]+". It’s under Messages & evidence."}):e}
function case56UsefulEvent(e){
  var l=String(e&&e.label||"");
  return !/^(?:Tapped add to (?:Google )?Calendar|Email reminders (?:on|off)|Asked a helper|Shared with a helper|Brought across from the phone|End date not known yet|Renewing:|Started\. Before any advice)/i.test(l);
}
function case56Timeline(t){
  var all=(t.events||[]).slice().reverse(),useful=all.filter(case56UsefulEvent),shown=useful.slice(0,3),h='<section class="case56-section" aria-labelledby="case56-timeline"><div class="case56-section-head"><div><p class="case56-overline">Case memory</p><h2 class="h2" id="case56-timeline">Timeline</h2></div><span class="case56-count">'+useful.length+'</span></div>';
  if(shown.length){h+='<ol class="thread case56-thread">';shown.forEach(function(e){h+=evRow(case56Event(e),t)});h+='</ol>'}
  else h+='<p class="muted">No key updates yet. Sorted is still keeping the full record.</p>';
  if(all.length>shown.length){h+='<details class="case56-fold"><summary><span>Full history</span><span class="case56-summary-note">'+all.length+' event'+(all.length===1?'':'s')+'</span></summary><div class="case56-fold-body"><ol class="thread">';all.forEach(function(e){h+=evRow(case56Event(e),t)});h+='</ol></div></details>'}
  return h+'</section>';
}
function case56Evidence(t,s){
  var ev=evidenceOf(t),h='<section class="case56-section" aria-labelledby="case56-evidence"><div class="case56-section-head"><div><p class="case56-overline">Keep the proof together</p><h2 class="h2" id="case56-evidence">Messages & evidence</h2></div>'+(ev.length?'<span class="case56-count">'+ev.length+'</span>':'')+'</div>';
  if(s!=="done"&&S.view.panel!=="paste")h+='<button class="link case56-add" data-a="panel" data-p="paste">Paste a message they sent</button>';
  if(ev.length){function item(x){return '<li class="ev-item"><div class="ev-top"><span class="ev-src">'+esc(EVSRC[x.src]||"Message")+'</span><time datetime="'+esc(x.at)+'">'+esc(stampLabel(x.at))+'</time></div><p class="ev-text">“'+esc(x.text)+'”</p></li>'}h+='<ol class="ev-list">'+ev.slice(0,2).map(item).join("")+'</ol>';if(ev.length>2)h+='<details class="case56-fold"><summary><span>More evidence</span><span class="case56-summary-note">'+(ev.length-2)+' more</span></summary><div class="case56-fold-body"><ol class="ev-list">'+ev.slice(2).map(item).join("")+'</ol></div></details>'}
  else h+='<p class="muted">Nothing added yet. Messages, screenshots and documents you bring into this case stay with it.</p>';
  return h+'</section>';
}
function case56ReminderStatus(t){
  var c=calPlan(t),x=[];
  if(t.emailRemind&&S.user&&S.user.email&&S.emailReady)x.push("Email");
  if(c&&t.calAt&&t.calFor===c.uid)x.push("calendar");
  return x.length?x.join(" + ")+" · Manage":"Manage";
}
function case56ReminderFold(t,body){return body?'<details class="case56-fold case56-reminders"><summary><span>Reminders</span><span class="case56-summary-note">'+esc(case56ReminderStatus(t))+'</span></summary><div class="case56-fold-body">'+body+'</div></details>':""}
function case56Sharing(t){
  var hp=S.helpers&&S.helpers[t.id],status=!t.shareToken?"Not shared":hp&&hp.status==="confirmed"?"Helper connected":hp&&hp.status==="pending"?"Awaiting helper":"Shared with a helper";
  var h='<details class="case56-fold case56-sharing"><summary><span>Sharing</span><span class="case56-summary-note">'+esc(status)+'</span></summary><div class="case56-fold-body stack-s">';
  if(!t.shareToken)h+='<p>Share this problem, not your whole list.</p>';
  h+='<button class="btn block" data-a="share">'+(t.shareToken?"Copy the helper link again":"Copy a link for someone helping you")+'</button>';
  if(t.shareToken&&S.shareBusy!==t.id){var waMsg="I’m keeping track of a problem on Sorted. This link shows you where it’s up to: "+location.origin+"/?share="+t.shareToken;h+='<a class="btn block wa" data-a="wa-share" href="https://wa.me/?text='+encodeURIComponent(waMsg)+'" target="_blank" rel="noopener">Send the link on WhatsApp</a>'}
  h+='<p class="muted case56-small">They see this case only. They can’t change it or see the rest of your list. The link stops after 30 days without a case change, or when you switch it off.</p>';
  if(t.shareToken)h+='<button class="link" data-a="unshare" style="text-align:left">Switch the helper link off</button>';
  h+=helperBlock(t);
  if(S.view.copyText)h+='<textarea class="copybox" id="copyfallback" readonly>'+esc(S.view.copyText)+'</textarea><p class="muted case56-small">Copy this by hand. Your browser blocked the copy button.</p>';
  return h+'</div></details>';
}
function case56More(t,s){
  if(t.example&&s==="done")return "";
  var h='<details class="case56-fold case56-more"><summary><span>More</span><span class="case56-summary-note">Finish or manage this case</span></summary><div class="case56-fold-body stack-s">';
  if(s!=="done"&&S.view.panel!=="done")h+='<button class="link" data-a="panel" data-p="done">Mark this finished</button>';
  if(!t.example&&S.view.panel!=="delcase")h+='<button class="link" data-a="panel" data-p="delcase" style="align-self:flex-start;color:var(--danger)">Delete this case</button>';
  return h+'</div></details>';
}
function viewTask(){`);

// The title is presentation-clean, just as it is on Home.
R(`<main class="stack fade" style="margin-top:8px;gap:20px">`,`<main class="case56 stack fade" style="margin-top:8px;gap:20px">`);
R(`<h1 class="h1">'+esc(t.title)+'</h1>`,`<h1 class="h1 case56-title">'+esc(home54Title(t))+'</h1>`);

// The case body now shows evidence, a meaningful timeline, compact sharing, then secondary controls.
P(`  h+=evidenceBlock(t);`,`  h+='<section class="stack-s"><hr class="cut">';`,`  h+=case56Evidence(t,s);\n  h+=case56Timeline(t);\n\n`);
C(`  h+='<section class="stack-s"><hr class="cut">';`,`  h+='</section></main>';`,`  h+=case56Sharing(t);\n  h+=case56More(t,s);\n  h+='</main>';`);

// Your own next action should look like one next action, not five repeated labels.
P(`function moveCard(t,m){`,`function movedCard(t){`,String.raw`function moveCard(t,m){
  var ph=phase(m),hot=ph!=="later"&&ph!=="nodate",a=moveAct(m.what),h='<section class="case56-next '+(hot?'hot':'')+'">';
  h+='<div class="case56-next-head"><p class="case56-overline">Next</p><h2 class="h2">'+esc(m.what||moveTitle(m))+'</h2>'+(m.dueAt?'<p class="case56-date">'+esc(whenText(m))+'</p>':'<p class="case56-date">No date set</p>')+'</div>';
  h+='<button class="btn primary block" data-a="move-done">'+esc(a.done)+'</button>';
  h+='<div class="case56-inline-actions"><button class="link" data-a="move-rebook">Change date</button><button class="link" data-a="move-drop">Drop it</button></div>';
  if(ph!=="check"){var sr=soonReminders(t);h+=case56ReminderFold(t,sr)}
  return h+'</section>';
}
`);

// Renewal guidance stays useful but no longer takes over the whole case.
P(`function renewCard(t){`,`function renewedForm(t){`,String.raw`function renewCard(t){
  var r=t.renew,info=rinfo(r),rp=rphase(r),sbd=startBy(r),h='',date=r.expiry?fmtDay(dayEnd(r.expiry)):"";
  var head=rp==="upcoming"?"Start by "+fmtDay(sbd):rp==="now"?"Renew now":rp==="expired"?(date?"Expired "+date:"Expired"):"Add the expiry date";
  h+='<section class="case56-renew-state '+(rp==="expired"?'expired':'')+'"><p class="case56-overline">'+esc(rname(r))+'</p><h2 class="h2">'+esc(head)+'</h2>';
  if(rp==="upcoming")h+='<p class="muted">Nothing to do yet. Sorted will bring this back when it is time to start.</p>';
  if(r.applied)h+='<p class="muted">Application sent. '+(openPromise(t)?"Sorted is holding the expected date.":"Add when it should arrive and Sorted can hold that too.")+'</p>';
  if(rp==="unknown")h+='<form class="row case56-date-form" data-f="rdate">'+dateField("f-expiry2","expiry","Date it ends","",-2,12)+'<button class="btn" type="submit">Save</button></form>';
  if(rp==="upcoming"){var cb=calBlock(t);h+=case56ReminderFold(t,cb)}
  h+='</section>';

  h+='<section class="sheet case56-official stack">';
  if(info){
    var gov=/gov\.uk/i.test(info.url||"");
    h+='<div class="case56-official-main"><div class="stack-s"><p class="case56-overline">Official route</p><h2 class="h2">'+(gov?'Renew on GOV.UK':'Use the official service')+'</h2><p class="muted">Use the official service. Avoid unexpected renewal links.</p></div><a class="btn primary block" href="'+info.url+'" target="_blank" rel="noopener noreferrer">'+(gov?'Open GOV.UK ↗':'Open official page ↗')+'</a></div>';
    if(info.extra||info.need.length||info.note){h+='<details class="case56-fold"><summary><span>More official guidance</span><span class="case56-summary-note">What you may need</span></summary><div class="case56-fold-body stack-s">';if(info.extra)h+='<a class="link" href="'+info.extra[0]+'" target="_blank" rel="noopener noreferrer">'+esc(info.extra[1])+' ↗</a>';if(info.need.length)h+='<div class="stack-s"><p style="font-weight:600">You’ll need</p><ul class="stack-s case56-list">'+info.need.map(function(x){return '<li>'+esc(x)+'</li>'}).join("")+'</ul></div>';if(info.note)h+='<p class="note">'+esc(info.note)+'</p>';h+='</div></details>'}
    h+='<p class="case56-trust"><strong>Use the official site.</strong> Other sites may charge extra. Don’t follow renewal links you weren’t expecting.</p>';
  }else if(r.how==="self"){
    h+='<div class="case56-official-main"><div class="stack-s"><p class="case56-overline">Official route</p><h2 class="h2">Renew with '+esc(r.provider||"them")+'</h2><p class="muted">Use the website or account you already trust.</p></div></div><p class="case56-trust">Go to the provider yourself rather than following an unexpected renewal link.</p>';
  }else{
    h+='<div class="stack-s"><p class="case56-overline">Next contact</p><h2 class="h2">Renew with '+esc(r.provider||"them")+'</h2><p class="muted">Use the account, letter or contract you already have.</p></div>';
    if(t.call)h+='<p class="note">'+esc(ch(t.call.via).card)+' is ready: '+esc(t.call.ask)+'</p>';
    h+='<button class="btn '+(t.call?'':'primary ')+'block" data-a="panel" data-p="call">'+(t.call?'Edit what to ask':'Get in touch with '+esc(r.provider||"them"))+'</button>';
    if(t.call)h+='<button class="btn primary block" data-a="panel" data-p="promise">'+ch(t.call.via).log+'</button>';
  }
  if(r.kind==="visa"){
    var ref=localRef(t.id);
    h+='<details class="case56-fold"><summary><span>Visa details</span><span class="case56-summary-note">Optional reference</span></summary><div class="case56-fold-body stack-s"><label class="f">Your '+(r.visa==="student"?'CAS':r.visa==="skilled"?'certificate of sponsorship':'reference')+' number <span class="hint">Optional. Stays on this phone only. It isn’t saved to Sorted’s servers or shown to helpers.</span><input type="text" id="f-localref" class="mono" autocomplete="off" value="'+esc(ref)+'"></label><button class="btn" data-a="save-localref">Keep it on this phone</button><p class="muted case56-small">Sorted doesn’t give immigration advice. For advice, speak to your university’s international student team or a regulated immigration adviser.</p></div></details>';
  }
  h+='<div class="row eq case56-renew-actions">'+(r.applied?'':'<button class="btn" data-a="applied">I’ve applied</button>')+'<button class="btn" data-a="panel" data-p="renewed">It’s renewed</button></div>';
  if(r.applied&&!openPromise(t))h+='<button class="btn block" data-a="panel" data-p="promise">When should it arrive?</button>';
  return h+'</section>';
}
`);

R(`</style>\n\n</head>`,String.raw`/* v56 case detail: the next move first, the system machinery folded away */
.case56{padding-bottom:12px}
.case56-title{font-size:clamp(31px,8vw,40px)}
.case56-overline{font-size:12px;font-weight:800;letter-spacing:.13em;text-transform:uppercase;color:var(--ink-2);margin:0 0 3px}
.case56-next{display:flex;flex-direction:column;gap:13px;background:var(--sheet);border:1.5px solid var(--rule);border-left:5px solid var(--lav);border-radius:16px;padding:16px;box-shadow:0 8px 24px rgba(20,23,38,.055)}
.case56-next.hot{border-left-color:var(--pink-edge);background:linear-gradient(145deg,var(--sheet),color-mix(in srgb,var(--pink) 26%,var(--sheet)))}
.case56-next-head{display:flex;flex-direction:column;gap:4px}
.case56-date{font-size:16px;color:var(--ink-2);margin-top:2px}
.case56-inline-actions{display:flex;gap:22px;align-items:center;flex-wrap:wrap}
.case56-inline-actions .link{font-size:16px;min-height:42px}
.case56-section{display:flex;flex-direction:column;gap:12px}
.case56-section-head{display:flex;align-items:end;justify-content:space-between;gap:14px}
.case56-count{display:grid;place-items:center;min-width:29px;height:29px;padding:0 8px;border-radius:999px;background:var(--carbon-soft);color:var(--carbon);font:700 13px/1 var(--mono)}
.case56-add{align-self:flex-start}
.case56-thread li{padding:11px 0}
.case56-fold{border:1px solid var(--rule);border-radius:12px;background:var(--sheet);overflow:hidden}
.case56-fold>summary{list-style:none;display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:52px;padding:11px 14px;cursor:pointer;font-weight:700;color:var(--ink)}
.case56-fold>summary::-webkit-details-marker{display:none}
.case56-fold>summary:after{content:'+';font-size:22px;line-height:1;color:var(--carbon);margin-left:4px}
.case56-fold[open]>summary:after{content:'−'}
.case56-summary-note{margin-left:auto;color:var(--ink-2);font-size:14px;font-weight:500;text-align:right}
.case56-fold-body{border-top:1px solid var(--rule);padding:14px}
.case56-small{font-size:15px}
.case56-sharing,.case56-more{background:transparent}
.case56-sharing>summary,.case56-more>summary{background:var(--sheet)}
.case56-reminders{margin-top:1px;background:transparent}
.case56-reminders .case56-fold-body{background:var(--paper)}
.case56-renew-state{display:flex;flex-direction:column;gap:6px;padding:14px 16px;border:1.5px solid var(--rule);border-left:5px solid var(--lav);border-radius:14px;background:var(--sheet)}
.case56-renew-state.expired{border-left-color:var(--pink-edge);background:color-mix(in srgb,var(--pink) 42%,var(--sheet))}
.case56-date-form{align-items:flex-end;margin-top:8px}
.case56-official{padding:16px;gap:14px;border-radius:14px}
.case56-official-main{display:flex;flex-direction:column;gap:12px}
.case56-official-main .btn{width:100%}
.case56-trust{font-size:15px;color:var(--ink-2);padding:10px 12px;border-radius:9px;background:var(--paper)}
.case56-list{margin:0;padding-left:1.15em}
.case56-renew-actions{padding-top:1px}
.case56 .ev-item{border-radius:10px}
@media (max-width:520px){
  .case56-next{padding:14px;gap:11px}
  .case56-fold>summary{padding:10px 12px}
  .case56-summary-note{max-width:52%;font-size:13px}
  .case56-official{padding:14px}
}
@media (prefers-reduced-motion:no-preference){
  .case56-next,.case56-renew-state,.case56-official{animation:case56In .28s ease both}
}
@media (prefers-reduced-motion:reduce){.case56-next,.case56-renew-state,.case56-official{animation:none!important}}
@keyframes case56In{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
</style>

</head>`);

fs.writeFileSync('public/index.html',s);
const EXPECT='';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v56 ok',h(s),s.length);
