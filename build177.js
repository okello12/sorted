const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='54563d63a86e6f7f7c258547eb21df42d9e1fef4')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,70));s=s.split(a).join(b)}
// ---- v177, from Baldwin's walk of 24 October 2026: "They said I don't qualify" pasted into a case was saved, then the
// screen said "Sorted couldn't find a date in it, so nothing else changed" and stayed open.
// 1. Everyday refusals are read as one ("don't qualify", "not eligible" on its own, "not entitled", "turned me down",
//    "unsuccessful", "they said no"), unless the words are hedged ("might not qualify", "worried I don't qualify",
//    "if I don't qualify"). As before it is only proposed: "Sounds like they've said no. Record that?" with Yes and
//    Not that. Nothing changes without the tap.
// 2. A message with nothing to propose closes the paste screen and says so plainly, instead of an error-styled note
//    about dates on a form that stays open.
R("var _outCard143=outCard;",
`var REFUSE177=/(?:\\b(?:do|does|did|would|will)\\s+not\\s+qualify|\\b(?:don't|doesn't|didn't|wouldn't|won't)\\s+qualify|(?:\\bnot|n't|\\bno\\s+longer)\\s+(?:be\\s+)?(?:eligible|entitled)\\b|\\bineligible\\b|\\bturned\\s+(?:me|us|him|her|them|it|(?:my|our|the|your)\\s+\\w+(?:\\s+\\w+)?)\\s+down\\b|\\b(?:refused|rejected|declined)\\s+(?:me|us|my|our)\\b|\\b(?:claim|application|appeal|request|complaint|bid|case)\\s+(?:has\\s+been\\s+|was\\s+|is\\s+|were\\s+)?unsuccessful\\b|\\b(?:said|told\\s+(?:me|us))\\s+no\\b(?!\\s+(?:later|more|longer|need|problem|worries|charge|cost|fee|one|other)\\b)|\\banswer\\s+(?:is|was)\\s+no\\b)/gi;
var HEDGE177=/\\b(?:might|may|could|probably|maybe|perhaps|possibly|think|thought|worried|worry|afraid|scared|whether|if|unless|not\\s+sure|in\\s+case)\\b[^.?!]{0,40}$/i;
var _R143=REFUSE143;
REFUSE143={test:function(x){return !!this.exec(x)},exec:function(x){x=String(x||"");var m=_R143.exec(x);if(m)return m;var r=new RegExp(REFUSE177.source,"gi"),k;
  while((k=r.exec(x))){var tail=x.slice(k.index).split(/[.!\\n]/)[0];if(!HEDGE177.test(x.slice(Math.max(0,k.index-60),k.index))&&!/\\?/.test(tail))return k}return null}};
var _outCard143=outCard;`);
R('save();d.err="Added to the case. Sorted couldn’t find a date in it, so nothing else changed.";render();return}',
  'S.view.panel=null;S.draft={};commit();window.scrollTo(0,0);toast("Added to the case. Sorted found nothing in it that changes a date or a promise.");return}');
// 3. "Not that" marks the case changed, so the turned-down proposal is saved as gone (before, a reload brought it back).
R('    case "out-no":if(t&&t.outP){delete t.outP;commit()}break;','    case "out-no":if(t&&t.outP){delete t.outP;t._dirty=true;commit()}break;');
// 4. The card and the history quote the person's words as written (curly apostrophes kept), not the copy the reader
//    normalised.
R("var _outCard143=outCard;","var _outIn177=outIn;outIn=function(t,text,src){var r=_outIn177(t,text,src);if(r&&t.outP&&t.outP.k===\"refused143\"){var cl=String(text||\"\").replace(/\\s+/g,\" \").trim();if(cl.length>200)cl=cl.slice(0,197).replace(/\\s+\\S*$/,\"\")+\"…\";t.outP.said=cl}return r};\nvar _outCard143=outCard;");
R('SORTED_V="v176"','SORTED_V="v177"');
fs.writeFileSync('public/index.html',s);
const EXPECT='3bda7b0fb947322ed24df4d02d9b572cf5ada4ca';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v177 ok',h(s),s.length);
