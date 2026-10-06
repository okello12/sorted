const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='cd9670f22a3949b7f6ef30f67156bf0d20a45bde')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v140: told-date anchoring with a choice, words and dates said apart, one next action, unknown names, kept reminders, guest wording. ----
R("  var prec=\"day\",ph=\"\";function cap(re){var mm=s.match(re);return mm?mm[0].trim():\"\"}",
  "  var prec=\"day\",ph=\"\";function cap(re){var mm=s.match(re);return mm?mm[0].trim():\"\"}\n  var told=null,toldPh=\"\",alt=null,tm=DUR140.test(s)&&s.match(/\\b(?:on |that was |this was )?(?:last (monday|tuesday|wednesday|thursday|friday|saturday|sunday)|(yesterday)|(\\d+|a|one|two|three|four|five|six) days? ago)\\b/);\n  if(tm){told=new Date(base);if(tm[1]){var ti=[\"sunday\",\"monday\",\"tuesday\",\"wednesday\",\"thursday\",\"friday\",\"saturday\"].indexOf(tm[1]);told.setDate(told.getDate()-(((told.getDay()-ti+7)%7)||7))}else if(tm[2])told.setDate(told.getDate()-1);else told.setDate(told.getDate()-numw(tm[3]));toldPh=tm[0].replace(/^(?:on |that was |this was )/,\"\").trim();s=s.replace(tm[0],\" \")}\n  function addC(n){var d=new Date(told||base);d.setDate(d.getDate()+n);return d}");
R("      prec=\"calc\";ph=m[0].trim();var n=numw(m[1]);if(/week/.test(m[3]))day=add(7*n);\n      else if(m[2]){day=wdFrom(base,n)}\n      else day=add(n);",
  "      prec=\"calc\";ph=m[0].trim();var n=numw(m[1]);if(/week/.test(m[3]))day=addC(7*n);\n      else if(m[2]){day=wdFrom(told||base,n);if(told&&n>=1&&told.getDay()%6&&!UK_BH[ymdL(told)])alt=n>1?wdFrom(told,n-1):new Date(told)}\n      else{day=addC(n);if(told&&n>=1)alt=addC(n-1)}");
R("{day=m[3]?wdFrom(base,+m[2]):add(+m[2]);wstart=m[3]?wdFrom(base,+m[1]):add(+m[1]);by=true;prec=\"calc\";",
  "{day=m[3]?wdFrom(told||base,+m[2]):addC(+m[2]);wstart=m[3]?wdFrom(told||base,+m[1]):addC(+m[1]);by=true;prec=\"calc\";");
R("{day=add(+m[1]/24);by=true;prec=\"calc\";",
  "{day=addC(+m[1]/24);by=true;prec=\"calc\";");
R("  if(day<base)return null;",
  "  if(day<base&&!told)return null;");
R("  if(wstart&&!from&&wstart<day)out.wstart=ymdL(wstart);\n  return out;\n}",
  "  if(wstart&&!from&&wstart<day)out.wstart=ymdL(wstart);\n  if(told&&prec===\"calc\"){out.told=ymdL(told);var tom=new RegExp(toldPh.replace(/ /g,\"\\\\s+\"),\"i\").exec(String(text||\"\"));out.toldPh=tom?tom[0]:toldPh;if(alt&&alt<day&&!wstart)out.alt=ymdL(alt)}\n  return out;\n}");
R("function parseWhen(text,now){",
  "/* v140: a duration is counted from when they told you. \"Last Wednesday they said within five working days\" is read\n   from Wednesday, not from today, and when it isn't clear whether that day counts Sorted shows both readings and asks\n   which to use. Until the person chooses, there is no confirmed deadline. */\nvar DUR140=/\\b(?:in|within|takes?|taking|allow(?:ing)?)(?: up to)? (?:\\d+|a|an|one|two|three|four|five|six|seven|ten|fourteen)(?: ?(?:-|to|or) ?\\d+)? (?:working |business )?(?:day|days|week|weeks)\\b|\\b(?:24|48|72) ?(?:hours|hrs|h)\\b/i;\nvar TOLD_RE=/\\b(?:last (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)|yesterday|(?:\\d+|a|one|two|three|four|five|six) days? ago)\\b/i;\nfunction withTold(c,full){if(TOLD_RE.test(c)||!DUR140.test(c))return c;var m=TOLD_RE.exec(String(full||\"\"));return m?c+\" (\"+m[0]+\")\":c}\nfunction d140(y){var a=String(y||\"\").split(\"-\").map(Number);return new Date(a[0],a[1]-1,a[2])}\nfunction calcOpen(p){return !!p&&!!p.alt&&!!p.altB&&!p.dpick&&!p.chk&&p.status===\"open\"}\nfunction calcBlock(p,chips){if(!p||!p.told||!aprx(p)||p.chk)return \"\";var ph=String(p.phrase||\"\").trim(),td=d140(p.told),wk=/working|business/i.test(ph),tdn=fmtDay(td).split(\" \")[0];\n  var h='<div class=\"calc140 stack-s\"><p><strong>What they said:</strong> “'+esc(ph)+'”</p><p><strong>When you were told:</strong> '+esc(fmtDay(td))+(p.toldPh?' (“'+esc(p.toldPh)+'”)':'')+'</p>';\n  if(p.alt&&p.altB)h+='<p><strong>Sorted’s calculation:</strong> '+esc(fmtDay(d140(p.alt)))+' if '+esc(tdn)+' counts as the first day, or '+esc(fmtDay(d140(p.altB)))+' if counting starts the next '+(wk?\"working \":\"\")+'day.</p>';\n  else h+='<p><strong>Sorted’s calculation:</strong> about '+esc(whenText0(p).replace(/^By /,\"\").replace(/^Sometime between/,\"between\"))+'.</p>';\n  h+='<p><strong>Exact deadline:</strong> '+(p.dpick?esc(fmtDay(new Date(p.dueAt)))+', the day you chose':'not confirmed')+'</p>';\n  if(chips&&calcOpen(p))h+='<p class=\"h3\" id=\"calc140-q\">Which should Sorted use?</p><div class=\"chips\" role=\"group\" aria-labelledby=\"calc140-q\"><button type=\"button\" class=\"chip\" data-a=\"calc-pick\" data-v=\"alt\">'+esc(fmtDay(d140(p.alt)))+'</button><button type=\"button\" class=\"chip\" data-a=\"calc-pick\" data-v=\"day\">'+esc(fmtDay(d140(p.altB)))+'</button><button type=\"button\" class=\"chip\" data-a=\"calc-pick\" data-v=\"unsure\">I’m not sure</button></div><p class=\"muted\" style=\"font-size:16px\">Until you choose, Sorted waits until the later day, '+esc(fmtDay(new Date(p.dueAt)))+', before asking you.</p>';\n  return h+'</div>'}\nfunction parseWhen(text,now){");
R("  var told=null,toldPh=\"\",alt=null,tm=",
  "  s=s.replace(/\\b(will|would|should|'ll|'d|to) (?:take|allow)(?: up to)? (?=(?:\\d+|a|an|one|two|three|four|five|six|seven|ten|fourteen)(?: ?(?:-|to|or) ?\\d+)? (?:working |business )?(?:day|days|week|weeks)\\b)/g,\"$1 within \");\n  var told=null,toldPh=\"\",alt=null,tm=");
R("  if(told&&prec===\"calc\"){out.told=",
  "  if(out.phrase===ph&&/^within /.test(ph)){var pm2=new RegExp(\"\\\\b(?:takes?|taking|allow(?:ing)?)(?:\\\\s+up\\\\s+to)?\\\\s+\"+ph.slice(7).replace(/[.*+?^${}()|[\\]\\\\]/g,\"\\\\$&\").replace(/ /g,\"\\\\s+\"),\"i\").exec(String(text||\"\").replace(/[–—]/g,\"-\"));if(pm2)out.phrase=pm2[0]}\n  if(told&&prec===\"calc\"){out.told=");
R("var w=parseWhen(q,t&&PCHG.test(pt)",
  "var w=parseWhen(withTold(q,TOLD_SENT.test(raw)?raw:\"\"),t&&PCHG.test(pt)");
R("function withTold(c,full){",
  "var TOLD_SENT=/\\b(?:that|this|it) was (?:on )?(?:last (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)|yesterday|(?:\\d+|a|one|two|three|four|five|six) days? ago)\\b|\\b(?:told|said|emailed|messaged|texted|called|rang|wrote)(?: to)?(?: me| us)? (?:on )?(?:last (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)|yesterday|(?:\\d+|a|one|two|three|four|five|six) days? ago)\\b/i;\nfunction withTold(c,full){");
R("  c=String(c||\"\").replace(/\\byesterday\\b/gi,",
  "  c=DUR140.test(String(c||\"\"))?String(c||\"\"):String(c||\"\").replace(/\\byesterday\\b/gi,");
R("(sp.fromMsg?\". Taken from their message, and confirmed.\":\". Taken from what you wrote, and confirmed.\")",
  "(aprx(spr)?(sp.fromMsg&&!sp.typed?\". The words are from their message\":\". The words are from what you wrote\")+\"; the date is Sorted’s working, not a day they gave. You said yes to it.\":sp.fromMsg&&!sp.typed?\". Taken from their message, and confirmed.\":\". Taken from what you wrote, and confirmed.\")");
R("    var ago=elapsedDays(s);base=ago?addDays(today,-ago):new Date();w=parseWhen(clause,base);",
  "    var ctold=withTold(clause,s),ago=TOLD_RE.test(ctold)?0:elapsedDays(s);base=ago?addDays(today,-ago):new Date();w=parseWhen(ctold,base);");
R("  pr.prec=w.prec||\"day\";if(w.phrase)pr.phrase=w.phrase;",
  "  pr.prec=w.prec||\"day\";if(w.phrase)pr.phrase=w.phrase;if(w.told){pr.told=w.told;pr.toldPh=w.toldPh;if(w.alt){pr.alt=w.alt;pr.altB=w.date}}");
R("pr.prec=bw.prec||\"day\";if(bw.phrase)pr.phrase=bw.phrase;",
  "pr.prec=bw.prec||\"day\";if(bw.phrase)pr.phrase=bw.phrase;if(bw.told){pr.told=bw.told;pr.toldPh=bw.toldPh;if(bw.alt){pr.alt=bw.alt;pr.altB=bw.date}}");
R("if(sp.phrase)spr.phrase=sp.phrase;",
  "if(sp.phrase)spr.phrase=sp.phrase;if(sp.told){spr.told=sp.told;spr.toldPh=sp.toldPh;if(sp.alt){spr.alt=sp.alt;spr.altB=sp.altB}}");
R("delete p.chk;t.board=\"waiting\"",
  "delete p.chk;delete p.told;delete p.toldPh;delete p.alt;delete p.altB;delete p.dpick;t.board=\"waiting\"");
R("  if(p.chk)return (ph?cap1(ph):\"No day given\")+\"; you’ll check on \"+fmtDay(new Date(p.dueAt));",
  "  if(p.chk)return (ph?cap1(ph):\"No day given\")+\"; you’ll check on \"+fmtDay(new Date(p.dueAt));\n  if(p.told&&ph){if(p.dpick)return cap1(ph)+\" (you chose \"+fmtDay(new Date(p.dueAt))+\")\";if(p.alt&&p.altB)return cap1(ph)+\", told \"+fmtDay(d140(p.told))+\" (Sorted’s working: \"+fmtDay(d140(p.alt))+\" or \"+fmtDay(d140(p.altB))+\")\"}");
R("function aprxLine(p){if(!aprx(p))return \"\";",
  "function aprxLine(p){if(!aprx(p))return \"\";if(p.told&&!p.chk)return calcBlock(p,false);");
R("h+=aprxLine(p)+'<button class=\"link\" data-a=\"panel\" data-p=\"chk138\" style=\"text-align:left\">Choose when to check</button>';",
  "h+=(p.told&&!p.chk?calcBlock(p,true):aprxLine(p))+(calcOpen(p)?'':'<button class=\"link\" data-a=\"panel\" data-p=\"chk138\" style=\"text-align:left\">Choose when to check</button>');");
R("h+='<p>'+esc(p.by||p.allDay?\"Due by the end of \"",
  "h+='<p>'+esc(calcOpen(p)?\"No exact deadline yet. Say which day Sorted should use, below.\":p.by||p.allDay?\"Due by the end of \"");
R("function pw137(p){",
  "function pw137(p){if(p&&p.told&&aprx(p)&&!p.chk&&p.phrase)return \"“\"+p.phrase+\"”, \"+(p.dpick?\"and you chose \"+fmtDay(new Date(p.dueAt)):\"told on \"+fmtDay(d140(p.told))+\"; the exact day isn’t confirmed\");");
R("function sugMsgLine(p){return p.fromMsg?'<p class=\"muted\" style=\"font-size:16px\">'+(p.typed?\"Sorted picked this date out of what you wrote.\":\"Found in the message you pasted.\")+' Check the date before you say yes.</p>':''}",
  "function sugMsgLine(p){if(!p.fromMsg)return \"\";var w=aprx(p)?(p.typed?\"The words are yours. The date is Sorted’s working from them, not a day anyone gave you.\":\"The words are from the message you pasted. The date is Sorted’s working, not a day they gave.\"):(p.typed?\"Sorted picked this date out of what you wrote.\":\"Found in the message you pasted.\");return '<p class=\"muted\" style=\"font-size:16px\">'+w+' Check the date before you say yes.</p>'}");
R("  if(t.sugP&&!t.sugDone)return \"Next: check what they promised\";",
  "  if(t.sugP&&!t.sugDone)return \"Next: check what they promised\";\n  var mv140=openMove(t);if(mv140&&mv140.what&&!(mv140.src===\"parking\"&&pkOn(t)))return \"Next: \"+lc1(String(mv140.what).replace(/[.!]+$/,\"\"));\n  var op140=openPromise(t);if(op140&&calcOpen(op140))return \"Next: say which day Sorted should use\";\n  if(appCue(t)&&!(op140&&op140.dueAt))return \"Next: check \"+appWho(t)+\" app or website for an update\";");
R("  else if(p&&(s===\"waiting\"||s===\"waitdue\")){lab=\"Waiting for \"",
  "  else if(p&&calcOpen(p))tx=\"say which day Sorted should use for “\"+p.phrase+\"”\";\n  else if(p&&(s===\"waiting\"||s===\"waitdue\")){lab=\"Waiting for \"");
R("(p.chk?\"you chose to check on \"+fmtDay(new Date(p.dueAt)):\"no day given",
  "(p.chk?\"you chose to check on \"+fmtDay(new Date(p.dueAt)):p.dpick?\"by \"+fmtDay(new Date(p.dueAt))+\", the day you chose\":\"no day given");
R("    case \"chk-app\":if(t){",
  "    case \"calc-pick\":if(t){var cq=openPromise(t),cv=b.getAttribute(\"data-v\");if(!cq||!calcOpen(cq))break;\n      if(cv===\"unsure\"){S.view.panel=\"chk138\";S.draft={chkday:cq.altB};render();var cf=$(\"#f-chkday\");if(cf)try{cf.focus()}catch(e){}break}\n      var cd=cv===\"alt\"?cq.alt:cq.altB,cdd=d140(cd);cq.dueAt=cdd.toISOString();cq.dueEnd=null;cq.allDay=true;cq.by=true;cq.dpick=cv;\n      log(t,\"You chose \"+fmtDay(cdd)+\" as the day for “\"+String(cq.phrase||\"\").replace(/[.!]+$/,\"\")+\"”. Sorted had worked out \"+fmtDay(d140(cq.alt))+\" or \"+fmtDay(d140(cq.altB))+\".\");\n      try{sb.from(\"reminders\").delete().eq(\"task_id\",t.id).is(\"sent_at\",null).then(function(){scheduleEmail(t)},function(){})}catch(e){}\n      t._dirty=true;save();render();toast(\"Sorted will use \"+fmtDay(cdd)+\".\")}break;\n    case \"chk-app\":if(t){");
R("    if(gk2!==\"fix\"&&!gv.who){d.caseErr=\"Say who it is",
  "    var gunk=gk2!==\"fix\"&&UNK_WHO.test(gv.who);if(gunk)gv.who=\"\";\n    if(gk2!==\"fix\"&&!gv.who&&!gunk){d.caseErr=\"Say who it is");
R("  if(k===\"promise\"){if(!what||",
  "  if(k===\"promise\"){var w140=what.replace(/^(?:they|he|she|it|we)\\s+(?:said|told me|told us|promised)\\s+(?:that\\s+)?/i,\"\"),s140=w140!==what&&w140.length>3;if(!what||");
R("return \"Waiting for \"+T(who)+\".\";return T(who)+\" said they would \"+what+\".\";}",
  "return who?\"Waiting for \"+T(who)+\".\":\"Waiting for them.\";return (who?T(who):\"They\")+\" said \"+(s140?w140:\"they would \"+what)+\".\";}");
R("  if(k===\"chase\")return T(what)+\" from \"+who+\" still hasn’t happened.\";",
  "  if(k===\"chase\")return T(what)+(who?\" from \"+who:\"\")+\" still hasn’t happened.\";");
R("  if(k===\"call\")return \"Call \"+who+\" about \"+what+\".\";",
  "  if(k===\"call\")return \"Call \"+(who||\"them\")+\" about \"+what+\".\";");
R("function giText(k,v){",
  "/* v140: \"Shop name not in front of me\" is not a name. The case keeps the company unknown and asks for it later. */\nvar UNK_WHO=/^(?:the )?(?:shop|company|their|the)?\\s*(?:name\\s+)?(?:not (?:in front of me|sure|known|to hand)|don'?t know|do not know|dunno|can'?t remember|cannot remember|no idea|unknown|forgot(?:ten)?|n\\/?a|\\?+|someone|somebody)\\b|\\b(?:not in front of me|can'?t remember|cannot remember|don'?t know (?:the |their )?name|do not know (?:the |their )?name|no idea (?:of )?(?:the |their )?name|forgot(?:ten)? (?:the |their )?name|not to hand)\\b/i;\nfunction giText(k,v){");
R("function goHome(){\n  S.draft={};",
  "function goHome(){\n  formKeepSnap({name:\"home\"});S.draft={};");
R("  keepAll()[v.id]={panel:v.panel,draft:JSON.parse(JSON.stringify(S.draft||{})),words:w.slice(0,90),at:Date.now()};keepWrite();",
  "  keepAll()[v.id]={panel:v.panel,draft:JSON.parse(JSON.stringify(S.draft||{})),words:w.slice(0,90),at:Date.now()};keepWrite();\n  if(nextView&&(nextView.name!==\"task\"||nextView.id!==v.id))setTimeout(function(){toast(\"Kept what you were writing. Open the case to carry on.\")},60);");
R("  return t.rev?\"Saved to your account\":\"\";",
  "  return t.rev?(S.user.email?\"Saved to your account\":\"Saved to Sorted. You can reopen this case on this browser. Add an email to open it on another device.\"):\"\";");
R("if(!n)return \"Everything is saved to your account.\";",
  "if(!n)return S.user.email?\"Everything is saved to your account.\":\"Everything is saved to Sorted. Add an email to open your cases on another device.\";");
R("</style>\n</head>",
  "</style>\n<style>\n/* v140 */\n.calc140{border-left:3px solid var(--yellow-edge);padding-left:12px}\n.calc140 p{margin:0}\n</style>\n</head>");
R("SORTED_V=\"v139\"",
  "SORTED_V=\"v140\"");
fs.writeFileSync('public/index.html',s);
const EXPECT='7168e65628c9ee1253a1cbdf4ebf2e244c7f87f8';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v140 ok',h(s),s.length);
