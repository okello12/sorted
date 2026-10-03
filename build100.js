const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='8ca9a5f1d49b0534c1ff2cd65f333610cb7b3a2b')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v100: hardening. The installed app's Home button really goes Home (goHome clears half-done state); Moving home
// is reachable before the first case and opens an existing move instead of making a duplicate; a case belongs to one
// move only; the same move date never makes a second move. ----
R("lastChoice='';if(standalone)document.documentElement.classList.add('cap87-standalone')",
  "lastChoice='';window.__cap87reset=function(){lastChoice=''};if(standalone)document.documentElement.classList.add('cap87-standalone')");
R("  var last='';\n  var MAP={",
  "  var last='';window.__cap90reset=function(){last=''};\n  var MAP={");
R("if(a==='home'){location.hash='#start';if(typeof render==='function')render();window.scrollTo(0,0);return}",
  "if(a==='home'){if(window.SortedHome){window.SortedHome();return}location.hash='#start';window.scrollTo(0,0);return}");
R("function go(view){",
  "/* v100: one way Home. Clears anything half-done (a start choice, a draft, an open panel, a pending link to a move), shows\n   Home, scrolls to the top and leaves one history entry. Saved cases and moves are untouched. */\nfunction goHome(){\n  S.draft={};S.composeOpen=false;S.pendingMom=null;\n  try{sessionStorage.removeItem(\"sorted.cap82\");sessionStorage.removeItem(\"cap90.choice\");sessionStorage.removeItem(\"sorted.moment\")}catch(e){}\n  try{if(window.__cap87reset)window.__cap87reset();if(window.__cap90reset)window.__cap90reset()}catch(e){}\n  document.documentElement.classList.remove(\"cap90-intake\");\n  try{history.replaceState(null,\"\",location.pathname+(S.user?\"#start\":\"\"))}catch(e){}\n  go({name:\"home\"});window.scrollTo(0,0);\n}\nwindow.SortedHome=function(){goHome()};\nfunction go(view){");
R("function momOf(id){",
  "function momLatest(){var ms=(S.moments||[]).filter(function(m){return m.type===\"moving\"});if(!ms.length)return null;var td=momToday(),up=ms.filter(function(m){return m.date>=td}).sort(function(a,b){return a.date<b.date?-1:1});return up[0]||ms.slice().sort(function(a,b){return a.date<b.date?1:-1})[0]}\nfunction momStartEntry(){\n  if(!S.user||!S.loaded||giKind()||momLatest())return \"\";var d=S.draft||{};if(d.pkShort||d.psShort||d.vague||d.matchId||d.fromShare)return \"\";\n  return '<div class=\"cap100-big\"><span>Planning something bigger?</span><button type=\"button\" class=\"btn cap100-btn\" data-a=\"mom-start\">Moving home</button></div>';\n}\nfunction momPendingBoot(){var k=\"\";try{k=sessionStorage.getItem(\"sorted.moment\")||\"\";sessionStorage.removeItem(\"sorted.moment\")}catch(e){}if(!k)return;if(k===\"moving\"){var mv=momLatest();S.view=mv?{name:\"moment\",id:mv.id}:{name:\"moment-new\"};return}setTimeout(function(){var x=$(\"#cap95-explore\"),mo=$(\"#moment-\"+k);if(x&&mo){x.open=true;mo.open=true;mo.scrollIntoView({block:\"start\"})}},400)}\nfunction momOf(id){");
R("  h+='<main class=\"home44 fade\">';",
  "  h+='<main class=\"home44 fade\">';h+=momStartEntry();");
R("  S.tasks=cacheRead();momSplit();S.booting=false;",
  "  S.tasks=cacheRead();momSplit();momPendingBoot();S.booting=false;");
R("case \"mom-new\":{S.view={name:\"moment-new\"};",
  "case \"mom-start\":{var mls=momLatest();if(mls){go({name:\"moment\",id:mls.id})}else{S.view={name:\"moment-new\"};S.draft={};render();window.scrollTo(0,0)}break}\n    case \"mom-new\":{S.view={name:\"moment-new\"};");
R("}else{try{sessionStorage.setItem(\"sorted.moment\",mvk)}catch(z){}if(S.user){",
  "}else{try{sessionStorage.setItem(\"sorted.moment\",mvk)}catch(z){}if(S.user){try{sessionStorage.removeItem(\"sorted.moment\")}catch(z){}");
R("    if(it.on&&!it.on(a))return;var st=(m.items||{})[it.k]||{},c=st.caseId?task(st.caseId):null;",
  "    if(it.on&&!it.on(a))return;var st=(m.items||{})[it.k]||{},c=st.caseId?task(st.caseId):null;if(c&&c.momentId!==m.id){c=null;st={}}");
R("function momAttach(t){",
  "function momDetach(cid,keep){(S.moments||[]).forEach(function(o){if(o.id===keep)return;var ch=false;Object.keys(o.items||{}).forEach(function(k){if(o.items[k].caseId===cid){delete o.items[k];ch=true}});if(ch)o._dirty=true})}\nfunction momAttach(t){");
R("  t.momentId=m.id;m.items=m.items||{};if(pm.k){",
  "  t.momentId=m.id;momDetach(t.id,m.id);m.items=m.items||{};if(pm.k){");
R("if(ml&&lc){lc.momentId=ml.id;lc._dirty=true;",
  "if(ml&&lc){lc.momentId=ml.id;momDetach(lc.id,ml.id);lc._dirty=true;");
R("    var nm={id:uid(),kind:\"moment\",type:\"moving\"",
  "    var same=(S.moments||[]).filter(function(x){return x.type===\"moving\"&&x.date===mvd})[0];if(same){go({name:\"moment\",id:same.id});toast(\"You already have a move on that day. Here it is.\");return}\n    var nm={id:uid(),kind:\"moment\",type:\"moving\"");
R(".cap99-home{margin:0}",
  ".cap100-big{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;padding:10px 14px;border:1.5px dashed color-mix(in srgb,var(--violet) 30%,var(--rule));border-radius:14px;background:var(--sheet)}\n.cap100-big span{font-weight:700}\n.cap100-btn{min-height:44px}\n.cap99-home{margin:0}");
fs.writeFileSync('public/index.html',s);
const EXPECT='71073c67b75d5e7933395eb812cdb0e39c569d02';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v100 ok',h(s),s.length);
