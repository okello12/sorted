const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='846b76b0684aa708e0d545b4925f933843eb3c1f')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+String(a).slice(0,80));s=s.split(a).join(b)}
// v84: universal email intake. Signed-in users can forward an email to their private Sorted intake address,
// then explicitly choose which existing/new case it belongs to. Nothing joins a case until that choice.
R('</style>\n\n</head>',String.raw`/* v84 forwarded inbox */
.fw-inbox{border:1px solid color-mix(in srgb,var(--aqua) 34%,var(--rule));background:linear-gradient(135deg,color-mix(in srgb,var(--asoft) 62%,var(--sheet)),var(--sheet));border-radius:18px;padding:15px;display:flex;flex-direction:column;gap:10px}.fw-inbox h3,.fw-inbox p{margin:0}.fw-inbox-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;border-top:1px solid var(--rule);padding-top:10px}.fw-inbox-copy{min-width:0}.fw-inbox-copy strong,.fw-inbox-copy span{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.fw-inbox-copy span{font-size:14px;color:var(--ink-2)}.fw-forward{border:1px dashed color-mix(in srgb,var(--violet) 35%,var(--rule));border-radius:14px;padding:11px 12px;margin-top:9px;background:color-mix(in srgb,var(--sheet) 94%,var(--vsoft))}.fw-address{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px;overflow-wrap:anywhere}.fw-forward .row{margin-top:8px}@media(max-width:520px){.fw-inbox-row{grid-template-columns:1fr}.fw-inbox-row .btn{width:100%}}
</style>

</head>`);
R('boot();\n})();',String.raw`/* v84 forwarded email inbox */
function fwLoadUniversal(force){if(!S.user||!S.user.email)return;if(!force&&S.fwInboxAt&&Date.now()-S.fwInboxAt<60000)return;S.fwInboxAt=Date.now();
  try{sb.from('inbound_items').select('id,subject,body,received_at,from_domain').is('task_id',null).is('used_at',null).then(function(r){S.fwInbox=r&&!r.error&&Array.isArray(r.data)?r.data:[];if(S.view.name==='home')render()},function(){})}catch(e){}
  if(S.fwAddress===undefined)try{sb.rpc('my_inbound_address',{}).then(function(r){S.fwAddress=r&&!r.error&&r.data?String(r.data):'';if(S.view.name==='home')render()},function(){S.fwAddress=''})}catch(e){S.fwAddress=''}
}
function fwForwardBox(){if(!S.user||!S.user.email)return '';fwLoadUniversal();var a=S.fwAddress||'';if(!a)return '';return '<div class="fw-forward"><p class="fw-sub"><strong>Forward an email into Sorted</strong></p><p class="fw-sub">Forward from the email address you use for Sorted. It waits in your private inbox until you choose a case.</p><div class="fw-address">'+esc(a)+'</div><div class="row"><button type="button" class="btn" data-fw="copy-address" data-v="'+esc(a)+'">Copy address</button></div></div>'}
function fwInboxHTML(){var l=S.fwInbox||[];if(!l.length)return '';var h='<section class="fw-inbox"><p class="eyebrow">Came in</p><h3 class="h3">Forwarded to Sorted</h3><p class="fw-sub">Choose where each email belongs. Nothing is added to a case until you do.</p>';l.slice(0,5).forEach(function(x){var sub=x.subject||'Forwarded email';h+='<div class="fw-inbox-row"><div class="fw-inbox-copy"><strong>'+esc(sub)+'</strong><span>'+esc((x.from_domain?x.from_domain+' · ':'')+stampLabel(x.received_at))+'</span></div><div class="row"><button type="button" class="btn" data-fw="inbox-sort" data-id="'+esc(x.id)+'">Sort this</button><button type="button" class="link" data-fw="inbox-drop" data-id="'+esc(x.id)+'">Remove</button></div></div>'});if(l.length>5)h+='<p class="fw-sub">And '+(l.length-5)+' more.</p>';return h+'</section>'}
function fwUniversalEnhance(){if(S.view.name!=='home')return;fwLoadUniversal();var hint=document.querySelector('.fw-intake-hint');if(hint&&!document.querySelector('.fw-forward'))hint.insertAdjacentHTML('afterend',fwForwardBox());if(!document.querySelector('.fw-inbox')){var html=fwInboxHTML();if(html){var main=document.querySelector('main'),money=document.querySelector('.fw-money-home'),came=document.querySelector('.found-strip');if(money)money.insertAdjacentHTML('beforebegin',html);else if(came)came.insertAdjacentHTML('beforebegin',html);else if(main)main.insertAdjacentHTML('afterbegin',html)}}}
var fwEnhancePrev=fwEnhance;fwEnhance=function(){fwEnhancePrev();fwUniversalEnhance()};
var fwIntakeAdd=intakeAdd;intakeAdd=function(d){var id=d&&d.fwInboundId;fwIntakeAdd(d);if(id){try{sb.from('inbound_items').update({used_at:nowIso()}).eq('id',id).then(function(){},function(){})}catch(e){}S.fwInbox=(S.fwInbox||[]).filter(function(x){return x.id!==id})}};
document.addEventListener('click',function(e){var b=e.target.closest('[data-fw]');if(!b)return;var a=b.getAttribute('data-fw');
  if(a==='copy-address'){var v=b.getAttribute('data-v')||'';copy(v).then(function(){toast('Forwarding address copied')});return}
  if(a==='inbox-drop'){var id=b.getAttribute('data-id');try{sb.from('inbound_items').delete().eq('id',id).then(function(){},function(){})}catch(x){}S.fwInbox=(S.fwInbox||[]).filter(function(x){return x.id!==id});render();toast('Removed');return}
  if(a==='inbox-sort'){var id2=b.getAttribute('data-id'),x=(S.fwInbox||[]).filter(function(q){return q.id===id2})[0];if(!x)return;var tx=(x.subject?x.subject+'. ':'')+(x.body||'');S.composeOpen=true;S.draft={fromShare:true,casetext:tx,src:'an email reply',fwInboundId:id2};render();window.scrollTo(0,0);return}
},true);
boot();
})();`);
fs.writeFileSync('public/index.html',s);
const EXPECT='0000000000000000000000000000000000000000';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v84 ok',h(s),s.length);
