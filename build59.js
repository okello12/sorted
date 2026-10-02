const fs=require('fs'),c=require('crypto');
const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
const EXPECT='148a932ad99218c71b8d8930cd8753352e359ed6';
if(h(s)!==EXPECT)throw new Error('base mismatch '+h(s));
fs.writeFileSync('public/index.html',s);
if(h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v59 ok',h(s),s.length);
