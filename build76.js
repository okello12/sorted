const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='8c72bc97ccfe09fdc30c4f25f2751c735623a1b2')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// v76: polish v75's consolidation: one group helper, a real summary panel, and one visual treatment for secondary rows.
R(`function case75Group(title,note,body,cls){
  if(!body)return "";return '<details class="case75-group '+(cls||"")+'"><summary><span class="case75-group-copy"><strong>'+esc(title)+'</strong><small>'+esc(note)+'</small></span></summary><div class="case75-group-body stack">'+body+'</div></details>';
}
function case75Secondary(t,s){`,
`function case75Secondary(t,s){`);
R(`  if(t.mode==="fix"&&t.fix.step==="done"&&s!=="done")tools+='<section class="stack-s"><button class="link" data-a="summary" style="align-self:flex-start">'+(S.view.panel==="summary"?"Hide the summary":"Copy a summary for whoever fixes it")+'</button>'+(S.view.panel==="summary"?'<textarea class="copybox" id="sumtext" readonly>'+esc(repairerSummary(t))+'</textarea><button class="btn primary block" data-a="copy-summary">Copy summary</button>':"")+'</section>';`,
`  if(t.mode==="fix"&&t.fix.step==="done"&&s!=="done")tools+='<section class="stack-s"><button class="link" data-a="summary">Copy a summary for whoever fixes it</button></section>';`);
R(`  else if(S.view.panel==="pack"){h+=packView(t)}
  else if(S.view.panel==="evmove"){h+=mvPanel(t)}`,
`  else if(S.view.panel==="pack"){h+=packView(t)}
  else if(S.view.panel==="summary"){h+='<section class="sheet stack" aria-labelledby="sumh"><div class="stack-s"><p class="eyebrow">Repair summary</p><h2 class="h2" id="sumh">For whoever fixes it</h2></div><textarea class="copybox" id="sumtext" readonly>'+esc(repairerSummary(t))+'</textarea><button class="btn primary block" data-a="copy-summary">Copy summary</button><button class="btn block" data-a="panel" data-p="">Close</button></section>'}
  else if(S.view.panel==="evmove"){h+=mvPanel(t)}`);
R('.case75-parking-pending p{margin:0}', `.case75-parking-pending p{margin:0}
.case75-group .link{display:flex;width:100%;min-height:46px;align-items:center;text-align:left;text-decoration:none;padding:10px 2px;border-bottom:1px solid var(--rule)}
.case75-group .case56-fold{border:0;border-bottom:1px solid var(--rule);border-radius:0}
.case75-group .case56-fold>summary{min-height:46px;padding:10px 2px}
.case75-group .note p a.link{display:inline;width:auto;min-height:0;padding:0;border:0;text-decoration:underline}`);
fs.writeFileSync('public/index.html',s);
const EXPECT='';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v76 ok',h(s),s.length);
