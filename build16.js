const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='14b9c0d1a138eeaa2a37a1541a0e37e676b1d244')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+String(a).slice(0,70));s=s.split(a).join(b)}
// ---- v16: the case trail. Entries open to show the promise behind them, only when there is more to show ----
R(`function evRow(e){
  var src=evSource(e),txt=src==="They said"?e.label.replace(/^They said: /,""):e.label;
  return '<li><time datetime="'+e.at+'">'+stampLabel(e.at)+'</time><span><span class="src">'+src+'</span>'+esc(txt)+'</span></li>';
}`,`function evPromise(e,t){
  if(!t||!t.promises||!t.promises.length)return null;
  var L=e.label||"",key=null;
  if(/^They said: |^Waiting for their reply/.test(L))key="loggedAt";
  else if(/^They kept it: |^It didn’t happen: |^They changed the date\\. |^Asked them for a date\\./.test(L))key="closedAt";
  if(!key)return null;
  var at=Date.parse(e.at),best=null,gap=3000;
  t.promises.forEach(function(p){if(!p[key])return;var g=Math.abs(Date.parse(p[key])-at);if(g<=gap){gap=g;best=p}});
  return best;
}
function promiseDetail(p,t){
  var i=t.promises.indexOf(p),next=null;
  for(var j=i+1;j<t.promises.length;j++){if(t.promises[j].loggedAt&&p.closedAt&&Date.parse(t.promises[j].loggedAt)>=Date.parse(p.closedAt)-3000){next=t.promises[j];break}}
  var out={open:(p.dueAt&&phase(p)==="check")?"Due. Not confirmed yet":"Still open",kept:"Kept",missed:"Missed",replaced:"Replaced"}[p.status]||"";
  if(p.closedAt&&p.status!=="open")out+=", "+stampLabel(p.closedAt);
  if(p.status==="replaced")out+=next?". New date: "+whenText(next):". They were asked for a new date";
  var rows=[["Who",p.party||"Them"],["They said",p.said],["When",whenText(p)]];
  if(p.ref)rows.push(["Reference",p.ref]);
  rows.push(["Outcome",out]);
  if(p.loggedAt)rows.push(["Recorded",stampLabel(p.loggedAt)+(p.src==="email"?", from a forwarded email":p.src==="letter"?", from your letter":", from your note")]);
  return '<dl class="trail-d">'+rows.map(function(r){return '<dt>'+r[0]+'</dt><dd'+(r[0]==="Reference"?' class="mono"':'')+'>'+esc(r[1])+'</dd>'}).join("")+'</dl>';
}
function evRow(e,t){
  var src=evSource(e),txt=src==="They said"?e.label.replace(/^They said: /,""):e.label,p=evPromise(e,t);
  var head='<span class="src">'+src+'</span>'+esc(txt);
  if(!p)return '<li><time datetime="'+e.at+'">'+stampLabel(e.at)+'</time><span>'+head+'</span></li>';
  var k=t.id+"|"+e.at+"|"+(e.label||"");
  return '<li><time datetime="'+e.at+'">'+stampLabel(e.at)+'</time><details class="trail" data-k="'+esc(k)+'"'+((S.openTrail||{})[k]?" open":"")+'><summary>'+head+'</summary>'+promiseDetail(p,t)+'</details></li>';
}`);
R(`t.events.slice().reverse().forEach(function(e){h+=evRow(e)});`,`t.events.slice().reverse().forEach(function(e){h+=evRow(e,t)});`);
// keep an opened entry open when the page re-renders
R(`\ndocument.addEventListener("input",function(e){`,`\ndocument.addEventListener("toggle",function(e){var d=e.target;if(!d||!d.classList||!d.classList.contains("trail"))return;S.openTrail=S.openTrail||{};var k=d.getAttribute("data-k");if(d.open)S.openTrail[k]=1;else delete S.openTrail[k]},true);\ndocument.addEventListener("input",function(e){`);
R(`.thread .src{display:block;font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2)}`,`.thread .src{display:block;font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2)}
.thread details.trail>summary{cursor:pointer;list-style:none;position:relative;padding-right:28px;min-height:44px;font-weight:400;margin-top:0}
.thread details.trail>summary::-webkit-details-marker{display:none}
.thread details.trail>summary::after{content:"";position:absolute;right:6px;top:22px;width:8px;height:8px;border-right:2px solid var(--ink-2);border-bottom:2px solid var(--ink-2);transform:rotate(45deg);transition:transform .15s}
.thread details.trail[open]>summary::after{transform:rotate(-135deg);top:26px}
.thread details.trail>summary:focus-visible{outline:3px solid var(--ink);outline-offset:2px}
.trail-d{display:grid;grid-template-columns:auto 1fr;gap:4px 12px;margin:10px 0 2px;padding:10px 12px;background:var(--sheet);border:1px solid var(--rule);border-radius:6px;font-size:15px}
.trail-d dt{color:var(--ink-2);font-weight:600}
.trail-d dd{margin:0;overflow-wrap:anywhere}`);

fs.writeFileSync('public/index.html',s);
const EXPECT='153ec7b8e8445584541aa853775929a11e6237ee';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v16 ok',h(s),s.length);
