const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='4f1a841e869d2eb0b31f2299dd0c5879e101c3d6')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v132: a finished case offers Reopen this case and Save the full record on its finished card. ----
R("<button class=\"btn block quiet\" data-a=\"new-case\">+ Start something new</button></div>",
  "<button class=\"btn block quiet\" data-a=\"new-case\">+ Start something new</button></div><div class=\"rc132\"><p class=\"h3\" style=\"margin:0\">Need it again?</p><div class=\"row eq\"><button class=\"btn\" data-a=\"case-reopen\">Reopen this case</button><button class=\"btn\" data-a=\"panel\" data-p=\"pack\">Save the full record</button></div><p class=\"muted\" style=\"font-size:15px;margin:0\">Reopening keeps everything: its history, messages, references and dates. The full record is a file of all of it, for evidence or an adviser.</p></div>");
R("<p class=\"muted\" style=\"font-size:15px\">Sorted keeps finished cases for 90 days after your last change, or 30 days if you haven’t added an email, in case the problem comes back.</p></section>';",
  "<p class=\"muted\" style=\"font-size:15px\">Finished cases stay under Done in Cases. Sorted keeps them for 90 days after your last change, or 30 days if you haven’t added an email. To keep it for longer, save the full record.</p></section>';");
R(".home131-start{font-weight:700}",
  ".home131-start{font-weight:700}\n.rc132{display:grid;gap:10px;padding-top:6px;border-top:1px solid var(--rule)}\n.rc132 .btn{min-height:48px}");
R("var SORTED_V=\"v131\"",
  "var SORTED_V=\"v132\"");
fs.writeFileSync('public/index.html',s);
const EXPECT='ec8f1676239ca423e456c491b39acd589b65fcef';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v132 ok',h(s),s.length);
