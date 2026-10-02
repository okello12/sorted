const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='869655438477e79505f7cbb8fa05061bc82a2556')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v42: forwarding addresses were removed from the database on 2 October 2026, so the page stops asking for one ----
R(`function loadInbox(){\n  sb.rpc("my_inbound_address")`,
  `function loadInbox(){\n  S.inboundAddr=null;S.inbox=[];return;   /* forwarding is off (v28) and its addresses are gone; see docs/LATER.md item 2 */\n  sb.rpc("my_inbound_address")`);
fs.writeFileSync('public/index.html',s);
const EXPECT='69d86b6da5c1ed43d34d729424c9ce2be73a0480';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v42 ok',h(s),s.length);
