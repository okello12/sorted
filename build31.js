const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='90b5b17ccad998d6a191341b457497f50e777221')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v31: the right safety question, honest next steps, how long it has been ----

// 1. "gas" alone is not danger ("British Gas engineer didn't turn up"); a gas smell or leak is
R(`|flame|gas\\b|smell of gas|melt|`,`|flame|smell(s|ing|ed)? (of )?gas|gas (leak|smell)|leaking gas|gas is leaking|melt|`);

// 2. heating asks about gas first
R(`    h+='<div class="stack-s"><span style="font-weight:600">Is anything burning, smoking or sparking, or is there water near the plug or socket?</span>`,`    h+='<div class="stack-s"><span style="font-weight:600">'+(/heating|boiler|hot water|radiator/i.test(item)?"Can you smell gas, or is anything burning, smoking or sparking?":"Is anything burning, smoking or sparking, or is there water near the plug or socket?")+'</span>`);

// 3. the case list names the real next step
R(`  if(t.mode==="fix"&&t.fix&&t.fix.step!=="done")return "Next: finish the checks";`,`  if(t.mode==="fix"&&t.fix&&t.fix.step!=="done")return t.fix.step==="checks"?"Next: finish the checks":"Next: a few quick questions";`);
R(`  if(!t.call)return "Next: get the call ready";`,`  if(!t.call)return "Next: "+lc1(ch(t.facts&&t.facts.benefit==="Universal Credit"?"account":"phone").prep);`);

// 4. how long it has been, when they said so
R(`  for(i=0;i<ITEMS.length;i++)if(ITEMS[i][0].test(s)){f.item=ITEMS[i][1];break}
  return f;`,String.raw`  for(i=0;i<ITEMS.length;i++)if(ITEMS[i][0].test(s)){f.item=ITEMS[i][1];break}
  var N="(?:\\d+|a|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|a few|several)\\s+(?:day|week|month)s?";
  m=new RegExp("\\b(?:for|been|over|nearly|almost|waiting)\\s+("+N+")\\b","i").exec(s)||new RegExp("\\b("+N+")\\s+(?:later|ago|now)\\b","i").exec(s);
  f.dur=m?m[1].toLowerCase():"";
  return f;`);
R(`  var hasFault=(f.item?"My "+item.toLowerCase():"It")+(fault?" has a fault: "+lc1(fault).replace(/[.!]+$/,""):" needs repairing")+".";`,`  var hasFault=(f.item?"My "+item.toLowerCase():"It")+(fault?" has a fault: "+lc1(fault).replace(/[.!]+$/,""):" needs repairing")+"."+(t.facts&&t.facts.dur?" It has been like this for "+t.facts.dur+".":"");`);
R(`ask="I’m getting in touch about a refund I’m still waiting for"+(t.facts.ref?" (reference "+t.facts.ref+")":"")+". Can you tell me`,`ask="I’m getting in touch about a refund I’m still waiting for"+(t.facts.ref?" (reference "+t.facts.ref+")":"")+"."+(t.facts.dur?" I have been waiting "+t.facts.dur+".":"")+" Can you tell me`);
R(`(t.facts.ref?" (reference "+t.facts.ref+")":"")+". Can you tell me what is happening and when`,`(t.facts.ref?" (reference "+t.facts.ref+")":"")+"."+(t.facts.dur?" I have been waiting "+t.facts.dur+".":"")+" Can you tell me what is happening and when`);

// 5. after a landlord misses a repair date: an honest note on where else to turn
R(`  if(t.facts&&t.facts.kind==="benefit")h+=benefitNote(t);`,`  if(t.facts&&t.facts.kind==="benefit")h+=benefitNote(t);
  if(m&&((t.fix&&t.fix.responsible==="landlord")||(t.facts&&t.facts.resp==="landlord")))h+=housingNote();`);
R(`function benefitNote(t){`,`function housingNote(){
  return '<div class="note stack-s"><p><strong>If your landlord still doesn’t fix it.</strong> Sorted keeps the dates and what they told you, which is the record you’d need. It doesn’t give legal advice.</p><p>For serious problems like no heating, damp or mould, your local council may be able to step in. For free housing advice, contact Shelter at <a class="link" href="https://www.shelter.org.uk/" target="_blank" rel="noopener">shelter.org.uk</a> or Citizens Advice at <a class="link" href="https://www.citizensadvice.org.uk/" target="_blank" rel="noopener">citizensadvice.org.uk</a>.</p></div>';
}
function benefitNote(t){`);

// 6. a chased repair names the repair; the call card never says "The fault: Something else"
R(`t.facts&&t.facts.kind==="benefit"?"my "+t.facts.benefit.replace(/^DWP$/,"claim"):lc1(t.title)`,`t.facts&&t.facts.kind==="benefit"?"my "+t.facts.benefit.replace(/^DWP$/,"claim"):t.fix&&t.fix.item?"the repair to my "+t.fix.item.toLowerCase():lc1(t.title)`);
R(`if(f.fault)out.push("The fault: "`,`if(f.fault&&f.fault!=="other")out.push("The fault: "`);

// 7. links inside a sentence in a note stay in the sentence
R(`a.btn.wa{border-color:#1F7A4D;color:#1F7A4D}`,`a.btn.wa{border-color:#1F7A4D;color:#1F7A4D}
.note p a.link{display:inline;min-height:0;padding:0}`);

fs.writeFileSync('public/index.html',s);
const EXPECT='a13026c2842997ee4b04be1cdeefef73d64020a4';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v31 ok',h(s),s.length);
