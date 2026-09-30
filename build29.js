const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='aa22748e3d1c0e783be315c653e9b4500bd14e58')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v29: send the helper link on WhatsApp ----
// once the link exists (never while it is still being created), offer WhatsApp as a real link, so phones open the app directly.
// The message carries the link only: no case title or details go to WhatsApp.
R(`  h+='<button class="btn block" data-a="share">'+(t.shareToken?"Copy the helper link again":"Copy a link for someone helping you")+'</button>';`,`  h+='<button class="btn block" data-a="share">'+(t.shareToken?"Copy the helper link again":"Copy a link for someone helping you")+'</button>';
  if(t.shareToken&&S.shareBusy!==t.id){var waMsg="I’m keeping track of a problem on Sorted. This link shows you where it’s up to: "+location.origin+"/?share="+t.shareToken;
    h+='<a class="btn block wa" data-a="wa-share" href="https://wa.me/?text='+encodeURIComponent(waMsg)+'" target="_blank" rel="noopener">Send the link on WhatsApp</a>'}`);
// the WhatsApp send counts as using the link: refresh what the helper sees and restart its 30 days
R(`    case "unshare":if(t&&t.shareToken){`,`    case "wa-share":if(t&&t.shareToken){sb.from("shares").update({card:shareCard(t)}).eq("task_id",t.id).then(function(){},function(){});if(!t.events.some(function(e){return /^Sent the helper link on WhatsApp/.test(e.label)})){log(t,"Sent the helper link on WhatsApp.");commit()}}break;
    case "unshare":if(t&&t.shareToken){`);
// mark the link as not ready while it is being created
R(`      if(fresh){save();
        sb.from("shares").insert(`,`      if(fresh){save();S.shareBusy=t.id;
        sb.from("shares").insert(`);
R(`.then(function(r){if(r.error){toast("Couldn’t create the link. Try again.");delete t.shareToken;`,`.then(function(r){S.shareBusy=null;if(r.error){toast("Couldn’t create the link. Try again.");delete t.shareToken;`);
R(`render()}},function(){toast("Couldn’t create the link. Check your connection.");delete t.shareToken;`,`render()}},function(){S.shareBusy=null;toast("Couldn’t create the link. Check your connection.");delete t.shareToken;`);
R(`a.btn.primary{color:var(--carbon-ink)}`,`a.btn.primary{color:var(--carbon-ink)}
a.btn.wa{border-color:#1F7A4D;color:#1F7A4D}
:root[data-theme="dark"] a.btn.wa{border-color:#5FD39A;color:#5FD39A}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) a.btn.wa{border-color:#5FD39A;color:#5FD39A}}`);
fs.writeFileSync('public/index.html',s);
const EXPECT='dc9fe39ac92ae705c4d1dbaed1b31ab4c3a6747f';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v29 ok',h(s),s.length);
