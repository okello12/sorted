const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='7c55e8861534d3278fc132e192d8f6e732095bdf')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,70));s=s.split(a).join(b)}
// ---- v173: a driving licence is not always a renewal. From Baldwin's case of 20 October 2026: the person's own step
// said "apply for it" after a driving ban, but the licence record only knows an expiry date, so the case led with
// "Expired Saturday 25 April" and "Renew on GOV.UK". Reapplying after a ban and reapplying after a health condition
// are different GOV.UK pages (hand-checked 20 October 2026). The record gains `why` (expired, ban or health):
// proposed from the person's words, confirmed by one tap, changeable; nothing is assumed from the hint alone.
R("function renewCard(t){\n",
`var LIC173={ban:{url:"https://www.gov.uk/reapply-licence-revoked",head:"Reapply on GOV.UK",state:"After a driving ban",note:"GOV.UK says when you can reapply and which form to use: the D27 if DVLA sends you one, otherwise a D1 from a Post Office. You can’t drive until the ban has ended. In Northern Ireland it’s the DVA."},health:{url:"https://www.gov.uk/reapply-driving-licence-health-condition",head:"Reapply on GOV.UK",state:"After a health condition",note:"DVLA writes to you when you can reapply, up to 8 weeks before any waiting period ends. Check with your doctor first."}};
var LIC173_BAN=/\\b(?:ban|banned|disqualif\\w*|revoked|cancelled|taken (?:away|off me)|took (?:away )?my licen[cs]e|lost my licen[cs]e)\\b/i,LIC173_HEALTH=/\\b(?:medical|health|doctor|epilep\\w*|eyesight|seizure|surrender\\w*)\\b/i;
function lic173Words(t){var m=openMove(t);return [t.said,t.title,m&&m.what].filter(Boolean).join(" ")}
var LIC173_APPLY=/\\bappl(?:y|ied|ication|ying)\\b/i;
function lic173Apply(t){var w=lic173Words(t);return LIC173_APPLY.test(w)&&!/\\brenew/i.test(w)}
function lic173Hint(t){var w=lic173Words(t);return LIC173_BAN.test(w)?"ban":LIC173_HEALTH.test(w)?"health":""}
function lic173Why(t){var r=t.renew;return r&&r.kind==="licence"&&LIC173[r.why]?r.why:(r&&r.kind==="licence"&&r.why==="expired"?"expired":"")}
function lic173Ask(t,hint){var cur=lic173Why(t),o={expired:["expired","It ran out"],ban:["ban","It was taken away after a driving ban"],health:["health","It was taken away for a health condition"]},order=hint==="ban"?["ban","health","expired"]:hint==="health"?["health","ban","expired"]:["expired","ban","health"];
  return '<div class="stack-s lic173-ask"><p class="case56-overline">Which GOV.UK page?</p><h2 class="h2">Why do you need a licence?</h2><p class="muted">'+(hint?'Your words mention '+(hint==="ban"?'a ban':'a health condition')+'. Sorted can’t be sure, so check before it shows a page.':'Renewing, reapplying after a ban and reapplying after a health condition are different GOV.UK pages.')+'</p><div class="chips">'+order.map(function(k){return '<button type="button" class="chip" data-a="lic173-why" data-v="'+k+'" aria-pressed="'+(cur===k)+'">'+o[k][1]+'</button>'}).join("")+'</div></div>'}
function renewCard(t){
`);
R("  var head=rp===\"upcoming\"?\"Start by \"+fmtDay(sbd):rp===\"now\"?\"Renew now\":rp===\"expired\"?(date?\"Expired \"+date:\"Expired\"):\"Add the expiry date\";\n  h+='<section class=\"case56-renew-state '+(rp===\"expired\"?'expired':'')+'\"><p class=\"case56-overline\">'+esc(rname(r))+'</p><h2 class=\"h2\">'+esc(head)+'</h2>';\n",
`  var why=lic173Why(t),hint=r.kind==="licence"&&!why?lic173Hint(t):"",asking=r.kind==="licence"&&(S.view.lic173Ask||(!why&&(hint||(rp==="expired"&&lic173Apply(t))))),notRenew=r.kind==="licence"&&(asking||(why&&why!=="expired"));
  var head=notRenew?(LIC173[why]?LIC173[why].state:"Check which page fits"):rp==="upcoming"?"Start by "+fmtDay(sbd):rp==="now"?"Renew now":rp==="expired"?(date?"Expired "+date:"Expired"):"Add the expiry date";
  h+='<section class="case56-renew-state '+(rp==="expired"&&!notRenew?'expired':'')+'"><p class="case56-overline">'+esc(rname(r))+'</p><h2 class="h2">'+esc(head)+'</h2>';
  if(notRenew&&date)h+='<p class="muted">You gave '+esc(date)+' as the date.</p>';
`);
R("  if(rp===\"upcoming\")h+='<p class=\"muted\">Nothing to do yet. Sorted will bring this back when it is time to start.</p>';\n",
  "  if(rp===\"upcoming\"&&!notRenew)h+='<p class=\"muted\">Nothing to do yet. Sorted will bring this back when it is time to start.</p>';\n");
R("  h+='<section class=\"sheet case56-official stack\">';\n  if(info){\n",
`  h+='<section class="sheet case56-official stack">';
  if(asking){h+=lic173Ask(t,hint||why)}
  else if(LIC173[why]){var L173=LIC173[why];
    h+='<div class="case56-official-main"><div class="stack-s"><p class="case56-overline">Official route</p><h2 class="h2">'+L173.head+'</h2><p class="muted">'+L173.state+'. Use the official service.</p></div><a class="btn primary block" href="'+L173.url+'" target="_blank" rel="noopener noreferrer">Open GOV.UK ↗</a></div>';
    h+='<p class="muted">'+L173.note+'</p><p class="case56-trust"><strong>Use the official site.</strong> Other sites may charge extra. Don’t follow links you weren’t expecting.</p><button type="button" class="link" data-a="lic173-ask" style="align-self:flex-start;min-height:44px">Not right? Choose a different page</button>';
  }
  else if(info){
`);
R("Don’t follow renewal links you weren’t expecting.</p>';\n  }else if(r.how===\"self\"){",
  "Don’t follow renewal links you weren’t expecting.</p>';\n    if(r.kind===\"licence\")h+='<button type=\"button\" class=\"link\" data-a=\"lic173-ask\" style=\"align-self:flex-start;min-height:44px\">Taken away after a ban or for a health condition? Choose the right page</button>';\n  }else if(r.how===\"self\"){");
R("<button class=\"btn\" data-a=\"panel\" data-p=\"renewed\">It’s renewed</button></div>';",
  "<button class=\"btn\" data-a=\"panel\" data-p=\"renewed\">'+(LIC173[why]?'I’ve got it back':'It’s renewed')+'</button></div>';");
R('    case "p-cancel":',
`    case "lic173-ask":S.view.lic173Ask=true;render();break;
    case "lic173-why":if(t&&t.renew){var lw=b.getAttribute("data-v");if(lw!==t.renew.why){t.renew.why=lw;log(t,lw==="ban"?"Driving licence: needed again after a driving ban. Your choice.":lw==="health"?"Driving licence: needed again after a health condition. Your choice.":"Driving licence: it ran out. Your choice.")}S.view.lic173Ask=false;commit()}break;
    case "p-cancel":`);
R('SORTED_V="v172"','SORTED_V="v173"');
fs.writeFileSync('public/index.html',s);
const EXPECT='01d72dfa697d3b760cfad48c647e331e3dbec105';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v173 ok',h(s),s.length);
