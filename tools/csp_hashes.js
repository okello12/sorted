// node tools/csp_hashes.js [--check]: puts the SHA-256 hash of every inline <script> in public/index.html into the
// script-src of the Content Security Policy in vercel.json (replacing any earlier hashes, and 'unsafe-inline'), so the
// browser runs Sorted's own inline scripts and nothing injected. Run it after every build that changes the page; with
// --check it only says whether vercel.json is current (test 124 runs it). Build first: node all.js.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),page=fs.readFileSync(path.join(root,'public/index.html'),'utf8');
const hashes=[];const re=/<script>([\s\S]*?)<\/script>/g;let m;
while((m=re.exec(page)))hashes.push("'sha256-"+crypto.createHash('sha256').update(m[1],'utf8').digest('base64')+"'");
if(/<script(?![^>]*\bsrc=)[^>]+>/.test(page.replace(/<script>/g,'')))throw new Error('an inline script with attributes: add it to tools/csp_hashes.js');
const vp=path.join(root,'vercel.json'),v=JSON.parse(fs.readFileSync(vp,'utf8'));let found=0,cur='';
v.headers.forEach(function(hd){hd.headers.forEach(function(x){if(x.key!=='Content-Security-Policy')return;found++;cur=x.value;
  x.value=x.value.split('; ').map(function(d){if(!/^script-src /.test(d))return d;
    var parts=d.split(' ').filter(function(p){return p!=="'unsafe-inline'"&&!/^'sha256-/.test(p)});parts.splice(2,0,...hashes);return parts.join(' ')}).join('; ')})});
if(!found)throw new Error('no Content-Security-Policy in vercel.json');
const next=JSON.stringify(v,null,2)+'\n',same=fs.readFileSync(vp,'utf8')===next;
if(process.argv.includes('--check')){console.log(same?'CSP hashes current ('+hashes.length+')':'CSP hashes OUT OF DATE: run node tools/csp_hashes.js');process.exit(same?0:1)}
if(!same)fs.writeFileSync(vp,next);console.log((same?'unchanged, ':'written, ')+hashes.length+' inline scripts');
