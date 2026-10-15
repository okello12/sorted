const fs=require('fs'),c=require('crypto');
const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='14fc5910f24349bf9a6cc972ae91a5dd575c08eb')throw new Error('base mismatch '+h(s));
function R(a,b){const k=s.split(a).length-1;if(k!==1)throw new Error('match '+k+': '+a.slice(0,70));s=s.replace(a,b)}
// Presentation only: reuse attention and date wording. No new case decisions, writes or model calls.
const UI=String.raw`
/* v169: make the existing attention decisions visible and inspectable. */
function home169Reason(t){
  var a=attention(t),why=a.why,body;
  if(why)body=why+'. Check the case before deciding what to do. A date passing does not tell Sorted whether it happened.';
  else if(t.sugP&&!t.sugDone)body='What they promised is still a suggestion. Check it before Sorted tracks it as a promise.';
  else body='This case is in Needs you. Open it to review or change the next move.';
  return '<details class="context169-why"><summary>Why this is next</summary><p>'+esc(body)+'</p><p class="muted">Sorted uses the dates and updates in your cases. You confirm what happened.</p></details>';
}
function home169Waiting(list){
  var dated=list.map(function(t){var p=openPromise(t),w=p&&window_(p);return {t:t,p:p,w:w}}).filter(function(x){return x.w&&!calcOpen(x.p)&&Number.isFinite(+x.w.start)});
  dated.sort(function(a,b){return a.w.start-b.w.start||String(a.t.id).localeCompare(String(b.t.id))});
  if(!dated.length)return '';
  var x=dated[0],title=case75TitleParts(x.t).title;
  return '<section class="context169-next" aria-labelledby="context169-heading"><h2 id="context169-heading" class="context169-label">Next tracked date</h2><button class="context169-open" data-a="open" data-id="'+esc(x.t.id)+'"><span class="context169-title">'+esc(title)+'</span><span class="context169-date">'+esc(whenText(x.p))+'</span><span class="context169-party">Waiting for '+esc(whoSay(x.p.party)||'them')+'</span><span class="context169-review">Review this case <span aria-hidden="true">›</span></span></button><p class="muted context169-note">Based on the promise saved in this case. Add an update if things change.</p></section>';
}
`;
R('function home44Spot(t){',UI+'function home44Spot(t){');
R("  return h+'</section>';\n}\nfunction home54Title(t){","  return h+'</section>'+home169Reason(t);\n}\nfunction home54Title(t){");
R('    h+=home44Section("Waiting",waiting,"waiting",','    h+=home169Waiting(waiting);\n    h+=home44Section("Waiting",waiting,"waiting",');
R('</head>',String.raw`<style>
/* v169: quiet context, readable on a phone and with the existing dark theme. */
.context169-why{border-top:1px solid var(--rule);margin-top:14px;padding-top:4px;font-size:15px}
.context169-why summary{cursor:pointer;min-height:44px;display:list-item;align-content:center;font-weight:600;margin-left:18px;padding:10px 0}
.context169-why summary:focus-visible{outline:3px solid var(--violet);outline-offset:3px;border-radius:4px}
.context169-why p{margin:6px 0 10px;line-height:1.5;overflow-wrap:anywhere}
.context169-next{display:block;padding:18px;border:1px solid var(--rule);border-left:4px solid var(--violet);border-radius:14px;background:var(--sheet);margin:16px 0}
.context169-open{display:grid;gap:6px;width:100%;text-align:left;font:inherit;color:var(--ink);background:transparent;border:0;padding:0;cursor:pointer}.context169-open:focus-visible{outline:3px solid var(--violet);outline-offset:4px;border-radius:4px}.context169-party{font-size:14px;color:var(--ink-2)}.context169-review{font-weight:600;color:var(--ink);min-height:44px;display:flex;align-items:center;justify-content:space-between}
.context169-label{font-size:13px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;margin:0 0 8px;color:var(--ink-2)}
.context169-title{font-size:19px;font-weight:700;margin:0 0 4px;overflow-wrap:anywhere}
.context169-date{margin:0;line-height:1.5;overflow-wrap:anywhere}
.context169-note{font-size:14px;line-height:1.5;margin:8px 0 0}
.context169-next .btn{min-height:44px;flex-shrink:0}
@media(max-width:520px){.context169-next{align-items:stretch;flex-direction:column;gap:12px}.context169-next .btn{width:100%}}
</style>
</head>`);
R('SORTED_V="v168"','SORTED_V="v169"');
fs.writeFileSync('public/index.html',s);
const EXPECT='2ee50b8849f50ae23e99f8bcc00db86d1e7001b6';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v169 ok',h(s),s.length);
