const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='321f34fb75585da4e4f4df63ce67d7b8f7e0f76c')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v49: the 345-sentence adversarial corpus (tests/corpus.py): 30 false promises in five patterns ----


// 1. Pasted messages and longer sentences get the full set of conditions and maybes
R("var PTMSG=/\\b(?:maybe|might|perhaps|possibly|hopefully|probably|not sure|no guarantee|may (?:be|come|arrive|send|call|get|have|need|take|turn)|if the|unless|subject to|depending on|we hope|we'll try|we will try)\\b/i;",
  "var PTMSG=/\\b(?:maybe|might|perhaps|possibly|hopefully|probably|not sure|no guarantee|may (?:be|come|arrive|send|call|get|have|need|take|turn)|if|unless|subject to|depending on|as long as|provided|providing|once (?:the|it|we|you|they|your|our|this)|assuming|we hope|hope to|hoping to|we'll try|we will try|try to|trying to|aim to|aiming to|if possible|can't guarantee|cannot guarantee)\\b/i;");

// 2. More conditions in a sentence: "as long as", "once the claim is approved"
R("var PTENT=/\\b(?:maybe|might|perhaps|possibly|hopefully|probably|could|should|may (?:be|come|arrive|send|call|get|have|need|take|turn))\\b|\\b(?:not sure|unsure|no guarantee|try to|trying to|aim to|hope to|hoping to|if possible|if (?:they|he|she|we) can)\\b|\\b(?:if|unless|subject to|depending on|provided that|assuming|we hope|we'll try|we will try|in theory)\\b/i;",
  "var PTENT=/\\b(?:maybe|might|perhaps|possibly|hopefully|probably|could|should|may (?:be|come|arrive|send|call|get|have|need|take|turn))\\b|\\b(?:not sure|unsure|no guarantee|try to|trying to|aim to|hope to|hoping to|if possible|if (?:they|he|she|we) can)\\b|\\b(?:if|unless|subject to|depending on|provided that|assuming|we hope|we'll try|we will try|in theory)\\b|\\b(?:as long as|provided|providing|once (?:the|it|we|you|they|your|our|this)|aiming to)\\b/i;");

// 3. Sales and offers ending are information; "said to call back", "told me to ring" are instructions
R("var PINFO=/\\b(?:lines are open|opening hours|office hours|we(?:'re| are) open|open (?:from )?(?:mon|monday)|call us|ring us|contact us|phone us|email us|get in touch|if you still need|if it still|if you need|if you have any)\\b|\\b(?:shop|store|branch|office|lines?|we|it|they)\\s+(?:closes?|opens?)\\b|\\b(?:be|are|is|'re)\\s+(?:open|closed)\\b|\\b(?:available|availability|free slots?|next available)\\b|\\b(?:told|asked)\\s+(?:me|us)\\s+to\\b|\\b(?:usually|normally|typically|generally|can take|may take|takes? up to)\\b/i;",
  "var PINFO=/\\b(?:lines are open|opening hours|office hours|we(?:'re| are) open|open (?:from )?(?:mon|monday)|call us|ring us|contact us|phone us|email us|get in touch|if you still need|if it still|if you need|if you have any)\\b|\\b(?:shop|store|branch|office|lines?|we|it|they)\\s+(?:closes?|opens?)\\b|\\b(?:be|are|is|'re)\\s+(?:open|closed)\\b|\\b(?:available|availability|free slots?|next available)\\b|\\b(?:told|asked)\\s+(?:me|us)\\s+to\\b|\\b(?:usually|normally|typically|generally|can take|may take|takes? up to)\\b|\\b(?:sale|sales|offer|offers|deal|deals|promotion|discount|price|prices)\\s+(?:ends?|expires?|finish(?:es)?|runs? (?:out|until))\\b/i;\nvar PSAIDDO=/\\b(?:said|told (?:me|us)|asked (?:me|us))\\s+(?:that\\s+)?(?:to\\s+)?(?:please\\s+)?(?:call|ring|phone|email|text|contact|check|try|chase|write|come back|get back|go|visit|log in|wait|send|reply|respond|book|ask|keep|look)\\b/i;");

// 4. "Can't guarantee", "couldn't confirm"
R("var PNEG=/\\b(?:no ?one|nobody)\\s+(?:has\\s+|have\\s+|had\\s+)?(?:promised|said|agreed|committed|told)\\b|\\b(?:hasn't|haven't|hadn't|didn't|did not|has not|have not|never|won't|wouldn't|refused to|can't|cannot)\\s+(?:promised?|agreed?|committed?|commit)\\b|\\bno (?:promises?|commitments?)\\b|\\bnothing (?:was |has been |had been )?(?:promised|agreed)\\b|\\b(?:promised|agreed|committed to|confirmed|guaranteed)\\s+(?:nothing|no date|no time|anything)\\b|\\b(?:didn't|did not|wouldn't|won't|couldn't|can't|cannot)\\s+(?:give|offer)\\s+(?:me\\s+|us\\s+)?(?:a\\s+|any\\s+)?(?:date|time|guarantee)\\b/i;",
  "var PNEG=/\\b(?:no ?one|nobody)\\s+(?:has\\s+|have\\s+|had\\s+)?(?:promised|said|agreed|committed|told)\\b|\\b(?:hasn't|haven't|hadn't|didn't|did not|has not|have not|never|won't|wouldn't|refused to|can't|cannot)\\s+(?:promised?|agreed?|committed?|commit)\\b|\\bno (?:promises?|commitments?)\\b|\\bnothing (?:was |has been |had been )?(?:promised|agreed)\\b|\\b(?:promised|agreed|committed to|confirmed|guaranteed)\\s+(?:nothing|no date|no time|anything)\\b|\\b(?:didn't|did not|wouldn't|won't|couldn't|can't|cannot)\\s+(?:give|offer)\\s+(?:me\\s+|us\\s+)?(?:a\\s+|any\\s+)?(?:date|time|guarantee)\\b|\\b(?:can't|cannot|can not|couldn't|could not|won't|wouldn't|refused to|unable to)\\s+(?:guarantee|confirm)\\b/i;");

// 5. Use them in the sentence reader
R("  if(PTENT.test(clause)||PINFO.test(clause)||PIMP.test(clause.replace(/^that\\s+/i,\"\")))return null;",
  "  if(PTENT.test(clause)||PINFO.test(clause)||PIMP.test(clause.replace(/^that\\s+/i,\"\"))||PSAIDDO.test(s))return null;");

// ... and in the message reader
R("    if(PTMSG.test(pt)||PIMP.test(pt))continue;   /* not definite, or an instruction to you */",
  "    if(PTMSG.test(pt)||PIMP.test(pt)||PSAIDDO.test(pt))continue;   /* not definite, or an instruction to you */");

fs.writeFileSync('public/index.html',s);
const EXPECT='a7437d3a5700eaa29f69b83533df3716f7eae338';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v49 ok',h(s),s.length);
