const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='69d86b6da5c1ed43d34d729424c9ce2be73a0480')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v43: the seven false promises from the 2 October rigorous test ----


// 1. "They promised nothing", "wouldn't give a date"
R("var PNEG=/\\b(?:no ?one|nobody)\\s+(?:has\\s+|have\\s+|had\\s+)?(?:promised|said|agreed|committed|told)\\b|\\b(?:hasn't|haven't|hadn't|didn't|did not|has not|have not|never|won't|wouldn't|refused to|can't|cannot)\\s+(?:promised?|agreed?|committed?|commit)\\b|\\bno (?:promises?|commitments?)\\b|\\bnothing (?:was |has been |had been )?(?:promised|agreed)\\b/i;",
  "var PNEG=/\\b(?:no ?one|nobody)\\s+(?:has\\s+|have\\s+|had\\s+)?(?:promised|said|agreed|committed|told)\\b|\\b(?:hasn't|haven't|hadn't|didn't|did not|has not|have not|never|won't|wouldn't|refused to|can't|cannot)\\s+(?:promised?|agreed?|committed?|commit)\\b|\\bno (?:promises?|commitments?)\\b|\\bnothing (?:was |has been |had been )?(?:promised|agreed)\\b|\\b(?:promised|agreed|committed to|confirmed|guaranteed)\\s+(?:nothing|no date|no time|anything)\\b|\\b(?:didn't|did not|wouldn't|won't|couldn't|can't|cannot)\\s+(?:give|offer)\\s+(?:me\\s+|us\\s+)?(?:a\\s+|any\\s+)?(?:date|time|guarantee)\\b/i;");

// 2. Conditionals are not promises: "if the part arrives, the engineer may come"
R("var PTENT=/\\b(?:maybe|might|perhaps|possibly|hopefully|probably|could|should|may (?:be|come|arrive|send|call|get|have|need|take|turn))\\b|\\b(?:not sure|unsure|no guarantee|try to|trying to|aim to|hope to|hoping to|if possible|if (?:they|he|she|we) can)\\b/i;",
  "var PTENT=/\\b(?:maybe|might|perhaps|possibly|hopefully|probably|could|should|may (?:be|come|arrive|send|call|get|have|need|take|turn))\\b|\\b(?:not sure|unsure|no guarantee|try to|trying to|aim to|hope to|hoping to|if possible|if (?:they|he|she|we) can)\\b|\\b(?:if|unless|subject to|depending on|provided that|assuming|we hope|we'll try|we will try|in theory)\\b/i;\nvar PTMSG=/\\b(?:maybe|might|perhaps|possibly|hopefully|probably|not sure|no guarantee|may (?:be|come|arrive|send|call|get|have|need|take|turn)|if the|unless|subject to|depending on|we hope|we'll try|we will try)\\b/i;");

// 3. Information and instructions: opening times, availability, "please call", "check back", "told me to"
R("var PINFO=/\\b(?:lines are open|opening hours|office hours|we(?:'re| are) open|open (?:from )?(?:mon|monday)|call us|ring us|contact us|phone us|email us|get in touch|if you still need|if it still|if you need|if you have any)\\b/i;",
  "var PINFO=/\\b(?:lines are open|opening hours|office hours|we(?:'re| are) open|open (?:from )?(?:mon|monday)|call us|ring us|contact us|phone us|email us|get in touch|if you still need|if it still|if you need|if you have any)\\b|\\b(?:shop|store|branch|office|lines?|we|it|they)\\s+(?:closes?|opens?)\\b|\\b(?:be|are|is|'re)\\s+(?:open|closed)\\b|\\b(?:available|availability|free slots?|next available)\\b|\\b(?:told|asked)\\s+(?:me|us)\\s+to\\b|\\b(?:usually|normally|typically|generally|can take|may take|takes? up to)\\b/i;\nvar PIMP=/^(?:please\\s+(?!allow|note|be aware)|(?:call|ring|phone|email|text|contact|check|try|chase|write|come back|get back|go|visit|log in|wait|send|reply|respond|book|ask|keep|look)\\b)/i;");
R("  if(PTENT.test(clause)||PINFO.test(clause))return null;",
  "  if(PTENT.test(clause)||PINFO.test(clause)||PIMP.test(clause.replace(/^that\\s+/i,\"\")))return null;");

// 4. The same checks for each sentence of a pasted message
R("    if(/\\b(?:maybe|might|perhaps|possibly|hopefully|probably|not sure|no guarantee)\\b/i.test(pt))continue;   /* not definite */",
  "    if(PTMSG.test(pt)||PIMP.test(pt))continue;   /* not definite, or an instruction to you */");

fs.writeFileSync('public/index.html',s);
const EXPECT='523d54d100a27dc509819e2f4197d6061e564b96';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v43 ok',h(s),s.length);
