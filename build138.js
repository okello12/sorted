const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='324b294808e1ce02adf34635426bbfddb76b661f')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v138: the date model (precision, their words, your check day), a legacy flag, Check the app, the notice line only on notices. ----
R("var wdName=false,day=null,by=false,wstart=null,m,T=",
  "var prec=\"day\",ph=\"\";function cap(re){var mm=s.match(re);return mm?mm[0].trim():\"\"}\n  var wdName=false,day=null,by=false,wstart=null,m,T=");
R("    else if((m=s.match(/\\b(next |this |on |by |until )?(monday",
  "    else if((m=s.match(/\\b(?:on |by )?(mon|tue|wed|thu|fri|sat|sun)[a-z]* or (mon|tue|wed|thu|fri|sat|sun)[a-z]*\\b/))){var DW=[\"sun\",\"mon\",\"tue\",\"wed\",\"thu\",\"fri\",\"sat\"];wstart=nextWd(DW.indexOf(m[1]));day=nextWd(DW.indexOf(m[2]));if(day<wstart)day.setDate(day.getDate()+7);by=true;prec=\"window\";ph=m[0].trim()}\n    else if((m=s.match(/\\b(next |this |on |by |until )?(monday");
R("else if(/\\b(this |the |at the )?weekend\\b/.test(s))day=nextWd(6);",
  "else if(/\\b(this |the |at the )?weekend\\b/.test(s)){day=nextWd(6);prec=\"approx\";ph=cap(/\\b(?:by |over |at |for |before )?(?:this |the |at the )?weekend\\b/)}");
R("      var n=numw(m[1]);",
  "      prec=\"calc\";ph=m[0].trim();var n=numw(m[1]);");
R("{day=m[3]?wdFrom(base,+m[2]):add(+m[2]);wstart=m[3]?wdFrom(base,+m[1]):add(+m[1]);by=true}",
  "{day=m[3]?wdFrom(base,+m[2]):add(+m[2]);wstart=m[3]?wdFrom(base,+m[1]):add(+m[1]);by=true;prec=\"calc\";ph=m[0].trim()}");
R("{wstart=add(1);day=add(/\\bcouple\\b|\\bday or two\\b/.test(s)?2:3);by=true}",
  "{wstart=add(1);day=add(/\\bcouple\\b|\\bday or two\\b/.test(s)?2:3);by=true;prec=\"approx\";ph=cap(/\\b(?:(?:in|over|within) )?(?:the )?(?:next (?:few|couple of) days|a (?:few|couple of) days|a day or two)\\b/)}");
R("{wstart=/\\blater\\b/.test(s)?add(1):base;day=nextWd(5);if(day<wstart)day=wstart;by=true}",
  "{wstart=/\\blater\\b/.test(s)?add(1):base;day=nextWd(5);if(day<wstart)day=wstart;by=true;prec=\"window\";ph=cap(/\\b(?:sometime |later |some point )?(?:this|the coming) week\\b/)}");
R("{var enw=base.getDay();wstart=add(((1-enw+7)%7)||7);day=new Date(wstart);day.setDate(day.getDate()+2);by=true}",
  "{var enw=base.getDay();wstart=add(((1-enw+7)%7)||7);day=new Date(wstart);day.setDate(day.getDate()+2);by=true;prec=\"approx\";ph=\"early next week\"}");
R("{day=add(+m[1]/24);by=true}",
  "{day=add(+m[1]/24);by=true;prec=\"calc\";ph=cap(/\\b(?:(?:in|within) )?(?:24|48|72) ?(?:hours|hrs|h)\\b/)}");
R("{day=nextWd(5);by=true}",
  "{day=nextWd(5);by=true;prec=\"approx\";ph=cap(/\\b(?:by |before )?(?:the )?end of (?:the |this )?week\\b/)}");
R("{wstart.setDate(wstart.getDate()+2)}by=true}",
  "{wstart.setDate(wstart.getDate()+2);prec=\"approx\"}by=true;if(prec===\"day\")prec=\"window\";ph=cap(/\\b(?:(?:by|during|sometime|later|late|the end of|end of) )*next week\\b/)}");
R("{day=new Date(base.getFullYear(),base.getMonth()+1,0);by=true}",
  "{day=new Date(base.getFullYear(),base.getMonth()+1,0);by=true;prec=\"approx\";ph=cap(/\\b(?:by |before )?(?:the )?end of (?:the |this )?month\\b/)}");
R("var out={when:from?\"slot\":(by?\"by\":\"slot\"),date:ymdL(day),from:from||\"\",to:to||\"\",label:label};",
  "var out={when:from?\"slot\":(by?\"by\":\"slot\"),date:ymdL(day),from:from||\"\",to:to||\"\",label:label,prec:prec};if(ph){var om=new RegExp(ph.replace(/[.*+?^${}()|[\\]\\\\]/g,\"\\\\$&\").replace(/ /g,\"\\\\s+\"),\"i\").exec(String(text||\"\").replace(/[’‘]/g,\"'\").replace(/[–—]/g,\"-\"));out.phrase=om?om[0]:ph}");
R("  var last=end?new Date(end):new Date(start.getTime()+(allDay?DAY:HOUR));\n  pr.past=last<new Date();",
  "  pr.prec=w.prec||\"day\";if(w.phrase)pr.phrase=w.phrase;\n  var last=end?new Date(end):new Date(start.getTime()+(allDay?DAY:HOUR));\n  pr.past=last<new Date();");
R("fromMsg:true};",
  "fromMsg:true};pr.prec=bw.prec||\"day\";if(bw.phrase)pr.phrase=bw.phrase;");
R("return {dueAt:start.toISOString(),dueEnd:end,allDay:!w.from,by:w.when===\"by\"&&!win,win:win}}",
  "return {dueAt:start.toISOString(),dueEnd:end,allDay:!w.from,by:w.when===\"by\"&&!win,win:win,prec:w.prec||\"day\",phrase:w.phrase||\"\"}}");
R("win:!!c.win,loggedAt:at});delete np.closedAt;",
  "win:!!c.win,loggedAt:at,prec:c.prec||\"day\",phrase:c.phrase||\"\"});delete np.closedAt;delete np.chk;if(!np.phrase)delete np.phrase;");
R("else if(p){p.dueAt=c.dueAt;p.dueEnd=c.dueEnd;p.allDay=c.allDay;p.by=c.by;p.win=!!c.win;",
  "else if(p){p.dueAt=c.dueAt;p.dueEnd=c.dueEnd;p.allDay=c.allDay;p.by=c.by;p.win=!!c.win;p.prec=c.prec||\"day\";if(c.phrase)p.phrase=c.phrase;else delete p.phrase;delete p.chk;");
R("if(sp.win)spr.win=true;",
  "if(sp.win)spr.win=true;spr.prec=sp.prec||\"day\";if(sp.phrase)spr.phrase=sp.phrase;");
R("ref:letterRef(t),status:\"open\",loggedAt:nowIso()}",
  "ref:letterRef(t),status:\"open\",loggedAt:nowIso(),prec:\"calc\"}");
R("status:\"open\",loggedAt:nowIso(),src:\"parking\"});",
  "status:\"open\",loggedAt:nowIso(),src:\"parking\",prec:\"notice\"});",2);
R("var pr={id:uid(),said:said,party:party,dueAt:dueAt,dueEnd:end,allDay:allDay,by:when===\"by\",ref:ref,status:\"open\",loggedAt:nowIso()};if(spoke)pr.spoke=spoke;",
  "var pr={id:uid(),said:said,party:party,dueAt:dueAt,dueEnd:end,allDay:allDay,by:when===\"by\",ref:ref,status:\"open\",loggedAt:nowIso(),prec:dueAt?\"day\":\"none\"};if(spoke)pr.spoke=spoke;");
R("function whenText(p){\n  var w=window_(p);\n  if(!w)return \"No date given\";",
  "/* v138 (the date model). A promise's date carries how precise it is (prec: day, window, approx, calc, none, notice),\n   their words for it (phrase) and, when they gave no day, whether the day is the person's own check day (chk). A\n   reading or a calculation never shows as a firm day: their words come first, Sorted's reading second, marked \"about\". */\nfunction aprx(p){return !!p&&(p.prec===\"approx\"||p.prec===\"calc\")}\nfunction whenText(p){var b=whenText0(p);if(!aprx(p))return b;var ph=String(p.phrase||\"\").trim();\n  if(p.chk)return (ph?cap1(ph):\"No day given\")+\"; you’ll check on \"+fmtDay(new Date(p.dueAt));\n  var inner=b.replace(/^By /,\"\").replace(/^Sometime between/,\"between\");\n  return ph?cap1(ph)+\" (\"+(/^between/.test(inner)?\"\":\"about \")+inner+\")\":b+\" (Sorted’s reading)\"}\nfunction aprxLine(p){if(!aprx(p))return \"\";var ph=String(p.phrase||\"\").trim(),rd=whenText0(p).replace(/^By /,\"\").replace(/^Sometime between/,\"between\");\n  if(p.chk)return '<p class=\"aprx138\">They didn’t give a day. They said “'+esc(ph)+'”. You chose to check on '+esc(fmtDay(new Date(p.dueAt)))+'.</p>';\n  return '<p class=\"aprx138\">'+(p.prec===\"calc\"?'Sorted worked this out'+(ph?' from “'+esc(ph)+'”':'')+': '+(/^between/.test(rd)?'':'about ')+esc(rd)+'. It isn’t a day they gave.':'They didn’t give a day. Sorted reads “'+esc(ph)+'” as '+(/^between/.test(rd)?'':'about ')+esc(rd)+'. That isn’t confirmed.')+' Sorted asks you then, and you can choose a different day to check.</p>'}\nfunction aprxCard(t,p){var h=\"\";\n  if(!p.prec&&p.src!==\"parking\")h+='<p class=\"muted leg138\">Saved before Sorted recorded where each date came from. Check this is the date they gave you.</p>';\n  if(aprx(p)&&p.status===\"open\"&&!t.example)h+=aprxLine(p)+'<button class=\"link\" data-a=\"panel\" data-p=\"chk138\" style=\"text-align:left\">Choose when to check</button>';\n  return h}\nfunction chkForm(t){var p=openPromise(t),d=S.draft,v=d.chkday||(p&&p.dueAt?ymdL(new Date(p.dueAt)):\"\");if(!p)return \"\";\n  return '<section class=\"sheet stack-s chk138\" aria-labelledby=\"chkh\"><p class=\"eyebrow\">Your check day</p><h2 class=\"h2\" id=\"chkh\">When do you want to check?</h2><p>They said “'+esc(p.phrase||p.said||\"\")+'”. That isn’t a confirmed day, so the day Sorted asks you is your choice. Their words stay as they are.</p><form class=\"stack-s\" data-f=\"chk138\"><label class=\"f\"><span class=\"h3\">Check on</span><input type=\"date\" id=\"f-chkday\" name=\"chkday\" min=\"'+pkToday()+'\" value=\"'+esc(v)+'\"></label>'+(d.err?'<p class=\"err\" role=\"alert\">'+esc(d.err)+'</p>':'')+'<button class=\"btn primary block\" type=\"submit\">Save my check day</button><button class=\"btn block\" type=\"button\" data-a=\"panel\" data-p=\"\">Cancel</button></form></section>'}\nfunction whenText0(p){\n  var w=window_(p);\n  if(!w)return \"No date given\";");
R("h+='<p class=\"mono\">'+esc(cap1(wt))+(p.ref?\" · ref \"+esc(p.ref):\"\")+'</p>';",
  "h+='<p class=\"mono\">'+esc(cap1(wt))+(p.ref?\" · ref \"+esc(p.ref):\"\")+'</p>'+aprxLine(p);");
R("  if(p.src!==\"parking\"&&!t.example)h+='<button class=\"link p-cancel\" data-a=\"p-cancel\">",
  "  h+=aprxCard(t,p);\n  if(p.src!==\"parking\"&&!t.example)h+='<button class=\"link p-cancel\" data-a=\"p-cancel\">");
R("  else if(S.view.panel===\"summary137\"){h+=sum137Panel(t)}",
  "  else if(S.view.panel===\"summary137\"){h+=sum137Panel(t)}\n  else if(S.view.panel===\"chk138\"&&s!==\"done\"&&openPromise(t)){h+=chkForm(t)}");
R("  if(k===\"helpask\"&&t){",
  "  if(k===\"chk138\"&&t){\n    var cp=openPromise(t),cv=String(($(\"#f-chkday\")||{}).value||\"\");d.chkday=cv;d.err=\"\";\n    if(!cp){S.view.panel=null;render();return}\n    if(!cv||cv<pkToday()){d.err=\"Choose today or a later day.\";render();return}\n    var cy=cv.split(\"-\").map(Number);cp.dueAt=new Date(cy[0],cy[1]-1,cy[2]).toISOString();cp.dueEnd=null;cp.allDay=true;cp.by=true;cp.win=false;cp.chk=true;if(!aprx(cp)){cp.prec=\"approx\";cp.phrase=cp.phrase||\"no day given\"}\n    log(t,\"You chose to check on \"+fmtDay(new Date(cp.dueAt))+\". They didn’t give a day: “\"+String(cp.phrase||\"\").replace(/[.!]+$/,\"\")+\"”.\");\n    try{sb.from(\"reminders\").delete().eq(\"task_id\",t.id).is(\"sent_at\",null).then(function(){scheduleEmail(t)},function(){})}catch(e){}\n    t._dirty=true;S.view.panel=null;S.draft={};save();render();toast(\"Sorted will ask you on \"+fmtDay(new Date(cp.dueAt))+\". Their words stay as they are.\");return;\n  }\n  if(k===\"helpask\"&&t){");
R("function pw137(p){var w=window_(p);",
  "function pw137(p){if(aprx(p)&&p.phrase)return \"“\"+p.phrase+\"”, no day given\"+(p.chk?\" (you chose to check on \"+fmtDay(new Date(p.dueAt))+\")\":\"\");var w=window_(p);");
R("+(ph===\"check\"?\" That time has passed.\":\"\")}",
  "+(ph===\"check\"?(aprx(p)?(p.chk?\" The day you chose to check has come.\":\" The day Sorted read has passed.\"):\" That time has passed.\"):\"\")}");
R("lab=\"Waiting for \"+(p.party||\"them\");tx=phase(p)===\"later\"?",
  "lab=\"Waiting for \"+(p.party||\"them\");tx=aprx(p)&&p.phrase?(p.chk?\"you chose to check on \"+fmtDay(new Date(p.dueAt)):\"no day given, they said “\"+p.phrase+\"”\"):phase(p)===\"later\"?");
R("function now137(t,s){",
  "var APPCUE=/\\b(?:check|track|see|follow|look at|keep an eye on)\\b[^.!?\\n]{0,30}\\b(?:app|website|online account|tracking(?: page| link)?|portal)\\b|\\b(?:in|on|via|through) (?:the|our|their|your|my) (?:app|website|online account|portal)\\b|\\btracking (?:link|page|number)\\b/i;\nfunction appCue(t){if(!t||t.board===\"done\"||openMove(t))return false;var x=[t.said||\"\"].concat((t.events||[]).slice(-4).map(function(e){return e.label||\"\"})).join(\" \\n \");return APPCUE.test(x)}\nfunction appWho(t){var p=openPromise(t)||recentMiss(t),w=(p&&p.party)||(t.facts&&t.facts.party)||(t.call&&t.call.who)||\"\";return w?w+\"’s\":\"their\"}\nfunction now137(t,s){");
R("  else if(p&&phase(p)===\"check\")tx=\"tell Sorted whether \"",
  "  else if(appCue(t)&&!(p&&p.dueAt))tx=\"check \"+appWho(t)+\" app or website for an update\";\n  else if(p&&phase(p)===\"check\")tx=\"tell Sorted whether \"");
R("  return '<div class=\"q130-line now137-links\"><button class=\"btn quiet now137-add\" data-a=\"panel\" data-p=\"paste\">Add what they just said</button>",
  "  return '<div class=\"q130-line now137-links\">'+(appCue(t)?'<button class=\"btn quiet now137-add now138-app\" data-a=\"chk-app\">I’ve checked their app</button>':'')+'<button class=\"btn quiet now137-add\" data-a=\"panel\" data-p=\"paste\">Add what they just said</button>");
R("    case \"sc-own\":if(t){S.view.panel=\"paste\";S.view.pasteOwn=true;",
  "    case \"chk-app\":if(t){S.view.panel=\"paste\";S.view.pasteOwn=false;S.view.pasteApp=true;S.view.copyText=null;S.draft={};render();var ca=$(\"#f-paste\");if(ca)try{ca.focus()}catch(e){}}break;\n    case \"sc-own\":if(t){S.view.panel=\"paste\";S.view.pasteOwn=true;S.view.pasteApp=false;");
R("S.view.pasteOwn=false;S.draft={};var fk125",
  "S.view.pasteOwn=false;S.view.pasteApp=false;S.draft={};var fk125");
R("(S.view.pasteOwn?'Something changed':'Their latest message')",
  "(S.view.pasteApp?'Their app or website':S.view.pasteOwn?'Something changed':'Their latest message')");
R("(S.view.pasteOwn?'What’s changed?':'Paste what they sent')",
  "(S.view.pasteApp?'What does it say now?':S.view.pasteOwn?'What’s changed?':'Paste what they sent')");
R("(S.view.pasteOwn?'Say it in your own words",
  "(S.view.pasteApp?'Copy the update, or add a screenshot of it. Sorted looks for a date or a change, and asks you before it changes anything.':S.view.pasteOwn?'Say it in your own words");
R("  L.push(\"\");L.push(PACK_FOOT);",
  "  L.push(\"\");L.push(packFoot(t));");
R("'<p class=\"cf-src\">'+esc(PACK_FOOT)+'</p></div></div>';",
  "'<p class=\"cf-src\">'+esc(packFoot(t))+'</p></div></div>';");
R("function packText(t){",
  "function packFoot(t){return ((pkOn(t)||t.cf)?PACK_FOOT:\"Sorted doesn’t give legal advice.\")+((t.promises||[]).some(aprx)?\" Where they gave no day, their words come first and the date marked “about” is Sorted’s reading.\":\"\")}\nfunction packText(t){");
R("var SORTED_V=\"v137\"",
  "var SORTED_V=\"v138\"");
R("function corrDayWords(iso){",
  "function corrBase(x,iso){var n=new Date();if(!iso||!/\\b(?:mon|tue|wed|thu|fri|sat|sun)[a-z]*\\b/i.test(x)||/\\bnext\\b|\\d{1,2}(?:st|nd|rd|th)?\\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)|\\d{1,2}\\/\\d{1,2}/i.test(x))return n;var d=new Date(iso);d.setHours(0,0,0,0);d.setDate(d.getDate()-((d.getDay()+6)%7));return d>n?d:n}\nfunction corrDayWords(iso){");
R("rawN=pNorm(raw),w=parseWhen(rawN,new Date());",
  "rawN=pNorm(raw),w=parseWhen(rawN,corrBase(rawN,cur.dueAt));");
R("var q=pNorm(pChanged(pt.replace(/\\b(?:please )?allow (?:up to )?/i,\"in \")));var w=parseWhen(q,today);",
  "var q=pNorm(pChanged(pt.replace(/\\b(?:please )?allow (?:up to )?/i,\"in \")));var w=parseWhen(q,t&&PCHG.test(pt)&&openPromise(t)?corrBase(q,openPromise(t).dueAt):today);");
R("  var last=end?new Date(end):new Date(start.getTime()+(allDay?DAY:HOUR));\n  pr.past=last<new Date();",
  "  var last=end?new Date(end):new Date(start.getTime()+(allDay?DAY:HOUR));\n  pr.past=last<new Date()||(missedWords&&start<=new Date());");
R("</style>\n</head>",
  "</style>\n<style>\n/* v138 */\n.aprx138{margin:0;font-size:16px;line-height:1.45}\n.leg138{margin:0;font-size:15px}\n.chk138 input[type=date]{min-height:48px}\n</style>\n</head>");
fs.writeFileSync('public/index.html',s);
const EXPECT='445f0632d2a28fa9120909ff01922217fe4ff675';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v138 ok',h(s),s.length);
