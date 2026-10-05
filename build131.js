const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='487a638e38f1fc475106fd30f2391c0bb16ab22d')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v131: fixes from Baldwin's phone after v130. ----
R("function case75TitleParts(t){\n  var x=String(t.title||\"\").replace(/^\\s*TEST:\\s*/i,\"\").trim();",
  "function case75TitleParts(t){\n  var x=String(t.title||\"\").replace(/^\\s*TEST:\\s*/i,\"\").trim();\n  /* v131: an older guided start saved \"<Who> said they would nothing\"; show \"Waiting for <Who>\" everywhere the title appears */\n  x=x.replace(/^(.+?)\\s+said (?:they|he|she|it) would\\s+(?:nothing|none|n\\/?a|not sure|unsure|dunno|no idea|idk|tbc|nothing yet|not yet)\\.?(\\s*[·•].*)?$/i,\"Waiting for $1$2\");");
R("var SORTED_V=\"v130\"",
  "var SORTED_V=\"v131\"");
fs.writeFileSync('public/index.html',s);
const EXPECT='670828e59bc54e35e5a5fb1007b867310150806d';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v131 ok',h(s),s.length);
