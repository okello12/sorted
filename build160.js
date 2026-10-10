const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='109d8cff7d139f27be69041e2212fa3ccff5606a')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v160: label in name (WCAG 2.5.3). The ways-in cards carried an aria-label of their title only, while they also
// show a description, so a voice-control user saying what they see might not reach them (found by axe-core 4.14,
// "label-content-name-mismatch"). The cards now take their name from what they show: the title, then the description.
R(`<button type="button" class="cap82-card cap82-'+x.id+'" data-cap82="'+x.id+'" aria-label="'+x.title+'">`,
  `<button type="button" class="cap82-card cap82-'+x.id+'" data-cap82="'+x.id+'">`);
s=s.split('SORTED_V="v159"').join('SORTED_V="v160"');
fs.writeFileSync('public/index.html',s);
const EXPECT='c29a75e77782dd541161bd1bc87e8d64cb895957';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v160 ok',h(s),s.length);
