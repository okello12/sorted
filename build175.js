const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='361327da2b5bf527cb70049f3a70db8a6e304592')throw new Error('base mismatch '+h(s));
function R(a,b){const n=s.split(a).length-1;if(n!==1)throw new Error('match '+n+': '+a.slice(0,80));s=s.replace(a,b)}
// A refresh can arrive while any case form is open. Keep the current screen and its DOM
// (including values that have not yet reached S.draft) while the case remains active.
R('  var keepChoice=hit&&(v.panel==="later"||v.panel==="changed"||v.panel==="paste")&&recOf143(vid)&&recOf143(vid).board!=="done";',
  '  var updated=recOf143(vid),keepChoice=hit&&v.panel&&updated&&updated.board!=="done";');
// Home quick-answer sheets are a choice too. A refresh of the same open case should not
// collapse one; if it is no longer a quick-answer case, redraw from its latest state.
R('  if(S.qOpen&&vis.some(function(c){return c.id===S.qOpen.id})){S.qOpen=null;S.qErr=null}',
  '  if(S.qOpen&&vis.some(function(c){return c.id===S.qOpen.id})&&!qKind(recOf143(S.qOpen.id))){S.qOpen=null;S.qErr=null}');
R('  if(keepChoice&&vis.every(function(c){return c.id===vid}))return;',
  '  if(keepChoice&&vis.every(function(c){return c.id===vid}))return;\n  if(v.name==="home"&&S.qOpen&&qKind(recOf143(S.qOpen.id))&&vis.every(function(c){return c.id===S.qOpen.id}))return;');
R('SORTED_V="v174"','SORTED_V="v175"');
fs.writeFileSync('public/index.html',s);
const EXPECT='4ab4449d828bd217534ae6ec307cd4d8e4145960';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v175 ok',h(s),s.length);
