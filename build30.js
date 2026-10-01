const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='dc9fe39ac92ae705c4d1dbaed1b31ab4c3a6747f')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v30: start from what the person said ----
// 1. read the first sentence: what kind of problem, who, which reference, which thing
R(`function caseMode(text){
  var s=String(text||"").toLowerCase();`,String.raw`var PARTIES=[[/\bcurrys\b/i,"Currys"],[/\bamazon\b/i,"Amazon"],[/\bargos\b/i,"Argos"],[/\bjohn lewis\b/i,"John Lewis"],[/\bAO(\.com)?\b/,"AO"],[/\bebay\b/i,"eBay"],[/\bikea\b/i,"IKEA"],[/\bapple\b/i,"Apple"],[/\bsamsung\b/i,"Samsung"],[/\bdyson\b/i,"Dyson"],[/\bBoots\b/,"Boots"],[/\btesco\b/i,"Tesco"],[/\bsainsbury.?s\b/i,"Sainsbury’s"],[/\basda\b/i,"Asda"],[/\bbt\b/i,"BT"],[/\bvirgin media\b/i,"Virgin Media"],[/\bsky\b/i,"Sky"],[/\bEE\b/,"EE"],[/\bo2\b/i,"O2"],[/\bvodafone\b/i,"Vodafone"],[/\bbritish gas\b/i,"British Gas"],[/\boctopus\b/i,"Octopus Energy"],[/\bovo\b/i,"OVO"],[/\bedf\b/i,"EDF"],[/\be\.?on\b/i,"E.ON"],[/\bthames water\b/i,"Thames Water"],[/\broyal mail\b/i,"Royal Mail"],[/\bevri\b|\bhermes\b/i,"Evri"],[/\bdpd\b/i,"DPD"],[/\bdhl\b/i,"DHL"],[/\bryanair\b/i,"Ryanair"],[/\beasyjet\b/i,"easyJet"],[/\bhmrc\b/i,"HMRC"],[/\bdvla\b/i,"DVLA"],[/\bletting agent\b|\bletting agency\b/i,"the letting agent"],[/\bhousing association\b/i,"the housing association"],[/\bcouncil\b/i,"the council"]];
var BENEFITS=[[/\buniversal credit\b|\buc\b/i,"Universal Credit","DWP"],[/\bpip\b|personal independence/i,"PIP","DWP"],[/\besa\b/i,"ESA","DWP"],[/\bjsa\b|jobseeker/i,"Jobseeker’s Allowance","DWP"],[/\bhousing benefit\b/i,"Housing Benefit","the council"],[/\bchild benefit\b/i,"Child Benefit","HMRC"],[/\bpension credit\b/i,"Pension Credit","DWP"],[/\bcarer.?s allowance\b/i,"Carer’s Allowance","DWP"],[/\bdwp\b/i,"DWP","DWP"]];
var ITEMS=[[/washing machine/i,"Washing machine"],[/\bboiler\b|\bheating\b|\bradiator|\bhot water\b/i,"Heating or hot water"],[/\bfridge|\bfreezer/i,"Fridge or freezer"],[/dishwasher/i,"Dishwasher"],[/tumble dryer|\bdryer\b/i,"Tumble dryer"],[/\boven\b|\bcooker\b|\bhob\b/i,"Oven or cooker"],[/\bshower\b/i,"Shower"],[/\btoilet\b/i,"Toilet"],[/\bdamp\b|\bmould\b|\bmold\b/i,"Damp or mould"],[/\blaptop\b/i,"Laptop"],[/\bphone\b/i,"Phone"],[/\bwindow/i,"Window"],[/\bdoor\b|\block\b/i,"Door or lock"],[/\broof\b|\bceiling\b/i,"Roof or ceiling"],[/\bleak/i,"Leak"]];
function caseFacts(text){
  var s=String(text||""),f={kind:"other",party:"",ref:"",item:"",resp:"",benefit:""},i,m;
  for(i=0;i<BENEFITS.length;i++)if(BENEFITS[i][0].test(s)){f.kind="benefit";f.benefit=BENEFITS[i][1];f.party=BENEFITS[i][2];break}
  if(f.kind==="other"&&/\b(refund|refunded|money back|reimburs\w*|compensation|overcharged|charged (me )?twice|double charged|chargeback|owe[sd]? me|deposit back)\b/i.test(s))f.kind="money";
  if(!f.party)for(i=0;i<PARTIES.length;i++)if(PARTIES[i][0].test(s)){f.party=PARTIES[i][1];break}
  if(/\blandlord\b|\bletting agent|\bhousing association\b|\btenan(t|cy)\b|\brent(ing|ed)?\b/i.test(s))f.resp="landlord";else if(/\b(halls|student accommodation)\b/i.test(s))f.resp="uni";
  m=/\b(?:order|ref(?:erence)?|case|claim|job|ticket|booking|policy|complaint)\s*(?:no\.?|number|num|#|:)?\s*([A-Z0-9][A-Z0-9\/-]{3,})/i.exec(s);
  if(m&&/\d/.test(m[1]))f.ref=m[1].toUpperCase();
  else{m=/\b([A-Z]{1,5}-?\d{4,})\b/.exec(s);if(m)f.ref=m[1]}
  for(i=0;i<ITEMS.length;i++)if(ITEMS[i][0].test(s)){f.item=ITEMS[i][1];break}
  return f;
}
function lc1(x){x=String(x||"");var w=(x.match(/^\S+/)||[""])[0];if(PARTIES.some(function(p){return p[0].test(w)}))return x;return /^[A-Z][a-z]/.test(x)?x.charAt(0).toLowerCase()+x.slice(1):x}
function cap1(x){x=String(x||"");return x.charAt(0).toUpperCase()+x.slice(1)}
function shortTitle(text,f){
  var t="";
  if(f.kind==="money")t=(f.party&&!/^the /.test(f.party)?f.party+" refund":"Refund");
  else if(f.kind==="benefit")t=f.benefit;
  else if(f.item&&caseMode(text)==="fix")t=f.item+(f.resp==="landlord"?" · landlord":f.resp==="uni"?" · accommodation":f.party?" · "+f.party.replace(/^the /,""):"");
  if(t)return t+(f.ref?" · "+f.ref:"");
  var c=String(text||"").split(/[.;!?]|,\s|\s[-–]\s/)[0].trim();
  if(c.length>48){c=c.slice(0,48);c=c.slice(0,Math.max(c.lastIndexOf(" "),20))+"…"}
  return cap1(c);
}
function caseMode(text){
  var s=String(text||"").toLowerCase(),cf=caseFacts(text);
  if(cf.kind!=="other")return "call";`);

// 2. create the case with the short title, the person's full words kept in the timeline, and the facts carried in
R(`    var cm=caseMode(ctx),ctitle=ctx.length>90?ctx.slice(0,88)+"…":ctx;`,`    var cm=caseMode(ctx),cfx=caseFacts(ctx),ctitle=shortTitle(ctx,cfx);`);
R(`S.pendingSafety={title:ctitle}`,`S.pendingSafety={title:ctitle,said:ctx,facts:cfx}`);
R(`S.draft={step:"baseline",title:ctitle,baseline:"",fromCase:true};render();window.scrollTo(0,0);return;`,`S.draft={step:"baseline",title:ctitle,baseline:"",fromCase:true,said:ctx,facts:cfx};render();window.scrollTo(0,0);return;`);
R(`S.draft={step:(S.pendingSafety&&S.pendingSafety.title)?"baseline":"title",title:(S.pendingSafety&&S.pendingSafety.title)||"",baseline:"",safety:true};render()}`,`S.draft={step:(S.pendingSafety&&S.pendingSafety.title)?"baseline":"title",title:(S.pendingSafety&&S.pendingSafety.title)||"",baseline:"",safety:true,said:S.pendingSafety&&S.pendingSafety.said,facts:S.pendingSafety&&S.pendingSafety.facts};render()}`);
R(`  log(t,t.mode==="do"?"Started.":"Started. Before any advice, the plan was: “"+t.baseline+"”");`,`  if(d.facts){t.facts=d.facts;t.said=d.said||"";
    if(t.fix){if(d.facts.item)t.fix.item=d.facts.item;else if(!/washing machine/i.test(t.said))t.fix.item="";if(d.facts.resp)t.fix.responsible=d.facts.resp;if(d.facts.party&&!/^the /.test(d.facts.party)&&d.facts.resp!=="landlord")t.fix.party=d.facts.party;if(d.facts.ref)t.fix.jobRef=d.facts.ref}}
  if(t.said&&t.said!==t.title)log(t,"In your words: “"+t.said.replace(/[.!]+$/,"")+"”");
  log(t,t.mode==="do"?"Started.":"Started. Before any advice, the plan was: “"+t.baseline+"”");`);

// 3. repairs start from the thing they named, not a washing machine
R(`    var item=d.item!==undefined?d.item:(f.item||"Washing machine"),fault=d.fault!==undefined?d.fault:f.fault;`,`    var item=d.item!==undefined?d.item:(f.item!==undefined?f.item:"Washing machine"),fault=d.fault!==undefined?d.fault:f.fault;`);
R(`  var item=d.item!==undefined?d.item:(f.item||"Washing machine");
  f.item=item||f.item||"";`,`  var item=d.item!==undefined?d.item:(f.item!==undefined?f.item:"Washing machine");
  f.item=item||f.item||"";`);
R(`    var item=d.item!==undefined?d.item:(t.fix.item||"Washing machine");`,`    var item=d.item!==undefined?d.item:(t.fix.item!==undefined?t.fix.item:"Washing machine");`);

// 4. messages use what they already told Sorted, and never say "a fault: something else"
R(`  var fault=label(FAULTS,f.fault)||f.detail||"a fault";`,`  var fault=(f.fault&&f.fault!=="other"?label(FAULTS,f.fault):"")||f.detail||"";`);
R(`  if(kind==="report"){who=f.party||"";ask="My "+item.toLowerCase()+" has a fault: "+fault.toLowerCase()+". Please arrange a repair and give me a date."+(f.jobRef?" My job number is "+f.jobRef+".":"")}`,`  var hasFault=(f.item?"My "+item.toLowerCase():"It")+(fault?" has a fault: "+lc1(fault).replace(/[.!]+$/,""):" needs repairing")+".";
  if(kind==="report"){who=f.party||(f.responsible==="landlord"?"My landlord":"");ask=hasFault+" Please arrange a repair and give me a date."+(f.jobRef?" My reference is "+f.jobRef+".":"")}`);
R(`ask="My "+item.toLowerCase()+" has a fault: "+fault.toLowerCase()+"."+((agoText(f.age)`,`ask=hasFault+((agoText(f.age)`);
R(`ask="My "+item.toLowerCase()+" has a fault: "+fault.toLowerCase()+". Can you give me a price`,`ask=hasFault+" Can you give me a price`);
R(`  else if(t.mode==="call"&&t.title){
    var parts=t.title.split(/\\s+about\\s+/i);`,`  else if(t.mode==="call"&&t.facts&&t.facts.kind==="money"){
    who=t.facts.party||"";ask="I’m getting in touch about a refund I’m still waiting for"+(t.facts.ref?" (reference "+t.facts.ref+")":"")+". Can you tell me the date it will be paid, and confirm that in writing?";
  }
  else if(t.mode==="call"&&t.facts&&t.facts.kind==="benefit"){
    who=t.facts.party||"";ask="I’m getting in touch about my "+t.facts.benefit.replace(/^DWP$/,"claim")+(t.facts.ref?" (reference "+t.facts.ref+")":"")+". Can you tell me what is happening and when, and confirm it in writing?";
  }
  else if(t.mode==="call"&&t.said){
    who=t.facts&&t.facts.party?cap1(t.facts.party):(t.facts&&t.facts.resp==="landlord"?"My landlord":"");ask="I’m getting in touch about this: "+lc1(t.said).replace(/[.!]+$/,"")+"."+(t.facts&&t.facts.ref?" My reference is "+t.facts.ref+".":"")+" ";
  }
  else if(t.mode==="call"&&t.title){
    var parts=t.title.split(/\\s+about\\s+/i);`);
R(`else{who="";ask="I’m getting in touch about "+t.title.charAt(0).toLowerCase()+t.title.slice(1)+". "}`,`else{who="";ask="I’m getting in touch about "+lc1(t.title)+". "}`);
// a missed promise without a reference names the case sensibly
R(`ask="Hi, I’m getting in touch about "+(m.ref?"reference "+m.ref:t.title.charAt(0).toLowerCase()+t.title.slice(1).replace(/[.!]+$/,""))`,`ask="Hi, I’m getting in touch about "+(m.ref?"reference "+m.ref:t.facts&&t.facts.kind==="money"?"my refund":t.facts&&t.facts.kind==="benefit"?"my "+t.facts.benefit.replace(/^DWP$/,"claim"):lc1(t.title).replace(/ · .*$/,"").replace(/[.!]+$/,""))`);
// Universal Credit: the journal is the default way in
R(`via=d.via!==undefined?d.via:(t.call?t.call.via:(t.renew&&t.renew.via)||"phone");`,`via=d.via!==undefined?d.via:(t.call?t.call.via:(t.renew&&t.renew.via)||(t.facts&&t.facts.benefit==="Universal Credit"?"account":"phone"));`);

// 5. benefits: say plainly what Sorted does and doesn't know
R(`  h+=checkPanel(via);
  if(d.err)h+='<p class="err">'+esc(d.err)+'</p>';
  h+='<button class="btn primary block" type="submit">Save</button>'+(t.call?`,`  h+=checkPanel(via);
  if(t.facts&&t.facts.kind==="benefit")h+=benefitNote(t);
  if(d.err)h+='<p class="err">'+esc(d.err)+'</p>';
  h+='<button class="btn primary block" type="submit">Save</button>'+(t.call?`);
R(`function ch(via){return CH[via]||CH.phone}`,`function ch(via){return CH[via]||CH.phone}
function benefitNote(t){
  var org=t.facts.party||"DWP";
  return '<div class="note stack-s"><p><strong>What Sorted can and can’t do here.</strong> Sorted keeps the dates and what they told you, and helps you write. It doesn’t know how '+esc(org)+' handles cases, so it won’t tell you what to expect.</p>'+(t.facts.benefit==="Universal Credit"?'<p>For Universal Credit, writing in the journal in your online account keeps a record they can see.</p>':'')+'<p>For free, independent help, contact Citizens Advice at <a class="link" href="https://www.citizensadvice.org.uk/" target="_blank" rel="noopener">citizensadvice.org.uk</a>.</p></div>';
}`);

fs.writeFileSync('public/index.html',s);
const EXPECT='90b5b17ccad998d6a191341b457497f50e777221';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v30 ok',h(s),s.length);
