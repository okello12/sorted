const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='20dd3864e79db7d745c4877567394dfd8f04ed64')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v152: the attention extraction, step 3. The next step, your own deadline, Later and the reminder day move inside
// attention(), and the old names now ask the new rules everywhere (not only during a draw). ----
// nextStepText had a base function and two wrappers (v143: your deadline, whose move, waiting; v144: what you found).
// att152Next() is the three in one, in the same order, reading the facts gathered once. ownDeadline, snoozed and
// rem149Due follow. Outside a draw each old name now works out only its own field from the facts, so the old function
// bodies are no longer used by the page: they stay in ATT150.F as the reference test 119 compares against.
R("function boot(){",
`/* ---------- v152: the rest of the attention rules ---------- */
function att152Base(f){var t=f.t,mv=f.m,op=f.p;
  if(t.cf&&t.board!=="done"&&cfProposed(t).length)return "Next: check the notice details";
  if(pkOn(t)){var pkn=pkNext(t);if(pkn)return pkn}
  if(t.mode==="fix"&&t.fix&&t.fix.step!=="done")return t.fix.step==="checks"?"Next: finish the checks":"Finish setting up this case";
  if(t.mode==="renew"&&t.renew&&t.renew.step!=="done")return "Finish setting up this case";
  if(t.mode==="do")return "Add your next step and when";
  if(t.sugP&&!t.sugDone)return "Next: check what they promised";
  if(mv&&mv.what&&!(mv.src==="parking"&&pkOn(t)))return "Next: "+lc1(String(mv.what).replace(/[.!]+$/,""));
  if(op&&calcOpen(op))return "Next: say which day Sorted should use";
  if(appCue(t)&&!(op&&op.dueAt))return "Next: check "+appWho(t)+" app or website for an update";
  if(!op&&!mv){var dl=dl141(t);if(dl&&(!t.pb||["read","owe","send","unsure","waiting"].indexOf(t.pb.stage)>=0))return "Next: decide what to do before "+pkDayLabel(dl.date)+": pay, reply or ask them";
    var pbh=pbHead141(t);if(pbh)return "Next: "+lc1(pbh);
    if(settled141(t))return "Next: finish this case, or add what happens next"}
  var rmx=f.rm;if(rmx&&!op&&(!t.call||!t.call.at||t.call.at<rmx.closedAt))return "Next: chase them";
  if(!t.call)return "Next: "+lc1(ch(t.facts&&t.facts.benefit==="Universal Credit"?"account":"phone").prep);
  return "Next: "+ch(t.call.via).next}
function att152Next(f){var t=f.t;
  try{if(t&&t.mode==="call"&&planDone144(t)&&!t.call&&!(t.promises||[]).length&&!t.turn&&t.board!=="done")return "Next: say what you found, or what happens now"}catch(e){}
  var r=att152Base(f),d=f.dl;
  if(d&&(d.st==="passed"||d.st==="today")&&!f.p&&!f.m&&!(t.cf&&cfProposed(t).length)&&!(t.sugP&&!t.sugDone)&&!(t.mode==="fix"&&t.fix&&t.fix.step!=="done")&&!(t.mode==="renew"&&t.renew&&t.renew.step!=="done")&&t.mode!=="do"){
    var who=dlWho143(t);r=d.st==="today"?"Next: your deadline is today: pay, reply or contact "+who:"Next: your deadline passed on "+fmtDay(d.day)+": pay, or contact "+who+" now"}
  else if(turnLeadCase143(t)&&/^Next: get the call ready$/i.test(r))r="Next: say whether it’s your move or theirs";
  else if(waitLeadCase143(t)&&/^Next: get the call ready$/i.test(r))r="Next: wait to hear back, or save a reminder to check";
  return r}
function att152Own(f){var t=f.t,x=null;
  if(pkOn(t)){var s=pkSoonest(t);if(s){var p=s.iso.split("-").map(Number);x={label:s.label.charAt(0).toLowerCase()+s.label.slice(1),d:new Date(p[0],p[1]-1,p[2])}}}
  var m=f.m;if(!x&&m&&m.dueAt)x={label:"your step: "+String(m.what||"").replace(/[.!]+$/,"").toLowerCase(),d:new Date(m.dueAt)};
  if(!x){var fd=null;try{fd=frDeadline(t)}catch(e){}if(fd&&fd.date){var q=typeof fd.date==="string"?fd.date.split("-").map(Number):null;x={label:"the date they set",d:q?new Date(q[0],q[1]-1,q[2]):new Date(fd.date)}}}
  if(x){x.end=new Date(x.d);x.end.setHours(23,59,59,999)}
  return x}
function att152Snoozed(f,own){var t=f.t;if(!(t&&t.snooze&&t.board!=="done"&&Date.parse(t.snooze.until)>Date.now()))return false;
  var hd=own&&!/^your step/.test(own.label)?own:null;return !(hd&&hd.d<=new Date(new Date().setHours(23,59,59,999)))}
function att152Due(f){var p=f.p,m=f.m,x=(m&&m.dueAt&&(!p||!p.dueAt||new Date(m.dueAt)<new Date(p.dueAt)))?m:p;return x&&x.dueAt?new Date(x.dueAt):null}
var ATT152={state:function(f){return att151State(f)},prio:function(f){return att151Prio(f,att151State(f))},why:att151Why,q:att151Q,own:att152Own,snoozed:function(f){return att152Snoozed(f,att152Own(f))},next:att152Next,due:att152Due};
att150Calc=function(t){var f=att151Facts(t),st=att151State(f),own=att152Own(f);
  return {t:t,state:st,prio:att151Prio(f,st),why:att151Why(f),q:att151Q(f),own:own,snoozed:att152Snoozed(f,own),next:att152Next(f),due:att152Due(f),at:Date.now()}};
function att152Field(k,t){return ATT150.memo&&t&&typeof t==="object"?attention(t)[k]:ATT152[k](att151Facts(t))}
state=function(t){return att152Field("state",t)};
home44Priority=function(t){return att152Field("prio",t)};
home111Why=function(t){return att152Field("why",t)};
qKind=function(t){return att152Field("q",t)};
ownDeadline=function(t){return att150Copy(att152Field("own",t))};
snoozed=function(t){return att152Field("snoozed",t)};
nextStepText=function(t){return arguments.length===1?att152Field("next",t):ATT150.F.next.apply(this,arguments)};
rem149Due=function(t){var d=att152Field("due",t);return d instanceof Date?new Date(d):d};
function boot(){`);
s=s.split('SORTED_V="v151"').join('SORTED_V="v152"');
fs.writeFileSync('public/index.html',s);
const EXPECT='37dbc2019adc5b6fcd895bb13fb7609b7b7a0a8d';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v152 ok',h(s),s.length);
