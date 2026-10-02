const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='af214e65dc8bea2880dae263157c7773cfdf35d4')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v73: "Came in" on Home: replies and helper notes waiting in any case, newest first, each opening its case. ----
R("function stampLabel(",
  "/* v73: \"Came in\" on Home. Replies and helper notes waiting in any case, so they're seen without opening every case.\n   Only ids, the case, where it came from and when are fetched here; the words are read in the case itself. */\nfunction loadFound(force){\n  if(!S.user||(!force&&S.foundAt&&Date.now()-S.foundAt<60000))return;S.foundAt=Date.now();var got={};\n  var done=function(){if(!got.m||!got.n)return;var was=JSON.stringify(S.found||null);S.found={mail:got.m,notes:got.n};if(was!==JSON.stringify(S.found)&&S.view.name===\"home\")render()};\n  try{sb.from(\"inbound_items\").select(\"id,task_id,from_domain,received_at\").is(\"used_at\",null).then(function(r){got.m=(r&&!r.error&&Array.isArray(r.data)?r.data:[]).filter(function(x){return x.task_id});done()},function(){got.m=[];done()})}catch(e){got.m=[]}\n  try{sb.from(\"case_notes\").select(\"id,task_id,author,created_at\").then(function(r){got.n=r&&!r.error&&Array.isArray(r.data)?r.data:[];done()},function(){got.n=[];done()})}catch(e){got.n=[]}\n}\nfunction foundDrop(id){if(S.found){S.found.mail=S.found.mail.filter(function(x){return x.id!==id});S.found.notes=S.found.notes.filter(function(x){return x.id!==id})}}\nfunction foundBlock(){\n  loadFound();var f=S.found;if(!f)return \"\";\n  var rows=[];\n  f.mail.forEach(function(x){var t=task(x.task_id);if(t)rows.push({t:t,at:x.received_at,what:\"A reply came in\"+(x.from_domain?\" from \"+x.from_domain:\"\")})});\n  f.notes.forEach(function(x){var t=task(x.task_id);if(t)rows.push({t:t,at:x.created_at,what:x.author+\" added a note\"})});\n  if(!rows.length)return \"\";\n  rows.sort(function(a,b){return String(b.at).localeCompare(String(a.at))});\n  var more=rows.length-5,h='<section class=\"sheet stack-s found-strip\" aria-labelledby=\"fdh\"><p class=\"eyebrow\">Came in</p><h2 class=\"h3\" id=\"fdh\">'+(rows.length===1?\"Something came in for you to look at\":rows.length+\" things came in for you to look at\")+'</h2>';\n  rows.slice(0,5).forEach(function(r){h+='<button class=\"found-row\" data-a=\"open\" data-id=\"'+esc(r.t.id)+'\"><span class=\"found-what\">'+esc(r.what)+'</span><span class=\"found-case\">'+esc(home54Title(r.t))+' · '+esc(stampLabel(r.at))+'</span></button>'});\n  if(more>0)h+='<p class=\"muted\" style=\"font-size:14px;margin:0\">And '+more+' more.</p>';\n  return h+'<p class=\"muted\" style=\"font-size:14px;margin:0\">Nothing joins a case until you add it there.</p></section>';\n}\nfunction stampLabel(");
R("    if(shareTop)h+='<div class=\"home44-compose\">'+caseEntry()+'</div>';\n",
  "    if(shareTop)h+='<div class=\"home44-compose\">'+caseEntry()+'</div>';\n    h+=foundBlock();\n");
R("S.caseMail[t.id]=cml.filter(function(x){return x!==cmx});",
  "S.caseMail[t.id]=cml.filter(function(x){return x!==cmx});foundDrop(cmx.id);");
R("var cmd=b.getAttribute(\"data-id\");",
  "var cmd=b.getAttribute(\"data-id\");foundDrop(cmd);");
R("S.notes[t.id]=nkl.filter(function(x){return x!==nk});",
  "S.notes[t.id]=nkl.filter(function(x){return x!==nk});foundDrop(nk.id);");
R("var nd=b.getAttribute(\"data-id\");",
  "var nd=b.getAttribute(\"data-id\");foundDrop(nd);");
R(".pk-card p{margin:0}",
  ".pk-card p{margin:0}\n.found-strip{gap:10px}\n.found-row{display:flex;flex-direction:column;align-items:flex-start;gap:2px;width:100%;text-align:left;background:none;border:0;border-top:1px solid var(--rule);padding:12px 0 4px;font:inherit;color:var(--ink);cursor:pointer;min-height:44px}\n.found-what{font-weight:600}\n.found-case{font-size:15px;color:var(--ink-2)}");
fs.writeFileSync('public/index.html',s);
const EXPECT='6c7dd8339e7c012ff1e81d3702e8c763e667057e';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v73 ok',h(s),s.length);
