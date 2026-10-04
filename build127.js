const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='636142b116aeb4e38d147367f97be60e8aeca61a')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v127 (Baldwin's iPhone, 4 October 2026): a photo taken with the camera was lost because the page redrew when it
// came back from the camera. Nothing redraws while a picker is open, the file box carries its own handler, big photos
// are scaled before reading, a start choice survives the email link, the box heading follows the real choice, and the
// parking screen has one photo button. ----
R("document.addEventListener(\"visibilitychange\",function(){if(!document.hidden&&S.user){var a=document.activeElement;if(!a||!/INPUT|TEXTAREA/.test(a.tagName))render()}});",
  "/* v127: while a photo or file picker is open (up to 3 minutes), nothing redraws the page */\nfunction picking(){return !!(S.picking&&Date.now()-S.picking<180000)}\nwindow.__sortedPicking=picking;\nfunction ocrBind(inp){if(!inp||inp._ocrBound)return;inp._ocrBound=1;inp.addEventListener(\"change\",function(){var f=inp.files&&inp.files[0],tg=inp.getAttribute(\"data-ocr\");inp._ocrAt=Date.now();S.picking=0;if(f)readPicture(f,tg);else{var oc0=document.getElementById(\"ocr-status\");if(oc0&&!oc0.textContent)oc0.textContent=\"\"}try{inp.value=\"\"}catch(e){}})}\ndocument.addEventListener(\"click\",function(e){var el=e.target;if(el&&el.matches&&el.matches('input[type=file][data-ocr]')){S.picking=Date.now();ocrBind(el)}},true);\ndocument.addEventListener(\"visibilitychange\",function(){if(!document.hidden&&S.user&&!picking()){var a=document.activeElement;if(!a||!/INPUT|TEXTAREA/.test(a.tagName))render()}});");
R("setInterval(function(){if(S.view.name===\"home\"||S.view.name===\"task\"){var a=document.activeElement;",
  "setInterval(function(){if((S.view.name===\"home\"||S.view.name===\"task\")&&!picking()){var a=document.activeElement;");
R("var oc=e.target&&e.target.getAttribute&&e.target.getAttribute(\"data-ocr\");if(oc){readPicture(e.target.files&&e.target.files[0],oc);e.target.value=\"\";return}",
  "var oc=e.target&&e.target.getAttribute&&e.target.getAttribute(\"data-ocr\");if(oc){if(e.target._ocrAt&&Date.now()-e.target._ocrAt<3000)return;S.picking=0;readPicture(e.target.files&&e.target.files[0],oc);e.target.value=\"\";return}");
R("window.addEventListener('pageshow',function(e){if(e.persisted&&typeof render==='function'){render();tune()}});",
  "window.addEventListener('pageshow',function(e){if(e.persisted&&typeof render==='function'&&!(window.__sortedPicking&&window.__sortedPicking())){render();tune()}});");
R(".then(function(w){wk=w;return w.recognize(file)})",
  ".then(function(w){wk=w;return ocrScale(file).then(function(src){return w.recognize(src)})})");
R("function readPicture(file,target){\n  if(!file)return;",
  "/* v127: a camera photo is often 12 megapixels; reading it at full size is slow and can stop the page on a phone.\n   Scale it so the longer side is at most 2400 pixels (enough for a notice), respecting the photo's orientation. */\nfunction ocrScale(file){\n  return new Promise(function(res){\n    try{\n      if(!file||!(file instanceof Blob)||!/^image\\//.test(file.type||\"\")){res(file);return}\n      var url=URL.createObjectURL(file),img=new Image();\n      img.onload=function(){try{var w=img.naturalWidth,h=img.naturalHeight,m=Math.max(w,h),k=m>2400?2400/m:1;if(k>=1){URL.revokeObjectURL(url);res(file);return}var c=document.createElement(\"canvas\");c.width=Math.round(w*k);c.height=Math.round(h*k);c.getContext(\"2d\").drawImage(img,0,0,c.width,c.height);URL.revokeObjectURL(url);res(c)}catch(e){res(file)}};\n      img.onerror=function(){URL.revokeObjectURL(url);res(file)};img.src=url;\n    }catch(e){res(file)}\n  });\n}\nfunction readPicture(file,target){\n  S.picking=0;\n  if(!file)return;");
R("if(!S.user){try{sessionStorage.setItem(\"sorted.carry82\",\"1\")}catch(z){}}",
  "if(!S.user){try{sessionStorage.setItem(\"sorted.carry82\",\"1\");localStorage.setItem(\"sorted.carry82\",JSON.stringify({k:ck,at:Date.now()}))}catch(z){}}");
R("function giRestore(){var k=\"\",carry=\"\";try{k=sessionStorage.getItem(\"sorted.cap82\")||\"\";carry=sessionStorage.getItem(\"sorted.carry82\")||\"\";sessionStorage.removeItem(\"sorted.carry82\")}catch(e){}",
  "function giRestore(){var k=\"\",carry=\"\";try{k=sessionStorage.getItem(\"sorted.cap82\")||\"\";carry=sessionStorage.getItem(\"sorted.carry82\")||\"\";sessionStorage.removeItem(\"sorted.carry82\");var lc=JSON.parse(localStorage.getItem(\"sorted.carry82\")||\"null\");localStorage.removeItem(\"sorted.carry82\");if(!carry&&lc&&lc.k&&Date.now()-(lc.at||0)<3600000){carry=\"1\";k=lc.k;try{sessionStorage.setItem(\"sorted.cap82\",k)}catch(z){}}}catch(e){}");
R("function giKind(){",
  "window.__sortedGk=function(){try{return giKind()}catch(e){return \"\"}};\nfunction giKind(){");
R("function chosenCap(){try{return lastChoice||sessionStorage.getItem('sorted.cap82')||''}catch(e){return lastChoice}}",
  "function chosenCap(){if(window.__sortedGk)return window.__sortedGk()||'';try{return lastChoice||sessionStorage.getItem('sorted.cap82')||''}catch(e){return lastChoice}}");
R("(isDoc?'<label class=\"btn primary block gi-photo\">Take a photo or choose the letter<input type=\"file\" accept=\"image/*,application/pdf,.pdf\" data-ocr=\"f-case\" class=\"sr-only\"></label><p class=\"muted\" style=\"font-size:15px;margin:0\">Sorted reads it on your phone. Nothing is uploaded. Sorted tries to read the notice. Check the details before continuing. For a scanned PDF, only the first page is read.</p>",
  "(isDoc?(d.pkShort?'':'<label class=\"btn primary block gi-photo\">Take a photo or choose the letter<input type=\"file\" accept=\"image/*,application/pdf,.pdf\" data-ocr=\"f-case\" class=\"sr-only\"></label><p class=\"muted\" style=\"font-size:15px;margin:0\">Sorted reads it on your phone. Nothing is uploaded. Sorted tries to read the notice. Check the details before continuing. For a scanned PDF, only the first page is read.</p>')+'");
fs.writeFileSync('public/index.html',s);
const EXPECT='156bc7b7aca9b3009ad6779ccf6bd8196b42461e';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v127 ok',h(s),s.length);
