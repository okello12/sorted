const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='3ecb4ca1db0e54db26bdd29d46d89477f98a4aa3')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,70));s=s.split(a).join(b)}
// ---- v171: the document door, from Baldwin's walk on 20 October 2026 ("From hmrc" typed into the door).
// 1. One line under the photo button instead of three overlapping sentences, and "letter" throughout (the button
//    already said letter; the text said notice).
// 2. A name on its own in the document door ("From hmrc") keeps asking for the letter. The general box still carries
//    on at a second Start (test 48); the door came with a letter, so the letter is what Sorted asks for, with the
//    same two routes (a photo, or a few words). Nothing is saved until the letter or some words are there.
R("Sorted reads it on your phone. Nothing is uploaded. Sorted tries to read the notice. Check the details before continuing. For a scanned PDF, only the first page is read.",
  "Sorted reads it on your phone. Nothing is uploaded. Check what it found before you continue. For a scanned PDF, only the first page is read.");
R("    if(d.psShort&&ctx===d.casetext)d.skipPs=true;\n",
  "    if(d.psShort&&ctx===d.casetext){if(giKind()===\"document\")d.psAgain171=true;else d.skipPs=true}\n");
R("function psShortBlock(p){var P=p.charAt(0).toUpperCase()+p.slice(1);\n  return '<div class=\"note stack-s pk-short ps-short\"><p><strong>Something from '+esc(p)+'.</strong> What did they send or say? Add a photo of it, or add a few words above and press Start, for example “'+esc(P)+' wants £300 by 31 January” or “'+esc(P)+' still hasn’t replied”.</p>",
  "function psShortBlock(p){var P=p.charAt(0).toUpperCase()+p.slice(1),isDoc171=giKind()===\"document\",again171=isDoc171&&S.draft&&S.draft.psAgain171;\n  return '<div class=\"note stack-s pk-short ps-short\"><p><strong>Something from '+esc(p)+'.</strong> '+(isDoc171?'What does the letter say? Add a photo of it, or type a few words above, for example “'+esc(P)+' wants £300 by 31 January” or “'+esc(P)+' still hasn’t replied”.':'What did they send or say? Add a photo of it, or add a few words above and press Start, for example “'+esc(P)+' wants £300 by 31 January” or “'+esc(P)+' still hasn’t replied”.')+'</p>'+(again171?'<p class=\"err\" role=\"alert\" style=\"margin:0\">To start, add a photo of the letter or a few words about what it says.</p>':'')+'");
R("    d.pkShort=false;d.psShort=\"\";\n    d.caseErr=\"\";\n","    d.pkShort=false;d.psShort=\"\";d.psAgain171=false;\n    d.caseErr=\"\";\n");
R('SORTED_V="v170"','SORTED_V="v171"');
fs.writeFileSync('public/index.html',s);
const EXPECT='fb39271410fe76acf86511b0475dd9b8f330d181';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v171 ok',h(s),s.length);
