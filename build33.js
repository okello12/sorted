const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='84f16740bfe11b1c708ffeb3cba0d7b952f586b7')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v33: a promise in the first sentence is offered back, for the person to confirm ----

// 1. find the promise, when it was due, and whether that has passed
R(`function shortTitle(text,f){`,String.raw`var PVERB=/\b(promised|promise[sd]?|said|told (?:me|us)|agreed|confirmed|assured|guaranteed|(?:was|were) (?:supposed|meant|due) to|is due to|are due to|booked)\b/i;
var PMISS=/\b(didn.?t|did not|never|no[- ]?show|hasn.?t|haven.?t|has not|have not|nobody|no one|missed|wasn.?t|weren.?t|still (?:no|not|waiting))\b/i;
var DURN={a:1,an:1,one:1,two:2,three:3,four:4,five:5,six:6,seven:7,eight:8,nine:9,ten:10,eleven:11,twelve:12,several:3,"a few":3};
function durDays(d){var m=/^(\d+|a few|[a-z]+)\s+(day|week|month)s?$/.exec(String(d||"").toLowerCase());if(!m)return 0;var n=/^\d+$/.test(m[1])?+m[1]:(DURN[m[1]]||0);return n*(m[2]==="week"?7:m[2]==="month"?30:1)}
function suggestPromise(text,f){
  var s=String(text||"").replace(/[’‘]/g,"'"),vm=PVERB.exec(s);if(!vm)return null;
  var clause=s.slice(vm.index+vm[0].length).split(/[.;!?]|,\s*(?:it'?s|it has|but|and (?:it|they|nobody|no one|still)|still|now)\b|\s(?:but|and still|yet)\s/i)[0].trim();
  clause=clause.replace(/^(that\s+|me\s+|us\s+|to\s+me\s+)/i,"").replace(/^(they|he|she|it|we)\s*(would|'d|will|'ll|could)\s+/i,"").trim();
  if(clause.length<4)return null;
  var today=new Date();today.setHours(0,0,0,0);
  var missedWords=PMISS.test(s),w=null,base;
  if(/\b(in|within)\s+(\d+|a|an|one|two|three|four|five|six|seven|ten|fourteen)\s+(working |business )?(day|days|week|weeks)\b/i.test(clause)){
    var ago=durDays(f&&f.dur);base=new Date(today.getTime()-ago*DAY);w=parseWhen(clause,base);
  }else if(/\b(mon|tue|wed|thu|fri|sat|sun)[a-z]*\b/i.test(clause)&&!/\bnext\b/i.test(clause)&&missedWords){
    base=new Date(today.getTime()-6*DAY);w=parseWhen(clause,base);
  }else w=parseWhen(clause,today);
  if(!w||!w.date)return null;
  var ymd=w.date.split("-").map(Number),start=new Date(ymd[0],ymd[1]-1,ymd[2]),end=null,allDay=!w.from;
  if(w.from){var a=w.from.split(":");start.setHours(+a[0],+a[1]);if(w.to){var b=w.to.split(":"),e=new Date(start);e.setHours(+b[0],+b[1]);if(e>start)end=e.toISOString()}}
  var pr={said:cap1(clause.replace(/[,\s]+$/,"")),party:(f&&f.party&&!/^the /.test(f.party)?f.party:(f&&f.party)?cap1(f.party.replace(/^the /,"")):(f&&f.resp==="landlord"?"Landlord":"")),dueAt:start.toISOString(),dueEnd:end,allDay:allDay,by:w.when==="by",ref:(f&&f.ref)||""};
  var last=end?new Date(end):new Date(start.getTime()+(allDay?DAY:HOUR));
  pr.past=last<new Date();
  return pr;
}
function shortTitle(text,f){`);

// 2. keep the suggestion with the new case
R(`  if(t.said&&t.said!==t.title)log(t,"In your words: “"+t.said.replace(/[.!]+$/,"")+"”");`,`  if(t.said&&t.said!==t.title)log(t,"In your words: “"+t.said.replace(/[.!]+$/,"")+"”");
  if(t.said&&t.mode!=="do"){var sgp=suggestPromise(t.said,t.facts);if(sgp)t.sugP=sgp}`);

// 3. show it back at the top of the case
R(`  h+='<section class="stack-s"><p class="eyebrow">'+({yours:"Needs you"`,`  if(t.sugP&&!t.sugDone&&s!=="done")h+=sugCard(t);
  h+='<section class="stack-s"><p class="eyebrow">'+({yours:"Needs you"`);
R(`function benefitNote(t){`,`function sugCard(t){
  var p=t.sugP,who=p.party||"They",wt=whenText(p).replace(/^By/,"by");
  var h='<section class="sheet stack-s sug" aria-labelledby="sugh"><p class="eyebrow">From what you wrote</p><h2 class="h3" id="sugh">'+esc(who)+' promised: “'+esc(p.said)+'”</h2>';
  h+='<p class="mono">'+esc(cap1(wt))+(p.ref?" · ref "+esc(p.ref):"")+'</p>';
  h+=p.past?'<p>That has passed. If it hasn’t happened, Sorted will help you chase it, quoting their words.</p>':'<p>Sorted can hold this and ask you afterwards whether it happened.</p>';
  h+='<div class="row eq">'+(p.past?'<button class="btn primary" data-a="sug-yes" data-v="missed">Yes, and it hasn’t happened</button>':'<button class="btn primary" data-a="sug-yes" data-v="open">Yes, keep track of it</button>')+'<button class="btn" data-a="sug-edit">Change the details</button></div>';
  h+='<button class="link" data-a="sug-no" style="align-self:flex-start">That’s not a promise</button></section>';
  return h;
}
function benefitNote(t){`);

// 4. what each answer does
R(`    case "missed":if(t){`,`    case "sug-yes":if(t&&t.sugP&&!t.sugDone){
      var sp=t.sugP,spr={id:uid(),said:sp.said,party:sp.party,dueAt:sp.dueAt,dueEnd:sp.dueEnd,allDay:sp.allDay,by:sp.by,ref:sp.ref,status:"open",loggedAt:nowIso(),src:"sentence"};
      t.sugDone=true;t.promises.push(spr);log(t,"They said: "+spr.said+", "+whenText(spr).replace(/^By/,"by")+(spr.ref?", ref "+spr.ref:"")+". Taken from what you wrote, and confirmed.");trackPromise(t,spr,false);
      if(b.getAttribute("data-v")==="missed"){spr.status="missed";spr.closedAt=nowIso();track("outcome_missed",t,{promise_id:spr.id});log(t,"It didn’t happen: "+spr.said+" ("+whenText(spr)+(spr.ref?", ref "+spr.ref:"")+").");t.board="yours";S.view.panel="call";S.draft={};commit();window.scrollTo(0,0)}
      else{t.board="waiting";var sem=defaultEmail(t);S.view.panel=(S.user&&!S.user.email)?"claim":null;S.draft={};commit();window.scrollTo(0,0);if(sem)toast("Sorted will email you a reminder. You can turn it off.")}
    }break;
    case "sug-edit":if(t&&t.sugP){var se=t.sugP,sd=new Date(se.dueAt);t.sugDone=true;t._dirty=true;S.view.panel="promise";S.draft={said:se.said,party:se.party,ref:se.ref,when:se.by?"by":"slot",date:ymdL(sd),from:se.allDay?"":pad2(sd.getHours())+":"+pad2(sd.getMinutes()),to:se.dueEnd?pad2(new Date(se.dueEnd).getHours())+":"+pad2(new Date(se.dueEnd).getMinutes()):""};save();render();window.scrollTo(0,0)}break;
    case "sug-no":if(t){t.sugDone=true;t._dirty=true;commit()}break;
    case "missed":if(t){`);

R(`.note p a.link{display:inline;min-height:0;padding:0}`,`.note p a.link{display:inline;min-height:0;padding:0}
.sug{border-left:6px solid var(--carbon)}`);

// 5. "by 5 October" is a date, not 5 o'clock (fixes the promise form's date reader too)
R(String.raw`(?! ?(days?|weeks?|hours?|mins?|minutes?|working|business))/`,String.raw`(?! ?(days?|weeks?|hours?|mins?|minutes?|working|business|(?:of )?(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)))/`);

fs.writeFileSync('public/index.html',s);
const EXPECT='4763b84e6e0ddbe22baaa8819dc28c8139e36b53';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v33 ok',h(s),s.length);
