const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='bb73812b7d2d6de7e8f7d19bc6080be4d8a779aa')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v51: intake, first slice. One door into an existing case, one reader, every message kept as evidence with its source ----


// 1. One reader for everything brought into an existing case, and one way to keep it as evidence
R("function readCase(t,f){",
  "function intakeRead(x,t,f){var lng=x.length>100||/\\n/.test(x);return lng?(sugFromMessage(x,t,f)||suggestPromise(x,f)):(suggestPromise(x,f)||sugFromMessage(x,t,f))}\nfunction evidence(t,x,src){x=String(x||\"\").replace(/\\s+/g,\" \").trim();if(x.length>200)x=x.slice(0,197).replace(/\\s+\\S*$/,\"\")+\"…\";log(t,\"Added \"+(src||\"a message\")+\": “\"+x.replace(/[.!]+$/,\"\")+\"”\")}\nfunction readCase(t,f){");

// 2. Screenshots and PDFs say where their words came from
R("var tok=S.ocrTok={v:S.view.name+\":\"+(S.view.id||\"\")+\":\"+target};",
  "var tok=S.ocrTok={v:S.view.name+\":\"+(S.view.id||\"\")+\":\"+target,src:isPdf?\"a PDF\":\"a screenshot\"};");
R("var ta=document.getElementById(target);if(ta){ta.value=txt;S.draft[ta.name===\"paste\"?\"paste\":\"casetext\"]=txt}",
  "var ta=document.getElementById(target);if(ta){ta.value=txt;S.draft[ta.name===\"paste\"?\"paste\":\"casetext\"]=txt;if(tok&&tok.src)S.draft.src=tok.src}");

// 3. Adding to a matched case uses the shared reader and keeps the message with its source
R("      var mf=Object.assign({},mx.facts||{},caseFacts(mtx)),msg=sugFromMessage(mtx,mx,mf)||suggestPromise(mtx,mf);\n      log(mx,\"Added a message: “\"+(mtx.length>140?mtx.slice(0,137).replace(/\\s+\\S*$/,\"\")+\"…\":mtx)+\"”\");mx._dirty=true;",
  "      var mf=Object.assign({},mx.facts||{},caseFacts(mtx)),msg=intakeRead(mtx,mx,mf);\n      evidence(mx,mtx,d.src||(d.fromShare?\"a message shared from another app\":\"\"));mx._dirty=true;");

// 4. Pasting into a case keeps the message even when there is no date in it
R("    var psg=sugFromMessage(ptx,t,t.facts);\n    if(!psg){d.err=\"Sorted couldn’t find a date or time in that. You can still log what they said yourself.\";render();return}\n    t.sugP=psg;t.sugDone=false;t._dirty=true;log(t,\"Pasted a message they sent.\");S.view.panel=null;S.draft={};commit();window.scrollTo(0,0);return;",
  "    var psg=intakeRead(ptx,t,t.facts);\n    if(d.kept!==ptx){evidence(t,ptx,d.src);d.kept=ptx}\n    if(!psg){save();d.err=\"Added to the case. Sorted couldn’t find a date in it, so nothing else changed.\";render();return}\n    t.sugP=psg;t.sugDone=false;t._dirty=true;S.view.panel=null;S.draft={};commit();window.scrollTo(0,0);return;");

fs.writeFileSync('public/index.html',s);
const EXPECT='107e873bd5f6b1854680491c25542cb9f86999c0';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v51 ok',h(s),s.length);
