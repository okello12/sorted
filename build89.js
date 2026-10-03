const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='485a1332b6ee019632585a1cda7d0cd8087c835b')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,120));s=s.split(a).join(b)}
R("new MutationObserver(function(){tune()}).observe(document.documentElement,{childList:true,subtree:true});","document.addEventListener('click',function(){setTimeout(tune,80);setTimeout(tune,300)},false);document.addEventListener('submit',function(){setTimeout(tune,80);setTimeout(tune,300)},true);window.addEventListener('hashchange',function(){setTimeout(tune,50);setTimeout(tune,220)});");
fs.writeFileSync('public/index.html',s);
const EXPECT='cb714d9ff7bc393d6270ddc70624c1964a4ddef7';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v89 event-driven pwa polish',h(s),s.length);
