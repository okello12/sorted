const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='e4dde7b16f62345fb0952eb672088f684a00a2a5')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v40: borrowed from Things 3 (2 October 2026) ----


// 1. Share into Sorted from any app. An Apple Shortcut in the share sheet opens /#new=<text>. The text travels after the #,
//    which browsers never send to the server, so it can't reach Vercel's logs. The page only fills the box: nothing is
//    saved until the person presses Start.
R("function boot(){\n",
  "function grabShared(){\n  var m=/^#new=([\\s\\S]*)$/.exec(location.hash||\"\");if(!m)return false;\n  var tx=\"\";try{tx=decodeURIComponent(m[1])}catch(e){tx=m[1]}\n  tx=tx.replace(/\\r/g,\"\").trim().slice(0,4000);\n  try{history.replaceState(null,\"\",location.pathname+location.search)}catch(e){}\n  if(!tx)return false;\n  S.sharedIn=tx;try{sessionStorage.setItem(\"sorted.sharedIn\",tx)}catch(e){}\n  return true;\n}\nfunction boot(){\n  if(!grabShared()){try{var ssx=sessionStorage.getItem(\"sorted.sharedIn\");if(ssx)S.sharedIn=ssx}catch(e){}}\n");
R("window.addEventListener(\"hashchange\",function(){",
  "window.addEventListener(\"hashchange\",function(){if(/^#new=/.test(location.hash)&&grabShared()&&S.user){S.view={name:\"home\"};render();window.scrollTo(0,0)}});\nwindow.addEventListener(\"hashchange\",function(){");
R("function viewHome(){",
  "function viewHome(){\n  if(S.sharedIn&&S.user){S.draft={casetext:S.sharedIn,fromShare:true};S.sharedIn=null;try{sessionStorage.removeItem(\"sorted.sharedIn\")}catch(e){}S.composeOpen=true;S.draft.matchId=null}");
R("<form class=\"stack-s\" data-f=\"case\">",
  "<form class=\"stack-s\" data-f=\"case\">'+(S.draft.fromShare?'<p class=\"note\">Shared into Sorted. Check the words and take out anything it doesn’t need, like account numbers. Nothing is saved until you press Start.</p>':'')+'");

// 2. Like a start date and a deadline: say exactly when Sorted will check, and what it will ask
R("</p><p>Nothing to do until then. Sorted brings this back to the top of your list when it’s due.</p>",
  "</p><p>Nothing to do until then. Afterwards, Sorted brings this back to the top of your list and asks you: “'+esc(askFor(p)[0])+'”</p>");

// 3. The relief, in plain words
R("<p class=\"lede\">One calm place to work out what to do, keep track of what people promise, and come back when it matters.</p>",
  "<p class=\"lede\">One calm place for problems where someone else owes you the next move. You don’t have to keep remembering whether they got back to you.</p>");

fs.writeFileSync('public/index.html',s);
const EXPECT='15278abd8a8431350f97cb8ddfec2231d60c7904';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v40 ok',h(s),s.length);
