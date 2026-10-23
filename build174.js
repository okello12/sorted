const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='01d72dfa697d3b760cfad48c647e331e3dbec105')throw new Error('base mismatch '+h(s));
function R(a,b){const n=s.split(a).length-1;if(n!==1)throw new Error('match '+n+': '+a.slice(0,80));s=s.replace(a,b)}
// Reading a newer revision must not dismiss an open choice while the case still needs attention.
// The next normal render uses the refreshed record. Leaving the DOM alone here also keeps a
// selected date and anything typed into the change form.
R('  if(hit&&v.panel){v.panel=null;S.draft={}}\n  if(S.qOpen',
  '  var keepChoice=hit&&(v.panel==="later"||v.panel==="changed")&&recOf143(vid)&&recOf143(vid).board!=="done";\n  if(hit&&v.panel&&!keepChoice){v.panel=null;S.draft={}}\n  if(keepChoice&&vis.every(function(c){return c.id===vid}))return;\n  if(S.qOpen');
R('  if(hit&&vis.some(function(c){return c.id===vid&&c.k!=="merge"}))toast("This case changed elsewhere. Here’s where it is now.")}',
  '  if(hit&&!keepChoice&&vis.some(function(c){return c.id===vid&&c.k!=="merge"}))toast("This case changed elsewhere. Here’s where it is now.")}');
R('SORTED_V="v173"','SORTED_V="v174"');
fs.writeFileSync('public/index.html',s);
const EXPECT='0d281533123b6a717b336cb447f6e58f3c6ff4a7';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v174 ok',h(s),s.length);
