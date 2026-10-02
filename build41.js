const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='15278abd8a8431350f97cb8ddfec2231d60c7904')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v41: the notice covers the last two database changes (2 October 2026) ----
// Shipped before the database change runs, so the notice is never behind what Sorted does.

// helper protections: a stopped helper's address is kept only as a one-way hash, so they are never emailed again
R(`If you ask Sorted to nudge a helper, it keeps their email address, asks them first, and deletes it when you switch the helper link off.`,
  `If you ask Sorted to nudge a helper, it keeps their email address, asks them first, and deletes it when you switch the helper link off. If they ask Sorted to stop, it keeps a scrambled, one-way copy of their address so it never emails them again.`);
// idle accounts
R(`Sorted waits longer while a case is waiting on a promise: until 30 days after it was due, or 30 days after an undated promise was recorded.`,
  `Sorted waits longer while a case is waiting on a promise: until 30 days after it was due, or 30 days after an undated promise was recorded. An account with an email but no cases is deleted after 12 months without a sign-in.`);

fs.writeFileSync('public/index.html',s);
const EXPECT='869655438477e79505f7cbb8fa05061bc82a2556';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v41 ok',h(s),s.length);
