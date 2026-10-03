const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='694f1f5948155df085eeab3e076dac8a99aae679')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,100));s=s.split(a).join(b)}
// v86: preserve v84 scene compatibility while making the chooser physically follow the compact hero.
R("art.classList.remove('cap84-scene');art.classList.add('cap85-scene')","art.classList.add('cap84-scene','cap85-scene')");
R('</style>\n\n</head>',String.raw`/* v86 landing continuity */
.cap85-public .hero{margin-bottom:0!important}
.cap85-public #cap82-landing{position:relative;top:-24px!important;margin-bottom:-24px!important}
@media(max-width:520px){.cap85-public #cap82-landing{top:-24px!important;margin-top:0!important;margin-bottom:-24px!important}}
</style>

</head>`);
fs.writeFileSync('public/index.html',s);
const EXPECT='PENDING_V86';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v86 ok',h(s),s.length);
