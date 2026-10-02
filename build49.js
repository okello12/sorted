const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='321f34fb75585da4e4f4df63ce67d7b8f7e0f76c')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,80));s=s.split(a).join(b)}
// ---- v49: visual polish. Keep the state model; make Home feel alive, calmer and more legible. ----

// Display titles are presentation only. Never rewrite the case itself.
R(`function home44Row(t,kind){`,String.raw`function home49Title(t){
  var x=String(t.title||"").replace(/^\s*TEST:\s*/i,"").trim();
  x=x.replace(/\s+(?:today|tomorrow)(?:\s+by\s+.+)?$/i,"").trim();
  if(x.length>48)x=x.slice(0,47).replace(/\s+\S*$/,"")+"…";
  return x||"Untitled case";
}
function home49Visual(count){
  return '<span class="home49-visual" aria-hidden="true"><span class="home49-folder"><i></i></span><span class="home49-clock"><i></i><b></b></span><span class="home49-count">'+count+'</span></span>';
}
function home44Row(t,kind){`);

// Spotlight and rows use the cleaned display title, while the stored title remains untouched.
R(`id="home44-spot-title">'+esc(t.title)+'</h2>`,`id="home44-spot-title">'+esc(home49Title(t))+'</h2>`);
R(`home44-row-title">'+esc(t.title)+'</span>`,`home44-row-title">'+esc(home49Title(t))+'</span>`);

// Secondary active rows do not all need the same "Your move" pill. Keep pills for meaningful distinct states.
R(`  else badge=s==="upcoming"?"Later":"Your move";`,`  else badge=s==="upcoming"?"Later":"";`);
R(`'+(note?'<span class="home44-row-note">'+esc(note)+'</span>':'')+'</span><span class="home44-pill">'+esc(badge)+'</span><span class="home44-chevron"`, `'+(note?'<span class="home44-row-note">'+esc(note)+'</span>':'')+'</span>'+(badge?'<span class="home44-pill">'+esc(badge)+'</span>':'<span></span>')+'<span class="home44-chevron"`);

// Give sections their state as a class so Waiting/Done can have their own quiet visual language.
R(`return '<section class="home44-section"><div class="home44-section-head">`, `return '<section class="home44-section '+kind+'"><div class="home44-section-head">`);

// "Also open" already explains itself. Remove the redundant explanatory line.
R(`home44Section("Also open",needs.slice(1),"needs","The rest of your open cases.")`,`home44Section("Also open",needs.slice(1),"needs","")`);

// Replace the plain count circle with a small folder/clock object inspired by the visual concepts.
R(`</div><span class="home44-orb" aria-hidden="true">'+needs.length+'</span></section>`, `</div>'+home49Visual(needs.length)+'</section>`);

// New-case entry stays easy to find without competing with the active case.
R(`'<button class="btn primary block home44-new" data-a="compose">+ Sort something new</button>'`,`'<button class="btn block home44-new" data-a="compose">+ Sort something new</button>'`);

// Styling and restrained motion. Motion is fully disabled for reduced-motion users.
R(`</style>\n\n</head>`,String.raw`/* v49 visual polish */
.home44{gap:23px}
.home44-intro{align-items:center}
.home49-visual{position:relative;display:block;flex:0 0 88px;width:88px;height:74px;filter:drop-shadow(0 10px 18px rgba(0,0,0,.14));transform-origin:50% 60%}
.home49-folder{position:absolute;left:5px;bottom:7px;width:64px;height:46px;border:1px solid var(--lav);border-radius:10px 11px 12px 12px;background:linear-gradient(145deg,var(--carbon-soft),var(--sheet));box-shadow:inset 0 1px 0 rgba(255,255,255,.12),0 8px 18px rgba(0,0,0,.08);transform:rotate(-4deg)}
.home49-folder:before{content:"";position:absolute;left:7px;top:-10px;width:30px;height:14px;border:1px solid var(--lav);border-bottom:0;border-radius:7px 7px 0 0;background:var(--carbon-soft)}
.home49-folder:after{content:"";position:absolute;left:8px;right:8px;top:12px;height:2px;border-radius:999px;background:var(--lav);opacity:.55;box-shadow:0 8px 0 color-mix(in srgb,var(--lav) 55%,transparent),0 16px 0 color-mix(in srgb,var(--lav) 35%,transparent)}
.home49-clock{position:absolute;right:2px;top:4px;width:37px;height:37px;border-radius:50%;border:2px solid var(--lav);background:var(--sheet);box-shadow:0 6px 16px rgba(0,0,0,.12)}
.home49-clock:after{content:"";position:absolute;inset:4px;border-radius:50%;border:1px solid var(--rule);opacity:.7}
.home49-clock i,.home49-clock b{position:absolute;left:17px;top:8px;width:2px;height:11px;border-radius:3px;background:var(--ink);transform-origin:50% 9px;z-index:2}
.home49-clock b{top:14px;height:8px;transform-origin:50% 3px;transform:rotate(125deg)}
.home49-count{position:absolute;right:0;bottom:0;display:grid;place-items:center;min-width:27px;height:27px;padding:0 7px;border-radius:999px;background:var(--lav);color:var(--carbon);border:2px solid var(--sheet);font:800 12px/1 var(--mono);box-shadow:0 5px 14px rgba(0,0,0,.16)}
.home44-spot{padding:17px 18px;gap:13px;border-radius:18px;background:radial-gradient(circle at 92% 3%,color-mix(in srgb,var(--lav) 18%,transparent),transparent 32%),linear-gradient(145deg,var(--sheet),var(--carbon-soft));box-shadow:0 16px 38px rgba(20,23,38,.11)}
.home44-question{font-size:clamp(25px,6.4vw,35px)}
.home44-actions{gap:8px}
.home44-actions .btn{min-height:49px}
.home44-details{opacity:.82}
.home44-section.needs .home44-section-head .muted{display:none}
.home44-section.waiting .h2:before{content:"";display:inline-block;width:9px;height:9px;margin:0 9px 2px 1px;border-radius:50%;background:var(--yellow-edge);box-shadow:0 0 0 5px color-mix(in srgb,var(--yellow) 55%,transparent)}
.home44-list{gap:8px}
.home44-row{grid-template-columns:10px minmax(0,1fr) auto 18px;position:relative;padding:14px 13px;min-height:68px;border-radius:14px;box-shadow:0 5px 16px rgba(0,0,0,.035);transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease,background .18s ease}
.home44-row:before{content:"";width:8px;height:8px;border-radius:50%;background:var(--lav);box-shadow:0 0 0 4px color-mix(in srgb,var(--lav) 18%,transparent)}
.home44-row.waiting:before{background:var(--yellow-edge);box-shadow:0 0 0 4px color-mix(in srgb,var(--yellow) 55%,transparent)}
.home44-row.done:before{background:var(--ink-2);box-shadow:none}
.home44-row:hover{transform:translateY(-1px);box-shadow:0 9px 22px rgba(0,0,0,.07)}
.home44-row:active{transform:translateY(0) scale(.995)}
.home44-row-title{font-size:18px}
.home44-row-meta,.home44-row-note{font-size:14px}
.home44-row.needs{border-left-width:2px}
.home44-pill{font-size:12px;min-height:28px;padding:3px 9px}
.home44-compose{padding-top:0}
.home44-new{border-radius:14px;font-size:17px;font-weight:700;background:var(--sheet);color:var(--ink);border:1.5px dashed var(--rule);box-shadow:none;min-height:50px;transition:background .18s ease,border-color .18s ease,transform .18s ease}
.home44-new:hover{background:var(--carbon-soft);border-color:var(--lav)}
.home44-new:active{transform:scale(.99)}
.home44-calm{position:relative;overflow:hidden;border-radius:18px;background:radial-gradient(circle at 88% 18%,color-mix(in srgb,var(--lav) 12%,transparent),transparent 35%),var(--sheet);box-shadow:0 12px 30px rgba(20,23,38,.07)}
.home44-calm .art-state{filter:drop-shadow(0 9px 18px rgba(0,0,0,.1))}
.home44-done{opacity:.92}
@media (max-width:520px){
  .home49-visual{flex-basis:76px;width:76px;height:66px}
  .home49-folder{width:56px;height:41px}
  .home49-clock{width:33px;height:33px}
  .home49-clock i{left:15px;top:7px;height:10px}
  .home49-clock b{left:15px;top:13px;height:7px}
  .home44-spot{padding:16px 15px}
  .home44-row{grid-template-columns:9px minmax(0,1fr) auto 15px;padding:13px 11px}
}
@media (prefers-reduced-motion:no-preference){
  .home49-visual{animation:home49Float 4.8s ease-in-out infinite}
  .home49-clock i{animation:home49Tick 10s linear infinite}
  .home44-spot{animation:home49Rise .42s cubic-bezier(.2,.75,.25,1) both}
  .home44-row{animation:home49Row .32s ease both}
  .home44-row:nth-child(2){animation-delay:.045s}
  .home44-row:nth-child(3){animation-delay:.09s}
  .home44-row:nth-child(4){animation-delay:.135s}
  .home44-calm .art-state{animation:home49Calm 5.6s ease-in-out infinite}
  .home49-count{animation:home49Pulse .6s ease .25s both}
}
@media (prefers-reduced-motion:reduce){
  .home49-visual,.home49-clock i,.home44-spot,.home44-row,.home44-calm .art-state,.home49-count{animation:none!important;transition:none!important}
}
@keyframes home49Float{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(-4px) rotate(1.2deg)}}
@keyframes home49Tick{to{transform:rotate(360deg)}}
@keyframes home49Rise{from{opacity:0;transform:translateY(8px) scale(.995)}to{opacity:1;transform:none}}
@keyframes home49Row{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:none}}
@keyframes home49Calm{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
@keyframes home49Pulse{0%{transform:scale(.75);opacity:.5}70%{transform:scale(1.08);opacity:1}100%{transform:scale(1)}}
</style>

</head>`);

fs.writeFileSync('public/index.html',s);
const EXPECT='e5bb671872c22e3d072b03ceb9d91be85d215ee1';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v49 ok',h(s),s.length);
