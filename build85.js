const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='761c9c32b4cab1201ee28d1c57a6968a5ed02a32')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,80));s=s.split(a).join(b)}
// v85: public landing hierarchy. The chooser becomes the product, not a feature list under a full-screen hero.
R('</style>\n\n</head>',String.raw`/* v85 landing hierarchy + miniature 3D object world */
.cap85-public .hero{padding:20px 20px 16px;border-radius:24px;gap:12px;margin-bottom:12px;min-height:0}
.cap85-public .hero .eyebrow{font-size:12px;line-height:1.25;letter-spacing:.13em;margin-bottom:2px}
.cap85-public .hero .h1{font-size:clamp(34px,9.8vw,46px);line-height:.98;max-width:12.5ch;hyphens:none!important;-webkit-hyphens:none!important;word-break:normal!important;overflow-wrap:normal!important}
.cap85-public .hero .h1 *{hyphens:none!important;-webkit-hyphens:none!important;word-break:normal!important;overflow-wrap:normal!important}
.cap85-public .hero .lede{font-size:17px;line-height:1.43;max-width:34em;margin-top:2px}
.cap85-public .hero .cap85-top-cta{display:none!important}
.cap85-public .hero .hero-art{display:block;width:min(70%,270px);height:auto;max-width:270px;margin:3px auto -2px;filter:drop-shadow(0 14px 22px rgba(28,42,110,.2))}
.cap85-public #cap82-landing{margin-top:12px;margin-bottom:24px}
.cap85-public #cap82-landing.cap82{padding:16px;gap:12px;border-radius:22px}
.cap85-public #cap82-landing .cap82-title{font-size:clamp(28px,7.6vw,34px);line-height:1.02}
.cap85-public #cap82-landing .cap82-copy{font-size:15px;line-height:1.4}
.cap85-public #cap82-landing .cap82-card{box-shadow:0 10px 26px rgba(17,22,56,.12)}
.cap85-public #cap82-landing .cap82-art{height:82px;background:radial-gradient(circle at 50% 28%,rgba(255,255,255,.16),transparent 45%),linear-gradient(145deg,color-mix(in srgb,var(--cap) 18%,var(--sheet)),color-mix(in srgb,var(--cap-soft) 84%,var(--sheet)))}
.cap85-scene{overflow:visible!important;isolation:isolate}.cap85-scene:before{left:16%!important;right:16%!important;bottom:7px!important;height:9px!important;filter:blur(8px)!important;opacity:.9!important}
.cap85-scene svg{width:92px!important;height:76px!important;overflow:visible;filter:drop-shadow(0 9px 8px rgba(0,0,0,.22))!important;transform:none!important}
.cap85-pilot-note{margin:16px 0 0!important;padding:13px 15px!important;border:1px solid color-mix(in srgb,var(--violet) 18%,var(--rule))!important;border-radius:16px!important;background:color-mix(in srgb,var(--sheet) 96%,var(--vsoft))!important;color:var(--ink-2)!important;font-size:14px!important;line-height:1.45!important}
.cap85-public section[aria-labelledby="ex-h"]{margin-top:22px}
.cap85-public section[aria-labelledby="ex-h"] .group-h{margin-bottom:10px}.cap85-public section[aria-labelledby="ex-h"] .h3{font-size:22px}
.cap85-ex-rail{display:flex;gap:12px;overflow-x:auto;scroll-snap-type:x proximity;scrollbar-width:none;padding:1px 2px 9px;-webkit-overflow-scrolling:touch}.cap85-ex-rail::-webkit-scrollbar{display:none}
.cap85-ex-rail .slip{flex:0 0 min(84%,330px);scroll-snap-align:start;margin:0!important;border-radius:18px}.cap85-ex-rail .slip-body{font-size:15px;line-height:1.42;padding-top:2px}.cap85-ex-rail .slip-stub{font-size:14px}
@media(max-width:520px){.cap85-public .hero{padding:17px 16px 14px}.cap85-public .hero .h1{font-size:clamp(34px,10.2vw,43px);max-width:11.7ch}.cap85-public .hero .lede{font-size:16px}.cap85-public .hero .hero-art{width:220px;max-width:62%;margin-top:0}.cap85-public #cap82-landing{margin-top:10px}.cap85-public #cap82-landing .cap82-card{min-height:154px}.cap85-public #cap82-landing .cap82-art{height:80px}.cap85-public #cap82-landing .cap82-label strong{font-size:15px}.cap85-public #cap82-landing .cap82-label small{font-size:12.5px;line-height:1.3}.cap85-ex-rail .slip{flex-basis:86%}}
</style>

</head>`);
R('</body>',String.raw`<script>
(function(){
  function gid(id,n){return 'c85-'+id+'-'+n}
  function defs(id){return '<defs>'+['cream','blue','coral','teal','gold'].map(function(n){var a=n==='cream'?['#fffaf0','#e6d5b7']:n==='blue'?['#58b9ff','#18358f']:n==='coral'?['#ffad74','#d93f66']:n==='teal'?['#65e3d1','#188f8f']:['#ffd76a','#e08b20'];return '<linearGradient id="'+gid(id,n)+'" x1="0" y1="0" x2="1" y2="1"><stop stop-color="'+a[0]+'"/><stop offset="1" stop-color="'+a[1]+'"/></linearGradient>'}).join('')+'</defs>'}
  function U(id,n){return 'url(#'+gid(id,n)+')'}
  function scene(id){var a='<svg viewBox="0 0 120 86" aria-hidden="true" focusable="false">'+defs(id),z='</svg>';
    if(id==='fix')return a+'<ellipse cx="58" cy="76" rx="39" ry="6" fill="#2ebfe2" opacity=".38"/><path d="M28 16h49l9 7v42l-9 8H28z" fill="'+U(id,'blue')+'"/><rect x="17" y="12" width="60" height="59" rx="10" fill="'+U(id,'cream')+'"/><rect x="24" y="18" width="46" height="9" rx="4" fill="#d9e5ed"/><circle cx="48" cy="48" r="17" fill="#203e89"/><circle cx="48" cy="48" r="12" fill="#9ee4ff"/><path d="M39 47c6-8 11 8 20-1" stroke="#ff7b5f" stroke-width="5" stroke-linecap="round" fill="none"/><path d="M88 58c6 7 8 10 8 14a8 8 0 1 1-16 0c0-4 2-7 8-14z" fill="'+U(id,'teal')+'"/><path d="M92 24l12 12-8 8-6-6-7 7" stroke="#f1ca82" stroke-width="4" fill="none" stroke-linecap="round"/>'+z;
    if(id==='call')return a+'<ellipse cx="60" cy="76" rx="38" ry="6" fill="#5b4cbd" opacity=".3"/><g transform="rotate(-6 37 45)"><rect x="13" y="27" width="46" height="38" rx="7" fill="'+U(id,'cream')+'"/><path d="M21 39h28M21 47h23M21 55h19" stroke="#64748b" stroke-width="3" stroke-linecap="round"/></g><path d="M67 14h28l7 7v47l-8 7H67z" fill="#19367e"/><rect x="59" y="10" width="37" height="61" rx="9" fill="'+U(id,'blue')+'"/><rect x="64" y="18" width="27" height="39" rx="5" fill="#f2f7ff" opacity=".92"/><path d="M88 22h20a7 7 0 0 1 7 7v12a7 7 0 0 1-7 7h-7l-9 8v-8h-4z" fill="'+U(id,'coral')+'"/><path d="M97 31h10M97 37h7" stroke="#fff" stroke-width="3" stroke-linecap="round"/>'+z;
    if(id==='promise')return a+'<ellipse cx="59" cy="76" rx="39" ry="6" fill="#c67b2d" opacity=".3"/><rect x="15" y="12" width="61" height="56" rx="9" fill="'+U(id,'cream')+'"/><path d="M15 29h61" stroke="#dc8d45" stroke-width="5"/><path d="M29 8v13M61 8v13" stroke="#3853a6" stroke-width="5" stroke-linecap="round"/><rect x="25" y="38" width="13" height="10" rx="3" fill="#79b5ff"/><rect x="45" y="38" width="13" height="10" rx="3" fill="'+U(id,'coral')+'"/><circle cx="80" cy="50" r="19" fill="'+U(id,'gold')+'"/><path d="M80 38v13l9 6" stroke="#49386f" stroke-width="4" stroke-linecap="round" fill="none"/><path d="M94 18l12 5-12 5z" fill="#ff6f63"/>'+z;
    if(id==='chase')return a+'<ellipse cx="59" cy="76" rx="39" ry="6" fill="#c6476d" opacity=".28"/><path d="M13 16h59a8 8 0 0 1 8 8v28a8 8 0 0 1-8 8H45L31 71V60H13a8 8 0 0 1-8-8V24a8 8 0 0 1 8-8z" fill="'+U(id,'cream')+'"/><path d="M20 31h38M20 40h30" stroke="#6f6d80" stroke-width="4" stroke-linecap="round"/><circle cx="84" cy="24" r="18" fill="'+U(id,'coral')+'"/><path d="M84 13v12l8 5" stroke="#fff5ef" stroke-width="4" stroke-linecap="round" fill="none"/><path d="M74 60h28l-7-7M102 60l-7 7" stroke="#ff7f75" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'+z;
    if(id==='document')return a+'<ellipse cx="58" cy="76" rx="39" ry="6" fill="#279c91" opacity=".3"/><path d="M13 27l28-15 31 15v42H13z" fill="#176f79"/><path d="M20 9h47l11 11v45H20z" fill="'+U(id,'cream')+'"/><path d="M67 9v13h11" fill="#e7d8bb"/><path d="M31 32h32M31 41h28M31 50h20" stroke="#617581" stroke-width="3.5" stroke-linecap="round"/><path d="M13 27l28 24 31-24v42H13z" fill="'+U(id,'teal')+'" opacity=".92"/><circle cx="86" cy="54" r="14" fill="#e7fff9" stroke="#35a99d" stroke-width="4"/><path d="M96 64l12 11" stroke="#35a99d" stroke-width="6" stroke-linecap="round"/>'+z;
    return a+'<ellipse cx="58" cy="76" rx="39" ry="6" fill="#bd802a" opacity=".3"/><rect x="13" y="10" width="45" height="60" rx="8" fill="'+U(id,'gold')+'"/><circle cx="35" cy="32" r="10" fill="#fff4c8"/><path d="M24 51h22M24 57h16" stroke="#6b4b2e" stroke-width="3.5" stroke-linecap="round"/><g transform="rotate(5 76 46)"><rect x="52" y="24" width="46" height="42" rx="7" fill="'+U(id,'cream')+'"/><path d="M61 35h26M61 43h18" stroke="#69748a" stroke-width="3.5" stroke-linecap="round"/></g><circle cx="89" cy="54" r="15" fill="'+U(id,'gold')+'"/><path d="M82 54l5 5 10-13" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'+z;
  }
  function pilotIn(hero){var xs=Array.prototype.slice.call(hero.querySelectorAll('.note,p,div,section'));return xs.filter(function(x){return /research pilot/i.test(x.textContent||'')}).sort(function(a,b){return (a.textContent||'').length-(b.textContent||'').length})[0]||null}
  function enhance(){
    if(document.documentElement.classList.contains('cap85-ready'))return;
    var landing=document.querySelector('#cap82-landing'),hero=document.querySelector('.hero');if(!landing||!hero||document.querySelector('main.home44'))return;
    document.documentElement.classList.add('cap85-public');hero.classList.add('cap85-hero');
    var h1=hero.querySelector('.h1');if(h1)h1.classList.add('cap85-headline');
    var top=hero.querySelector('a.btn.primary,button.btn.primary');if(top)top.classList.add('cap85-top-cta');
    if(hero.nextElementSibling!==landing)hero.insertAdjacentElement('afterend',landing);
    landing.querySelectorAll('.cap82-card').forEach(function(card){var art=card.querySelector('.cap82-art'),id=card.getAttribute('data-cap82');if(!art||!id)return;art.innerHTML=scene(id);art.classList.remove('cap84-scene');art.classList.add('cap85-scene');art.setAttribute('data-cap85','1')});
    var ex=document.querySelector('section[aria-labelledby="ex-h"]');if(ex){var eh=ex.querySelector('#ex-h');if(eh&&eh.textContent!=='See how Sorted handles it')eh.textContent='See how Sorted handles it';var slips=Array.prototype.slice.call(ex.querySelectorAll(':scope > .slip'));if(!ex.querySelector('.cap85-ex-rail')&&slips.length){var rail=document.createElement('div');rail.className='cap85-ex-rail';slips.forEach(function(x,i){if(i<3)rail.appendChild(x);else x.remove()});ex.appendChild(rail)}var bodies=ex.querySelectorAll('.slip-body'),copy=['Try a few safe checks. If it is still broken, Sorted keeps the next step in one place.','The promised date has passed. Sorted brings it back so you can chase with the reference.','When they give you a date, Sorted waits with you until it is due.'];bodies.forEach(function(x,i){if(copy[i]&&x.textContent!==copy[i])x.textContent=copy[i]})}
    var pn=pilotIn(hero);if(pn&&ex&&!pn.classList.contains('cap85-pilot-note')){pn.classList.add('cap85-pilot-note');ex.insertAdjacentElement('afterend',pn)}
    document.documentElement.classList.add('cap85-ready');
  }
  function schedule(){enhance();setTimeout(enhance,40);setTimeout(enhance,180)}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',schedule,{once:true});else schedule();window.addEventListener('load',enhance,{once:true});window.addEventListener('hashchange',function(){document.documentElement.classList.remove('cap85-ready');setTimeout(enhance,20)});
})();
</script>
</body>`);
fs.writeFileSync('public/index.html',s);
const EXPECT='694f1f5948155df085eeab3e076dac8a99aae679';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v85 ok',h(s),s.length);
