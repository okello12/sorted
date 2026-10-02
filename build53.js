const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='67f6c514a66915d746e3f291cc64543feee11c27')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v53: intake slice 2. A shared message asks which case it belongs to ----
R("function readCase(t,f){",
  "function shareCases(tx){var m=matchCase(caseFacts(tx)),list=S.tasks.filter(function(x){return !x.example&&state(x)!==\"done\"});if(m)list=[m].concat(list.filter(function(x){return x!==m}));return {m:m,list:list.slice(0,6)}}\nfunction sharePicking(d){return !!(d.fromShare&&!d.picked&&shareCases(d.casetext||\"\").list.length)}\nfunction shareBlock(d){\n  var sc=shareCases(d.casetext||\"\");\n  var h='<div class=\"stack-s share-pick\" role=\"group\" aria-labelledby=\"shp\"><h3 class=\"h3\" id=\"shp\">Where does this go?</h3><p class=\"muted\" style=\"font-size:16px\">Add it to a case you already have, or start a new one.</p>';\n  sc.list.forEach(function(x){h+='<button type=\"button\" class=\"btn block share-to'+(x===sc.m?' primary':'')+'\" data-a=\"share-to\" data-id=\"'+x.id+'\"><span class=\"share-t\">'+esc(x.title)+'</span>'+(x===sc.m?'<span class=\"share-hint\">Looks like this one</span>':'')+'</button>'});\n  return h+'<button type=\"button\" class=\"btn block\" data-a=\"share-new\">Start a new case</button></div>';\n}\nfunction intakeAdd(d){\n  var mx=task(d.matchId),mtx=String(d.casetext||\"\");if(!mx)return;\n  if(!mtx.trim()){d.caseErr=\"There’s nothing to add yet. Paste or type what they sent.\";render();return}\n  S.composeOpen=false;\n  var mf=Object.assign({},mx.facts||{},caseFacts(mtx)),msg=intakeRead(mtx,mx,mf);\n  evidence(mx,mtx,d.src||(d.fromShare?\"a message shared from another app\":\"\"));mx._dirty=true;\n  if(msg){mx.sugP=msg;mx.sugDone=false;save();go({name:\"task\",id:mx.id})}\n  else{save();go({name:\"task\",id:mx.id});S.view.panel=\"paste\";S.draft={paste:mtx,err:\"Added to the case. Sorted couldn’t find a date in it, so nothing else changed.\"};render()}\n}\nfunction readCase(t,f){");
R("(d.matchId&&task(d.matchId)?matchBlock(",
  "(sharePicking(d)?shareBlock(d):d.matchId&&task(d.matchId)?matchBlock(");
R("Nothing is saved until you press Start.</p>'",
  "Nothing is saved until you '+(sharePicking(S.draft)?'choose where it goes':'press Start')+'.</p>'");
R("    case \"match-add\":{var mx=task(d.matchId),mtx=d.casetext||\"\";if(!mx)break;S.composeOpen=false;\n      var mf=Object.assign({},mx.facts||{},caseFacts(mtx)),msg=intakeRead(mtx,mx,mf);\n      evidence(mx,mtx,d.src||(d.fromShare?\"a message shared from another app\":\"\"));mx._dirty=true;\n      if(msg){mx.sugP=msg;mx.sugDone=false;save();go({name:\"task\",id:mx.id})}\n      else{save();go({name:\"task\",id:mx.id});S.view.panel=\"paste\";S.draft={paste:mtx,err:\"Added to the case. Sorted couldn’t find a date in it, so nothing else changed.\"};render()}\n      break}",
  "    case \"match-add\":intakeAdd(d);break;\n    case \"share-to\":{d.matchId=b.getAttribute(\"data-id\");intakeAdd(d);break}\n    case \"share-new\":{d.picked=true;d.skipMatch=true;d.matchId=null;render();var snf=$(\"#f-case\");if(snf){try{snf.focus({preventScroll:true})}catch(e){}}break}");
R("  }else{\n    if(needs.length){\n      h+='<section class=\"home44-intro\">",
  "  }else{\n    if(shareTop)h+='<div class=\"home44-compose\">'+caseEntry()+'</div>';\n    if(needs.length){\n      h+='<section class=\"home44-intro\">");
R("    if(!entryFirst){\n      h+='<div class=\"home44-compose\">'",
  "    if(!entryFirst&&!shareTop){\n      h+='<div class=\"home44-compose\">'");
R("  var active=needs.length+waiting.length,entryFirst=!active&&S.loaded;\n  if(S.tasks.length&&!needs.length&&!waiting.length)",
  "  var active=needs.length+waiting.length,entryFirst=!active&&S.loaded,shareTop=!entryFirst&&S.composeOpen&&sharePicking(S.draft);\n  if(S.tasks.length&&!needs.length&&!waiting.length)");
R(".art-share{width:220px;margin:0 auto}",
  ".art-share{width:220px;margin:0 auto}\n.share-pick{border-top:1px solid var(--rule);padding-top:14px}\n.share-to{flex-direction:column;align-items:flex-start;gap:2px;text-align:left;height:auto;min-height:52px;padding-top:10px;padding-bottom:10px}\n.share-t{overflow-wrap:anywhere}\n.share-hint{font-size:13px;font-weight:600;opacity:.85}");
fs.writeFileSync('public/index.html',s);
const EXPECT='e5d8ebef7e3cde3436ac0568e07930c0b1802e55';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v53 ok',h(s),s.length);
