const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='da781afccdb2bd98fa5950a13dbaddacf8f6aeb1')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,120));s=s.split(a).join(b)}
R("function intakeCategory(ph){ph=(ph||'').toLowerCase();",`function intakeCategory(ph){var sid='';try{sid=sessionStorage.getItem('sorted.cap82')||''}catch(e){}if(sid==='fix')return ['What’s broken?','Tell Sorted what stopped working and what has happened so far.'];if(sid==='call')return ['What’s the call about?','Tell Sorted who you need to contact and what you need from them.'];if(sid==='promise')return ['What did they promise?','Tell Sorted what they said they would do and when.'];if(sid==='chase')return ['What are you chasing?','Tell Sorted what you are waiting for and who needs to act.'];if(sid==='document')return ['What did you receive?','Tell Sorted what the letter or document is about, or add it below.'];if(sid==='renew')return ['What needs renewing or sorting?','Tell Sorted what it is and any deadline you already know.'];ph=(ph||'').toLowerCase();`);
fs.writeFileSync('public/index.html',s);
const EXPECT='0000000000000000000000000000000000000000';
if(false&&EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v89 candidate',h(s),s.length);
