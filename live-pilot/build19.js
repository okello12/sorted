const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='a02019d301c187b542ff1db31408b76153116074')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+String(a).slice(0,70));s=s.split(a).join(b)}
function G(a,b){const k=s.split(a).length-1;if(k<1)throw new Error('none: '+String(a).slice(0,70));s=s.split(a).join(b)}
// ---- v19: pilot-ready honesty ----

// 1. nobody running the pilot reads cases; the notice before Start says so
R(`function privacyBlock(){
  return '<section class="sheet stack-s"><p class="h3">How your data is handled</p>'+
  '<p>Sorted is a small research pilot run by Baldwin Thompson-Addo. It keeps your email address and the tasks you add, stored on servers in London.</p>'+
  '<p>Only you see your tasks in the app. The person running the pilot can read them to learn how Sorted is used, and won’t share them with anyone else. If you send a helper link, that person sees that one task until you switch the link off.</p>'+
  '<p>Tasks you haven’t touched for 90 days are deleted automatically. If you start without an email, your cases are deleted after 30 days away unless you add your email.`,`function privacyBlock(){
  return '<section class="sheet stack-s"><p class="h3">How your data is handled</p>'+
  '<p>Sorted is a small UK research pilot run by Baldwin Thompson-Addo. It keeps the cases you add, and your email address if you add one, stored on servers in London.</p>'+
  '<p><strong>Your cases are private.</strong> Nobody running the pilot reads them. If you send a helper link, that person sees that one case until you switch the link off.</p>'+
  '<p>Cases you haven’t touched for 90 days are deleted automatically. If you haven’t added an email, your cases are deleted after 30 days away.`);
R(`unless you turn it off for that task; the email doesn’t include task details.`,`unless you turn it off for that case; the email doesn’t include case details.`);
R(`without any case details. These records are deleted after 12 months, or straight away if you delete your account.</p>'+
  '<p class="muted" style="font-size:16px">Please don’t add bank details, medical information or anything you wouldn’t want a researcher to read.</p></section>';`,`without any case details. You can turn this off in “Your data”. These records are deleted after 12 months, or straight away if you delete your account.</p>'+
  '<p class="muted" style="font-size:16px">Please don’t add bank details or medical information.</p></section>';`);
G(`<p>By continuing, you’re taking part in the Sorted pilot.</p>`,`<p>By continuing, you’re taking part in the Sorted pilot. Your cases are private: nobody running the pilot reads them. Sorted records which steps you use, without case details, and deletes idle cases after 90 days.</p>`);

// 2. a switch for the step records, on this phone
R(`function track(name,t,x){
  if(!S.user)return;`,`function noSteps(){try{return localStorage.getItem("sorted.nosteps")==="1"}catch(e){return false}}
function track(name,t,x){
  if(!S.user||noSteps()||(t&&t.example))return;`);
R(`  h+=privacyBlock();
  if(S.isAdmin)`,`  h+=privacyBlock();
  h+='<section class="sheet stack-s"><p class="h3">Step records</p><p>'+(noSteps()?"Sorted isn’t recording which steps you use on this phone.":"Sorted records which steps you use, such as “promise added”, without any case details. It helps show whether the pilot works.")+'</p><button class="btn" data-a="steps-toggle">'+(noSteps()?"Record my steps again":"Don’t record my steps")+'</button></section>';
  if(S.isAdmin)`);

// 3. an example case, so the promise loop is visible in minute one
R(`    case "compose":`,`    case "steps-toggle":try{if(noSteps())localStorage.removeItem("sorted.nosteps");else{localStorage.setItem("sorted.nosteps","1");EVQ=[];saveQ()}}catch(e){}render();break;
    case "example":{var ex=exampleCase();S.tasks.unshift(ex);save();go({name:"home"});break}
    case "example-del":if(t){S.tasks=S.tasks.filter(function(x){return x.id!==t.id});cacheWrite();sb.from("tasks").delete().eq("id",t.id).then(function(){},function(){});go({name:"home"});toast("Example removed")}break;
    case "compose":`);
R(`function newTask(mode){`,`function exampleCase(){
  var d=new Date();d.setDate(d.getDate()-1);d.setHours(8,0,0,0);var e=new Date(d);e.setHours(13,0,0,0);
  var st=new Date(d.getTime()-3*86400000),lg=new Date(st.getTime()+20*60000);
  var pr={id:uid(),said:"An engineer will come to replace the pump, between 8am and 1pm",party:"Oakridge",dueAt:d.toISOString(),dueEnd:e.toISOString(),allDay:false,by:false,ref:"OL-55821",status:"open",loggedAt:lg.toISOString()};
  var t={id:uid(),mode:"call",example:true,title:"Washing machine (example)",baseline:"Call someone",created:st.toISOString(),updatedAt:nowIso(),board:"waiting",safety:false,fix:null,renew:null,
    call:{who:"Oakridge",via:"phone",ask:"My washing machine stopped draining. It’s under your cover. Can you send an engineer?"},promises:[pr],outcome:"",sharedAt:null,
    events:[{at:st.toISOString(),label:"Started. Before any advice, the plan was: “Call someone”"},{at:new Date(st.getTime()+60000).toISOString(),label:"Call ready: Oakridge, by phone."},{at:lg.toISOString(),label:"They said: "+pr.said+", "+whenText(pr)+", ref OL-55821."}],_dirty:true};
  return t;
}
function newTask(mode){`);
R(`  if(entryFirst)h+=caseEntry();
  h+=anonNote();`,`  if(entryFirst)h+=caseEntry();
  if(entryFirst&&!S.tasks.some(function(x){return x.example}))h+='<p class="muted" style="font-size:16px;margin-top:-12px">Not ready yet? <button class="link" data-a="example" style="display:inline;min-height:0;padding:0">See how it works with an example case</button></p>';
  h+=anonNote();`);
// the case page: state only, and an example says what it is
R(`h+='<section class="stack-s"><p class="eyebrow">'+MODE_LABEL[t.mode]+' · '+({yours:"Needs you"`,`if(t.example&&s!=="done")h+='<div class="note stack-s"><p><strong>This is an example case.</strong> Oakridge promised an engineer yesterday morning. Try answering what happened. Nothing here is sent to anyone.</p><button class="link" data-a="example-del" style="align-self:flex-start">Remove the example</button></div>';
  h+='<section class="stack-s"><p class="eyebrow">'+({yours:"Needs you"`);
R(`h+='<p class="eyebrow">'+MODE_LABEL[mode]+(mode==="do"?"":' · step '+(d.step==="title"?1:2)+' of 2')+'</p>';`,`h+='<p class="eyebrow">New case'+(mode==="do"?"":' · step '+(d.step==="title"?1:2)+' of 2')+'</p>';`);

// 4. advice, not law
R(`body:"It is "+whoName(t)+"’s job to fix this. Report it in writing if you can, so there is a record, and ask for a date."`,`body:"Repairs like this are usually "+whoName(t)+"’s responsibility, unless your agreement says otherwise or the damage was caused in your home. Report it in writing if you can, so there is a record, and ask for a date."`);

// 5. after the call, logging the promise is the one obvious action
R(`<div class="row eq"><button class="btn" data-a="no-promise">'+w.none+'</button><button class="btn" data-a="panel" data-p="call">Edit</button></div>`,`<div class="row" style="gap:20px"><button class="link" data-a="no-promise">'+w.none+'</button><button class="link" data-a="panel" data-p="call">Edit the call</button></div>`);
R(`h+='<button class="btn block" data-a="panel" data-p="move">Remind me to do something</button>';`,`h+='<button class="link" data-a="panel" data-p="move" style="align-self:flex-start">Remind me to do something</button>';`);

// 6. the public story: promises, not renewals; one retention sentence
R(`ex('','Coming up','Passport','Add the date it runs out. Sorted works out when to start and sends you to the official GOV.UK page.','Start 3 months before','GOV.UK')`,`ex('','Needs you','Refund not received','The date they gave has passed. Sorted asks what happened, then helps you chase them with the reference.','Has the money arrived?','Ref CR-7781')`);
R(`A UK research pilot. You can start without an account. Idle tasks are deleted after 90 days.`,`A UK research pilot. You can start without an account. Your cases stay private, and idle cases are deleted after 90 days (30 if you haven’t added an email).`);
R(`Sorted is a UK research pilot run by Baldwin Thompson-Addo in London. Your tasks are stored in London and idle tasks are deleted after 90 days.`,`Sorted is a UK research pilot run by Baldwin Thompson-Addo in London. Cases are stored in London, nobody running the pilot reads them, and idle cases are deleted after 90 days (30 without an email).`);

// 7. task → case, everywhere a person reads it
[["All tasks","All cases"],["all tasks","all cases"],["Start this task","Start this case"],["Finish this task","Finish this case"],["Copy all my tasks","Copy all my cases"],["Delete my account and tasks","Delete my account and cases"],["about your tasks","about your cases"],["That task isn’t on this phone","That case isn’t on this phone"],["open your task","open your case"],["opens this task","opens this case"],["Add it to a task","Add it to a case"],["My own tasks","My own cases"],["Opening the task…","Opening the case…"],["same task. Your task is still here","same case. Your case is still here"],["Your tasks are still here","Your cases are still here"],["open the task from your email","open the case from your email"],["sent you this task","sent you this case"],["Each task keeps","Each case keeps"],["Start a task first","Start a case first"],["They see this task only","They see this case only"],["doesn’t open a task","doesn’t open a case"],["what the task is","what the case is"],["off for this task","off for this case"],["Your account and tasks are deleted","Your account and cases are deleted"],["Start a new task from it","Start a new case from it"],["all '+S.tasks.length+' tasks","all '+S.tasks.length+' cases"],["' task'+(S.tasks.length===1?\"\":\"s\")","' case'+(S.tasks.length===1?\"\":\"s\")"]].forEach(function(p){G(p[0],p[1])});

fs.writeFileSync('public/index.html',s);
const EXPECT='33dfdb5291ed10dbc107a3680b61542c5ee2ab33';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v19 ok',h(s),s.length);
