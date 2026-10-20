const fs=require('fs'),c=require('crypto');
const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='3ecb4ca1db0e54db26bdd29d46d89477f98a4aa3')throw new Error('base mismatch '+h(s));
function R(a,b){const n=s.split(a).length-1;if(n!==1)throw new Error('match '+n+': '+a.slice(0,80));s=s.replace(a,b)}
const UI=String.raw`
/* v171: document entry is a focused screen. Reuse the existing readers and confirmation rules. */
function doc171Active(){return S.composeOpen&&(giKind()==="document"||!!(S.draft&&S.draft.doc))}
function doc171Only(text,facts){return psOnly(text,facts)&&psNoun(text)!=="call"}
function doc171Incomplete(t){return !!(t&&t.mode==="call"&&!t.call&&!openPromise(t)&&!openMove(t)&&!pkOn(t)&&doc171Only(t.said||t.title,t.facts))}
function doc171Missing(t){return '<section class="sheet stack doc171-missing" aria-labelledby="doc171-missing-h"><h2 class="h2" id="doc171-missing-h">What did they send or say?</h2><p>Sorted knows who it is from, but not what it asks or whether you need to reply. Add a photo or paste the letter or message. Check any date against the original.</p><button class="btn primary block" data-a="panel" data-p="paste">Add the letter or message</button><button class="link" data-a="panel" data-p="call" style="align-self:flex-start">I want to contact them about it</button></section>'}
function doc171Review(d){
  var f=d.facts||{},text=String(d.said||""),dl=frDeadline({said:text,facts:f}),only=psOnly(text,f);
  return '<section class="sheet stack-s doc171-review" aria-labelledby="doc171-review-h"><h1 class="h2" id="doc171-review-h">Check the letter</h1><p>Check the sender, date and words against the letter. Use Back to correct anything. Not saved yet.</p><dl class="u117"><div><dt>From</dt><dd>'+esc(f.party?psSay(f):'Not identified. Check the letter.')+'</dd></div><div><dt>Your deadline</dt><dd>'+esc(dl?pkDayLabel(dl.date)+' (check this against the letter)':'No clear deadline found. Check the letter.')+'</dd></div></dl>'+(only?'<p class="note">Only the sender is known. Sorted still needs what the letter asks before suggesting a response.</p>':'')+'<details><summary>Check the letter’s words</summary><p class="doc171-words">'+esc(text)+'</p></details></section>';
}
`;
R('function viewHome(){',UI+'function viewHome(){');
R('  var needs=[],waiting=[],done=[];',`  if(doc171Active())return topbar('<button class="link" data-a="doc171-home">Cancel</button>')+'<main class="stack fade document171">'+(S.draft.doc?'<h1 class="sr-only">Check your document</h1>':'')+caseEntry()+'</main>';
  var needs=[],waiting=[],done=[];`);
R('var cur=TAB_VIEWS[S.view.name]||"",it=function','var cur=doc171Active()&&S.view.name==="home"?"new":TAB_VIEWS[S.view.name]||"",it=function');
R("(S.tasks.length?'<h2 class=\"h2\">'+hd+'</h2>':'<h1 class=\"h1\">'+hd+'</h1>')","(S.tasks.length&&!doc171Active()?'<h2 class=\"h2\">'+hd+'</h2>':'<h1 class=\"h1\">'+hd+'</h1>')");
R("d.vague?vagueBlock():'<button class=\"btn primary block\" type=\"submit\">Start</button>'","d.vague?vagueBlock():'<button class=\"btn primary block\" type=\"submit\">'+(isDoc?'Review this letter':'Start')+'</button>'");
R('cfsrc:d.src||(d.fromShare?"a message shared from another app":""),docConfirmed:', 'cfsrc:d.src||(d.fromShare?"a message shared from another app":""),document171:giKind()==="document"||!!d.docConfirmed,docConfirmed:');
R('if(fam||d.title)h+=', 'if(!d.document171&&(fam||d.title))h+=');
R(`    h+='<div class="stack-s"><h1 class="h2">What were you planning to do next?</h1><p class="lede">We ask before giving any advice. There’s no right answer, and “not sure” is fine.</p></div>';`,
`    if(d.document171)h+=doc171Review(d);
    h+='<div class="stack-s"><'+(d.document171?'h2':'h1')+' class="h2">What were you planning to do next?</'+(d.document171?'h2':'h1')+'><p class="lede">This optional pilot question helps us see whether Sorted is useful. “Not sure yet” is fine, or skip it below.</p></div>';`);
R('case "back-title":d.step="title";d.err="";render();break;', 'case "back-title":if(d.document171){S.draft={gk:"document",casetext:d.said||"",docConfirmed:d.docConfirmed||null};S.view={name:"home"};S.composeOpen=true;S.newOpen=true;render();window.scrollTo(0,0);break}d.step="title";d.err="";render();break;');
R('    case "home":S.newOpen=false;', '    case "doc171-home":docKeepSave143();if(S.view.name==="new"&&d.document171)S.draft={gk:"document",casetext:d.said||""};draftSave();goHome();break;\n    case "home":S.newOpen=false;');
R('var h=topbar(\'<button class="link" data-a="home">Cancel</button>\');', 'var h=topbar(\'<button class="link" data-a="\'+(d.document171?"doc171-home":"home")+\'">Cancel</button>\');');
R('S.draft=dgo.gk&&GI[dgo.gk]?', 'S.draft=dgo.gk&&(GI[dgo.gk]||dgo.gk==="document")?');
R('&&!t.cf&&!pcnRead(String(t.said||""))?"call":null', '&&!t.cf&&!doc171Only(t.said||t.title,t.facts)&&!pcnRead(String(t.said||""))?"call":null');
R('S._info=frCard(t)+prodCard161(t)+uCard(t);', 'S._info=(doc171Incomplete(t)&&!S.view.panel?"":frCard(t))+prodCard161(t)+uCard(t);');
R('  }else if(pkOn(t)&&!p&&(!mv||', '  }else if(!S.view.panel&&doc171Incomplete(t)){\n    h+=doc171Missing(t);\n  }else if(pkOn(t)&&!p&&(!mv||');
R('function now137(t,s){', 'function now137(t,s){\n  if(s!=="done"&&!t.example&&!S.view.panel&&doc171Incomplete(t))return "";');
R('</head>', `<style>\n.document171{margin-top:12px;padding-bottom:28px}.doc171-words{white-space:pre-wrap;overflow-wrap:anywhere;max-height:260px;overflow:auto}.doc171-review details summary{min-height:44px;cursor:pointer;font-weight:600}.doc171-review .u117 dd{overflow-wrap:anywhere}\n</style>\n</head>`);
R('SORTED_V="v170"','SORTED_V="v171"');
fs.writeFileSync('public/index.html',s);
const EXPECT='4447bff06e0a8646e267d7ac71042c8b59749292';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v171 ok',h(s),s.length);
