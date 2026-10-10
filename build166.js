const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='eeb5932006e2ee9a4af015615f49241865a4a3da')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v166: from Baldwin's walk through a vacuum cleaner case on his iPhone (10 October 2026, 20:09 to 20:12).
// 1. The case asked again what it is and what's happening, with washing-machine chips, after the start had both. On a
//    case with a product, the first step is now only the safety question, with an optional line for more detail.
//    Repetition is not clarification. A product washing machine no longer has to pick a fault chip.
// 2. Started without the label, the product said "Not known yet" three times with no way forward but "Change these
//    details". It now says Sorted needs the model for the right support page and offers "Photograph the label" on the
//    case. The read is candidates, shown on the card to accept ("Looks right"), change or turn down, as at the start.
// 3. The product's details were an unstyled list (labels over indented values). They are rows now.
// (The capital in "My vacuum cleaner: It’s not working" stays: those are the person's words, kept as typed.)
const GLUE=String.raw`/* ---- v166: the product's first step, and the label on the case ---- */
function prodWhat166(t){
  var f=t.fix,d=S.draft,said=String(t.said||"").replace(/^my [^:]{1,40}:\s*/i,"").replace(/[.!]+$/,"").trim(),gas=/boiler|heating|gas/i.test(f.item||"")||PR161.value(t.prod,"category")==="boiler";
  var h='<form class="stack" data-f="what"><h2 class="h2">Before anything else</h2>'+(said?'<p style="margin:0">You said: “'+esc(said.slice(0,160))+'”.</p>':'');
  h+=(f.item&&f.item!=="Washing machine"?'<input type="hidden" id="f-item" value="'+esc(f.item)+'">':'')+'<label class="f">Anything to add? <span class="hint">Optional. An error code, noises, when it started.</span><textarea id="f-detail" name="detail" rows="2">'+esc(d.detail!==undefined?d.detail:(f.detail||""))+'</textarea></label>';
  h+='<div class="stack-s"><span style="font-weight:600">'+(gas?"Can you smell gas, or is anything burning, smoking or sparking?":"Is anything burning, smoking or sparking, or is there water near the plug or socket?")+'</span><div class="row"><button type="button" class="btn danger" data-a="unsafe">Yes</button><button type="submit" class="btn primary" style="flex:1">No, carry on</button></div></div>';
  if(d.err)h+='<p class="err">'+esc(d.err)+'</p>';
  return h+'</form>';
}
/* The label, photographed later on the case: candidates the person accepts here. */
function prodLabelCase166(t){
  var r=t.prod,c=["brand","model","serial"].filter(function(k){return PR161.candidate(r,k)}),ms=S.view.prodModels166&&S.view.prodModels166.id===t.id?S.view.prodModels166.list:[],h="";
  if(c.length||ms.length){
    h+='<form class="note stack-s" data-f="prod166c"><p class="h3" style="margin:0">Check what Sorted read</p>';
    c.forEach(function(k){h+='<p style="margin:0">'+PROD_SAY161[k]+': <span'+(k==="brand"?'':' class="mono"')+'>'+esc(k==="serial"?PR161.mask(PR161.candidate(r,k)):PR161.candidate(r,k))+'</span></p>'});
    if(ms.length)h+='<p style="margin:0">Sorted found more than one model. Which is it?</p><div class="chips">'+ms.map(function(x,i){return '<label class="chip gi-chip"><input type="radio" name="prod-model" value="'+esc(x)+'"'+(i===0?' checked':'')+' class="sr-only"> <span class="mono">'+esc(x)+'</span></label>'}).join("")+'</div>';
    h+='<p class="cf-src" style="margin:0">Check it letter by letter against the label. A photo can turn a Z into a 2.</p><div class="row" style="flex-wrap:wrap"><button class="btn primary" type="submit">Looks right</button><button type="button" class="btn" data-a="panel" data-p="prod161c">Change</button><button type="button" class="link" data-a="prod166-no">Not right</button></div></form>';
  }
  if(!PR161.value(r,"model")&&!c.length&&!ms.length)h+='<div class="stack-s"><p style="margin:0">To find the right support page, Sorted needs the model. It’s on the rating label.</p><div class="row" style="flex-wrap:wrap">'+prodPick161("Photograph the label",true,"","f-prodc")+'<button type="button" class="btn" data-a="panel" data-p="prod161c">Type it</button></div>'+'<button type="button" class="link" data-a="prod166-where" aria-expanded="'+(S.view.prodWhere166?"true":"false")+'" style="align-self:flex-start">Show me where to look</button>'+(S.view.prodWhere166?prodWhere161({where:true},true):'')+'</div>';
  if(h)h+='<p class="muted" id="ocr-status" role="status" aria-live="polite" style="font-size:15px;margin:0">Sorted reads the label on your phone. The photo isn’t uploaded or kept.</p>';
  return h;
}
function prodOcrCase166(raw,target,tok){
  if(tok&&(tok!==S.ocrTok||tok.v!==S.view.name+":"+(S.view.id||"")+":"+target))return;
  var t=S.view.id?task(S.view.id):null;if(!t||!t.prod)return;var r=Product.intake.readLabel(ocrClean(raw)),now=Date.now(),any=!!(r.brand||r.models.length||r.serial);
  if(r.brand)PR161.propose(t.prod,"brand",r.brand,"label_photo",now);if(r.model)PR161.propose(t.prod,"model",r.model,"label_photo",now);if(r.serial)PR161.propose(t.prod,"serial",r.serial,"label_photo",now);
  S.view.prodModels166=r.models.length>1&&!PR161.value(t.prod,"model")?{id:t.id,list:r.models}:null;
  prodTrack161(any?"product_candidate_found":"product_read_failed",t,{brand:!!r.brand,models:r.models.length,serial:!!r.serial,where:"case"});
  if(any){t._dirty=true;save()}render();ocrStatus(any?"Label read. Check what Sorted found.":"Sorted didn’t find a make, model or serial number in that photo. Get close so the label fills the photo, in good light.",!any);
}
document.addEventListener("submit",function(e){var f=e.target;if(!f||!f.getAttribute||f.getAttribute("data-f")!=="prod166c")return;e.preventDefault();e.stopImmediatePropagation();
  var t=S.view.id?task(S.view.id):null;if(!t||!t.prod)return;var r=t.prod,now=Date.now(),mc=f.querySelector('input[name="prod-model"]:checked');
  if(mc){PR161.propose(r,"model",mc.value,"label_photo",now)}
  ["brand","model","serial"].forEach(function(k){if(PR161.candidate(r,k)&&PR161.confirm(r,k,now))log(t,PROD_SAY161[k]+": "+prodShow161(r,k)+", read from the label photo and confirmed by you.")});
  S.view.prodModels166=null;prodTrack161("product_confirmed",t,{src:"label",where:"case",model:!!PR161.value(r,"model"),serial:!!PR161.value(r,"serial")});t._dirty=true;save();render();
},true);
document.addEventListener("click",function(e){var b=e.target.closest&&e.target.closest("[data-a]");if(!b)return;var a=b.getAttribute("data-a"),t=S.view.id?task(S.view.id):null;
  if(a==="prod166-no"&&t&&t.prod){var now=Date.now();["brand","model","serial"].forEach(function(k){if(PR161.candidate(t.prod,k))PR161.reject(t.prod,k,now)});S.view.prodModels166=null;t._dirty=true;save();render();return}
  if(a==="prod166-where"&&t){S.view.prodWhere166=!S.view.prodWhere166;render()}
});
`;
R('function boot(){',GLUE+'function boot(){');
R('  if(f.step==="what"){','  if(f.step==="what"&&t.prod&&PR161.value(t.prod,"category")){h+=prodWhat166(t);\n  }else if(f.step==="what"){');
R('if(item==="Washing machine"&&!fault){d.err="Pick what it’s doing.";render();return}','if(item==="Washing machine"&&!fault&&t.prod)fault="other";if(item==="Washing machine"&&!fault){d.err="Pick what it’s doing.";render();return}');
R(`+'</dl>'+(d?'<p class="prod161-safety'`,`+'</dl>'+prodLabelCase166(t)+(d?'<p class="prod161-safety'`);
R('ocrDone=function(raw,target,tok){if(target==="f-prod")return prodOcr161(raw,target,tok);','ocrDone=function(raw,target,tok){if(target==="f-prod")return prodOcr161(raw,target,tok);if(target==="f-prodc")return prodOcrCase166(raw,target,tok);');
R(`id="prod-brand" autocomplete="off" value="'+esc(PR161.value(r,"brand"))+'"`,`id="prod-brand" autocomplete="off" value="'+esc(PR161.value(r,"brand")||PR161.candidate(r,"brand"))+'"`);
R(`spellcheck="false" value="'+esc(PR161.value(r,"model"))+'"`,`spellcheck="false" value="'+esc(PR161.value(r,"model")||PR161.candidate(r,"model"))+'"`);
R('.more129 [data-a=acct-jump]{display:inline-flex!important;align-items:center;min-height:44px!important;vertical-align:middle}\n</style>',
  '.more129 [data-a=acct-jump]{display:inline-flex!important;align-items:center;min-height:44px!important;vertical-align:middle}\n/* v166: the product\'s details as rows */\n.prod161-dl{display:flex;flex-direction:column;margin:0}\n.prod161-row{display:flex;flex-wrap:wrap;gap:2px 12px;padding:8px 0;border-top:1px solid var(--rule)}\n.prod161-row:first-child{border-top:0}\n.prod161-row dt{font-weight:600;min-width:7.5em}\n.prod161-row dd{margin:0;flex:1}\n.prod161-card{border:1px solid var(--rule);border-radius:18px;padding:16px 18px}\n</style>');
s=s.split('SORTED_V="v165"').join('SORTED_V="v166"');
fs.writeFileSync('public/index.html',s);
const EXPECT='9f2fec997d17d07a62c6e7bb7f4852fed833e80b';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v166 ok',h(s),s.length);
