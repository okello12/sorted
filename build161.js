const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='c29a75e77782dd541161bd1bc87e8d64cb895957')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v161: Something I own isn't working, stage 1 (docs/PRODUCT_PHASE1.md). The product logic is in the pure modules
// under src/product, put into the page at the marker below by tools/inline_modules.js (the last step of all.js). This
// layer is the page's thin part: the start inside the repair door (photo of the label, or typed), "Check what Sorted
// read", the product on the case (t.prod), its ledger rows and history, the safety decision on every save, and the
// serial masked wherever text leaves the case. Direct edits where the page decides; no new wrapper round a function.

// 1. The modules and the glue sit just before boot().
const GLUE=String.raw`/*@product-modules*/
/* ---- v161: the page's side of the product journey (docs/PRODUCT_PHASE1.md). It renders and records; the modules decide. ---- */
var PROD_TRACK161=false;/* usage records wait for migration 30 (the step names); switched on in the release that applies it */
function prodTrack161(name,t,x){if(!PROD_TRACK161)return;try{track(name,t,x||{})}catch(e){}}
var PR161=Product.record;
var PROD_ITEM161={washing_machine:"Washing machine",boiler:"Boiler or heating",fridge_freezer:"Fridge or freezer"};
var PROD_SAY161={brand:"Make",model:"Model",serial:"Serial number",category:"What it is",retailer:"Bought from",bought:"Bought on"};
var PROD_LG161={brand:"prod_brand",model:"prod_model",serial:"prod_serial",category:"prod_category",retailer:"buy_retailer",bought:"buy_date"};
Object.keys(PROD_LG161).forEach(function(k){LG_TYPE[PROD_LG161[k]]=PROD_SAY161[k]});
/* A value as it may be shown: the serial masked unless shown on purpose, a kind by its name, a date written out. */
function prodShow161(rec,k,full){var v=PR161.value(rec,k)||PR161.candidate(rec,k);if(!v)return "";if(k==="serial")return full?v:PR161.mask(v);if(k==="category")return PR161.catName(v);if(k==="bought")return Product.route.fmt(v);return v}
function prodItem161(k){var p=k==="fix"&&S.draft&&S.draft.prod161;if(!p||!p.ok)return "";var c=PR161.value(p.rec,"category");return c?(PROD_ITEM161[c]||"Something else"):""}
function prodScrubAll161(x){x=String(x==null?"":x);(S.tasks||[]).forEach(function(t){if(t&&t.prod)x=PR161.scrub(t.prod,x)});return x}
function prodSafeCard161(t,c){if(!t||!t.prod||!c)return c;try{return JSON.parse(PR161.scrub(t.prod,JSON.stringify(c)))}catch(e){return c}}
function prodPick161(lab,cap,cls,target){return '<label class="btn'+(cls||"")+' prod161-pick">'+lab+'<input type="file" accept="image/*" data-ocr="'+(target||"f-prod")+'"'+(cap?' capture="environment"':'')+' class="sr-only"></label>'}
function prodWhere161(p){return '<button type="button" class="link" data-a="prod161-where" aria-expanded="'+(p&&p.where?"true":"false")+'" style="align-self:flex-start">Show me where to look</button>'+(p&&p.where?'<p class="note" style="margin:0">The label is often inside the door or lid, on the back, or underneath. Look for the words Model, Type or E-Nr. A serial number is often marked S/N.</p>':'')}
function prodCats161(rec){var cur=PR161.value(rec,"category")||PR161.candidate(rec,"category");return '<fieldset class="f"><legend class="h3">What is it?</legend><div class="chips">'+PR161.CATS.filter(function(x){return x[0]!=="car"}).map(function(x){return '<label class="chip gi-chip"><input type="radio" name="prod-cat" value="'+x[0]+'"'+(cur===x[0]?' checked':'')+' class="sr-only"> '+esc(x[1])+'</label>'}).join("")+'</div></fieldset>'}
/* The start, inside the repair door. Nothing here is saved until Start. */
function prodStart161(){
  var p=S.draft&&S.draft.prod161,h='<section class="prod161 stack-s" aria-labelledby="prod161-h">',st='<p class="muted" id="ocr-status" role="status" aria-live="polite" style="font-size:15px;margin:0">'+(p&&p.msg?esc(p.msg):'Sorted reads the label on your phone. The photo isn’t uploaded or kept.')+'</p>';
  if(!p)return h+'<h2 class="h3" id="prod161-h">Something you own isn’t working?</h2><p class="muted" style="margin:0">Photograph it or tell Sorted what it is. A photo of the label with the model number works best.</p><div class="row" style="flex-wrap:wrap">'+prodPick161("Take a photo",true," primary")+prodPick161("Choose a photo")+'</div><button type="button" class="link" data-a="prod161-type" style="align-self:flex-start">Type the make and model</button>'+st+'<p class="muted" style="margin:0;font-size:15px">Or tell Sorted below what needs repairing.</p></section>';
  var r=p.rec,has=["brand","model","serial","category"].some(function(k){return prodShow161(r,k)})||(p.models||[]).length;
  if(p.ok)return h+'<h2 class="h3" id="prod161-h">The product</h2><p style="margin:0">'+esc(prodLine161(r))+'</p><div class="row" style="flex-wrap:wrap"><button type="button" class="link" data-a="prod161-edit">Change</button><button type="button" class="link" data-a="prod161-drop">Remove</button></div></section>';
  if(p.edit){
    var sc=PR161.candidate(r,"serial")||PR161.value(r,"serial");
    h+='<h2 class="h3" id="prod161-h" tabindex="-1">Make and model</h2><form class="stack-s" data-f="prod161" data-m="edit">';
    h+='<label class="f">Make<input type="text" id="prod-brand" autocomplete="off" value="'+esc(prodShow161(r,"brand"))+'" placeholder="For example: Bosch"></label>';
    h+='<label class="f">Model<span class="hint">On the label, next to Model, Type or E-Nr.</span><input type="text" id="prod-model" class="mono" autocomplete="off" autocapitalize="characters" spellcheck="false" value="'+esc(PR161.value(r,"model")||PR161.candidate(r,"model")||(p.models||[])[0]||"")+'"></label>';
    h+='<label class="f">Serial number<span class="hint">Optional. Sorted shows it as ••••1234.'+(sc?' Leave this blank to keep '+esc(PR161.mask(sc))+'.':'')+'</span><input type="text" id="prod-serial" class="mono" autocomplete="off" autocapitalize="characters" spellcheck="false"></label>';
    if(sc)h+='<label class="chip gi-chip" style="align-self:flex-start"><input type="checkbox" name="prod-noserial" class="sr-only"> Don’t keep the serial number</label>';
    h+=prodCats161(r)+(p.err?'<p class="err" role="alert">'+esc(p.err)+'</p>':'')+'<button class="btn primary block" type="submit">Save these details</button><button type="button" class="link" data-a="prod161-cancel" style="align-self:flex-start">Cancel</button></form>'+st;
    return h+'</section>';
  }
  if(!has)return h+'<h2 class="h3" id="prod161-h" tabindex="-1">Sorted couldn’t read that photo</h2><p role="alert" style="margin:0">It couldn’t find a make, model or serial number. Nothing has been saved.</p><div class="row" style="flex-wrap:wrap">'+prodPick161("Retake photo",true," primary")+prodPick161("Choose another photo")+'</div><button type="button" class="link" data-a="prod161-type" style="align-self:flex-start">Type the make and model</button>'+prodWhere161(p)+st+'</section>';
  var row=function(k,v){return '<div class="prod161-row"><dt>'+PROD_SAY161[k]+'</dt><dd>'+v+'</dd></div>'};
  var b=prodShow161(r,"brand"),ms=p.models||[],m=PR161.candidate(r,"model")||PR161.value(r,"model"),sr=prodShow161(r,"serial",!!p.show);
  h+='<h2 class="h3" id="prod161-h" tabindex="-1">Check what Sorted read</h2>'+(p.fail?'<p role="alert" class="err" style="margin:0">Sorted couldn’t read the last photo. The details below are from before.</p>':'')+'<form class="stack-s" data-f="prod161" data-m="ok"><dl class="prod161-dl" style="margin:0">';
  h+=row("brand",b?esc(b):'<span class="muted">Not found</span>');
  if(ms.length>1&&!m)h+=row("model",'<span class="muted">Sorted found more than one. Which is the model?</span><span class="chips">'+ms.map(function(x,i){return '<label class="chip gi-chip"><input type="radio" name="prod-model" value="'+esc(x)+'"'+(i===0?' checked':'')+' class="sr-only"> <span class="mono">'+esc(x)+'</span></label>'}).join("")+'</span>');
  else h+=row("model",m?'<span class="mono">'+esc(m)+'</span>'+(p.how==="unlabelled"&&PR161.candidate(r,"model")?'<span class="cf-src">Sorted isn’t sure this is the model. Check it against the label.</span>':''):'<span class="muted">Not known yet</span>');
  if(sr)h+=row("serial",'<span class="mono">'+esc(sr)+'</span> <button type="button" class="link" data-a="prod161-reveal">'+(p.show?"Hide":"Show")+'</button>');
  h+='</dl>'+prodCats161(r);
  if(!m&&ms.length<2)h+='<div class="note stack-s"><p style="margin:0">To find the right support page, Sorted needs the model.</p><div class="row" style="flex-wrap:wrap">'+prodPick161("Photograph the label",true)+'<button type="button" class="btn" data-a="prod161-edit">Type the model</button></div>'+prodWhere161(p)+'</div>';
  h+='<div class="row" style="flex-wrap:wrap"><button class="btn primary" type="submit">'+(m||ms.length>1?"Looks right":"Continue without it")+'</button><button type="button" class="btn" data-a="prod161-edit">Change</button></div><p class="muted" style="margin:0;font-size:15px">Nothing is saved until you press Start.</p></form>'+st;
  return h+'</section>';
}
/* One line for a product, from facts only: "Bosch washing machine, model WGG244ZCGB, serial ••••6789" */
function prodLine161(r){var a=[],l=PR161.label(r),m=PR161.value(r,"model"),s=PR161.value(r,"serial");if(l)a.push(l);if(m)a.push("model "+m);if(s)a.push("serial "+PR161.mask(s));return a.join(", ")||"No details yet"}
function prodHasFact161(r){return PR161.FIELDS.some(function(k){return PR161.isFact(PR161.field(r,k))})}
/* The label read: candidates only. A brand or kind alone is progress, never a model. */
function prodOcr161(raw,target,tok){
  if(tok&&(tok!==S.ocrTok||tok.v!==S.view.name+":"+(S.view.id||"")+":"+target))return;
  var x=ocrClean(raw),r=Product.intake.readLabel(x),now=Date.now(),p=S.draft.prod161&&!S.draft.prod161.ok?S.draft.prod161:{rec:PR161.make("",now),src:"label"},rec=p.rec;
  var any=!!(r.brand||r.models.length||r.serial);
  p.fail=false;p.edit=false;p.ok=false;p.msg="";
  if(any){if(r.brand)PR161.propose(rec,"brand",r.brand,"label_photo",now);if(r.model)PR161.propose(rec,"model",r.model,"label_photo",now);if(r.serial)PR161.propose(rec,"serial",r.serial,"label_photo",now);if(r.category)PR161.propose(rec,"category",r.category,"label_photo",now);
    if(r.models.length)p.models=r.models;p.how=r.modelHow||p.how||"";p.src="label";p.msg=r.model||r.models.length?"Label read. Check what Sorted found.":"Sorted found the make but not the model.";}
  else{p.fail=true;p.msg="Sorted couldn’t read that photo. Nothing has been saved."}
  S.draft.prod161=p;prodTrack161(any?"product_candidate_found":"product_read_failed",null,{brand:!!r.brand,models:r.models.length,serial:!!r.serial});
  render();var hd=$("#prod161-h");if(hd){hd.scrollIntoView({block:"start"});try{hd.focus({preventScroll:true})}catch(e){}}
}
/* What the person accepts or types. Equal to the reading: confirmed. Different: corrected, the reading kept. */
function prodEditField161(rec,k,v,now){v=String(v||"").trim();var c=PR161.candidate(rec,k),cv=k==="model"||k==="serial"?v.replace(/\s+/g,"").toUpperCase():v;
  if(!v){if(c)PR161.reject(rec,k,now);else if(PR161.value(rec,k))PR161.forget(rec,k,now);return}
  if(c&&c===cv)PR161.confirm(rec,k,now);else PR161.set(rec,k,v,now)}
function prodCat161(form,rec,now){var e=form.querySelector('input[name="prod-cat"]:checked'),v=e?e.value:"";if(!v)return;if(PR161.candidate(rec,"category")===v)PR161.confirm(rec,"category",now);else PR161.set(rec,"category",v,now)}
document.addEventListener("submit",function(e){var f=e.target,k=f&&f.getAttribute&&f.getAttribute("data-f");if(k!=="prod161"&&k!=="prod161c")return;
  e.preventDefault();e.stopImmediatePropagation();var now=Date.now();
  if(k==="prod161"){var p=S.draft&&S.draft.prod161;if(!p)return;var rec=p.rec,m=f.getAttribute("data-m");p.err="";
    if(m==="edit"){var sv=String(($("#prod-serial")||{}).value||"").trim(),nos=f.querySelector('input[name="prod-noserial"]:checked');
      if(sv&&sv.replace(/\s+/g,"").length<4){p.err="A serial number has at least 4 letters or numbers. Leave it blank if you don’t have it.";render();return}
      prodEditField161(rec,"brand",($("#prod-brand")||{}).value,now);prodEditField161(rec,"model",($("#prod-model")||{}).value,now);
      if(nos){if(PR161.candidate(rec,"serial"))PR161.reject(rec,"serial",now);else if(PR161.value(rec,"serial"))PR161.forget(rec,"serial",now)}
      else if(sv)prodEditField161(rec,"serial",sv,now);else if(PR161.candidate(rec,"serial"))PR161.confirm(rec,"serial",now);
    }else{["brand","serial"].forEach(function(x){if(PR161.candidate(rec,x))PR161.confirm(rec,x,now)});
      var mc=f.querySelector('input[name="prod-model"]:checked');if(mc){PR161.propose(rec,"model",mc.value,"label_photo",now);PR161.confirm(rec,"model",now)}else if(PR161.candidate(rec,"model"))PR161.confirm(rec,"model",now)}
    prodCat161(f,rec,now);p.edit=false;p.show=false;
    if(!prodHasFact161(rec)){S.draft.prod161=null;render();return}
    p.ok=true;prodTrack161("product_confirmed",null,{src:p.src||"label",model:!!PR161.value(rec,"model"),serial:!!PR161.value(rec,"serial"),cat:PR161.value(rec,"category")||"none"});
    render();var gw=$("#gi-what");if(gw)gw.focus();return}
  var t=S.view.id?task(S.view.id):null;if(!t||!t.prod)return;var r=t.prod,before={};PR161.FIELDS.forEach(function(x){before[x]=prodShow161(r,x)});
  var sv2=String(($("#prod-serial")||{}).value||"").trim(),nos2=f.querySelector('input[name="prod-noserial"]:checked');
  if(sv2&&sv2.replace(/\s+/g,"").length<4){S.view.prodErr="A serial number has at least 4 letters or numbers.";render();return}
  S.view.prodErr="";prodEditField161(r,"brand",($("#prod-brand")||{}).value,now);prodEditField161(r,"model",($("#prod-model")||{}).value,now);
  if(nos2)PR161.forget(r,"serial",now);else if(sv2)prodEditField161(r,"serial",sv2,now);prodCat161(f,r,now);
  PR161.FIELDS.forEach(function(x){var a=before[x],b=prodShow161(r,x);if(a!==b)log(t,PROD_SAY161[x]+(b?(a?" changed by you from "+a+" to "+b:" added by you: "+b):" removed by you")+".")});
  t._dirty=true;save();S.view.panel=null;render();
},true);
document.addEventListener("click",function(e){var b=e.target.closest&&e.target.closest("[data-a]");if(!b)return;var a=b.getAttribute("data-a");if(a.indexOf("prod161-")!==0)return;
  var p=S.draft&&S.draft.prod161,t=S.view.id?task(S.view.id):null,foc=function(sel){var el=$(sel);if(el)try{el.focus()}catch(e){}};
  if(a==="prod161-type"){S.draft.prod161={rec:PR161.make("",Date.now()),src:"manual",edit:true};prodTrack161("product_flow_started",null,{src:"manual"});render();foc("#prod-brand");return}
  if(a==="prod161-edit"&&p){p.edit=true;p.ok=false;render();foc("#prod-brand");return}
  if(a==="prod161-cancel"&&p){if(p.src==="manual"&&!prodHasFact161(p.rec))S.draft.prod161=null;else{p.edit=false;p.ok=prodHasFact161(p.rec)&&!["brand","model","serial","category"].some(function(k){return PR161.candidate(p.rec,k)})}render();foc("#prod161-h");return}
  if(a==="prod161-reveal"&&p){p.show=!p.show;render();return}
  if(a==="prod161-where"&&p){p.where=!p.where;render();return}
  if(a==="prod161-where"&&!p){S.draft.prod161={rec:PR161.make("",Date.now()),src:"label",where:true};render();return}
  if(a==="prod161-drop"){S.draft.prod161=null;render();foc("#prod161-h");return}
  if(a==="prod161-reveal-case"&&t){S.view.prodShow=S.view.prodShow===t.id?null:t.id;render();return}
  if(a==="prod161-copy"&&t&&t.prod){var full=PR161.value(t.prod,"serial");if(!full)return;try{navigator.clipboard.writeText(full).then(function(){toast("Serial number copied")},function(){toast("Couldn’t copy. Tap Show and copy it yourself.")})}catch(er){toast("Couldn’t copy. Tap Show and copy it yourself.")}return}
});
/* A photo picked for the label starts the flow; the read itself goes through the page's usual reader. */
document.addEventListener("change",function(e){var i=e.target;if(i&&i.getAttribute&&i.getAttribute("data-ocr")==="f-prod"&&i.files&&i.files.length)prodTrack161("product_flow_started",null,{src:"label"})},true);
/* The product joins the case at Start. Its history says where each detail came from. */
function prodAttach161(t,p){
  var r=p.rec;r.id=t.id+":p";t.prod=r;prodNoSerialRef161(t);
  PR161.FIELDS.forEach(function(k){var fl=PR161.field(r,k);if(!PR161.isFact(fl))return;var v=prodShow161(r,k),said=PROD_SAY161[k]+": "+v,read=(fl.was||[]).filter(function(w){return w.st==="candidate"}).pop();
    log(t,fl.st==="corrected"&&read?said+", corrected by you. Sorted had read "+(k==="serial"?PR161.mask(read.v):k==="category"?PR161.catName(read.v):read.v)+".":fl.src==="label_photo"?said+", read from the label photo and confirmed by you.":fl.src==="receipt"?said+", read from the receipt and confirmed by you.":said+", from you.")});
  prodSync161(t);
}
var PROD_SAFE_SAY161={STOP_USE:"stop using it.",PROFESSIONAL_ONLY:"only a qualified person should work on it.",OFFICIAL_INFORMATION_ONLY:"official information and contact only, no checks.",SAFE_EXTERNAL_CHECKS:"nothing said so far sounds dangerous."};
/* A serial number is not the case's reference. Sorted's reference reader can take "Serial SN98765432" in the person's
   words for one; once the product holds that serial, the reading is dropped everywhere a reference lives. */
function prodNoSerialRef161(t){
  var sr=PR161.value(t.prod,"serial")||"",S1=sr.toUpperCase(),same=function(v){return S1&&String(v||"").replace(/\s+/g,"").toUpperCase()===S1};if(!S1)return;
  if(t.facts&&same(t.facts.ref))t.facts.ref="";
  var tt=String(t.title||"");if(S1&&tt.toUpperCase().slice(-S1.length)===S1&&/[·•]\s*$/.test(tt.slice(0,-S1.length))){tt=tt.slice(0,-S1.length).replace(/\s*[·•]\s*$/,"");t.title=tt||PR161.label(t.prod)||"Repair"}if(t.fix&&same(t.fix.jobRef))t.fix.jobRef="";if(t.sugP&&same(t.sugP.ref))t.sugP.ref="";
  if(t.refs)t.refs=t.refs.filter(function(r){return !same(r.v)});(t.promises||[]).forEach(function(q){if(same(q.ref))q.ref=""});
  (t.ledger||[]).forEach(function(r){if(r.type==="ref"&&same(r.v)){r.v=PR161.mask(r.v);if(r.st!=="superseded")r.st="rejected"}});
}
/* On every save of a case with a product: the facts the repair engine reads, and the safety decision with its rules. */
function prodSync161(t){
  if(!t||!t.prod||t._deleted)return;var now=Date.now(),o=PR161.forFix(t.prod,now);prodNoSerialRef161(t);
  if(t.fix)["item","model","seller","age"].forEach(function(k){if(o[k]&&t.fix[k]!==o[k])t.fix[k]=o[k]});
  var words=[String(t.said||""),String(t.fix&&t.fix.detail||"")],all=words.join(". ");
  var dec=Product.safety.decide({category:PR161.value(t.prod,"category"),words:words,answers:{unsafe:!!t.safety},legacyDanger:looksUnsafe(all)||looksUrgent(all)},now);
  var old=t.prod.safety,sig=function(x){return x?x.result+"|"+x.matched_rules.join(",")+"|"+x.rule_version:""};
  if(sig(old)!==sig(dec)){if(old)(t.prod.safetyWas=t.prod.safetyWas||[]).push(old);t.prod.safety=dec;
    if(dec.result==="STOP_USE"&&!t.safety){t.safety=true;log(t,"Safety stop shown. Told to switch off only if safe and get qualified help.")}
    if(dec.result==="STOP_USE"||dec.result==="PROFESSIONAL_ONLY"||(old&&old.result!==dec.result))log(t,"Sorted’s safety rules ("+dec.rule_version+"): "+PROD_SAFE_SAY161[dec.result]);
    if(dec.result==="STOP_USE")prodTrack161("safety_stopped",t,{cls:dec.product_class,rules:dec.matched_rules.length})}
  prodLedger161(t);t._dirty=true;
}
/* Ledger rows for the product: every state of every field once, in order. A serial only ever masked. */
function prodLedger161(t){
  if(!t||!t.prod||!t.prod.f)return false;var ch=false;
  PR161.FIELDS.forEach(function(k){var fl=PR161.field(t.prod,k);if(!fl)return;var all=(fl.was||[]).concat([{v:fl.v,st:fl.st,src:fl.src,at:fl.at}]),n=fl.lgN||0;
    for(var i=n;i<all.length;i++){var x=all[i];if(!x.v)continue;var st=x.st==="candidate"?"read":x.st==="rejected"?"rejected":(x.st==="confirmed"||x.st==="corrected")?"confirmed":"";if(!st)continue;
      var v=k==="serial"?PR161.mask(x.v):k==="category"?PR161.catName(x.v):k==="bought"?Product.route.fmt(x.v):x.v,ph=x.src==="label_photo"||x.src==="receipt";
      ch=lgPut(t,{type:PROD_LG161[k],v:v,by:x.st==="corrected"||!ph?"you":"photo",src:x.st==="corrected"||!ph?"":(x.src==="receipt"?"the receipt":"the label"),st:st,cby:st==="confirmed"?"you":null},new Date(x.at||now0161()).toISOString())||ch}
    if(fl.lgN!==all.length){fl.lgN=all.length;ch=true}});
  return ch;
}
function now0161(){return Date.now()}
/* The product on the case page. */
function prodCard161(t){
  if(!t||!t.prod)return "";var r=t.prod,show=S.view.prodShow===t.id;
  var row=function(k){var fl=PR161.field(r,k),on=PR161.isFact(fl),v=on?prodShow161(r,k,show):"",how=!on?"":fl.st==="corrected"?"corrected by you":fl.src==="label_photo"?"read from the label, confirmed by you":fl.src==="receipt"?"read from the receipt, confirmed by you":"from you";
    return '<div class="prod161-row"><dt>'+PROD_SAY161[k]+'</dt><dd>'+(on?'<span'+(k==="model"||k==="serial"?' class="mono"':'')+'>'+esc(v)+'</span>':'<span class="muted">Not known yet</span>')+(k==="serial"&&on?' <button type="button" class="link" data-a="prod161-reveal-case">'+(show?"Hide":"Show")+'</button> <button type="button" class="link" data-a="prod161-copy">Copy</button>':'')+(how?' <span class="cf-src">'+esc(how)+'</span>':'')+'</dd></div>'};
  var d=r.safety;
  return '<section class="prod161-card stack-s"><h2 class="h3">'+esc(PR161.label(r)||"The product")+'</h2><dl class="prod161-dl" style="margin:0">'+["brand","model","serial","category"].map(row).join("")+'</dl>'+(d?'<p class="prod161-safety'+(d.result==="STOP_USE"?" err":"")+'" style="margin:0">'+esc(d.reason)+'</p>':'')+'<button type="button" class="link" data-a="panel" data-p="prod161c" style="align-self:flex-start">Change these details</button></section>';
}
function prodEditCase161(t){
  var r=t.prod||PR161.make(t.id+":p",Date.now()),s=PR161.value(r,"serial");
  return '<section class="sheet stack"><h2 class="h2" id="prod161-h" tabindex="-1">The product’s details</h2><form class="stack-s" data-f="prod161c">'+
    '<label class="f">Make<input type="text" id="prod-brand" autocomplete="off" value="'+esc(PR161.value(r,"brand"))+'"></label>'+
    '<label class="f">Model<input type="text" id="prod-model" class="mono" autocomplete="off" autocapitalize="characters" spellcheck="false" value="'+esc(PR161.value(r,"model"))+'"></label>'+
    '<label class="f">Serial number<span class="hint">'+(s?'Leave this blank to keep '+esc(PR161.mask(s))+'.':'Optional. Sorted shows it as ••••1234.')+'</span><input type="text" id="prod-serial" class="mono" autocomplete="off" autocapitalize="characters" spellcheck="false"></label>'+
    (s?'<label class="chip gi-chip" style="align-self:flex-start"><input type="checkbox" name="prod-noserial" class="sr-only"> Remove the serial number</label>':'')+prodCats161(r)+
    (S.view.prodErr?'<p class="err" role="alert">'+esc(S.view.prodErr)+'</p>':'')+'<button class="btn primary block" type="submit">Save</button><button type="button" class="link" data-a="panel" data-p="" style="align-self:flex-start">Cancel</button></form><p class="muted" style="margin:0;font-size:15px">Sorted keeps the earlier details in the case’s history.</p></section>';
}
`;
R('function boot(){',GLUE+'function boot(){');

// 2. The start leads the repair door; a confirmed kind picks the matching chip.
R(`'><form class="stack-s" data-f="gi" data-k="'+k+'">';`,`'>'+(k==="fix"?prodStart161():"")+'<form class="stack-s" data-f="gi" data-k="'+k+'">';`);
R('((ex&&ex.item?x===ex.item:i===0&&k!=="fix")?','((prodItem161(k)?x===prodItem161(k):ex&&ex.item?x===ex.item:i===0&&k!=="fix")?');

// 3. The confirmed product travels with the start (guided form, the box, the planning question, a safety stop) and joins
// the case in newTask. Only a product the person accepted travels.
R('S.draft={casetext:gtx,gfrom:gk2,gwho:gk2!=="fix"?gv.who:"",gwhat:gv.what||""};','S.draft={casetext:gtx,gfrom:gk2,gwho:gk2!=="fix"?gv.who:"",gwhat:gv.what||"",prod161:gk2==="fix"&&d.prod161&&d.prod161.ok?d.prod161:null};');
R('docConfirmed:d.docConfirmed||null};','docConfirmed:d.docConfirmed||null,prod161:d.prod161&&d.prod161.ok?d.prod161:null};');
R('S.pendingSafety={title:ctitle,said:ctx,facts:cfx};','S.pendingSafety={title:ctitle,said:ctx,facts:cfx,prod161:d.prod161&&d.prod161.ok?d.prod161:null};');
R('facts:S.pendingSafety&&S.pendingSafety.facts};render()}','facts:S.pendingSafety&&S.pendingSafety.facts,prod161:S.pendingSafety&&S.pendingSafety.prod161};render()}');
R('gv.item=gsel("gi-item");gv.resp=gsel("gi-resp");','gv.item=gsel("gi-item");gv.resp=gsel("gi-resp");if(gk2==="fix"&&d.prod161&&d.prod161.ok&&(!gv.item||gv.item==="Something else")){var pc161=PR161.value(d.prod161.rec,"category");if(pc161&&pc161!=="other")gv.item=PR161.catName(pc161)}');
R('var cm=caseMode(ctx),','var cm=d.prod161&&d.prod161.ok?"fix":caseMode(ctx),');
R('S.tasks.unshift(t);save();trackStart(t,d);','if(d.prod161&&d.prod161.ok&&mode!=="do")prodAttach161(t,d.prod161);S.tasks.unshift(t);save();trackStart(t,d);');

// A label photo goes to the product reader, never into the box.
R('ocrDone=function(raw,target,tok){MASK145C.n=0;','ocrDone=function(raw,target,tok){if(target==="f-prod")return prodOcr161(raw,target,tok);MASK145C.n=0;');

// 4. On the case: the product card, its edit panel, its ledger rows. Sorted's own washing-machine checks are not the
// maker's, so a product case never offers them.
R('S._info=frCard(t)+uCard(t);','S._info=frCard(t)+prodCard161(t)+uCard(t);');
R(`if(S.view.panel==="rename")return h+renameForm(t)+'</main>';`,`if(S.view.panel==="rename")return h+renameForm(t)+'</main>';
  if(S.view.panel==="prod161c")return h+prodEditCase161(t)+'</main>';`);
R('try{if(lgSync(t)){t._dirty=true;setTimeout(save,0)}}catch(e){}','try{if(lgSync(t)+prodLedger161(t)){t._dirty=true;setTimeout(save,0)}}catch(e){}');
R('if(st==="checks")return t.safety||','if(st==="checks")return !!t.prod||t.safety||');
R('var skipChecks=t.safety||','var skipChecks=!!t.prod||t.safety||');
R('function savePrep155(){','function savePrep155(){try{(S.tasks||[]).forEach(function(t){if(t&&t._dirty&&!t._deleted&&t.prod)prodSync161(t)})}catch(e){}');

// What happened, on the case's Now card, is something that happened, not a detail the person confirmed.
R('return !/^(?:Opened from the |Started\\b|In your words)/.test(x.label||"")','return !/^(?:Opened from the |Started\\b|In your words|Sorted’s safety rules|(?:Make|Model|Serial number|What it is): )/.test(x.label||"")');

// 5. The serial never leaves in full by itself: the assistant, a helper's link, Home's titles and error reports.
R('context:aiContext(t),text:String(text||"")','context:(t&&t.prod?PR161.scrub(t.prod,aiContext(t)):aiContext(t)),text:(t&&t.prod?PR161.scrub(t.prod,String(text||"")):String(text||""))');
R('question:String(q||"")','question:(t&&t.prod?PR161.scrub(t.prod,String(q||"")):String(q||""))');
R('card:shareCard(t)','card:prodSafeCard161(t,shareCard(t))',4);
R('  return x||"Untitled case";','  if(t&&t.prod)x=PR161.scrub(t.prod,x);\n  return x||"Untitled case";');
R('function errText(x){return String(x||"").split("\\n")[0].replace(/["\'“”‘’`][\\s\\S]*$/,"…").slice(0,200)}','function errText(x){return prodScrubAll161(String(x||"").split("\\n")[0].replace(/["\'“”‘’`][\\s\\S]*$/,"…").slice(0,200))}');

s=s.split('SORTED_V="v160"').join('SORTED_V="v161"');
fs.writeFileSync('public/index.html',s);
const EXPECT='07ce12a8e009a29f9a95c8d07dd276794d6da8b9';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v161 ok',h(s),s.length);
