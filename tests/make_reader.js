// Test-only copy of the page that exposes the case reader to tests (tests/out/reader.html).
// Production is never changed: this runs on the test copy after the build.
const fs=require('fs');
let s=fs.readFileSync('tests/out/index.html','utf8');
const a='\nboot();\n})();\n';
if(s.split(a).length!==2)throw new Error('reader hook: end of the main script not found exactly once');
s=s.replace(a,'\nwindow.__read={readCase:readCase,suggestPromise:suggestPromise,sugFromMessage:sugFromMessage,caseFacts:caseFacts,parseWhen:parseWhen,shortTitle:shortTitle,pcnRead:pcnRead};\nboot();\n})();\n');
fs.writeFileSync('tests/out/reader.html',s);
