const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='e5d939a91d8343b62070961f938cac47ca2838f8')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v146: "should" is their estimate, the same whether typed or pasted ----
// Before v146 a typed "should" was a maybe (PTENT) while a pasted one was a promise, and both counted the same as a
// firm date once confirmed. Now "should" with a day, from them, is proposed as their estimate: the person confirms it,
// Sorted asks on the day, and "Not yet" is never a broken promise or a company score. "Might", "maybe", "could",
// "hopefully" and "try" stay non-commitments; "try their best" joins them.
R("|could|should|may (?:be",
  "|could|may (?:be");
R("try to|trying to|aim to|hope to|hoping to|if possible|",
  "try to|trying to|try (?:their|our|his|her|my) best|do (?:their|our|his|her) best|fingers crossed|aim to|hope to|hoping to|if possible|");
R("if(sp.win)spr.win=true;spr.prec=",
  "if(sp.win)spr.win=true;if(sp.est146)spr.est146=true;spr.prec=");
R("function firmOrg143(p){return !!p&&p.src!==\"parking\"&&!p.chkMig&&",
  "function firmOrg143(p){return !!p&&p.src!==\"parking\"&&!p.chkMig&&!p.est146&&");
R("function notFirm143(p){return !!p&&p.src!==\"parking\"&&(aprx(p)||!!p.chk||!!p.chkMig)}",
  "function notFirm143(p){return !!p&&p.src!==\"parking\"&&(aprx(p)||!!p.chk||!!p.chkMig||!!p.est146)}");
R("function realMiss143(q){return !!q&&q.status===\"missed\"&&!aprx(q)&&!q.chkMig}",
  "function realMiss143(q){return !!q&&q.status===\"missed\"&&!aprx(q)&&!q.chkMig&&!q.est146}");
R("(q.prec===\"calc\"?\"The day Sorted worked out isn’t a day they gave\":\"They didn’t give a firm day\")",
  "(q.est146&&!aprx(q)?\"They said it should happen by then, not that it would\":q.prec===\"calc\"?\"The day Sorted worked out isn’t a day they gave\":\"They didn’t give a firm day\")");
R("notFirm143(p)?\"The day Sorted worked out has passed\"",
  "notFirm143(p)?(p.est146&&!aprx(p)?\"The day they expected has passed\":\"The day Sorted worked out has passed\")");
R("notFirm143(p)?\"THEY SAID · NO DAY GIVEN\"",
  "notFirm143(p)?(p.est146&&!aprx(p)?\"THEY EXPECTED\":\"THEY SAID · NO DAY GIVEN\")");
R(":\"They promised\")+'</p><h2 class=\"h2\">'+esc(phaseTitle(p))",
  ":p.est146?\"They expect\":\"They promised\")+'</p><h2 class=\"h2\">'+esc(phaseTitle(p))");
R("+'</p>'+aprxLine(p);",
  "+'</p>'+aprxLine(p)+est146Line(p);");
R(":who(p)+\" promised it \"+pw137(p))",
  ":who(p)+(p.est146?\" expects it \":\" promised it \")+pw137(p))");
R("if(p)return \"Theirs: \"+(whoSay(p.party)||who||\"they\")+\" said they would, and the date is on the case.\";",
  "if(p)return \"Theirs: \"+(whoSay(p.party)||who||\"they\")+(p.est146?\" said it should happen, and the date is on the case.\":\" said they would, and the date is on the case.\");");
R("function boot(){",
`/* ---------- v146: "should" is their estimate ---------- */
var EST146=/\\bshould(?:n['’]t| not)?\\b/i,FIRM146=/\\b(?:will|won['’]t|['’]ll|shall|is going to|are going to|booked|confirmed|guaranteed?|promised|agreed)\\b/i;
function est146Of(p){if(!p||typeof p!=="object")return p;var x=String(p.said||"");if(EST146.test(x)&&!FIRM146.test(x.replace(EST146,"")))p.est146=true;return p}
var _rc146=readCase;readCase=function(){return est146Of(_rc146.apply(this,arguments))};
var _ir146=intakeRead;intakeRead=function(){return est146Of(_ir146.apply(this,arguments))};
function est146Line(p){if(!p||!p.est146||p.status&&p.status!=="open")return "";
  return '<p class="aprx138 est146">'+esc(cap1(whoSay(p.party)||"they"))+' said it should happen by then. That’s their estimate, not a firm promise. Sorted asks you on the day, and if it hasn’t happened it doesn’t count as a broken promise.</p>'}
var _ac146=aprxCard;aprxCard=function(t,p){var x=_ac146.apply(this,arguments);if(p&&p.est146&&!aprx(p)&&p.status==="open"&&!(t&&t.example))x+=est146Line(p)+'<button class="link" data-a="panel" data-p="chk138" style="text-align:left">Choose when to check</button>';return x};
function boot(){`);
s=s.split('SORTED_V="v145"').join('SORTED_V="v146"');
fs.writeFileSync('public/index.html',s);
const EXPECT='a8ab6ad9042f0b34f1d4331b9f42e82a43861c6e';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v146 ok',h(s),s.length);
