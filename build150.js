const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='3f0c0d43c9d3f5c078ab0812da39eacda2222451')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v150: one answer to "what needs attention" (the attention extraction, step 1) ----
// Home, the case page, quick answers and the reminder question each asked state(), home44Priority(), home111Why(),
// qKind(), ownDeadline(), snoozed(), nextStepText() and rem149Due() separately, and each of those was wrapped by later
// releases. attention(t) now asks them once, in a fixed order, and returns one record. While a screen is drawn the
// record is kept for that draw, so every part of the screen reads the same answer (and Home with 100 cases does the
// work once per case, not once per mention). The old names still work: during a draw they read the record; outside a
// draw they compute as before. No change on screen is intended; test 119 checks the record agrees with the old answers.
R("function boot(){",
`/* ---------- v150: attention(t), one record per case per draw ---------- */
var ATT150={memo:null,depth:0,busy:null,F:{state:state,prio:home44Priority,why:home111Why,q:qKind,own:ownDeadline,snoozed:snoozed,next:nextStepText,due:rem149Due}};
function att150Calc(t){var F=ATT150.F,b=ATT150.busy||(ATT150.busy=new Set());b.add(t);
  try{return {t:t,state:F.state(t),prio:F.prio(t),why:F.why(t),q:F.q(t),own:F.own(t),snoozed:F.snoozed(t),next:F.next(t),due:F.due(t),at:Date.now()}}
  finally{b.delete(t)}}
function attention(t){if(!t||typeof t!=="object")return null;
  var m=ATT150.memo;if(!m)return att150Calc(t);
  var r=m.get(t);if(!r){r=att150Calc(t);m.set(t,r)}return r}
function att150Copy(x){return x&&typeof x==="object"&&!(x instanceof Date)?Object.assign({},x):x}
function att150Use(t){return !!(ATT150.memo&&t&&typeof t==="object"&&!(ATT150.busy&&ATT150.busy.has(t)))}
state=function(t){return att150Use(t)?attention(t).state:ATT150.F.state(t)};
home44Priority=function(t){return att150Use(t)?attention(t).prio:ATT150.F.prio(t)};
home111Why=function(t){return att150Use(t)?attention(t).why:ATT150.F.why(t)};
qKind=function(t){return att150Use(t)?attention(t).q:ATT150.F.q(t)};
ownDeadline=function(t){return att150Use(t)?att150Copy(attention(t).own):ATT150.F.own(t)};
snoozed=function(t){return att150Use(t)?attention(t).snoozed:ATT150.F.snoozed(t)};
nextStepText=function(t){return arguments.length===1&&att150Use(t)?attention(t).next:ATT150.F.next.apply(this,arguments)};
rem149Due=function(t){var d=att150Use(t)?attention(t).due:ATT150.F.due(t);return d instanceof Date?new Date(d):d};
var _render150=render;
render=function(){if(!ATT150.depth++)ATT150.memo=new WeakMap();try{return _render150.apply(this,arguments)}finally{if(!--ATT150.depth)ATT150.memo=null}};
function boot(){`);
s=s.split('SORTED_V="v149"').join('SORTED_V="v150"');
fs.writeFileSync('public/index.html',s);
const EXPECT='3bca8105a5a9279730e55064c43985dc48935acb';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v150 ok',h(s),s.length);
