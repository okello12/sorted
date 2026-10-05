const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='324b294808e1ce02adf34635426bbfddb76b661f')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v138: truth integrity. Keep source wording, Sorted's interpretation, confirmed facts, the person's own plan/reminder
// and an outbound draft separate. Tentative dates are not appointments. A request to check an existing booking stays a
// check until the person says what they found. Old pre-window vague dates are flagged for review, not silently rewritten.
// Anonymous save copy says what is actually true: server-backed, reopenable with this browser, not "your account". ----
R('var SORTED_V="v137"','var SORTED_V="v138"');
const PATCH=String.raw`
/* v138 truth integrity */
var _readCase138=readCase,_whenText138=whenText,_lgSync138=lgSync,_uCard138=uCard,_nextStepText138=nextStepText,_nowLine138=nowLine,_syncText138=syncText,_syncAll138=syncAll,_viewNew138=viewNew;
function truthWhen138(text){
  var s=String(text||"").replace(/[’‘]/g,"'").replace(/\s+/g," ").trim(),m,WD="(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)";
  m=new RegExp("\\bnot\\s+(?:on\\s+)?"+WD+"\\b","i").exec(s);if(m)return {phrase:m[0],precision:"negated"};
  m=new RegExp("\\b(?:probably|maybe|possibly|likely|tentatively|provisionally|should(?:\\s+be)?|expected(?:\\s+to\\s+be)?)\\b[^.!?]{0,30}\\b"+WD+"\\b","i").exec(s);if(m)return {phrase:m[0],precision:"tentative"};
  var wins=[/\b(?:sometime\s+)?next week\b/i,/\bearly next week\b/i,/\b(?:later|late) this week\b/i,/\bend of next week\b/i,/\bthis week\b/i,/\b(?:in|within)\s+\d+\s*(?:-|–|to|or)\s*\d+\s+(?:working|business)\s+days\b/i,/\bin\s+\d+\s+to\s+\d+\s+days\b/i,/\b(?:in|over)\s+(?:the\s+)?next\s+(?:few|couple of)\s+days\b/i,/\bin a (?:few|couple of) days\b/i,/\bnext few days\b/i];
  for(var i=0;i<wins.length;i++){m=wins[i].exec(s);if(m)return {phrase:m[0],precision:"window"}}
  m=new RegExp("\\bby\\s+(?:"+WD+"|tomorrow|today|(?:the\\s+)?\\d{1,2}(?:st|nd|rd|th)?(?:\\s+of)?\\s+[A-Za-z]+)","i").exec(s);if(m)return {phrase:m[0],precision:"deadline"};
  m=new RegExp("\\b(?:on\\s+)?(?:"+WD+"|tomorrow|today)(?:\\s+(?:at|between)\\s+[^,.!?]{1,22})?","i").exec(s);if(m)return {phrase:m[0].trim(),precision:"exact_day"};
  m=/\b(?:on\s+)?(?:the\s+)?\d{1,2}(?:st|nd|rd|th)?(?:\s+of)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)(?:\s+\d{4})?\b/i.exec(s);if(m)return {phrase:m[0],precision:"exact_day"};
  return {phrase:"",precision:"unknown"};
}
function truthPrec138(p){if(!p)return "unknown";if(p.tentative)return "tentative";if(p.win)return "window";if(p.by)return "deadline";if(p.dueAt)return p.dueEnd?"time_window":p.allDay?"exact_day":"exact_time";return "unknown"}
function truthSet138(o,k,v){if(v===undefined||v===null)return false;if(o[k]===v)return false;o[k]=v;return true}
function truthSource138(t,p){if(p&&p.sourceText)return p.sourceText;if(p&&p.src==="message")return p.said||"";return String(t&&t.said||p&&p.said||"").trim()}
function truthStamp138(t,p,src){
  if(!p)return false;var ch=false,text=String(src||truthSource138(t,p)||"").trim(),meta=truthWhen138(text),wasV=p.truthV;
  if(!wasV&&p.dueAt&&!p.win&&(meta.precision==="window"||meta.precision==="tentative")){ch=truthSet138(p,"legacyTimingReview",true)||ch}
  if(text)ch=truthSet138(p,"sourceText",text)||ch;
  if(meta.phrase)ch=truthSet138(p,"sourceWhen",meta.phrase)||ch;
  if(!p.precision||p.precision==="unknown")ch=truthSet138(p,"precision",meta.precision!=="unknown"?meta.precision:truthPrec138(p))||ch;
  ch=truthSet138(p,"truthV",1)||ch;return ch;
}
readCase=function(text,f){
  var r=_readCase138.apply(this,arguments);if(!r)return r;var src=String(text||"").trim(),m=truthWhen138(src);r.sourceText=src;r.sourceWhen=m.phrase||"";r.precision=m.precision!=="unknown"?m.precision:truthPrec138(r);r.truthV=1;
  if(m.precision==="tentative"&&r.dueAt){r.candidateDueAt=r.dueAt;r.candidateDueEnd=r.dueEnd||null;r.dueAt=null;r.dueEnd=null;r.by=false;r.win=false;r.allDay=true;r.tentative=true}
  if(m.precision==="negated"&&r.dueAt){r.dueAt=null;r.dueEnd=null;r.by=false;r.win=false;r.allDay=true;r.precision="unknown"}
  return r;
};
whenText=function(p){if(p&&p.tentative)return (p.sourceWhen||"Tentative day")+" (not confirmed)";return _whenText138(p)};
function truthSync138(t){
  if(!t||isMom(t)||t.example)return false;var ch=false,sp=t.sugP;
  if(sp)ch=truthStamp138(t,sp,sp.sourceText||t.said)||ch;
  var ps=t.promises||[],op=openPromise(t);
  ps.forEach(function(p,i){var src=p.sourceText||(p.src==="message"?p.said:(i===0?t.said:p.said));ch=truthStamp138(t,p,src)||ch});
  if(t.sugDone&&sp&&op&&String(op.said||"")===String(sp.said||"")){
    ["sourceText","sourceWhen","precision","candidateDueAt","candidateDueEnd","tentative"].forEach(function(k){if(sp[k]!==undefined)ch=truthSet138(op,k,sp[k])||ch});ch=truthSet138(op,"truthV",1)||ch;
  }
  if(truthNeedsCheck138(t)&&!t.truthPlan){t.truthPlan={kind:"check_existing",what:"Check the provider’s app and latest email for the booking",by:"sorted",st:"suggested",at:nowIso()};ch=true}
  if(ch)t.truthV=1;return ch;
}
lgSync=function(t){var a=truthSync138(t),b=_lgSync138(t);return !!(a||b)};
function truthNeedsCheck138(t){
  if(!t||t.board==="done"||(t.truthCheck&&t.truthCheck.status))return false;var x=String(t.said||"").replace(/[’‘]/g,"'");
  return /\b(?:haven't|have not|hadn't|had not|not|never)\s+(?:yet\s+)?(?:checked|looked|confirmed)\b[^.]{0,100}\b(?:app|email|booking|appointment|account|portal)\b/i.test(x)||/\bneed to check\b[^.]{0,80}\b(?:app|email|booking|appointment|account|portal)\b/i.test(x);
}
function truthParty138(t,p){return p&&p.party||(t.facts&&t.facts.party)||"the provider"}
function truthInterpret138(t,p){
  if(!p)return "Sorted has not recorded a promise with a confirmed date.";
  if(p.tentative)return "A possible day was mentioned, but it is not a confirmed appointment.";
  if(p.win||p.precision==="window")return "An event is expected during an approximate period. There is no confirmed appointment day.";
  if(!p.dueAt)return "A promise is recorded, but there is no confirmed day on the case.";
  return "A date is recorded on the case.";
}
function truthDraft138(t,p){var w=p&&p.sourceWhen?" "+p.sourceWhen:"";return "Hello, you mentioned an engineer visit"+w+". Could you confirm the appointment day, time window and booking reference?"}
function truthFoundForm138(t){return '<form class="stack-s truth138-found" data-f="truth138-found" data-id="'+esc(t.id)+'"><label class="f"><span class="h3">What day did you find?</span><input type="date" name="tdate" required></label><label class="f"><span>Booking reference <span class="muted">(optional)</span></span><input type="text" name="tref" autocomplete="off" maxlength="80"></label><p class="muted">This records what you found in the provider’s app or email. It does not say they changed the appointment.</p><div class="row"><button class="btn primary" type="submit">Keep these booking details</button><button class="btn" type="button" data-a="truth-close" data-id="'+esc(t.id)+'">Cancel</button></div></form>'}
function truthCard138(t){
  if(!t||t.board==="done"||t.example)return "";truthSync138(t);var p=openPromise(t)||(t.sugP&&!t.sugDone?t.sugP:null),need=truthNeedsCheck138(t),unc=p&&(p.win||p.tentative||p.legacyTimingReview||p.precision==="window"||p.precision==="tentative"),chk=t.truthCheck||null;
  if(!p&&!need&&!chk)return "";if(!unc&&!need&&!chk&&!(S.truth138&&S.truth138.id===t.id))return "";
  var src=truthSource138(t,p),h='<section class="sheet stack-s truth138" aria-labelledby="truth138-h"><h2 class="h3" id="truth138-h">Source, meaning and next step</h2>';
  if(src)h+='<div><p class="eyebrow">What was actually said</p><p class="truth138-quote">“'+esc(src)+'”</p></div>';
  h+='<div><p class="eyebrow">Sorted’s interpretation</p><p>'+esc(truthInterpret138(t,p))+'</p></div>';
  if(p&&p.sourceWhen)h+='<p class="muted">Timing wording kept as: “'+esc(p.sourceWhen)+'”.</p>';
  if(p&&p.legacyTimingReview)h+='<div class="check truth138-review"><p class="h3">Please check this date against the original message.</p><p>This case was created before Sorted kept vague timing separately. The old date is still in the history until you review it.</p><div class="stack-s"><button class="btn primary" data-a="truth-date-ok" data-id="'+esc(t.id)+'">This date is correct</button><button class="btn" data-a="panel" data-p="correct">Change it</button><button class="btn" data-a="truth-date-none" data-id="'+esc(t.id)+'">There was no confirmed date</button></div></div>';
  if(need){h+='<div class="truth138-plan"><p class="eyebrow">Suggested next step</p><p><strong>Check the provider’s app and latest email for the booking.</strong></p><div class="stack-s"><button class="btn primary" data-a="truth-check-found" data-id="'+esc(t.id)+'">I found the booking</button><button class="btn" data-a="truth-check-none" data-id="'+esc(t.id)+'">There’s still no confirmed day</button><button class="btn" data-a="truth-remind" data-id="'+esc(t.id)+'">Remind me to check</button></div></div>'}
  if(chk&&chk.status==="none"){h+='<div class="truth138-plan"><p class="eyebrow">What you found</p><p>You checked and there is still no confirmed booking day.</p><button class="btn primary" data-a="truth-draft" data-id="'+esc(t.id)+'">Prepare a message</button></div>'}
  if(chk&&chk.status==="found")h+='<div class="truth138-plan"><p class="eyebrow">Confirmed booking details</p><p>You found the booking'+(chk.day?' for '+esc(fmtDay(new Date(chk.day+"T12:00:00"))):'')+(chk.ref?' · '+esc(chk.ref):'')+'.</p></div>';
  if(t.snooze&&(need||(t.truthPlan&&t.truthPlan.kind==="check_existing")))h+='<div><p class="eyebrow">Your reminder</p><p>'+esc(snSay(new Date(t.snooze.until)))+'. This is when you chose to check. It is not the provider’s appointment.</p></div>';
  if(S.truth138&&S.truth138.id===t.id&&S.truth138.mode==="found")h+=truthFoundForm138(t);
  if(S.truth138&&S.truth138.id===t.id&&S.truth138.mode==="draft"){var d=truthDraft138(t,p);h+='<div class="truth138-draft"><p class="eyebrow">Draft — check before sending</p><label class="f"><span class="hint">This is Sorted’s proposed message. It is not part of what they said or what you said.</span><textarea id="truth138-draft">'+esc(d)+'</textarea></label><div class="row"><button class="btn primary" data-a="truth-copy" data-id="'+esc(t.id)+'">Copy draft</button><button class="btn" data-a="truth-close" data-id="'+esc(t.id)+'">Close</button></div></div>'}
  return h+'</section>';
}
uCard=function(t){return truthCard138(t)+_uCard138(t)};
nextStepText=function(t){if(truthNeedsCheck138(t))return "Next: check the provider’s app and latest email for the booking";if(!t.call){var x=String(t.said||"");if(/\b(?:their|the provider'?s?)\s+(?:app|account|portal)\b/i.test(x))return "Next: open their account and check the information";if(/\b(?:email|message|text)\b/i.test(x)&&/\b(?:send|write|reply|contact)\b/i.test(x))return "Next: prepare a message"}return _nextStepText138(t)};
nowLine=function(t,s){if(truthNeedsCheck138(t)&&s!=="done"&&!t.example)return '<p class="now125"><strong>Next:</strong> check the provider’s app and latest email for the booking</p>';return _nowLine138(t,s)};
syncText=function(t){
  if(S.user&&!S.user.email&&t&&!t.example){if(t._saving)return "Saving…";if(t._dirty)return isOffline()?"Saved on this phone, not yet sent. It sends when you’re back online.":"Saved on this phone, not yet sent.";return t.rev?"Saved. You can reopen it in this browser.":""}
  return _syncText138(t);
};
syncAll=function(){if(S.user&&!S.user.email){var n=pendingRecs().length;if(!n)return "Saved. You can reopen your cases in this browser.";return (n===1?"1 case":n+" cases")+" saved on this phone, not yet sent"+(isOffline()?". "+(n===1?"It sends":"They send")+" when you’re back online.":".")}return _syncAll138()};
viewNew=function(){var h=_viewNew138();if(S.user&&!S.user.email)h+='<p class="muted guest-save138">Sorted saves this case on its servers. Without an email, this browser holds the key needed to reopen it.</p>';return h};
function truthTask138(el){var id=el&&el.getAttribute("data-id")||(S.view&&S.view.id);return id?task(id):null}
function truthDonePlan138(t){if(t.truthPlan&&t.truthPlan.kind==="check_existing"){t.truthPlan.st="done";t.truthPlan.doneAt=nowIso();t.truthPlan.by="you"}}
function truthReplaceWithFound138(t,day,ref){
  var p=openPromise(t),at=nowIso(),ymd=day.split("-").map(Number),d=new Date(ymd[0],ymd[1]-1,ymd[2]);if(!p)return false;
  p.status="replaced";p.closedAt=at;var np={id:uid(),said:p.said,party:p.party||"",dueAt:d.toISOString(),dueEnd:null,allDay:true,by:false,ref:ref||p.ref||"",status:"open",loggedAt:at,src:"message",sourceType:"provider_account",sourceText:"Booking details you confirmed from the provider’s app or email",sourceWhen:day,precision:"exact_day",truthV:1};
  t.promises=t.promises||[];t.promises.push(np);t.board="waiting";t.truthCheck={status:"found",day:day,ref:np.ref||"",at:at};truthDonePlan138(t);if(ref){t.facts=t.facts||{};t.facts.ref=ref}log(t,"You found the booking in the provider’s app or email: "+fmtDay(d)+(np.ref?", reference "+np.ref:"")+". The earlier timing stays in the history.");track("booking_found",t,{promise:np.id});t._dirty=true;return true;
}
function truthNoDate138(t){var p=openPromise(t);if(!p)return;var at=nowIso();p.status="replaced";p.closedAt=at;var np={id:uid(),said:p.said,party:p.party||"",dueAt:null,dueEnd:null,allDay:true,by:false,ref:p.ref||"",status:"open",loggedAt:at,src:p.src||"sentence",sourceType:"user_review",sourceText:p.sourceText||t.said||p.said,sourceWhen:p.sourceWhen||"",precision:"unknown",truthV:1};t.promises.push(np);t.board="waiting";p.legacyTimingReview=false;t.truthCheck={status:"none",at:at};log(t,"You checked the original wording. There was no confirmed date. The earlier date stays in the history.");track("date_reviewed_no_confirmed_date",t,{promise:np.id});t._dirty=true;commit()}
function truthClick138(e){var b=e.target&&e.target.closest?e.target.closest("[data-a]"):null;if(!b)return;var a=b.getAttribute("data-a"),t;
  if(a==="truth-check-found"){e.preventDefault();t=truthTask138(b);if(!t)return;S.truth138={id:t.id,mode:"found"};render();setTimeout(function(){var x=document.querySelector('.truth138-found input[name="tdate"]');if(x)x.focus()},20)}
  else if(a==="truth-check-none"){e.preventDefault();t=truthTask138(b);if(!t)return;t.truthCheck={status:"none",at:nowIso()};truthDonePlan138(t);log(t,"You checked the provider’s app or email. There is still no confirmed booking day.");track("booking_checked_none",t,{});t._dirty=true;commit()}
  else if(a==="truth-remind"){e.preventDefault();t=truthTask138(b);if(!t)return;if(t.truthPlan&&t.truthPlan.kind==="check_existing"){t.truthPlan.st="confirmed";t.truthPlan.by="you";t.truthPlan.confirmedAt=nowIso();t._dirty=true;save()}S.view.panel="later";render()}
  else if(a==="truth-draft"){e.preventDefault();t=truthTask138(b);if(!t)return;S.truth138={id:t.id,mode:"draft"};render()}
  else if(a==="truth-copy"){e.preventDefault();var ta=document.getElementById("truth138-draft");if(ta)copy(ta.value,"Draft copied. Nothing on the case changed.")}
  else if(a==="truth-close"){e.preventDefault();S.truth138=null;render()}
  else if(a==="truth-date-ok"){e.preventDefault();t=truthTask138(b);if(!t)return;var p=openPromise(t);if(p){p.legacyTimingReview=false;p.truthChecked=true;p.precision=truthPrec138(p);log(t,"You checked the old date against the original wording and confirmed it.");track("legacy_date_confirmed",t,{promise:p.id});t._dirty=true;commit()}}
  else if(a==="truth-date-none"){e.preventDefault();t=truthTask138(b);if(t)truthNoDate138(t)}
}
function truthSubmit138(e){var f=e.target;if(!f||f.getAttribute("data-f")!=="truth138-found")return;e.preventDefault();e.stopPropagation();var t=truthTask138(f),day=f.elements.tdate.value,ref=String(f.elements.tref.value||"").trim();if(!t||!day)return;if(truthReplaceWithFound138(t,day,ref)){S.truth138=null;commit()}}
document.addEventListener("click",truthClick138,false);document.addEventListener("submit",truthSubmit138,true);
`;
R("boot();\n})();\n</script>",PATCH+"\nboot();\n})();\n</script>");
R("</style>\n</head>","</style>\n<style>\n/* v138 */\n.truth138{margin-top:12px;border-left:4px solid var(--carbon)}\n.truth138 .eyebrow{margin-bottom:4px}\n.truth138-quote{white-space:pre-wrap}\n.truth138-plan{border-top:1px solid var(--rule);padding-top:12px}\n.truth138-draft{border-top:1px solid var(--rule);padding-top:12px}\n.truth138-review{margin-top:4px}\n.guest-save138{font-size:15px;margin-top:10px}\n</style>\n</head>");
fs.writeFileSync('public/index.html',s);
const EXPECT='';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v138 ok',h(s),s.length);
