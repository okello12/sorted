/* ---------- your move: things you need to do ---------- */
var ACTS=[["submit","Submit","I’ve submitted it","Submitted"],["upload","Submit","I’ve uploaded it","Uploaded"],["send","Send","I’ve sent it","Sent"],["email","Send","I’ve sent it","Sent"],["post","Send","I’ve sent it","Sent"],["prepare","Prepare","It’s ready","Ready"],["draft","Prepare","It’s ready","Ready"],["write","Prepare","It’s written","Written"],["finish","Prepare","It’s finished","Finished"],["chase","Chase","I’ve chased them","Chased"],["follow up","Chase","I’ve followed up","Followed up"],["call","Call","I’ve called","Called"],["ring","Call","I’ve called","Called"],["phone","Call","I’ve called","Called"],["pay","Pay","I’ve paid","Paid"],["book","Book","I’ve booked it","Booked"],["apply","Apply","I’ve applied","Applied"],["sign","Sign","I’ve signed it","Signed"],["reply","Reply","I’ve replied","Replied"],["return","Return","I’ve returned it","Returned"],["renew","Renew","I’ve renewed it","Renewed"]];
function moveAct(text){
  var s=" "+String(text||"").toLowerCase()+" ",best=null,at=1e9;
  ACTS.forEach(function(a){var m=s.match(new RegExp("\\b"+a[0]+"(s|es|ed|ing)?\\b"));if(m&&m.index<at){at=m.index;best=a}});
  return best?{key:best[0],label:best[1],done:best[2],past:best[3]}:{key:"do",label:"To do",done:"It’s done",past:"Done"};
}
function openMove(t){var m=t.moves||[];for(var i=m.length-1;i>=0;i--)if(m[i].status==="open")return m[i];return null}
function moveTitle(m){
  var ph=phase(m),w=window_(m),n=new Date();
  if(ph==="nodate")return "Your move";
  if(ph==="check")return "Overdue";
  if(ph==="now")return "Due now";
  if(ph==="soon")return sameDay(w.start,n)?"Due today":"Due tomorrow";
  return "Your move";
}
function moveDraft(text,now){
  var d={mwhat:text},p=parseWhen(text,now);
  if(p){d.when=p.when;d.date=p.date;d.from=p.from;d.to=p.to}
  return d;
}
function moveSug(text,d){
  var p=parseWhen(text);if(!p)return "";
  if(d&&d.when===p.when&&d.date===p.date&&(d.from||"")===p.from&&(d.to||"")===p.to)return '<p class="suggest ok">✓ Using what you wrote: <strong>'+esc(p.label)+'</strong>. Check it below.</p>';
  return '<div class="suggest"><p>Sounds like <strong>'+esc(p.label)+'</strong></p><button type="button" class="btn" data-a="use-msug">Use this</button></div>';
}
function moveForm(t){
  var d=S.draft,when=d.when||"by",ex=t.mode==="do"?"Submit the bursary documents by Friday":"Send them the photos by Friday";
  var h='<section class="sheet stack" id="moveform"><div class="stack-s"><p class="eyebrow">Your move</p><h2 class="h2">'+(d.mreplaces?"When will you do it now?":"What do you need to do?")+'</h2></div><form class="stack" data-f="move">';
  h+='<label class="f">In a sentence<span class="hint">Write it as you’d say it, for example “'+esc(ex)+'”. Sorted picks out the date.</span><textarea id="f-mwhat" name="mwhat" rows="2">'+esc(d.mwhat||"")+'</textarea></label>';
  h+='<div id="msug">'+moveSug(d.mwhat||"",d)+'</div>';
  h+='<div class="stack-s"><span style="font-weight:600">When?</span><div class="chips">'+[["slot","A day and time"],["by","By a day"],["none","No date"]].map(function(x){return '<button type="button" class="chip" data-a="d" data-k="when" data-v="'+x[0]+'" aria-pressed="'+(when===x[0])+'">'+x[1]+'</button>'}).join("")+'</div></div>';
  if(when!=="none")h+='<label class="f">'+(when==="by"?"By which day?":"Which day")+'<input type="date" id="f-mdate" name="date" value="'+esc(d.date||"")+'"></label>';
  if(when==="slot")h+='<div class="pair"><label class="f">At<input type="time" id="f-mfrom" name="from" value="'+esc(d.from||"")+'"></label><label class="f">Until<span class="hint">Optional</span><input type="time" id="f-mto" name="to" value="'+esc(d.to||"")+'"></label></div>';
  if(when==="none")h+='<p class="note">It stays under Your move, with no reminder.</p>';
  if(d.err)h+='<p class="err">'+esc(d.err)+'</p>';
  h+='<button class="btn primary block" type="submit">'+(when==="none"?"Save it":"Remind me")+'</button><button class="btn block" type="button" data-a="panel" data-p="">Cancel</button></form></section>';
  return h;
}
function moveCard(t,m){
  var ph=phase(m),hot=ph!=="later"&&ph!=="nodate",a=moveAct(m.what);
  var h='<section class="promise '+(hot?"pink":"white")+'"><div class="promise-head"><div class="stack-s"><p class="eyebrow">Your move</p><h2 class="h2">'+esc(moveTitle(m))+'</h2></div><span class="ref">'+esc(a.label.toUpperCase())+'</span></div>';
  h+='<div class="promise-body"><p class="h3">'+esc(m.what)+'</p><p class="mono">'+esc(m.dueAt?whenText(m):"No date set")+'</p></div><div class="promise-foot">';
  h+='<button class="btn primary block" data-a="move-done">'+esc(a.done)+'</button>';
  h+='<div class="row eq"><button class="btn" data-a="move-rebook">Change the date</button><button class="btn" data-a="move-drop">Drop it</button></div>';
  if(ph!=="check")h+=soonReminders(t);
  return h+'</div></section>';
}
function movedCard(t){
  var m=(t.moves||[]).filter(function(x){return x.status==="done"}).slice(-1)[0],a=moveAct(m?m.what:"");
  var h='<section class="sheet stack"><div class="stack-s"><p class="eyebrow">'+esc(a.past)+'</p><h2 class="h2">What happens next?</h2><p class="muted">Sorted keeps what you did and what comes back in one place.</p></div>';
  h+='<button class="btn primary block" data-a="move-reply">They’ve replied or promised something</button>';
  h+='<button class="btn block" data-a="move-follow">Remind me to chase if they don’t reply</button>';
  h+='<button class="btn block" data-a="panel" data-p="move">I have something else to do</button>';
  h+='<button class="btn block" data-a="panel" data-p="done">Nothing else. Finish this task</button>';
  return h+'<button class="link" data-a="panel" data-p="" style="text-align:left">Not now</button></section>';
}
function doIdleCard(t){
  return '<section class="sheet stack"><div class="stack-s"><p class="eyebrow">Your move</p><h2 class="h2">What’s next?</h2></div><button class="btn primary block" data-a="panel" data-p="move">Remind me to do something</button><button class="btn block" data-a="move-reply">Someone replied or promised something</button><button class="btn block" data-a="panel" data-p="done">Finish this task</button></section>';
}
function followDate(){var d=new Date(),k=0;while(k<3){d.setDate(d.getDate()+1);if(d.getDay()%6)k++}return ymdL(d)}
function mkDue(when,date,from,to){
  if(when==="none"||!date)return {dueAt:null,dueEnd:null,allDay:false};
  var ymd=date.split("-").map(Number),start=new Date(ymd[0],ymd[1]-1,ymd[2],0,0,0,0),end=null;
  if(from){var hm=from.split(":").map(Number);start.setHours(hm[0],hm[1])}
  if(from&&to){var hm2=to.split(":").map(Number),e2=new Date(start);e2.setHours(hm2[0],hm2[1]);if(e2>start)end=e2.toISOString()}
  return {dueAt:start.toISOString(),dueEnd:end,allDay:!from};
}
