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
  /* Outside that compatibility edge, the mature date parser remains authoritative. In particular, do not reinterpret
     prices as times or turn its working-day/date rules into a different range here. */
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

/* v125 deliberately moves informational cards into a quieter secondary region. That region can be collapsed on some
   mature case layouts, which hid the truth review and its draft after confirmation. Relocate the card that uCard already
   rendered; do not call truthCard a second time, because rendering may synchronise legacy state and must stay single-pass. */
var _truthCard140=truthCard138,_viewTask140=viewTask;
truthCard138=function(t){var h=_truthCard140(t);if(h)S._truthCardHtml140=h;return h};
viewTask=function(){
  S._truthCardHtml140='';
  var h=_viewTask140(),card=S._truthCardHtml140||'';S._truthCardHtml140='';
  if(!card)return h;
  var old=h.indexOf(card);if(old>=0)h=h.slice(0,old)+h.slice(old+card.length);
  var p=h.lastIndexOf('</main>');return p>=0?h.slice(0,p)+card+h.slice(p):h+card;
};
`;
R("boot();\n})();\n</script>",PATCH+"\nboot();\n})();\n</script>");
fs.writeFileSync('public/index.html',s);
const EXPECT='';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v140 ok',h(s),s.length);
