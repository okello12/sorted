const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='2f9e23afaa0140af6f07439a8fb014871ea4b2ba')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,80));s=s.split(a).join(b)}
// v80: two extra visual cues only. 1) colourful section sigils. 2) purposeful state motion / completion flourish.
R('</style>\n\n</head>',String.raw`/* v80: two extra expressive cues */
.case75-group>summary:before{display:inline-grid;place-items:center;width:28px;height:28px;margin-right:10px;border-radius:10px;color:#fff;font-size:15px;font-weight:900;line-height:1;vertical-align:-7px;box-shadow:0 7px 18px rgba(48,38,103,.14)}
.case75-happened>summary:before{content:"↺";background:linear-gradient(145deg,var(--aqua),var(--violet))}
.case75-tools>summary:before{content:"✦";background:linear-gradient(145deg,var(--violet),var(--coral))}
.home44-section.needs .h2:after,.home44-section.waiting .h2:after{display:inline-grid;place-items:center;width:22px;height:22px;margin-left:8px;border-radius:8px;color:#fff;font-size:12px;font-weight:900;vertical-align:2px;box-shadow:0 6px 14px rgba(44,34,100,.14)}
.home44-section.needs .h2:after{content:"!";background:linear-gradient(145deg,var(--coral),#FF8A66)}
.home44-section.waiting .h2:after{content:"◷";background:linear-gradient(145deg,var(--violet),var(--aqua))}
.case56-next:after{content:"";position:absolute;z-index:0;top:-55%;left:-45%;width:28%;height:210%;pointer-events:none;background:linear-gradient(90deg,transparent,rgba(255,255,255,.54),transparent);transform:rotate(18deg) translateX(-180%);opacity:.46}
.case56-next>*{position:relative;z-index:1}
.home44-row.done{position:relative;padding-right:48px}
.home44-row.done:after{content:"✓";position:absolute;right:14px;top:50%;transform:translateY(-50%);display:grid;place-items:center;width:27px;height:27px;border-radius:50%;background:linear-gradient(145deg,var(--green),#55C98C);color:#fff;font-size:15px;font-weight:900;box-shadow:0 7px 18px color-mix(in srgb,var(--green) 24%,transparent)}
:root[data-theme="dark"] .case75-group>summary:before{box-shadow:0 8px 20px rgba(0,0,0,.32)}
@media (prefers-reduced-motion:no-preference){.case56-next:after{animation:v80Sheen 8s ease-in-out infinite}.home44-row.done:after{animation:v80Done 4.8s ease-in-out infinite}}
@media (prefers-reduced-motion:reduce){.case56-next:after,.home44-row.done:after{animation:none!important}}
@keyframes v80Sheen{0%,63%,100%{transform:rotate(18deg) translateX(-180%);opacity:0}72%{opacity:.5}82%{transform:rotate(18deg) translateX(620%);opacity:0}}
@keyframes v80Done{0%,84%,100%{transform:translateY(-50%) scale(1)}90%{transform:translateY(-50%) scale(1.11)}}
</style>

</head>`);
fs.writeFileSync('public/index.html',s);
const EXPECT='0000000000000000000000000000000000000000';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v80 ok',h(s),s.length);
