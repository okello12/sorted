const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='4f945c7f0acb2ea74e90eb2f236d5f2872d28db2')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v83: the Home spotlight shows your own step and its date, with a button to tick it off; an existing renewal step
// points to GOV.UK; a reference must contain a digit (so "landlord" is never a Ref); complaints are named after the company. ----
R("function caseEntry(){",
  "/* v83: the official place to do a renewal step that already exists in a case, from the hand-checked OFFICIAL table */\nfunction doOfficial(t){\n  if(t.mode!==\"do\")return \"\";var x=(t.title||\"\")+\" \"+(t.said||\"\"),k=/passport/i.test(x)?\"passport\":/tv licen/i.test(x)?\"tv\":/licen[cs]e/i.test(x)?\"licence\":/\\bmot\\b/i.test(x)?\"mot\":/(car|road|vehicle) tax/i.test(x)?\"tax\":\"\";\n  var o=k&&OFFICIAL[k];if(!o||!o.url)return \"\";\n  return '<p class=\"note\" style=\"margin:0\">Do it on the official site: <a href=\"'+esc(o.url)+'\" target=\"_blank\" rel=\"noopener\">'+esc(o.url.replace(/^https:\\/\\/(www\\.)?/,\"\").replace(/\\/.*$/,\"\"))+'</a>. Sorted can’t renew it for you, but it can remind you.</p>';\n}\nfunction caseEntry(){");
R("    case \"compose\":S.composeOpen=true;render();var cf=$(\"#f-case\");if(cf)cf.focus();break;",
  "    case \"compose\":S.composeOpen=true;render();var cf=$(\"#f-case\");if(cf)cf.focus();break;\n    case \"home-move\":{var hmid=b.getAttribute(\"data-id\");S.retSrc=\"home\";go({name:\"task\",id:hmid,panel:null});var hmb=document.querySelector('[data-a=\"move-done\"]');if(hmb)hmb.click();break}");
R("    var next=m?moveTitle(m):nextStepText(t),meta=home44Meta(t);\n    h+='<p class=\"home44-question\">'+esc(next)+'</p>'+(meta&&meta!==next?'<p class=\"home44-meta\">'+esc(meta)+'</p>':'');\n    h+='<button class=\"btn primary home44-open\" data-a=\"open\" data-id=\"'+t.id+'\">Open this case</button>';",
  "    if(m&&m.what){\n      h+='<p class=\"home44-question\">'+esc(cap1(String(m.what).replace(/[.!]+$/,\"\")))+'</p><p class=\"home44-meta\">'+esc(m.dueAt?(moveTitle(m)===\"Your move\"?\"\":moveTitle(m)+\" · \")+whenText(m):\"No date set\")+'</p>';\n      h+='<div class=\"home44-actions\"><button class=\"btn primary\" data-a=\"home-move\" data-id=\"'+t.id+'\">'+esc(moveAct(m.what).done)+'</button><button class=\"btn\" data-a=\"open\" data-id=\"'+t.id+'\">Open this case</button></div>';\n    }else{\n    var next=m?moveTitle(m):nextStepText(t),meta=home44Meta(t);\n    h+='<p class=\"home44-question\">'+esc(next)+'</p>'+(meta&&meta!==next?'<p class=\"home44-meta\">'+esc(meta)+'</p>':'');\n    h+='<button class=\"btn primary home44-open\" data-a=\"open\" data-id=\"'+t.id+'\">Open this case</button>';}");
R("  if(t.mode===\"do\")return \"What’s the next step?\";",
  "  if(t.mode===\"do\")return \"Add your next step and when\";");
R("  if(mv&&s!==\"done\"&&!(mv.src===\"parking\"&&pkOn(t)))h+=moveCard(t,mv);",
  "  if(mv&&s!==\"done\"&&!(mv.src===\"parking\"&&pkOn(t)))h+=moveCard(t,mv)+doOfficial(t);");
R("  var m=/^(.*?)[\\s]*[·•]\\s*([A-Z0-9][A-Z0-9-]{3,})$/i.exec(x),ref=\"\";",
  "  var m=/^(.*?)[\\s]*[·•]\\s*((?=[A-Z-]*\\d)[A-Z0-9][A-Z0-9-]{3,})$/i.exec(x),ref=\"\";");
R("[/\\bcomplaint\\b/i,\"complaint\"]",
  "[/\\bcomplain(?:t|ts|ed|ing)?\\b/i,\"complaint\"]");
fs.writeFileSync('public/index.html',s);
const EXPECT='801ac97609b9c4150a0f3ec1360dad8676843849';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v83 ok',h(s),s.length);
