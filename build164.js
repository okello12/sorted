const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='e56d4378915df234d590a43dd8332edb6d143bca')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v164: Sorted no longer writes physical repair instructions (Baldwin's decision of 10 October 2026, after Phase 1).
// The washing-machine "Try these safe checks" step is retired for every repair, not only product cases: official
// guidance or none. What stays: the repair questions (intake), every safety warning, and the history of cases that
// already answered checks. Their answers stay on the case and still appear as "What you tried" in the message and the
// pack (triedList and CHECKS are kept for that). A case saved at the checks step opens at the decision instead, so no
// existing case loses its place. The plan chip "Try a safe check" becomes "Look up the maker’s own guidance".
R('if(st==="checks")return !!t.prod||t.safety||f.item!=="Washing machine"||f.responsible!=="me"||!(CHECKS[f.fault]||[]).length;','if(st==="checks")return true;');
R('  var f=t.fix,d=S.draft,order=["what","who","bought","checks","decide"];','  var f=t.fix,d=S.draft,order=["what","who","bought","checks","decide"];if(f.step==="checks")f.step="decide";');
R('t.fix.step=skipChecks?"decide":"checks";','t.fix.step="decide";');
R('if(mode==="fix")return ["Not sure yet","Try a safe check","Contact whoever is responsible","Leave it for now"];','if(mode==="fix")return ["Not sure yet","Look up the maker’s own guidance","Contact whoever is responsible","Leave it for now"];');
R("'Try a few safe checks. If it is still broken, Sorted keeps the next step in one place.'","'Tell Sorted what’s wrong. If someone needs to fix it, Sorted keeps the next step in one place.'");
// The product's ledger rows are written once each, recognised by type, value and time, with no counter on the record
// (a counter differed between two devices and made a merge name a false conflict).
R(String.raw`function prodLedger161(t){
  if(!t||!t.prod||!t.prod.f)return false;var ch=false;
  PR161.FIELDS.forEach(function(k){var fl=PR161.field(t.prod,k);if(!fl)return;var all=(fl.was||[]).concat([{v:fl.v,st:fl.st,src:fl.src,at:fl.at}]),n=fl.lgN||0;
    for(var i=n;i<all.length;i++){var x=all[i];if(!x.v)continue;var st=x.st==="candidate"?"read":x.st==="rejected"?"rejected":(x.st==="confirmed"||x.st==="corrected")?"confirmed":"";if(!st)continue;
      var v=k==="serial"?PR161.mask(x.v):k==="category"?PR161.catName(x.v):k==="bought"?Product.route.fmt(x.v):x.v,ph=x.src==="label_photo"||x.src==="receipt";
      ch=lgPut(t,{type:PROD_LG161[k],v:v,by:x.st==="corrected"||!ph?"you":"photo",src:x.st==="corrected"||!ph?"":(x.src==="receipt"?"the receipt":"the label"),st:st,cby:st==="confirmed"?"you":null},new Date(x.at||now0161()).toISOString())||ch}
    if(fl.lgN!==all.length){fl.lgN=all.length;ch=true}});
  return ch;
}
`,String.raw`function prodLedger161(t){
  if(!t||!t.prod||!t.prod.f)return false;var ch=false,L=t.ledger||[];
  /* idempotent without a counter on the record (a counter differs between two devices and made merges name a false
     conflict): a state is written once, recognised by its type, value and time */
  PR161.FIELDS.forEach(function(k){var fl=PR161.field(t.prod,k);if(!fl)return;var all=(fl.was||[]).concat([{v:fl.v,st:fl.st,src:fl.src,at:fl.at}]);
    for(var i=0;i<all.length;i++){var x=all[i];if(!x.v)continue;var st=x.st==="candidate"?"read":x.st==="rejected"?"rejected":(x.st==="confirmed"||x.st==="corrected")?"confirmed":"";if(!st)continue;
      var v=k==="serial"?PR161.mask(x.v):k==="category"?PR161.catName(x.v):k==="bought"?Product.route.fmt(x.v):x.v,ph=x.src==="label_photo"||x.src==="receipt",at=new Date(x.at||now0161()).toISOString();
      if((t.ledger||[]).some(function(r){return r.type===PROD_LG161[k]&&r.v===v&&(r.at===at||r.at2===at)}))continue;
      var c0=lgCur(t,PROD_LG161[k]),r0=lgPut(t,{type:PROD_LG161[k],v:v,by:x.st==="corrected"||!ph?"you":"photo",src:x.st==="corrected"||!ph?"":(x.src==="receipt"?"the receipt":"the label"),st:st,cby:st==="confirmed"?"you":null},at);
      if(r0&&c0&&c0.v===v&&!c0.at2)c0.at2=at;ch=r0||ch}
    if(fl.lgN!==undefined){delete fl.lgN;ch=true}});
  return ch;
}
`);
// A product's details merge key by key, like the repair answers. The repair fields that are worked out from the product
// (item, model, seller, age) never count as a conflict: they are worked out again from the merged product on the next save.
R('var SP={events:1,promises:1,moves:1,corr:1,refs:1,ledger:1,evDel:1,cf:1,docNames:1,items:1,rev:1,wid:1,fix:1,pk:1,goal:1,snooze:1,att:1,turn:1};','var SP={events:1,promises:1,moves:1,corr:1,refs:1,ledger:1,evDel:1,cf:1,docNames:1,items:1,rev:1,wid:1,fix:1,pk:1,goal:1,snooze:1,att:1,turn:1,prod:1};');
R('["fix","pk","goal","snooze","att","turn"].forEach(function(k){var v=dmD143(bb[k],mine[k],srv[k],hasB,K,diff,k);if(v!==undefined)out[k]=v});','["fix","pk","goal","snooze","att","turn","prod"].forEach(function(k){var mk=mine[k];if(k==="fix"&&(mine.prod||srv.prod)&&mk&&srv.fix&&typeof mk==="object"&&typeof srv.fix==="object"){mk=JSON.parse(JSON.stringify(mk));["item","model","seller","age"].forEach(function(q){if(srv.fix[q]===undefined)delete mk[q];else mk[q]=srv.fix[q]})}var v=dmD143(bb[k],mk,srv[k],hasB,K,diff,k);if(v!==undefined)out[k]=v});');
// Every model read from a photo is checked letter by letter: a tilted photo turned WGG244ZCGB/01 into WGG2442CGBI0Y.
R(`(p.how==="unlabelled"&&PR161.candidate(r,"model")?'<span class="cf-src">Sorted isn’t sure this is the model. Check it against the label.</span>':'')`,`(p.how==="unlabelled"&&PR161.candidate(r,"model")?'<span class="cf-src">Sorted isn’t sure this is the model. Check it against the label.</span>':PR161.candidate(r,"model")?'<span class="cf-src">Check it letter by letter against the label. A photo can turn a Z into a 2.</span>':'')`);
// A product detail changed on two devices is named in the merge line like any other nested answer.
R('var DM143={fix:"repair answer",','var DM143={fix:"repair answer",prod:"product detail",');
s=s.split('SORTED_V="v163"').join('SORTED_V="v164"');
fs.writeFileSync('public/index.html',s);
const EXPECT='0db852ee8c73d5eb4eb15fd3ffc7f9ba6b8ec311';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v164 ok',h(s),s.length);
