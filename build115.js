const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='ca22f435d1868d83d2164a507bc6d80a9a2f495d')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v115: the two moderate axe findings. A guided start on a newcomer's Home has an h1; the first response's
// eyebrow is an h2, so its h3 rows follow in order. ----
R("var SORTED_V=\"v114\"",
  "var SORTED_V=\"v115\"");
R("<h2 class=\"h1\" style=\"margin:0\">'+esc(ex&&ex.h||g.h)+'</h2><form class=\"stack-s\" data-f=\"gi\" data-k=\"'+k+'\">",
  "<'+(S.tasks.length?'h2':'h1')+' class=\"h1\" style=\"margin:0\">'+esc(ex&&ex.h||g.h)+'</'+(S.tasks.length?'h2':'h1')+'><form class=\"stack-s\" data-f=\"gi\" data-k=\"'+k+'\">");
R("<p class=\"eyebrow\" id=\"frh\">Here’s what Sorted makes of it</p>",
  "<h2 class=\"eyebrow\" id=\"frh\" style=\"margin:0\">Here’s what Sorted makes of it</h2>");
fs.writeFileSync('public/index.html',s);
const EXPECT='c4025e5524fd39afc2bfa75dc4845e32b99d8045';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v115 ok',h(s),s.length);
