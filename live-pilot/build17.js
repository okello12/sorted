const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='153ec7b8e8445584541aa853775929a11e6237ee')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+String(a).slice(0,70));s=s.split(a).join(b)}
// ---- v17: honest front door ----
// 1. read the link error before anything strips it from the address bar
R(`var sb = window.supabase.createClient(`,`var LINK_ERR=(function(x){return /otp_expired/.test(x)?"expired":/error_description|access_denied|error_code/.test(x)?"bad":null})(location.hash||"");
function pendingTitle(){
  if(!S.pending)return "";
  try{for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);if(k.indexOf("sorted.cache.")!==0)continue;var a=JSON.parse(localStorage.getItem(k)||"[]");if(!Array.isArray(a))continue;for(var j=0;j<a.length;j++)if(a[j]&&a[j].id===S.pending.id&&a[j].title)return a[j].title}}catch(e){}
  return "";
}
var sb = window.supabase.createClient(`);
// an expired link with no task still lands on sign-in, not the marketing page
R(`  var hq=qs.get("helper"),ht=qs.get("h");`,`  if(LINK_ERR&&!tk){try{history.replaceState(null,"",location.pathname+"#signin")}catch(e){}}
  var hq=qs.get("helper"),ht=qs.get("h");`);
// 2. say the link expired, and name the task when this phone knows it
R(`  var h='<section class="stack-s"><a class="link" href="#" style="align-self:flex-start">← Back</a><h1 class="h2">Sign in to Sorted</h1><p class="lede">'+(S.pending?"Sign in to open your task.":"New here or coming back, it works the same way.")+'</p></section>';`,
`  var pt=pendingTitle();
  var h='<section class="stack-s"><a class="link" href="#" style="align-self:flex-start">← Back</a><h1 class="h2">Sign in to Sorted</h1>';
  if(LINK_ERR&&!d.sent)h+='<div class="note linkerr" role="alert"><p><strong>'+(LINK_ERR==="expired"?"This email link has expired.":"This email link didn’t work. It may already have been used.")+'</strong> '+(S.pending?"Sign in again and we’ll open the same task. Your task is still here.":"Sign in again below. Your tasks are still here.")+'</p></div>';
  h+='<p class="lede">'+(S.pending?(pt?'Sign in to open: <strong>'+esc(pt)+'</strong>':"Sign in to open the task from your email."):"New here or coming back, it works the same way.")+'</p></section>';`);
// 3. the homepage says what this is, and the policy has its own page
R(`<p class="lede">One calm place to work out what to do, keep track of what people promise, and come back when it matters.</p>`,`<p class="lede">One calm place to work out what to do, keep track of what people promise, and come back when it matters.</p><p class="pilot-line">A UK research pilot. You can start without an account. Idle tasks are deleted after 90 days.</p>`);
R(`  if(location.hash==="#signin")return h+signInBlock(d)+'</main>';
  if(location.hash==="#start")return h+startBlock(d)+'</main>';`,`  if(location.hash==="#signin")return h+signInBlock(d)+'</main>'+siteFoot();
  if(location.hash==="#start")return h+startBlock(d)+'</main>'+siteFoot();
  if(location.hash==="#privacy")return h+'<section class="stack-s"><a class="link" href="#" style="align-self:flex-start">← Back</a><h1 class="h2">How Sorted handles your data</h1></section>'+privacyBlock()+'<a class="btn primary" href="#start" style="align-self:flex-start">Get something sorted →</a></main>'+siteFoot();`);
R(`'+landingExamples();
  return h+'</main>';`,`'+landingExamples();
  return h+'</main>'+siteFoot();`);
R(`function landingExamples(){`,`function siteFoot(){
  return '<footer class="foot"><p>Sorted is a UK research pilot run by Baldwin Thompson-Addo in London. Your tasks are stored in London and idle tasks are deleted after 90 days.</p><p><a class="link" href="#privacy">How Sorted handles your data</a> · <a class="link" href="#signin">Sign in</a></p></footer>';
}
function landingExamples(){`);
R(`.hero{display:flex;flex-direction:column;gap:14px;padding-top:6px}`,`.hero{display:flex;flex-direction:column;gap:14px;padding-top:6px}
.pilot-line{font-size:16px;color:var(--ink-2);margin:0;padding:8px 12px;border:1px solid var(--rule);border-radius:6px;align-self:flex-start;max-width:34em}
.linkerr{border:2px solid var(--ink);background:var(--sheet)}
.foot{max-width:640px;margin:40px auto 24px;padding:18px 16px 0;border-top:1px solid var(--rule);font-size:15px;color:var(--ink-2);display:flex;flex-direction:column;gap:8px}
.foot p{margin:0}`);
// the signed-in data page links to the same policy page for anyone reading it later
fs.writeFileSync('public/index.html',s);
const EXPECT='f7a51d75f598e4891479edfe80469ad981ab224d';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v17 ok',h(s),s.length);
