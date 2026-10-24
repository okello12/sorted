const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='4ab4449d828bd217534ae6ec307cd4d8e4145960')throw new Error('base mismatch '+h(s));
function R(a,b){const n=s.split(a).length-1;if(n!==1)throw new Error('match '+n+': '+a.slice(0,80));s=s.replace(a,b)}
// Sync bookkeeping stays in the full record; it is not the latest real-world case update.
R('function case56UsefulEvent(e){\n  var l=String(e&&e.label||"");',
  'function case56UsefulEvent(e){\n  var l=String(e&&e.label||"");\n  if(/^Merged with changes saved (?:in another tab|from another device)\\.$/.test(l))return false;');
R('var e=(t.events||[]).filter(case56UsefulEvent).filter(function(x){return !/^(?:Opened from the ',
  'var e=(t.events||[]).filter(case56UsefulEvent).filter(function(x){return !/^Merged with changes saved (?:in another tab|from another device)\\./.test(x.label||"")&&!/^(?:Opened from the ');
// The older anchor rule used carbon-ink, which becomes dark on the violet button in dark mode.
R('</head>','<style>\na.btn.primary,a.btn.primary:visited{color:#fff}\n</style>\n</head>');
R('SORTED_V="v175"','SORTED_V="v176"');
fs.writeFileSync('public/index.html',s);
const EXPECT='54563d63a86e6f7f7c258547eb21df42d9e1fef4';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v176 ok',h(s),s.length);
