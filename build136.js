const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='21f9f61dc6cfa8f002ba73e73975bf78cc1f89e5')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v136: a first visit meets one question; Moving home moves below the ideas; the guest note waits for a case. ----
R("  if(entryFirst)h+=momStartEntry();\n",
  "");
R("  if(newcomer)h+=momHomeBlock()+anonNote();\n",
  "  if(newcomer)h+=momHomeBlock();\n");
R("h+=ex95Explore();\n  h+='</main>';\n  return h;\n}\nfunction viewHomeLegacy",
  "h+=ex95Explore()+(entryFirst?'<div class=\"more136\">'+momStartEntry()+'</div>':'');\n  h+='</main>';\n  return h;\n}\nfunction viewHomeLegacy");
R("var SORTED_V=\"v135\"",
  "var SORTED_V=\"v136\"");
fs.writeFileSync('public/index.html',s);
const EXPECT='6386c397df153969095e0711aeff744fe2ed0316';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v136 ok',h(s),s.length);
