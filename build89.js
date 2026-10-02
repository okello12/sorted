const fs=require('fs'),c=require('crypto'),cp=require('child_process');
const h=b=>c.createHash('sha1').update(b).digest('hex');
const placeholder="const EXPECT='0000000000000000000000000000000000000000';";
const neutral="const EXPECT='';";
let src=fs.readFileSync('build88.js','utf8').replace(placeholder,neutral);
const tmp='.build88-v89-run.js';fs.writeFileSync(tmp,src);
try{cp.execSync('node '+tmp,{stdio:'inherit'});}finally{try{fs.unlinkSync(tmp)}catch(e){}}
const out=fs.readFileSync('public/index.html');
const EXPECT='ec7c665901ccb67af43fecf6d0041bca8c49fb83';
if(h(out)!==EXPECT)throw new Error('output mismatch '+h(out));
console.log('v89 ok',h(out),out.length);
