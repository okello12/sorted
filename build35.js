const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='d54f773aefab1862a7e67dd8ff46766eff470bc5')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v35: read a screenshot or photo on the phone itself; the picture is never uploaded ----

// 1. the reader: loaded only when someone picks a picture, pinned and integrity-checked
R(`function pasteForm(t){`,`var OCRV="5.1.1",OCRP=null;
function loadOcr(){
  if(window.Tesseract)return Promise.resolve();
  if(OCRP)return OCRP;
  OCRP=new Promise(function(res,rej){var sc=document.createElement("script");sc.src="https://cdn.jsdelivr.net/npm/tesseract.js@"+OCRV+"/dist/tesseract.min.js";sc.integrity="sha384-GJqSu7vueQ9qN0E9yLPb3Wtpd7OrgK8KmYzC8T1IysG1bcvxvIO4qtYR/D3A991F";sc.crossOrigin="anonymous";sc.onload=function(){res()};sc.onerror=function(){OCRP=null;rej(new Error("load"))};document.head.appendChild(sc)});
  return OCRP;
}
function ocrStatus(msg){var el=document.getElementById("ocr-status");if(el)el.textContent=msg}
function readPicture(file,target){
  if(!file)return;
  if(!/^image\\//.test(file.type||"")){ocrStatus("That isn’t a picture. Add a screenshot or a photo.");return}
  ocrStatus("Reading the picture on your phone. This can take a few seconds the first time…");
  var wk=null;
  loadOcr().then(function(){return Tesseract.createWorker("eng",1,{workerPath:"https://cdn.jsdelivr.net/npm/tesseract.js@"+OCRV+"/dist/worker.min.js",corePath:"https://cdn.jsdelivr.net/npm/tesseract.js-core@"+OCRV,langPath:"https://cdn.jsdelivr.net/npm/@tesseract.js-data/eng@1.0.0/4.0.0_best_int"})})
  .then(function(w){wk=w;return w.recognize(file)})
  .then(function(r){if(wk)wk.terminate();
    var txt=String(r&&r.data&&r.data.text||"").replace(/[ \\t]+/g," ").replace(/([^\\n])\\n(?!\\n)/g,"$1 ").replace(/\\n{3,}/g,"\\n\\n").trim();
    if(txt.length<8){ocrStatus("Sorted couldn’t find any words in that picture. You can type or paste the message instead.");return}
    var ta=document.getElementById(target);if(ta){ta.value=txt;S.draft[ta.name==="paste"?"paste":"casetext"]=txt}
    ocrStatus("Done. Check the words above, fix anything it misread, then tap "+(target==="f-paste"?"Read it":"Start")+".");
  })
  .catch(function(){if(wk)try{wk.terminate()}catch(e){}ocrStatus("Sorted couldn’t read that picture. Check your connection, or type or paste the message instead.")});
}
function picPicker(target){
  return '<label class="link pic" style="align-self:flex-start">Add a screenshot or photo instead<input type="file" accept="image/*" data-ocr="'+target+'" class="sr-only"></label><p class="muted" id="ocr-status" role="status" aria-live="polite" style="font-size:15px;margin-top:-4px">Sorted reads the picture on your phone. The picture isn’t uploaded.</p>';
}
function pasteForm(t){`);
R(`document.addEventListener("change",function(e){`,`document.addEventListener("change",function(e){
  var oc=e.target&&e.target.getAttribute&&e.target.getAttribute("data-ocr");if(oc){readPicture(e.target.files&&e.target.files[0],oc);e.target.value="";return}`);

// 2. offered where a message can go in: inside a case, and when starting one
R(`<textarea id="f-paste" name="paste" rows="6">'+esc(d.paste||"")+'</textarea></label>`,`<textarea id="f-paste" name="paste" rows="6">'+esc(d.paste||"")+'</textarea></label>'+picPicker("f-paste")+'`);
R(`'<button class="btn primary block" type="submit">Start</button></form>`,`picPicker("f-case")+'<button class="btn primary block" type="submit">Start</button></form>`);
R(`.sr-only{position:absolute;`,`label.pic{cursor:pointer;display:inline-flex;align-items:center;min-height:44px}
label.pic:focus-within{outline:3px solid var(--focus);outline-offset:2px}
.sr-only{position:absolute;`);

// 3. the notice says so
R(`'<p class="muted" style="font-size:16px">Please don’t add bank details or medical information.</p></section>';`,`'<p>If you add a screenshot or photo, Sorted reads it on your phone. The picture isn’t uploaded. Only the words you then choose to save are kept, like anything you type.</p>'+
  '<p class="muted" style="font-size:16px">Please don’t add bank details or medical information.</p></section>';`);

// 4. longer text reads as a message first, so the card quotes the whole sentence
R(`var sgp=suggestPromise(t.said,t.facts)||(t.said.length>60?sugFromMessage(t.said,null,t.facts):null);`,`var lng=t.said.length>100||/\\n/.test(t.said),sgp=lng?(sugFromMessage(t.said,null,t.facts)||suggestPromise(t.said,t.facts)):(suggestPromise(t.said,t.facts)||(t.said.length>60?sugFromMessage(t.said,null,t.facts):null));`);

// 5. a sender's name at the start of a text ("British Gas: ...") is not part of the quote
R(String.raw`var said=best.replace(/^(hi|hello|dear)\b[^,]*,\s*/i,"");`,String.raw`var said=best.replace(/^(hi|hello|dear)\b[^,]*,\s*/i,"").replace(/^[A-Z][A-Za-z0-9 &'.-]{1,30}:\s+/,"");`);

fs.writeFileSync('public/index.html',s);
const EXPECT='12edea4f6033abee97c752f403bca4bb25914ac5';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v35 ok',h(s),s.length);
