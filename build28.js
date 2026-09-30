const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='cc73c485a42ae702aebe2564a6cfdb4701485346')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v28: email forwarding switched off for the pilot ----
// the app no longer offers a forwarding address (emails already forwarded can still be used until they expire)
R(`function forwardHint(){
  if(!S.inboundAddr||!S.user||!S.user.email)return "";`,`function forwardHint(){
  return ""; /* forwarding is off for the pilot */
  if(!S.inboundAddr||!S.user||!S.user.email)return "";`);
// the notice says what is true now
R(`Emails you forward to your Sorted address are kept for 30 days, then deleted.`,`Forwarding emails into Sorted is switched off during the pilot. Any email forwarded before that is deleted after 30 days.`);
R(`Resend sends Sorted’s emails and receives emails you forward. Vercel and Resend are US companies, so your email address, and any email you forward, may be processed in the US under their data protection terms.`,`Resend sends Sorted’s emails. Vercel and Resend are US companies, so your email address may be processed in the US under their data protection terms.`);
fs.writeFileSync('public/index.html',s);
const EXPECT='aa22748e3d1c0e783be315c653e9b4500bd14e58';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v28 ok',h(s),s.length);
