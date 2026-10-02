const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='e9041b2b18b0e1642d28ed76101dde9b377f31d0')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,80));s=s.split(a).join(b)}
// v81: two extra visual cues only. History/tools get distinct sigils; current work gets a neutral sheen and resolved rows a green finish mark.
R('</style>\n\n</head>',String.raw`/* v81: two extra expressive cues */
.case75-group>summary:before{display:inline-grid;place-items:center;width:28px;height:28px;margin-right:10px;border-radius:10px;color:#fff;font-size:15px;font-weight:900;line-height:1;vertical-align:-7px;box-shadow:0 7px 18px rgba(48,38,103,.14)}
.case75-happened>summary:before{content:"↺";background:linear-gradient(145deg,var(--aqua),#168D98)}
.case75-tools>summary:before{content:"✦";background:linear-gradient(145deg,var(--violet),var(--violet2))}
.case56-next:after{content:"";position:absolute;z-index:0;top:-55%;left:-45%;width:28%;height:210%;pointer-events:none;background:linear-gradient(90deg,transparent,rgba(255,255,255,.52),transparent);transform:rotate(18deg) translateX(-180%);opacity:.44}
.case56-next>*{position:relative;z-index:1}
.home44-row.done{position:relative;padding-right:48px}
.home44-row.done:after{content:"✓";position:absolute;right:14px;top:50%;transform:translateY(-50%);display:grid;place-items:center;width:27px;height:27px;border-radius:50%;background:linear-gradient(145deg,var(--green),#55C98C);color:#fff;font-size:15px;font-weight:900;box-shadow:0 7px 18px color-mix(in srgb,var(--green) 24%,transparent)}
:root[data-theme="dark"] .case75-group>summary:before{box-shadow:0 8px 20px rgba(0,0,0,.32)}
@media (prefers-reduced-motion:no-preference){.case56-next:after{animation:v81Sheen 9s ease-in-out infinite}.home44-row.done:after{animation:v81Done 5.2s ease-in-out infinite}}
@media (prefers-reduced-motion:reduce){.case56-next:after,.home44-row.done:after{animation:none!important}}
@keyframes v81Sheen{0%,66%,100%{transform:rotate(18deg) translateX(-180%);opacity:0}74%{opacity:.46}84%{transform:rotate(18deg) translateX(620%);opacity:0}}
@keyframes v81Done{0%,86%,100%{transform:translateY(-50%) scale(1)}91%{transform:translateY(-50%) scale(1.1)}}
</style>

</head>`);
fs.writeFileSync('public/index.html',s);
const EXPECT='30189ca2f049dc4b2a509fbbb19f1386d5f310c4';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v81 ok',h(s),s.length);
