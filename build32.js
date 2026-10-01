const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='a13026c2842997ee4b04be1cdeefef73d64020a4')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v32: the gaps from the v31 live check ----

// 1. duration: any "two weeks" / "2 weeks" in the sentence counts, except a promise window ("in 14 days", "within 10 days")
R(String.raw`  m=new RegExp("\\b(?:for|been|over|nearly|almost|waiting)\\s+("+N+")\\b","i").exec(s)||new RegExp("\\b("+N+")\\s+(?:later|ago|now)\\b","i").exec(s);
  f.dur=m?m[1].toLowerCase():"";`,String.raw`  var re=new RegExp("(\\b\\w+\\s+)?\\b("+N+")\\b","ig");f.dur="";
  while((m=re.exec(s))){if(!/^(in|within|after|every|by)\s+$/i.test(m[1]||"")){f.dur=m[2].toLowerCase();break}}`);

// 2. a gas-related stop screen leads with gas
R(`function safetyBlock(){
  return '<section class="safety stack" role="alert"><h1 class="h2">Stop. Don’t use it.</h1>'+
  '<ul class="stack-s" style="margin:0;padding-left:1.1em">'+
  '<li>If you can reach the socket safely, switch it off at the wall. If not, leave it.</li>'+
  '<li>Don’t open it, touch wiring, or mop water near the plug.</li>'+
  '<li>Smell gas? Don’t use switches. Open windows, leave, and call the gas emergency line: <span class="mono">0800 111 999</span>.</li>'+`,`function safetyBlock(){
  var st=S.view.id&&task(S.view.id),ctx=(st?[st.title,st.fix&&st.fix.item,st.fix&&st.fix.detail].join(" "):(S.pendingSafety&&S.pendingSafety.title)||""),gasy=/heating|boiler|hot water|radiator|gas/i.test(ctx);
  var gasLi='<li>Smell gas? Don’t use switches. Open windows, leave, and call the gas emergency line: <span class="mono">0800 111 999</span>.</li>';
  return '<section class="safety stack" role="alert"><h1 class="h2">Stop. Don’t use it.</h1>'+
  '<ul class="stack-s" style="margin:0;padding-left:1.1em">'+(gasy?gasLi:'')+
  '<li>If you can reach the socket safely, switch it off at the wall. If not, leave it.</li>'+
  '<li>Don’t open it, touch wiring, or mop water near the plug.</li>'+(gasy?'':gasLi)+`);

// 3. only a landlord or accommodation gets the "repairs to heating and the building" line; someone else gets a plain one
R(`  if(f.responsible&&f.responsible!=="me"){
    return {key:"report",title:"Report it to "+whoName(t),`,`  if(f.responsible==="other"||f.responsible==="employer"){
    return {key:"report",title:"Get "+whoName(t)+" to fix it",
      body:"You said it’s "+whoName(t)+"’s job to fix this. Contact them in writing if you can, so there is a record, and ask for a date. If a visit was missed, say so and ask for a new one."};
  }
  if(f.responsible&&f.responsible!=="me"){
    return {key:"report",title:"Report it to "+whoName(t),`);
// a company name guessed from the sentence isn't put forward as the landlord
R(`value="'+esc(d.party!==undefined?d.party:(f.party||""))+'">`,`value="'+esc(d.party!==undefined?d.party:(f.partyAuto&&(r==="landlord"||r==="uni")?"":(f.party||"")))+'">`);
R(`if(d.facts.party&&!/^the /.test(d.facts.party)&&d.facts.resp!=="landlord")t.fix.party=d.facts.party;`,`if(d.facts.party&&!/^the /.test(d.facts.party)&&d.facts.resp!=="landlord"){t.fix.party=d.facts.party;t.fix.partyAuto=true}`);

fs.writeFileSync('public/index.html',s);
const EXPECT='84f16740bfe11b1c708ffeb3cba0d7b952f586b7';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v32 ok',h(s),s.length);
