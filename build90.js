const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='cb714d9ff7bc393d6270ddc70624c1964a4ddef7')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,100));s=s.split(a).join(b)}
R('</head>',String.raw`<style>
/* v90: compact case handoff after a chooser selection. */
html.cap90-intake .cap90-intake-art{display:none!important}
html.cap90-intake .cap87-empty-cases{display:none!important}
html.cap90-intake main{padding-top:4px}
@media(max-width:520px){html.cap90-intake .h1{margin-top:2px}}
</style>
</head>`);
R('</body>',String.raw`<script>
(function(){
  var last='';
  var MAP={
    fix:['What’s broken?','Tell Sorted what stopped working and what has happened so far.','Tell Sorted what is broken and what has happened so far…'],
    call:['What’s the call about?','Tell Sorted who you need to contact and what you need from them.','Who do you need to call, and what do you need from them?…'],
    promise:['What did they promise?','Tell Sorted what they said they would do and when.','What did they promise, and by when?…'],
    chase:['What are you chasing?','Tell Sorted what you are waiting for and who needs to act.','What are you waiting for, and who needs to act?…'],
    document:['What did you receive?','Tell Sorted what the letter or document is about, or add it below.','What did you receive, and what does it seem to be about?…'],
    renew:['What needs renewing or sorting?','Tell Sorted what it is and any deadline you already know.','What needs renewing or sorting, and is there a deadline?…']
  };
  function choice(){try{return last||sessionStorage.getItem('cap90.choice')||sessionStorage.getItem('sorted.cap82')||''}catch(e){return last}}
  function hideLargeArt(main,heading){
    if(!main||!heading)return;
    var hy=heading.getBoundingClientRect().top;
    Array.from(main.querySelectorAll('img,picture,figure,svg,[class*="hero-art"],[class*="illustration"],[class*="artwork"]')).forEach(function(el){
      var target=el.closest('picture,figure,[class*="hero-art"],[class*="illustration"],[class*="artwork"]')||el;
      if(target.closest('.cap82-card,.cap87-appnav'))return;
      var r=target.getBoundingClientRect();
      if(r.width>=170&&r.height>=100&&r.bottom<=hy+50)target.classList.add('cap90-intake-art');
    });
    Array.from(main.children).forEach(function(el){
      if(el===heading||el.contains(heading)||el.querySelector('#f-case'))return;
      var r=el.getBoundingClientRect(),cs=getComputedStyle(el);
      if(r.width>=220&&r.height>=120&&r.bottom<=hy+50&&cs.backgroundImage&&cs.backgroundImage!=='none')el.classList.add('cap90-intake-art');
    });
  }
  function hideEmpty(){
    Array.from(document.querySelectorAll('h1,h2,h3,p,div,section')).filter(function(e){return (e.textContent||'').trim()==='Nothing here yet.'}).forEach(function(h){
      var p=h.parentElement;while(p&&p!==document.body){var t=(p.textContent||'');if(/YOUR CASES|Your cases/.test(t)){p.classList.add('cap87-empty-cases');break}p=p.parentElement}
    });
  }
  function tune(){
    var ta=document.querySelector('#f-case');
    if(!ta){document.documentElement.classList.remove('cap90-intake');return}
    document.documentElement.classList.add('cap90-intake');
    var main=ta.closest('main')||document.querySelector('main')||document.body;
    var hs=Array.from(main.querySelectorAll('h1,h2'));
    var heading=hs.find(function(e){var t=(e.textContent||'').trim();return t==='What do you need to sort out?'||/^What’s broken\?$/.test(t)||/^What did they promise\?$/.test(t)||/^What are you chasing\?$/.test(t)||/^What’s the call about\?$/.test(t)||/^What did you receive\?$/.test(t)||/^What needs renewing or sorting\?$/.test(t)})||hs[0];
    var c=MAP[choice()];
    if(c&&heading){heading.textContent=c[0];var lede=Array.from(main.querySelectorAll('p')).find(function(e){return /Tell Sorted in one sentence|Tell Sorted what stopped working|Tell Sorted who you need to contact|Tell Sorted what they said|Tell Sorted what you are waiting|Tell Sorted what the letter|Tell Sorted what it is/.test(e.textContent||'')});if(lede)lede.textContent=c[1];ta.setAttribute('placeholder',c[2])}
    hideLargeArt(main,heading);hideEmpty();
  }
  function afterChoice(){setTimeout(tune,0);setTimeout(tune,120);setTimeout(tune,320)}
  document.addEventListener('click',function(e){
    var b=e.target.closest&&e.target.closest('[data-cap82]');
    if(b){last=b.getAttribute('data-cap82')||'';try{sessionStorage.setItem('cap90.choice',last)}catch(x){}afterChoice();return}
    if(e.target.closest&&e.target.closest('[data-cap87=home]'))document.documentElement.classList.remove('cap90-intake');
  },true);
  document.addEventListener('submit',function(){if(document.querySelector('#f-case')){setTimeout(tune,80);setTimeout(tune,260)}},true);
  window.addEventListener('hashchange',function(){setTimeout(tune,60)});
  window.addEventListener('pageshow',function(){setTimeout(tune,60)});
  document.addEventListener('visibilitychange',function(){if(document.visibilityState==='visible')setTimeout(tune,60)});
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){setTimeout(tune,60)});else setTimeout(tune,60);
})();
</script>
</body>`);
fs.writeFileSync('public/index.html',s);
const EXPECT='5e506b9e3bed60d30a1b5c18c81e614c92074e48';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v90 intake handoff',h(s),s.length);
