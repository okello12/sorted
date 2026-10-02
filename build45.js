const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='a34bb5edfefccc81f32e067ffa5f2e3f68f32e3b')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- home redesign follow-up: keep case details reachable and clarify the priority copy ----
R(`    h+='<div class="home44-actions" role="group" aria-label="'+esc(q[0])+'"><button class="btn primary" data-a="home-ans" data-v="kept" data-id="'+t.id+'">'+esc(q[1])+'</button><button class="btn" data-a="home-ans" data-v="missed" data-id="'+t.id+'">'+esc(q[2])+'</button><button class="btn" data-a="home-ans" data-v="rebook" data-id="'+t.id+'">They rescheduled</button></div>';`,
`    h+='<div class="home44-actions" role="group" aria-label="'+esc(q[0])+'"><button class="btn primary" data-a="home-ans" data-v="kept" data-id="'+t.id+'">'+esc(q[1])+'</button><button class="btn" data-a="home-ans" data-v="missed" data-id="'+t.id+'">'+esc(q[2])+'</button><button class="btn" data-a="home-ans" data-v="rebook" data-id="'+t.id+'">They rescheduled</button></div>';\n    h+='<button class="link home44-details" data-a="open" data-id="'+t.id+'">Open case details</button>';`);
R(`<p class="lede">Deal with this first. Sorted is holding the rest.</p>`,`<p class="lede">Start here. The rest of your open cases are below.</p>`);
R(`.home44-open{align-self:flex-start;margin-left:4px}`,
`.home44-open{align-self:flex-start;margin-left:4px}\n.home44-details{align-self:flex-start;margin-left:4px;padding:9px 0;min-height:44px}`);
fs.writeFileSync('public/index.html',s);
const EXPECT='5d20ad4f2f1e31e55f8251df03a57bd88a5d7281';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('home follow-up ok',h(s),s.length);
