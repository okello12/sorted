const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='f030407b7577e550857c1ecfc04a12bb70354f8b')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v47: one page heading on Home. The v44 headline is the h1, so the hidden "Your cases" heading is only for
//      a list of finished cases, and the empty state's heading sits under the box's own h1. ----
R(`var active=needs.length+waiting.length,entryFirst=!active&&S.loaded;\n  if(!entryFirst)h+='<h1 class="sr-only">Your cases</h1>';`,
  `var active=needs.length+waiting.length,entryFirst=!active&&S.loaded;\n  if(S.tasks.length&&!needs.length&&!waiting.length)h+='<h1 class="sr-only">Your cases</h1>';`);
R(`<h1 class="h1">Nothing here yet.</h1>`,`<h2 class="h1">Nothing here yet.</h2>`);
fs.writeFileSync('public/index.html',s);
const EXPECT='074b32a8b976ea666944d5bf258fa9a1a1d878fc';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v47 ok',h(s),s.length);
