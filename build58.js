const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='0557086046447453912f48ad3819dbf5327476b2')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,90));s=s.split(a).join(b)}
// ---- v58: final case-detail polish after integration testing. ----

R(`return !/^(?:Tapped add to (?:Google )?Calendar|Email reminders (?:on|off)|Asked a helper|Shared with a helper|Brought across from the phone|End date not known yet|Renewing:|Started\\. Before any advice)/i.test(l);`,
  `return !/^(?:Tapped add to (?:Google )?Calendar|Email reminders (?:on|off)|Asked a helper|Shared with a helper|Brought across from the phone|End date not known yet|Renewing:|Started\\. Before any advice|Your move:|Ends .+\\. Start by )/i.test(l);`);

R(`Nothing added yet. Messages, screenshots and documents you bring into this case stay with it.`,
  `Nothing added yet. Add the useful text from a message, screenshot or document when you need it.`);

R(`var h='<details class="case56-fold case56-sharing"><summary>`,
  `var h='<details class="case56-fold case56-sharing"'+(S.view.copyText?' open':'')+'><summary>`);

R(`var r=t.renew,info=rinfo(r),rp=rphase(r),sbd=startBy(r),h='',date=r.expiry?fmtDay(dayEnd(r.expiry)):"";`,
  `var r=t.renew,info=rinfo(r),rp=rphase(r),sbd=startBy(r),h='',date=r.expiry?fmtDay(dayEnd(r.expiry)):"",rm=openMove(t),hasApplyMove=!!(rm&&/appl/i.test(String(moveAct(rm.what).done||rm.what||"")));`);
R(`h+='<div class="row eq case56-renew-actions">'+(r.applied?'':'<button class="btn" data-a="applied">I’ve applied</button>')+'<button class="btn" data-a="panel" data-p="renewed">It’s renewed</button></div>';`,
  `h+='<div class="row eq case56-renew-actions">'+(r.applied||hasApplyMove?'':'<button class="btn" data-a="applied">I’ve applied</button>')+'<button class="btn" data-a="panel" data-p="renewed">It’s renewed</button></div>';`);

fs.writeFileSync('public/index.html',s);
const EXPECT='';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v58 ok',h(s),s.length);
