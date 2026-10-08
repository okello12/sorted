const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='be0e123c6ed62af11990958ae095d91c32229b4b')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v142: a day said yesterday counts from yesterday; one reminder row per promise or step; the stop link asks first; Android shares arrive through the service worker. ----
R("if(DAYW141.test(c.replace(/\\byesterday\\b/gi,\" \")))c=c.replace(/\\b(?:on\\s+)?yesterday\\b,?/gi,\" \");else",
  "if(DAYW141.test(c.replace(/\\byesterday\\b/gi,\" \"))){var y142=/\\byesterday\\b/i.test(c);c=c.replace(/\\b(?:on\\s+)?yesterday\\b,?/gi,\" \");/* v142: a day said yesterday counts from yesterday */if(!y142);else if(/\\bthe day after tomorrow\\b/i.test(c))c=c.replace(/\\bthe day after tomorrow\\b/gi,\"tomorrow\");else c=c.replace(/\\b(?:tomorrow|tmrw|tmr)\\b/gi,\"today\")}else");
R("upsert(rows,{onConflict:\"task_id,kind,send_at\",ignoreDuplicates:true})",
  "upsert(rows.map(function(x){if(x.promise_id===undefined)x.promise_id=null;return x}),{onConflict:\"task_id,kind,send_at,promise_id\",ignoreDuplicates:true})");
R("  var hq=qs.get(\"helper\"),ht=qs.get(\"h\");",
  "  var stm=/^#stop=([0-9a-f-]{36})\\.([0-9a-f]{32})$/.exec(location.hash||\"\");\n  if(stm){S.view={name:\"estop\",u:stm[1],t:stm[2]};try{history.replaceState(null,\"\",location.pathname)}catch(e){}render();return}\n  var hq=qs.get(\"helper\"),ht=qs.get(\"h\");");
R("  else if(v.name===\"helper\")html=viewHelper();",
  "  else if(v.name===\"helper\")html=viewHelper();\n  else if(v.name===\"estop\")html=viewEstop();");
R("function docTitle141(){var v=S.view,h=location.hash||\"\";",
  "function docTitle141(){var v=S.view,h=location.hash||\"\";if(v.name===\"estop\")return \"Stop reminder emails · Sorted\";");
R("window.addEventListener(\"hashchange\",function(){if(/^#new=/.test(location.hash)",
  "window.addEventListener(\"hashchange\",function(){var stm=/^#stop=([0-9a-f-]{36})\\.([0-9a-f]{32})$/.exec(location.hash||\"\");if(stm){S.view={name:\"estop\",u:stm[1],t:stm[2]};S.estopResult=null;try{history.replaceState(null,\"\",location.pathname)}catch(e){}render();window.scrollTo(0,0)}});\nwindow.addEventListener(\"hashchange\",function(){if(/^#new=/.test(location.hash)");
R("/* ---------- 4. letters: a complaint, and a subject access request ---------- */",
  "/* v142: \"Stop all reminder emails\" from an email footer. The link carries a signed token in the address's # part, so\n   it never reaches a server log; the page asks first and only the tap sends it to email-stop. */\nfunction viewEstop(){var r=S.estopResult,h='<header class=\"bar\"><span class=\"mark\">sorted<b>.</b></span></header><main class=\"stack fade\" style=\"margin-top:8px\">';\n  if(r===\"busy\")return h+'<p class=\"muted\" role=\"status\">One moment…</p></main>';\n  if(r===\"done\")return h+'<h1 class=\"h2\" id=\"estop-h\" tabindex=\"-1\">Done. No more reminder emails.</h1><p>Sorted won’t send you reminder emails any more. Your cases stay as they are, and reminders on your phone’s lock screen, if you switched them on, carry on.</p><p>You can turn emails back on in Settings.</p><a class=\"btn block\" href=\"/#start\">Open Sorted</a></main>';\n  if(r===\"bad\")return h+'<h1 class=\"h2\" id=\"estop-h\" tabindex=\"-1\">That didn’t work.</h1><p>Nothing has changed. You can turn reminder emails off in Settings, or use the Unsubscribe button in your email app.</p><a class=\"btn block\" href=\"/#more-settings\">Open Settings</a></main>';\n  return h+'<h1 class=\"h2\" id=\"estop-h\" tabindex=\"-1\">Stop all reminder emails?</h1><p>Sorted will stop sending you reminder emails for every case. Your cases stay as they are.</p><button class=\"btn primary block\" data-a=\"estop-yes\">Stop reminder emails</button><a class=\"btn block\" href=\"/#start\">Keep them</a></main>'}\n/* ---------- 4. letters: a complaint, and a subject access request ---------- */");
R("    case \"helper-answer\":",
  "    case \"estop-yes\":{if(S.estopResult===\"busy\")break;S.estopResult=\"busy\";render();var eu=S.view.u,et=S.view.t;\n      fetch(SUPA_URL+\"/functions/v1/email-stop?u=\"+encodeURIComponent(eu)+\"&t=\"+encodeURIComponent(et),{method:\"POST\"}).then(function(r){S.estopResult=r.ok?\"done\":\"bad\"},function(){S.estopResult=\"bad\"}).then(function(){render();var eh=document.getElementById(\"estop-h\");if(eh)try{eh.focus()}catch(e){}});break}\n    case \"helper-answer\":");
R("function boot(){\n  if(!grabShared()){",
  "function boot(){\n  try{if(\"serviceWorker\" in navigator&&/Android/i.test(navigator.userAgent||\"\"))navigator.serviceWorker.register(\"/sw.js\",{scope:\"/\"}).catch(function(){})}catch(e){}\n  if(!grabShared()){");
R("Every reminder email links to this switch, and your email app’s Unsubscribe button stops them all.",
  "Every reminder email has a link that stops them all, after asking you once, and a link to this switch.");
R("Every reminder email links to that switch, and your email app’s Unsubscribe button stops them all.",
  "Every reminder email has a link that stops them all, after asking you once, and a link to that switch.");
s=s.split('SORTED_V="v141"').join('SORTED_V="v142"');
fs.writeFileSync('public/index.html',s);
const EXPECT='ec661431c2b0b644c65fbed3e2053547298099c5';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v142 ok',h(s),s.length);
