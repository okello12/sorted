const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='7d20ac95de8bbe88baa1160c3bc7f6531e9d00e9')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,90));s=s.split(a).join(b)}
// v106 / SEM-03. Keep the runtime separate; this layer only installs it into the final v105 application.
const SEM=fs.readFileSync('sem03.runtime.js','utf8');
R("function commit(){save();render()}",SEM+"\nfunction commit(){var ct=S.view.id&&task(S.view.id);if(ct)semEnsure(ct,true);save();render()}");
R("  var b=e.target.closest(\"[data-a]\");if(!b)return;\n  var a=b.getAttribute(\"data-a\"),d=S.draft,t=S.view.id?task(S.view.id):null;",
  "  var b=e.target.closest(\"[data-a]\");if(!b)return;\n  var a=b.getAttribute(\"data-a\"),d=S.draft,t=S.view.id?task(S.view.id):null;\n  if(t&&a===\"cm-add\"){var sc=document.querySelector(\".cm-card\");if(sc)semObserveText(t,sc.innerText,\"the email reply you added\")}\n  if(t&&a===\"note-keep\"){var sn=document.querySelector(\".notes-block\");if(sn)semObserveText(t,sn.innerText,\"the helper note you kept\")}");
R("  switch(a){\n    case \"home\":",
  "  switch(a){\n    case \"sem-yes\":if(t)semApplyPending(t,\"correction\");break;\n    case \"sem-no\":if(t)semRejectPending(t);break;\n    case \"sem-date-correct\":if(t)semApplyPending(t,\"correction\");break;\n    case \"sem-date-moved\":if(t)semApplyPending(t,\"reschedule\");break;\n    case \"home\":");
R("  var form=e.target,k=form.getAttribute(\"data-f\"),d=S.draft,t=S.view.id?task(S.view.id):null;",
  "  var form=e.target,k=form.getAttribute(\"data-f\"),d=S.draft,t=S.view.id?task(S.view.id):null;\n  if(t)semObserveForm(t,form,k);");
fs.writeFileSync('public/index.html',s);
const EXPECT='';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v106 ok',h(s),s.length);
