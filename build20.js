const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='33dfdb5291ed10dbc107a3680b61542c5ee2ab33')throw new Error('base mismatch '+h(s));
function R(a,b){const k=s.split(a).length-1;if(k!==1)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v20: survives 200% zoom; nothing below 14px that carries meaning ----
R(`.thread{list-style:none;margin:0;padding:0;display:flex;flex-direction:column}`,`.thread{list-style:none;margin:0;padding:0;display:flex;flex-direction:column}
.btn{max-width:100%;overflow-wrap:anywhere}
.slip-acts .btn{min-width:0}
.promise-head{flex-wrap:wrap}
.ref{white-space:normal;overflow-wrap:anywhere;max-width:100%}
.mark{min-height:44px}
.thread li>*{min-width:0;overflow-wrap:anywhere}
.eyebrow{font-size:14px}
.h1,.h2,.slip-title{overflow-wrap:break-word;hyphens:auto}
.thread .src{font-size:13px}
.prov{font-size:14px}
@media (max-width:340px){.thread li{grid-template-columns:1fr;gap:4px}.trail-d{grid-template-columns:1fr}.trail-d dd{margin-bottom:6px}.promise-head,.promise-body,.promise-foot{padding-left:12px;padding-right:12px}}`);
fs.writeFileSync('public/index.html',s);
const EXPECT='a9b8245f323619a9d1d4aed72e5c88df42a0e225';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v20 ok',h(s),s.length);
