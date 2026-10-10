const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='2a4aabf6b047bc4a32211d0757196519d5fcb8a0')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v163: Something I own isn't working, stage 3 (docs/PRODUCT_PHASE1.md). Migration 30 adds the product step names
// to pilot_events on staging and live, so the page now records them: codes and counts only (source, kind of product,
// route, how many safety rules matched), never a brand, model, serial, shop, date, OCR text or the person's words.
R('var PROD_TRACK161=false;/* usage records wait for migration 30 (the step names); switched on in the release that applies it */','var PROD_TRACK161=true;/* migration 30 (v163) allows the step names */');
s=s.split('SORTED_V="v162"').join('SORTED_V="v163"');
fs.writeFileSync('public/index.html',s);
const EXPECT='e56d4378915df234d590a43dd8332edb6d143bca';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v163 ok',h(s),s.length);
