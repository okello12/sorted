/* ---------- 1. understanding what they said ---------- */
var WDN=["sunday","monday","tuesday","wednesday","thursday","friday","saturday"];
var MONN=["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"];
var NUMW={a:1,an:1,one:1,two:2,three:3,four:4,five:5,six:6,seven:7,eight:8,nine:9,ten:10,fourteen:14};
function pad2(n){return (n<10?"0":"")+n}
function ymdL(d){return d.getFullYear()+"-"+pad2(d.getMonth()+1)+"-"+pad2(d.getDate())}
function numw(x){return /^\d+$/.test(x)?+x:(NUMW[x]||0)}
function tclock(h,m,ap,hint){
  h=+h;m=+(m||0);if(h>23||m>59)return null;
  if(ap==="pm"&&h<12)h+=12;else if(ap==="am"&&h===12)h=0;
  else if(!ap&&h>=1&&h<=7)h+=12;           /* "between 1 and 3", "by 5" mean the afternoon */
  else if(!ap&&hint==="pm"&&h<12)h+=12;
  return pad2(h)+":"+pad2(m);
}
function parseWhen(text,now){
  now=now?new Date(now):new Date();
  var s=" "+String(text||"").toLowerCase().replace(/[’‘]/g,"'").replace(/[–—]/g,"-").replace(/\s+/g," ")+" ";
  var base=new Date(now.getFullYear(),now.getMonth(),now.getDate());
  function add(n){var d=new Date(base);d.setDate(d.getDate()+n);return d}
  function nextWd(i,skip){var diff=(i-base.getDay()+7)%7;if(skip&&diff===0)diff=7;return add(diff)}
  var day=null,by=false,m,T="(\\d{1,2})(?:[:.](\\d{2}))? ?(am|pm|a\\.m\\.|p\\.m\\.)?";
  var mon="(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\\.?";
  function mk(dd,mi,yy){if(mi<0||dd<1||dd>31)return null;var y=yy?(+yy<100?2000+ +yy:+yy):base.getFullYear();var d=new Date(y,mi,dd);if(d.getMonth()!==mi)return null;if(!yy&&d<base&&(base-d)>60*DAY)d=new Date(y+1,mi,dd);return d}
  if((m=s.match(new RegExp("\\b(\\d{1,2})(?:st|nd|rd|th)?(?: of)? "+mon+"(?: (\\d{4}))?"))))day=mk(+m[1],MONN.indexOf(m[2]),m[3]);
  else if((m=s.match(new RegExp("\\b"+mon+" (\\d{1,2})(?:st|nd|rd|th)?\\b(?:,? (\\d{4}))?"))))day=mk(+m[2],MONN.indexOf(m[1]),m[3]);
  else if((m=s.match(/\b(\d{1,2})\/(\d{1,2})(?:\/(\d{2,4}))?\b/)))day=mk(+m[1],+m[2]-1,m[3]);
  if(!day){
    if(/\b(today|tonight|this (morning|afternoon|evening)|later on|end of (the )?day|close of business|eod|cob)\b/.test(s))day=base;
    else if(/\b(tomorrow|tmrw|tmr)\b/.test(s))day=add(1);
    else if((m=s.match(/\b(next |this |on |by |until )?(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tues?|wed|weds|thu|thur|thurs|fri)\b/))){
      var key=m[2].slice(0,3),idx=["sun","mon","tue","wed","thu","fri","sat"].indexOf(key);day=nextWd(idx,m[1]==="next ");
    }
    else if(/\b(this |the |at the )?weekend\b/.test(s))day=nextWd(6);
    else if((m=s.match(/\b(?:in|within) (\d+|a|an|one|two|three|four|five|six|seven|ten|fourteen) (working |business )?(day|days|week|weeks)\b/))){
      var n=numw(m[1]);if(/week/.test(m[3]))day=add(7*n);
      else if(m[2]){var d0=new Date(base),k=0;while(k<n){d0.setDate(d0.getDate()+1);if(d0.getDay()%6)k++}day=d0}
      else day=add(n);
      by=true;
    }
    else if((m=s.match(/\bin (\d+) ?(?:-|to|or) ?(\d+) (working |business )?days\b/))){day=add(+m[2]+(m[3]?Math.ceil(+m[2]/5)*2:0));by=true}
    else if((m=s.match(/\b(24|48|72) ?(hours|hrs|h)\b/))){day=add(+m[1]/24);by=true}
    else if(/\bend of (the |this )?week\b/.test(s)){day=nextWd(5);by=true}
    else if(/\bnext week\b/.test(s)){day=add(((5-base.getDay()+7)%7)+7);by=true}
    else if(/\bend of (the |this )?month\b/.test(s)){day=new Date(base.getFullYear(),base.getMonth()+1,0);by=true}
  }
  if(!day&&/\b(yesterday|last (week|night|month|monday|tuesday|wednesday|thursday|friday|saturday|sunday))\b/.test(s))return null;
  var from=null,to=null,byTime=false;
  if((m=s.match(new RegExp("\\bbetween "+T+" (?:and|-|to) "+T))) || (m=s.match(new RegExp("\\b(?:from )?"+T+" ?(?:-|to|until|till) ?"+T+"(?=[ ,.;!)])")))){
    var ap1=(m[3]||"").replace(/\./g,""),ap2=(m[6]||"").replace(/\./g,"");
    if(ap1||ap2||+m[1]<=23&&+m[4]<=23){
      from=tclock(m[1],m[2],ap1||(ap2==="pm"&&+m[1]<=+m[4]?"pm":ap2==="am"?"am":""));to=tclock(m[4],m[5],ap2,ap1);
      if(from&&to&&to<=from)to=null;
      if(!ap1&&!ap2&&!m[2]&&!m[5]&&!/\bbetween\b/.test(m[0]))from=to=null;   /* "3-4 days" is not a time */
    }
  }
  if(!from){
    if((m=s.match(/\b(?:(by|before|at|around|about|from|after|for) )?(\d{1,2})(?:[:.](\d{2}))? ?(am|pm|a\.m\.|p\.m\.)(?=[^a-z]|$)/))||(m=s.match(/\b(?:(by|before|at|around|about|from|after|for) )?([01]?\d|2[0-3])[:.]([0-5]\d)\b/))){
      from=tclock(m[2],m[3],(m[4]||"").replace(/\./g,""));byTime=m[1]==="by"||m[1]==="before";
    }else if((m=s.match(/\b(by|before|at|around|after) (\d{1,2})(?: o'?clock)?\b(?! ?(days?|weeks?|hours?|mins?|minutes?|working|business))/))){
      from=tclock(m[2],0,"");byTime=m[1]==="by"||m[1]==="before";
    }else if(/\b(noon|midday|lunchtime)\b/.test(s)){from="12:00";byTime=/\bby (noon|midday|lunchtime)\b/.test(s)}
    else if(/\b(end of (the )?day|close of business|eod|cob)\b/.test(s)){from="17:00";byTime=true}
    else if(/\bfirst thing\b/.test(s)){from="08:00";to="10:00"}
    else if(/\bmorning\b/.test(s)){from="08:00";to="12:00"}
    else if(/\bafternoon\b/.test(s)){from="12:00";to="17:00"}
    else if(/\b(evening|tonight)\b/.test(s)){from="17:00";to="20:00"}
  }
  if(from&&!day){var tt=from.split(":");day=new Date(base);day.setHours(+tt[0],+tt[1]);day=day>now?base:add(1)}
  if(!day)return null;
  if(day<base)return null;
  if(from){var st=new Date(day);var p2=from.split(":");st.setHours(+p2[0],+p2[1]);if(st<now&&sameDay(day,now)&&!to)return null}
  if(!from&&/\bby\b/.test(s)&&!by)by=true;
  var dl=sameDay(day,base)?"Today":sameDay(day,add(1))?"Tomorrow":fmtDay(day);
  var label=from?(dl+", "+(to?from+"–"+to:(byTime?"by ":"")+from)):(by?"By "+(dl==="Today"||dl==="Tomorrow"?dl.toLowerCase():dl):dl+", any time");
  return {when:from?"slot":(by?"by":"slot"),date:ymdL(day),from:from||"",to:to||"",label:label};
}
function parseRef(text){
  var re=/\b(?:ref(?:erence)?|job|case|ticket|claim|booking|order|complaint)(?: ?(?:no\.?|number|num|#|id|ref(?:erence)?))?(?: is)?\s*[:#.]?\s*([A-Z0-9][A-Z0-9\-\/]{2,19})\b/gi,m;
  while((m=re.exec(String(text||"")))){if(/\d/.test(m[1]))return m[1].toUpperCase()}
  return "";
}
function sugHtml(text,d){
  var p=parseWhen(text),r=parseRef(text);
  if(!p&&!r)return "";
  var using=p&&d&&d.when===p.when&&d.date===p.date&&(d.from||"")===p.from&&(d.to||"")===p.to;
  var bits=(p?'<strong>'+esc(p.label)+'</strong>':"")+(r?(p?" · ":"")+'ref <span class="mono">'+esc(r)+'</span>':"");
  if(using&&(!r||d.ref===r))return '<p class="suggest ok">✓ Using what they said: '+bits+'. Check it below.</p>';
  return '<div class="suggest"><p>Sounds like '+bits+'</p><button type="button" class="btn" data-a="use-sug">Use this</button></div>';
}

/* ---------- 2. reminders by default ---------- */
function defaultEmail(t){
  if(t.emailRemind===undefined&&S.user&&S.user.email&&S.emailReady&&calTimes(t).length){t.emailRemind=true;logK(t,"Email reminders on (the default). You can turn them off.","email",{auto:true});return true}
  return false;
}
function soonReminders(t){
  if(!calTimes(t).length)return "";
  return '<div class="stack-s" style="margin-top:4px">'+calBlock(t)+'</div>';
}

/* ---------- 3. a helper who gets nudged ---------- */
function loadHelper(id){
  if(!S.helpers)S.helpers={};if(S.helpers[id]!==undefined||S.helperLoading===id)return;S.helperLoading=id;
  sb.from("helpers").select("task_id,email,status").eq("task_id",id).then(function(r){S.helperLoading=null;S.helpers[id]=(r.data&&r.data[0])||null;if(S.view.name==="task"&&S.view.id===id)render()},function(){S.helperLoading=null});
}
function helperBlock(t){
  if(!t.shareToken||!S.user||!S.emailReady)return "";
  loadHelper(t.id);var hp=S.helpers&&S.helpers[t.id],d=S.draft;
  if(hp===undefined)return "";
  if(hp&&hp.status==="confirmed")return '<div class="note stack-s"><p><strong>Sorted will nudge '+esc(hp.email)+'</strong> when this is due, at the same times as your own reminders. The nudge doesn’t say what it is.</p>'+(t.emailRemind?"":'<p>Your email reminders are off for this task, so no nudges go out. Turn them on above.</p>')+'<button class="link" data-a="helper-off" style="align-self:flex-start">Stop nudging them</button></div>';
  if(hp&&hp.status==="pending")return '<div class="note stack-s"><p><strong>Waiting for '+esc(hp.email)+' to say yes.</strong> Sorted asked them once. If they don’t reply, they won’t hear from Sorted again.</p><button class="link" data-a="helper-off" style="align-self:flex-start">Cancel</button></div>';
  if(hp&&hp.status==="stopped")return '<div class="note"><p>'+esc(hp.email)+' asked not to get nudges.</p></div>';
  var nm=d.hname!==undefined?d.hname:localGet("name");
  return '<div class="note stack-s"><p><strong>Want Sorted to nudge them too?</strong> When it’s due, they get a short email with this link, so they can check in with you. Sorted asks them first, and they can stop at any time.</p><form class="stack-s" data-f="helper"><label class="f">Their email<input type="email" id="f-hemail" name="hemail" autocomplete="off" value="'+esc(d.hemail||"")+'"></label><label class="f">Your first name<span class="hint">So they know it’s you</span><input type="text" id="f-hname" name="hname" maxlength="40" value="'+esc(nm||"")+'"></label>'+(d.herr?'<p class="err">'+esc(d.herr)+'</p>':"")+'<button class="btn block" type="submit">Ask them</button></form></div>';
}
function localGet(k){try{return localStorage.getItem("sorted.local."+k)||""}catch(e){return ""}}
function localSet(k,v){try{localStorage.setItem("sorted.local."+k,v)}catch(e){}}
function viewHelper(){
  var v=S.view,r=S.helperResult;
  var h='<header class="bar"><span class="mark">sorted<b>.</b></span></header><main class="stack fade" style="margin-top:8px">';
  if(r==="busy")return h+'<p class="muted">One moment…</p></main>';
  if(r==="confirmed")return h+'<h1 class="h2">Thanks. You’re in the loop.</h1><p>When it’s due, Sorted will send you a short email with the link you were sent. It won’t say what the task is.</p><p class="muted">Every nudge has a link to stop them.</p></main>';
  if(r==="stopped")return h+'<h1 class="h2">Done. No more nudges.</h1><p>Sorted won’t email you about this again.</p></main>';
  if(r==="unknown")return h+'<h1 class="h2">This link doesn’t work any more.</h1><p class="muted">The person may have switched it off. You don’t need to do anything.</p></main>';
  if(v.action==="stop")return h+'<h1 class="h2">Stop the nudges?</h1><p>You won’t get any more emails from Sorted about this.</p><button class="btn primary block" data-a="helper-answer" data-v="stop">Stop them</button></main>';
  return h+'<h1 class="h2">Get a nudge when it’s due?</h1><p>Someone you know asked Sorted to email you when a thing they’re waiting on is due, so you can check in with them. The email won’t say what it is.</p><button class="btn primary block" data-a="helper-answer" data-v="yes">Yes, nudge me</button><p class="muted" style="font-size:16px">If you’d rather not, just close this page. Sorted won’t email you again.</p></main>';
}

/* ---------- 4. letters: a complaint, and a subject access request ---------- */
function oneMonth(d){var y=d.getFullYear(),mo=d.getMonth()+1,day=d.getDate(),r=new Date(y,mo,day);if(r.getDate()!==day)r=new Date(y,mo+1,0);return r}
function inDays(n){var d=new Date();d.setHours(0,0,0,0);d.setDate(d.getDate()+n);return d}
function letterWho(t){var p=t.promises[t.promises.length-1];return (t.call&&t.call.who)||(p&&p.party)||(t.fix&&t.fix.party)||(t.renew&&t.renew.provider)||""}
function letterRef(t){for(var i=t.promises.length-1;i>=0;i--)if(t.promises[i].ref)return t.promises[i].ref;return (t.fix&&t.fix.jobRef)||""}
function complaintText(t,d){
  var who=d.lwho||letterWho(t)||"Sir or Madam",ref=letterRef(t),lines=[];
  t.events.forEach(function(e){if(/^(Called|Emailed|Messaged|Wrote to) .*(Nothing agreed|No reply)/.test(e.label))lines.push("- "+fmtDay(new Date(e.at))+": "+e.label.replace(/^Called/,"I called").replace(/^Emailed/,"I emailed").replace(/^Messaged/,"I messaged").replace(/^Wrote to/,"I wrote to"))});
  t.promises.forEach(function(p){
    var st={missed:"This didn’t happen.",replaced:"The date was later changed.",kept:"This happened.",open:"This is still outstanding."}[p.status]||"";
    lines.push("- "+fmtDay(new Date(p.loggedAt||t.created))+": "+(p.party||who)+" said “"+p.said+"” ("+whenText(p).replace(/^By/,"by")+(p.ref?", ref "+p.ref:"")+"). "+st);
  });
  var missed=t.promises.filter(function(p){return p.status==="missed"}).length;
  return "Subject: Complaint: "+t.title+(ref?" (ref "+ref+")":"")+"\n\nDear "+who+",\n\nI’m making a formal complaint about "+t.title.replace(/^./,function(c){return c.toLowerCase()})+"."+(missed?" "+(missed===1?"A promise you made to me was":missed+" promises you made to me were")+" not kept.":"")+"\n\nWhat has happened so far:\n"+(lines.length?lines.join("\n"):"- (add the dates and what was said)")+"\n\nWhat I want you to do:\n"+(d.lwant||"").trim()+"\n\nPlease reply within 14 days. If we can’t resolve this, I’ll take it to the relevant ombudsman or redress scheme.\n\nYours sincerely,\n"+(d.lname||"").trim();
}
function dsarText(t,d){
  var who=d.lwho||letterWho(t)||"Data Protection Officer",ref=letterRef(t);
  return "Subject: Subject access request\n\nDear "+who+",\n\nI’m making a subject access request under Article 15 of the UK GDPR.\n\nPlease send me:\n1. A copy of all the personal data you hold about me, including call notes, emails and account records.\n2. Why you use it, who you’ve shared it with, how long you’ll keep it, and where you got it from.\n3. Details of any automated decisions you’ve made about me.\n\nTo help you find my information:\nName: "+(d.lname||"").trim()+((d.ldetails||"").trim()?"\n"+d.ldetails.trim():"")+(ref?"\nReference: "+ref:"")+"\n\nPlease reply within one calendar month of receiving this request. If you need more information to confirm who I am, please tell me straight away.\n\nYours sincerely,\n"+(d.lname||"").trim();
}
function wantDefault(t){return t.mode==="fix"?"Fix it, or give me a firm date and time when it will be fixed, and keep to it.":t.mode==="renew"?"Process my renewal and confirm in writing when it will be done.":"Give me a firm date and time, in writing, and keep to it."}
function lettersBlock(t,s){
  if(s==="done"||S.view.panel==="promise"||(S.view.panel==="call"&&!recentMiss(t)))return "";
  if(!t.promises.length&&!t.events.some(function(e){return /Nothing agreed|No reply/.test(e.label)}))return "";
  var p=S.view.panel,d=S.draft,m=t.promises.filter(function(x){return x.status==="missed"}).length;
  if(p==="complaint"||p==="dsar"){
    var dsar=p==="dsar",h='<section class="sheet stack" id="letters"><div class="stack-s"><p class="eyebrow">Put it in writing</p><h2 class="h2">'+(dsar?"Ask what they hold about you":"Your complaint")+'</h2>';
    h+=dsar?'<p>This is a subject access request. It’s free, and the law gives them one month to reply. What they send often shows what they knew and when.</p>':'<p>Sorted fills this in from what’s happened so far. Check it before you send it.</p>';
    h+='</div>';
    if(d.letter){
      h+='<textarea class="copybox" id="lettertext" rows="14">'+esc(d.letter)+'</textarea>';
      h+='<button class="btn primary block" data-a="letter-copy">Copy the letter</button>';
      h+='<a class="btn block" data-a="letter-mail" href="mailto:?subject='+encodeURIComponent((d.letter.match(/^Subject: (.*)/)||[,""])[1])+'&body='+encodeURIComponent(d.letter.replace(/^Subject: .*\n\n/,""))+'">Open it in my email app</a>';
      h+='<p class="muted" style="font-size:16px">'+(dsar?"Send it to their data protection or privacy contact. You’ll find it in their privacy notice, usually linked at the bottom of their website.":"Send it to their complaints address, from their official website or your paperwork. Keep a copy.")+'</p>';
      if(!openPromise(t))h+='<button class="btn block" data-a="letter-track">'+(dsar?"Track the one-month deadline ("+esc(fmtDay(oneMonth(new Date())))+")":"Track their reply (by "+esc(fmtDay(inDays(14)))+")")+'</button>';
      if(!dsar)h+='<p class="muted" style="font-size:16px">If they don’t sort it out, most sectors have a free ombudsman or redress scheme. You can usually go to them after 8 weeks, or sooner if the company sends a final response.</p>';
      h+='<button class="link" data-a="letter-edit" style="text-align:left">Change the details</button>';
    }else{
      h+='<form class="stack" data-f="letter"><label class="f">Who it’s to<input type="text" id="f-lwho" name="lwho" value="'+esc(d.lwho!==undefined?d.lwho:letterWho(t))+'"></label>';
      if(!dsar)h+='<label class="f">What you want them to do<textarea id="f-lwant" name="lwant" rows="3">'+esc(d.lwant!==undefined?d.lwant:wantDefault(t))+'</textarea></label>';
      h+='<label class="f">Your full name<input type="text" id="f-lname" name="lname" autocomplete="name" value="'+esc(d.lname||"")+'"></label>';
      if(dsar)h+='<label class="f">Details to help them find you<span class="hint">Optional. For example your address, account number or the email you used with them.</span><textarea id="f-ldetails" name="ldetails" rows="3">'+esc(d.ldetails||"")+'</textarea></label>';
      h+='<p class="muted" style="font-size:16px">Your name and details go into the letter only. Sorted doesn’t save them.</p>';
      if(d.err)h+='<p class="err">'+esc(d.err)+'</p>';
      h+='<button class="btn primary block" type="submit">Write it</button></form>';
    }
    return h+'<button class="btn block" data-a="letter" data-p="">Close</button></section>';
  }
  var h2='<section class="stack-s" id="letters"><h2 class="h3">Put it in writing</h2>';
  if(m)h2+='<p class="muted">'+(m===1?"They’ve missed a promise.":"They’ve missed "+m+" promises.")+' A written complaint with the dates is hard to ignore.</p>';
  h2+='<button class="btn block'+(m?" primary":"")+'" data-a="letter" data-p="complaint">Write my complaint</button>';
  h2+='<button class="btn block" data-a="letter" data-p="dsar">Ask what they hold about you</button>';
  h2+='<p class="muted" style="font-size:16px">The second is a subject access request. It’s free, and they must reply within a month.</p></section>';
  return h2;
}

/* ---------- 5. forwarded emails ---------- */
function loadInbox(){
  sb.rpc("my_inbound_address").then(function(r){
    S.inboundAddr=(r&&r.data)||null;
    if(!S.inboundAddr){S.inbox=[];return}
    sb.from("inbound_items").select("id,subject,body,received_at").is("used_at",null).order("received_at",{ascending:false}).limit(20).then(function(q){
      S.inbox=(q&&q.data)||[];if(S.view.name==="home"||S.view.name==="inbound")render();
    });
  },function(){});
}
function cleanMail(body){
  return String(body||"").split(/\r?\n/).filter(function(l){return !/^\s*(>|-{3,}.*forwarded|begin forwarded|from:|sent:|date:|to:|cc:|subject:|on .{6,80} wrote:$)/i.test(l)}).join("\n");
}
function mailFrom(body){var m=String(body||"").match(/^\s*from:\s*"?([^"<\n]+?)"?\s*(<[^>]+>)?\s*$/im);return m?m[1].trim():""}
function mailInfo(it){
  var txt=cleanMail(it.body),when=null,said="";
  var parts=txt.replace(/\s+/g," ").replace(/([.!?])\s+/g,"$1\n").split("\n");
  for(var i=0;i<parts.length&&!when;i++){var p=parseWhen(parts[i],it.received_at);if(p){when=p;said=parts[i].trim()}}
  if(!said)said=it.subject||"";
  if(said.length>200)said=said.slice(0,197)+"…";
  return {when:when,said:said,ref:parseRef((it.subject||"")+" "+txt),party:mailFrom(it.body)};
}
function inboxBlock(){
  if(!S.inbox||!S.inbox.length)return "";
  var h='<section class="stack"><div class="group-h"><h2 class="h3">From your email</h2><span class="mono muted">'+S.inbox.length+'</span></div>';
  S.inbox.forEach(function(it){var mi=mailInfo(it);
    h+='<button class="slip" data-a="inbound" data-id="'+esc(it.id)+'"><div class="slip-main"><span class="slip-kind">Forwarded '+esc(stampLabel(it.received_at))+(mi.party?" · "+esc(mi.party):"")+'</span><span class="slip-title">'+esc(it.subject||"(no subject)")+'</span></div><div class="slip-stub"><span>'+(mi.when?"Sounds like":"No date found")+'</span><span class="mono">'+esc(mi.when?mi.when.label:"")+(mi.ref?" · "+esc(mi.ref):"")+'</span></div></button>';
  });
  return h+'</section>';
}
function viewInbound(){
  var it=(S.inbox||[]).filter(function(x){return x.id===S.view.id})[0];
  var h=topbar('<button class="link" data-a="home">← All tasks</button>')+'<main class="stack fade" style="margin-top:8px">';
  if(!it)return h+'<p>That email isn’t here any more.</p></main>';
  var mi=mailInfo(it),open=S.tasks.filter(function(t){return state(t)!=="done"&&(t.mode==="call"||(t.fix&&t.fix.step==="done")||(t.renew&&t.renew.step==="done"))});
  h+='<section class="stack-s"><p class="eyebrow">Forwarded email'+(mi.party?" · "+esc(mi.party):"")+'</p><h1 class="h2">'+esc(it.subject||"(no subject)")+'</h1></section>';
  h+='<section class="sheet stack-s"><p class="h3">'+(mi.when?"Sounds like "+esc(mi.when.label):"No date found")+(mi.ref?' · <span class="mono">'+esc(mi.ref)+'</span>':"")+'</p><p>“'+esc(mi.said)+'”</p><details><summary>Show the email</summary><pre class="copybox" style="white-space:pre-wrap;max-height:320px;overflow:auto">'+esc(cleanMail(it.body).trim().slice(0,4000))+'</pre></details></section>';
  h+='<section class="stack-s"><h2 class="h3">Add it to a task</h2>';
  if(!open.length)h+='<p class="muted">Start a task first, then come back to this.</p>';
  open.slice(0,8).forEach(function(t){h+='<button class="btn block" style="justify-content:flex-start;text-align:left" data-a="inbound-use" data-id="'+esc(t.id)+'">'+esc(t.title)+'</button>'});
  h+='<button class="btn block" data-a="inbound-new">Start a new task from it</button>';
  h+='</section><button class="link" data-a="inbound-del" style="text-align:left">Delete this email from Sorted</button></main>';
  return h;
}
function inboundDraft(it){
  var mi=mailInfo(it),d={said:mi.said,party:mi.party||undefined,ref:mi.ref||undefined,inboundId:it.id};
  if(mi.when){d.when=mi.when.when;d.date=mi.when.date;d.from=mi.when.from;d.to=mi.when.to}
  if(d.party===undefined)delete d.party;if(d.ref===undefined)delete d.ref;
  return d;
}
function forwardHint(){
  if(!S.inboundAddr)return "";
  return '<div class="note stack-s"><p><strong>Got their reply by email?</strong> Forward it to your Sorted address and it will pick out the date for you. Forward it from '+esc(S.user.email)+'.</p><p class="mono" style="word-break:break-all">'+esc(S.inboundAddr)+'</p><button class="link" data-a="copy-inbound" style="align-self:flex-start">Copy the address</button></div>';
}
