const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='107e873bd5f6b1854680491c25542cb9f86999c0')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v52: intake slice 1. "What they sent" on each case ----


// 1. "What they sent": the messages, screenshots and PDFs added to this case, newest first, read from its history
R("  if(s!==\"done\"&&S.view.panel!==\"paste\")h+='<button class=\"link\" data-a=\"panel\" data-p=\"paste\" style=\"align-self:flex-start\">Paste a message they sent</button>';",
  "  h+=evidenceBlock(t);\n  if(s!==\"done\"&&S.view.panel!==\"paste\")h+='<button class=\"link\" data-a=\"panel\" data-p=\"paste\" style=\"align-self:flex-start\">Paste a message they sent</button>';");
R("function readCase(t,f){",
  "var EVRE=/^Added (a message shared from another app|a screenshot|a PDF|a message): “([\\s\\S]*)”$/;\nvar EVSRC={\"a message shared from another app\":\"Shared\",\"a screenshot\":\"Screenshot\",\"a PDF\":\"PDF\",\"a message\":\"Message\"};\nfunction evidenceOf(t){return (t.events||[]).map(function(e){var m=EVRE.exec(e.label||\"\");return m?{at:e.at,src:m[1],text:m[2]}:null}).filter(Boolean).reverse()}\nfunction evidenceBlock(t){\n  var ev=evidenceOf(t);if(!ev.length)return \"\";\n  function item(x){return '<li class=\"ev-item\"><div class=\"ev-top\"><span class=\"ev-src\">'+esc(EVSRC[x.src]||\"Message\")+'</span><time datetime=\"'+esc(x.at)+'\">'+esc(stampLabel(x.at))+'</time></div><p class=\"ev-text\">“'+esc(x.text)+'”</p></li>'}\n  var h='<section class=\"stack-s evidence\" aria-labelledby=\"evh\"><h2 class=\"h3\" id=\"evh\">What they sent <span class=\"ev-count\">'+ev.length+'</span></h2><ol class=\"ev-list\">'+ev.slice(0,3).map(item).join(\"\")+'</ol>';\n  if(ev.length>3)h+='<details class=\"ev-more\"><summary>Show '+(ev.length-3)+' more</summary><ol class=\"ev-list\">'+ev.slice(3).map(item).join(\"\")+'</ol></details>';\n  return h+'</section>';\n}\nfunction readCase(t,f){");

// 2. The history says what was added and points to the block, instead of repeating the whole message
R("  t.events.slice().reverse().forEach(function(e){h+=evRow(e,t)});",
  "  t.events.slice().reverse().forEach(function(e){var em=EVRE.exec(e.label||\"\");h+=evRow(em?Object.assign({},e,{label:\"Added \"+em[1]+\". It’s under What they sent.\"}):e,t)});");

// 3. Styles, from the theme colours so light and dark both work
R(".art-share{width:220px;margin:0 auto}",
  ".art-share{width:220px;margin:0 auto}\n.ev-count{display:inline-grid;place-items:center;min-width:26px;height:26px;padding:0 7px;border-radius:999px;background:var(--carbon-soft);color:var(--carbon);font-size:13px;vertical-align:middle}\n.ev-list{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px}\n.ev-item{background:var(--sheet);border:1px solid var(--rule);border-radius:12px;padding:12px 14px;display:flex;flex-direction:column;gap:6px}\n.ev-top{display:flex;justify-content:space-between;align-items:center;gap:10px;font-size:14px;color:var(--ink-2)}\n.ev-src{font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--carbon);background:var(--carbon-soft);border-radius:999px;padding:3px 9px}\n.ev-text{margin:0;font-size:16px;overflow-wrap:anywhere}\n.ev-more>summary{min-height:44px;display:flex;align-items:center;color:var(--carbon);font-weight:600;cursor:pointer}\n.ev-more[open]>summary{margin-bottom:8px}");

fs.writeFileSync('public/index.html',s);
const EXPECT='67f6c514a66915d746e3f291cc64543feee11c27';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v52 ok',h(s),s.length);
