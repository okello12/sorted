const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='fa2caae7e7239782e01204334cee548540f4630a')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v72: a reply that comes into a case sends its owner a short email (inbound-email v5, readers.mjs made from this
// page by tools/make_server_reader.js). The page counts opening the case from that email as a return, and the notice says so. ----
R("if(src===\"cal\"||src===\"email\"){var rph=returnPhase(t),prev=t.lastReturnAt,rep=!!(prev&&Date.now()-Date.parse(prev)<30*60000);logK(t,\"Opened from the \"+(src===\"cal\"?\"calendar\":\"email\")+\" link\"",
  "if(src===\"cal\"||src===\"email\"||src===\"reply\"){var rph=returnPhase(t),prev=t.lastReturnAt,rep=!!(prev&&Date.now()-Date.parse(prev)<30*60000);logK(t,\"Opened from the \"+(src===\"cal\"?\"calendar\":src===\"reply\"?\"reply\":\"email\")+\" link\"");
R("Sorted keeps only which website sent a reply, not the sender’s address.",
  "Sorted keeps only which website sent a reply, not the sender’s address. When a reply comes in, Sorted emails you to say so and what kind of reply it looks like (a no, good news, a date, or something else). That email never says which case, who sent it or what it says.");
fs.writeFileSync('public/index.html',s);
const EXPECT='af214e65dc8bea2880dae263157c7773cfdf35d4';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v72 ok',h(s),s.length);
