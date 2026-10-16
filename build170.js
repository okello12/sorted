const fs=require('fs'),c=require('crypto');
const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='2ee50b8849f50ae23e99f8bcc00db86d1e7001b6')throw new Error('base mismatch '+h(s));
function R(a,b){const n=s.split(a).length-1;if(n!==1)throw new Error('match '+n+': '+a.slice(0,70));s=s.replace(a,b)}
// A choice does not prove that a calendar event was imported or a phone accepted notifications.
R('function rem149Say(t){var r=t.rem149;if(!r)return "";\n  var w={cal:"In your calendar. Your calendar app will remind you.",phone:"On this phone, if you allowed notifications.",email:"By email, once you’ve confirmed your address.",none:"No reminder. Sorted shows it on Home when it’s due, if you open Sorted."}[r.how]||"";\n  return \'<p class="muted rem149-said" style="margin:0;font-size:15px">Reminder: \'+esc(w)+\' <button class="link" data-a="rem149-change">Change</button></p>\'}',
`function rem149Say(t){var r=t.rem149;if(!r)return "";
  var st=(S.push||{}).state,w="";
  if(r.how==="cal")w="Calendar file offered. Open it and add the event to your calendar. Sorted cannot tell whether you saved it there.";
  else if(r.how==="phone")w=st==="on"?"On this phone. Notifications are on.":st==="denied"?"Not set: notifications are blocked on this phone. Allow them in your phone’s settings, then choose Change.":"Not set on this phone yet. Choose Change to try again.";
  else if(r.how==="email")w=S.user&&S.user.email&&S.emailReady&&t.emailRemind&&S.emailOff!==true?"By email. Your address is confirmed and reminders are on.":"Not set by email yet. Confirm your address and turn on email reminders, or choose Change.";
  else if(r.how==="none")w="No reminder. Sorted shows it on Home when it’s due, if you open Sorted.";
  return '<p class="muted rem149-said" style="margin:0;font-size:15px">Reminder: '+esc(w)+' <button class="link" data-a="rem149-change">Change</button></p>'}`);
R('SORTED_V="v169"','SORTED_V="v170"');
fs.writeFileSync('public/index.html',s);
const EXPECT='3ecb4ca1db0e54db26bdd29d46d89477f98a4aa3';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v170 ok',h(s),s.length);
