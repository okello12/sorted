const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v139: two adversarial truth-integrity edges found while reviewing v138 itself.
// 1) "Wednesday, not Tuesday" must keep Wednesday rather than treating the whole sentence as a negated date.
// 2) booking details confirmed from the provider's app/email outrank an older vague suggestion; later ledger sync must
//    never copy the old suggestion's uncertainty back over the newly confirmed exact booking. ----
R('var SORTED_V="v138"','var SORTED_V="v139"');
const PATCH=String.raw`
/* v139: truth-integrity precedence */
truthWhen138=function(text){
  var s=String(text||"").replace(/[’‘]/g,"'").replace(/\s+/g," ").trim(),m,WD="(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)",neg=[];
  var nr=new RegExp("\\bnot\\s+(?:on\\s+)?"+WD+"\\b","ig"),clean=s;
  while((m=nr.exec(s)))neg.push(m[0]);
  if(neg.length)clean=s.replace(nr," ").replace(/\s+/g," ").trim();
  m=new RegExp("\\b(?:probably|maybe|possibly|likely|tentatively|provisionally|should(?:\\s+be)?|expected(?:\\s+to\\s+be)?)\\b[^.!?]{0,30}\\b"+WD+"\\b","i").exec(clean);if(m)return {phrase:m[0],precision:"tentative"};
  var wins=[/\b(?:sometime\s+)?next week\b/i,/\bearly next week\b/i,/\b(?:later|late) this week\b/i,/\bend of next week\b/i,/\bthis week\b/i,/\b(?:in|within)\s+\d+\s*(?:-|–|to|or)\s*\d+\s+(?:working|business)\s+days\b/i,/\bin\s+\d+\s+to\s+\d+\s+days\b/i,/\b(?:in|over)\s+(?:the\s+)?next\s+(?:few|couple of)\s+days\b/i,/\bin a (?:few|couple of) days\b/i,/\bnext few days\b/i];
  for(var i=0;i<wins.length;i++){m=wins[i].exec(clean);if(m)return {phrase:m[0],precision:"window"}}
  m=new RegExp("\\bby\\s+(?:"+WD+"|tomorrow|today|(?:the\\s+)?\\d{1,2}(?:st|nd|rd|th)?(?:\\s+of)?\\s+[A-Za-z]+)","i").exec(clean);if(m)return {phrase:m[0],precision:"deadline"};
  m=new RegExp("\\b(?:on\\s+)?(?:"+WD+"|tomorrow|today)(?:\\s+(?:at|between)\\s+[^,.!?]{1,22})?","i").exec(clean);if(m)return {phrase:m[0].trim(),precision:"exact_day"};
  m=/\b(?:on\s+)?(?:the\s+)?\d{1,2}(?:st|nd|rd|th)?(?:\s+of)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)(?:\s+\d{4})?\b/i.exec(clean);if(m)return {phrase:m[0],precision:"exact_day"};
  return neg.length?{phrase:neg[0],precision:"negated"}:{phrase:"",precision:"unknown"};
};
var _truthSync139=truthSync138;
truthSync138=function(t){
  var ch=_truthSync139(t),sp=t&&t.sugP,op=t&&openPromise(t);
  if(t&&t.sugDone&&sp&&op&&String(op.said||"")===String(sp.said||"")&&op.sourceType){
    /* A later, explicit source wins. Undo any stale suggestion metadata that an older sync may have copied over it. */
    if(op.sourceType==="provider_account"){
      ch=truthSet138(op,"precision","exact_day")||ch;op.tentative=false;op.win=false;op.legacyTimingReview=false;
      if(op.sourceText!=="Booking details you confirmed from the provider’s app or email"){op.sourceText="Booking details you confirmed from the provider’s app or email";ch=true}
      if(op.sourceWhen!==String(op.dueAt||"").slice(0,10)){op.sourceWhen=String(op.dueAt||"").slice(0,10);ch=true}
      delete op.candidateDueAt;delete op.candidateDueEnd;
    }else if(op.sourceType==="user_review"){
      ch=truthSet138(op,"precision","unknown")||ch;op.tentative=false;op.win=false;op.legacyTimingReview=false;delete op.candidateDueAt;delete op.candidateDueEnd;
    }
  }
  return !!ch;
};
`;
R("boot();\n})();\n</script>",PATCH+"\nboot();\n})();\n</script>");
fs.writeFileSync('public/index.html',s);
const EXPECT='';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v139 ok',h(s),s.length);
