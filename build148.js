const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='1a75139aa432861354051f55443aeb91f760546a')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v148: two obligations at once. What they owe and what you plan are kept apart, and nothing Sorted reads or
// proposes replaces your plan without your say. (The refund, TSB and garage tests, 8 and 9 October.)

// 1. Confirming their promise asks before it changes anything about your own plan.
R("else{t.board=openMove(t)?\"yours\":\"waiting\";var sem=defaultEmail(t);",
  "else{t.board=openMove(t)?\"yours\":\"waiting\";planAsk148Set(t);var sem=defaultEmail(t);");
R("t.promises.push(pr);t.board=pr.dueAt&&!openMove(t)?\"waiting\":\"yours\";",
  "t.promises.push(pr);t.board=pr.dueAt&&!openMove(t)?\"waiting\":\"yours\";planAsk148Set(t);");
// 2. The case page shows both obligations together, under the header.
R("+dlOffer141(t,s)+\"\\u0001\"",
  "+dlOffer141(t,s)+planAskCard148(t,s)+both148Card(t,s)+\"\\u0001\"");
// 3. Home: "I heard from them" next to your step, on the spotlight and in the quick answers.
R("'<div class=\"home44-actions\"><button class=\"btn primary\" data-a=\"home-move\" data-id=\"'+t.id+'\">'+esc(moveAct(m.what).done)+'</button>",
  "'<div class=\"home44-actions\"><button class=\"btn primary\" data-a=\"home-move\" data-id=\"'+t.id+'\">'+esc(moveAct(m.what).done)+'</button>'+heardBtn148(t)+'");
R("h='<button class=\"btn primary\" data-a=\"home-move\" data-id=\"'+id+'\">'+esc(moveAct(m.what).done)+'</button>'+b(\"q-later\",\"Later\")}",
  "h='<button class=\"btn primary\" data-a=\"home-move\" data-id=\"'+id+'\">'+esc(moveAct(m.what).done)+'</button>'+heardBtn148(t)+b(\"q-later\",\"Later\")}");
// 4. Parking actions close only their own reminder, never a step of yours.
R("var pmv=openMove(t);if(pmv){pmv.status=\"done\"",
  "var pmv=openMove(t);if(pmv&&pmv.src!==\"plan\"){pmv.status=\"done\"");
R("var ppm=openMove(t);if(ppm){ppm.status=\"done\"",
  "var ppm=openMove(t);if(ppm&&ppm.src!==\"plan\"){ppm.status=\"done\"");
// 5. "Something's broken" asks what needs repairing, presumes nothing, and a car is a chip of its own.
R("fix:{h:\"What’s broken?\"",
  "fix:{h:\"What needs repairing?\"");
R("((ex&&ex.item?x===ex.item:i===0)?' checked':'')",
  "((ex&&ex.item?x===ex.item:i===0&&k!==\"fix\")?' checked':'')");
R(".join(\"\")+'</div></fieldset>'+(k===\"fix\"?'<p class=\"gi147-car\" style=\"margin:0\"><button type=\"button\" class=\"link\" data-cap95=\"garage\" style=\"text-align:left\">A car or van at a garage? Use the garage questions</button></p>':'');",
  ".join(\"\")+(k===\"fix\"?'<button type=\"button\" class=\"chip gi-chip gi147-car\" data-cap95=\"garage\">A car or van</button>':'')+'</div></fieldset>';");
// 6. The new actions and the opening-time form.
R("    case \"move-done\":",
  "    case \"plan-keep148\":if(t){planKeep148(t)}break;\n    case \"plan-wait148\":if(t){planWait148(t)}break;\n    case \"open148-ask\":if(t){S.view.open148=true;render();var o1=$(\"#open148-time\");if(o1)o1.focus()}break;\n    case \"heard148\":{var hid=b.getAttribute(\"data-id\")||b.getAttribute(\"data-qid\")||(t&&t.id),ht=task(hid);if(ht)heard148(ht)}break;\n    case \"move-done\":");
R("  if(k===\"promise\"){\n    var rn2=",
  "  if(k===\"open148\"){var ov=($(\"#open148-time\")||{}).value||\"\";if(t&&ov)open148(t,ov);else{S.view.open148err=\"Choose a time.\";render()}return}\n  if(k===\"promise\"){\n    var rn2=");
R("function boot(){",
`/* ---------- v148: two obligations at once ---------- */
/* The rule: what they owe (a promise) and what you plan (your step) are separate records. A promise Sorted reads, or
   one you confirm, never closes, replaces or hides your plan; if both are open, the case is yours and Home is never
   "All clear" (state() already says so for any open step). When you confirm their promise and you had a plan, Sorted
   asks whether to keep it. */
var PLAN_NONE148=/^\\s*(?:not sure(?: yet)?|nothing(?: yet)?|no plan|no idea|dunno|idk|don'?t know|leave it(?: for now)?|(?:just )?wait(?:ing)?(?:\\b.*)?|see what happens|skip|n\\/?a|none|-+)\\s*[.!]?\\s*$/i;
var IFNO148=/\\b(?:if|unless)\\b[^.;,]{0,60}?\\b(?:no|not|haven'?t|hasn'?t|didn'?t|don'?t|nothing|still)\\b[^.;,]{0,40}/i;
var OPENUNK148=/\\b(?:not sure|don'?t know|unsure|no idea)\\b[^.;]{0,40}\\bopen|\\bopen(?:s|ing)?\\s+(?:at\\s+)?\\d{1,2}(?::\\d\\d)?\\s*(?:am|pm)?\\s+or\\s+\\d/i;
function planActionable148(b){b=String(b||"").trim();return b.length>=4&&!PLAN_NONE148.test(b)}
function planWords148(b){var w=String(b||"").trim().replace(/[.!]+$/,"");w=w.charAt(0).toUpperCase()+w.slice(1);if(w.length>200)w=w.slice(0,200).replace(/\\s+\\S*$/,"")+"…";return w}
function planMv148(t){return (t.moves||[]).filter(function(m){return m.src==="plan"&&m.status==="open"})[0]||null}
function planMake148(t){
  var b=String(t.baseline||"").trim(),w=planWords148(b),wn=plan147When(b),kind=checkPlan144(b)?"check":CONTACT144.test(b)?"contact":"own";
  var mv={id:uid(),what:w,act:moveAct(w).key,status:"open",loggedAt:nowIso(),src:"plan",kind:kind,chosen:true};
  var ifn=IFNO148.exec(b);if(ifn)mv.cond=ifn[0].trim().replace(/[,;]+$/,"");
  if(OPENUNK148.test(b))mv.openUnk=true;
  if(wn){mv.dueAt=wn.at.toISOString();mv.dueEnd=null;mv.allDay=wn.allDay;mv.by=wn.allDay}
  t.moves=t.moves||[];t.moves.push(mv);t.board="yours";
  log(t,"Your step, from your plan: "+w+(wn?" ("+(wn.allDay?fmtDay(wn.at):fmtDay(wn.at)+", "+fmtTime(wn.at))+")":"")+".");
  return mv;
}
/* At the start: any plan of yours (not only a call) next to their promise is kept as your step. */
planAdd147=function(t){
  if(!t||t.example||(t.moves||[]).length||t.cf)return;
  if(!planActionable148(t.baseline))return;
  var prom=(t.sugP&&!t.sugDone)||(t.promises||[]).some(function(p){return p.status==="open"});if(!prom)return;
  planMake148(t);
};
function planAsk148Set(t){
  if(!t||t.example||t.planAsk148||t.planAns148||t.board==="done"||pkOn(t))return;
  var p=openPromise(t);if(!p)return;
  var mv=planMv148(t);
  if(mv){t.planAsk148={at:nowIso(),pid:p.id};return}
  if(planActionable148(t.baseline)&&!(t.moves||[]).some(function(m){return m.src==="plan"})&&!t.call&&Date.now()-Date.parse(t.created||nowIso())<14*DAY)t.planAsk148={at:nowIso(),pid:p.id,make:true};
}
function who148(t,p){var w=whoSay((p&&p.party)||(t.facts&&t.facts.party)||"");return w||"they"}
function planAskCard148(t,s){
  var a=t&&t.planAsk148;if(!a||s==="done"||t.example)return "";var p=openPromise(t);if(!p){delete t.planAsk148;return ""}
  var mv=planMv148(t),plan=mv?mv.what:planWords148(t.baseline),who=cap1(who148(t,p));
  return '<section class="sheet stack-s plan148" aria-labelledby="plan148-h"><p class="eyebrow">Before Sorted waits</p><h2 class="h3" id="plan148-h" tabindex="-1">'+esc(who)+' said: “'+esc(String(q143(p)).replace(/[.!]+$/,""))+'”, '+esc(whenMid(p))+'.</h2>'+
    '<p>You also said you planned to: “'+esc(plan)+'”.</p><p class="muted" style="margin:0;font-size:15px">Sorted keeps both unless you say otherwise.</p>'+
    '<div class="row eq"><button class="btn primary" data-a="plan-keep148">Keep my follow-up</button><button class="btn" data-a="plan-wait148">I’ll just wait for them</button></div></section>';
}
function planKeep148(t){
  var a=t.planAsk148||{},mv=planMv148(t);if(!mv&&a.make)mv=planMake148(t);
  delete t.planAsk148;t.planAns148="keep";if(mv){t.board="yours";log(t,"You’re keeping your own step as well as their promise: "+mv.what+".")}
  commit();toast("Kept your follow-up");
}
function planWait148(t){
  var mv=planMv148(t),p=openPromise(t);delete t.planAsk148;t.planAns148="wait";
  if(mv){mv.status="dropped";mv.closedAt=nowIso();log(t,"You chose to wait for "+who148(t,p)+" instead of your own step: "+mv.what+".")}
  else log(t,"You chose to wait for "+who148(t,p)+".");
  if(p&&!openMove(t))t.board="waiting";commit();toast("Sorted will wait with you");
}
function heardBtn148(t){var mv=planMv148(t);return mv&&mv.kind==="contact"&&openPromise(t)&&!t.example?'<button class="btn" data-a="heard148" data-id="'+t.id+'">I heard from them</button>':""}
function heard148(t){
  var p=openPromise(t),mv=planMv148(t),who=who148(t,p);
  if(mv&&mv.kind==="contact"){mv.status="dropped";mv.closedAt=nowIso();mv.heard=true;log(t,"You heard from "+who+", so your follow-up isn’t needed now: "+mv.what+".")}
  else log(t,"You heard from "+who+".");
  t._dirty=true;S.view={name:"task",id:t.id,panel:"paste"};S.view.pasteOwn=true;S.draft={};commit();window.scrollTo(0,0);
  var f=$("#f-paste");if(f)f.focus();
}
function open148(t,v){
  var mv=planMv148(t);if(!mv)return;var hm=String(v).split(":").map(Number);if(isNaN(hm[0]))return;
  var d=mv.dueAt?new Date(mv.dueAt):new Date();if(!mv.dueAt||d<new Date()){d=new Date();if(d.getHours()*60+d.getMinutes()>=hm[0]*60+(hm[1]||0))d.setDate(d.getDate()+1)}
  d.setHours(hm[0],hm[1]||0,0,0);mv.dueAt=d.toISOString();mv.allDay=false;mv.by=false;mv.openUnk=false;mv.opens=v;
  delete S.view.open148;delete S.view.open148err;log(t,"They open at "+fmtTime(d)+". Your step is now "+fmtDay(d)+", "+fmtTime(d)+".");
  try{scheduleEmail(t)}catch(e){}commit();
}
function both148Card(t,s){
  if(!t||s==="done"||t.example||t.planAsk148)return "";var p=openPromise(t),mv=planMv148(t);if(!p||!mv)return "";
  var who=cap1(who148(t,p)),when=mv.dueAt?(mv.allDay?fmtDay(new Date(mv.dueAt)):fmtDay(new Date(mv.dueAt))+", "+fmtTime(new Date(mv.dueAt))):"when you’re ready";
  var row=function(k,v){return '<div class="both148-row"><h3 class="h3">'+esc(k)+'</h3><p>'+v+'</p></div>'};
  var h='<section class="sheet stack-s both148" aria-labelledby="both148-h"><h2 class="eyebrow" id="both148-h">Both of you have a next step</h2>';
  h+=row("What "+who.replace(/^Your /,"your ")+" said","“"+esc(String(q143(p)).replace(/[.!]+$/,""))+"”, "+esc(whenMid(p))+".");
  h+=row("Your plan",esc(mv.what)+"."+(mv.cond?'<br><span class="muted">Only '+esc(mv.cond.replace(/^unless/i,"unless"))+'.</span>':''));
  if(mv.openUnk)h+=row("Opening time","Not known yet."+(S.view.open148?'':' <button class="link" data-a="open148-ask">I know when they open</button>'));
  if(S.view.open148)h+='<form class="stack-s" data-f="open148"><label class="f"><span class="h3">When do they open?</span><input type="time" id="open148-time" name="opens"></label>'+(S.view.open148err?'<p class="err">'+esc(S.view.open148err)+'</p>':'')+'<button class="btn" type="submit">Save the time</button></form>';
  h+=row("Needs you "+(mv.dueAt?(sameDay(new Date(mv.dueAt),new Date())?"today":"on "+when):""),mv.openUnk?"Check when they open, then "+(mv.kind==="contact"?"contact them"+(mv.cond?" "+esc(mv.cond):"")+".":"do your step."):esc(mv.what)+(mv.dueAt?", "+esc(when):"")+".");
  h+=row("Also waiting for",esc(who)+", "+esc(whenMid(p))+".");
  h+='<div class="row">'+'<button class="btn primary" data-a="move-done">'+esc(moveAct(mv.what).done)+'</button>'+(mv.kind==="contact"?'<button class="btn" data-a="heard148" data-id="'+t.id+'">I heard from them</button>':'')+'<button class="btn" data-a="panel" data-p="later">Later</button></div></section>';
  return h;
}
function boot(){`);
s=s.split('SORTED_V="v147"').join('SORTED_V="v148"');
fs.writeFileSync('public/index.html',s);
const EXPECT='0daf85b5cf27bfb9f1e868439abca8d49b26cf64';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v148 ok',h(s),s.length);
