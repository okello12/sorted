(function(){
var DB=JSON.parse(localStorage.getItem("__mockdb")||'{"tasks":[],"shares":[],"reminders":[],"helpers":[],"inbound_items":[]}');
if(!DB.reminders)DB.reminders=[];if(!DB.pilot_events)DB.pilot_events=[];if(!DB.helpers)DB.helpers=[];if(!DB.inbound_items)DB.inbound_items=[];if(!DB.case_notes)DB.case_notes=[];function persist(){localStorage.setItem("__mockdb",JSON.stringify(DB))}
var session=JSON.parse(localStorage.getItem("__mocksession")||"null");
var listeners=[];window.__otp=[];
function q(table){
  var op="select",payload=null,filters=[],self={};
  function fmatch(r,f){if(f[0].indexOf("data->>")===0){var k=f[0].slice(7);return String(r.data&&r.data[k])===String(f[1])}return r[f[0]]===f[1]}
  function run(){
    try{var fresh=localStorage.getItem("__mockdb");if(fresh)DB=JSON.parse(fresh)}catch(e){}  /* the "server" is localStorage, so a test can play another device */
    if(!DB[table])DB[table]=[];
    var rows=DB[table];
    if(op==="select"){var fr=rows.filter(r=>filters.every(f=>r[f[0]]===f[1]));return {data:(table==="tasks"||table==="shares")?fr.map(r=>({data:r.data,card:r.card})):fr.map(r=>Object.assign({},r)),error:null}}
    if(op==="upsert"&&Array.isArray(payload)){payload.forEach(function(p){if(!rows.some(r=>r.task_id===p.task_id&&r.kind===p.kind&&r.send_at===p.send_at&&(r.promise_id||null)===(p.promise_id||null)))rows.push(Object.assign({sent_at:null},p))});persist();return {data:null,error:null}}
    if(op==="upsert"){if(localStorage.getItem("__failWrites")==="1")return {data:null,error:{message:"offline (test)"}};if(localStorage.getItem("__failWrites")==="2")return {data:null,error:{message:"permission denied (test)",code:"42501"}};var i=rows.findIndex(r=>r.id===payload.id);var row=Object.assign({},payload,{updated_at:new Date().toISOString()});if(i>=0)rows[i]=row;else rows.push(row);persist();return {data:null,error:null}}
    if(op==="insert"&&Array.isArray(payload)){if(localStorage.getItem("__evfail")==="1")return {data:null,error:{message:"offline"}};payload.forEach(p=>rows.push(Object.assign({at:new Date().toISOString(),actor:session&&session.user.id},p)));persist();return {data:null,error:null}}
    if(op==="insert"){rows.push(Object.assign({},payload,{updated_at:new Date().toISOString()}));persist();return {data:null,error:null}}
    if(op==="update"){if(table==="tasks"&&localStorage.getItem("__failWrites")==="1")return {data:null,error:{message:"offline (test)"}};if(table==="tasks"&&localStorage.getItem("__failWrites")==="2")return {data:null,error:{message:"permission denied (test)",code:"42501"}};var hit=[];rows.forEach(r=>{if(filters.every(f=>fmatch(r,f))){Object.assign(r,payload,{updated_at:new Date().toISOString()});hit.push({id:r.id})}});persist();return {data:hit,error:null}}
    if(op==="delete"&&table==="shares"&&localStorage.getItem("__failShareDelete")==="1")return {data:null,error:{message:"test: delete refused"}};
    if(op==="delete"){DB[table]=rows.filter(r=>!filters.every(f=>r[f[0]]===f[1]));persist();return {data:null,error:null}}
  }
  self.select=function(){if(op==="update"||op==="insert")return self;op="select";return self};
  self.order=function(){return self};self.limit=function(){return self};self.gte=function(){return self};self.lt=function(){return self};
  self.upsert=function(p){op="upsert";payload=p;return self};
  self.insert=function(p){op="insert";payload=p;return self};
  self.update=function(p){op="update";payload=p;return self};
  self.delete=function(){op="delete";return self};
  self.eq=function(k,v){filters.push([k,v]);return self};
  self.is=function(k,v){filters.push([k,v]);return self};
  /* __slowWrites (ms) holds case saves in flight, so a test can act mid-save; __failWrites "1" fails case saves like a lost connection, "2" like a refusal from the server (v141) */
  /* v143: __dropAck "1" lets the next case save reach the "server" but loses its answer, like a dropped connection; the server's size cap (tasks_data_size) refuses a case over 100,000 bytes */
  self.then=function(a,b){if(table==="tasks"&&(op==="update"||op==="upsert")&&payload&&!Array.isArray(payload)&&payload.data&&JSON.stringify(payload.data).length>100000)return Promise.resolve({data:null,error:{message:'new row for relation "tasks" violates check constraint "tasks_data_size"',code:"23514"}}).then(a,b);
    if(table==="tasks"&&(op==="update"||op==="upsert")&&localStorage.getItem("__dropAck")==="1"){localStorage.removeItem("__dropAck");return Promise.resolve().then(run).then(function(){return Promise.reject(new TypeError("Failed to fetch"))}).then(a,b)}
    var d=+(localStorage.getItem("__slowWrites")||0);if(d&&table==="tasks"&&(op==="update"||op==="upsert"))return new Promise(function(r){setTimeout(r,d)}).then(run).then(a,b);return Promise.resolve(run()).then(a,b)};
  return self;
}
window.supabase={createClient:function(){
  return {
    from:q,
    rpc:function(name,args){
      if(name==="report_page_error"){var pe=JSON.parse(localStorage.getItem("__errs")||"[]");pe.push(args);localStorage.setItem("__errs",JSON.stringify(pe));return Promise.resolve({data:null,error:null})}
      if(name==="share_seen"){var sn=JSON.parse(localStorage.getItem("__seen")||"[]");sn.push(args.p_token);localStorage.setItem("__seen",JSON.stringify(sn));return Promise.resolve({data:null,error:null})}
      if(name==="get_share"){var s=DB.shares.find(r=>r.token===args.p_token);return Promise.resolve({data:s?[{card:s.card,updated_at:s.updated_at}]:[],error:null})}
      if(name==="invite_helper"){window.__invites=(window.__invites||0)+1;DB.helpers=DB.helpers.filter(h=>h.task_id!==args.p_task_id);DB.helpers.push({task_id:args.p_task_id,email:args.p_email.toLowerCase(),inviter_name:args.p_name,status:"pending",token:"tok"+"x".repeat(60)});persist();return Promise.resolve({data:"pending",error:null})}
      if(name==="remove_helper"){DB.helpers=DB.helpers.filter(h=>h.task_id!==args.p_task_id);persist();return Promise.resolve({data:null,error:null})}
      if(name==="helper_respond"){var hh=DB.helpers.find(h=>h.token===args.p_token);if(!hh)return Promise.resolve({data:"unknown",error:null});hh.status=args.p_action==="yes"?"confirmed":"stopped";persist();return Promise.resolve({data:hh.status,error:null})}
      if(name==="inbound_address_new"){var nn=String((+localStorage.getItem("__inboundN")||0)+1);localStorage.setItem("__inboundN",nn);return Promise.resolve({data:"log-new"+nn+"abcdef0123@inbound.getsorted.uk",error:null})}
      if(name==="my_inbound_address"||name==="my_inbound_address_get")return Promise.resolve({data:localStorage.getItem("__inbound")==="ready"&&name==="my_inbound_address_get"?"":localStorage.getItem("__inbound")==="1"?"log-abc123@inbound.getsorted.uk":null,error:null});
      if(name==="stash_carry"){window.__stash=(window.__stash||0)+1;var tk="tok-"+(session&&session.user.id);localStorage.setItem("__stashfor",session&&session.user.id);return Promise.resolve({data:tk,error:null})}
      if(name==="claim_carry"){var from=localStorage.getItem("__stashfor");var mp={};(args.p_pairs||[]).forEach(p=>mp[p[0]]=p[1]);DB.pilot_events.forEach(e=>{if(e.actor===from){if(mp[e.case_id])e.case_id=mp[e.case_id];e.actor=session.user.id}});persist();localStorage.setItem("__claimed",JSON.stringify(args));return Promise.resolve({data:true,error:null})}
      if(name==="pilot_health")return Promise.resolve({data:JSON.parse(localStorage.getItem("__health")||"null"),error:null});
      if(name==="report_auth_error"){var q=JSON.parse(localStorage.getItem("__reperr")||"[]");q.push(args.p_kind);localStorage.setItem("__reperr",JSON.stringify(q));return Promise.resolve({data:null,error:null})}
      if(name==="set_email_optout"){if(!DB.email_optouts)DB.email_optouts=[];var ou=session&&session.user&&session.user.id;DB.email_optouts=DB.email_optouts.filter(r=>r.user_id!==ou);if(args.p_off)DB.email_optouts.push({user_id:ou});persist();return Promise.resolve({data:!!args.p_off,error:null})}
      if(name==="touch_seen"){localStorage.setItem("__seenTouch",String((+localStorage.getItem("__seenTouch")||0)+1));return Promise.resolve({data:null,error:null})}
      if(name==="is_pilot_admin")return Promise.resolve({data:localStorage.getItem("__admin")==="1",error:null});
      if(name==="pilot_metrics"){window.__pm=args;return Promise.resolve({data:{people:3,include_admins:args.include_admins,funnel:{started:10,promised:7,matured:5,returned:4,acted:3,closed:2,closers:2,second:1},miss:{missed:2,recovered:1},return_hours_median:5.2,email:{anon_promises:4,emails_added:3},counts:{case_started:{total:10,week:6}}},error:null})}
      if(name==="record_outcome"){var oc=JSON.parse(localStorage.getItem("__outcomes")||"[]");oc.push(args);localStorage.setItem("__outcomes",JSON.stringify(oc));return Promise.resolve({data:null,error:null})}
      if(name==="drop_outcome"){var od=JSON.parse(localStorage.getItem("__outcomes")||"[]").filter(function(x){return x.p_promise!==args.p_promise});localStorage.setItem("__outcomes",JSON.stringify(od));return Promise.resolve({data:null,error:null})}
      if(name==="company_scores"){window.__scoresCalls=(window.__scoresCalls||0)+1;return Promise.resolve({data:JSON.parse(localStorage.getItem("__scores")||"[]"),error:null})}
      if(name==="case_reply_address")return Promise.resolve({data:localStorage.getItem("__replyOn")==="1"?"case-"+String(args.p_task_id).slice(0,8)+"@inbound.getsorted.uk":null,error:null});
      if(name==="add_share_note"){var sh=DB.shares.find(r=>r.token===args.p_token);if(!sh)return Promise.resolve({data:"gone",error:null});if(!sh.notes_on)return Promise.resolve({data:"off",error:null});DB.case_notes.push({id:"n"+Date.now(),task_id:sh.task_id,author:args.p_author,body:args.p_body,created_at:new Date().toISOString()});persist();return Promise.resolve({data:"ok",error:null})}
      if(name==="push_state"){var ps=(DB.push_subs||[]),pu=session&&session.user&&session.user.id;return Promise.resolve({data:{ready:localStorage.getItem("__pushReady")==="1",mine:!!ps.find(r=>r.user_id===pu&&r.endpoint===args.p_endpoint),count:ps.filter(r=>r.user_id===pu).length},error:null})}
      if(name==="push_save"){if(!/^https:\/\/(fcm\.googleapis\.com|web\.push\.apple\.com|updates\.push\.services\.mozilla\.com)\//.test(args.p_endpoint))return Promise.resolve({data:null,error:{message:"unknown push service"}});DB.push_subs=(DB.push_subs||[]).filter(r=>r.endpoint!==args.p_endpoint);DB.push_subs.push({user_id:session.user.id,endpoint:args.p_endpoint,p256dh:args.p_p256dh,auth:args.p_auth});persist();return Promise.resolve({data:DB.push_subs.length,error:null})}
      if(name==="push_drop"){var pd=session&&session.user&&session.user.id;DB.push_subs=(DB.push_subs||[]).filter(r=>!(r.user_id===pd&&(!args.p_endpoint||r.endpoint===args.p_endpoint)));persist();return Promise.resolve({data:0,error:null})}
      if(name==="email_reminders_ready")return Promise.resolve({data:localStorage.getItem("__emailReady")==="1",error:null});
      if(name==="delete_my_account"){DB={tasks:[],shares:[],reminders:[],helpers:[],inbound_items:[]};persist();return Promise.resolve({data:null,error:null})}
    },
    /* v135: storage for kept documents, in localStorage (__storage: [{bucket,name,size,type,at}]); __storageFail makes uploads fail */
    storage:{from:function(bucket){var all=function(){return JSON.parse(localStorage.getItem("__storage")||"[]")},put=function(a){localStorage.setItem("__storage",JSON.stringify(a))};return {
      upload:function(path,file,o){if(localStorage.getItem("__storageFail")==="1")return Promise.resolve({data:null,error:{message:"new row violates row-level security policy"}});var uid=session&&session.user&&session.user.id;if(String(path).split("/")[0]!==uid)return Promise.resolve({data:null,error:{message:"new row violates row-level security policy"}});var a=all();if(a.find(x=>x.name===path))return Promise.resolve({data:null,error:{message:"The resource already exists"}});a.push({bucket:bucket,name:path,size:file.size,type:(o&&o.contentType)||file.type,at:new Date().toISOString()});put(a);window.__uploads=(window.__uploads||[]).concat([path]);return Promise.resolve({data:{path:path},error:null})},
      list:function(prefix){var pre=String(prefix).replace(/\/$/,"")+"/";return Promise.resolve({data:all().filter(x=>x.bucket===bucket&&x.name.indexOf(pre)===0).map(x=>({name:x.name.slice(pre.length),created_at:x.at,metadata:{size:x.size,mimetype:x.type}})),error:null})},
      remove:function(paths){put(all().filter(x=>paths.indexOf(x.name)<0));return Promise.resolve({data:paths,error:null})},
      /* v139: the stored bytes are stand-ins ("mock file <path>"); __storageDlFail makes downloads fail */
      download:function(path){if(localStorage.getItem("__storageDlFail")==="1")return Promise.resolve({data:null,error:{message:"download failed"}});var x=all().find(y=>y.bucket===bucket&&y.name===path);if(!x)return Promise.resolve({data:null,error:{message:"Object not found"}});return Promise.resolve({data:new Blob(["mock file "+path],{type:x.type||"application/octet-stream"}),error:null})},
      createSignedUrl:function(path,sec){window.__signed=(window.__signed||[]).concat([[path,sec]]);return Promise.resolve({data:{signedUrl:"https://sorted.test/__signed/"+path},error:null})}
    }}},
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
