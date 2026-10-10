// node tests/make_ref.js <buildN.js> <sha1> builds the page as it was after that layer into tests/out/ref<N>.html
// (with the database library's integrity attribute removed, as run.sh does), in a scratch folder of links to this
// repository, so nothing here changes. Tests use it as the reference when a release replaces old code.
const fs=require('fs'),path=require('path'),os=require('os'),{execSync}=require('child_process');
const layer=process.argv[2],want=process.argv[3],n=layer.replace(/\D/g,'');
const root=path.resolve(__dirname,'..'),tmp=fs.mkdtempSync(path.join(os.tmpdir(),'ref'+n+'-'));
for(const f of fs.readdirSync(root)){if(f==='public'||f==='.git'||f==='tests')continue;fs.symlinkSync(path.join(root,f),path.join(tmp,f))}
fs.mkdirSync(path.join(tmp,'public'));
const list=fs.readFileSync(path.join(root,'all.js'),'utf8').match(/\[('build[^\]]+)\]/)[1].split(',').map(x=>x.trim().replace(/'/g,''));
if(list.indexOf(layer)<0)throw new Error('no layer '+layer);
for(const f of list.slice(0,list.indexOf(layer)+1))execSync('node '+f,{cwd:tmp,stdio:'pipe'});
const out=fs.readFileSync(path.join(tmp,'public/index.html'),'utf8');
if(require('crypto').createHash('sha1').update(out).digest('hex')!==want)throw new Error('ref'+n+' fingerprint');
fs.mkdirSync(path.join(root,'tests/out'),{recursive:true});
fs.writeFileSync(path.join(root,'tests/out/ref'+n+'.html'),out.replace(/(supabase-js@[0-9.]*\/dist\/umd\/supabase.js") integrity="[^"]*"/,'$1'));
fs.rmSync(tmp,{recursive:true,force:true});
console.log('ref'+n+' ok');
