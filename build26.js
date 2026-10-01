const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='acdf7776a5f6c608bf66b2899ce7fea67ce8a133')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v26: a contact for the controller, everywhere the notice appears ----
var M='<a class="link" href="mailto:old-contact@sorted.invalid">old-contact@sorted.invalid</a>';
R(`who decides how your data is used.</p>`,`who decides how your data is used. Contact him at `+M+`.</p>`);
R(`You can also ask for a copy, a correction or deletion, and you can complain`,`You can also ask for a copy, a correction or deletion by emailing `+M+`, and you can complain`);
R(`a UK research pilot run by Baldwin Thompson-Addo. Sorted keeps`,`a UK research pilot run by Baldwin Thompson-Addo (`+M+`). Sorted keeps`,2);
R(`Sorted is a UK research pilot run by Baldwin Thompson-Addo in London.`,`Sorted is a UK research pilot run by Baldwin Thompson-Addo in London. Contact: `+M+`.`);
fs.writeFileSync('public/index.html',s);
const EXPECT='82486be8a2f949f29c25e8a1f3532780641527f6';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v26 ok',h(s),s.length);
