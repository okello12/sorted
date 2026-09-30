const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='af747368d541145f0b658e7746fd2a07e7b875c6')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v24: the board's stop-ship list ----

// 1. rescheduling starts clean: no old wording, no date guessed from it
R(`S.draft={replaces:rp0.id,said:rp0.said,party:rp0.party||"",ref:rp0.ref||"",when:rp0.by?"by":"slot"}`,`S.draft={replaces:rp0.id,said:"",party:rp0.party||"",ref:rp0.ref||"",when:rp0.by?"by":"slot"}`);

R(`if(!said){d.err="Write what they said, in a few words.";render();return}`,`if(!said&&d.replaces){var rold=t.promises.filter(function(x){return x.id===d.replaces})[0];if(rold)said=rold.said}
    if(!said){d.err="Write what they said, in a few words.";render();return}`);
// 2. the no-email banner says where the cases really are
R(`<p><strong>Your cases are only on this phone.</strong> Add your email to keep them safe and get reminders.</p>`,`<p><strong>Without an email, only this phone can open your cases.</strong> They’re saved on Sorted’s servers, but if you clear this browser or change phone, they can’t be recovered. Add your email to keep them and get reminders.</p>`);
// 3. Done says what really happens
R(`Sorted keeps this case, so it’s here if the problem comes back.`,`Sorted keeps this case for 90 days after your last change, in case the problem comes back.`);

// 4. the pilot only takes problems with another party: renewals and to-dos go down the same path
R(`  if(/\\b(renew|renewal|expir|passport|mot\\b|visa|brp\\b|tv licen|driving licen|car tax|road tax)/.test(s))return "renew";
  if(!/\\b(refund|landlord|repair|broken|not working|money back|engineer)/.test(s)&&/\\b(deadline|due|submit|send|apply|application|bursary|form|pay|tax return|by (monday|tuesday|wednesday|thursday|friday|saturday|sunday)|tomorrow)\\b/.test(s))return "do";`,`  /* pilot scope: renewals and personal to-dos are not routed to their own modes */`);

// 5. advice, hedged where the law is not simple
R(`body:"Repairs like this are usually "+whoName(t)+"’s responsibility, unless your agreement says otherwise or the damage was caused in your home. Report it in writing if you can, so there is a record, and ask for a date."`,`body:"Repairs to heating, hot water and the building, and to appliances "+whoName(t)+" supplied, are usually their responsibility, unless your agreement says otherwise or the damage was caused in your home. Report it in writing if you can, so there is a record, and ask for a date."`);
R(`The second is a subject access request. It’s free, and they must reply within a month.`,`The second is a subject access request. It’s usually free, and they normally have a month to reply.`);

// 6. after "yes", one thing to do: finish it. Same words on the case as on Home.
R(`  }else if(S.view.panel==="call"||!t.call){
    h+=callForm(t);`,`  }else if(S.view.panel==="done"){
  }else if(S.view.panel==="call"||!t.call){
    h+=callForm(t);`);
R(`<button class="btn primary block" data-a="kept">Yes, it happened</button><button class="btn block" data-a="missed">No, it didn’t happen</button><button class="btn block" data-a="rebook">They rescheduled</button>`,`<button class="btn primary block" data-a="kept">'+esc(askFor(p)[1])+'</button><button class="btn block" data-a="missed">'+esc(askFor(p)[2])+'</button><button class="btn block" data-a="rebook">They rescheduled</button>`);
R(`+(t.baseline?'<p class="muted">Your plan before any advice: “'+esc(t.baseline)+'”</p>':'')+'</section>';`,`+'</section>';`);
R(`<section class="stack-s"><button class="btn block" data-a="summary">'+(S.view.panel==="summary"?"Hide the summary":"Summary to send a repairer")+'</button>`,`<section class="stack-s"><button class="link" data-a="summary" style="align-self:flex-start">'+(S.view.panel==="summary"?"Hide the summary":"Copy a summary for whoever fixes it")+'</button>`);

// 7. sharing: only say "copied" once the link exists; only say "off" once it is off
R(`copy(url,"Link copied. Send it to them.");if(!fresh)sb.from("shares").update({card:shareCard(t)}).eq("task_id",t.id).then(function(){},function(){});`,`if(!fresh){copy(url,"Link copied. Send it to them.");sb.from("shares").update({card:shareCard(t)}).eq("task_id",t.id).then(function(){},function(){})}`);
R(`if(fresh){log(t,"Shared with a helper.");save();
        sb.from("shares").insert({token:t.shareToken,task_id:t.id,card:shareCard(t)}).then(function(r){if(r.error){toast("Couldn’t create the link. Try again.");delete t.shareToken;t._dirty=true;save();render()}})}`,`if(fresh){save();
        sb.from("shares").insert({token:t.shareToken,task_id:t.id,card:shareCard(t)}).then(function(r){if(r.error){toast("Couldn’t create the link. Try again.");delete t.shareToken;t._dirty=true;save();render()}else{log(t,"Shared with a helper.");save();copy(url,"Link copied. Send it to them.");render()}},function(){toast("Couldn’t create the link. Check your connection.");delete t.shareToken;t._dirty=true;save();render()})}`);
R(`case "unshare":if(t&&t.shareToken){sb.from("shares").delete().eq("task_id",t.id).then(function(){});delete t.shareToken;log(t,"Stopped sharing. The old link no longer works.");commit();toast("Link switched off")}break;`,`case "unshare":if(t&&t.shareToken){var ust=t;sb.from("shares").delete().eq("task_id",ust.id).then(function(r){if(r&&r.error){toast("Couldn’t switch the link off. Try again.");return}delete ust.shareToken;log(ust,"Stopped sharing. The old link no longer works.");commit();toast("Link switched off")},function(){toast("Couldn’t switch the link off. Check your connection.")})}break;`);
// 8. signing out leaves no case text behind on a shared device
R(`case "signout":sb.auth.signOut().finally(function(){S.user=null;S.tasks=[];go({name:"home"})});break;`,`case "signout":try{localStorage.removeItem(cacheKey());localStorage.removeItem("sorted.evq")}catch(e){}sb.auth.signOut().finally(function(){S.user=null;S.tasks=[];go({name:"home"})});break;`);

// 9. screen readers: announce toasts; keep focus somewhere sensible after every re-render
R(`<div id="toast" class="toast" hidden></div>`,`<div id="toast" class="toast" role="status" aria-live="polite" hidden></div>`);
R(`function go(view){if(view.name!=="home")S.composeOpen=false;S.view=view;S.draft={};render();window.scrollTo(0,0)}`,`function go(view){if(view.name!=="home")S.composeOpen=false;S.view=view;S.draft={};render();window.scrollTo(0,0);focusMain()}
function focusMain(){var h=document.querySelector("#app main h1, #app main h2, #app main .h2");if(h){if(!h.hasAttribute("tabindex"))h.setAttribute("tabindex","-1");try{h.focus({preventScroll:true})}catch(e){}}}`);
R(`    case "resend":S.draft.sent=false;render();break;
  }
});`,`    case "resend":S.draft.sent=false;render();break;
  }
  /* after a re-render, put focus back on the same control if it still exists, otherwise on the page heading */
  if(!document.activeElement||document.activeElement===document.body){
    var sel='[data-a="'+a+'"]'+(b.getAttribute("data-id")?'[data-id="'+b.getAttribute("data-id")+'"]':'')+(b.getAttribute("data-v")?'[data-v="'+b.getAttribute("data-v")+'"]':'');
    var back=null;try{back=document.querySelector(sel)}catch(e){}
    if(back&&back.offsetParent!==null)back.focus();else focusMain();
  }
});`);
R(`  $("#app").innerHTML=html;
}`,`  var app=$("#app"),ae=document.activeElement,inApp=!!(ae&&ae!==document.body&&app.contains(ae)),key=null;
  if(inApp){if(ae.id)key="#"+ae.id;else if(ae.getAttribute("data-a"))key='[data-a="'+ae.getAttribute("data-a")+'"]'+(ae.getAttribute("data-id")?'[data-id="'+ae.getAttribute("data-id")+'"]':'')+(ae.getAttribute("data-v")?'[data-v="'+ae.getAttribute("data-v")+'"]':'')}
  app.innerHTML=html;
  if(inApp){var back=null;try{back=key&&document.querySelector(key)}catch(e){}if(back&&back.offsetParent!==null){try{back.focus({preventScroll:true})}catch(e){}}else focusMain()}
}`);
// 10. touch targets
R(`<button class="link" data-a="example" style="display:inline;min-height:0;padding:0">`,`<button class="link" data-a="example" style="display:inline-block;padding:10px 0">`);
R(`.thread{list-style:none;margin:0;padding:0;display:flex;flex-direction:column}`,`.thread{list-style:none;margin:0;padding:0;display:flex;flex-direction:column}
.foot a.link,p a.link{display:inline-block;min-height:44px;padding:10px 0}
[tabindex="-1"]:focus{outline:none}`);

fs.writeFileSync('public/index.html',s);
const EXPECT='ea0646fd54b65d0a5809192e4ea92d3bc8f6d496';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v24 ok',h(s),s.length);
