const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='35dee41e03cf8879e379c3c340f3106a22cbd7c3')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+String(a).slice(0,70));s=s.split(a).join(b)}
// ---- v12: one person across an anonymous start and an existing account ----
R(`var cem=d.cemail;sb.auth.signOut().finally(function(){`,`var cem=d.cemail;sb.rpc("stash_carry").then(function(r){try{if(r&&r.data)localStorage.setItem("sorted.carrytok",r.data)}catch(e){}},function(){}).then(function(){return sb.auth.signOut()}).finally(function(){`);
R(`list.forEach(function(ct){ct.id=uid();`,`var pairs=[];list.forEach(function(ct){pairs.push([ct.id,ct.id=uid()]);`);
R(`  if(list.length){save();render();toast(`,`  var ctok=null;try{ctok=localStorage.getItem("sorted.carrytok");localStorage.removeItem("sorted.carrytok")}catch(e){}\n  if(ctok)sb.rpc("claim_carry",{p_token:ctok,p_pairs:pairs}).then(function(){},function(){});\n  if(list.length){save();render();toast(`);
R(`pct(f.promised,f.started)+" of started"`,`(f.started?pct(f.promised,f.started)+" of started":"")`);
R(`pct(f.acted,f.returned)+" of returns"`,`(f.returned?pct(f.acted,f.returned)+" of returns":"")`);
R(`pct(f.closed,f.acted)+" of those"`,`(f.acted?pct(f.closed,f.acted)+" of those":"")`);
fs.writeFileSync('public/index.html',s);
const EXPECT='3139a5a5c3b18d7b335f1851483870c63d2c301d';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v12 ok',h(s),s.length);
