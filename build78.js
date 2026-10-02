const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='d94a96a3ccd9bbc8de25f9e451ceaf27c68e0ca6')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v78: small fixes after the v75 to v77 review. A promise that isn't a visit says "Due today" with no "Show this"
// and no "It didn't" before its time; the reference shows once; Home rows line up; step 2 shows the case name and Ref. ----
R("  if(ph===\"now\")return \"Happening now\";",
  "  if(ph===\"now\")return (p.by||p.allDay)&&!pVisit(p)?\"Due today\":\"Happening now\";");
R("function askFor(p){",
  "/* v78: is this promise someone turning up (an engineer, a delivery, an appointment)? Only then is \"Show this\" useful. */\nfunction pVisit(p){return /\\b(?:engineers?|visit|come|coming|call round|arrive between|technicians?|plumbers?|electricians?|fitters?|repair ?man|delivery|deliver|appointment|collect(?:ion)?|inspection|survey)\\b/i.test((p.said||\"\")+\" \"+(p.party||\"\"))}\nfunction askFor(p){");
R("  }else{\n    h+=art(\"hold-up-pack\",\"mini\")+'<button class=\"btn primary block\" data-a=\"panel\" data-p=\"hold\">Show this</button>",
  "  }else if(!pVisit(p)){\n    h+='<p>'+esc(p.by||p.allDay?\"Due by the end of \"+(sameDay(window_(p).start,new Date())?\"today\":fmtDay(window_(p).start))+\".\":\"Due \"+whenText(p)+\".\")+' If it hasn’t happened by then, Sorted will ask you.</p><button class=\"btn primary block\" data-a=\"kept\">'+esc(askFor(p)[1]===\"Yes\"?\"It’s happened\":askFor(p)[1])+'</button><button class=\"link\" data-a=\"rebook\" style=\"text-align:left\">They changed the date</button>';\n    h+=soonReminders(t);\n  }else{\n    h+=art(\"hold-up-pack\",\"mini\")+'<button class=\"btn primary block\" data-a=\"panel\" data-p=\"hold\">Show this</button>");
R("(p.ref?'<span class=\"ref\">'+esc(p.ref)+'</span>':\"\")+'</div>';\n  h+='<div class=\"promise-body\">",
  "(p.ref&&p.ref!==case75HeaderRef(t)?'<span class=\"ref\">'+esc(p.ref)+'</span>':\"\")+'</div>';\n  h+='<div class=\"promise-body\">");
R("(p.ref?'<p class=\"home55-ref\">Ref '+esc(p.ref)+'</p>':'')",
  "(p.ref&&p.ref!==ht.ref?'<p class=\"home55-ref\">Ref '+esc(p.ref)+'</p>':'')");
R("    if(p.ref)a.push(\"Ref \"+p.ref);",
  "    if(p.ref&&p.ref!==case75TitleParts(t).ref)a.push(\"Ref \"+p.ref);");
R(".case75-title-ref{margin:0;font-size:14px;color:var(--ink-2)}",
  ".case75-title-ref{margin:0;font-size:14px;color:var(--ink-2)}\nmain .home44-row{grid-template-columns:9px minmax(0,1fr) 15px;column-gap:10px}\nmain .home44-row:before{grid-column:1;grid-row:1/3;align-self:center}\nmain .home44-row main .home44-row-copy{grid-column:2;grid-row:1}\nmain .home44-row .home44-pill{grid-column:2;grid-row:2;justify-self:start}\nmain .home44-row>span:empty{display:none}\nmain .home44-row .home44-chevron{grid-column:3;grid-row:1/3;align-self:center}");
R("(d.title?'<p class=\"h3\">'+esc(d.title)+'</p>':\"\")",
  "(d.title?(function(z){return '<p class=\"h3\">'+esc(z.title)+'</p>'+(z.ref?'<p class=\"case75-title-ref mono\">Ref '+esc(z.ref)+'</p>':'')})(case75TitleParts({title:d.title})):\"\")");
fs.writeFileSync('public/index.html',s);
const EXPECT='7cde655a2e3d0b3158d440b79019b1be196a6ba1';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v78 ok',h(s),s.length);
