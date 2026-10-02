const fs=require('fs'),c=require('crypto'),cp=require('child_process');
const h=b=>c.createHash('sha1').update(b).digest('hex');
const placeholder="const EXPECT='0000000000000000000000000000000000000000';";
const neutral="const EXPECT='';";
let src=fs.readFileSync('build82.js','utf8').replace(placeholder,neutral);
const tmp='.build82-v83-run.js';
fs.writeFileSync(tmp,src);
try{cp.execSync('node '+tmp,{stdio:'inherit'});}finally{try{fs.unlinkSync(tmp)}catch(e){}}
const out=fs.readFileSync('public/index.html');
const EXPECT='846b76b0684aa708e0d545b4925f933843eb3c1f';
if(h(out)!==EXPECT)throw new Error('output mismatch '+h(out));
console.log('v83 ok',h(out),out.length);
