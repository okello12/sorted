const fs=require('fs'),c=require('crypto'),cp=require('child_process');
const h=b=>c.createHash('sha1').update(b).digest('hex');
const placeholder="const EXPECT='0000000000000000000000000000000000000000';";
const neutral="const EXPECT='';";
let src=fs.readFileSync('build84.js','utf8').replace(placeholder,neutral);
const tmp='.build84-v85-run.js';fs.writeFileSync(tmp,src);
try{cp.execSync('node '+tmp,{stdio:'inherit'});}finally{try{fs.unlinkSync(tmp)}catch(e){}}
const out=fs.readFileSync('public/index.html');
const EXPECT='c454196b36a6cba8a9651b6fb123c365adfa118a';
if(h(out)!==EXPECT)throw new Error('output mismatch '+h(out));
console.log('v85 ok',h(out),out.length);
