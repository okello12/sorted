const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='327f02128e1fe0e8b4f8f404589a2ba1dbc0f631')throw new Error('base mismatch '+h(s));
function R(a,b){const k=s.split(a).length-1;if(k!==1)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v22: no silent hang, day-first dates, a quieter Waiting card ----

// 1. Start never hangs silently
R(`case "anon-start":d.err="";d.busy=true;render();
      sb.auth.signInAnonymously({options:{data:{pilot_notice_at:nowIso()}}}).then(function(r){d.busy=false;`,`case "anon-start":{d.err="";d.busy=true;render();var anDone=false;
      setTimeout(function(){if(anDone||S.user)return;d.busy=false;d.err="This is taking longer than it should. Check your connection, then tap Start again.";repErr("anon_slow");render()},10000);
      sb.auth.signInAnonymously({options:{data:{pilot_notice_at:nowIso()}}}).then(function(r){anDone=true;d.busy=false;`);
R(`function(){d.busy=false;d.err="Couldn’t start. Check your connection.";render()});break;
    case "go-claim":`,`function(){anDone=true;d.busy=false;d.err="Couldn’t start. Check your connection.";render()});break}
    case "go-claim":`);

// 2. dates are always day, month, year: no browser-locale guessing
R(`function newTask(mode){`,`var MONTHS=["January","February","March","April","May","June","July","August","September","October","November","December"];
function dateField(id,name,label,val,y0,y1,hint){
  var m=/^(\\d{4})-(\\d{2})-(\\d{2})$/.exec(val||""),Y=m?+m[1]:0,M=m?+m[2]:0,D=m?+m[3]:0,cy=new Date().getFullYear(),i,o;
  o='<fieldset class="f dp"><legend>'+label+'</legend>'+(hint?'<span class="hint">'+hint+'</span>':'')+'<input type="hidden" id="'+id+'" name="'+name+'" value="'+(m?esc(val):"")+'"><div class="dp-row">';
  o+='<select data-dp="'+id+'" data-part="d" aria-label="Day"><option value="">Day</option>';for(i=1;i<=31;i++)o+='<option value="'+i+'"'+(i===D?" selected":"")+'>'+i+'</option>';o+='</select>';
  o+='<select data-dp="'+id+'" data-part="m" aria-label="Month"><option value="">Month</option>';for(i=1;i<=12;i++)o+='<option value="'+i+'"'+(i===M?" selected":"")+'>'+MONTHS[i-1]+'</option>';o+='</select>';
  o+='<select data-dp="'+id+'" data-part="y" aria-label="Year"><option value="">Year</option>';var ys=Math.min(cy+y0,Y||cy),ye=Math.max(cy+y1,Y||cy);for(i=ys;i<=ye;i++)o+='<option value="'+i+'"'+(i===Y?" selected":"")+'>'+i+'</option>';o+='</select>';
  return o+'</div></fieldset>';
}
document.addEventListener("change",function(e){
  var el=e.target;if(!el||!el.getAttribute||!el.getAttribute("data-dp"))return;
  var id=el.getAttribute("data-dp"),hid=document.getElementById(id);if(!hid)return;
  var g=function(p){var x=document.querySelector('select[data-dp="'+id+'"][data-part="'+p+'"]');return x?x:null},sd=g("d"),sm=g("m"),sy=g("y");
  var D=+sd.value,M=+sm.value,Y=+sy.value;
  if(M&&Y&&D){var last=new Date(Y,M,0).getDate();if(D>last){D=last;sd.value=String(last)}}
  hid.value=(D&&M&&Y)?Y+"-"+String(M).padStart(2,"0")+"-"+String(D).padStart(2,"0"):"";
  S.draft[hid.name]=hid.value;
});
function newTask(mode){`);
R(`<label class="f">Date it ends<input type="date" id="f-expiry" name="expiry" value="'+esc(d.expiry!==undefined?d.expiry:(r.expiry||""))+'"></label>`,`'+dateField("f-expiry","expiry","Date it ends",d.expiry!==undefined?d.expiry:(r.expiry||""),-2,12)+'`);
R(`<label class="f" style="flex:1 1 12em">Date it ends<input type="date" id="f-expiry2" name="expiry"></label>`,`'+dateField("f-expiry2","expiry","Date it ends","",-2,12)+'`);
R(`<label class="f">When does the new one end?<span class="hint">Optional. Add it and Sorted will bring it back next time.</span><input type="date" id="f-newexp" name="newexp" value="'+esc(d.newexp||"")+'"></label>`,`'+dateField("f-newexp","newexp","When does the new one end?",d.newexp||"",0,12,"Optional. Add it and Sorted will bring it back next time.")+'`);
R(`<label class="f">'+(when==="by"?"By which day?":"Which day")+'<input type="date" id="f-date" name="date" value="'+esc(d.date||"")+'"></label>`,`'+dateField("f-date","date",(when==="by"?"By which day?":"Which day"),d.date||"",-1,2)+'`);
R(`<label class="f">'+(when==="by"?"By which day?":"Which day")+'<input type="date" id="f-mdate" name="date" value="'+esc(d.date||"")+'"></label>`,`'+dateField("f-mdate","date",(when==="by"?"By which day?":"Which day"),d.date||"",-1,2)+'`);

// 3. the Waiting card: the reward first, the calendar folded away
R(`h+='<p>Nothing to do until then. This moves to the top of your list the day before.</p>';
    h+=calBlock(t);`,`h+='<p class="h3">'+esc(putDown(p))+'</p><p>Nothing to do until then. Sorted brings this back to the top of your list when it’s due.</p>';
    h+=calBlock(t)?'<details class="calfold"'+(S.calOpen===t.id?" open":"")+'><summary>Remind me as well</summary>'+calBlock(t)+'</details>':"";`);

// 4. no complaint letters before anything has gone wrong
R(`  if(!t.promises.length&&!t.events.some(function(e){return /Nothing agreed|No reply/.test(e.label)}))return "";`,`  if(!t.promises.some(function(x){return x.status==="missed"})&&!t.events.some(function(e){return /Nothing agreed|No reply/.test(e.label)}))return "";`);

// 5. the privacy sentence says exactly what is true
R(`'<p><strong>Your cases are private.</strong> Nobody running the pilot reads them. If you send`,`'<p><strong>Your cases are private.</strong> Nobody running the pilot reads them. The pilot numbers come only from step records, which hold no case details. The person running the pilot has technical access to the database, as with any online service, and doesn’t use it to open cases. If you send`);

R(`.thread{list-style:none;margin:0;padding:0;display:flex;flex-direction:column}`,`.thread{list-style:none;margin:0;padding:0;display:flex;flex-direction:column}
fieldset.dp{border:0;padding:0;margin:0;min-width:0;display:flex;flex-direction:column;gap:6px}
fieldset.dp legend{padding:0;margin-bottom:6px;font-weight:600}
fieldset.dp .hint{font-weight:400;font-size:16px;color:var(--ink-2)}
.dp-row{display:flex;flex-wrap:wrap;gap:8px}
.dp-row select{min-height:52px;padding:10px 12px;border:2px solid var(--ink-2);border-radius:6px;background:var(--sheet);font-size:18px;flex:1 1 auto;min-width:0}
.dp-row select[data-part=m]{flex:2 1 9em}
details.calfold>summary{cursor:pointer;min-height:44px;display:flex;align-items:center;color:var(--carbon);font-weight:600;text-decoration:underline;text-underline-offset:3px}
details.calfold[open]>summary{margin-bottom:8px}`);
// the "details" fold keeps its open state across the 60-second refresh
R(`document.addEventListener("change",function(e){
  var el=e.target;if(!el||!el.getAttribute||!el.getAttribute("data-dp"))return;`,`document.addEventListener("toggle",function(e){var d=e.target;if(d&&d.classList&&d.classList.contains("calfold")){S.calOpen=d.open?S.view.id:null}},true);
document.addEventListener("change",function(e){
  var el=e.target;if(!el||!el.getAttribute||!el.getAttribute("data-dp"))return;`);
R(`anon_failed:["no-email start that failed","no-email starts that failed"]`,`anon_failed:["no-email start that failed","no-email starts that failed"],anon_slow:["no-email start that took over 10 seconds","no-email starts that took over 10 seconds"]`);

fs.writeFileSync('public/index.html',s);
const EXPECT='b799478ad188030ef08e1315c3e7a6c3230c65a3';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v22 ok',h(s),s.length);
