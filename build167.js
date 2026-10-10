const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='9f2fec997d17d07a62c6e7bb7f4852fed833e80b')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v167: from Baldwin's iPhone (10 October 2026). A "Heating or hot water" case showed "What is it, and what's it
// doing?" with "What is it?" empty. Every way of starting a repair names the thing; the name was wiped on the case by
// tapping "Something else", which was already the choice shown: its value was always empty. Now "Something else" keeps
// the name the case already has (from Washing machine it goes back to the case's own name, if it isn't a washing
// machine), and a repair whose name is missing is named again from the person's words, as at the start.
R(`    var item=d.item!==undefined?d.item:(f.item!==undefined&&f.item!==null?f.item:""),fault=d.fault!==undefined?d.fault:f.fault;`,
  `    var item=d.item!==undefined?d.item:(f.item!==undefined&&f.item!==null?f.item:""),fault=d.fault!==undefined?d.fault:f.fault;if(d.item===undefined&&!item){var it167=(caseFacts(String(t.said||"")).item||thingOf(String(t.said||""))||"");if(it167&&it167!=="Washing machine")item=it167}var keep167=item!=="Washing machine"?item:(f.item&&f.item!=="Washing machine"?f.item:"");`);
R(`data-a="d" data-k="item" data-v="'+(x==="Washing machine"?"Washing machine":"")+'" aria-pressed="'+on+'">'+x+'</button>'}).join("")+'</div>';`,
  `data-a="d" data-k="item" data-v="'+(x==="Washing machine"?"Washing machine":esc(keep167))+'" aria-pressed="'+on+'">'+x+'</button>'}).join("")+'</div>';`);
R('  if(k==="what"){\n    var item=d.item!==undefined?d.item:(t.fix.item!==undefined&&t.fix.item!==null?t.fix.item:"");',
  '  if(k==="what"){\n    var item=d.item!==undefined?d.item:(t.fix.item!==undefined&&t.fix.item!==null?t.fix.item:"");if(d.item===undefined&&!item){var it167s=(caseFacts(String(t.said||"")).item||thingOf(String(t.said||""))||"");if(it167s&&it167s!=="Washing machine")item=it167s}');
s=s.split('SORTED_V="v166"').join('SORTED_V="v167"');
fs.writeFileSync('public/index.html',s);
const EXPECT='aff1b674955dfc1393a785c0f847d5ce769cb354';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v167 ok',h(s),s.length);
