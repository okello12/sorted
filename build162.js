const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='07ce12a8e009a29f9a95c8d07dd276794d6da8b9')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v162: Something I own isn't working, stage 2 (docs/PRODUCT_PHASE1.md). On a repair case with a product:
// purchase details typed or read from a receipt photo and confirmed before they count; the maker's hand-checked UK
// support page, saying plainly that Sorted found the page and hasn't read its instructions; "Best next step" from
// confirmed facts with its reason and source, the other routes beneath; "Have these ready"; and "Prepare contact",
// which hands over to the existing message form (callDefaults) with only confirmed details and no serial unless the
// person adds it. Nothing here makes a promise: what they say next goes through the ordinary reader.

const GLUE=String.raw`/* ---- v162: purchase details, official support, Best next step and the contact (docs/PRODUCT_PHASE1.md) ---- */
var PROD_ROUTE_SAY162={RETAILER:"Contact",MANUFACTURER:"Contact",QUALIFIED_REPAIR:"Get",OFFICIAL_SERVICE_CENTRE:"Contact",SELF_RESOLVED:"",OTHER:"Contact"};
function prodRoute162(t){var f=t.fix||{},p=t.prod;return Product.route.route({rec:p,safety:p&&p.safety,responsible:f.responsible,party:f.party||cap1(whoName(t)),partyResp:whoName(t),fixed:f.decision==="fixed"},Date.now())}
function prodRouteHead162(r){return r.key==="QUALIFIED_REPAIR"?"Get "+r.who:"Contact "+r.who}
/* The purchase step on a product case: the shop and the date, typed or read from a receipt and confirmed. */
function prodBought162(t){
  var r=t.prod,d=S.draft,v=S.view.rcpt162&&S.view.rcpt162.id===t.id?S.view.rcpt162:null,today=new Date(),ti=today.getFullYear()+"-"+("0"+(today.getMonth()+1)).slice(-2)+"-"+("0"+today.getDate()).slice(-2);
  var shopC=PR161.candidate(r,"retailer"),dayC=PR161.candidate(r,"bought"),c=d.cover!==undefined?d.cover:t.fix.cover;
  var h='<form class="stack" data-f="prod162b"><h2 class="h2" id="prod162-h" tabindex="-1">Where and when did you buy it?</h2><p class="muted" style="margin:0">This can change who to contact first. Sorted uses it only once you’ve said it’s right.</p>';
  if(v&&v.fail)h+='<p class="err" role="alert" style="margin:0">Sorted couldn’t read a shop or a date on that receipt. Nothing has been changed. Type them below, or try another photo.</p>';
  if(shopC||dayC||(v&&(v.dates||[]).length>1)||(v&&v.odd)){
    h+='<div class="note stack-s"><h3 class="h3" style="margin:0">Check what Sorted found</h3><dl class="prod161-dl" style="margin:0">'+(shopC?'<div class="prod161-row"><dt>Bought from</dt><dd>'+esc(shopC)+'</dd></div>':'')+(dayC?'<div class="prod161-row"><dt>Bought on</dt><dd>'+esc(Product.route.fmt(dayC))+'</dd></div>':'')+'</dl>';
    if(v&&(v.dates||[]).length>1&&!dayC)h+='<p style="margin:0">The receipt has more than one date: '+v.dates.map(function(x){return esc(Product.route.fmt(x))}).join(", ")+'. Put the day you bought it below.</p>';
    if(v&&v.odd)h+='<p style="margin:0">A date on it only makes sense written month first, so Sorted didn’t read it. Put the date below.</p>';
    if(shopC||dayC)h+='<div class="row" style="flex-wrap:wrap"><button type="button" class="btn primary" data-a="prod162-rok">Looks right</button><button type="button" class="btn" data-a="prod162-rchange">Change</button></div>';
    h+='</div>';
  }
  var shopV=d.pbShop!==undefined?d.pbShop:(PR161.value(r,"retailer")||shopC||t.fix.seller||""),dayV=d.pbDay!==undefined?d.pbDay:(PR161.value(r,"bought")||dayC||"");
  h+='<label class="f">Shop or website<span class="hint">Leave it blank if you don’t know.</span><input type="text" id="pb-shop" autocomplete="off" value="'+esc(shopV)+'"></label>';
  h+='<label class="f">The day you bought it<span class="hint">Leave it blank if you don’t know.</span><input type="date" id="pb-day" max="'+ti+'" value="'+esc(dayV)+'"></label>';
  h+='<div class="row" style="flex-wrap:wrap">'+prodPick161("Photograph the receipt",true,"","f-rcpt")+prodPick161("Choose a photo of it",false,"","f-rcpt")+'</div><p class="muted" id="ocr-status" role="status" aria-live="polite" style="font-size:15px;margin:0">Sorted reads a receipt or order confirmation on your phone. The photo isn’t uploaded or kept.</p>';
  h+='<div class="stack-s"><span style="font-weight:600">Do you have a paid warranty or insurance for it?</span><div class="chips">'+COVER.map(function(x){return '<button type="button" class="chip" data-a="d" data-k="cover" data-v="'+x[0]+'" aria-pressed="'+(c===x[0])+'">'+x[1]+'</button>'}).join("")+'</div></div>';
  if(d.err)h+='<p class="err">'+esc(d.err)+'</p>';
  return h+'<button class="btn primary block" type="submit">Next</button></form>';
}
/* The maker's support page, if Sorted has a checked one. Found, not read. */
function prodSupport162(t){
  var r=t.prod,b=PR161.value(r,"brand"),dec=r.safety,mk=b?Product.makers.makerByName(b):null;if(!b)return "";
  if(!mk)return '<section class="prod162-support stack-s"><h3 class="h3">'+esc(b)+'’s support</h3><p style="margin:0">Sorted doesn’t have a checked support page for '+esc(b)+' yet. Look for it on '+esc(b)+'’s own website, not through an advert or a search result that only looks official.</p></section>';
  if(!Product.safety.allows(dec).supportLink)return "";
  var u=Product.makers.link(mk,"support");if(!u)return "";
  return '<section class="prod162-support stack-s"><h3 class="h3">'+esc(mk.name)+'’s official support</h3><p style="margin:0"><a href="'+esc(u)+'" target="_blank" rel="noopener" data-a="prod162-open">'+esc(mk.supportTitle||mk.name+" support")+'</a></p><p style="margin:0">Sorted found '+esc(mk.name)+'’s UK support page. It hasn’t read '+esc(mk.name)+'’s instructions for your problem, so it can’t tell you what they say.</p>'+(navigator.onLine===false?'<p class="muted" style="margin:0">You’re offline. The page will open once you’re connected.</p>':'')+'<p class="cf-src" style="margin:0">Link checked by hand on '+esc(Product.makers.CHECKED)+'.</p></section>';
}
/* What to have ready, from confirmed details only. The serial masked. */
function prodReady162(t){
  var r=t.prod,out=[],f=t.fix||{},w=String(f.detail||"").trim()||String(t.said||"").replace(/^my [^:]{1,40}:\s*/i,"").trim();
  PR161.ready(r,false).forEach(function(x){out.push(x.k==="bought"?"Bought on "+Product.route.fmt(x.v):x.v)});
  if(w)out.push("What’s happening, in your words: “"+w.replace(/[.!]+$/,"").slice(0,160)+"”");
  if(PR161.value(r,"retailer")||PR161.value(r,"bought"))out.push("Your receipt or order confirmation");
  return out;
}
function prodDecide162(t){
  var r=t.prod,dec=r.safety,rt=prodRoute162(t),h='<div class="stack">';
  if(dec&&dec.result==="STOP_USE")h+='<section class="safety"><p class="h3">Keep it switched off</p><p style="margin-top:6px">'+esc(dec.reason)+' Don’t try any checks yourself.</p></section>';
  else if(dec&&dec.result==="PROFESSIONAL_ONLY")h+='<p class="note" style="margin:0">'+esc(dec.reason)+'</p>';
  h+=prodSupport162(t);
  if(rt.key==="SELF_RESOLVED")return h+'</div>';
  h+='<section class="prod162-best stack-s"><p class="eyebrow">Best next step</p><h2 class="h2" id="prod162-h" tabindex="-1">'+esc(prodRouteHead162(rt))+'</h2><p style="margin:0">'+esc(rt.reason)+'</p>';
  (rt.basis||[]).forEach(function(b){h+='<p class="cf-src" style="margin:0">Source: <a href="'+esc(b.url)+'" target="_blank" rel="noopener">'+esc(b.title)+'</a></p>'});
  if(rt.url)h+='<p style="margin:0"><a href="'+esc(rt.url)+'" target="_blank" rel="noopener">'+esc(rt.key==="RETAILER"?rt.who+"’s help page":rt.key==="QUALIFIED_REPAIR"?"How to check an engineer":rt.who+"’s repair and contact page")+'</a></p>';
  var rd=prodReady162(t);if(rd.length)h+='<h3 class="h3" style="margin:8px 0 0">Have these ready</h3><ul class="stack-s" style="margin:0;padding-left:1.1em">'+rd.map(function(x){return '<li>'+esc(x)+'</li>'}).join("")+'</ul>';
  h+='<button class="btn primary block" data-a="prod162-contact" data-k="'+rt.key+'" data-w="'+esc(rt.who)+'">Prepare contact</button>';
  if((rt.alt||[]).length)h+='<details class="prod162-alt"><summary>See other options</summary><ul class="stack-s" style="margin:8px 0 0;padding-left:1.1em">'+rt.alt.map(function(a){return '<li><strong>'+esc(prodRouteHead162(a))+'</strong>. '+esc(a.why)+(a.url?' <a href="'+esc(a.url)+'" target="_blank" rel="noopener">Their page</a>':'')+' <button type="button" class="link" data-a="prod162-contact" data-k="'+a.key+'" data-w="'+esc(a.who)+'">Prepare contact</button></li>'}).join("")+'</ul></details>';
  h+='<button class="link" data-a="decide" data-v="fixed" style="align-self:flex-start">It’s working again</button></section>';
  return h+'</div>';
}
/* The message for the existing contact form: confirmed details only, the person's words for the fault, no serial. */
function prodContact162(t,fault){
  var r=t.prod,rt=t.prod.route||{},who=rt.who||"",b=PR161.value(r,"brand"),m=PR161.value(r,"model"),c=PR161.catName(PR161.value(r,"category")),sh=PR161.value(r,"retailer"),dy=PR161.value(r,"bought");
  var what=(b?b+" ":"")+(c&&c!=="Something else"?c.toLowerCase():"product")+(m?", model "+m:"");
  var ask="Hi, I have a "+what+"."+(fault?" It has a fault: "+lc1(fault).replace(/[.!]+$/,"")+".":"")+(sh||dy?" I bought it"+(sh?" from "+sh:"")+(dy?" on "+Product.route.fmt(dy):"")+".":"");
  ask+=rt.key==="RETAILER"?" Can you repair or replace it, and tell me how and by when?":rt.key==="MANUFACTURER"?" Can you tell me how to get it repaired, and the earliest date an engineer could come?":rt.key==="QUALIFIED_REPAIR"?" Can you give me a price and the earliest date an engineer can come?":" Please arrange a repair and give me a date.";
  return {who:/^(?:a |the )/i.test(who)?cap1(who):who,ask:ask};
}
function prodRcpt162(raw,target,tok){
  if(tok&&(tok!==S.ocrTok||tok.v!==S.view.name+":"+(S.view.id||"")+":"+target))return;
  var t=S.view.id?task(S.view.id):null;if(!t||!t.prod)return;var rr=Product.intake.readReceipt(ocrClean(raw),Date.now()),now=Date.now(),any=!!(rr.retailer||rr.bought);
  if(rr.retailer)PR161.propose(t.prod,"retailer",rr.retailer,"receipt",now);if(rr.bought)PR161.propose(t.prod,"bought",rr.bought,"receipt",now);
  S.view.rcpt162={id:t.id,dates:rr.dates,odd:rr.odd,fail:!any&&!rr.dates.length};S.draft.pbShop=undefined;S.draft.pbDay=undefined;
  prodTrack161(any?"product_candidate_found":"product_read_failed",t,{doc:"receipt",shop:!!rr.retailer,dates:rr.dates.length});
  if(any){t._dirty=true;save()}render();ocrStatus(any?"Receipt read. Check what Sorted found.":"Sorted couldn’t read a shop or a date on that receipt.",!any);var hd=$("#prod162-h");if(hd)try{hd.focus({preventScroll:false})}catch(e){}
}
document.addEventListener("submit",function(e){var f=e.target;if(!f||!f.getAttribute||f.getAttribute("data-f")!=="prod162b")return;e.preventDefault();e.stopImmediatePropagation();
  var t=S.view.id?task(S.view.id):null;if(!t||!t.prod||!t.fix)return;var d=S.draft,r=t.prod,now=Date.now();
  var shop=String(($("#pb-shop")||{}).value||"").trim(),day=String(($("#pb-day")||{}).value||"").trim();
  if(day&&!PR161.okDate(day)){d.err="That date doesn’t look right. Pick it again, or leave it blank.";render();return}
  if(day&&day>new Date().toISOString().slice(0,10)){d.err="That date is in the future. Pick the day you bought it, or leave it blank.";render();return}
  prodEditField161(r,"retailer",shop,now);prodEditField161(r,"bought",day,now);
  t.fix.cover=(d.cover!==undefined?d.cover:t.fix.cover)||"unsure";var o=PR161.forFix(r,now);t.fix.seller=o.seller||"";if(o.age)t.fix.age=o.age;else if(!t.fix.age)t.fix.age="unsure";
  var sh=PR161.value(r,"retailer"),dy=PR161.value(r,"bought"),fl=function(k){var x=PR161.field(r,k);return x&&x.src==="receipt"&&x.st==="confirmed"?" (from the receipt, confirmed by you)":""};
  var both=sh&&dy&&fl("retailer")&&fl("bought");
  log(t,(sh?"Bought from "+sh+(both?"":fl("retailer")):"Not sure where it was bought")+(dy?" on "+Product.route.fmt(dy)+(both?"":fl("bought")):", date not known")+(both?", read from the receipt and confirmed by you":"")+". Warranty or insurance: "+label(COVER,t.fix.cover).toLowerCase()+".");
  if(sh||dy)prodTrack161("purchase_confirmed",t,{shop:!!sh,date:!!dy,src:(PR161.field(r,"retailer")||PR161.field(r,"bought")||{}).src==="receipt"?"receipt":"user"});
  t.fix.step="decide";S.view.rcpt162=null;S.draft={};prodSync161(t);
  var rt=prodRoute162(t);prodTrack161("resolution_route_shown",t,{route:rt.key});if(Product.makers.makerByName(PR161.value(r,"brand"))&&Product.safety.allows(r.safety).supportLink)prodTrack161("official_support_shown",t,{});
  commit();var hd=$("#prod162-h");if(hd)try{hd.focus()}catch(er){}
},true);
document.addEventListener("click",function(e){var b=e.target.closest&&e.target.closest("[data-a]");if(!b)return;var a=b.getAttribute("data-a");if(a.indexOf("prod162-")!==0)return;
  var t=S.view.id?task(S.view.id):null;if(!t||!t.prod)return;var now=Date.now();
  if(a==="prod162-rok"){["retailer","bought"].forEach(function(k){if(PR161.candidate(t.prod,k))PR161.confirm(t.prod,k,now)});S.draft.pbShop=undefined;S.draft.pbDay=undefined;t._dirty=true;save();render();var sh=$("#pb-shop");if(sh)sh.focus();return}
  if(a==="prod162-rchange"){var x=$("#pb-shop");if(x)x.focus();return}
  if(a==="prod162-open"){log(t,"Opened "+String(b.textContent||"the maker’s support page")+".");t._dirty=true;setTimeout(save,0);return}
  if(a==="prod162-contact"){var k=b.getAttribute("data-k"),w=b.getAttribute("data-w")||"";e.preventDefault();
    t.prod.route={key:k,who:w,at:nowIso()};t.fix.decision="product";t.fix.step="done";log(t,"Best next step chosen: "+prodRouteHead162({key:k,who:w}).replace(/^Contact /,"contact ").replace(/^Get /,"get ")+".");
    prodTrack161("contact_prepared",t,{route:k});S.view.panel="call";S.draft={};save();render();window.scrollTo(0,0);return}
  if(a==="prod162-addserial"){var ta=$("#f-ask"),full=PR161.value(t.prod,"serial");if(ta&&full&&ta.value.indexOf(full)<0){ta.value=ta.value.replace(/\s*$/,"")+" The serial number is "+full+".";S.draft.ask=ta.value;b.remove();ta.focus()}return}
});
`;
R('var PROD_TRACK161=false;',GLUE+'var PROD_TRACK161=false;');
// The fix steps on a product case: the purchase step and the decision are the product's own; the steps stay the case's.
R('}else if(f.step==="bought"){','}else if(f.step==="bought"&&t.prod){h+=prodBought162(t);\n  }else if(f.step==="bought"){');
R('}else if(f.step==="decide"){','}else if(f.step==="decide"&&t.prod){h+=prodDecide162(t);\n  }else if(f.step==="decide"){');
// The message: the product's own branch in the one contact engine, after a missed promise (a chase wins).
R('  var hasFault=(f.item?"My "+item.toLowerCase():"It")','  if(kind==="product"&&t.prod)return prodContact162(t,fault);\n  var hasFault=(f.item?"My "+item.toLowerCase():"It")');
R(`h+='<label class="f">What to ask for<textarea id="f-ask" name="ask" rows="6">'+esc(ask)+'</textarea></label>';`,`h+='<label class="f">What to ask for<textarea id="f-ask" name="ask" rows="6">'+esc(ask)+'</textarea></label>';
  if(t.prod&&PR161.value(t.prod,"serial")&&String(ask).indexOf(PR161.value(t.prod,"serial"))<0)h+='<button type="button" class="link" data-a="prod162-addserial" style="align-self:flex-start">Add the full serial number to the message</button>';`);
R('if(f.item)out.push("What it is: "+f.item+(f.model?" ("+f.model+")":""));','if(t.prod&&prodReady162(t).length)prodReady162(t).forEach(function(x){if(!/^What’s happening/.test(x))out.push(x)});else if(f.item)out.push("What it is: "+f.item+(f.model?" ("+f.model+")":""));');
R('if(f.age&&f.responsible==="me")out.push("When you bought it"','if(!(t.prod&&(PR161.value(t.prod,"retailer")||PR161.value(t.prod,"bought")))&&f.age&&f.responsible==="me")out.push("When you bought it"');
// The adviser pack carries the product, the serial masked, the support page Sorted found and the route chosen.
R('if(t.facts&&t.facts.amount)sum.push(["Amount","£"+t.facts.amount]);','if(t.facts&&t.facts.amount)sum.push(["Amount","£"+t.facts.amount]);\n    if(t.prod){PR161.ready(t.prod,false).forEach(function(x){sum.push([{product:"Product",serial:"Serial number",retailer:"Bought from",bought:"Bought on"}[x.k],x.k==="serial"?x.v.replace(/^Serial /,""):x.k==="retailer"?x.v.replace(/^Bought from /,""):x.k==="bought"?Product.route.fmt(x.v):x.v])});var mk162=Product.makers.makerByName(PR161.value(t.prod,"brand")),su162=mk162&&Product.makers.link(mk162,"support");if(su162)sum.push(["Maker’s support page (found by Sorted, checked "+Product.makers.CHECKED+")",su162]);if(t.prod.route&&t.prod.route.who)sum.push(["Next step chosen",prodRouteHead162(t.prod.route)])}');
// A receipt photo goes to the purchase reader.
R('ocrDone=function(raw,target,tok){if(target==="f-prod")return prodOcr161(raw,target,tok);','ocrDone=function(raw,target,tok){if(target==="f-prod")return prodOcr161(raw,target,tok);if(target==="f-rcpt")return prodRcpt162(raw,target,tok);');

s=s.split('SORTED_V="v161"').join('SORTED_V="v162"');
fs.writeFileSync('public/index.html',s);
const EXPECT='2a4aabf6b047bc4a32211d0757196519d5fcb8a0';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v162 ok',h(s),s.length);
