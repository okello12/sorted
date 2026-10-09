const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='3bca8105a5a9279730e55064c43985dc48935acb')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v151: the attention extraction, step 2. The rules move inside attention(). ----
// state, priority, the reason a case leads and the quick answer were four functions (two of them wrapped in v143) that
// each looked at the open promise, your open step, their phases, your own deadline and a recent miss on their own.
// att151Facts(t) now gathers those facts once and att151Rules() derives all four from them, in one place. The old
// functions stay in ATT150.F as the reference: test 119 checks the new rules give the same answers on every case and on
// hundreds of variations of their dates. No change on screen is intended.
R("function boot(){",
`/* ---------- v151: the attention rules, from one set of facts ---------- */
function att151Facts(t,now){now=now||new Date();
  var p=openPromise(t),m=openMove(t),mw=m?window_(m):null,dl=null;try{dl=dlOwn143(t)}catch(e){}
  return {t:t,now:now,done:t.board==="done",p:p,m:m,pp:p?phase(p):null,mp:m?phase(m):null,mStart:mw?mw.start:null,dl:dl,rm:recentMiss(t)}}
function att151State(f){var t=f.t;
  if(f.done)return "done";
  if(f.m){if(f.mp==="later"&&f.m.dueAt&&new Date(f.m.dueAt)-Date.now()>28*DAY&&!f.p)return "upcoming";return f.mp==="later"||f.mp==="nodate"?"yours":"due"}
  if(f.p)return f.pp==="nodate"?"yours":f.pp==="later"?"waiting":f.pp==="check"?"due":"waitdue";
  if(t.mode==="renew"&&t.renew&&t.renew.step==="done"&&!t.renew.applied&&rphase(t.renew)==="upcoming")return "upcoming";
  return "yours"}
function att151Prio(f,st){
  var r=f.pp==="check"?0:f.mp==="check"?1:st==="due"?2:st==="yours"?3:st==="upcoming"?4:5;
  if(f.dl&&f.dl.st!=="later")return f.dl.st==="soon"?Math.min(r,2):-1;return r}
function att151Why(f){var p=f.p,m=f.m,d=f.dl;
  if(d){var w=d.st==="passed"?"Your deadline passed on "+fmtDay(d.day):d.st==="today"?"Your deadline is today":d.st==="soon"?"Due "+fmtDay(d.day):"";if(w)return w}
  if(p&&f.pp==="check")return p.chk&&p._ck?"Your check day":notFirm143(p)?(p.est146&&!aprx(p)?"The day they expected has passed":"The day Sorted worked out has passed"):"The date they gave has passed";
  if(m&&f.mp==="check")return "Overdue";
  if(m&&m.dueAt&&f.mp==="now")return "Due now";
  if(m&&m.dueAt&&f.mp==="soon"&&sameDay(f.mStart,new Date()))return "Due today";
  if(f.rm&&!p)return f.rm.partly?"Only partly happened":"They missed the date";
  return ""}
function att151Q(f){var t=f.t,p=f.p,m=f.m;
  if(f.done)return "";
  if(p&&f.pp==="check")return "promise";
  if(m&&m.what&&m.dueAt&&(f.mp==="check"||f.mp==="now"||(f.mp==="soon"&&sameDay(f.mStart,new Date()))))return "move";
  if(!p&&pkOn(t)&&/^(?:notice|nto|rejected)$/.test(pkStage(t))){var d=pkSoonest(t);if(d&&qDays(d.iso)<=7)return "pcn"}
  return ""}
function att151Rules(t){var f=att151Facts(t),st=att151State(f);return {state:st,prio:att151Prio(f,st),why:att151Why(f),q:att151Q(f)}}
att150Calc=function(t){var F=ATT150.F,b=ATT150.busy||(ATT150.busy=new Set());b.add(t);
  try{var r=att151Rules(t);r.t=t;r.own=F.own(t);r.snoozed=F.snoozed(t);r.next=F.next(t);r.due=F.due(t);r.at=Date.now();return r}
  finally{b.delete(t)}};
function boot(){`);
R("function att150Calc(t){","var att150Calc=function(t){");
R("finally{b.delete(t)}}\nfunction attention(t){","finally{b.delete(t)}};\nfunction attention(t){");
s=s.split('SORTED_V="v150"').join('SORTED_V="v151"');
fs.writeFileSync('public/index.html',s);
const EXPECT='20dd3864e79db7d745c4877567394dfd8f04ed64';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v151 ok',h(s),s.length);
