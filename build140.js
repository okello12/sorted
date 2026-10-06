const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v140: truth metadata must never manufacture an obligation. The mature promise reader decides whether anyone
// actually committed to something; this layer only records source wording/precision for promises that reader accepted,
// keeps unrelated legacy cases untouched, fixes guest save truthfulness, and owns its truth-specific controls. ----
R('var SORTED_V="v139"','var SORTED_V="v140"');
const PATCH=String.raw`
/* v140: truth metadata, not promise manufacture */
var _readCase140=readCase,_truthSync140=truthSync138,_syncText140=syncText,_syncAll140=syncAll;
readCase=function(text,f){
  /* Promise/obligation confidence and date precision are separate questions. The existing reader has a large adversarial
     corpus for the first one. Never create a promise merely because a sentence contains a date-ish phrase such as
     "maybe Tuesday", "I will call Friday" or "check tomorrow". */
  var r=_readCase140.apply(this,arguments);if(!r)return r;
  var src=String(text||'').trim(),meta=truthWhen138(src);
  r.sourceText=src;r.sourceWhen=meta.phrase||r.sourceWhen||'';r.precision=meta.precision!=='unknown'?meta.precision:(r.precision||truthPrec138(r));r.truthV=1;
  /* The mature parser already understands windows. One older path still flattened "sometime next week" when extra
     sentences followed the promise. Repair that accepted promise only; never create a promise that the reader rejected. */
  if(meta.precision==='window'&&!r.win&&/\b(?:sometime\s+)?next week\b/i.test(meta.phrase||'')){
    var w=parseWhen(meta.phrase,new Date());
    if(w&&w.wstart&&w.date){
      var a=w.wstart.split('-').map(Number),z=w.date.split('-').map(Number),st=new Date(a[0],a[1]-1,a[2]),en=new Date(z[0],z[1]-1,z[2]);
      en.setHours(23,59,59,999);r.dueAt=st.toISOString();r.dueEnd=en.toISOString();r.allDay=true;r.by=false;r.win=true;
    }
  }
  /* A plain weekday plus an explicit no-show is necessarily about a visit that has already failed. On the named
     weekday itself the older parser can otherwise choose today and keep it "open" until midnight. Use the previous
     occurrence only for unambiguous no-show language; "hasn't confirmed a time" is deliberately not included. */
  var noShow=/\b(?:nobody|no one)\s+(?:came|turned up|arrived|showed up)\b|\b(?:didn't|did not|never)\s+(?:come|turn up|arrive|show up|happen)\b|\bno[- ]?show\b/i.test(src);
  var bareWd=/\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b/i.test(src)&&!/\b(?:next|last)\s+(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b/i.test(src);
  if(noShow&&bareWd&&r.dueAt){
    var ns=new Date(r.dueAt),nn=new Date(),sameNs=ns.getFullYear()===nn.getFullYear()&&ns.getMonth()===nn.getMonth()&&ns.getDate()===nn.getDate();
    if(sameNs||ns>nn){ns.setDate(ns.getDate()-7);r.dueAt=ns.toISOString();if(r.dueEnd){var ne=new Date(r.dueEnd);ne.setDate(ne.getDate()-7);r.dueEnd=ne.toISOString()}r.past=true}
  }
  /* Outside those compatibility edges, the mature date parser remains authoritative. In particular, do not reinterpret
     prices as times or turn its working-day/date rules into a different range here. */
  return r;
};
/* Bare-weekday corrections are relative to the appointment being corrected, not to the day the user happens to type
   the correction. If a Tuesday booking is next week, "sorry, I meant Wednesday" means the Wednesday beside that booking,
   not tomorrow. Preserve the original time window unless the correction itself supplies a new time. */
var _corrRead140=corrRead;
corrRead=function(cur,text){
  var r=_corrRead140.apply(this,arguments);if(!r||r.k!=='date'||!cur||!cur.dueAt)return r;
  var raw=String(text||''),m=/\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b/i.exec(raw);
  if(!m||/\b(?:next|last|this)\s+(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b/i.test(raw))return r;
  if(/\b\d{1,2}(?:st|nd|rd|th)?(?:\s+of)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[A-Za-z]*\b/i.test(raw))return r;
  var hasTime=/\b\d{1,2}(?::\d{2})?\s*(?:am|pm)\b|\bbetween\s+\d{1,2}/i.test(raw),days=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'],want=days.map(function(x){return x.toLowerCase()}).indexOf(m[1].toLowerCase());
  var old=new Date(cur.dueAt),delta=(want-old.getDay()+7)%7,target=new Date(old);target.setDate(target.getDate()+delta);
  if(!hasTime){
    r.to=target.toISOString();r.dueAt=r.to;r.allDay=!!cur.allDay;r.by=!!cur.by;
    if(cur.dueEnd){var oe=new Date(cur.dueEnd),span=oe.getTime()-old.getTime(),te=new Date(target.getTime()+span);r.dueEnd=te.toISOString();r.toEnd=r.dueEnd}else{r.dueEnd=null;r.toEnd=null}
  }else{
    var parsed=new Date(r.dueAt||r.to);parsed.setFullYear(target.getFullYear(),target.getMonth(),target.getDate());r.dueAt=parsed.toISOString();r.to=r.dueAt;
    if(r.dueEnd){var pe=new Date(r.dueEnd);pe.setFullYear(target.getFullYear(),target.getMonth(),target.getDate());r.dueEnd=pe.toISOString();r.toEnd=r.dueEnd}
  }
  return r;
};
function truthRelevant140(t){
  if(!t||isMom(t)||t.example)return false;if(t.truthV||t.truthPlan||t.truthCheck)return true;var p=t.sugP||openPromise(t);
  if(p&&(p.truthV||p.sourceText||p.sourceWhen||p.tentative||p.win||p.legacyTimingReview||p.precision==='window'||p.precision==='tentative'))return true;
  var q=truthWhen138(String(t.said||''));return q.precision==='window'||q.precision==='tentative'||q.precision==='negated';
}
truthSync138=function(t){if(!truthRelevant140(t))return false;return _truthSync140(t)};
/* The ledger still runs for every case; the truth extension only mutates cases to which it applies. */
lgSync=function(t){var a=truthSync138(t),b=_lgSync138(t);return !!(a||b)};
syncText=function(t){
  if(S.user&&!S.user.email&&t&&!t.example){if(t._saving)return 'Saving…';if(t._dirty||isOffline())return 'Saved on this phone, not yet sent. It sends when the connection is available.';return t.rev?'Saved. You can reopen it in this browser.':''}
  return _syncText140(t);
};
syncAll=function(){
  if(S.user&&!S.user.email){var n=pendingRecs().length;if(n||isOffline())return (n===1?'1 case':n?n+' cases':'Changes')+' saved on this phone, not yet sent'+(isOffline()?'. They send when the connection is available.':'.');return 'Saved. You can reopen your cases in this browser.'}
  return _syncAll140();
};
/* Truth controls are ours. Run them before the older generic click switch and stop that switch seeing an unknown action. */
try{document.removeEventListener('click',truthClick138,false)}catch(e){}
function truthCapture140(e){var b=e.target&&e.target.closest?e.target.closest('[data-a]'):null,a=b&&b.getAttribute('data-a');if(!a||a.indexOf('truth-')!==0)return;truthClick138(e);e.stopPropagation()}
document.addEventListener('click',truthCapture140,true);

/* Show truth review in the visible action area without wrapping viewTask. Restrict it to genuinely uncertain/check
   cases, so ordinary exact-date repairs and correction flows stay on the long-proven legacy path. */
function truthShow140(t){
  if(!t||t.example||t.board==='done')return false;
  var p=openPromise(t)||(t.sugP&&!t.sugDone?t.sugP:null);
  return !!(truthNeedsCheck138(t)||t.truthCheck||(S.truth138&&S.truth138.id===t.id)||
    (p&&(p.win||p.tentative||p.legacyTimingReview||p.precision==='window'||p.precision==='tentative')));
}
var _keepBanner140=keepBanner;
uCard=function(t){return _uCard138(t)};
keepBanner=function(t){return _keepBanner140(t)+(truthShow140(t)?truthCard138(t):'')};

`;
R("boot();\n})();\n</script>",PATCH+"\nboot();\n})();\n</script>");
fs.writeFileSync('public/index.html',s);
const EXPECT='';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v140 ok',h(s),s.length);
