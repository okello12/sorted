const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='0daf85b5cf27bfb9f1e868439abca8d49b26cf64')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v149: a reminder that reaches a guest ----
// On 9 October production had 16 people, 42 cases and no reminder ever sent: almost everyone is a guest, and a guest
// is reminded only with an email or this phone's notifications, which almost nobody set up. A case with a date now
// says plainly that nothing will reach them outside Sorted yet, and offers one choice: their calendar (first, since it
// needs nothing else), this phone, an email, or no reminder. The choice is kept on the case and recorded as a code
// (reminder_path_chosen, migration 28). It replaces the once-per-phone nudge and the email panel that opened by itself.
R("S.view.panel=(S.user&&!S.user.email)?\"claim\":null",
  "S.view.panel=null");
R("    case \"nudge-skip\":",
  "    case \"rem149\":if(t){rem149Pick(t,b.getAttribute(\"data-v\"))}break;\n    case \"rem149-change\":if(t){delete t.rem149;t._dirty=true;commit()}break;\n    case \"nudge-skip\":");
R("if(refsProposed(t).length&&s!==\"done\"&&!S.view.panel&&!(t.frNew&&frCard(t)))h+=refsCard(t);",
  "if(refsProposed(t).length&&s!==\"done\"&&!S.view.panel&&!(t.frNew&&frCard(t))&&!rem149Asking(t))h+=refsCard(t);");
R("if(!S.user.email)return S.view.panel===\"claim\"||remindNudge(t)?\"\":",
  "if(!S.user.email)return S.view.panel===\"claim\"||rem149Asking(t)?\"\":");
R("function boot(){",
`/* ---------- v149: how Sorted reminds you, chosen per case ---------- */
var REM149={cal:"calendar",phone:"phone",email:"email",none:"none"};
function rem149Due(t){var p=openPromise(t),m=openMove(t),x=(m&&m.dueAt&&(!p||!p.dueAt||new Date(m.dueAt)<new Date(p.dueAt)))?m:p;return x&&x.dueAt?new Date(x.dueAt):null}
function rem149Path(){var st=(S.push||{}).state;return (S.user&&S.user.email&&S.emailReady&&!S.emailOff)?"email":st==="on"?"phone":""}
function rem149Say(t){var r=t.rem149;if(!r)return "";
  var w={cal:"In your calendar. Your calendar app will remind you.",phone:"On this phone, if you allowed notifications.",email:"By email, once you’ve confirmed your address.",none:"No reminder. Sorted shows it on Home when it’s due, if you open Sorted."}[r.how]||"";
  return '<p class="muted rem149-said" style="margin:0;font-size:15px">Reminder: '+esc(w)+' <button class="link" data-a="rem149-change">Change</button></p>'}
remindNudge=function(t){
  if(!t||t.example||t.board==="done")return "";
  var due=rem149Due(t);if(!due||due<new Date(Date.now()-DAY))return "";
  if(t.rem149)return rem149Say(t);
  if(rem149Path())return "";
  var st=(S.push||{}).state,guest=S.user&&!S.user.email,cal=calPlan(t),h="";
  if(cal)h+='<button class="btn primary block" data-a="rem149" data-v="cal">Add it to my calendar</button>';
  if(st==="off")h+='<button class="btn block'+(cal?'':' primary')+'" data-a="rem149" data-v="phone">Notify this phone</button>';
  else if(st==="needhome")h+='<p class="muted" style="margin:0;font-size:15px">'+esc(PUSH_HOME)+'</p>';
  if(guest)h+='<button class="btn block" data-a="rem149" data-v="email">Email me</button><p class="muted" style="margin:0;font-size:15px">Email adds your address to Sorted, so you can also open your cases on another phone.</p>';
  h+='<button class="link" data-a="rem149" data-v="none" style="align-self:flex-start">No reminder, I’ll check myself</button>';
  return '<section class="sheet stack-s nudge133 rem149" aria-labelledby="rem149-h"><h2 class="h3" id="rem149-h">How should Sorted remind you on '+esc(fmtDay(due))+'?</h2><p style="margin:0">At the moment nothing will reach you outside Sorted. Choose one; it takes a few seconds.</p>'+h+'</section>';
};
function rem149Asking(t){try{return /class="[^"]*rem149"/.test(remindNudge(t))}catch(e){return false}}
function rem149Pick(t,v){
  if(!REM149[v])return;t.rem149={how:v,at:nowIso()};t._dirty=true;track("reminder_path_chosen",t,{how:REM149[v]});
  if(v==="cal"){var cp=calPlan(t);if(cp){saveFile("sorted-reminder.ics",icsText(cp),"text/calendar","cal");t.calAt=nowIso();t.calFor=cp.uid;t.calWhen=calWhenText(t);logK(t,"Tapped add to calendar.","calendar",{via:"ics",for:cp.uid})}commit();return}
  if(v==="phone"){commit();pushOnNow();return}
  if(v==="email"){S.view.panel="claim";S.draft={};commit();var gc=$("#claim");if(gc)gc.scrollIntoView({block:"start"});return}
  commit();
}
function boot(){`);
s=s.split('SORTED_V="v148"').join('SORTED_V="v149"');
fs.writeFileSync('public/index.html',s);
const EXPECT='3f0c0d43c9d3f5c078ab0812da39eacda2222451';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v149 ok',h(s),s.length);
