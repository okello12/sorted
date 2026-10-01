const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='bcb902ed24eed8dd7a7c91add6944e216b7e3529')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v38: the last audit items (1 October 2026) ----

// 1. The database library is checked against a known fingerprint, like the screenshot and PDF readers.
//    sha384 of @supabase/supabase-js@2.117.2 dist/umd/supabase.js, taken from the npm package and checked against jsDelivr.
R(`<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.117.2/dist/umd/supabase.js" crossorigin="anonymous"></script>`,
  `<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.117.2/dist/umd/supabase.js" integrity="sha384-Rj26LVGvoeRVR6+mwQmFfcR3QOBEwT+ZmuCWpuiqeTzJpCs0ER4ITAWGb4Hiy3Ok" crossorigin="anonymous"></script>`);

// 2. The lettering is served by Sorted itself (Atkinson Hyperlegible, SIL Open Font License, @fontsource 5.3.0), so Google sees nothing.
R(`<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Mono:wght@400;600&family=Atkinson+Hyperlegible+Next:wght@400;600;800&display=swap">`,
  `<link rel="preload" href="/fonts/atkinson-hyperlegible-next-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<style>
@font-face{font-family:"Atkinson Hyperlegible Next";font-style:normal;font-weight:400;font-display:swap;src:url(/fonts/atkinson-hyperlegible-next-latin-400-normal.woff2) format("woff2")}
@font-face{font-family:"Atkinson Hyperlegible Next";font-style:normal;font-weight:600;font-display:swap;src:url(/fonts/atkinson-hyperlegible-next-latin-600-normal.woff2) format("woff2")}
@font-face{font-family:"Atkinson Hyperlegible Next";font-style:normal;font-weight:800;font-display:swap;src:url(/fonts/atkinson-hyperlegible-next-latin-800-normal.woff2) format("woff2")}
@font-face{font-family:"Atkinson Hyperlegible Mono";font-style:normal;font-weight:400;font-display:swap;src:url(/fonts/atkinson-hyperlegible-mono-latin-400-normal.woff2) format("woff2")}
@font-face{font-family:"Atkinson Hyperlegible Mono";font-style:normal;font-weight:600;font-display:swap;src:url(/fonts/atkinson-hyperlegible-mono-latin-600-normal.woff2) format("woff2")}
</style>`);
R(`jsDelivr (the database connection code, and the tools that read screenshots and PDFs) and Google Fonts (the lettering).`,
  `jsDelivr (the database connection code, and the tools that read screenshots and PDFs).`);

// 3. Step records say whether a confirmed suggestion came from a sentence or a pasted message.
R(`status:"open",loggedAt:nowIso(),src:"sentence"};`,`status:"open",loggedAt:nowIso(),src:sp.fromMsg?"message":"sentence"};`);

fs.writeFileSync('public/index.html',s);
const EXPECT='c799da873e8dd7b0784aac4764a0ad3096296762';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v38 ok',h(s),s.length);
