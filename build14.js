const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='9a8bbc6cec58b19825563d49ed8a6ec12e6df4c4')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+String(a).slice(0,70));s=s.split(a).join(b)}
// ---- v14: the working home puts cases first ----
// the entry: not everything has "gone wrong"; smaller once there are cases; no error until Start is pressed empty
R(`<h1 class="h1">What’s gone wrong?</h1>`,`'+(S.tasks.length?'<h2 class="h2">What do you need to sort out?</h2>':'<h1 class="h1">What do you need to sort out?</h1>')+'`);
R(`(d.err&&S.view.name==="home"?'<p class="err">'+esc(d.err)+'</p>':'')`,`(d.caseErr?'<p class="err">'+esc(d.caseErr)+'</p>':'')`);
R(`For example “Landlord still hasn’t fixed the heating” or “Refund from Currys hasn’t arrived”.`,`For example “Landlord still hasn’t fixed the heating”, “Refund from Currys hasn’t arrived” or “Bursary documents due Friday”.`);
R(`if(ctx.length<3){d.err="Tell Sorted what’s gone wrong, in a few words.";render();return}`,`if(ctx.length<3){d.caseErr="Type a few words first, then press Start.";render();return}\n    d.caseErr="";`);
R(`  S.draft[el.name]=el.value;`,`  S.draft[el.name]=el.value;\n  if(el.name==="casetext"&&S.draft.caseErr){S.draft.caseErr="";var cer=el.form&&el.form.querySelector(".err");if(cer)cer.remove()}`);
// home order: what needs you first, then the box; big art only on a genuinely empty home (after cases have loaded)
R(`  if(!S.tasks.length)h+=art("hero-case","hero",true);
  h+=caseEntry();
  h+=anonNote();
  h+=inboxBlock();
  if(!S.tasks.length){`,`  var entryFirst=!yours.length;
  if(!S.tasks.length&&S.loaded)h+=art("hero-case","hero",true);
  if(entryFirst)h+=caseEntry();
  h+=anonNote();
  h+=inboxBlock();
  if(!S.tasks.length&&!S.loaded){
    h+='<p class="muted">Opening your cases…</p>';
  }else if(!S.tasks.length){`);
R(`    h+=group("Needs you",yours);\n`,`    h+=group("Needs you",yours);\n    if(!entryFirst)h+=caseEntry();\n`);
R(`h+='<section class="calm stack-s">'+art("state-waiting","hero")+'<p class="h2">`,`h+='<section class="calm stack-s">'+art("state-waiting","context")+'<p class="h2">`);
// know when the cases have actually arrived
R(`    offline(false);
    var dirty=S.tasks.filter(function(t){return t._dirty});`,`    offline(false);S.loaded=true;
    var dirty=S.tasks.filter(function(t){return t._dirty});`);
R(`  if(!u){S.tasks=[];S.booting=false;render();return}`,`  S.loaded=false;\n  if(!u){S.tasks=[];S.booting=false;render();return}`);

// your own deadlines are not problems: route them to "Your move"
R("  if(/\\b(broken|broke|","  if(!/\\b(refund|landlord|repair|broken|not working|money back|engineer)/.test(s)&&/\\b(deadline|due|submit|send|apply|application|bursary|form|pay|tax return|by (monday|tuesday|wednesday|thursday|friday|saturday|sunday)|tomorrow)\\b/.test(s))return \"do\";\n  if(/\\b(broken|broke|");
R('S.view={name:"new",mode:cm};S.draft={step:"baseline",title:ctitle,baseline:"",fromCase:true};','if(cm==="do"){S.view={name:"new",mode:"do"};S.draft={title:ctitle,baseline:"",fromCase:true};newTask("do");return}\n    S.view={name:"new",mode:cm};S.draft={step:"baseline",title:ctitle,baseline:"",fromCase:true};');

fs.writeFileSync('public/index.html',s);
const EXPECT='b04faec3a0920092ab6cbf20b9233e850e3fb736';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v14 ok',h(s),s.length);
