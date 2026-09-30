const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='5ee98890fdb2f3d4bcc0f253613ab93f5050b5a3')throw new Error('base mismatch '+h(s));
// ---- v27: the controller contact address changes ----
const n=s.split('bthompsonaddo@gmail.com').length-1;if(n!==10)throw new Error('expected 10 mentions, found '+n);
s=s.split('bthompsonaddo@gmail.com').join('kofiniiakwei@gmail.com');
fs.writeFileSync('public/index.html',s);
const EXPECT='cc73c485a42ae702aebe2564a6cfdb4701485346';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v27 ok',h(s),s.length);
