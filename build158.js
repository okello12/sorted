const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='9f8919295dc6329bf154210b1b5bfd00a3a208cd')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v158: a strict script policy. The page runs no inline event handler, so the Content Security Policy can drop
// 'unsafe-inline' for scripts and list the page's own inline scripts by their SHA-256 hashes instead (vercel.json,
// written by tools/csp_hashes.js; test 124 fails if they don't match the page). The one handler, an illustration that
// removes itself if its file is missing, becomes a listener. Styles keep 'unsafe-inline' (the page sets styles inline).
R(`(eager?' fetchpriority="high"':' loading="lazy"')+' onerror="this.remove()">'}`,
  `(eager?' fetchpriority="high"':' loading="lazy"')+'>'}
/* v158: no inline handlers (the script policy allows only Sorted's own scripts): a missing illustration removes itself */
document.addEventListener("error",function(e){var x=e.target;if(x&&x.tagName==="IMG"&&x.classList&&x.classList.contains("art"))x.remove()},true);`);
s=s.split('SORTED_V="v157"').join('SORTED_V="v158"');
fs.writeFileSync('public/index.html',s);
const EXPECT='3bae6a756028682a67ec55f123f5c32d6bd9b835';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v158 ok',h(s),s.length);
