const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='b04faec3a0920092ab6cbf20b9233e850e3fb736')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+String(a).slice(0,70));s=s.split(a).join(b)}
// ---- v15: the empty list describes all of Sorted, not only promises ----
R(`Nothing here yet. When someone promises you something, it sits here like this until it’s due.`,`Nothing here yet. Start with what you need to sort out, and Sorted will keep the next step here.`);
fs.writeFileSync('public/index.html',s);
const EXPECT='14b9c0d1a138eeaa2a37a1541a0e37e676b1d244';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v15 ok',h(s),s.length);
