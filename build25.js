const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='ea0646fd54b65d0a5809192e4ea92d3bc8f6d496')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v25: the notice states the deletion rules that actually run ----
R(`Cases you haven’t touched for 90 days are deleted automatically. If you haven’t added an email, your cases are deleted after 30 days away.`,`Cases you haven’t touched for 90 days are deleted automatically. If you haven’t added an email, your cases are deleted after 30 days away. Sorted waits longer while a case is waiting on a promise: until 30 days after it was due, or 30 days after an undated promise was recorded.`);
R(`Idle cases are deleted after 90 days, or 30 if you haven’t added an email. You can copy`,`Idle cases are deleted after 90 days, or 30 if you haven’t added an email, unless a promise on them is still pending. You can copy`,2);
R(`Sorted keeps this case for 90 days after your last change, in case the problem comes back.`,`Sorted keeps finished cases for 90 days after your last change, or 30 days if you haven’t added an email, in case the problem comes back.`);
fs.writeFileSync('public/index.html',s);
const EXPECT='acdf7776a5f6c608bf66b2899ce7fea67ce8a133';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v25 ok',h(s),s.length);
