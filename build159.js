const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='3bae6a756028682a67ec55f123f5c32d6bd9b835')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v159: the copy on this phone when storage is full. ----
// Found by test 125 (500 cases with long histories): when the copy no longer fitted in the browser's storage (about
// 5 MB), cacheWrite failed silently and wrote nothing, so an edit made offline, which exists nowhere else, was lost on
// the next reload. cachePut159 now writes the whole copy if it fits, and otherwise keeps every record with an unsent
// edit (the account already holds the rest, and the next load reads it from there), reporting the kind once ("save",
// "cache_quota", never words).
R('out=out.filter(function(o){return o&&!gone[o.id]});localStorage.setItem(k,JSON.stringify(out))}catch(e){}}',
  'out=out.filter(function(o){return o&&!gone[o.id]});cachePut159(k,out)}catch(e){}}');
R('function boot(){',`/* v159: write the copy on this phone; if it doesn't fit, keep what exists nowhere else (records with an unsent edit) */
function cachePut159(k,out){
  try{localStorage.setItem(k,JSON.stringify(out));S._cacheShort=false;return true}catch(e){}
  var keep=out.filter(function(o){return o&&(o._dirty||o._saving||o._tab)});
  try{localStorage.removeItem(k);localStorage.setItem(k,JSON.stringify(keep))}catch(e2){}
  if(!S._cacheShort){S._cacheShort=true;try{reportErr("save","cache_quota","")}catch(e3){}}
  return false}
function boot(){`);
s=s.split('SORTED_V="v158"').join('SORTED_V="v159"');
fs.writeFileSync('public/index.html',s);
const EXPECT='109d8cff7d139f27be69041e2212fa3ccff5606a';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v159 ok',h(s),s.length);
