const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='7e43c30fd3cba8ea479c121ac2df26fa50ff2261')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,90));s=s.split(a).join(b)}
// ---- v57: final case-detail polish after integration testing. ----

// Keep the default timeline about the case, not about Sorted's UI or information already visible above.
R(`return !/^(?:Tapped add to (?:Google )?Calendar|Email reminders (?:on|off)|Asked a helper|Shared with a helper|Brought across from the phone|End date not known yet|Renewing:|Started\\. Before any advice)/i.test(l);`,
  `return !/^(?:Tapped add to (?:Google )?Calendar|Email reminders (?:on|off)|Asked a helper|Shared with a helper|Brought across from the phone|End date not known yet|Renewing:|Started\\. Before any advice|Your move:|Ends .+\\. Start by )/i.test(l);`);

// Be precise about what is kept when screenshots/documents are read locally.
R(`Nothing added yet. Messages, screenshots and documents you bring into this case stay with it.`,
  `Nothing added yet. Add the useful text from a message, screenshot or document when you need it.`);

// If clipboard copying is blocked, reopen Sharing automatically so the manual-copy fallback is visible.
R(`var h='<details class="case56-fold case56-sharing"><summary>`,
  `var h='<details class="case56-fold case56-sharing"'+(S.view.copyText?' open':'')+'><summary>`);

// A renewal with an open "apply" move already has a primary I've applied action. Do not repeat it lower down.
R(`var r=t.renew,info=rinfo(r),rp=rphase(r),sbd=startBy(r),h='',date=r.expiry?fmtDay(dayEnd(r.expiry)):"";`,
  `var r=t.renew,info=rinfo(r),rp=rphase(r),sbd=startBy(r),h='',date=r.expiry?fmtDay(dayEnd(r.expiry)):"",rm=openMove(t),hasApplyMove=!!(rm&&/appl/i.test(String(moveAct(rm.what).done||rm.what||"")));`);
R(`h+='<div class="row eq case56-renew-actions">'+(r.applied?'':'<button class="btn" data-a="applied">I’ve applied</button>')+'<button class="btn" data-a="panel" data-p="renewed">It’s renewed</button></div>';`,
  `h+='<div class="row eq case56-renew-actions">'+(r.applied||hasApplyMove?'':'<button class="btn" data-a="applied">I’ve applied</button>')+'<button class="btn" data-a="panel" data-p="renewed">It’s renewed</button></div>';`);

fs.writeFileSync('public/index.html',s);
const EXPECT='';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v57 ok',h(s),s.length);
