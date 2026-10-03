const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='a73ef163d00fab757ecb37cc2a74173561afe6aa')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v93: a renewal typed in gets a reminder to renew, not the call form; a case with no date yet is steered to
// getting one, and the message it prepares asks for it. ----
R("go({name:\"task\",id:t.id,panel:mode===\"call\"?\"call\":null});",
  "go({name:\"task\",id:t.id,panel:mode===\"call\"&&!frRenewOnly(t)?\"call\":null});");
R("function frParty(t,p){",
  "function frRenewOnly(t){return t.mode!==\"do\"&&!t.sugP&&!t.cf&&!(t.promises||[]).length&&FR_RENEW.test(String(t.said||\"\"))}\nfunction frRenewWhat(t){var m=FR_RENEW.exec(String(t.said||\"\"));if(!m)return \"\";var k=m[1].toLowerCase().replace(/^mot$/,\"MOT\").replace(/^tv /,\"TV \");return \"Renew my \"+k}\nfunction frParty(t,p){");
R("h+='<div class=\"row eq\">'+(dl?'<button class=\"btn primary\" data-a=\"fr-remind\">Remind me before '+esc(pkDayLabel(dl.date))+'</button>':'')+'<button class=\"btn'+(dl||/^Check /.test(N)?'':' primary')+'\" data-a=\"fr-ok\">Got it</button></div>';",
  "var rno=frRenewOnly(t);h+='<div class=\"row eq\">'+(dl?'<button class=\"btn primary\" data-a=\"fr-remind\">Remind me before '+esc(pkDayLabel(dl.date))+'</button>':rno?'<button class=\"btn primary\" data-a=\"fr-renew\">Remind me to renew it</button>':'')+'<button class=\"btn'+(dl||rno||/^Check /.test(N)?'':' primary')+'\" data-a=\"fr-ok\">Got it</button></div>';");
R("N=\"Renew it on the official GOV.UK page, in good time. To get a reminder, use “Remind me to do something” below.\";",
  "N=\"Renew it on the official GOV.UK page, in good time. Sorted can remind you before it runs out.\";");
R("case \"fr-ok\":if(t){t.frNew=false;t._dirty=true;commit()}break;",
  "case \"fr-ok\":if(t){t.frNew=false;t._dirty=true;commit()}break;\n    case \"fr-renew\":if(t){var rwt=frRenewWhat(t),rwm=/\\b(?:expir\\w*|runs?\\s+out|due)\\s+(?:on\\s+|in\\s+)?(.+)$/i.exec(String(t.said||\"\").replace(/[.!]+$/,\"\"));t.frNew=false;t._dirty=true;S.view.panel=\"move\";S.draft=moveDraft(rwt+(rwm?\" by \"+rwm[1]:\"\"));S.draft.mwhat=rwt+\" before it runs out\";if(!S.draft.when)S.draft.when=\"by\";commit();var mfr=$(\"#moveform\");if(mfr)mfr.scrollIntoView({block:\"start\"})}break;");
R("else if(!pk&&!dl&&t.mode!==\"do\"&&/\\b(?:will|would|'ll|said|keep saying)\\b/i.test(said))U.push(\"They haven’t given you a date yet.\");",
  "else if(!pk&&!dl&&t.mode!==\"do\"&&FR_NODATE.test(said))U.push(\"They haven’t given you a date yet.\");");
R("  else N=frCap(String(nextStepText(t)).replace(/^Next:\\s*/,\"\"))+\".\";",
  "  else if(t.mode===\"call\"&&!p&&!pk&&FR_NODATE.test(said))N=\"Ask \"+(who||\"them\")+\" for a date\"+(/\\bengineer|\\btechnician/i.test(said)?\" for the engineer\":\"\")+\", and get it in writing if you can. When they give one, add it here and Sorted will hold them to it.\";\n  else N=frCap(String(nextStepText(t)).replace(/^Next:\\s*/,\"\"))+\".\";");
R("var FR_RENEW=",
  "var FR_NODATE=/\\b(?:will|would|'ll|said|keep saying)\\b/i;\nvar FR_RENEW=");
R("ask=\"I’m getting in touch about this: \"+lc1(t.said).replace(/[.!]+$/,\"\")+\".\"+(t.facts&&t.facts.ref?\" My reference is \"+t.facts.ref+\".\":\"\")+\" \";",
  "ask=\"I’m getting in touch about this: \"+lc1(t.said).replace(/[.!]+$/,\"\")+\".\"+(t.facts&&t.facts.ref?\" My reference is \"+t.facts.ref+\".\":\"\")+\" \"+(PDEMAND.test(t.said)?\"Can you confirm what I need to pay, by when, and how I can query it if I think it’s wrong?\":/\\bengineer|\\btechnician/i.test(t.said)?\"Please give me a date for the engineer, and confirm it in writing.\":\"Can you tell me what happens next and by when, and confirm it in writing?\");");
R("  }else if(t.mode===\"do\"&&S.view.panel!==\"call\"){\n    if(!mv)h+=doIdleCard(t);",
  "  }else if((t.mode===\"do\"||frRenewOnly(t))&&S.view.panel!==\"call\"){\n    if(!mv&&!(t.frNew&&frRenewOnly(t)))h+=doIdleCard(t);");
R("if((t.mode===\"call\"||t.mode===\"fix\")&&!pk&&D.length<2)",
  "if((t.mode===\"call\"||t.mode===\"fix\")&&!pk&&!rn&&D.length<2)");
fs.writeFileSync('public/index.html',s);
const EXPECT='a801027354df043565265a18f31d88f05a98040a';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v93 ok',h(s),s.length);
