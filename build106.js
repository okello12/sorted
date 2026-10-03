const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='7d20ac95de8bbe88baa1160c3bc7f6531e9d00e9')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,90));s=s.split(a).join(b)}
// ---- v106 / SEM-03: corrections for every case. Important facts get a provenance/history ledger.
// A correction is proposed from new words, then confirmed. The old current value becomes replaced, not deleted.
// Promise-date corrections are distinguished from company reschedules so outcome history stays honest. ----
const SEM=String.raw`
/* v106: universal fact history. Plain t.facts remains the compatibility/current-value view. */
function semMoney(v){if(v==null||v==='')return '';var n=String(v).replace(/[^0-9.]/g,'');if(!n)return '';return '£'+n.replace(/\.00$/,'')}
function semNorm(k,v){if(v==null)return '';v=String(v).trim();if(k==='amount')return semMoney(v);if(k==='promise_date'){var d=new Date(v);return isNaN(d)?v:d.toISOString()}return v.toLowerCase().replace(/\s+/g,' ')}
function semDay(v){var d=new Date(v);return isNaN(d)?String(v||''):fmtDay(d)}
function semShow(k,v){return k==='promise_date'?semDay(v):String(v==null?'':v)}
function semRe(v){return String(v||'').replace(/[.*+?^${}()|[\]\\]/g,'\\$&')}
function semSwap(x,a,b){if(!x||!a||semNorm('',a)===semNorm('',b))return x;try{return String(x).replace(new RegExp(semRe(a),'gi'),b)}catch(e){return x}}
function semCfVal(t,k){var f=t&&t.cf&&t.cf.f&&t.cf.f[k];return f&&f.st!=='rejected'?f.v:''}
function semCanonical(t){
  var f=t.facts||{},p=openPromise(t),out={};
  out.who=(p&&p.party)||f.party||semCfVal(t,'issuer')||(t.call&&t.call.who)||(t.fix&&t.fix.party)||'';
  out.reference=(p&&p.ref)||f.ref||semCfVal(t,'ref')||(t.fix&&t.fix.jobRef)||'';
  out.amount=f.amount!=null&&f.amount!==''?semMoney(f.amount):semCfVal(t,'amount');
  out.thing=(t.fix&&t.fix.item)||f.item||'';
  out.said=(p&&p.said)||'';
  out.promise_date=(p&&p.dueAt)||'';
  return out;
}
function semEnsure(t,refresh){
  if(!t||t.kind==='moment')return false;
  var fresh=!t.factLedger,led=t.factLedger||(t.factLedger={v:1,f:{},pending:[],rejected:[]}),now=nowIso(),cur=semCanonical(t),changed=fresh;
  led.v=1;led.f=led.f||{};led.pending=led.pending||[];led.rejected=led.rejected||[];
  Object.keys(cur).forEach(function(k){var v=cur[k];if(!v)return;var q=led.f[k];
    if(!q){led.f[k]={value:v,source:fresh?'existing case':'confirmed in Sorted',time:now,status:'confirmed',history:[]};changed=true;return}
    if(refresh&&semNorm(k,q.value)!==semNorm(k,v)){
      var hist=(q.history||[]).slice();hist.push({value:q.value,source:q.source,time:q.time,status:'replaced'});
      led.f[k]={value:v,source:'confirmed in Sorted',time:now,status:'confirmed',history:hist};changed=true;
    }
  });
  if(changed)t._dirty=true;return changed;
}
function semCurrent(t,k){semEnsure(t,false);return t.factLedger&&t.factLedger.f[k]?t.factLedger.f[k].value:''}
function semSet(t,k,v,source){
  semEnsure(t,false);var led=t.factLedger,q=led.f[k],hist=q?(q.history||[]).slice():[];
  if(q&&semNorm(k,q.value)!==semNorm(k,v))hist.push({value:q.value,source:q.source,time:q.time,status:'replaced'});
  led.f[k]={value:v,source:source||'you corrected it',time:nowIso(),status:'confirmed',history:hist};t._dirty=true;
}
function semCue(x){return /\b(?:sorry|actually|i meant|correction|correct that|rather than|instead|wasn['’]?t|was not|isn['’]?t|is not|not .{1,45}(?:it was|it is|it['’]?s)|changed it to|moved it to|rescheduled)/i.test(String(x||''))}
function semEntityAfterOld(text,old){if(!old)return '';var o=semRe(old),r1=new RegExp("(?:wasn['’]?t|was not|isn['’]?t|is not)\\s+(?:the\\s+)?"+o+"\\b[^.!?]{0,45}?(?:it\\s+)?(?:was|is|it['’]?s)\\s+(?:the\\s+)?([A-Za-z0-9][A-Za-z0-9&'’.\\-]*(?:\\s+[A-Za-z0-9][A-Za-z0-9&'’.\\-]*){0,5})","i"),m=r1.exec(text);if(!m){var r2=new RegExp("(?:it\\s+)?(?:was|is|it['’]?s)\\s+(?:the\\s+)?([A-Za-z0-9][A-Za-z0-9&'’.\\-]*(?:\\s+[A-Za-z0-9][A-Za-z0-9&'’.\\-]*){0,5})\\s*[,;]?\\s*(?:not|rather than)\\s+(?:the\\s+)?"+o+"\\b","i");m=r2.exec(text)}
  if(!m)return '';return m[1].replace(/\s+(?:actually|instead|now)$/i,'').trim()}
function semExtract(t,text){
  var out={},meta={},cf={};try{cf=caseFacts(text)||{}}catch(e){}
  if(cf.party)out.who=cf.party;if(cf.ref)out.reference=cf.ref;if(cf.amount!=null&&cf.amount!=='')out.amount=semMoney(cf.amount);
  var th='';try{th=thingOf(text)}catch(e){}if(th)out.thing=th;
  var sg=null;try{sg=readCase(text,cf)}catch(e){}if(sg){if(sg.party)out.who=sg.party;if(sg.ref)out.reference=sg.ref;if(sg.said)out.said=sg.said;if(sg.dueAt){out.promise_date=sg.dueAt;meta.promise_date={dueEnd:sg.dueEnd||null,allDay:!!sg.allDay,by:!!sg.by}}}
  var ow=semCurrent(t,'who'),ot=semCurrent(t,'thing'),x;if((x=semEntityAfterOld(text,ow)))out.who=x;if((x=semEntityAfterOld(text,ot)))out.thing=x;
  var rm=/\b(?:ref(?:erence)?|claim ref|order(?: number| no\.?)?)\s*(?:is|was|:|#)?\s*([A-Z0-9][A-Z0-9-]{2,})\b/i.exec(text);if(rm)out.reference=rm[1].toUpperCase();
  var am=/£\s?\d{1,7}(?:\.\d{1,2})?/.exec(text);if(am)out.amount=semMoney(am[0]);
  var sm=/\b(?:actually|sorry[, ]*|i meant[, ]*)(?:what\s+)?(?:they\s+)?said\s+(?:that\s+)?[“\"]?(.{3,140}?)[”\"]?(?:[.!]|$)/i.exec(text);if(sm)out.said=sm[1].trim();
  if(!out.promise_date){try{var dt=readCase('They said '+text,caseFacts('They said '+text)||{});if(dt&&dt.dueAt){out.promise_date=dt.dueAt;meta.promise_date={dueEnd:dt.dueEnd||null,allDay:!!dt.allDay,by:!!dt.by}}}catch(e){}}
  return {v:out,m:meta};
}
function semQueue(t,k,to,source,meta){var from=semCurrent(t,k);if(!from||!to||semNorm(k,from)===semNorm(k,to))return false;semEnsure(t,false);var p=t.factLedger.pending;
  if(p.some(function(q){return q.key===k&&semNorm(k,q.to)===semNorm(k,to)}))return false;
  p.push({id:uid(),key:k,from:from,to:to,source:source||'what you added',time:nowIso(),status:'proposed',meta:meta||{}});t._dirty=true;return true}
function semObserveText(t,text,source){text=String(text||'').trim();if(!t||!text||!semCue(text))return false;semEnsure(t,false);var r=semExtract(t,text),n=0;
  ['who','reference','amount','thing','said','promise_date'].forEach(function(k){if(r.v[k]&&semQueue(t,k,r.v[k],source,r.m[k]))n++});return !!n}
function semObserveForm(t,form,k){if(!t||!form)return;var structured=/^(?:what|who|call|promise|rwhat|rwho|rdate|renewed|done|cf|baseline|title|case|gi)$/;if(structured.test(k||''))return;
  var xs=form.querySelectorAll('textarea,input[type=text]'),a=[];for(var i=0;i<xs.length;i++)if(xs[i].value)a.push(xs[i].value);var text=a.join(' ');if(!semCue(text))return;
  var src=k==='paste'?'the message you pasted':k==='reply'?'the reply you added':'what you added';semObserveText(t,text,src)}
function semApplyTextFields(t,k,oldv,newv){
  var p=openPromise(t);if(k==='who'){if(p&&semNorm('who',p.party)===semNorm('who',oldv))p.party=newv;if(t.sugP&&semNorm('who',t.sugP.party)===semNorm('who',oldv))t.sugP.party=newv;if(t.call&&semNorm('who',t.call.who)===semNorm('who',oldv))t.call.who=newv;if(t.fix&&semNorm('who',t.fix.party)===semNorm('who',oldv))t.fix.party=newv;if(t.facts)t.facts.party=newv;if(t.cf&&t.cf.f&&t.cf.f.issuer&&t.cf.f.issuer.st!=='rejected')t.cf.f.issuer.v=newv;t.title=semSwap(t.title,oldv,newv)}
  else if(k==='reference'){if(p&&semNorm('reference',p.ref)===semNorm('reference',oldv))p.ref=newv;if(t.sugP&&semNorm('reference',t.sugP.ref)===semNorm('reference',oldv))t.sugP.ref=newv;if(t.fix&&semNorm('reference',t.fix.jobRef)===semNorm('reference',oldv))t.fix.jobRef=newv;if(t.facts)t.facts.ref=newv;if(t.cf&&t.cf.f&&t.cf.f.ref&&t.cf.f.ref.st!=='rejected')t.cf.f.ref.v=newv;t.title=semSwap(t.title,oldv,newv);if(t.call)t.call.ask=semSwap(t.call.ask,oldv,newv);if(p)p.said=semSwap(p.said,oldv,newv)}
  else if(k==='amount'){var num=Number(String(newv).replace(/[^0-9.]/g,''));t.facts=t.facts||{};if(!isNaN(num))t.facts.amount=num;if(t.cf&&t.cf.f&&t.cf.f.amount&&t.cf.f.amount.st!=='rejected')t.cf.f.amount.v=newv;t.title=semSwap(t.title,oldv,newv);if(t.call)t.call.ask=semSwap(t.call.ask,oldv,newv);if(p)p.said=semSwap(p.said,oldv,newv);if(t.sugP)t.sugP.said=semSwap(t.sugP.said,oldv,newv)}
  else if(k==='thing'){if(t.fix)t.fix.item=newv;t.facts=t.facts||{};t.facts.item=newv;t.title=semSwap(t.title,oldv,newv);if(t.call)t.call.ask=semSwap(t.call.ask,oldv,newv)}
  else if(k==='said'){if(p)p.said=newv;if(t.sugP)t.sugP.said=newv}
}
function semDateApply(t,q,mode){var p=openPromise(t),old=q.from,nw=q.to;if(!p||!p.dueAt){semSet(t,'promise_date',nw,mode==='reschedule'?'they changed it':'you corrected it');return}
  var od=new Date(p.dueAt),nd=new Date(nw);if(isNaN(nd))return;var delta=nd-od,oldEnd=p.dueEnd?new Date(p.dueEnd):null;
  if(mode==='reschedule'){
    p.status='replaced';p.closedAt=nowIso();p.changeKind='reschedule';var np=JSON.parse(JSON.stringify(p));np.id=uid();np.status='open';delete np.closedAt;np.loggedAt=nowIso();np.rescheduledFrom=p.id;np.dueAt=nd.toISOString();if(oldEnd)np.dueEnd=new Date(oldEnd.getTime()+delta).toISOString();t.promises.push(np);t.board='waiting';
    semSet(t,'promise_date',np.dueAt,'they changed it');log(t,'They moved it from '+semDay(old)+' to '+semDay(np.dueAt)+'.');
  }else{
    p.dueAt=nd.toISOString();if(oldEnd)p.dueEnd=new Date(oldEnd.getTime()+delta).toISOString();semSet(t,'promise_date',p.dueAt,'you corrected it');log(t,'Changed from '+semDay(old)+' to '+semDay(p.dueAt)+'. You corrected it on '+new Date().toLocaleDateString('en-GB',{day:'numeric',month:'short'})+'.');
  }}
function semApplyPending(t,mode){semEnsure(t,false);var led=t.factLedger,q=led.pending&&led.pending[0];if(!q)return;
  led.pending.shift();if(q.key==='promise_date')semDateApply(t,q,mode);else{semApplyTextFields(t,q.key,q.from,q.to);semSet(t,q.key,q.to,'you corrected it');log(t,'Changed from '+semShow(q.key,q.from)+' to '+semShow(q.key,q.to)+'. You corrected it on '+new Date().toLocaleDateString('en-GB',{day:'numeric',month:'short'})+'.')}
  t._dirty=true;save();render();toast(mode==='reschedule'?'Saved as a reschedule':'Correction saved')}
function semRejectPending(t){semEnsure(t,false);var led=t.factLedger,q=led.pending&&led.pending.shift();if(!q)return;q.status='rejected';q.rejectedAt=nowIso();led.rejected.push(q);t._dirty=true;save();render()}
function semDecorate(){if(S.view.name!=='task'||!S.view.id)return;var t=task(S.view.id);if(!t)return;var changed=semEnsure(t,true);if(changed)save();var p=t.factLedger&&t.factLedger.pending&&t.factLedger.pending[0];if(!p)return;
  var main=document.querySelector('main');if(!main||main.querySelector('.sem-correction'))return;var sec=document.createElement('section');sec.className='check stack-s sem-correction';sec.setAttribute('role','status');var old=semShow(p.key,p.from),nw=semShow(p.key,p.to),h='<p class="eyebrow">Correction spotted</p>';
  if(p.key==='promise_date')h+='<h2 class="h3">'+esc(nw)+' instead of '+esc(old)+'?</h2><p>Did they change it, or did you mean '+esc(nw)+' all along?</p><div class="row"><button class="btn primary" data-a="sem-date-moved">They changed it</button><button class="btn" data-a="sem-date-correct">I meant '+esc(nw)+' all along</button></div><button class="link" data-a="sem-no">Neither. Keep '+esc(old)+'</button>';
  else h+='<h2 class="h3">Change '+esc(old)+' to '+esc(nw)+'?</h2><p class="muted">Sorted spotted this in '+esc(p.source)+'. Nothing changes until you confirm it.</p><div class="row"><button class="btn primary" data-a="sem-yes">Yes, change it</button><button class="btn" data-a="sem-no">No, keep '+esc(old)+'</button></div>';
  sec.innerHTML=h;var first=main.firstElementChild;if(first&&first.nextSibling)main.insertBefore(sec,first.nextSibling);else main.insertBefore(sec,main.firstChild)}
`;
R("function commit(){save();render()}",SEM+"\nfunction commit(){var ct=S.view.id&&task(S.view.id);if(ct)semEnsure(ct,true);save();render()}");
R("  $(\"#app\").innerHTML=html;","  $(\"#app\").innerHTML=html;\n  semDecorate();");
R("  var b=e.target.closest(\"[data-a]\");if(!b)return;\n  var a=b.getAttribute(\"data-a\"),d=S.draft,t=S.view.id?task(S.view.id):null;",
  "  var b=e.target.closest(\"[data-a]\");if(!b)return;\n  var a=b.getAttribute(\"data-a\"),d=S.draft,t=S.view.id?task(S.view.id):null;\n  if(t&&a===\"cm-add\"){var sc=document.querySelector(\".cm-card\");if(sc)semObserveText(t,sc.innerText,\"the email reply you added\")}\n  if(t&&a===\"note-keep\"){var sn=document.querySelector(\".notes-block\");if(sn)semObserveText(t,sn.innerText,\"the helper note you kept\")}");
R("  switch(a){\n    case \"home\":",`  switch(a){
    case "sem-yes":if(t)semApplyPending(t,"correction");break;
    case "sem-no":if(t)semRejectPending(t);break;
    case "sem-date-correct":if(t)semApplyPending(t,"correction");break;
    case "sem-date-moved":if(t)semApplyPending(t,"reschedule");break;
    case "home":`);
R("  var form=e.target,k=form.getAttribute(\"data-f\"),d=S.draft,t=S.view.id?task(S.view.id):null;",
  "  var form=e.target,k=form.getAttribute(\"data-f\"),d=S.draft,t=S.view.id?task(S.view.id):null;\n  if(t)semObserveForm(t,form,k);");
fs.writeFileSync('public/index.html',s);
const EXPECT='';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v106 ok',h(s),s.length);
