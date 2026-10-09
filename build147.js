const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='a8ab6ad9042f0b34f1d4331b9f42e82a43861c6e')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v147: the garage test (9 October). The person's own plan survives a promise. ----
// "A garage said the car would be ready today after a brake job and would text when done. No text. I'll phone them in
// the morning." Sorted dropped the plan, said "All clear", offered a calendar alarm the evening before (already past) and
// "any time"; "Garage name not with me" became the garage's name in the quote and title, with "said they would said";
// "Something's broken" only offered household repairs.

// 1. A name placeholder is not a name; the example's role ("Which garage?") stands in for it.
R("var UNK_WHO=/^\\s*(?:they|",
  "var UNK_WHO=/^(?:the |their |my )?[a-z][a-z'’&-]*\\s+name\\b|^\\s*(?:they|");
R("|not to hand)\\b/i;",
  "|not to hand|not with me|not on me|not handy)\\b/i;");
R("var gunk=gk2!==\"fix\"&&UNK_WHO.test(gv.who);if(gunk)gv.who=\"\";",
  "var gunk=gk2!==\"fix\"&&UNK_WHO.test(gv.who);if(gunk)gv.who=unkRole147(d.ex,gk2);");
// 2. "said the car would be ready" typed into "What did they say?" is not "said they would said the car would…"
R("if(k===\"promise\"){var w140=what.replace(/^(?:they|he|she|it|we)\\s+(?:said|told me|told us|promised)\\s+(?:that\\s+)?/i,\"\")",
  "if(k===\"promise\"){var w140=what.replace(/^(?:(?:they|he|she|it|we)\\s+)?(?:said|says|told me|told us|promised(?: me)?)\\s+(?:that\\s+)?/i,\"\")");
R("var w=String(what||\"\").trim().replace(/^(?:they|she|he|it|the)\\s+/i,\"\")",
  "var w=String(what||\"\").trim().replace(/^(?:(?:they|he|she|it|we)\\s+)?(?:said|says|told me|told us|promised(?: me)?)\\s+(?:that\\s+)?/i,\"\").replace(/^(?:they|she|he|it|the)\\s+/i,\"\")");
// 3. The plan survives: "phone them in the morning" next to their promise is the person's step, dated from their words.
R("  planAdd144(t);",
  "  planAdd144(t);planAdd147(t);");
R("if(!m||m.src!==\"plan\")return _movedCard144(t);",
  "if(!m||m.src!==\"plan\"||m.kind===\"contact\")return _movedCard144(t);");
// 4. Confirming their promise doesn't hide your own open step: the case stays with you until you've done it.
R("else{t.board=\"waiting\";var sem=defaultEmail(t);",
  "else{t.board=openMove(t)?\"yours\":\"waiting\";var sem=defaultEmail(t);");
R("t.promises.push(pr);t.board=pr.dueAt?\"waiting\":\"yours\";",
  "t.promises.push(pr);t.board=pr.dueAt&&!openMove(t)?\"waiting\":\"yours\";");
// 5. "Any time" says nothing; "no time given" says what is known.
R("if(p.allDay)return fmtDay(w.start)+\", any time\";",
  "if(p.allDay)return fmtDay(w.start)+\", no time given\";");
R("dl+\", any time\");",
  "dl+\", no time given\");");
s=s.split("/, any time$/").join("/, no time given$/");
// 6. A calendar alarm that has already passed is moved to 6pm that day, or not offered.
R("c.alarm===\"PT9H\"?\"It reminds you at 9am that day.\":",
  "c.alarm===\"PT9H\"?\"It reminds you at 9am that day.\":c.alarm===\"PT18H\"?\"It reminds you at 6pm that day.\":");
// 7. Something's broken knows cars go to a garage.
R("Washing machine, boiler, broadband, a landlord repair.",
  "Washing machine, boiler, broadband, a landlord repair, a car at the garage.");
R("' checked':'')+' class=\"sr-only\"> '+esc(x)+'</label>'}).join(\"\")+'</div></fieldset>';",
  "' checked':'')+' class=\"sr-only\"> '+esc(x)+'</label>'}).join(\"\")+'</div></fieldset>'+(k===\"fix\"?'<p class=\"gi147-car\" style=\"margin:0\"><button type=\"button\" class=\"link\" data-cap95=\"garage\" style=\"text-align:left\">A car or van at a garage? Use the garage questions</button></p>':'');");
// 8. One way of saying where a guest's cases are.
R("They’re saved on Sorted’s servers, but only this browser can open them until you add an email.",
  "They’re saved to Sorted, but only this browser can open them until you add an email.");
R("function boot(){",
`/* ---------- v147: the person's own plan survives a promise ---------- */
var UNK_ROLE147=/^Which ((?:removal )?(?:garage|dealer|council|bank|airline|nursery|company|shop|landlord|builder|insurer))\\?$/;
function unkRole147(ex,gk){var e=EX[ex];if(!e||e.gk!==gk)return "";var m=UNK_ROLE147.exec(String(e.h||""));return m?"the "+m[1]:""}
/* When the person says they will contact them (call, ring, phone, email, chase…) and Sorted has also found their
   promise, the plan is kept as the person's step in their own words, never replaced by "wait". Its time comes from
   their words: "in the morning" is the next 8am, "tonight" 6pm, "tomorrow", a weekday or "at 9" as said. */
function plan147When(x,now){
  x=String(x||"");now=now||new Date();var d=new Date(now),hr=null,day=null,L=x.toLowerCase();
  if(/\\b(?:tomorrow|tmrw|tomoz)\\b/.test(L))day=1;
  else if(/\\b(?:today|this (?:morning|afternoon|evening)|tonight|later)\\b/.test(L))day=0;
  if(/\\b(?:morning|first thing|when they open)\\b/.test(L))hr=8;
  else if(/\\bafternoon\\b/.test(L))hr=14;
  else if(/\\b(?:tonight|evening|after work)\\b/.test(L))hr=18;
  else if(/\\blunch(?:time)?\\b/.test(L))hr=12;
  var at=/\\bat (\\d{1,2})(?::(\\d{2}))?\\s*(am|pm)?\\b/.exec(L);
  if(at){var hh=+at[1];if(at[3]==="pm"&&hh<12)hh+=12;else if(!at[3]&&hh<7)hh+=12;if(hh>=6&&hh<=21)hr=hh}
  if(day===null&&hr===null){var pw=null;try{pw=parseWhen(x)}catch(e){}if(pw&&pw.date){var pd=new Date(pw.date);if(pd>=new Date(now.getFullYear(),now.getMonth(),now.getDate()))return {at:pd,allDay:true}}return null}
  if(day===null){day=0;if(hr!==null&&now.getHours()>=hr)day=1}
  d.setDate(d.getDate()+day);
  if(hr===null){d.setHours(0,0,0,0);return {at:d,allDay:true}}
  d.setHours(hr,0,0,0);return {at:d,allDay:false};
}
function planAdd147(t){
  if(!t||t.example||(t.moves||[]).length||t.cf)return;
  var b=String(t.baseline||"").trim();if(!b||b.length<4||checkPlan144(b)||!CONTACT144.test(b))return;
  var prom=(t.sugP&&!t.sugDone)||(t.promises||[]).some(function(p){return p.status==="open"});if(!prom)return;
  var w=b.replace(/[.!]+$/,"");w=w.charAt(0).toUpperCase()+w.slice(1);if(w.length>200)w=w.slice(0,200).replace(/\\s+\\S*$/,"")+"…";
  var wn=plan147When(b),mv={id:uid(),what:w,act:moveAct(w).key,status:"open",loggedAt:nowIso(),src:"plan",kind:"contact",chosen:true};
  if(wn){mv.dueAt=wn.at.toISOString();mv.dueEnd=null;mv.allDay=wn.allDay;mv.by=wn.allDay}
  t.moves=t.moves||[];t.moves.push(mv);t.board="yours";
  log(t,"Your step, from your plan: "+w+(wn?" ("+(wn.allDay?fmtDay(wn.at):fmtDay(wn.at)+", "+fmtTime(wn.at))+")":"")+".");
}
/* A calendar alarm that has already passed (the evening before something due today) moves to 6pm on the day, or isn't offered. */
var _calPlan147=calPlan;calPlan=function(t){var c=_calPlan147.apply(this,arguments);try{if(c&&c.allDay&&/^-PT6H$|^PT9H$/.test(c.alarm)){var q=String(c.s),day=new Date(+q.slice(0,4),+q.slice(4,6)-1,+q.slice(6,8)),now=new Date(),al=new Date(day);if(c.alarm==="PT9H")al.setHours(9,0,0,0);else al.setHours(-6,0,0,0);if(al<now){var six=new Date(day);six.setHours(18,0,0,0);if(six>now)c.alarm="PT18H";else return null}}}catch(e){}return c};
function boot(){`);
s=s.split('SORTED_V="v146"').join('SORTED_V="v147"');
fs.writeFileSync('public/index.html',s);
const EXPECT='1a75139aa432861354051f55443aeb91f760546a';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v147 ok',h(s),s.length);
