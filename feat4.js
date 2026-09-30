/* ---------- pilot measurement: step names and ids only, never case text ---------- */
var EVQ=null;
function evq(){if(!EVQ){try{EVQ=JSON.parse(localStorage.getItem("sorted.evq")||"[]")}catch(e){EVQ=[]}}return EVQ}
function saveQ(){EVQ=evq().slice(-50);try{localStorage.setItem("sorted.evq",JSON.stringify(EVQ))}catch(e){}}
function track(name,t,x){
  if(!S.user)return;
  x=x||{};var row={name:name,case_id:t?t.id:null,promise_id:null,props:{}};
  if(x.promise_id){row.promise_id=x.promise_id;delete x.promise_id}
  if(t)x.mode=t.mode;if(x.anon===undefined)x.anon=!S.user.email;row.props=x;
  evq().push(row);saveQ();clearTimeout(track.t);track.t=setTimeout(sendEvents,400);
}
function sendEvents(){
  if(sendEvents.busy||!S.user)return;var batch=evq().slice(0);if(!batch.length)return;sendEvents.busy=true;
  sb.from("pilot_events").insert(batch).then(function(r){sendEvents.busy=false;if(!r||!r.error){EVQ=evq().slice(batch.length);saveQ();if(EVQ.length)sendEvents()}},function(){sendEvents.busy=false});
}
function maturesAt(p){var w=window_(p);return w?w.end.toISOString():null}
function trackPromise(t,pr,afterMiss){
  track("promise_created",t,{promise_id:pr.id,matures_at:maturesAt(pr),src:pr.src||"note",has_ref:!!pr.ref});
  if(afterMiss)track("new_promise_after_miss",t,{promise_id:pr.id});
}
function trackClosed(t){track("case_closed",t,{promises:t.promises.length})}
function trackStart(t,d){
  track("case_started",t,{entry:d.fromCase?"sentence":"route"});
  if(t.mode!=="do"&&t.baseline)track("baseline_action_recorded",t,{choice:PLANS.indexOf(t.baseline)>=0?t.baseline:"own words"});
  if(S.tasks.some(function(x){return x!==t&&x.board==="done"}))track("second_case_started",t);
}
/* the first time someone looks at a case after its promise has come due */
function dueReturn(){
  var t=S.view.id?task(S.view.id):null;if(!t||t.board==="done")return;
  var p=openPromise(t);if(!p||p.dueSeen||phase(p)!=="check")return;
  p.dueSeen=nowIso();t._dirty=true;
  track("promise_due_return",t,{promise_id:p.id,src:S.retSrc||"app"});S.retSrc=null;
  setTimeout(save,0);
}

/* ---------- pilot numbers, for the people running the pilot ---------- */
function loadPilot(){
  S.pilot={loading:true,mine:!!(S.pilot&&S.pilot.mine)};render();
  sb.rpc("pilot_metrics",{include_admins:S.pilot.mine}).then(function(r){
    S.pilot.loading=false;if(r.error){S.pilot.err="Couldn’t load the numbers.";}else S.pilot.m=r.data;if(S.view.name==="pilot")render();
  },function(){S.pilot.loading=false;S.pilot.err="Couldn’t load the numbers.";render()});
}
function pct(a,b){return b?Math.round(a/b*100)+"%":"No data yet"}
function viewPilot(){
  var P=S.pilot||{},m=P.m,h=topbar('<button class="link" data-a="data">← Your data</button>');
  h+='<main class="stack fade" style="margin-top:8px"><div class="stack-s"><p class="eyebrow">Pilot numbers</p><h1 class="h2">Do people come back when it’s due?</h1></div>';
  if(P.loading||!m){h+='<p class="muted">'+(P.err?esc(P.err):"Loading…")+'</p></main>';return h}
  var f=m.funnel||{},mi=m.miss||{},em=m.email||{},c=m.counts||{};
  function big(label,val,sub){return '<section class="sheet stack-s"><p class="h3">'+label+'</p><p class="mono" style="font-size:40px;font-weight:700;line-height:1">'+val+'</p><p class="muted" style="font-size:15px">'+sub+'</p></section>'}
  h+=big("Due Return Rate",pct(f.returned,f.matured),f.returned+" of "+f.matured+" cases came back after their promise came due.");
  h+=big("Miss Recovery Rate",pct(mi.recovered,mi.missed),mi.recovered+" of "+mi.missed+" missed promises were chased or rescheduled on the same case.");
  h+=big("Second Situation Rate",pct(f.second,f.closers),f.second+" of "+f.closers+" people who finished a case started a new one.");
  var rows=[["Started a case",f.started,""],["Recorded a promise",f.promised,pct(f.promised,f.started)+" of started"],["Came back when due",f.returned,f.matured+" came due"],["Acted on the same case",f.acted,pct(f.acted,f.returned)+" of returns"],["Closed it",f.closed,pct(f.closed,f.acted)+" of those"],["Started another case",f.second,"people, of "+f.closers+" who closed one"]];
  var top=Math.max(1,f.started||0);
  h+='<section class="sheet stack"><p class="h3">The case loop</p>'+rows.map(function(r){return '<div class="stack-s" style="gap:4px"><div style="display:flex;justify-content:space-between;gap:12px"><span>'+r[0]+'</span><span class="mono">'+r[1]+'</span></div><div style="height:8px;background:var(--rule);border-radius:4px"><div style="height:8px;border-radius:4px;background:var(--ink);width:'+Math.min(100,Math.round((r[1]||0)/top*100))+'%"></div></div>'+(r[2]?'<span class="muted" style="font-size:14px">'+r[2]+'</span>':'')+'</div>'}).join("")+'</section>';
  var med=m.return_hours_median;
  h+='<section class="sheet stack-s"><p class="h3">Also worth watching</p><p>Email added when asked at a promise: <span class="mono">'+(em.emails_added||0)+' of '+(em.anon_promises||0)+'</span> ('+pct(em.emails_added||0,em.anon_promises||0)+')</p><p>Typical time from due to return: <span class="mono">'+(med==null?"No data yet":med<1?Math.round(med*60)+" min":med<48?Math.round(med)+" hours":Math.round(med/24)+" days")+'</span></p><p>People in the pilot: <span class="mono">'+(m.people||0)+'</span></p></section>';
  var names=["case_started","baseline_action_recorded","promise_created","email_added_at_promise","promise_due_return","outcome_kept","outcome_missed","outcome_rescheduled","chase_used","new_promise_after_miss","case_closed","recap_copied","second_case_started"];
  h+='<section class="sheet stack-s"><p class="h3">Events</p><div class="mono" style="font-size:14px;display:grid;grid-template-columns:1fr auto auto;gap:6px 14px"><span class="muted">event</span><span class="muted">7 days</span><span class="muted">all</span>'+names.map(function(n){var x=c[n]||{};return '<span style="word-break:break-all">'+n+'</span><span>'+(x.week||0)+'</span><span>'+(x.total||0)+'</span>'}).join("")+'</div></section>';
  h+='<section class="stack-s"><button class="btn block" data-a="pilot-mine">'+(P.mine?"Hide my own test cases":"Include my own test cases")+'</button><button class="link" data-a="pilot" style="align-self:flex-start">Refresh</button><p class="muted" style="font-size:15px">'+(P.mine?"Including":"Not including")+' cases from pilot admins. These numbers come from step records only. No case details are stored with them.</p></section></main>';
  return h;
}
