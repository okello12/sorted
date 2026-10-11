const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='aff1b674955dfc1393a785c0f847d5ce769cb354')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v168: from the external audit of 11 October 2026.
// 1. Safety: every repair, not only a product's, also goes through the product safety rules (ps-3). The page's older
//    danger reader still runs first; a STOP_USE from the rules stops too. ps-3 never lets a negation clear danger that is
//    past or paused, and adds smells, electrical noises, discoloured sockets, hedged gas, carbon monoxide signs and more.
// 2. A model read from a photo is doubted when the reader scored the photo under 85, or the model has lower-case letters
//    inside it, or an O, I or L beside a 0 or 1 (every wrong model in the audit's photos did). Sorted says so and puts
//    "Retake photo" first. Under 60 it offers no model at all. The person still confirms whatever is offered.
const GLUE=String.raw`/* ---- v168: one set of safety rules, and doubt about a model read from a photo ---- */
function lu168(a){try{var w=[].slice.call(a).filter(Boolean).map(String);if(!w.length)return false;return Product.safety.decide({category:"",words:w},0).result==="STOP_USE"}catch(e){return false}}
var PROD_DOUBT168="Sorted isn’t sure it read the model correctly. The photo may be blurred, tilted or too far away.";
var PROD_UNCLEAR168="The photo is too unclear to read the model. Retake it close up, straight on, in good light, or type the model.";
function prodDoubtBox168(dbt,target){if(!dbt||!dbt.length)return "";var un=dbt.indexOf("unclear")>=0;
  return '<div class="note stack-s prod168-doubt" role="status"><p style="margin:0"><b>'+(un?PROD_UNCLEAR168:PROD_DOUBT168)+'</b>'+(un?'':' Retake it if you can, or check every letter and number against the label.')+'</p><div class="row" style="flex-wrap:wrap">'+prodPick161("Retake photo",true," primary",target)+'</div></div>'}
`;
R('function boot(){',GLUE+'function boot(){');
// 1. the page's danger reader also asks the product safety rules
R('if(DANGER.test(x)||DANGER_HOT.test(x)||DANGER_MORE.test(x)||DANGER_WET.test(x))return true}return false}','if(DANGER.test(x)||DANGER_HOT.test(x)||DANGER_MORE.test(x)||DANGER_WET.test(x))return true}return lu168(arguments)}');
// 2. the start: the photo's confidence, the doubt, the box
R('var x=ocrClean(raw),r=Product.intake.readLabel(x),now=Date.now(),p=S.draft.prod161','var x=ocrClean(raw),r=Product.intake.readLabel(x,{conf:tok&&typeof tok.conf==="number"?tok.conf:undefined}),now=Date.now(),p=S.draft.prod161');
R('  p.fail=false;p.edit=false;p.ok=false;p.msg="";\n','  p.fail=false;p.edit=false;p.ok=false;p.msg="";p.doubt=r.doubt||[];\n');
R(`  S.draft.prod161=p;prodTrack161(any?"product_candidate_found"`,`  if(r.withheld&&r.withheld.length)p.msg=PROD_UNCLEAR168;else if(p.doubt.length&&r.models.length)p.msg="Label read, but Sorted isn’t sure of the model. Check it carefully.";
  S.draft.prod161=p;prodTrack161(any?"product_candidate_found"`);
R(`'<h2 class="h3" id="prod161-h" tabindex="-1">Check what Sorted read</h2>'+(p.fail?`,`'<h2 class="h3" id="prod161-h" tabindex="-1">Check what Sorted read</h2>'+prodDoubtBox168(p.doubt,"f-prod")+(p.fail?`);
// 3. on the case
R('var t=S.view.id?task(S.view.id):null;if(!t||!t.prod)return;var r=Product.intake.readLabel(ocrClean(raw)),now=Date.now(),any=!!(r.brand||r.models.length||r.serial);',
  'var t=S.view.id?task(S.view.id):null;if(!t||!t.prod)return;var r=Product.intake.readLabel(ocrClean(raw),{conf:tok&&typeof tok.conf==="number"?tok.conf:undefined}),now=Date.now(),any=!!(r.brand||r.models.length||r.serial);S.view.prodDoubt166=r.doubt&&r.doubt.length?{id:t.id,d:r.doubt}:null;');
R(`render();ocrStatus(any?"Label read. Check what Sorted found.":"Sorted didn’t find a make, model or serial number in that photo. Get close so the label fills the photo, in good light.",!any);`,
  `render();ocrStatus(r.withheld&&r.withheld.length?PROD_UNCLEAR168:any?(r.doubt&&r.doubt.length&&r.models.length?"Label read, but Sorted isn’t sure of the model. Check it carefully.":"Label read. Check what Sorted found."):"Sorted didn’t find a make, model or serial number in that photo. Get close so the label fills the photo, in good light.",!any||!!(r.withheld&&r.withheld.length));`);
R(`  if(c.length||ms.length){
    h+='<form class="note stack-s" data-f="prod166c"><p class="h3" style="margin:0">Check what Sorted read</p>';`,
  `  var dv168=S.view.prodDoubt166&&S.view.prodDoubt166.id===t.id?S.view.prodDoubt166.d:null;
  if(dv168&&dv168.indexOf("unclear")>=0&&!c.length&&!ms.length)h+=prodDoubtBox168(dv168,"f-prodc");
  if(c.length||ms.length){
    h+=(dv168&&(PR161.candidate(r,"model")||ms.length)?prodDoubtBox168(dv168,"f-prodc"):"")+'<form class="note stack-s" data-f="prod166c"><p class="h3" style="margin:0">Check what Sorted read</p>';`);
R(`  if(a==="prod166-no"&&t&&t.prod){var now=Date.now();`,`  if(a==="prod166-no"&&t&&t.prod){S.view.prodDoubt166=null;var now=Date.now();`);
R(`  S.view.prodModels166=null;prodTrack161("product_confirmed",t,{src:"label",where:"case"`,`  S.view.prodModels166=null;S.view.prodDoubt166=null;prodTrack161("product_confirmed",t,{src:"label",where:"case"`);
s=s.split('SORTED_V="v167"').join('SORTED_V="v168"');
fs.writeFileSync('public/index.html',s);
const EXPECT='14fc5910f24349bf9a6cc972ae91a5dd575c08eb';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v168 ok',h(s),s.length);
