const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='e85685844d0348a06ba6852123ec0cb1100d77dd')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v56: a case started from a message gets a clear name (company and what's happening) when its first line would be cut off or a pleasantry; the share picker uses Home's titles ----
R("function shortTitle(text,f){",
  "var TOPICS=[[/\\bengineers?\\b/i,\"engineer visit\"],[/\\bplumbers?\\b/i,\"plumber visit\"],[/\\belectricians?\\b/i,\"electrician visit\"],[/\\binspect/i,\"inspection\"],[/\\binstall/i,\"installation\"],[/\\bcall(?:ing)? (?:you |me )?back\\b|\\bcallback\\b/i,\"callback\"],[/\\b(?:parcel|package|delivery|deliver(?:ed)?|redelivery)\\b/i,\"delivery\"],[/\\bappointment\\b/i,\"appointment\"],[/\\brepairs?\\b/i,\"repair\"],[/\\bclaim\\b/i,\"claim\"],[/\\bcomplaint\\b/i,\"complaint\"],[/\\b(?:bill|invoice|overcharg\\w*)\\b/i,\"bill\"]];\nfunction caseTopic(text){\n  var x=String(text||\"\"),m=/\\breplacement(?:\\s+([a-z]{3,}))?/i.exec(x),stop=/^(?:will|is|has|was|for|of|to|on|and|item|order|should|would|can|could|be)$/i;\n  if(m)return \"replacement\"+(m[1]&&!stop.test(m[1])?\" \"+m[1].toLowerCase():\"\");\n  for(var i=0;i<TOPICS.length;i++)if(TOPICS[i][0].test(x))return TOPICS[i][1];\n  return \"\";\n}\nfunction namedTitle(text,f){var tp=caseTopic(text),pn=f&&f.party?String(f.party).replace(/^the /,\"\"):\"\",rf=f&&f.ref?\" · \"+f.ref:\"\";return pn&&tp?pn+\" \"+tp+rf:(pn&&rf?pn+rf:\"\")}\nfunction shortTitle(text,f){");
R("  if(c.length>48){c=c.slice(0,48);c=c.slice(0,Math.max(c.lastIndexOf(\" \"),20))+\"…\"}\n  return cap1(c);",
  "  if(c.length>48||/^(?:thanks|thank you|many thanks|sorry|we apologi[sz]e|good news|great news|your |we |please |this is |re:|fw:|fwd:)/i.test(c)){\n    var nt=namedTitle(text,f);if(nt)return nt;\n  }\n  if(c.length>48){c=c.slice(0,48);c=c.slice(0,Math.max(c.lastIndexOf(\" \"),20))+\"…\"}\n  return cap1(c);");
R("if(t.facts)t.titleFb=!(t.facts.kind===\"money\"||t.facts.kind===\"benefit\"||(t.facts.item&&t.mode===\"fix\"));",
  "if(t.facts)t.titleFb=!(t.facts.kind===\"money\"||t.facts.kind===\"benefit\"||(t.facts.item&&t.mode===\"fix\")||(t.said&&t.title===namedTitle(t.said,t.facts)));");
R("<span class=\"share-t\">'+esc(x.title)+'</span>",
  "<span class=\"share-t\">'+esc(home54Title(x))+'</span>");
R("'</form><p class=\"muted\" style=\"font-size:15px\">For example “Landlord still hasn’t fixed the heating” or “Refund from Currys hasn’t arrived”.</p></section>'",
  "'</form>'+(sharePicking(d)?'':'<p class=\"muted\" style=\"font-size:15px\">For example “Landlord still hasn’t fixed the heating” or “Refund from Currys hasn’t arrived”.</p>')+'</section>'");
R("  if(!/^Did it happen\\??$/i.test(original))return original;",
  "  if(!/^(?:Did it happen|Has it happened|Did they come|Has the money arrived)\\??$/i.test(original))return original;");
fs.writeFileSync('public/index.html',s);
const EXPECT='08e6ce3a01d8ab3f772ade1dcbb0f346d2be8473';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v56 ok',h(s),s.length);
