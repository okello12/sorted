const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='30189ca2f049dc4b2a509fbbb19f1386d5f310c4')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,80));s=s.split(a).join(b)}
// v82: one permanent start surface. Visual real-life choices teach the product; existing cases remain directly below.
R('</style>\n\n</head>',String.raw`/* v82 unified visual start surface */
.cap82{display:flex;flex-direction:column;gap:14px;padding:19px;border:1px solid color-mix(in srgb,var(--violet) 16%,var(--rule));border-radius:24px;background:radial-gradient(circle at 95% 0%,color-mix(in srgb,var(--aqua) 12%,transparent),transparent 30%),linear-gradient(145deg,color-mix(in srgb,var(--sheet) 96%,var(--vsoft)),color-mix(in srgb,var(--sheet) 94%,var(--asoft)));box-shadow:0 16px 42px rgba(35,28,82,.08)}
.cap82-head{display:flex;flex-direction:column;gap:5px}.cap82-eyebrow{margin:0;font-size:12px;font-weight:850;letter-spacing:.13em;text-transform:uppercase;color:var(--violet)}.cap82-title{margin:0;font-size:clamp(25px,6.5vw,34px);line-height:1.04;letter-spacing:-.03em}.cap82-copy{margin:0;color:var(--ink-2);font-size:15px;max-width:42em}
.cap82-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.cap82-card{--cap:var(--violet);--cap-soft:var(--vsoft);position:relative;display:grid;grid-template-columns:76px minmax(0,1fr);align-items:center;gap:11px;width:100%;min-height:112px;padding:12px;text-align:left;color:var(--ink);background:linear-gradient(145deg,color-mix(in srgb,var(--sheet) 90%,var(--cap-soft)),var(--sheet));border:1px solid color-mix(in srgb,var(--cap) 25%,var(--rule));border-radius:18px;cursor:pointer;box-shadow:0 8px 22px rgba(31,27,65,.045);transition:transform .16s ease,border-color .16s ease,box-shadow .16s ease}.cap82-card:hover{transform:translateY(-2px);border-color:color-mix(in srgb,var(--cap) 55%,var(--rule));box-shadow:0 13px 28px rgba(31,27,65,.09)}.cap82-card:active{transform:scale(.99)}
.cap82-fix{--cap:var(--aqua);--cap-soft:var(--asoft)}.cap82-call{--cap:var(--violet);--cap-soft:var(--vsoft)}.cap82-promise{--cap:var(--warm);--cap-soft:var(--wsoft)}.cap82-chase{--cap:var(--coral);--cap-soft:var(--csoft)}.cap82-document{--cap:#2B8A78;--cap-soft:var(--gsoft)}.cap82-renew{--cap:var(--amber);--cap-soft:var(--amsoft)}
.cap82-art{display:grid;place-items:center;width:76px;height:76px;border-radius:18px;background:linear-gradient(145deg,color-mix(in srgb,var(--cap) 16%,var(--sheet)),color-mix(in srgb,var(--cap-soft) 80%,var(--sheet)));box-shadow:inset 0 1px 0 rgba(255,255,255,.28)}.cap82-art svg{width:62px;height:62px;color:var(--cap);overflow:visible}.cap82-label{display:flex;flex-direction:column;gap:3px;min-width:0}.cap82-label strong{font-size:17px;line-height:1.08;letter-spacing:-.015em}.cap82-label small{font-size:13px;line-height:1.25;color:var(--ink-2)}
.cap82-other{display:flex;align-items:center;justify-content:space-between;gap:12px;width:100%;min-height:48px;padding:10px 12px;border:1.5px dashed color-mix(in srgb,var(--violet) 30%,var(--rule));border-radius:14px;background:color-mix(in srgb,var(--sheet) 96%,var(--vsoft));color:var(--ink);font:700 15px/1.2 inherit;text-align:left;cursor:pointer}.cap82-other span:last-child{color:var(--violet);font-size:20px}
.cap82.cap82-with-cases{padding:16px;gap:12px}.cap82-with-cases .cap82-title{font-size:25px}.cap82-with-cases .cap82-copy{font-size:14px}.cap82-with-cases .cap82-card{grid-template-columns:54px minmax(0,1fr);min-height:82px;padding:9px}.cap82-with-cases .cap82-art{width:54px;height:54px;border-radius:14px}.cap82-with-cases .cap82-art svg{width:46px;height:46px}.cap82-with-cases .cap82-label strong{font-size:15px}.cap82-with-cases .cap82-label small{display:none}
#cap82-landing{margin-top:22px;margin-bottom:8px}.cap82-home-marker{margin:2px 0 -2px;font-size:13px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-2)}
:root[data-theme="dark"] .cap82{box-shadow:0 18px 44px rgba(0,0,0,.22)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .cap82{box-shadow:0 18px 44px rgba(0,0,0,.22)}}
@media (max-width:520px){.cap82{padding:15px;border-radius:20px}.cap82-grid{gap:8px}.cap82-card{grid-template-columns:1fr;align-content:start;gap:7px;min-height:142px;padding:10px}.cap82-art{width:100%;height:70px}.cap82-art svg{width:58px;height:58px}.cap82-label strong{font-size:15px}.cap82-label small{font-size:12.5px}.cap82-with-cases .cap82-card{grid-template-columns:1fr;min-height:100px}.cap82-with-cases .cap82-art{width:100%;height:52px}.cap82-with-cases .cap82-label strong{font-size:14px}.cap82-with-cases .cap82-copy{display:none}}
@media (prefers-reduced-motion:reduce){.cap82-card{transition:none!important}}
</style>

</head>`);
R('</body>',String.raw`<script>
(function(){
  var items=[
    {id:'fix',title:"Something's broken",desc:'Appliance, heating, home repair or something that stopped working.',ph:'Tell Sorted what is broken and what has happened so far…'},
    {id:'call',title:'I need to make a call',desc:'Know what to say, what to ask and what to write down.',ph:'Who do you need to call, and what do you need to sort out?…'},
    {id:'promise',title:'They promised me something',desc:'A refund, callback, repair, delivery, appointment or anything with a date.',ph:'What did they promise, who promised it, and by when?…'},
    {id:'chase',title:'I need to chase something',desc:'They have not replied, turned up, paid or done what they said.',ph:'What are you waiting for, and when did you last hear from them?…'},
    {id:'document',title:'I have a letter or document',desc:'Understand what it says and work out what needs doing.',ph:'Tell Sorted what the letter, email or document is about…'},
    {id:'renew',title:'I need to renew or sort admin',desc:'Renewals, expiries, forms and important dates.',ph:'What needs renewing or sorting, and is there a deadline?…'}
  ];
  function svg(id){
    var a='<svg viewBox="0 0 72 72" role="img" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">',z='</svg>';
    if(id==='fix')return a+'<rect x="12" y="15" width="46" height="44" rx="8"/><path d="M18 21h34"/><circle cx="35" cy="40" r="12"/><path d="M52 49c5 5 7 8 7 11a6 6 0 0 1-12 0c0-3 2-6 5-11z" fill="currentColor" opacity=".14"/>'+z;
    if(id==='call')return a+'<rect x="17" y="9" width="29" height="51" rx="7"/><path d="M27 53h9"/><path d="M49 18h11a5 5 0 0 1 5 5v13a5 5 0 0 1-5 5h-5l-6 6v-6h-3"/><path d="M53 26h7M53 32h5"/>'+z;
    if(id==='promise')return a+'<rect x="10" y="13" width="39" height="38" rx="7"/><path d="M18 9v9M40 9v9M10 24h39"/><circle cx="51" cy="47" r="14" fill="currentColor" opacity=".12"/><circle cx="51" cy="47" r="14"/><path d="M51 39v9l6 4"/>'+z;
    if(id==='chase')return a+'<path d="M12 17h39a7 7 0 0 1 7 7v18a7 7 0 0 1-7 7H30l-11 10V49h-7a7 7 0 0 1-7-7V24a7 7 0 0 1 7-7z"/><path d="M17 29h27M17 36h19"/><path d="M47 8l10 5-10 5"/>'+z;
    if(id==='document')return a+'<path d="M19 8h26l10 10v44H19z"/><path d="M45 8v11h10M27 31h20M27 39h20M27 47h13"/><path d="M8 24l11 8-11 8z" fill="currentColor" opacity=".12"/>'+z;
    return a+'<rect x="12" y="12" width="33" height="48" rx="6"/><circle cx="28.5" cy="32" r="8"/><path d="M20 47h17"/><rect x="40" y="34" width="23" height="23" rx="5" fill="currentColor" opacity=".11"/><path d="M45 45l5 5 9-11"/>'+z;
  }
  function card(x){return '<button type="button" class="cap82-card cap82-'+x.id+'" data-cap82="'+x.id+'" aria-label="'+x.title+'"><span class="cap82-art">'+svg(x.id)+'</span><span class="cap82-label"><strong>'+x.title+'</strong><small>'+x.desc+'</small></span></button>'}
  function panel(id,home){return '<section class="cap82" id="'+id+'" aria-labelledby="'+id+'-title"><div class="cap82-head"><p class="cap82-eyebrow">Start here</p><h2 class="cap82-title" id="'+id+'-title">What do you need to get sorted?</h2><p class="cap82-copy">Choose what is happening. Sorted will help you work out what to do next.</p></div><div class="cap82-grid">'+items.map(card).join('')+'</div><button type="button" class="cap82-other" data-cap82="other"><span><strong>Something else?</strong> Tell Sorted what happened.</span><span aria-hidden="true">→</span></button>'+(home?'<p class="cap82-home-marker">Your cases are below</p>':'')+'</section>'}
  function selected(){try{return sessionStorage.getItem('sorted.cap82')||''}catch(e){return ''}}
  function item(id){for(var i=0;i<items.length;i++)if(items[i].id===id)return items[i];return {id:'other',title:'Something else',ph:'Tell Sorted what happened…'}}
  function focusSelected(){var f=document.querySelector('#f-case');if(!f)return false;var x=item(selected());f.setAttribute('placeholder',x.ph);f.focus({preventScroll:true});f.scrollIntoView({behavior:'smooth',block:'center'});return true}
  function choose(id){try{sessionStorage.setItem('sorted.cap82',id)}catch(e){}if(focusSelected())return;var b=document.querySelector('[data-a="compose"]');if(b){b.click();setTimeout(function(){enhance();focusSelected()},80);return}if(location.hash!=='#start')location.hash='start';setTimeout(function(){enhance();focusSelected()},120)}
  function hasCases(home){return !!home.querySelector('.home44-spot,.home44-row,.home44-done,.found-strip')}
  function enhance(){
    var home=document.querySelector('main.home44');
    if(home){var p=home.querySelector('#cap82-start');if(!p){home.insertAdjacentHTML('afterbegin',panel('cap82-start',true));p=home.querySelector('#cap82-start')}if(p)p.classList.toggle('cap82-with-cases',hasCases(home));focusSelected();return}
    var hero=document.querySelector('.hero');
    if(hero&&!document.querySelector('#cap82-landing'))hero.insertAdjacentHTML('afterend',panel('cap82-landing',false));
  }
  document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('[data-cap82]');if(!b)return;e.preventDefault();choose(b.getAttribute('data-cap82'))},true);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',enhance);else enhance();
  new MutationObserver(function(){enhance()}).observe(document.documentElement,{childList:true,subtree:true});
  window.addEventListener('hashchange',function(){setTimeout(enhance,30)});
})();
</script>
</body>`);
fs.writeFileSync('public/index.html',s);
const EXPECT='4f945c7f0acb2ea74e90eb2f236d5f2872d28db2';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v82 ok',h(s),s.length);
