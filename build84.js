const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='c37a1cca646d1d110ad828517ad2fafc77929458')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,80));s=s.split(a).join(b)}
// v84: keep the old compose trigger programmatically actionable without showing a duplicate CTA to people.
R('</style>\n\n</head>',String.raw`/* v84 compose compatibility hook */
.cap83-redundant-new{display:block!important;position:fixed!important;left:0!important;bottom:0!important;width:1px!important;height:1px!important;min-width:1px!important;min-height:1px!important;padding:0!important;margin:0!important;border:0!important;border-radius:0!important;opacity:0!important;overflow:hidden!important;z-index:2!important;pointer-events:auto!important;color:transparent!important;background:transparent!important;box-shadow:none!important}
</style>

</head>`);
R('</body>',String.raw`<script>
(function(){
 function keepComposeHook(){var b=document.querySelector('.home44-compose .home44-new');if(!b)return;b.classList.add('cap83-redundant-new');b.setAttribute('aria-hidden','true');b.setAttribute('tabindex','-1')}
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',keepComposeHook);else keepComposeHook();
 new MutationObserver(keepComposeHook).observe(document.documentElement,{childList:true,subtree:true});
})();
</script>
</body>`);
fs.writeFileSync('public/index.html',s);
const EXPECT='PENDING_V84';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v84 ok',h(s),s.length);
