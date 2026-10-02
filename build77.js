const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='d235608a07c6225cf54afc0f1a386d4509a5042a')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,80));s=s.split(a).join(b)}
// v77: the two collapsed case groups stay available while a current action panel is open.
// A person can add a message, use sharing, or reach the record without abandoning the live step.
R('  if(!S.view.panel)h+=case75Secondary(t,s);','  h+=case75Secondary(t,s);');
fs.writeFileSync('public/index.html',s);
const EXPECT='';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v77 ok',h(s),s.length);
