const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='f7a51d75f598e4891479edfe80469ad981ab224d')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+String(a).slice(0,70));s=s.split(a).join(b)}
// ---- v18: home shows where each case stands, not what kind it is ----

// the question a passed promise asks, in the words of that promise
R(`function phaseTitle(p){`,`function askFor(p){
  var x=(p.said||"")+" "+(p.party||"");
  if(/\\b(engineer|visit|come|coming|call round|arrive between|technician|plumber|electrician|fitter|repair ?man|delivery|deliver)\\b/i.test(x))return ["Did they come?","They came","Nobody came"];
  if(/\\b(refund|money|pay|paid|payment|credit|transfer|reimburse)/i.test(x))return ["Has the money arrived?","It arrived","Not yet"];
  if(p.by)return ["Has it happened?","Yes","Not yet"];
  return ["Did it happen?","Yes","No"];
}
function putDown(p){
  var w=window_(p);if(!w)return "";var n=new Date();
  if(p.by||p.allDay)return "You can put this down until "+fmtDay(w.start)+".";
  return "You can put this down until "+(sameDay(w.end,n)?fmtTime(w.end):fmtDay(w.end)+", "+fmtTime(w.end))+".";
}
function phaseTitle(p){`);
R(`  if(ph==="check")return p.by?"Has it happened?":"Did it happen?";`,`  if(ph==="check")return askFor(p)[0];`);

// the card: title, then who has the ball; a passed promise can be answered from the list
R(`function slip(t){
  var s=state(t),p=openPromise(t),cls=(s==="due"||s==="waitdue")?"pink":s==="waiting"?"yellow":s==="done"?"grey":"";
  var kind=MODE_LABEL[t.mode];
  var left="",right="";`,`function slip(t){
  var s=state(t),p=openPromise(t),cls=(s==="waiting"||s==="waitdue")?"yellow":s==="done"?"grey":"needs";
  var left="",right="",body="",acts="";`);
R(`  else if(p){left='<span class="flag">'+esc(phaseTitle(p))+'</span>';right=esc(whenText(p))+(p.ref?" · "+esc(p.ref):"")}`,`  else if(p){var pph=phase(p),who=p.party||"them";
    if(pph==="check"){var q=askFor(p);left='<span class="flag">'+esc(q[0])+'</span>';right=esc(who)+" · "+esc(whenText(p));
      acts='<div class="slip-acts" role="group" aria-label="'+esc(q[0])+'"><button class="btn" data-a="home-ans" data-v="kept" data-id="'+t.id+'">'+esc(q[1])+'</button><button class="btn" data-a="home-ans" data-v="missed" data-id="'+t.id+'">'+esc(q[2])+'</button><button class="btn" data-a="home-ans" data-v="rebook" data-id="'+t.id+'">They rescheduled</button></div>'}
    else if(pph==="nodate"){left='<span class="flag">No date yet</span>';right="Ask "+esc(who)+" for one"}
    else if(pph==="now"){left='<span class="flag">Happening now</span> · '+esc(who);right=esc(whenText(p))+(p.ref?" · "+esc(p.ref):"")}
    else{left='<span class="flag">Waiting on '+esc(who)+'</span>';right=esc(whenText(p))+(p.ref?" · "+esc(p.ref):"");body=putDown(p)}}`);
R(`  return '<button class="slip '+cls+'" data-a="open" data-id="'+t.id+'"><div class="slip-main"><span class="slip-kind">'+kind+'</span><span class="slip-title">'+esc(t.title)+'</span></div><div class="slip-stub"><span>'+(s==="done"?esc(left):left)+'</span><span class="mono">'+right+'</span></div></button>';`,
`  var inner='<div class="slip-main"><span class="slip-title">'+esc(t.title)+'</span></div><div class="slip-stub"><span>'+(s==="done"?esc(left):left)+'</span><span class="mono">'+right+'</span></div>'+(body?'<p class="slip-body">'+esc(body)+'</p>':'');
  if(acts)return '<div class="slip '+cls+'"><button class="slip-open" data-a="open" data-id="'+t.id+'">'+inner+'</button>'+acts+'</div>';
  return '<button class="slip '+cls+'" data-a="open" data-id="'+t.id+'">'+inner+'</button>';`);
R(`  if(t.mode==="do")return "Next: decide what’s next";`,`  if(t.mode==="do")return "What’s the next step?";`);

// answering from the list opens the case, so it still counts as coming back, and a miss goes straight to chasing
R(`    case "open":go({name:"task",id:b.getAttribute("data-id"),panel:null});break;`,`    case "open":go({name:"task",id:b.getAttribute("data-id"),panel:null});break;
    case "home-ans":{var hid=b.getAttribute("data-id"),hv=b.getAttribute("data-v");S.retSrc="home";go({name:"task",id:hid,panel:null});var hb=document.querySelector('.promise [data-a="'+hv+'"]');if(hb)hb.click();break}
    case "compose":S.composeOpen=true;render();var cf=$("#f-case");if(cf)cf.focus();break;
    case "inbox-add":{var xit=(S.inbox||[]).filter(function(x){return x.id===b.getAttribute("data-id")})[0],xt=task(b.getAttribute("data-t"));if(xit&&xt){var xop=openPromise(xt);S.view={name:"task",id:xt.id,panel:"promise"};S.draft=inboundDraft(xit);if(xop)S.draft.replaces=xop.id;render();window.scrollTo(0,0)}break}`);
R(`function go(view){S.view=view;S.draft={};render();window.scrollTo(0,0)}`,`function go(view){if(view.name!=="home")S.composeOpen=false;S.view=view;S.draft={};render();window.scrollTo(0,0)}`);

// home order: cases first, the new-case box folds away once there is something to hold
R(`  var entryFirst=!yours.length;
  if(!S.tasks.length&&S.loaded)h+=art("hero-case","hero",true);
  if(entryFirst)h+=caseEntry();
  h+=anonNote();
  h+=inboxBlock();`,`  var active=yours.length+waiting.length+upcoming.length,entryFirst=!active&&S.loaded;
  if(entryFirst)h+=art("hero-case","hero",true);
  if(entryFirst)h+=caseEntry();
  h+=anonNote();`);
R(`    if(!yours.length&&held)h+='<section class="calm stack-s">'+art("state-waiting","context")+'<p class="h2">Nothing needs you right now.</p>`,`    if(!yours.length&&held)h+='<section class="calm stack-s">'+art("state-waiting","state")+'<p class="h2">Nothing needs you right now.</p>`);
R(`    h+=group("Needs you",yours);
    if(!entryFirst)h+=caseEntry();
    h+=group("Waiting",waiting,yours.length?art("state-waiting","group"):"");
    h+=group("Coming up",upcoming);`,`    h+=group("Needs you",yours);
    h+=inboxBlock();
    h+=group("Waiting",waiting,yours.length?art("state-waiting","group"):"");
    h+=group("Coming up",upcoming);
    if(!entryFirst){
      var answering=yours.some(function(x){var xp=openPromise(x);return xp&&!openMove(x)&&phase(xp)==="check"});
      h+='<div class="compose-wrap">'+(S.composeOpen?caseEntry():answering?'<button class="link compose-mini" data-a="compose" aria-label="Start another case">+ New case</button>':'<button class="btn block compose" data-a="compose">+ Sort something else</button>')+'</div>';
    }`);
R(`    h+='<div class="slip yellow example" aria-hidden="true"><span class="example-tag">EXAMPLE</span><div class="slip-main"><span class="slip-kind">Something’s broken · waiting on them</span><span class="slip-title">Washing machine won’t drain</span></div><div class="slip-stub"><span>Engineer visit</span><span class="mono">Tue 14:00–16:00 · A1842</span></div></div>';`,
`    h+='<div class="slip yellow example" aria-hidden="true"><span class="example-tag">EXAMPLE</span><div class="slip-main"><span class="slip-title">Washing machine</span></div><div class="slip-stub"><span><span class="flag">Waiting on Oakridge</span></span><span class="mono">Tue 14:00–16:00 · A1842</span></div></div>';`);

// forwarded email: offer it to the case it belongs to, quietly
R(`function inboxBlock(){
  if(!S.inbox||!S.inbox.length)return "";`,`function mailCase(mi){
  var open=S.tasks.filter(function(t){return state(t)!=="done"}),hit=[];
  var ws=String(mi.party||"").toLowerCase().split(/[^a-z0-9]+/).filter(function(w){return w.length>=3&&!/^(the|ltd|limited|plc|team|support|customer|customers|service|services|noreply|reply|info|hello|help|group|mail|email|and|from|care)$/.test(w)});
  open.forEach(function(t){
    var refs=(t.promises||[]).map(function(p){return (p.ref||"").toLowerCase()}).filter(Boolean);
    if(mi.ref&&refs.indexOf(String(mi.ref).toLowerCase())>=0){hit.push([t,2]);return}
    var hay=(t.title+" "+(t.promises||[]).map(function(p){return p.party||""}).join(" ")+" "+(t.call&&t.call.who||"")).toLowerCase();
    if(ws.some(function(w){return hay.indexOf(w)>=0}))hit.push([t,1]);
  });
  var top=hit.filter(function(x){return x[1]===2});if(top.length===1)return top[0][0];
  return hit.length===1?hit[0][0]:null;
}
function inboxBlock(){
  if(!S.inbox||!S.inbox.length)return "";
  var qh='<section class="stack-s inbox-q">';
  S.inbox.forEach(function(it){var mi=mailInfo(it),mt=mailCase(mi),from=mi.party?esc(mi.party):"someone";
    if(mt)qh+='<div class="note stack-s"><p><strong>You forwarded an email from '+from+'.</strong> Add this promise to <strong>'+esc(mt.title)+'</strong>?</p><div class="row"><button class="btn primary" data-a="inbox-add" data-id="'+esc(it.id)+'" data-t="'+esc(mt.id)+'">Add to '+esc(mt.title.length>28?mt.title.slice(0,27)+"…":mt.title)+'</button><button class="link" data-a="inbound" data-id="'+esc(it.id)+'">A different case</button></div></div>';
    else qh+='<div class="note stack-s"><p><strong>You forwarded an email from '+from+'.</strong> Which case is it for?</p><button class="link" data-a="inbound" data-id="'+esc(it.id)+'" style="align-self:flex-start">Choose a case</button></div>';
  });
  return qh+'</section>';`);
// keep the old list body unreachable-free: drop it
R(`  var h='<section class="stack"><div class="group-h"><h2 class="h3">From your email</h2><span class="mono muted">'+S.inbox.length+'</span></div>';
  S.inbox.forEach(function(it){var mi=mailInfo(it);
    h+='<button class="slip" data-a="inbound" data-id="'+esc(it.id)+'"><div class="slip-main"><span class="slip-kind">Forwarded '+esc(stampLabel(it.received_at))+(mi.party?" · "+esc(mi.party):"")+'</span><span class="slip-title">'+esc(it.subject||"(no subject)")+'</span></div><div class="slip-stub"><span>'+(mi.when?"Sounds like":"No date found")+'</span><span class="mono">'+esc(mi.when?mi.when.label:"")+(mi.ref?" · "+esc(mi.ref):"")+'</span></div></button>';
  });
  return h+'</section>';
}`,`}`);

// provenance, not guesswork
R(`return '<div class="suggest"><p>Sounds like '+bits+'</p><button type="button" class="btn" data-a="use-sug">Use this</button></div>';`,`return '<div class="suggest"><p><span class="prov">Sorted suggested</span> '+bits+'</p><button type="button" class="btn" data-a="use-sug">Use this</button></div>';`);
R(`return '<div class="suggest"><p>Sounds like <strong>'+esc(p.label)+'</strong></p><button type="button" class="btn" data-a="use-msug">Use this</button></div>';`,`return '<div class="suggest"><p><span class="prov">Sorted suggested</span> <strong>'+esc(p.label)+'</strong></p><button type="button" class="btn" data-a="use-msug">Use this</button></div>';`);
R(`(mi.when?"Sounds like "+esc(mi.when.label):"No date found")`,`(mi.when?'<span class="prov">Sorted suggested</span> '+esc(mi.when.label):"No date found")`);

// examples teach promises, not a to-do list
R(`For example “Landlord still hasn’t fixed the heating”, “Refund from Currys hasn’t arrived” or “Bursary documents due Friday”.`,`For example “Landlord still hasn’t fixed the heating” or “Refund from Currys hasn’t arrived”.`);
R(`ex('','Something’s broken','Washing machine won’t drain',`,`ex('','Your move','Washing machine',`);
R(`ex('','Something needs renewing','Passport',`,`ex('','Coming up','Passport',`);
R(`ex(' yellow','Contact someone','Landlord about the heating',`,`ex(' yellow','Waiting on your landlord','Heating',`);

// quiet navigation
R(`(extra||'<button class="link" data-a="data">Your data</button>')`,`(extra||'<button class="navq" data-a="data">Your data</button>')`);

R(`.slip.grey{background:var(--done);border-color:var(--rule)}`,`.slip.grey{background:var(--done);border-color:var(--rule)}
.slip.needs{background:var(--sheet);border-color:var(--rule);border-left:6px solid var(--lav)}
.slip.needs .slip-stub{border-top-color:var(--rule)}
.slip-open{display:block;width:100%;text-align:left;background:none;border:0;padding:0;color:inherit;font:inherit;cursor:pointer}
.slip-acts{display:flex;flex-wrap:wrap;gap:8px;padding:0 16px 14px}
.slip-acts .btn{flex:1 1 auto;min-height:44px}
.slip-body{margin:0;padding:0 16px 12px;font-size:16px;color:var(--ink-2)}
.navq{background:none;border:0;padding:8px 0;min-height:44px;color:var(--ink-2);font:inherit;font-size:16px;font-weight:500;cursor:pointer}
.navq:hover{color:var(--ink)}
.compose-wrap{border-top:1px solid var(--rule);padding-top:18px}
.compose{justify-content:center}
.compose-mini{font-size:16px}
.prov{font-size:13px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2);display:block}`);
R(`  --pink-edge:#D9738F;
  --done:#E3E6EA;`,`  --pink-edge:#D9738F;
  --lav:#7B68C8;
  --done:#E3E6EA;`);
R(`--yellow:#3B3514;--yellow-edge:#B89C22;--pink:#43202B;--pink-edge:#C8607D;--done:#232633;`,`--yellow:#3B3514;--yellow-edge:#B89C22;--pink:#43202B;--pink-edge:#C8607D;--done:#232633;--lav:#A99BEA;`,2);

fs.writeFileSync('public/index.html',s);
const EXPECT='a02019d301c187b542ff1db31408b76153116074';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v18 ok',h(s),s.length);
