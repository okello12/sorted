const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='a7437d3a5700eaa29f69b83533df3716f7eae338')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v50: messy real-world writing (tests/corpus.py, MESSY) ----


// 1. Helpers: changed dates, "yesterday", "the 20th", "8-12", short company notifications; "THEY" is not a company name
R("var PNOTNAME=/^(?:I|They|He|She|We|It|You|The|This|That|Then|And|But|So|My|Our|Your|Their|His|Her|Someone|Somebody|Nobody|Customer|Customers|Support|Service|Team|Staff|Engineer|Agent|Man|Woman|Lady|Guy|Person|Company|Shop|Store|Today|Yesterday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Also|Still|Now|Last|Next|When|After|Before|Apparently)$/;",
  "var PNOTNAME=/^(?:I|They|He|She|We|It|You|The|This|That|Then|And|But|So|My|Our|Your|Their|His|Her|Someone|Somebody|Nobody|Customer|Customers|Support|Service|Team|Staff|Engineer|Agent|Man|Woman|Lady|Guy|Person|Company|Shop|Store|Today|Yesterday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Also|Still|Now|Last|Next|When|After|Before|Apparently)$/i;\nvar PCHG=/\\b(?:changed|moved|rescheduled|re-?arranged|new (?:date|time|appointment|slot)|now (?:on|booked for)|update[d:]?)\\b/i;\nvar PNOTE=/^[A-Z][\\w&'. -]{1,30}:\\s|\\byour (?:order|parcel|package|refund|engineer|appointment|delivery|visit|repair|claim|booking)\\b/i;\nfunction pChanged(c){var m=/\\b(?:changed|moved|rescheduled|re-?arranged|pushed(?: back)?|put (?:it )?back|brought (?:it )?forward)\\b.*?\\b(?:to|until|till|for)\\s+(.+)$/i.exec(c);return m?m[1]:c}\nfunction pNorm(c){\n  var y=addDays(new Date(),-1),t=new Date();\n  c=String(c||\"\").replace(/\\byesterday\\b/gi,y.getDate()+\" \"+MONN[y.getMonth()]);\n  c=c.replace(/\\b(?:on\\s+)?the\\s+(\\d{1,2})(?:st|nd|rd|th)\\b(?!\\s*(?:of\\s+)?(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec))/gi,function(_,d){var mo=+d>=t.getDate()?t.getMonth():(t.getMonth()+1)%12;return \"on \"+d+\" \"+MONN[mo]});\n  return c.replace(/(^|[^\\w£$€\\/.:-])(\\d{1,2})\\s?-\\s?(\\d{1,2})(?![\\d\\/.:%]|\\s*(?:working |business )?(?:days?|weeks?|hours?|hrs|mins?|minutes?|months?)\\b)/gi,\"$1between $2 and $3\");\n}\nfunction readCase(t,f){var lng=t.length>100||/\\n/.test(t);return lng?(sugFromMessage(t,null,f)||suggestPromise(t,f)):(suggestPromise(t,f)||((t.length>60||PNOTE.test(t))?sugFromMessage(t,null,f):null))}");

// 2. The sentence reader reads the new date when a date was changed, and understands the forms above
R("  var two=pTwo(clause),also=\"\";if(two){clause=two[0];also=two[1]}",
  "  var two=pTwo(clause),also=\"\";if(two){clause=two[0];also=two[1]}\n  var clause0=clause;clause=pNorm(pChanged(clause));");
R("var pr={said:cap1(clause.replace(/[,\\s]+$/,\"\")),party:",
  "var pr={said:cap1(clause0.replace(/[,\\s]+$/,\"\")),party:");

// 3. The message reader ignores quoted old messages ("> ...") and reads an update or a changed date first
R("  if(PNEG.test(raw))return null;\n  var parts=raw.replace(/([.!?])\\s+/g,\"$1\\n\").split(/\\n+/).map(function(x){return x.trim()}).filter(function(x){return x.length>3});",
  "  if(PNEG.test(raw))return null;\n  raw=raw.split(\"\\n\").filter(function(l){return !/^\\s*>/.test(l)}).join(\"\\n\");\n  var parts=raw.replace(/([.!?])\\s+/g,\"$1\\n\").split(/\\n+/).map(function(x){return x.trim()}).filter(function(x){return x.length>3});\n  parts=parts.filter(function(x){return PCHG.test(x)}).concat(parts.filter(function(x){return !PCHG.test(x)}));");
R("var q=pt.replace(/\\b(?:please )?allow (?:up to )?/i,\"in \");var w=parseWhen(q,today);",
  "var q=pNorm(pChanged(pt.replace(/\\b(?:please )?allow (?:up to )?/i,\"in \")));var w=parseWhen(q,today);");
R("if(w&&w.date&&pWhenOk(q,w)){if(!best||(MSGW.test(pt)&&!MSGW.test(best))){best=pt;bw=w}if(MSGW.test(pt))break}",
  "if(w&&w.date&&pWhenOk(q,w)){if(PCHG.test(pt)){best=pt;bw=w;break}if(!best||(MSGW.test(pt)&&!MSGW.test(best))){best=pt;bw=w}if(MSGW.test(pt))break}");

// 4. The start box uses one reader, readCase(), which also reads short notifications like "Amazon: Your package will arrive tomorrow"
R("var fs0=String(d.said||t.said),lng=fs0.length>100||/\\n/.test(fs0),sgp=lng?(sugFromMessage(fs0,null,t.facts)||suggestPromise(fs0,t.facts)):(suggestPromise(fs0,t.facts)||(fs0.length>60?sugFromMessage(fs0,null,t.facts):null));",
  "var fs0=String(d.said||t.said),lng=fs0.length>100||/\\n/.test(fs0),sgp=readCase(fs0,t.facts);");

fs.writeFileSync('public/index.html',s);
const EXPECT='bb73812b7d2d6de7e8f7d19bc6080be4d8a779aa';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v50 ok',h(s),s.length);
