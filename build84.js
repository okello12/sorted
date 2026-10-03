const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='801ac97609b9c4150a0f3ec1360dad8676843849')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,80));s=s.split(a).join(b)}
// v84: real-device landing polish. Richer scenes for discovery; returning users get a compact carousel and their cases sooner.
R('</style>\n\n</head>',String.raw`/* v84 visual start polish */
.cap82-home-marker{display:none!important}
/* Returning users keep discovery without making their live cases wait below a full-screen menu. */
.cap82-with-cases{padding:0 0 4px;border:0;border-radius:0;background:none;box-shadow:none;gap:9px}
.cap82-with-cases .cap82-head{padding:0 2px}.cap82-with-cases .cap82-eyebrow,.cap82-with-cases .cap82-copy{display:none}.cap82-with-cases .cap82-title{font-size:23px;line-height:1.08}
.cap82-with-cases .cap82-grid{display:flex;grid-template-columns:none;gap:10px;overflow-x:auto;overflow-y:hidden;scroll-snap-type:x proximity;scrollbar-width:none;padding:2px 2px 8px;-webkit-overflow-scrolling:touch}
.cap82-with-cases .cap82-grid::-webkit-scrollbar{display:none}.cap82-with-cases .cap82-card{flex:0 0 clamp(138px,40vw,172px);grid-template-columns:1fr;align-content:start;gap:7px;min-height:126px;padding:8px 8px 10px;scroll-snap-align:start;border-radius:17px}
.cap82-with-cases .cap82-art{width:100%;height:72px;border-radius:15px}.cap82-with-cases .cap82-art svg{width:66px;height:66px}.cap82-with-cases .cap82-label strong{font-size:14px;line-height:1.1}.cap82-with-cases .cap82-label small{display:none}.cap82-with-cases .cap82-other{min-height:42px;padding:8px 10px;font-size:14px}
/* Scene illustrations: familiar objects before software categories. */
.cap84-scene{position:relative;overflow:hidden;isolation:isolate}.cap84-scene:before{content:"";position:absolute;left:12%;right:12%;bottom:8px;height:10px;border-radius:50%;background:color-mix(in srgb,var(--cap) 22%,transparent);filter:blur(7px);opacity:.7;z-index:-1}.cap84-scene svg{filter:drop-shadow(0 7px 8px rgba(0,0,0,.16));transform:translateY(-1px)}
.cap84-scene .s84-back{fill:color-mix(in srgb,var(--cap) 20%,var(--sheet));stroke:color-mix(in srgb,var(--cap) 66%,white)}.cap84-scene .s84-main{fill:color-mix(in srgb,var(--cap) 76%,white);stroke:color-mix(in srgb,var(--cap) 72%,var(--ink))}.cap84-scene .s84-paper{fill:color-mix(in srgb,var(--sheet) 84%,white);stroke:color-mix(in srgb,var(--cap) 52%,var(--rule))}.cap84-scene .s84-soft{fill:color-mix(in srgb,var(--cap) 24%,transparent);stroke:color-mix(in srgb,var(--cap) 70%,white)}.cap84-scene .s84-line{stroke:color-mix(in srgb,var(--ink) 78%,var(--cap));fill:none}.cap84-scene .s84-accent{fill:var(--cap);stroke:color-mix(in srgb,var(--cap) 74%,var(--ink))}
/* Sticky chrome should conceal scrolled content rather than ghost over it. */
.bar{background:var(--paper)!important;backdrop-filter:none!important;-webkit-backdrop-filter:none!important;z-index:120}.bar:before{background:var(--paper)!important;box-shadow:0 0 0 100vmax var(--paper),0 1px 0 100vmax var(--rule)!important;opacity:1!important}
/* Expanded case tools are secondary controls; keep them denser than the live next action. */
.case75-tools[open] .case75-group-body{gap:0!important;padding-top:6px}.case75-tools[open] .case75-group-body>section{margin-block:0!important;padding-block:10px}.case75-tools[open] .case75-group-body>section+section{border-top:1px solid color-mix(in srgb,var(--rule) 75%,transparent)}.case75-tools[open] .case75-group-body .h3{font-size:18px}.case75-tools[open] .case75-group-body .link{line-height:1.25}
/* The old compose trigger remains an actionability-compatible automation/programmatic hook, with no meaningful visual or keyboard footprint. */
.cap84-compose-hook{display:block!important;position:fixed!important;left:1px!important;top:1px!important;width:2px!important;height:2px!important;min-width:2px!important;min-height:2px!important;padding:0!important;margin:0!important;border:0!important;border-radius:0!important;opacity:.001!important;overflow:hidden!important;z-index:9999!important;pointer-events:auto!important;color:transparent!important;background:transparent!important;box-shadow:none!important}
@media(max-width:520px){.cap82-with-cases{padding-inline:0}.cap82-with-cases .cap82-grid{margin-right:-15px;padding-right:15px}.cap82-with-cases .cap82-card{flex-basis:142px;min-height:124px}.cap82-with-cases .cap82-art{height:70px}.cap82-with-cases .cap82-other{margin-top:0}.case75-tools[open] .case75-group-body>section{padding-block:8px}}
</style>

</head>`);
R('</body>',String.raw`<script>
(function(){
  function scene(id){
    var a='<svg viewBox="0 0 96 72" aria-hidden="true" focusable="false" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">',z='</svg>';
    if(id==='fix')return a+'<ellipse class="s84-soft" cx="48" cy="63" rx="31" ry="5"/><rect class="s84-back" x="16" y="11" width="42" height="48" rx="8"/><rect class="s84-paper" x="21" y="16" width="32" height="7" rx="3"/><circle class="s84-main" cx="37" cy="40" r="13"/><circle class="s84-soft" cx="37" cy="40" r="8"/><path class="s84-line" d="M67 19l11 11-9 9-6-6zM64 33l-9 9"/><path class="s84-accent" d="M67 49c5 6 7 9 7 12a7 7 0 1 1-14 0c0-3 2-6 7-12z" opacity=".82"/>'+z;
    if(id==='call')return a+'<ellipse class="s84-soft" cx="48" cy="64" rx="31" ry="5"/><rect class="s84-paper" x="13" y="30" width="42" height="28" rx="5" transform="rotate(-5 13 30)"/><path class="s84-line" d="M21 39h25M20 46h20M19 53h17"/><rect class="s84-main" x="47" y="9" width="23" height="48" rx="6"/><rect class="s84-soft" x="51" y="14" width="15" height="30" rx="3"/><path class="s84-line" d="M55 51h7"/><path class="s84-accent" d="M71 18h13a5 5 0 0 1 5 5v11a5 5 0 0 1-5 5h-5l-7 6v-6h-1z" opacity=".9"/>'+z;
    if(id==='promise')return a+'<ellipse class="s84-soft" cx="48" cy="64" rx="31" ry="5"/><rect class="s84-paper" x="12" y="13" width="45" height="43" rx="7"/><path class="s84-line" d="M20 9v10M47 9v10M12 25h45"/><rect class="s84-back" x="19" y="31" width="13" height="8" rx="2"/><rect class="s84-back" x="36" y="31" width="13" height="8" rx="2"/><circle class="s84-main" cx="67" cy="45" r="16"/><path class="s84-line" d="M67 35v11l7 5"/><path class="s84-accent" d="M73 16l7 3-7 3z"/>'+z;
    if(id==='chase')return a+'<ellipse class="s84-soft" cx="48" cy="64" rx="31" ry="5"/><path class="s84-paper" d="M12 18h51a7 7 0 0 1 7 7v20a7 7 0 0 1-7 7H37L25 61v-9H12a7 7 0 0 1-7-7V25a7 7 0 0 1 7-7z"/><path class="s84-line" d="M18 30h33M18 38h25"/><circle class="s84-main" cx="73" cy="24" r="13"/><path class="s84-line" d="M73 16v9l6 4"/><path class="s84-accent" d="M63 51h18l-5-5M81 51l-5 5"/>'+z;
    if(id==='document')return a+'<ellipse class="s84-soft" cx="48" cy="64" rx="31" ry="5"/><path class="s84-back" d="M10 25l26-14 26 14v31H10z"/><path class="s84-paper" d="M21 10h34l10 10v39H21z"/><path class="s84-line" d="M55 10v11h10M30 31h25M30 39h25M30 47h16"/><path class="s84-main" d="M10 25l26 20 26-20v31H10z" opacity=".92"/><circle class="s84-accent" cx="72" cy="47" r="11"/><path class="s84-line" d="M79 55l8 7"/>'+z;
    return a+'<ellipse class="s84-soft" cx="48" cy="64" rx="31" ry="5"/><rect class="s84-main" x="12" y="11" width="36" height="48" rx="6"/><circle class="s84-soft" cx="30" cy="31" r="8"/><path class="s84-line" d="M21 46h18M21 51h13"/><rect class="s84-paper" x="43" y="24" width="39" height="34" rx="6" transform="rotate(4 43 24)"/><path class="s84-line" d="M52 33h21M52 40h12"/><circle class="s84-accent" cx="73" cy="52" r="12"/><path d="M67 52l4 4 8-10" fill="none" stroke="white" stroke-width="3"/>'+z;
  }
  function upgrade(){
    document.querySelectorAll('.cap82-card').forEach(function(card){var art=card.querySelector('.cap82-art'),id=card.getAttribute('data-cap82');if(!art||!id||art.getAttribute('data-cap84')==='1')return;art.innerHTML=scene(id);art.classList.add('cap84-scene');art.setAttribute('data-cap84','1')});
    var p=document.querySelector('#cap82-start');if(p){var has=p.classList.contains('cap82-with-cases'),t=p.querySelector('.cap82-title');if(t){var want=has?'What do you need?':'What do you need to get sorted?';if(t.textContent!==want)t.textContent=want}var m=p.querySelector('.cap82-home-marker');if(m)m.remove()}
    var b=document.querySelector('main.home44 .home44-compose .home44-new');if(b){b.classList.add('cap84-compose-hook');b.setAttribute('aria-hidden','true');b.setAttribute('tabindex','-1')}
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',upgrade);else upgrade();new MutationObserver(upgrade).observe(document.documentElement,{childList:true,subtree:true});
})();
</script>
</body>`);
fs.writeFileSync('public/index.html',s);
const EXPECT='761c9c32b4cab1201ee28d1c57a6968a5ed02a32';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v84 ok',h(s),s.length);
