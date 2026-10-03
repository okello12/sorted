(function(){
var DB=JSON.parse(localStorage.getItem("__mockdb")||'{"tasks":[],"shares":[],"reminders":[],"helpers":[],"inbound_items":[]}');
if(!DB.reminders)DB.reminders=[];if(!DB.pilot_events)DB.pilot_events=[];if(!DB.helpers)DB.helpers=[];if(!DB.inbound_items)DB.inbound_items=[];if(!DB.case_notes)DB.case_notes=[];function persist(){localStorage.setItem("__mockdb",JSON.stringify(DB))}
var session=JSON.parse(localStorage.getItem("__mocksession")||"null");
var listeners=[];window.__otp=[];
function q(table){
  var op="select",payload=null,filters=[],self={};
  function run(){
    var rows=DB[table];
    if(op==="select"){var fr=rows.filter(r=>filters.every(f=>r[f[0]]===f[1]));return {data:(table==="tasks"||table==="shares")?fr.map(r=>({data:r.data,card:r.card})):fr.map(r=>Object.assign({},r)),error:null}}
    if(op==="upsert"&&Array.isArray(payload)){payload.forEach(function(p){if(!rows.some(r=>r.task_id===p.task_id&&r.kind===p.kind&&r.send_at===p.send_at))rows.push(Object.assign({sent_at:null},p))});persist();return {data:null,error:null}}
    if(op==="upsert"){if(localStorage.getItem("__failWrites")==="1")return {data:null,error:{message:"offline (test)"}};var i=rows.findIndex(r=>r.id===payload.id);var row=Object.assign({},payload,{updated_at:new Date().toISOString()});if(i>=0)rows[i]=row;else rows.push(row);persist();return {data:null,error:null}}
    if(op==="insert"&&Array.isArray(payload)){if(localStorage.getItem("__evfail")==="1")return {data:null,error:{message:"offline"}};payload.forEach(p=>rows.push(Object.assign({at:new Date().toISOString(),actor:session&&session.user.id},p)));persist();return {data:null,error:null}}
    if(op==="insert"){rows.push(Object.assign({},payload,{updated_at:new Date().toISOString()}));persist();return {data:null,error:null}}
    if(op==="update"){rows.forEach(r=>{if(filters.every(f=>r[f[0]]===f[1])){Object.assign(r,payload,{updated_at:new Date().toISOString()})}});persist();return {data:null,error:null}}
    if(op==="delete"){DB[table]=rows.filter(r=>!filters.every(f=>r[f[0]]===f[1]));persist();return {data:null,error:null}}
  }
  self.select=function(){op="select";return self};
  self.order=function(){return self};self.limit=function(){return self};self.gte=function(){return self};self.lt=function(){return self};
  self.upsert=function(p){op="upsert";payload=p;return self};
  self.insert=function(p){op="insert";payload=p;return self};
  self.update=function(p){op="update";payload=p;return self};
  self.delete=function(){op="delete";return self};
  self.eq=function(k,v){filters.push([k,v]);return self};
  self.is=function(k,v){filters.push([k,v]);return self};
  self.then=function(a,b){return Promise.resolve(run()).then(a,b)};
  return self;
}
window.supabase={createClient:function(){
  return {
    from:q,
    rpc:function(name,args){
      if(name==="share_seen"){var sn=JSON.parse(localStorage.getItem("__seen")||"[]");sn.push(args.p_token);localStorage.setItem("__seen",JSON.stringify(sn));return Promise.resolve({data:null,error:null})}
      if(name==="get_share"){var s=DB.shares.find(r=>r.token===args.p_token);return Promise.resolve({data:s?[{card:s.card,updated_at:s.updated_at}]:[],error:null})}
      if(name==="invite_helper"){window.__invites=(window.__invites||0)+1;DB.helpers=DB.helpers.filter(h=>h.task_id!==args.p_task_id);DB.helpers.push({task_id:args.p_task_id,email:args.p_email.toLowerCase(),inviter_name:args.p_name,status:"pending",token:"tok"+"x".repeat(60)});persist();return Promise.resolve({data:"pending",error:null})}
      if(name==="remove_helper"){DB.helpers=DB.helpers.filter(h=>h.task_id!==args.p_task_id);persist();return Promise.resolve({data:null,error:null})}
      if(name==="helper_respond"){var hh=DB.helpers.find(h=>h.token===args.p_token);if(!hh)return Promise.resolve({data:"unknown",error:null});hh.status=args.p_action==="yes"?"confirmed":"stopped";persist();return Promise.resolve({data:hh.status,error:null})}
      if(name==="my_inbound_address")return Promise.resolve({data:localStorage.getItem("__inbound")==="1"?"log-abc123@inbound.getsorted.uk":null,error:null});
      if(name==="stash_carry"){window.__stash=(window.__stash||0)+1;var tk="tok-"+(session&&session.user.id);localStorage.setItem("__stashfor",session&&session.user.id);return Promise.resolve({data:tk,error:null})}
      if(name==="claim_carry"){var from=localStorage.getItem("__stashfor");var mp={};(args.p_pairs||[]).forEach(p=>mp[p[0]]=p[1]);DB.pilot_events.forEach(e=>{if(e.actor===from){if(mp[e.case_id])e.case_id=mp[e.case_id];e.actor=session.user.id}});persist();localStorage.setItem("__claimed",JSON.stringify(args));return Promise.resolve({data:true,error:null})}
      if(name==="pilot_health")return Promise.resolve({data:JSON.parse(localStorage.getItem("__health")||"null"),error:null});
      if(name==="report_auth_error"){var q=JSON.parse(localStorage.getItem("__reperr")||"[]");q.push(args.p_kind);localStorage.setItem("__reperr",JSON.stringify(q));return Promise.resolve({data:null,error:null})}
      if(name==="is_pilot_admin")return Promise.resolve({data:localStorage.getItem("__admin")==="1",error:null});
      if(name==="pilot_metrics"){window.__pm=args;return Promise.resolve({data:{people:3,include_admins:args.include_admins,funnel:{started:10,promised:7,matured:5,returned:4,acted:3,closed:2,closers:2,second:1},miss:{missed:2,recovered:1},return_hours_median:5.2,email:{anon_promises:4,emails_added:3},counts:{case_started:{total:10,week:6}}},error:null})}
      if(name==="record_outcome"){var oc=JSON.parse(localStorage.getItem("__outcomes")||"[]");oc.push(args);localStorage.setItem("__outcomes",JSON.stringify(oc));return Promise.resolve({data:null,error:null})}
      if(name==="drop_outcome"){var od=JSON.parse(localStorage.getItem("__outcomes")||"[]").filter(function(x){return x.p_promise!==args.p_promise});localStorage.setItem("__outcomes",JSON.stringify(od));return Promise.resolve({data:null,error:null})}
      if(name==="company_scores"){window.__scoresCalls=(window.__scoresCalls||0)+1;return Promise.resolve({data:JSON.parse(localStorage.getItem("__scores")||"[]"),error:null})}
      if(name==="case_reply_address")return Promise.resolve({data:localStorage.getItem("__replyOn")==="1"?"case-"+String(args.p_task_id).slice(0,8)+"@inbound.getsorted.uk":null,error:null});
      if(name==="add_share_note"){var sh=DB.shares.find(r=>r.token===args.p_token);if(!sh)return Promise.resolve({data:"gone",error:null});if(!sh.notes_on)return Promise.resolve({data:"off",error:null});DB.case_notes.push({id:"n"+Date.now(),task_id:sh.task_id,author:args.p_author,body:args.p_body,created_at:new Date().toISOString()});persist();return Promise.resolve({data:"ok",error:null})}
      if(name==="email_reminders_ready")return Promise.resolve({data:localStorage.getItem("__emailReady")==="1",error:null});
      if(name==="delete_my_account"){DB={tasks:[],shares:[],reminders:[],helpers:[],inbound_items:[]};persist();return Promise.resolve({data:null,error:null})}
    },
    functions:{invoke:function(name,o){window.__ai=(window.__ai||[]);window.__ai.push({name:name,body:o&&o.body});var mode=localStorage.getItem('__aiMode')||'ok';
      if(mode!=='ok')return Promise.resolve({data:null,error:{context:{json:function(){return Promise.resolve({error:mode})}}}});
      var b=o.body;return Promise.resolve({data:{text:b.task==='improve'?'Dear Southwark Council,\n\nImproved: '+b.text.split('\n')[2]:'[assistant '+b.task+'] It says: '+(b.text||b.question).slice(0,60)},error:null})}},
    auth:{
      getSession:function(){return Promise.resolve({data:{session:session}})},
      onAuthStateChange:function(fn){listeners.push(fn);return {data:{subscription:{unsubscribe(){}}}}},
      signInWithOtp:function(o){window.__otp.push(o);if(localStorage.getItem('__rate')==='1')return Promise.resolve({error:{message:'For security purposes, you can only request this after 23 seconds.'}});return Promise.resolve({error:null})},
      signInAnonymously:function(o){if(localStorage.getItem('__anonHang')==='1')return new Promise(function(){});if(localStorage.getItem('__noanon')==='1')return Promise.resolve({data:{},error:{message:'Anonymous sign-ins are disabled'}});session={user:{id:'anon-'+Date.now(),is_anonymous:true}};localStorage.setItem('__mocksession',JSON.stringify(session));listeners.forEach(f=>f('SIGNED_IN',session));return Promise.resolve({data:{user:session.user},error:null})},
      updateUser:function(a){if(a.email==='taken@example.com')return Promise.resolve({data:{},error:{message:'A user with this email address has already been registered'}});window.__pendingEmail=a.email;return Promise.resolve({data:{user:session.user},error:null})},
      getUser:function(){return Promise.resolve({data:{user:session&&session.user}})},
      verifyOtp:function(o){if(o.type==='email_change'){if(o.token!=='123456')return Promise.resolve({data:{},error:{message:'Token has expired or is invalid'}});session.user=Object.assign({},session.user,{email:window.__pendingEmail,is_anonymous:false});localStorage.setItem('__mocksession',JSON.stringify(session));return Promise.resolve({data:{user:session.user,session:session},error:null})}if(o.token==='123456'){session={user:{id:'u-'+o.email,email:o.email}};localStorage.setItem('__mocksession',JSON.stringify(session));listeners.forEach(f=>f('SIGNED_IN',session));return Promise.resolve({data:{session:session},error:null})}return Promise.resolve({data:{},error:{message:'Token has expired or is invalid'}})},
      signOut:function(){session=null;localStorage.removeItem("__mocksession");listeners.forEach(f=>f("SIGNED_OUT",null));return Promise.resolve({})},
      __signIn:function(email){session={user:{id:"u-"+email,email:email}};localStorage.setItem("__mocksession",JSON.stringify(session));listeners.forEach(f=>f("SIGNED_IN",session))}
    }
  };
}};
})();
