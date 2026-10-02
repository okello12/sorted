const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='ab8c221a306877629486694b5e0fe7fa01ff6487')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v71: answer from the reminder email. Yes or No opens the case and records it with the case's own buttons,
// after a fresh load; the case says what was recorded and offers Undo, because the email never names the case. ----
R("function openPending(){\n  if(!S.pending||!S.user)return;var t=task(S.pending.id);if(!t)return;var src=S.pending.src;S.pending=null;",
  "/* v71: answer from the reminder email. \"Yes\" or \"No\" in the email opens this case and records the answer with the same\n   buttons as the case page, once the cases have loaded fresh. The email never says which case, so the case shows what\n   was recorded and offers Undo. */\nfunction ansTarget(t,pid){var p=openPromise(t);if(p&&p.id===pid&&p.src!==\"parking\")return {k:\"p\",x:p};var m=openMove(t);if(m&&m.id===pid)return {k:\"m\",x:m};return null}\nfunction ansApply(t,ans,pid){\n  var g=ansTarget(t,pid);if(!g){toast(\"You’d already answered that reminder.\");return}\n  var snap=JSON.stringify(clean(t)),sel=g.k===\"p\"?'.promise [data-a=\"'+(ans===\"yes\"?\"kept\":\"missed\")+'\"]':'[data-a=\"'+(ans===\"yes\"?\"move-done\":\"move-rebook\")+'\"]',b=document.querySelector(sel);if(!b)return;\n  b.click();if(g.k===\"m\"&&ans!==\"yes\")return;\n  S.ansUndo={id:t.id,snap:snap,pid:pid,scored:g.k===\"p\",said:g.k===\"p\"?(ans===\"yes\"?\"they kept it\":\"it didn’t happen\"):\"you did it\",what:String(g.x.said||g.x.what||\"\").replace(/[.!]+$/,\"\")};render();\n}\nfunction ansBanner(t){var u=S.ansUndo;if(!u||u.id!==t.id)return \"\";return '<div class=\"note stack-s ans-note\" role=\"status\"><p><strong>Recorded from your email: '+esc(u.said)+'.</strong>'+(u.what?' “'+esc(u.what)+'”':'')+'</p><button class=\"link\" data-a=\"ans-undo\" style=\"align-self:flex-start\">Not this case? Undo</button></div>'}\nfunction openPending(){\n  if(!S.pending||!S.user||(S.pending.ans&&!S.loaded))return;var t=task(S.pending.id);if(!t)return;var src=S.pending.src,ans=S.pending.ans,pid=S.pending.p;S.pending=null;");
R("  S.retSrc=src||null;go({name:\"task\",id:t.id,panel:null});\n}",
  "  S.retSrc=src||null;go({name:\"task\",id:t.id,panel:null});if(ans&&pid)ansApply(t,ans,pid);\n}");
R("if(tk){S.pending={id:tk,src:qs.get(\"src\")||\"\"};",
  "if(tk){var qa=qs.get(\"ans\")||\"\";S.pending={id:tk,src:qs.get(\"src\")||\"\",ans:/^(yes|no)$/.test(qa)?qa:\"\",p:String(qs.get(\"p\")||\"\").slice(0,40)};");
R("\"&src=\"+encodeURIComponent(S.pending.src):\"\"",
  "\"&src=\"+encodeURIComponent(S.pending.src)+(S.pending.ans&&S.pending.p?\"&ans=\"+S.pending.ans+\"&p=\"+encodeURIComponent(S.pending.p):\"\"):\"\"");
R("(pt?'Sign in to open: <strong>'+esc(pt)+'</strong>':\"Sign in to open the case from your email.\")",
  "(pt?(S.pending.ans?'Sign in and Sorted will record your answer for: <strong>':'Sign in to open: <strong>')+esc(pt)+'</strong>':(S.pending.ans?\"Sign in and Sorted will record your answer from the email.\":\"Sign in to open the case from your email.\"))");
R("+hoLine(t)+'</section>';",
  "+hoLine(t)+'</section>'+ansBanner(t);");
R("  var a=b.getAttribute(\"data-a\"),d=S.draft,t=S.view.id?task(S.view.id):null;\n  switch(a){\n",
  "  var a=b.getAttribute(\"data-a\"),d=S.draft,t=S.view.id?task(S.view.id):null;\n  if(S.ansUndo&&a!==\"ans-undo\")S.ansUndo=null;\n  switch(a){\n");
R("    case \"cf-rm\":",
  "    case \"ans-undo\":if(t&&S.ansUndo&&S.ansUndo.id===t.id){var au=S.ansUndo,ao=JSON.parse(au.snap);Object.keys(t).forEach(function(k){if(k.charAt(0)!==\"_\")delete t[k]});Object.keys(ao).forEach(function(k){t[k]=ao[k]});S.ansUndo=null;\n      if(au.scored)try{sb.rpc(\"drop_outcome\",{p_promise:String(au.pid).slice(0,40)}).then(function(){},function(){})}catch(e){}\n      t._dirty=true;S.view.panel=null;S.draft={};commit();window.scrollTo(0,0);toast(\"Undone. Nothing was recorded.\")}break;\n    case \"cf-rm\":");
fs.writeFileSync('public/index.html',s);
const EXPECT='fa2caae7e7239782e01204334cee548540f4630a';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v71 ok',h(s),s.length);
