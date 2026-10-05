const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='487a638e38f1fc475106fd30f2391c0bb16ab22d')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v131: fixes from Baldwin's phone after v130. ----
R("function case75TitleParts(t){\n  var x=String(t.title||\"\").replace(/^\\s*TEST:\\s*/i,\"\").trim();",
  "/* v131: older guided starts saved \"<Who> said they would nothing\" and \"<Who> said they would Need to do a credit check\"\n   (the second box typed in with its capital). Show \"Waiting for <Who>\" and \"<Who>: Need to do a credit check\" wherever the\n   title appears: Home, Cases, the case and the recap. The saved title is not changed. */\nfunction title131(x){x=String(x||\"\");\n  x=x.replace(/^(.+?)\\s+said (?:they|he|she|it) would\\s+(?:nothing|none|n\\/?a|not sure|unsure|dunno|no idea|idk|tbc|nothing yet|not yet)\\.?(\\s*[·•].*)?$/i,\"Waiting for $1$2\");\n  x=x.replace(/^(.+?)\\s+said (?:they|he|she|it) would\\s+(?=[A-Z])(.+)$/,\"$1: $2\");\n  return x}\nfunction case75TitleParts(t){\n  var x=String(t.title||\"\").replace(/^\\s*TEST:\\s*/i,\"\").trim();\n  x=title131(x);");
R("x=x.replace(/^(.+?)\\s+said (?:they|he|she|it) would\\s+(?:nothing|none|n\\/?a|not sure|dunno|no idea)\\.?$/i,\"Waiting for $1\");",
  "x=x.replace(/^(.+?)\\s+said (?:they|he|she|it) would\\s+(?:nothing|none|n\\/?a|not sure|dunno|no idea)\\.?$/i,\"Waiting for $1\");x=title131(x);");
R("var out=[t.title.replace(/[.!]+$/,\"\")+\". Started \"",
  "var out=[title131(t.title).replace(/[.!]+$/,\"\")+\". Started \"");
R("<p class=\"h3\">'+esc(t.outcome||\"Done\")+'</p></div><p class=\"note\">'+esc(recapText(t))+'</p><div class=\"row eq\"><button class=\"btn primary\" data-a=\"recap-copy\">Copy recap</button><button class=\"btn\" data-a=\"recap-share\">Share</button></div>",
  "<p class=\"h3\">'+esc(t.outcome||\"Done\")+'</p></div><div class=\"stack-s rc131\"><button class=\"btn primary block\" data-a=\"go-home\">Done, back to Home</button><button class=\"btn block quiet\" data-a=\"new-case\">+ Start something new</button></div><p class=\"note\">'+esc(recapText(t))+'</p><div class=\"row eq\"><button class=\"btn\" data-a=\"recap-copy\">Copy recap</button><button class=\"btn\" data-a=\"recap-share\">Share</button></div>");
R("if(location.hash!==h)history.replaceState(null,\"\",location.pathname+h)}else if(/^#(?:case-|cases$|more$|move-)/.test(location.hash))history.replaceState(null,\"\",location.pathname+\"#start\")",
  "if(location.hash!==h)history.pushState(null,\"\",location.pathname+h)}else if(/^#(?:case-|cases$|more$|move-)/.test(location.hash))history.pushState(null,\"\",location.pathname+\"#start\")");
R("try{history.replaceState(null,\"\",location.pathname+(S.user?\"#start\":\"\"))}catch(e){}",
  "try{if(!/^#(?:case-|cases$|more$|move-)/.test(location.hash))history.replaceState(null,\"\",location.pathname+(S.user?\"#start\":\"\"))}catch(e){}");
R("S.newOpen=true;S.view={name:\"home\"};render();",
  "S.newOpen=true;S.view={name:\"home\"};navHash(S.view);render();");
R("function navRestore(){",
  "/* v131: Safari's back arrow and the iPhone's swipe back move between the places Sorted pushed (a case, Cases, More, a\n   move, Home), instead of leaving Sorted or doing nothing. */\nwindow.addEventListener(\"popstate\",function(){if(!S.user||S.booting)return;var h=location.hash||\"\",m,v=null;\n  if((m=/^#case-([\\w-]+)$/.exec(h))&&task(m[1]))v={name:\"task\",id:m[1]};\n  else if(h===\"#cases\")v={name:\"cases\"};\n  else if(h===\"#more\")v={name:\"data\"};\n  else if((m=/^#move-([\\w-]+)$/.exec(h))&&momOf(m[1]))v={name:\"moment\",id:m[1]};\n  else if(!h||h===\"#start\")v={name:\"home\"};\n  if(!v||(S.view&&S.view.name===v.name&&S.view.id===v.id&&!S.view.panel))return;\n  S.newOpen=false;S.composeOpen=false;go(v)});\nfunction navRestore(){");
R("+ Sort something new</button>')+'</div><div class=\"home113-more\">'",
  "+ Sort something new</button>')+'</div>'+(nOpen?'':'<div class=\"home131-ways\"><button class=\"btn block home131-start\" data-a=\"new-case\">+ Start something new</button><button class=\"btn block quiet\" data-a=\"cases\">See all my cases</button></div>')+'<div class=\"home113-more\">'");
R(".more129{margin:0;font-size:15px}",
  ".more129{margin:0;font-size:15px}\n.home131-ways{display:grid;gap:10px}\n.home131-ways .btn{min-height:48px}\n.home131-start{font-weight:700}");
R(".tab129-new[aria-current=page]{color:#fff;background:var(--violet2,#4F39D9)}",
  ".tab129-new[aria-current=page]{color:#fff;background:var(--violet2,#4F39D9)}\n.tab129-b{position:relative}\n.tab129-b[aria-current=page]{color:var(--carbon);background:color-mix(in srgb,var(--violet) 20%,transparent)}\n.tab129-b[aria-current=page]::before{content:\"\";position:absolute;top:-7px;left:24%;right:24%;height:3px;border-radius:0 0 3px 3px;background:var(--violet)}\n.tab129-new,.tab129-new[aria-current=page]{background:transparent;color:var(--ink-2)}\n.tab129-new .tab129-i{display:grid;place-items:center;width:30px;height:30px;border-radius:50%;background:var(--violet2,#4F39D9);color:#fff;font-size:22px;line-height:1;margin:-7px 0 -3px}");
R("var SORTED_V=\"v130\"",
  "var SORTED_V=\"v131\"");
fs.writeFileSync('public/index.html',s);
const EXPECT='4f1a841e869d2eb0b31f2299dd0c5879e101c3d6';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v131 ok',h(s),s.length);
