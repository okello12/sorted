const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='911a1f0bacdf3bf1b5bf2216149f651feac5f2d2')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v102: what people said survives. Typos and shorthand (typoFix), a thing ruled out isn't the thing (notMention),
// the thing named in more shapes (THING_MORE), "no smoke or burning smell" is not danger (DANGER_NO), a hot plug is,
// "said they would but didn't" is a missed promise, a known thing gets its own question, a screen asks which one. ----
R("function caseFacts(text){\n  var s=String(text||\"\"),",
  "\nfunction caseFacts(text){\n  text=typoFix(text);var s=String(text||\"\"),");
R("  for(i=0;i<ITEMS.length;i++)if(ITEMS[i][0].test(s)){f.item=ITEMS[i][1];break}",
  "  var sItem=notMention(s);for(i=0;i<ITEMS.length;i++)if(ITEMS[i][0].test(sItem)){f.item=ITEMS[i][1];break}");
R("function looksUnsafe(){for(var i=0;i<arguments.length;i++){if(arguments[i]&&DANGER.test(arguments[i]))return true}return false}",
  "var DANGER_NO=/\\b(?:no|not any|without|isn't any|isn’t any|there'?s no|there’s no|there is no|no sign of|nothing)\\s+(?:(?:obvious|visible|real)\\s+)?(?:smoke|smoking|burning|burnt|burn|sparks?|sparking|fire|flames?|smell(?:s)?(?: of gas| of burning)?|gas smell|melting)(?:\\s*(?:,|or|and|nor)\\s*(?:any\\s+)?(?:smoke|smoking|burning|burnt|sparks?|sparking|fire|flames?|smell(?:s)?|gas smell)(?:\\s+smell)?)*(?:\\s+smell)?/gi;\nvar DANGER_HOT=/\\bhot (?:plug|socket)|\\b(?:plug|socket) (?:is |feels |was |gets )?(?:hot|warm|melted)\\b/i;\nfunction looksUnsafe(){for(var i=0;i<arguments.length;i++){var a=arguments[i];if(!a)continue;var x=String(a).replace(DANGER_NO,\" \");if(DANGER.test(x)||DANGER_HOT.test(x))return true}return false}");
R("var PMISS=/\\b(?:didn.?t|did not|never) (?:come|turn up",
  "var PMISS=/\\bbut (?:they |he |she |it |nobody |no one )?(?:(?:didn.?t|did not|never)\\b(?!\\s+(?:say|said|mention|tell|ask|want|need|know|give|confirm|book|agree))|(?:hasn.?t|haven.?t)\\s+(?:come|turned up|shown up|showed up|arrived|happened|called|rung|paid|refunded|delivered|been|fixed|sent)\\b)|\\b(?:didn.?t|did not|never) (?:come|turn up");
R("function readCase(t,f){if(PDEMAND.test(t))return null;",
  "function readCase(t,f){t=typoFix(t);if(PDEMAND.test(t))return null;");
R("function thingOf(x){var m=THING_RE.exec(String(x||\"\").replace(/[’‘]/g,\"'\"));if(!m)return \"\";",
  "var THING_MORE=[/^\\s*(?:my\\s+|the\\s+|our\\s+)?([a-z]+(?:\\s+[a-z]+)?)\\s*(?:'s|is|are|has)?\\s+(?:broken|broke|cracked|smashed|gone|dead|leaking|faulty|not working|stopped working|no longer works|keeps? breaking|packed up)\\b/i,/\\b(?:cracked|broke|smashed|dropped|damaged|snapped)\\s+(?:my|the|our)\\s+([a-z]+(?:\\s+[a-z]+)?)/i,/\\bproblem with (?:my|the|our)\\s+([a-z]+(?:\\s+[a-z]+)?)/i,/\\b([a-z]+)\\s+(?:no longer works|stopped working)\\b/i];\nvar THING_FILL=/^(?:it|this|that|everything|something|nothing|phone call|call|yesterday|today|now|still|just|again)$/i;\nfunction thingOf(x){x=notMention(typoFix(String(x||\"\").replace(/[’‘]/g,\"'\")));var m=THING_RE.exec(x);if(!m){for(var ti=0;ti<THING_MORE.length&&!m;ti++){var mm=THING_MORE[ti].exec(x);if(mm&&!THING_FILL.test(mm[1].trim()))m=mm}}if(!m)return \"\";");
R("<form class=\"stack\" data-f=\"what\"><h2 class=\"h2\">What is it, and what’s it doing?</h2>",
  "<form class=\"stack\" data-f=\"what\"><h2 class=\"h2\">'+(item&&item!==\"Washing machine\"?\"What’s happening with the \"+esc(itemSay(item))+\"?\":\"What is it, and what’s it doing?\")+'</h2>'+(/^(?:screen|display|the screen)$/i.test(item||\"\")?'<div class=\"stack-s\"><span style=\"font-weight:600\">You mentioned a screen. Which one?</span><div class=\"chips\">'+[\"Phone screen\",\"Laptop screen\",\"TV\",\"Computer monitor\"].map(function(x){return '<button type=\"button\" class=\"chip\" data-a=\"d\" data-k=\"item\" data-v=\"'+esc(x)+'\">'+esc(x)+'</button>'}).join(\"\")+'</div></div>':'')+'");
R("function psOnly(text,f){\n  var x=String(text||\"\").trim();",
  "function psOnly(text,f){\n  var x=typoFix(String(text||\"\")).trim();");
R("else if(!pk&&!dl&&t.mode!==\"do\"&&FR_NODATE.test(said))U.push(\"They haven’t given you a date yet.\");",
  "else if(!pk&&!dl&&t.mode!==\"do\"&&PMISS.test(said))U.push(\"They said they would, and it hasn’t happened.\");\n  else if(!pk&&!dl&&t.mode!==\"do\"&&FR_NODATE.test(said))U.push(\"They haven’t given you a date yet.\");");
R("  else if(t.mode===\"call\"&&!p&&!pk&&FR_NODATE.test(said))N=",
  "  else if(t.mode===\"call\"&&!p&&!pk&&PMISS.test(said))N=\"Chase \"+(who||\"them\")+\": say what they told you and that it didn’t happen, and ask for a new date in writing.\";\n  else if(t.mode===\"call\"&&!p&&!pk&&FR_NODATE.test(said))N=");
R("function momLatest(){",
  "/* v102: everyday typos and shorthand, read the way they were meant. Only whole words; the person's own words are kept. */\nvar TYPOS=[[/\\bwash(?:ine|in|ing|ign)\\s+mach?ine?\\b/gi,\"washing machine\"],[/\\bwashine\\b/gi,\"washing\"],[/\\bwasing\\b/gi,\"washing\"],[/\\bmachien\\b/gi,\"machine\"],[/\\bbo(?:lier|ilor|liler|ilre|iller)\\b/gi,\"boiler\"],[/\\bref(?:nd|und|ud|uned|udn)\\b/gi,\"refund\"],[/\\bsed\\b/gi,\"said\"],[/\\bsez\\b/gi,\"says\"],[/\\blett(?:a|er|re)\\b/gi,\"letter\"],[/\\bleter\\b/gi,\"letter\"],[/\\beng(?:ineer|ener|eneer|inner|inere|neer)\\b/gi,\"engineer\"],[/\\bdeliv(?:ary|ry|erey)\\b/gi,\"delivery\"],[/\\btmrw\\b|\\btomoz\\b|\\b2moro\\b/gi,\"tomorrow\"],[/\\bwont\\b/gi,\"won't\"],[/\\bisnt\\b/gi,\"isn't\"],[/\\bdidnt\\b/gi,\"didn't\"],[/\\bdoesnt\\b/gi,\"doesn't\"],[/\\bhasnt\\b/gi,\"hasn't\"],[/\\bcant\\b/gi,\"can't\"],[/\\blandlrd\\b|\\blanlord\\b|\\blandord\\b/gi,\"landlord\"],[/\\bcouncel\\b|\\bcounsil\\b/gi,\"council\"],[/\\bparcle\\b/gi,\"parcel\"],[/\\bappointmant\\b|\\bapointment\\b/gi,\"appointment\"]];\nfunction typoFix(x){var s=String(x||\"\");for(var i=0;i<TYPOS.length;i++)s=s.replace(TYPOS[i][0],TYPOS[i][1]);return s}\n/* \"It's not the boiler. The thermostat is broken\": a thing ruled out is not the thing */\nfunction notMention(x){return String(x||\"\").replace(/\\b(?:it'?s|it’s|it is|it was|that'?s|that’s)\\s+not\\s+(?:the|my|our|a)\\s+[a-z]+(?:\\s+[a-z]+)?/gi,\" \").replace(/\\bnot\\s+(?:the|my|our)\\s+[a-z]+(?:\\s+[a-z]+)?(?=\\s*(?:[.,;]|but\\b|it'?s\\b|it’s\\b))/gi,\" \")}\nfunction momLatest(){");
R("var w=m[1].trim().toLowerCase();",
  "var w=m[1].trim().toLowerCase().replace(/\\s+(?:yesterday|today|again|now|tonight|earlier|this morning|last night)$/,\"\");");
fs.writeFileSync('public/index.html',s);
const EXPECT='81388ded735db6f5f17a993285439e46593c6324';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v102 ok',h(s),s.length);
