const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='4763b84e6e0ddbe22baaa8819dc28c8139e36b53')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v34: the promise card is the first screen; paste a message; a short title; what Sorted has helped with ----

// 1. until the person answers the card, the card is the whole case page
R(`  if(t.sugP&&!t.sugDone&&s!=="done")h+=sugCard(t);
`,``);
R(`'</h1>'+'</section>';
`,`'</h1>'+'</section>';
  if(t.sugP&&!t.sugDone&&s!=="done")return h+sugCard(t)+'</main>';
`);

// 2. read a pasted message, not only a sentence: the line that carries a date becomes the proposed promise
R(`function shortTitle(text,f){`,String.raw`var MSGW=/\b(book|booked|booking|appointment|visit|engineer|technician|deliver|delivery|arrive|arriving|refund|refunded|process|processed|paid|payment|credit|credited|expect|scheduled|confirm|confirmed|will|due|collect|collection)\b/i;
function sugFromMessage(text,t,f){
  var raw=String(text||"").replace(/[’‘]/g,"'").replace(/\r/g,""),today=new Date();today.setHours(0,0,0,0);
  var parts=raw.replace(/([.!?])\s+/g,"$1\n").split(/\n+/).map(function(x){return x.trim()}).filter(function(x){return x.length>3});
  var best=null,bw=null;
  for(var i=0;i<parts.length;i++){var q=parts[i].replace(/\b(?:please )?allow (?:up to )?/i,"in ");var w=parseWhen(q,today);if(w&&w.date){if(!best||(MSGW.test(parts[i])&&!MSGW.test(best))){best=parts[i];bw=w}if(MSGW.test(parts[i]))break}}
  if(!best)return null;
  var ymd=bw.date.split("-").map(Number),start=new Date(ymd[0],ymd[1]-1,ymd[2]),end=null,allDay=!bw.from;
  if(bw.from){var a=bw.from.split(":");start.setHours(+a[0],+a[1]);if(bw.to){var b=bw.to.split(":"),e=new Date(start);e.setHours(+b[0],+b[1]);if(e>start)end=e.toISOString()}}
  var mf=caseFacts(raw),op=t&&(openPromise(t)||t.promises[t.promises.length-1]);
  var party=(op&&op.party)||(t&&t.call&&t.call.who)||(f&&f.party)||mf.party||"";party=party&&/^the /.test(party)?cap1(party.replace(/^the /,"")):party;
  var said=best.replace(/^(hi|hello|dear)\b[^,]*,\s*/i,"");if(said.length>160)said=said.slice(0,157).replace(/\s+\S*$/,"")+"…";
  var pr={said:cap1(said.replace(/[.\s]+$/,"")),party:party,dueAt:start.toISOString(),dueEnd:end,allDay:allDay,by:bw.when==="by",ref:parseRef(raw)||(f&&f.ref)||(op&&op.ref)||"",fromMsg:true};
  pr.past=(end?new Date(end):new Date(start.getTime()+(allDay?DAY:HOUR)))<new Date();
  return pr;
}
function shortTitle(text,f){`);
R(`  if(t.said&&t.mode!=="do"){var sgp=suggestPromise(t.said,t.facts);if(sgp)t.sugP=sgp}`,`  if(t.said&&t.mode!=="do"){var sgp=suggestPromise(t.said,t.facts)||(t.said.length>60?sugFromMessage(t.said,null,t.facts):null);if(sgp)t.sugP=sgp}
  if(t.facts)t.titleFb=!(t.facts.kind==="money"||t.facts.kind==="benefit"||(t.facts.item&&t.mode==="fix"));`);
// a pasted message's greeting is not a title
R(`  var c=String(text||"").split(/[.;!?]|,\\s|\\s[-–]\\s/)[0].trim();`,`  var c=String(text||"").replace(/^\\s*(hi|hello|dear|good (morning|afternoon|evening))\\b[^,.!\\n]*[,.!\\n]\\s*/i,"").split(/[.;!?\\n]|,\\s|\\s[-–]\\s/)[0].trim();`);
R(`<span class="hint">Tell Sorted in one sentence.</span><textarea id="f-case" name="casetext" rows="2"`,`<span class="hint">Tell Sorted in one sentence, or paste the message they sent you.</span><textarea id="f-case" name="casetext" rows="3"`);

// 3. inside a case: paste their latest message
R(`  h+='<section class="stack-s"><h2 class="h3">What’s happened so far</h2><ol class="thread">';`,`  if(s!=="done"&&S.view.panel!=="paste")h+='<button class="link" data-a="panel" data-p="paste" style="align-self:flex-start">Paste a message they sent</button>';
  h+='<section class="stack-s"><h2 class="h3">What’s happened so far</h2><ol class="thread">';`);
R(`  if(S.view.panel==="claim"){h+=claimBlock(t)}`,`  if(S.view.panel==="paste"&&s!=="done"){h+=pasteForm(t)}
  else if(S.view.panel==="claim"){h+=claimBlock(t)}`);
R(`function sugCard(t){`,`function pasteForm(t){
  var d=S.draft;
  return '<section class="sheet stack"><div class="stack-s"><p class="eyebrow">Their latest message</p><h2 class="h2">Paste what they sent</h2><p class="muted" style="font-size:16px">A text, an email or a chat message. Sorted looks for a date and a reference, and asks you before it changes anything.</p></div><form class="stack-s" data-f="paste"><label class="f"><span class="sr-only">Their message</span><textarea id="f-paste" name="paste" rows="6">'+esc(d.paste||"")+'</textarea></label>'+(d.err?'<p class="err">'+esc(d.err)+'</p>':'')+'<button class="btn primary block" type="submit">Read it</button><button class="btn block" type="button" data-a="panel" data-p="">Cancel</button></form></section>';
}
function sugCard(t){`);
R(`  if(k==="promise"){`,`  if(k==="paste"){
    var ptx=($("#f-paste").value||"").trim();d.paste=ptx;
    if(ptx.length<8){d.err="Paste their message first.";render();return}
    var psg=sugFromMessage(ptx,t,t.facts);
    if(!psg){d.err="Sorted couldn’t find a date or time in that. You can still log what they said yourself.";render();return}
    t.sugP=psg;t.sugDone=false;t._dirty=true;log(t,"Pasted a message they sent.");S.view.panel=null;S.draft={};commit();window.scrollTo(0,0);return;
  }
  if(k==="promise"){`);
R(`.sug{border-left:6px solid var(--carbon)}`,`.sug{border-left:6px solid var(--carbon)}
.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}`);

// 4. confirming: a new date replaces the old one, repair questions are skipped, and a long title becomes "British Gas · Fri 2 Oct"
R(`      t.sugDone=true;t.promises.push(spr);`,`      var sop=openPromise(t);if(sop){sop.status="replaced";sop.closedAt=nowIso();log(t,"They changed the date. It was "+whenText(sop)+".");track("outcome_rescheduled",t,{promise_id:sop.id,after_due:phase(sop)==="check"})}
      if(t.fix&&t.fix.step!=="done")t.fix.step="done";
      if(t.titleFb&&spr.party){t.title=spr.party+" · "+fmtDay(new Date(spr.dueAt)).replace(",","");t.titleFb=false}
      t.sugDone=true;t.promises.push(spr);`);
R(`(spr.ref?", ref "+spr.ref:"")+". Taken from what you wrote, and confirmed.");`,`(spr.ref?", ref "+spr.ref:"")+(sp.fromMsg?". Taken from their message, and confirmed.":". Taken from what you wrote, and confirmed."));`);
R(`h+=p.past?'<p>That has passed.`,`h+=sugMsgLine(p)+(p.past?'<p>That has passed.`);
R(`:'<p>Sorted can hold this and ask you afterwards whether it happened.</p>';`,`:'<p>Sorted can hold this and ask you afterwards whether it happened.</p>');`);
R(`function benefitNote(t){`,`function sugMsgLine(p){return p.fromMsg?'<p class="muted" style="font-size:16px">Found in the message you pasted. Check the date before you say yes.</p>':''}
function benefitNote(t){`);

// 5. the case list says the real next step after a missed promise or before the card is answered
R(`  if(!t.call)return "Next: "+lc1(`,`  if(t.sugP&&!t.sugDone)return "Next: check what they promised";
  var rmx=recentMiss(t);if(rmx&&!openPromise(t)&&(!t.call||!t.call.at||t.call.at<rmx.closedAt))return "Next: chase them";
  if(!t.call)return "Next: "+lc1(`);
R(`    t.call={who:who,ask:ask,via:via};`,`    t.call={who:who,ask:ask,via:via,at:nowIso()};`);

// 6. what Sorted has helped with: counted from the person's own cases, on their phone
R(`  if(!f.party)for(i=0;i<PARTIES.length;i++)`,`  m=/£\\s?(\\d{1,3}(?:,\\d{3})*|\\d+)(?:\\.(\\d{2}))?/.exec(s);if(m)f.amount=+(m[1].replace(/,/g,"")+"."+(m[2]||"0"));
  if(!f.party)for(i=0;i<PARTIES.length;i++)`);
R(`    if(done.length)h+='<details class="group">`,`    h+=winsBlock();
    if(done.length)h+='<details class="group">`);
R(`function sugMsgLine(p){`,`function winsBlock(){
  var real=S.tasks.filter(function(x){return !x.example}),fin=real.filter(function(x){return state(x)==="done"});
  if(!fin.length)return "";
  var kept=0,chased=0,money=0;
  real.forEach(function(x){(x.promises||[]).forEach(function(q){if(q.status==="kept")kept++});var ms=(x.promises||[]).filter(function(q){return q.status==="missed"});if(ms.length&&(x.call&&x.call.at&&x.call.at>ms[0].closedAt))chased++});
  fin.forEach(function(x){if(x.facts&&x.facts.kind==="money"&&x.facts.amount)money+=x.facts.amount});
  var bits=[fin.length+" case"+(fin.length===1?"":"s")+" finished"];
  if(kept)bits.push(kept+" promise"+(kept===1?"":"s")+" kept");
  if(chased)bits.push(chased+" missed promise"+(chased===1?"":"s")+" chased");
  if(money)bits.push("£"+money.toLocaleString("en-GB",{maximumFractionDigits:0})+" in refunds you told Sorted about");
  return '<section class="wins stack-s" aria-label="What Sorted has helped with"><p class="eyebrow">What Sorted has helped with</p><p>'+esc(bits.join(" · "))+'</p></section>';
}
function sugMsgLine(p){`);
R(`.sr-only{position:absolute;`,`.wins{border-top:2px solid var(--rule);padding-top:12px}
.sr-only{position:absolute;`);

// 7. the card says where the promise came from
R(`<p class="eyebrow">From what you wrote</p>`,`<p class="eyebrow">'+(p.fromMsg?"From their message":"From what you wrote")+'</p>`);

fs.writeFileSync('public/index.html',s);
const EXPECT='d54f773aefab1862a7e67dd8ff46766eff470bc5';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v34 ok',h(s),s.length);
