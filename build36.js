const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='12edea4f6033abee97c752f403bca4bb25914ac5')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v36: messages find their case; who you spoke to; open in your email app; PDFs ----

// 1. a message about a company you already have a case with goes into that case, if you say so
R(`    var cm=caseMode(ctx),cfx=caseFacts(ctx),ctitle=shortTitle(ctx,cfx);`,`    var cm=caseMode(ctx),cfx=caseFacts(ctx),ctitle=shortTitle(ctx,cfx);
    if(!d.skipMatch){var mtc=matchCase(cfx);if(mtc){d.matchId=mtc.id;render();return}}
    d.skipMatch=false;d.matchId=null;`);
R(`'<button class="btn primary block" type="submit">Start</button></form>`,`(d.matchId&&task(d.matchId)?matchBlock(task(d.matchId)):'<button class="btn primary block" type="submit">Start</button>')+'</form>`);
R(`function pasteForm(t){`,`function partyOf(x){var op=openPromise(x)||(x.promises||[])[x.promises.length-1];return String((x.facts&&x.facts.party)||(op&&op.party)||(x.call&&x.call.who)||(x.fix&&x.fix.party)||"").replace(/^the /i,"").toLowerCase()}
function matchCase(f){
  if(!f||(!f.party&&!f.ref))return null;
  var fp=String(f.party||"").replace(/^the /i,"").toLowerCase();
  return S.tasks.filter(function(x){return !x.example&&state(x)!=="done"&&(
    (f.ref&&((x.promises||[]).some(function(q){return q.ref&&q.ref.toUpperCase()===f.ref})||(x.facts&&x.facts.ref===f.ref)))||
    (fp&&fp.length>2&&partyOf(x)===fp))})[0]||null;
}
function matchBlock(x){
  return '<div class="note stack-s" role="status"><p><strong>This looks like it’s about your “'+esc(x.title)+'” case.</strong> Add it there, so everything stays in one place?</p><div class="row eq"><button type="button" class="btn primary" data-a="match-add">Add to that case</button><button type="button" class="btn" data-a="match-new">Start a new case</button></div></div>';
}
function pasteForm(t){`);
R(`    case "missed":if(t){`,`    case "match-add":{var mx=task(d.matchId),mtx=d.casetext||"";if(!mx)break;S.composeOpen=false;
      var mf=Object.assign({},mx.facts||{},caseFacts(mtx)),msg=sugFromMessage(mtx,mx,mf)||suggestPromise(mtx,mf);
      log(mx,"Added a message: “"+(mtx.length>140?mtx.slice(0,137).replace(/\\s+\\S*$/,"")+"…":mtx)+"”");mx._dirty=true;
      if(msg){mx.sugP=msg;mx.sugDone=false;save();go({name:"task",id:mx.id})}
      else{save();go({name:"task",id:mx.id});S.view.panel="paste";S.draft={paste:mtx,err:"Added to the case. Sorted couldn’t find a date in it, so nothing else changed."};render()}
      break}
    case "match-new":{d.skipMatch=true;d.matchId=null;var mfm=document.querySelector('form[data-f="case"]');if(mfm){if(mfm.requestSubmit)mfm.requestSubmit();else mfm.dispatchEvent(new Event("submit",{cancelable:true,bubbles:true}))}break}
    case "missed":if(t){`);

// 2. after a call: who you spoke to, kept with the promise and used when chasing
R(`  h+='<label class="f">Who said it<input type="text" id="f-party2" name="party" value="'+esc(d.party!==undefined?d.party:(t.call?t.call.who:(rn?(t.renew.kind==="visa"?"UKVI":t.renew.kind==="tv"?"TV Licensing":["mot"].indexOf(t.renew.kind)>=0?"MOT centre":(t.renew.provider||"GOV.UK")):"")))+'"></label>';`,`  h+='<label class="f">Who said it<input type="text" id="f-party2" name="party" value="'+esc(d.party!==undefined?d.party:(t.call?t.call.who:(rn?(t.renew.kind==="visa"?"UKVI":t.renew.kind==="tv"?"TV Licensing":["mot"].indexOf(t.renew.kind)>=0?"MOT centre":(t.renew.provider||"GOV.UK")):"")))+'"></label>';
  if(!rn)h+='<label class="f">Who did you speak to?<span class="hint">Optional. Their name, if they gave it.</span><input type="text" id="f-spoke" name="spoke" autocomplete="off" value="'+esc(d.spoke||"")+'"></label>';`);
R(`var pr={id:uid(),said:said,party:party,dueAt:dueAt,dueEnd:end,allDay:allDay,by:when==="by",ref:ref,status:"open",loggedAt:nowIso()};`,`var spv=$("#f-spoke"),spoke=spv?spv.value.trim().slice(0,60):"";d.spoke=spoke;
    var pr={id:uid(),said:said,party:party,dueAt:dueAt,dueEnd:end,allDay:allDay,by:when==="by",ref:ref,status:"open",loggedAt:nowIso()};if(spoke)pr.spoke=spoke;`);
R(`log(t,"They said: "+said+(pr.dueAt?", "+whenText(pr).replace(/^By/,"by"):". No date given")+(ref?", ref "+ref:"")+".");`,`log(t,"They said: "+said+(pr.dueAt?", "+whenText(pr).replace(/^By/,"by"):". No date given")+(ref?", ref "+ref:"")+(spoke?" (you spoke to "+spoke+")":"")+".");`);
R(`". I was told: “"+m.said.replace(/[.!]+$/,"")`,`". I was told"+(m.spoke?" by "+m.spoke:"")+": “"+m.said.replace(/[.!]+$/,"")`);

// 3. emails and app messages: open it in your email app, or copy it; the time is logged
R(`  h+='<div class="stack-s"><p style="font-weight:600">'+w.say+'</p><p class="note">'+esc(c.ask)+'</p></div>';`,`  h+='<div class="stack-s"><p style="font-weight:600">'+w.say+'</p><p class="note">'+esc(c.ask)+'</p>'+sendRow(t,c)+'</div>';`);
R(`function partyOf(x){`,`function refOf(x){var op=openPromise(x)||(x.promises||[])[x.promises.length-1];return (op&&op.ref)||(x.facts&&x.facts.ref)||(x.fix&&x.fix.jobRef)||""}
function sendRow(t,c){
  if(c.via==="email"){var rf=refOf(t),subj=rf?"Reference "+rf:t.title;return '<div class="row eq"><a class="btn" data-a="mail-open" href="mailto:?subject='+encodeURIComponent(subj)+'&amp;body='+encodeURIComponent(c.ask)+'">Open in your email app</a><button class="btn" data-a="copy-ask">Copy the message</button></div>'}
  if(c.via==="account"||c.via==="letter")return '<button class="btn block" data-a="copy-ask">Copy the message</button>';
  return "";
}
function partyOf(x){`);
R(`    case "match-add":{`,`    case "mail-open":if(t){log(t,"Opened the message in your email app.");commit()}break;
    case "copy-ask":if(t&&t.call){copy(t.call.ask,t.call.via==="letter"?"Copied. Paste it into your letter.":"Copied. Paste it into their app or website.");log(t,"Copied the message.");save()}break;
    case "match-add":{`);

// 4. PDFs: text read on the phone; a scanned PDF's first page is read like a photo
R(`function ocrStatus(msg){`,`var PDFV="3.11.174",PDFP=null;
function loadPdf(){
  if(window.pdfjsLib)return Promise.resolve();
  if(PDFP)return PDFP;
  PDFP=new Promise(function(res,rej){var sc=document.createElement("script");sc.src="https://cdn.jsdelivr.net/npm/pdfjs-dist@"+PDFV+"/build/pdf.min.js";sc.integrity="sha384-/1qUCSGwTur9vjf/z9lmu/eCUYbpOTgSjmpbMQZ1/CtX2v/WcAIKqRv+U1DUCG6e";sc.crossOrigin="anonymous";sc.onload=function(){window.pdfjsLib.GlobalWorkerOptions.workerSrc="https://cdn.jsdelivr.net/npm/pdfjs-dist@"+PDFV+"/build/pdf.worker.min.js";res()};sc.onerror=function(){PDFP=null;rej(new Error("load"))};document.head.appendChild(sc)});
  return PDFP;
}
function pdfToText(file){
  var doc;
  return loadPdf().then(function(){return file.arrayBuffer()}).then(function(buf){return window.pdfjsLib.getDocument({data:buf,isEvalSupported:false,disableFontFace:true}).promise})
  .then(function(d0){doc=d0;var n=Math.min(doc.numPages,3),ps=[];for(var i=1;i<=n;i++)ps.push(doc.getPage(i).then(function(pg){return pg.getTextContent()}).then(function(tc){return tc.items.map(function(it){return it.str+(it.hasEOL?"\\n":" ")}).join("")}));return Promise.all(ps)})
  .then(function(pages){var tx=pages.join("\\n\\n").replace(/[ \\t]+/g," ").trim();if(tx.length>=20)return tx;
    return doc.getPage(1).then(function(pg){var vp=pg.getViewport({scale:2}),cv=document.createElement("canvas");cv.width=vp.width;cv.height=vp.height;return pg.render({canvasContext:cv.getContext("2d"),viewport:vp}).promise.then(function(){return {canvas:cv}})})});
}
function ocrStatus(msg){`);
R(`  if(!/^image\\//.test(file.type||"")){ocrStatus("That isn’t a picture. Add a screenshot or a photo.");return}
  ocrStatus("Reading the picture on your phone. This can take a few seconds the first time…");
  var wk=null;
  loadOcr()`,`  var isPdf=file.type==="application/pdf"||/\\.pdf$/i.test(file.name||"");
  if(!isPdf&&!/^image\\//.test(file.type||"")){ocrStatus("That isn’t a picture or a PDF. Add a screenshot, a photo or a PDF.");return}
  ocrStatus(isPdf?"Reading the PDF on your phone…":"Reading the picture on your phone. This can take a few seconds the first time…");
  if(isPdf){pdfToText(file).then(function(r){if(typeof r==="string"){ocrDone(r,target);return}ocrStatus("This PDF is a scan. Reading its first page like a photo…");readImage(r.canvas,target)}).catch(function(){ocrStatus("Sorted couldn’t read that PDF. Check your connection, or type or paste the message instead.")});return}
  readImage(file,target);
}
function ocrDone(raw,target){
  var txt=String(raw||"").replace(/[ \\t]+/g," ").replace(/([^\\n])\\n(?!\\n)/g,"$1 ").replace(/\\n{3,}/g,"\\n\\n").trim();
  if(txt.length<8){ocrStatus("Sorted couldn’t find any words in that. You can type or paste the message instead.");return}
  var ta=document.getElementById(target);if(ta){ta.value=txt;S.draft[ta.name==="paste"?"paste":"casetext"]=txt}
  ocrStatus("Done. Check the words above, fix anything it misread, then tap "+(target==="f-paste"?"Read it":"Start")+".");
}
function readImage(file,target){
  var wk=null;
  loadOcr()`);
R(`  .then(function(r){if(wk)wk.terminate();
    var txt=String(r&&r.data&&r.data.text||"").replace(/[ \\t]+/g," ").replace(/([^\\n])\\n(?!\\n)/g,"$1 ").replace(/\\n{3,}/g,"\\n\\n").trim();
    if(txt.length<8){ocrStatus("Sorted couldn’t find any words in that picture. You can type or paste the message instead.");return}
    var ta=document.getElementById(target);if(ta){ta.value=txt;S.draft[ta.name==="paste"?"paste":"casetext"]=txt}
    ocrStatus("Done. Check the words above, fix anything it misread, then tap "+(target==="f-paste"?"Read it":"Start")+".");
  })`,`  .then(function(r){if(wk)wk.terminate();ocrDone(r&&r.data&&r.data.text,target)})`);
R(`Add a screenshot or photo instead<input type="file" accept="image/*"`,`Add a screenshot, photo or PDF instead<input type="file" accept="image/*,application/pdf,.pdf"`);
R(`Sorted reads the picture on your phone. The picture isn’t uploaded.`,`Sorted reads it on your phone. Nothing is uploaded.`);
R(`If you add a screenshot or photo, Sorted reads it on your phone. The picture isn’t uploaded.`,`If you add a screenshot, photo or PDF, Sorted reads it on your phone. The file isn’t uploaded.`);

fs.writeFileSync('public/index.html',s);
const EXPECT='35b20af9067754120a6c26345454a35ab85d74f7';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v36 ok',h(s),s.length);
