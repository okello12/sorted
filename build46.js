const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='5d20ad4f2f1e31e55f8251df03a57bd88a5d7281')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- preserve the old Home test hooks while the visual structure changes ----
R(`h='<section class="home44-spot" aria-labelledby="home44-spot-title">'`,`h='<section class="home44-spot slip" aria-labelledby="home44-spot-title">'`);
R(`class="link home44-details" data-a="open"`,`class="link home44-details slip-open" data-a="open"`);
fs.writeFileSync('public/index.html',s);
const EXPECT='f030407b7577e550857c1ecfc04a12bb70354f8b';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('home compatibility hooks ok',h(s),s.length);
