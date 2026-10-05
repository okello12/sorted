const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v140: make the truth model authoritative without mutating unrelated legacy cases.
// A vague period is rebuilt as a real window even when an older parser flattened it; a tentative day is represented
// even when the old promise parser declined to create a suggestion; failed guest writes cannot display a saved state;
// and truth-only controls run before the older generic click router. ----
R('var SORTED_V="v139"','var SORTED_V="v140"');
const PATCH=String.raw`
/* v140: truth parsing + compatibility */
var _readCase140=readCase,_truthSync140=truthSync138,_syncText140=syncText,_syncAll140=syncAll;
function truthDay140(name,base){
  var ds=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'],want=ds.map(function(x){return x.toLowerCase()}).indexOf(String(name||'').toLowerCase());
  if(want<0)return null;var d=new Date(base||new Date());d.setHours(0,0,0,0);var add=(want-d.getDay()+7)%7;if(!add)add=7;d.setDate(d.getDate()+add);return d;
}
function truthWork140(base,n){var d=new Date(base),left=+n;while(left>0){d.setDate(d.getDate()+1);if(d.getDay()!==0&&d.getDay()!==6)left--}return d}
function truthBounds140(text){
  var x=String(text||'').replace(/[’‘]/g,"'").replace(/\s+/g,' '),b=new Date();b.setHours(0,0,0,0);var a=null,z=null,m;
  if(/\bearly next week\b/i.test(x)||/\b(?:sometime )?next week\b/i.test(x)||/\b(?:later|late|end of) next week\b/i.test(x)){
    var n=(8-b.getDay())%7;if(!n)n=7;a=new Date(b);a.setDate(a.getDate()+n);z=new Date(a);z.setDate(z.getDate()+4);
    if(/\bearly next week\b/i.test(x))z.setDate(a.getDate()+2);
    if(/\b(?:later|late|end of) next week\b/i.test(x))a.setDate(a.getDate()+2);
  }else if(/\b(?:sometime |later |some point )?(?:this|the coming) week\b/i.test(x)){
    a=new Date(b);z=new Date(b);var toFri=(5-b.getDay()+7)%7;if(b.getDay()===6||b.getDay()===0){var toMon=(8-b.getDay())%7||7;a.setDate(a.getDate()+toMon);z=new Date(a);z.setDate(z.getDate()+4)}else z.setDate(z.getDate()+toFri);
    if(/\blater\b/i.test(x)){a.setDate(a.getDate()+1);if(a>z)a=new Date(z)}
  }else if((m=/\b(?:in|within)\s+(\d+)\s*(?:-|–|to|or)\s*(\d+)\s+(working|business)\s+days\b/i.exec(x))){a=truthWork140(b,+m[1]);z=truthWork140(b,+m[2])}
  else if((m=/\bin\s+(\d+)\s+(?:to|-)\s*(\d+)\s+days\b/i.exec(x))){a=new Date(b);z=new Date(b);a.setDate(a.getDate()+ +m[1]);z.setDate(z.getDate()+ +m[2])}
  else if(/\b(?:in|over)\s+(?:the\s+)?next\s+(?:few|couple of)\s+days\b|\bin a (?:few|couple of) days\b|\bnext few days\b/i.test(x)){a=new Date(b);z=new Date(b);a.setDate(a.getDate()+1);z.setDate(z.getDate()+( /couple/i.test(x)?2:3))}
  if(!a||!z)return null;a.setHours(0,0,0,0);z.setHours(23,59,59,999);return {start:a,end:z};
}
function truthParty140(text,f){
  if(f&&f.party)return f.party;var m=/^\s*(?:the\s+)?([A-Z][A-Za-z0-9&.'’ -]{0,45}?)\s+(?:said|says|told me|confirmed|advised)\b/.exec(String(text||''));return m?m[1].trim():'';
}
function truthClause140(text){var x=String(text||'').trim(),m=/\b(?:said|says|told me|confirmed|advised)\b\s+(.+)/i.exec(x),v=(m?m[1]:x).split(/[.!?]/)[0].trim();return v?v.charAt(0).toUpperCase()+v.slice(1):'They gave an update'}
function truthCandidate140(text){var m=/(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)/i.exec(String(text||''));return m?truthDay140(m[1],new Date()):null}
readCase=function(text,f){
  var r=_readCase140.apply(this,arguments),src=String(text||'').trim(),meta=truthWhen138(src),bounds,cand;
  if(!r&&(meta.precision==='window'||meta.precision==='tentative'))r={said:truthClause140(src),party:truthParty140(src,f),dueAt:null,dueEnd:null,allDay:true,by:false,ref:(f&&f.ref)||''};
  if(!r)return r;
  r.sourceText=src;r.sourceWhen=meta.phrase||r.sourceWhen||'';r.precision=meta.precision!=='unknown'?meta.precision:(r.precision||truthPrec138(r));r.truthV=1;
  if(meta.precision==='window'){
    /* Keep a window already produced by the mature date parser (including its working-day/bank-holiday rules). Only
       reconstruct when an older/later parser flattened or dropped the interval. */
    if(!(r.win&&r.dueAt&&r.dueEnd)){bounds=truthBounds140(src);if(bounds){r.dueAt=bounds.start.toISOString();r.dueEnd=bounds.end.toISOString();r.allDay=true;r.by=false;r.win=true}}
    r.tentative=false;delete r.candidateDueAt;delete r.candidateDueEnd;
  }else if(meta.precision==='tentative'){
    cand=r.candidateDueAt?new Date(r.candidateDueAt):r.dueAt?new Date(r.dueAt):truthCandidate140(meta.phrase||src);if(cand&&!isNaN(cand)){cand.setHours(0,0,0,0);r.candidateDueAt=cand.toISOString()}
    r.candidateDueEnd=r.candidateDueEnd||null;r.dueAt=null;r.dueEnd=null;r.allDay=true;r.by=false;r.win=false;r.tentative=true;
  }else if(meta.precision==='negated'){
    r.dueAt=null;r.dueEnd=null;r.by=false;r.win=false;r.allDay=true;r.precision='unknown';r.tentative=false;delete r.candidateDueAt;delete r.candidateDueEnd;
  }
  return r;
};
function truthRelevant140(t){
  if(!t||isMom(t)||t.example)return false;if(t.truthV||t.truthPlan||t.truthCheck)return true;var p=t.sugP||openPromise(t);
  if(p&&(p.truthV||p.sourceText||p.sourceWhen||p.tentative||p.win||p.legacyTimingReview||p.precision==='window'||p.precision==='tentative'))return true;
  var q=truthWhen138(String(t.said||''));return q.precision==='window'||q.precision==='tentative'||q.precision==='negated';
}
truthSync138=function(t){if(!truthRelevant140(t))return false;return _truthSync140(t)};
/* The ledger still runs for every old case, but the new truth layer only touches cases to which it actually applies. */
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
`;
R("boot();\n})();\n</script>",PATCH+"\nboot();\n})();\n</script>");
fs.writeFileSync('public/index.html',s);
const EXPECT='';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v140 ok',h(s),s.length);
