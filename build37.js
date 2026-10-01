const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='35b20af9067754120a6c26345454a35ab85d74f7')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v37: fixes from the full audit (1 October 2026) ----

/* ===== A. dates and promises ===== */

// A1, A9, A10: back-date a "within N days" promise only when the text says how long ago it was made; never by multiples of 24 hours
R(String.raw`    var ago=durDays(f&&f.dur);base=new Date(today.getTime()-ago*DAY);w=parseWhen(clause,base);`,String.raw`    var ago=elapsedDays(s);base=ago?addDays(today,-ago):new Date();w=parseWhen(clause,base);`);
R(String.raw`    base=new Date(today.getTime()-6*DAY);w=parseWhen(clause,base);
  }else w=parseWhen(clause,today);`,String.raw`    base=addDays(today,-6);w=parseWhen(clause,base);
  }else w=parseWhen(clause,new Date());
  if(!w&&/\b\d{1,2}(?:st|nd|rd|th)?(?: of)? (?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)|\b\d{1,2}\/\d{1,2}\b/i.test(clause))w=parseWhen(clause,addDays(today,-60));`);
R(String.raw`function durDays(d){`,String.raw`function addDays(d,n){var x=new Date(d);x.setDate(x.getDate()+n);return x}
var DURN_RE="(?:\\d+|a|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|a few|several)\\s+(?:day|week|month)s?";
function elapsedDays(s){var m=new RegExp("\\b("+DURN_RE+")\\s+(?:ago|later|on)\\b","i").exec(s)||new RegExp("\\b(?:it'?s|it has|it's now|i'?ve|i have|we'?ve|we have)?\\s*been(?: waiting)?(?: for)?\\s+("+DURN_RE+")\\b","i").exec(s)||new RegExp("\\bwaiting (?:for )?("+DURN_RE+")\\b","i").exec(s);return m?durDays(m[1]):0}
function durDays(d){`);
// A2: only words about the visit or payment not happening back-date a weekday
R(String.raw`var PMISS=/\b(didn.?t|did not|never|no[- ]?show|hasn.?t|haven.?t|has not|have not|nobody|no one|missed|wasn.?t|weren.?t|still (?:no|not|waiting))\b/i;`,String.raw`var PMISS=/\b(?:didn.?t|did not|never) (?:come|turn up|turned up|show|showed|arrive|arrived|happen|call|ring|pay|refund|deliver)|\bno[- ]?show\b|\b(?:nobody|no one) (?:came|turned up|showed|arrived|called|rang)\b|\bmissed (?:the|my|our) (?:appointment|visit|slot)\b/i;`);
// A3: a price is never a time ("£12.50" is not 12:50)
R(String.raw`var s=" "+String(text||"").toLowerCase().replace(/[’‘]/g,"'")`,String.raw`var s=" "+String(text||"").toLowerCase().replace(/[£$€]\s?\d[\d,]*(?:\.\d+)?/g," ").replace(/[’‘]/g,"'")`);
// A4: "a.m." and "£12.50" don't end a sentence
R(String.raw`var s=String(text||"").replace(/[’‘]/g,"'"),vm=PVERB.exec(s);if(!vm)return null;`,String.raw`var s=String(text||"").replace(/[’‘]/g,"'").replace(/\b([ap])\.m\./gi,"$1m"),vm=PVERB.exec(s);if(!vm)return null;`);
R(String.raw`.split(/[.;!?]|,\s*(?:it'?s|it has|but|and (?:it|they|nobody|no one|still)|still|now)\b|\s(?:but|and still|yet)\s/i)[0].trim();`,String.raw`.split(/[.;!?](?=\s|$)|,\s*(?:it'?s|it has|but|and (?:it|they|nobody|no one|still)|still|now)\b|\s(?:but|and still|yet)\s/i)[0].trim();`);
R(String.raw`var raw=String(text||"").replace(/[’‘]/g,"'").replace(/\r/g,"")`,String.raw`var raw=String(text||"").replace(/[’‘]/g,"'").replace(/\r/g,"").replace(/\b([ap])\.m\./gi,"$1m")`);
// A5: £1500 is 1500
R(String.raw`m=/£\s?(\d{1,3}(?:,\d{3})*|\d+)(?:\.(\d{2}))?/.exec(s);`,String.raw`m=/£\s?(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d{1,2}))?\b/.exec(s);`);
// A11: ordinary words are not companies or items
R(String.raw`[/\bapple\b/i,"Apple"]`,String.raw`[/\bApple\b/,"Apple"]`);
R(String.raw`[/\bsky\b/i,"Sky"]`,String.raw`[/\bSky\b|\bSKY\b/,"Sky"]`);
R(String.raw`[/\blaptop\b/i,"Laptop"],[/\bphone\b/i,"Phone"],[/\bwindow/i,"Window"]`,String.raw`[/\blaptop\b/i,"Laptop"],[/\bphone screen\b|\bmobile phone\b|\bmy phone (?:is|has|won.?t|keeps|stopped)/i,"Phone"],[/\bwindows? (?:is|are|won.?t|broken|smashed|cracked|leaks?|leaking)\b/i,"Window"]`);
// A12: one reference reader
R(String.raw`  for(i=0;i<ITEMS.length;i++)if(ITEMS[i][0].test(s)){f.item=ITEMS[i][1];break}
  var N=`,String.raw`  if(!f.ref){var pr2=parseRef(s);if(pr2)f.ref=pr2}
  for(i=0;i<ITEMS.length;i++)if(ITEMS[i][0].test(s)){f.item=ITEMS[i][1];break}
  var N=`);
// A13: opening hours are not a promise
R(String.raw`for(var i=0;i<parts.length;i++){var q=parts[i]`,String.raw`for(var i=0;i<parts.length;i++){if(/\b(lines are open|opening hours|office hours|we(?:'re| are) open|open (?:from )?(?:mon|monday)|call us|our team is available)\b/i.test(parts[i]))continue;var q=parts[i]`);
// A15: "Change the details" then Cancel brings the card back; it is answered only when the promise is saved
R(`    case "sug-edit":if(t&&t.sugP){var se=t.sugP,sd=new Date(se.dueAt);t.sugDone=true;t._dirty=true;`,`    case "sug-edit":if(t&&t.sugP){var se=t.sugP,sd=new Date(se.dueAt);t.sugEditing=true;`);
R(`  if(t.sugP&&!t.sugDone&&s!=="done")return h+sugCard(t)+'</main>';`,`  if(t.sugP&&!t.sugDone&&s!=="done"&&S.view.panel!=="promise")return h+sugCard(t)+'</main>';`);
R(`    t.promises.push(pr);t.board=pr.dueAt?"waiting":"yours";`,`    if(t.sugEditing){t.sugEditing=false;t.sugDone=true}
    t.promises.push(pr);t.board=pr.dueAt?"waiting":"yours";`);

/* ===== B. saving and step records ===== */

// A7, A8: one save per case at a time; a case still saving is not overwritten by the first load from the server
R(`    if(!t._dirty)return;t._dirty=false;
    var body=clean(t);
    sb.from("tasks").upsert({id:t.id,data:body}).then(function(r){
      if(r.error){t._dirty=true;cacheWrite();offline(true);return}`,`    if(!t._dirty)return;
    if(t._saving){t._again=true;return}
    t._dirty=false;t._saving=true;
    var body=clean(t);
    var fin=function(){t._saving=false;if(t._again){t._again=false;t._dirty=true;save()}};
    sb.from("tasks").upsert({id:t.id,data:body}).then(function(r){
      fin();
      if(r.error){t._dirty=true;cacheWrite();offline(true);return}`);
R(`    },function(){t._dirty=true;cacheWrite();offline(true)});
  });`,`    },function(){t._saving=false;t._dirty=true;cacheWrite();offline(true)});
  });`);
R(`function clean(t){var c={};for(var k in t)if(k!=="_dirty")c[k]=t[k];return c}`,`function clean(t){var c={};for(var k in t)if(k.charAt(0)!=="_")c[k]=t[k];return c}`);
R(`    var dirty=S.tasks.filter(function(t){return t._dirty});`,`    var dirty=S.tasks.filter(function(t){return t._dirty||t._saving});`);
// A18: only the step records that were sent are removed from the queue
R(`function saveQ(){EVQ=evq().slice(-50);`,`function saveQ(){EVQ=evq().slice(-200);`);
R(`if(!r||!r.error){EVQ=evq().slice(batch.length);saveQ();if(EVQ.length)sendEvents()}`,`if(!r||!r.error){EVQ=evq().filter(function(x){return batch.indexOf(x)<0});saveQ();if(EVQ.length)sendEvents()}`);

/* ===== C. reading files ===== */

// A14: a picture finishes only into the box it was picked for; A17: pdf.js is closed after use
R(`  ocrStatus(isPdf?"Reading the PDF on your phone…"`,`  var tok=S.ocrTok={v:S.view.name+":"+(S.view.id||"")+":"+target};
  ocrStatus(isPdf?"Reading the PDF on your phone…"`);
R(`if(isPdf){pdfToText(file).then(function(r){if(typeof r==="string"){ocrDone(r,target);return}ocrStatus("This PDF is a scan. Reading its first page like a photo…");readImage(r.canvas,target)})`,`if(isPdf){pdfToText(file).then(function(r){if(typeof r==="string"){ocrDone(r,target,tok);return}ocrStatus("This PDF is a scan. Reading its first page like a photo…");readImage(r.canvas,target,tok)})`);
R(`  readImage(file,target);
}
function ocrDone(raw,target){`,`  readImage(file,target,tok);
}
function ocrDone(raw,target,tok){
  if(tok&&(tok!==S.ocrTok||tok.v!==S.view.name+":"+(S.view.id||"")+":"+target))return;`);
R(`function readImage(file,target){`,`function readImage(file,target,tok){`);
R(`.then(function(r){if(wk)wk.terminate();ocrDone(r&&r.data&&r.data.text,target)})`,`.then(function(r){if(wk)wk.terminate();ocrDone(r&&r.data&&r.data.text,target,tok)})`);
R(`if(tx.length>=20)return tx;`,`if(tx.length>=20){try{doc.destroy()}catch(e){}return tx}`);
R(`return pg.render({canvasContext:cv.getContext("2d"),viewport:vp}).promise.then(function(){return {canvas:cv}})`,`return pg.render({canvasContext:cv.getContext("2d"),viewport:vp}).promise.then(function(){try{doc.destroy()}catch(e){}return {canvas:cv}})`);

/* ===== D. privacy ===== */

// B1: keep at most 300 characters of a pasted message as "In your words"; read the whole thing for dates first
R(`  if(d.facts){t.facts=d.facts;t.said=d.said||"";`,`  if(d.facts){t.facts=d.facts;t.said=String(d.said||"").length>300?String(d.said).slice(0,297).replace(/\\s+\\S*$/,"")+"…":String(d.said||"");`);
R(`var lng=t.said.length>100||/\\n/.test(t.said),sgp=lng?(sugFromMessage(t.said,null,t.facts)||suggestPromise(t.said,t.facts)):(suggestPromise(t.said,t.facts)||(t.said.length>60?sugFromMessage(t.said,null,t.facts):null));`,`var fs0=String(d.said||t.said),lng=fs0.length>100||/\\n/.test(fs0),sgp=lng?(sugFromMessage(fs0,null,t.facts)||suggestPromise(fs0,t.facts)):(suggestPromise(fs0,t.facts)||(fs0.length>60?sugFromMessage(fs0,null,t.facts):null));`);
R(`  ocrStatus("Done. Check the words above, fix anything it misread, then tap "+(target==="f-paste"?"Read it":"Start")+".");`,`  ocrStatus("Done. Check the words above. Delete anything Sorted doesn’t need, like account numbers or health details, then tap "+(target==="f-paste"?"Read it":"Start")+".");`);
R(`<span class="hint">Tell Sorted in one sentence, or paste the message they sent you.</span>`,`<span class="hint">Tell Sorted in one sentence, or paste the message they sent you. Leave out bank details and health information.</span>`);
R(`Who did you speak to?<span class="hint">Optional. Their name, if they gave it.</span>`,`Who did you speak to?<span class="hint">Optional. A first name or their role is enough.</span>`);
// B2, B4, B5, B6, B8, B14: the notice says what really happens
R(`If you send a helper link, that person sees that one case until you switch the link off.</p>`,`If you send a helper link, that person sees that one case until you switch the link off, or until 30 days pass without a change to it. Sorted deletes its copy for the link after 90 days.</p>`);
R(`You can copy or delete everything at any time from “Your data”.`,`You can delete a case, or everything, at any time.`);
R(`You can turn this off in “Your data”. These records are deleted after 12 months, or straight away if you delete your account.</p>'+`,`Step records are linked to your account but hold no case details. You can turn them off in “Your data”; that applies to the phone you’re using. They are deleted after 12 months, or straight away if you delete your account.</p>'+
  '<p><strong>Why Sorted can use your data.</strong> Sorted holds your cases to give you the service you asked for. It keeps step records because it has a legitimate interest in learning whether the pilot works, and you can turn them off. Sorted is for people aged 18 and over.</p>'+
  '<p><strong>Other people in your cases.</strong> Your cases can include other people’s names, such as who you spoke to. Only add what you need to follow up.</p>'+`);
R(`'<p><strong>Who else handles it.</strong> Supabase stores your cases on servers in London. Vercel hosts the website. Resend sends Sorted’s emails. Vercel and Resend are US companies, so your email address may be processed in the US under their data protection terms. None of them may use your data for anything else.</p>'+`,`'<p><strong>Who else handles it.</strong> Supabase stores your cases on servers in London. Vercel hosts the website. Resend sends Sorted’s emails. All three are US companies, so your data may be processed in the US under their data protection terms, and none of them may use it for anything else.</p>'+
  '<p>Like any website, Sorted’s pages load some parts from other services, which see your device’s internet address but never your cases: jsDelivr (the database connection code, and the tools that read screenshots and PDFs) and Google Fonts (the lettering). The services that run Sorted keep internet addresses in short-lived logs.</p>'+`);
// B13
R(`Copy everything Sorted holds about your cases.`,`Copy all your cases. For your step records or anything else Sorted holds, email kofiniiakwei@gmail.com.`);

// B11: delete one case
R(`if(s!=="done"&&S.view.panel!=="done")h+='<button class="link" data-a="panel" data-p="done">Mark this finished</button>';`,`if(s!=="done"&&S.view.panel!=="done")h+='<button class="link" data-a="panel" data-p="done">Mark this finished</button>';
  if(!t.example&&S.view.panel!=="delcase")h+='<button class="link" data-a="panel" data-p="delcase" style="align-self:flex-start;color:var(--danger)">Delete this case</button>';`);
R(`  if(S.view.panel==="paste"&&s!=="done"){h+=pasteForm(t)}`,`  if(S.view.panel==="delcase"){h+='<section class="sheet stack-s" aria-labelledby="delh"><h2 class="h2" id="delh">Delete this case?</h2><p>It’s removed from Sorted straight away, with its history, any helper link and its reminders. This can’t be undone.</p><div class="row eq"><button class="btn danger" data-a="case-del">Delete it</button><button class="btn" data-a="panel" data-p="">Keep it</button></div></section>'}
  else if(S.view.panel==="paste"&&s!=="done"){h+=pasteForm(t)}`);
R(`    case "mail-open":if(t){`,`    case "case-del":if(t&&!t.example){var dx=t;S.view.panel=null;sb.from("tasks").delete().eq("id",dx.id).then(function(r){if(r&&r.error){toast("Couldn’t delete it. Try again.");render();return}
        if(dx.shareToken)sb.from("shares").delete().eq("task_id",dx.id).then(function(){},function(){});
        sb.from("reminders").delete().eq("task_id",dx.id).then(function(){},function(){});
        try{sb.rpc("remove_helper",{p_task_id:dx.id}).then(function(){},function(){})}catch(e){}
        S.tasks=S.tasks.filter(function(x){return x.id!==dx.id});cacheWrite();go({name:"home"});toast("Case deleted")},function(){toast("Couldn’t delete it. Check your connection.");render()})}break;
    case "mail-open":if(t){`);

/* ===== E. accessibility ===== */

// focus goes back to the right control (panels included); opening a panel, an error or the match prompt moves focus to it
R(`key='[data-a="'+ae.getAttribute("data-a")+'"]'+(ae.getAttribute("data-id")?'[data-id="'+ae.getAttribute("data-id")+'"]':'')+(ae.getAttribute("data-v")?'[data-v="'+ae.getAttribute("data-v")+'"]':'')}`,`key='[data-a="'+ae.getAttribute("data-a")+'"]'+(ae.getAttribute("data-id")?'[data-id="'+ae.getAttribute("data-id")+'"]':'')+(ae.getAttribute("data-v")?'[data-v="'+ae.getAttribute("data-v")+'"]':'')+(ae.getAttribute("data-p")!==null?'[data-p="'+ae.getAttribute("data-p")+'"]':'')}`);
R(`  if(inApp){var back=null;try{back=key&&document.querySelector(key)}catch(e){}if(back&&back.offsetParent!==null){try{back.focus({preventScroll:true})}catch(e){}}else focusMain()}
}`,`  if(inApp){var back=null;try{back=key&&document.querySelector(key)}catch(e){}if(back&&back.offsetParent!==null){try{back.focus({preventScroll:true})}catch(e){}}else focusMain()}
  a11yPass(app);
}
function a11yPass(app){
  /* chip rows are groups named by their question */
  [].forEach.call(app.querySelectorAll(".chips:not([role])"),function(cg){var pv=cg.previousElementSibling,nm=pv?(pv.textContent||"").trim():"";cg.setAttribute("role","group");if(nm&&nm.length<80)cg.setAttribute("aria-label",nm)});
  /* links that open a new tab say so */
  [].forEach.call(app.querySelectorAll('a[target="_blank"]'),function(a){if(!a.querySelector(".sr-only")){var sp=document.createElement("span");sp.className="sr-only";sp.textContent=" (opens in a new tab)";a.appendChild(sp)}});
  /* answer buttons on Home name their case */
  [].forEach.call(app.querySelectorAll(".slip [data-a]"),function(bt){if(bt.getAttribute("aria-label")||bt.tagName!=="BUTTON")return;var sl=bt.closest(".slip"),ti=sl&&sl.querySelector(".slip-title");if(ti&&!bt.closest(".slip-main"))bt.setAttribute("aria-label",(bt.textContent||"").trim()+": "+(ti.textContent||"").trim())});
  /* errors are announced, tied to their field, and the field gets focus */
  var er=app.querySelector("form .err");
  if(er){er.setAttribute("role","alert");er.id=er.id||"form-err";var fm=er.closest("form"),fld=fm&&fm.querySelector('textarea,input:not([type=hidden]):not([type=file]),select');
    if(fld){fld.setAttribute("aria-invalid","true");fld.setAttribute("aria-describedby",er.id)}
    var ek=(S.view.name||"")+":"+(S.view.panel||"")+":"+er.textContent;if(ek!==S._lastErr&&fld){S._lastErr=ek;try{fld.focus({preventScroll:true});fld.scrollIntoView({block:"center"})}catch(e){}}}
  else S._lastErr=null;
  /* a newly opened panel: focus its first field */
  var pk=(S.view.name||"")+":"+(S.view.id||"")+":"+(S.view.panel||"");
  if(S.view.panel&&pk!==S._lastPanel&&!er){var pf=app.querySelector('main form textarea,main form input:not([type=hidden]):not([type=file]),main [data-a="case-del"]');if(pf){try{pf.focus({preventScroll:true});pf.scrollIntoView({block:"center"})}catch(e){}}}
  S._lastPanel=pk;
  /* the match prompt */
  var mb=app.querySelector('[data-a="match-add"]');if(mb&&S.draft.matchId&&S._matchShown!==S.draft.matchId){S._matchShown=S.draft.matchId;try{mb.focus({preventScroll:true});mb.scrollIntoView({block:"center"})}catch(e){}}
  if(!S.draft.matchId)S._matchShown=null;
}`);
R(`<div class="note stack-s" role="status"><p><strong>This looks like it’s about your`,`<div class="note stack-s"><p><strong>This looks like it’s about your`);
// Home has a page heading once there are cases
R(`var active=yours.length+waiting.length+upcoming.length,entryFirst=!active&&S.loaded;`,`var active=yours.length+waiting.length+upcoming.length,entryFirst=!active&&S.loaded;
  if(!entryFirst)h+='<h1 class="sr-only">Your cases</h1>';`);
// the toast is read out by a region that is always there, and stays longer
R(`<div id="toast" class="toast" role="status" aria-live="polite" hidden>`,`<div id="sr-live" class="sr-only" role="status" aria-live="polite"></div><div id="toast" class="toast" aria-hidden="true" hidden>`);
R(`function toast(msg){var el=$("#toast");el.textContent=msg;el.hidden=false;clearTimeout(toast.t);toast.t=setTimeout(function(){el.hidden=true},2400)}`,`function toast(msg){var el=$("#toast"),lv=$("#sr-live");el.textContent=msg;el.hidden=false;if(lv){lv.textContent="";setTimeout(function(){lv.textContent=msg},60)}clearTimeout(toast.t);toast.t=setTimeout(function(){el.hidden=true},4000)}`);
// visible focus on text fields, nothing hidden under the sticky header, readable placeholders, 44px Done header
R(`input:focus,textarea:focus,input[type=email]:focus{border-color:var(--carbon);outline:none;box-shadow:0 0 0 3px var(--carbon-soft)}`,`input:focus,textarea:focus,input[type=email]:focus{border-color:var(--carbon);outline:3px solid var(--focus);outline-offset:2px;box-shadow:none}
html{scroll-padding-top:90px}
::placeholder{color:var(--ink-2);opacity:1}
details.group>summary{min-height:44px;align-items:center}`);

fs.writeFileSync('public/index.html',s);
const EXPECT='bcb902ed24eed8dd7a7c91add6944e216b7e3529';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v37 ok',h(s),s.length);
