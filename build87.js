const fs=require('fs'),c=require('crypto'),cp=require('child_process');
const h=b=>c.createHash('sha1').update(b).digest('hex');
const placeholder="const EXPECT='0000000000000000000000000000000000000000';";
const neutral="const EXPECT='';";
let src=fs.readFileSync('build86.js','utf8').replace(placeholder,neutral);
const tmp='.build86-v87-run.js';fs.writeFileSync(tmp,src);
try{cp.execSync('node '+tmp,{stdio:'inherit'});}finally{try{fs.unlinkSync(tmp)}catch(e){}}
const out=fs.readFileSync('public/index.html');
const EXPECT='82140e8f0d506729ab95ee3fc580bba3c5ddf87b';
if(h(out)!==EXPECT)throw new Error('output mismatch '+h(out));
console.log('v87 ok',h(out),out.length);
