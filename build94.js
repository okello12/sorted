const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='a801027354df043565265a18f31d88f05a98040a')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v94: only a name ("From hmrc", "letter from the council"): Sorted asks what they sent before starting, and if
// you carry on, the case is named after them, says what it doesn't know, and the message asks what it's about. ----
R("function pkShortBlock(){",
  "var PS_FILL=/^(?:from|a|an|the|my|our|got|had|have|received|recieved|re|about|regarding|something|thing|stuff|to|with|and|i|i've|it|it's|its|is|this|that|letter|letters|email|emails|e-mail|text|texts|message|messages|call|bill|notice|post|today|yesterday|again)$/i;\nvar PS_NOUN=/\\b(letter|email|e-mail|text|message|bill|notice|call)\\b/i;\nfunction psOnly(text,f){\n  var x=String(text||\"\").trim();if(!f||!f.party||x.length>60||/\\d/.test(x))return false;\n  var p=String(f.party).replace(/^the /i,\"\").toLowerCase(),y=x.toLowerCase().replace(/[^a-z0-9'’&\\s-]/g,\" \");\n  y=y.split(p).join(\" \");\n  var rest=y.split(/\\s+/).filter(function(w){return w&&!PS_FILL.test(w.replace(/’/g,\"'\"))});\n  return rest.length===0;\n}\nfunction psName(f){var p=String(f&&f.party||\"\").replace(/^the /i,\"\");return /^[a-z]/.test(p)?p.charAt(0).toUpperCase()+p.slice(1):p}\nfunction psSay(f){var p=String(f&&f.party||\"\");return /^the /i.test(p)?p.toLowerCase():psName(f)}\nfunction psNoun(text){var m=PS_NOUN.exec(String(text||\"\"));return m?m[1].toLowerCase().replace(\"e-mail\",\"email\"):\"\"}\nfunction psShortBlock(p){var P=p.charAt(0).toUpperCase()+p.slice(1);\n  return '<div class=\"note stack-s pk-short ps-short\"><p><strong>Something from '+esc(p)+'.</strong> What did they send or say? Add a photo of it, or add a few words above and press Start, for example “'+esc(P)+' wants £300 by 31 January” or “'+esc(P)+' still hasn’t replied”.</p><div class=\"row eq\"><label class=\"btn primary\">Add a photo<input type=\"file\" accept=\"image/*,application/pdf,.pdf\" data-ocr=\"f-case\" class=\"sr-only\"></label><button type=\"submit\" class=\"btn\">Start</button></div></div>';\n}\nfunction pkShortBlock(){");
R("if(!d.skipPk&&PKSHORT.test(ctx)&&!pcnRead(ctx)){d.pkShort=true;d.casetext=ctx;render();return}",
  "if(!d.skipPk&&PKSHORT.test(ctx)&&!pcnRead(ctx)){d.pkShort=true;d.casetext=ctx;render();return}\n    if(d.psShort&&ctx===d.casetext)d.skipPs=true;\n    if(!d.skipPs){var psf=caseFacts(ctx);if(psOnly(ctx,psf)){d.psShort=psSay(psf);d.casetext=ctx;render();var psb=document.querySelector(\".ps-short\");if(psb)psb.scrollIntoView({block:\"center\"});return}}");
R("    d.pkShort=false;",
  "    d.pkShort=false;d.psShort=\"\";");
R("d.pkShort?pkShortBlock():",
  "d.pkShort?pkShortBlock():d.psShort?psShortBlock(d.psShort):");
R("case \"pk-short-go\":",
  "case \"ps-short-go\":{d.skipPs=true;d.psShort=\"\";var psfm=document.querySelector('form[data-f=\"case\"]');if(psfm){if(psfm.requestSubmit)psfm.requestSubmit();else psfm.dispatchEvent(new Event(\"submit\",{cancelable:true,bubbles:true}))}break}\n    case \"pk-short-go\":");
R("  log(t,t.mode===\"do\"?\"Started.\"",
  "  if(t.said&&t.facts&&psOnly(t.said,t.facts)){var psn=psNoun(t.said);t.title=psName(t.facts)+(psn&&psn!==\"call\"?\" \"+psn:\"\")}\n  log(t,t.mode===\"do\"?\"Started.\"");
R("if(pk)U.push(\"This is a parking ticket\"",
  "var pso=!pk&&psOnly(said,t.facts);if(pso)U.push(\"Something from \"+psSay(t.facts)+\". Sorted doesn’t know yet what it’s about.\");\n  else if(pk)U.push(\"This is a parking ticket\"");
R("if(t.sugP&&!t.sugDone)N=\"Check the promise",
  "if(pso)N=\"Add what they sent, with a photo or by pasting their message, so Sorted can read the dates and reference. Or contact them and ask what it’s about.\";\n  else if(t.sugP&&!t.sugDone)N=\"Check the promise");
R("  else if(t.mode===\"call\"&&t.said){",
  "  else if(t.mode===\"call\"&&t.said&&t.facts&&psOnly(t.said,t.facts)){\n    var psn2=psNoun(t.said);who=cap1(String(t.facts.party));ask=\"I’m getting in touch about \"+(psn2&&psn2!==\"call\"?\"a \"+psn2+\" I had from you\":\"my case with you\")+\". Can you tell me what it’s about, what I need to do and by when, and confirm it in writing?\";\n  }\n  else if(t.mode===\"call\"&&t.said){");
fs.writeFileSync('public/index.html',s);
const EXPECT='79b657262f7eb7821cafa9af393a3a1ba2cb02df';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v94 ok',h(s),s.length);
