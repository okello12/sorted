/* ---------- a case starts with one sentence ---------- */
function caseMode(text){
  var s=String(text||"").toLowerCase();
  if(/\b(renew|renewal|expir|passport|mot\b|visa|brp\b|tv licen|driving licen|car tax|road tax)/.test(s))return "renew";
  if(/\b(broken|broke|not working|isn.?t working|stopped|won.?t|doesn.?t|leak|leaking|fault|faulty|error|noise|noisy|cracked|smashed|damp|mould|mold|no hot water|no heating|boiler|washing machine|dryer|fridge|freezer|dishwasher|oven|cooker|heating|shower|toilet|laptop|phone screen)\b/.test(s))return "fix";
  return "call";
}
function caseEntry(){
  var d=S.draft;
  return '<section class="stack"><h1 class="h1">What’s gone wrong?</h1><form class="stack-s" data-f="case"><label class="f"><span class="hint">Tell Sorted in one sentence.</span><textarea id="f-case" name="casetext" rows="2" placeholder="Washing machine stopped draining">'+esc(d.casetext||"")+'</textarea></label>'+(d.err&&S.view.name==="home"?'<p class="err">'+esc(d.err)+'</p>':'')+'<button class="btn primary block" type="submit">Start</button></form><p class="muted" style="font-size:15px">For example “Landlord still hasn’t fixed the heating” or “Refund from Currys hasn’t arrived”.</p></section>';
}

/* ---------- closure recap ---------- */
function recapText(t){
  var out=[t.title.replace(/[.!]+$/,"")+". Started "+fmtDay(new Date(t.created))+"."];
  t.promises.forEach(function(p){
    var st={kept:"That happened.",missed:"That didn’t happen.",replaced:"That was rescheduled.",open:""}[p.status]||"";
    out.push((p.party||"They")+" said “"+p.said.replace(/[.!]+$/,"")+"” ("+whenText(p).replace(/^By/,"by")+(p.ref?", ref "+p.ref:"")+"). "+st);
  });
  (t.moves||[]).forEach(function(m){if(m.status==="done")out.push("On "+fmtDay(new Date(m.doneAt||m.loggedAt))+": "+m.what.replace(/[.!]+$/,"")+", done.")});
  out.push("Finished "+fmtDay(new Date(t.updatedAt||t.created))+": "+String(t.outcome||"done").replace(/[.!]+$/,"")+".");
  return out.join(" ").replace(/\s+/g," ").trim();
}
function recapCard(t){
  return '<section class="sheet stack"><div class="stack-s"><p class="eyebrow">Finished</p><h2 class="h2">This one is finished.</h2><p class="h3">'+esc(t.outcome||"Done")+'</p></div><p class="note">'+esc(recapText(t))+'</p><div class="row eq"><button class="btn primary" data-a="recap-copy">Copy recap</button><button class="btn" data-a="recap-share">Share</button></div><p class="muted" style="font-size:15px">Sorted keeps this case, so it’s here if the problem comes back.</p></section>';
}

/* ---------- where each line of the story came from ---------- */
function evSource(e){
  if(/^They said: /.test(e.label))return "They said";
  if(e.kind==="return"||e.auto||/^Logged from a forwarded email|^Email reminders on \(the default\)|^Brought across/.test(e.label))return "Sorted";
  return "You";
}
function evRow(e){
  var src=evSource(e),txt=src==="They said"?e.label.replace(/^They said: /,""):e.label;
  return '<li><time datetime="'+e.at+'">'+stampLabel(e.at)+'</time><span><span class="src">'+src+'</span>'+esc(txt)+'</span></li>';
}

/* ---------- start without an email; add it when there is something to hold ---------- */
function consentBox(d){
  return '<button type="button" data-a="consent" role="checkbox" aria-checked="'+(!!d.consent)+'" style="display:flex;gap:12px;align-items:flex-start;background:none;border:0;padding:0;text-align:left"><span aria-hidden="true" style="flex:none;width:28px;height:28px;border:2px solid var(--ink);border-radius:4px;display:grid;place-items:center;font-weight:800;'+(d.consent?"background:var(--ink);color:var(--paper)":"background:var(--sheet)")+'">'+(d.consent?"✓":"")+'</span><span>I’m happy to take part in the Sorted pilot, and I’ve read how my data is handled.</span></button><button type="button" class="link" data-a="privacy" style="text-align:left">'+(d.showPrivacy?"Hide":"Read")+' how your data is handled</button>'+(d.showPrivacy?privacyBlock():"");
}
function startBlock(d){
  var h='<section class="stack-s"><a class="link" href="#" style="align-self:flex-start">← Back</a><h1 class="h2">Get something sorted</h1><p class="lede">Start now. Sorted only asks for your email when there’s something for it to remember.</p></section>';
  h+='<section class="sheet stack">'+consentBox(d)+(d.err?'<p class="err">'+esc(d.err)+'</p>':'')+'<button class="btn primary block" data-a="anon-start"'+(d.busy?" disabled":"")+'>'+(d.busy?"Starting…":"Start")+'</button></section>';
  return h+'<a class="link" href="#signin" style="align-self:flex-start">Already use Sorted? Sign in with your email</a>';
}
function claimBlock(t){
  var d=S.draft,p=t?openPromise(t):null,day=p&&p.dueAt?fmtDay(new Date(p.dueAt)):"";
  var h='<section class="sheet stack" id="claim"><div class="stack-s"><p class="eyebrow">Keep this safe</p><h2 class="h2">'+(day?"Want me to hold this until "+esc(day)+"?":"Keep your cases safe")+'</h2><p>Add your email and Sorted will remind you when it matters. It also keeps your cases if you lose or change your phone.</p></div>';
  if(d.cexists){
    h+='<p>'+esc(d.cemail)+' already has a Sorted account. Sign in with it, and Sorted will bring the cases from this phone across.</p><button class="btn primary block" data-a="claim-signin">Sign in and bring my cases</button><button class="link" data-a="claim-reset" style="text-align:left">Use a different email</button>';
  }else if(d.csent){
    h+='<p>We sent an email to <span class="mono" style="word-break:break-all">'+esc(d.cemail)+'</span>. Tap the link in it, or type the code here.</p><form class="stack-s" data-f="claimcode"><label class="f">Code from the email<input type="text" id="f-ccode" name="ccode" inputmode="numeric" autocomplete="one-time-code" maxlength="10" class="mono" style="letter-spacing:4px;font-size:22px"></label>'+(d.cerr?'<p class="err">'+esc(d.cerr)+'</p>':'')+'<button class="btn primary block" type="submit">Confirm</button></form><button class="link" data-a="claim-reset" style="text-align:left">Use a different email</button>';
  }else{
    h+='<form class="stack-s" data-f="claim"><label class="f">Your email<input type="email" id="f-cemail" name="cemail" autocomplete="email" value="'+esc(d.cemail||"")+'"></label>'+(d.cerr?'<p class="err">'+esc(d.cerr)+'</p>':'')+'<button class="btn primary block" type="submit">'+(day?"Hold it for me":"Add my email")+'</button></form>';
  }
  return h+'<button class="link" data-a="'+(t?"panel":"home")+'" data-p="" style="text-align:left">Not now</button></section>';
}
function viewClaim(){return topbar('<button class="link" data-a="home">← All tasks</button>')+'<main class="stack fade" style="margin-top:8px">'+claimBlock(null)+'</main>'}
function anonNote(){
  if(!S.user||S.user.email||!S.tasks.length)return "";
  return '<div class="note stack-s"><p><strong>Your cases are only on this phone.</strong> Add your email to keep them safe and get reminders.</p><button class="link" data-a="go-claim-home" style="align-self:flex-start">Add my email</button></div>';
}
function carryIn(){
  if(!S.user||!S.user.email)return;
  var raw=null;try{raw=localStorage.getItem("sorted.carry")}catch(e){}
  if(!raw)return;try{localStorage.removeItem("sorted.carry")}catch(e){}
  var list=[];try{list=JSON.parse(raw)||[]}catch(e){}
  list.forEach(function(ct){ct.id=uid();delete ct.shareToken;delete ct.emailRemind;ct.events=ct.events||[];ct.promises=ct.promises||[];log(ct,"Brought across from the phone you started on.");S.tasks.unshift(ct)});
  if(list.length){save();render();toast("Brought "+list.length+" case"+(list.length===1?"":"s")+" across")}
}
