const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
const BASE='66db11563237339739eda0a64b6dff532f5c4a1f';if(h(s)!==BASE)throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,90));s=s.split(a).join(b)}
// v107: SEM-03 must not write from render. Lazy seeding stays in memory until the next real case save.
R("function semDecorate(){if(S.view.name!=='task'||!S.view.id)return;var t=task(S.view.id);if(!t)return;var changed=semEnsure(t,true);if(changed)save();var p=t.factLedger&&t.factLedger.pending&&t.factLedger.pending[0];if(!p)return;",
  "function semDecorate(){if(S.view.name!=='task'||!S.view.id)return;var t=task(S.view.id);if(!t)return;semEnsure(t,false);var p=t.factLedger&&t.factLedger.pending&&t.factLedger.pending[0];if(!p)return;");
R("if(!m)return '';return m[1].replace(/\\s+(?:actually|instead|now)$/i,'').trim()}",
  "if(!m)return '';return m[1].replace(/\\s+(?:actually|instead|now)$/i,'').replace(/[.,;:!?]+$/,'').trim()}");
fs.writeFileSync('public/index.html',s);
const EXPECT='PENDING';if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v107 ok',h(s),s.length);
