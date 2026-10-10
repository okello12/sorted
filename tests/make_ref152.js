// Builds the page as it was at v152 (the last release with the old attention functions, in ATT150.F) into
// tests/out/ref152.html, for test 119 to compare the attention rules against. Runs the layers in a scratch folder
// made of links to this repository, so nothing here changes.
const fs=require('fs'),path=require('path'),os=require('os'),{execSync}=require('child_process');
const root=path.resolve(__dirname,'..'),tmp=fs.mkdtempSync(path.join(os.tmpdir(),'ref152-'));
for(const f of fs.readdirSync(root)){if(f==='public'||f==='.git'||f==='tests')continue;fs.symlinkSync(path.join(root,f),path.join(tmp,f))}
fs.mkdirSync(path.join(tmp,'public'));
const list=fs.readFileSync(path.join(root,'all.js'),'utf8').match(/\[('build[^\]]+)\]/)[1].split(',').map(x=>x.trim().replace(/'/g,''));
for(const f of list.slice(0,list.indexOf('build152.js')+1))execSync('node '+f,{cwd:tmp,stdio:'pipe'});
const out=fs.readFileSync(path.join(tmp,'public/index.html'),'utf8');
if(require('crypto').createHash('sha1').update(out).digest('hex')!=='37dbc2019adc5b6fcd895bb13fb7609b7b7a0a8d')throw new Error('ref152 fingerprint');
fs.mkdirSync(path.join(root,'tests/out'),{recursive:true});
fs.writeFileSync(path.join(root,'tests/out/ref152.html'),out.replace(/(supabase-js@[0-9.]*\/dist\/umd\/supabase.js") integrity="[^"]*"/,'$1'));
fs.rmSync(tmp,{recursive:true,force:true});
console.log('ref152 ok');
