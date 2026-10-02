const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='074b32a8b976ea666944d5bf258fa9a1a1d878fc')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v48: Home copy polish ----
// "Needs you" once, at section level; the spotlight card starts with the case itself
R(`<div class="home44-spot-top"><div><span class="home44-kicker">Needs you</span><h2 class="home44-spot-title"`,
  `<div class="home44-spot-top"><div><h2 class="home44-spot-title"`);
// the line under the headline depends on whether anything else is open; "Also open" already explains the list
R(`<p class="lede">Start here. The rest of your open cases are below.</p>`,
  `<p class="lede">'+(needs.length+waiting.length>1?'Deal with this first. Sorted is holding the rest.':'This is the only thing that needs you right now.')+'</p>`);
fs.writeFileSync('public/index.html',s);
const EXPECT='321f34fb75585da4e4f4df63ce67d7b8f7e0f76c';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v48 ok',h(s),s.length);
