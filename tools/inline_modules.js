// The last step of all.js (since v161). Puts the pure modules listed in src/manifest.json into the built page at
// their marker, in order, and checks every fingerprint: the page before (`base`, the last layer's output), each
// module file, and the page after (`expect`). So the byte-for-byte rule holds for modules as for layers: a changed
// module is a changed manifest. `node tools/inline_modules.js --pin` rewrites the fingerprints after a deliberate
// change (then rerun the build, the tests and tools/csp_hashes.js).
const fs=require('fs'),c=require('crypto'),path=require('path');
const h=b=>c.createHash('sha1').update(b).digest('hex');
const root=path.join(__dirname,'..'),mf=path.join(root,'src/manifest.json'),pg=path.join(root,'public/index.html');
const man=JSON.parse(fs.readFileSync(mf,'utf8'));const pin=process.argv.includes('--pin');
let s=fs.readFileSync(pg,'utf8');
if(s.indexOf(man.marker)<0&&s.indexOf(man.begin)>=0)throw new Error('modules already inlined: run all.js from the start');
if(h(s)!==man.base){if(!pin)throw new Error('base mismatch '+h(s));man.base=h(s)}
const k=s.split(man.marker).length-1;if(k!==1)throw new Error('marker count '+k);
let code=man.begin+'\n';
for(const f of man.files){
  const b=fs.readFileSync(path.join(root,f.path),'utf8');
  if(/<\/script/i.test(b))throw new Error(f.path+' contains </script');
  if(h(b)!==f.sha1){if(!pin)throw new Error('module changed without --pin: '+f.path+' '+h(b));f.sha1=h(b)}
  code+='/* ---- '+f.path+' ---- */\n'+b.replace(/\s+$/,'')+'\n';
}
code+=man.end;
s=s.split(man.marker).join(code);
if(pin){man.expect=h(s);fs.writeFileSync(mf,JSON.stringify(man,null,2)+'\n')}
fs.writeFileSync(pg,s);
if(h(s)!==man.expect)throw new Error('output mismatch '+h(s));
console.log('modules ok',h(s),s.length);
