const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='d558cdcaa850cfade31a482f6f9280dbbd0ee6fd')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v113: the repair questions start from the thing named, never a washing machine nobody mentioned; Sort something
// new stays closed on a returning Home until asked, with the discovery fold inside it; an unfinished case says "Finish
// setting up this case" and the health line waits; Help beside Account; one selected look for every choice. ----
R("var SORTED_V=\"v112\"",
  "var SORTED_V=\"v113\"");
R("var THING_FILL=/^(?:it|this|that|everything|something|nothing|phone call|call|yesterday|today|now|still|just|again)$/i;",
  "var THING_FILL=/^(?:it|this|that|everything|something|nothing|phone call|call|yesterday|today|now|still|just|again)$/i;\n/* v113: \"My alarm is making too much noise\", \"the fridge keeps beeping\": a thing named by what it is doing */\nTHING_MORE.push(new RegExp(\"^\\\\s*(?:my|the|our)\\\\s+((?:\"+THING_TK+\"\\\\s+){0,3}\"+THING_TK+\")\\\\s+(?:is|are|keeps?|has been|have been|was|were|started|starts)\\\\s+(?:making|beeping|buzzing|clicking|humming|rattling|squealing|squeaking|grinding|banging|whistling|flashing|flickering|tripping|going off|overheating|noisy|loud|smelling|dripping)\",\"i\"));");
R("var item=d.item!==undefined?d.item:(f.item!==undefined?f.item:\"Washing machine\"),fault=d.fault!==undefined?d.fault:f.fault;",
  "var item=d.item!==undefined?d.item:(f.item!==undefined&&f.item!==null?f.item:\"\"),fault=d.fault!==undefined?d.fault:f.fault;");
R("    var item=d.item!==undefined?d.item:(t.fix.item!==undefined?t.fix.item:\"Washing machine\");",
  "    var item=d.item!==undefined?d.item:(t.fix.item!==undefined&&t.fix.item!==null?t.fix.item:\"\");");
R("if(item!==\"Washing machine\")h+='<label class=\"f\">What is it?<input type=\"text\" id=\"f-item\" name=\"item\" value=\"'+esc(item)+'\" placeholder=\"Fridge, boiler, laptop…\"></label>';",
  "if(item!==\"Washing machine\")h+='<label class=\"f\">What is it?<input type=\"text\" id=\"f-item\" name=\"item\" value=\"'+esc(item)+'\" placeholder=\"Fridge, boiler, alarm, laptop…\"></label><p class=\"muted\" style=\"margin:0;font-size:15px\">Say what’s happening in the box below. Sorted asks its own questions only for a washing machine; for anything else it keeps your words and works out who should fix it.</p>';");
R("      h+='<section class=\"home111-new\" id=\"home111-new\" aria-labelledby=\"home111-new-h\"><h2 class=\"h2\" id=\"home111-new-h\">Sort something new</h2><div id=\"cap82-slot\"></div>'+momStartEntry()+'<div class=\"home44-compose\">'+(S.composeOpen?caseEntry():'<button class=\"btn block home44-new\" data-a=\"compose\">+ Sort something new</button>')+'</div>'+ex95Also()+'</section>';",
  "      var nOpen=!!(S.newOpen||S.composeOpen);\n      h+='<section class=\"home111-new'+(nOpen?' open':'')+'\" id=\"home111-new\" aria-labelledby=\"home111-new-h\"><h2 class=\"h2\" id=\"home111-new-h\">Sort something new</h2><div class=\"home113-more\"><div id=\"cap82-slot\"></div>'+momStartEntry()+'</div><div class=\"home44-compose\">'+(S.composeOpen?caseEntry():'<button class=\"btn block home44-new\" data-a=\"compose\" aria-expanded=\"'+nOpen+'\">+ Sort something new</button>')+'</div><div class=\"home113-more\">'+ex95Also()+(S.loaded&&!giKind()?ex95Explore():'')+'</div></section>';");
R("  if(S.loaded&&!giKind()&&!(S.draft&&(S.draft.pkShort||S.draft.psShort||S.draft.vague||S.draft.matchId)))h+=ex95Explore();\n  h+='</main>';",
  "  if(newcomer&&S.loaded&&!giKind()&&!(S.draft&&(S.draft.pkShort||S.draft.psShort||S.draft.vague||S.draft.matchId)))h+=ex95Explore();\n  h+='</main>';");
R("    case \"new-case\":{var nn=$(\"#home111-new\");if(nn){nn.scrollIntoView({block:\"start\",behavior:\"smooth\"});var nd=nn.querySelector(\".cap82-card,.home44-new\");if(nd)setTimeout(function(){nd.focus({preventScroll:true})},400)}break}",
  "    case \"new-case\":{S.newOpen=true;render();setTimeout(function(){var nn=$(\"#home111-new\");if(!nn)return;nn.scrollIntoView({block:\"start\",behavior:\"smooth\"});var nd=nn.querySelector(\".cap82-card\")||nn.querySelector(\".home44-new\");if(nd)setTimeout(function(){nd.focus({preventScroll:true})},350)},30);break}");
R("    case \"home\":go({name:\"home\"});break;",
  "    case \"home\":S.newOpen=false;go({name:\"home\"});break;");
R("    case \"ex-all\":{var xd=$(\"#cap95-explore\");",
  "    case \"ex-all\":{if(!S.newOpen&&S.tasks.length){S.newOpen=true;render()}var xd=$(\"#cap95-explore\");");
R("function goHome(){\n  S.draft={};S.composeOpen=false;S.pendingMom=null;",
  "function goHome(){\n  S.draft={};S.composeOpen=false;S.newOpen=false;S.pendingMom=null;");
R("momAttach(t);giForget();t.frNew=true;",
  "momAttach(t);giForget();S.newOpen=false;t.frNew=true;");
R("sessionStorage.removeItem(\"sorted.moment\")}catch(e){}if(!k)return;if(k===\"moving\"){",
  "sessionStorage.removeItem(\"sorted.moment\")}catch(e){}if(!k)return;S.newOpen=true;if(k===\"moving\"){");
R("  if(t.mode===\"fix\"&&t.fix&&t.fix.step!==\"done\")return t.fix.step===\"checks\"?\"Next: finish the checks\":\"Next: a few quick questions\";\n  if(t.mode===\"renew\"&&t.renew&&t.renew.step!==\"done\")return \"Next: add the details\";",
  "  if(t.mode===\"fix\"&&t.fix&&t.fix.step!==\"done\")return t.fix.step===\"checks\"?\"Next: finish the checks\":\"Finish setting up this case\";\n  if(t.mode===\"renew\"&&t.renew&&t.renew.step!==\"done\")return \"Finish setting up this case\";");
R("function healthLine(t,s){\n  if(t.frNew||t.example||s===\"done\"||(t.sugP&&!t.sugDone))return \"\";",
  "function healthLine(t,s){\n  if(t.frNew||t.example||s===\"done\"||(t.sugP&&!t.sugDone))return \"\";\n  if((t.mode===\"fix\"&&t.fix&&t.fix.step!==\"done\")||(t.mode===\"renew\"&&t.renew&&t.renew.step!==\"done\"))return \"\";");
R("    (extra||'<button class=\"navq\" data-a=\"data\">Account</button>')+'</header>';",
  "    (extra||'<span class=\"navs\"><button class=\"navq\" data-a=\"help\">Help</button><button class=\"navq\" data-a=\"data\">Account</button></span>')+'</header>';");
R("    case \"data\":go({name:\"data\"});break;",
  "    case \"data\":go({name:\"data\"});break;\n    case \"help\":go({name:\"data\"});setTimeout(function(){var hp=$(\"#help\");if(hp){hp.scrollIntoView({block:\"start\"});var hh=$(\"#help-h\");if(hh){hh.setAttribute(\"tabindex\",\"-1\");hh.focus({preventScroll:true})}}},60);break;");
R("</style>\n</head>\n<body>\n<div class=\"wrap\" id=\"app\"></div>\n<d",
  "</style>\n<style>\n/* v113 */\nmain.home44 .home111-new:not(.open)>.h2,main.home44 .home111-new:not(.open)>.home113-more{display:none}\nmain.home44 .home111-new:not(.open){padding-top:14px}\n.navs{display:flex;align-items:center;gap:16px}\n/* one way to show a choice: filled violet, white text, bold. Hover is a quiet hint, and only where there is a mouse */\n.chip[aria-pressed=\"true\"],label.chip:has(input:checked),.gi-chip:has(input:checked){background:#4F39D9!important;background-image:none!important;border-color:#4F39D9!important;color:#fff!important;font-weight:700}\n.chip:hover{transform:none!important;border-color:inherit}\n@media (hover:hover){.chip:not([aria-pressed=\"true\"]):hover{border-color:color-mix(in srgb,var(--violet) 45%,var(--rule))}}\n</style>\n</head>\n<body>\n<div class=\"wrap\" id=\"app\"></div>\n<d");
fs.writeFileSync('public/index.html',s);
const EXPECT='b17574b1d1ff34081f973e9fbb24e9601f33d6c9';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v113 ok',h(s),s.length);
