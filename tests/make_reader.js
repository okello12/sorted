// Test-only copy of the page that exposes the case reader to tests (tests/out/reader.html).
// Production is never changed: this runs on the test copy after the build.
const fs=require('fs');
let s=fs.readFileSync('tests/out/index.html','utf8');
const a='\nboot();\n})();\n';
if(s.split(a).length!==2)throw new Error('reader hook: end of the main script not found exactly once');
s=s.replace(a,'\nwindow.__read={readCase:readCase,suggestPromise:suggestPromise,sugFromMessage:sugFromMessage,caseFacts:caseFacts,parseWhen:parseWhen,shortTitle:shortTitle,pcnRead:pcnRead,hoRead:hoRead,thingOf:(typeof thingOf==="function"?thingOf:null),looksUnsafe:(typeof looksUnsafe==="function"?looksUnsafe:null),typoFix:(typeof typoFix==="function"?typoFix:null),wdFrom:(typeof wdFrom==="function"?wdFrom:null),ymdL:ymdL,corrRead:(typeof corrRead==="function"?corrRead:null),PMISS:(typeof PMISS!=="undefined"?PMISS:null),refsRead:(typeof refsRead==="function"?refsRead:null),OUT_PART:(typeof OUT_PART!=="undefined"?OUT_PART:null)};\nboot();\n})();\n');
fs.writeFileSync('tests/out/reader.html',s);
