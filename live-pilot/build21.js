const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='a9b8245f323619a9d1d4aed72e5c88df42a0e225')throw new Error('base mismatch '+h(s));
function R(a,b){const k=s.split(a).length-1;if(k!==1)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v21: is the clock running? four rows under Pilot numbers ----

// the app reports sign-in failures it sees: a kind and a time, nothing else
R(`var sb = window.supabase.createClient(SUPA_URL, SUPA_KEY, {auth:{persistSession:true,autoRefreshToken:true,detectSessionInUrl:true,flowType:"implicit"}});`,`var sb = window.supabase.createClient(SUPA_URL, SUPA_KEY, {auth:{persistSession:true,autoRefreshToken:true,detectSessionInUrl:true,flowType:"implicit"}});
function repErr(k){try{sb.rpc("report_auth_error",{p_kind:k}).then(function(){},function(){})}catch(e){}}
if(LINK_ERR)repErr(LINK_ERR==="expired"?"link_expired":"link_invalid");`);
R(`if(r.error){d.err="Starting without an email`,`if(r.error){repErr("anon_failed");d.err="Starting without an email`);
R(`if(r.error){var wsec=`,`if(r.error){if(!/after \\d+ seconds|rate|many/i.test(r.error.message||""))repErr("send_failed");var wsec=`);
R(`if(r.error){d.cerr="That code didn’t work. Use the newest email`,`if(r.error){repErr("code_failed");d.cerr="That code didn’t work. Use the newest email`);
R(`if(r.error){d.cerr=/expired|invalid/i.test`,`if(r.error){repErr("code_failed");d.cerr=/expired|invalid/i.test`);
R(`if(r.error){var cm2=r.error.message||"";if(/already|registered|exists|taken/i.test(cm2)){d.cexists=true}else{`,`if(r.error){var cm2=r.error.message||"";if(/already|registered|exists|taken/i.test(cm2)){d.cexists=true}else{if(!/after \\d+ seconds|rate|many/i.test(cm2))repErr("send_failed");`);

// load the health rows with the numbers
R(`  sb.rpc("pilot_metrics",{include_admins:S.pilot.mine}).then(function(r){`,`  sb.rpc("pilot_health").then(function(r){S.pilot.h=r.error?{err:true}:r.data;if(S.view.name==="pilot")render()},function(){S.pilot.h={err:true};render()});
  sb.rpc("pilot_metrics",{include_admins:S.pilot.mine}).then(function(r){`);
R(`function viewPilot(){`,`function agoTxt(t,now){if(!t)return "never";var m=Math.round((Date.parse(now)-Date.parse(t))/60000);return m<1?"just now":m<60?m+" min ago":m<2880?Math.round(m/60)+" hours ago":Math.round(m/1440)+" days ago"}
function healthRows(H){
  if(!H)return {rows:[],clock:null};
  if(H.err)return {rows:[["red","Health","Couldn’t load the health check. Treat every number below as unchecked."]],clock:false};
  var n=H.now,sc=H.scheduler||{},rm=H.reminders||{},au=H.auth||{},ib=H.inbound||{},rows=[];
  var runMin=sc.last_run?(Date.parse(n)-Date.parse(sc.last_run))/60000:1e9,httpMin=sc.http_at?(Date.parse(n)-Date.parse(sc.http_at))/60000:1e9,why=[];
  if(!sc.last_run)why.push("The reminder job has never run.");else if(runMin>25)why.push("The reminder job last ran "+agoTxt(sc.last_run,n)+". It should run every 10 minutes.");else if(sc.last_status!=="succeeded")why.push("The reminder job’s last run "+(sc.last_status||"did not finish")+".");
  if(sc.last_run&&runMin<=25){if(!sc.http_at||httpMin>25)why.push("The reminder sender hasn’t replied since "+agoTxt(sc.http_at,n)+".");else if(sc.http_timed_out)why.push("The reminder sender timed out.");else if(sc.http_status!==200)why.push("The reminder sender replied with an error ("+sc.http_status+").");else if(sc.http_bad)why.push("The reminder sender ran but couldn’t send: email isn’t set up.")}
  if((sc.daily_failed||[]).length)why.push("Daily clean-up failed: "+sc.daily_failed.join(", ")+".");
  var clock=!why.length;
  rows.push([clock?"ok":"red","Scheduler",clock?"Reminder job ran "+agoTxt(sc.last_run,n)+" and the sender replied OK. Daily clean-ups OK.":why.join(" ")+" Due Return Rate can’t be trusted until this is green."]);
  var rbad=(rm.overdue||0)+(rm.failed_7d||0);
  rows.push([rbad?"red":"ok","Reminders",(rm.overdue?rm.overdue+" overdue (still unsent 15 minutes after due). ":"None overdue. ")+(rm.failed_7d?rm.failed_7d+" failed in 7 days, last "+agoTxt(rm.last_failed,n)+". ":"None failed in 7 days. ")+(rm.sent_7d||0)+" sent in 7 days."]);
  var AK={link_expired:["expired link","expired links"],link_invalid:["used or broken link","used or broken links"],code_failed:["code that didn’t work","codes that didn’t work"],send_failed:["sign-in email that couldn’t be sent","sign-in emails that couldn’t be sent"],anon_failed:["no-email start that failed","no-email starts that failed"]};
  function kinds(o,map){return Object.keys(o||{}).map(function(k){var l=map[k];return o[k]+" "+(l?(typeof l==="string"?l:l[o[k]===1?0:1]):k.replace(/_/g," "))}).join(", ")}
  rows.push([au.system_24h?"red":(au.user_24h>=3?"amber":"ok"),"Sign-in",au.count_7d?au.count_7d+" in 7 days, last "+agoTxt(au.last,n)+": "+kinds(au.kinds,AK)+"."+(au.system_24h?" Sorted couldn’t send or start sign-ins in the last day.":""):"No sign-in errors in 7 days."]);
  var IK={bad_signature:"unsigned or forged",unknown_address:"to an unknown address",not_owner:"forwarded from a different email",daily_limit:"over the daily limit",fetch_failed:"couldn’t read the email",store_failed:"couldn’t save",no_secret:"not set up",exception:"crashed",bad_json:"unreadable"};
  rows.push([ib.system_24h?"red":(ib.count_7d?"amber":"ok"),"Inbound email",(ib.count_7d?ib.count_7d+(ib.count_7d===1?" problem":" problems")+" in 7 days, last "+agoTxt(ib.last,n)+": "+kinds(ib.kinds,IK)+". ":"No problems in 7 days. ")+(ib.last_stored?"Last email stored "+agoTxt(ib.last_stored,n)+".":"No email stored yet.")]);
  return {rows:rows,clock:clock};
}
function healthHtml(H){
  var hr=healthRows(H);if(!hr.rows.length)return '<section class="sheet stack-s"><p class="h3">Is the clock running?</p><p class="muted">Checking…</p></section>';
  var W={ok:"OK",amber:"Check",red:"Failing"};
  return '<section class="sheet stack-s health"><p class="h3">Is the clock running?</p>'+hr.rows.map(function(r){return '<div class="hrow '+r[0]+'"><p><strong>'+esc(r[1])+'</strong> <span class="hstate">'+W[r[0]]+'</span></p><p>'+esc(r[2])+'</p></div>'}).join("")+'</section>';
}
function viewPilot(){`);
R(`  if(P.loading||!m){`,`  h+=healthHtml(P.h);
  if(P.loading||!m){`);
R(`  h+=big("Due Return Rate",`,`  if(healthRows(P.h).clock===false)h+='<p class="note" role="alert"><strong>Don’t trust Due Return Rate yet.</strong> The reminder clock isn’t confirmed as running. See the Scheduler row above.</p>';
  h+=big("Due Return Rate",`);
R(`.thread{list-style:none;margin:0;padding:0;display:flex;flex-direction:column}`,`.thread{list-style:none;margin:0;padding:0;display:flex;flex-direction:column}
.hrow{border-left:6px solid var(--rule);padding:6px 0 6px 12px;display:flex;flex-direction:column;gap:2px}
.hrow p{margin:0}
.hrow.ok{border-left-color:#2E7D4F}.hrow.amber{border-left-color:var(--yellow-edge)}.hrow.red{border-left-color:var(--danger);background:var(--danger-soft)}
.hstate{font-size:14px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;margin-left:6px}
.hrow.red .hstate{color:var(--danger)}`);

fs.writeFileSync('public/index.html',s);
const EXPECT='327f02128e1fe0e8b4f8f404589a2ba1dbc0f631';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v21 ok',h(s),s.length);
