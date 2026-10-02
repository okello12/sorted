const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='82140e8f0d506729ab95ee3fc580bba3c5ddf87b')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+String(a).slice(0,90));s=s.split(a).join(b)}
// v88: an answer-page CTA should arrive with the problem already waiting in universal intake.
R('Safe administration can happen automatically. Sorted still asks before sending, submitting, paying, accepting, admitting or closing anything.',
  'Sorted automatically watches the dates and incoming replies it can see. It still asks before sending, submitting, paying, accepting, admitting or closing anything.');
R('boot();\n})();',String.raw`/* v88 answer page -> instant case intake */
var fwAnswerRender=render;
render=function(){
  try{
    if(!S._fwAnswerSeeded&&S.user&&S.view&&S.view.name==='home'){
      var z=fwSeed();
      if(z){S._fwAnswerSeeded=true;S.composeOpen=true;S.draft=S.draft||{};if(!S.draft.casetext)S.draft.casetext=z.title;S.draft.src='a Sorted answer page'}
    }
  }catch(e){}
  return fwAnswerRender();
};
boot();
})();`);
fs.writeFileSync('public/index.html',s);
const EXPECT='0000000000000000000000000000000000000000';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v88 ok',h(s),s.length);
