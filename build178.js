const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='3bda7b0fb947322ed24df4d02d9b572cf5ada4ca')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,70));s=s.split(a).join(b)}
// ---- v178: a parcel that hasn't come, and a chase you send yourself (agreed with Baldwin on 9 November 2026).
// 1. A parcel playbook in the PB registry, before refunds: "marked delivered, not received", "tracking stopped" and
//    "not arrived". Their claim ("delivered") and the person's account ("not received") are kept apart in t.pcl178 and
//    shown apart in What Sorted understood. The case stays open until the person says how it ended (got the parcel,
//    refunded, a replacement coming, not sorted yet). One line of honest advice: the seller is usually responsible until
//    it reaches you (Citizens Advice, checked 9 November 2026). No tracking supplier, nothing sent by Sorted.
// 2. The chase (every case): an optional "Their email address" for an email; "Before you send" says who it goes to,
//    the subject, that only the message is shared and that the person sends it themselves; the Cc line no longer
//    promises the reply comes back ("If they reply to all…, if they reply only to you, add it here yourself").
//    After opening or copying, "Have you sent it?" with "I’ve sent it" (a history line and a follow-up reminder) and
//    "Not yet". Sorted never says it was sent unless the person does.
// 3. Usage records that keep the steps apart (migration 31, step names only): chase_prepared, chase_opened (email app
//    or copy), chase_sent_said, message_added (pasted or from the case address, and whether after a sent chase).
const CODE=String.raw`/* v178: parcels, and a chase you send yourself */
var PCL178_ON=/\b(?:parcels?|packages?|deliver(?:y|ies|ed)|couriers?|tracking|evri|hermes|dpd|yodel|royal mail|parcelforce|dhl|ups|fedex|inpost|amazon logistics)\b/i;
var PCL178_MONEY=/\b(?:refund|money back|reimburs)/i;
var PCL178_NOTRECV=/\b(?:haven[’']?t|have not|hasn[’']?t|has not|didn[’']?t|did not|never|not)\s+(?:yet\s+|actually\s+|even\s+)?(?:received|got|gotten|get|arrived|come|turned up|shown up|been received)\b|\bnot (?:here|arrived|received)\b|\bno sign of (?:it|them)\b|\bnowhere to be (?:seen|found)\b|\b(?:it|parcel|package|order)(?:’s|'s| is| has gone)? missing\b/i;
var PCL178_UNDEL=/\b(?:not|never|wasn[’']?t|hasn[’']?t been|isn[’']?t|won[’']?t be|will be|to be|be|being|un)\s*delivered\b/gi;
var PCL178_STUCK=/\btracking\b[^.!?\n]{0,40}\b(?:hasn[’']?t|has not|not|stopped|no longer|isn[’']?t)\b[^.!?\n]{0,25}?\b(?:updat\w*|mov\w*|chang\w*)|\btracking\b[^.!?\n]{0,30}\bstuck\b|\bstuck (?:at|in) (?:the |a )?(?:depot|hub|sorting|warehouse|customs)\b|\bno (?:tracking )?updates?\b/i;
var PCL178_CA="https://www.citizensadvice.org.uk/consumer/somethings-gone-wrong-with-a-purchase/if-something-you-ordered-hasnt-been-delivered/",PCL178_CHECKED="9 November 2026";
var EM178=/^[^\s@?&#,;<>"'()]+@[^\s@?&#,;<>"'()]+\.[^\s@?&#,;<>"'()]+$/;
function pcl178Text(t){return [t.title||"",t.said||""].join(" ")}
function pcl178Read(x){x=String(x||"");if(!PCL178_ON.test(x))return null;
  if(/\bdelivered\b/i.test(x.replace(PCL178_UNDEL," "))&&PCL178_NOTRECV.test(x))return "delivered";
  if(PCL178_STUCK.test(x))return "stuck";
  if(PCL178_NOTRECV.test(x))return "late";return null}
function pcl178Is(t){if(!t||t.example||t.mode!=="call"||pkOn(t))return false;var x=pcl178Text(t);return PCL178_ON.test(x)&&!PCL178_MONEY.test(x)&&!(t.facts&&t.facts.kind==="money")}
function pcl178Set(t,k,v){t.pcl178=t.pcl178||{};t.pcl178[k]=v;t.pcl178.at2=nowIso()}
function pcl178Rights(){return ' If you bought it online, the seller is usually responsible until it reaches you, unless you agreed it could be left somewhere, so it’s usually best to contact the seller rather than the courier. <a href="'+PCL178_CA+'" target="_blank" rel="noopener">Citizens Advice explains this<span class="sr-only"> (opens a new tab)</span></a>.'}
var PCL178_ACTS=[{l:"Get the message ready",a:"panel",p:"call",primary:true},{l:"It’s turned up",go:"received",log:"You said the parcel has arrived."},{l:"They’ve said what they’ll do",a:"move-reply"}];
PB.splice(PB.map(function(x){return x.id}).indexOf("refund"),0,{id:"parcel",name:"Parcel",start:"waiting",
  first:function(t){var k=pcl178Read(pcl178Text(t));if(!k)return null;t.pcl178={claim:k,recv:"no",src:"your words",at:nowIso()};return k},
  on:pcl178Is,
  events:{kept:function(){return "outcome"},partly:function(){return null},missed:function(t,p,s){s.misses=(s.misses||0)+1;return "late"}},
  stages:{
    waiting:{label:"Waiting for the parcel"},
    delivered:{label:"Marked delivered, not received",head:function(){return "They say it was delivered. You haven’t got it."},
      body:function(){return "Sorted keeps the two apart: their tracking or message says delivered, and you say it hasn’t reached you. Sorted hasn’t checked either."+pcl178Rights()},html:true,acts:PCL178_ACTS},
    stuck:{label:"Tracking stopped",head:function(){return "The tracking has stopped and it hasn’t arrived"},
      body:function(){return "Sorted can’t see the tracking. Ask where it is and by when it will arrive. When they give a date, add it and Sorted brings it back when it’s due."+pcl178Rights()},html:true,acts:PCL178_ACTS},
    late:{label:"Not arrived",head:function(t,s){return s.misses>1?"It still hasn’t come, after "+s.misses+" dates":"It hasn’t arrived"},
      body:function(){return "Ask where it is and by when it will arrive, or whether they’ll replace it or refund you. When they give a date, add it and Sorted brings it back when it’s due."+pcl178Rights()},html:true,acts:PCL178_ACTS},
    outcome:{label:"How it ended",head:function(){return "How did it end?"},
      body:function(){return "Sorted keeps this case open until you say what actually happened."},
      acts:[{l:"I’ve got the parcel",go:"received",primary:true,log:"You said the parcel has arrived."},{l:"They’ve refunded me",go:"refunded",log:"You said they refunded you."},{l:"They’re sending a replacement",a:"move-reply"},{l:"It isn’t sorted yet",go:"late",log:"You said it still isn’t sorted."}]},
    received:{label:"Received",enter:function(t,s){pcl178Set(t,"recv","yes");S.view.panel="done";S.draft={outcome:"Received."}}},
    refunded:{label:"Refunded",enter:function(t,s){S.view.panel="done";S.draft={outcome:"Refunded."}}}
  }});
var _pbCard178=pbCard;pbCard=function(t){var s=t&&t.pb;if(s&&s.id==="parcel"&&t.call&&t.call.at&&(!s.at||t.call.at>=s.at)&&["delivered","stuck","late"].indexOf(s.stage)>=0)return "";return _pbCard178(t)};
var _uRows178=uRows;uRows=function(t){var r=_uRows178(t),c=t.pcl178;if(!c||!c.claim||!pcl178Is(t))return r;var add=[];
  if(c.claim==="delivered")add.push(["What they say","Delivered (their tracking or message, as you described it; Sorted hasn’t checked it)"]);
  else if(c.claim==="stuck")add.push(["What the tracking shows","It has stopped updating (as you described it)"]);
  add.push(["What you’ve received",c.recv==="yes"?"The parcel (you said it arrived)":"Nothing yet (your words)"]);
  r.splice.apply(r,[1,0].concat(add));return r};
var _hr178=haveReady;haveReady=function(t){var o=_hr178(t);if(!pcl178Is(t))return o;
  if(!refOf(t))o.push("Your order number or tracking number, if you have it");
  o.push("Any delivery photo or note they sent, if there is one");return o};
var _cd178=callDefaults;callDefaults=function(t,kind){var r=_cd178(t,kind);if(recentMiss(t)||!pcl178Is(t))return r;var k=(t.pcl178&&t.pcl178.claim)||pcl178Read(pcl178Text(t));if(!k)return r;
  var rf=refOf(t),o="my order"+(rf?" (reference "+rf+")":"");
  var ask=k==="delivered"?"Hi, "+o+" is marked as delivered, but I haven’t received it. Please find out what happened and tell me by when you will redeliver it, replace it or refund me.":k==="stuck"?"Hi, the tracking for "+o+" has stopped updating and it hasn’t arrived. Please find out where it is and tell me by when it will arrive.":"Hi, "+o+" hasn’t arrived. Please tell me where it is and by when it will arrive, or whether you will replace it or refund me.";
  return {who:r.who,ask:ask+refsSay(t)}};
function pcl178Lead(t){var s=t&&t.pb;return !!(s&&s.id==="parcel"&&["delivered","stuck","late"].indexOf(s.stage)>=0&&pcl178Is(t)&&!openPromise(t))}
var _an178=att152Next;att152Next=function(f){var t=f.t;if(t&&pcl178Lead(t)&&!f.m)return !t.call?"Next: ask the seller what they’ll do":t.call.sentAt?"Next: wait for their reply, then add it here":t.call.via==="phone"?"Next: make the call, then log what they say":"Next: send the message, then say you’ve sent it";if(t&&t.pb&&t.pb.id==="parcel"&&t.pb.stage==="outcome"&&!f.p&&t.board!=="done"&&pcl178Is(t))return "Next: say how it ended";return _an178(f)};ATT152.next=att152Next;
var _appCue178=appCue;appCue=function(t){return pcl178Lead(t)?false:_appCue178(t)};
var _turnAsk178=turnAsk;turnAsk=function(t){return pcl178Lead(t)?false:_turnAsk178(t)};
var _frCard178=frCard;frCard=function(t){var h=_frCard178.apply(this,arguments);if(h&&pcl178Lead(t))h=h.replace(/(<h3 class="h3">What to do next<\/h3><p>)[^<]*(<\/p>)/,"$1Ask the seller where it is and what they’ll do about it. “Get the message ready” writes it for you to send.$2");return h};
function via178Shown(){var b=document.querySelector('form[data-f=call] [data-k=via][aria-pressed=true]');return b?b.getAttribute("data-v")||"":""}
function to178Field(t,d){var v=d.to!==undefined?d.to:((t.call&&t.call.to)||"");return '<label class="f">Their email address<span class="hint">Optional. Use the address on their official website or your account. Leave it empty to choose it in your email app.</span><input type="text" id="f-to" name="to" autocomplete="off" inputmode="email" autocapitalize="off" spellcheck="false" value="'+esc(v)+'"></label>'}
document.addEventListener("input",function(e){var x=e.target;if(x&&x.id==="f-to"&&S&&S.draft)S.draft.to=x.value});
function rev178(t,c,subj,ra){var h='<div class="rev178 stack-s"><p style="font-weight:600;margin:0">Before you send</p><dl class="u117"><div><dt>To</dt><dd>'+(c.to?esc(c.to):'You’ll choose the address in your email app')+'</dd></div><div><dt>Subject</dt><dd>'+esc(subj)+'</dd></div>'+(ra?'<div><dt>Cc</dt><dd>This case’s own Sorted address</dd></div>':'')+'<div><dt>What it shares</dt><dd>Only the message above. Nothing else from your case goes with it.</dd></div></dl><p class="muted case56-small" style="margin:0">You send it from your own email. Sorted doesn’t send it for you and can’t see whether it was sent.</p>';
  if(ra)h+='<p class="muted case56-small" style="margin:0">If they reply to all, their reply appears in this case. If they reply only to you, add it here yourself.</p>';
  return h+'</div>'}
function sent178(t,c){if(c.via==="phone")return "";
  if(c.sentAt)return '<div class="note stack-s sent178"><p style="margin:0"><strong>You said you sent it on '+esc(fmtDay(new Date(c.sentAt)))+'.</strong> When they reply, add it here and Sorted will suggest what changes.</p><button class="btn block" data-a="panel" data-p="paste">Add their reply</button></div>';
  return '<div class="note stack-s sent178"><p style="margin:0"><strong>Have you sent it?</strong> Sorted can’t see your email or their app, so it only knows if you say.</p><div class="row eq"><button class="btn'+(c.openedAt?' primary':'')+'" data-a="chase-sent178">I’ve sent it</button>'+(c.openedAt?'<button class="btn" data-a="chase-notyet178">Not yet</button>':'')+'</div></div>'}
`;
R('function boot(){',CODE+'function boot(){');
R('if(pb98&&pb98.first)t.pb={id:pb98.id,stage:pb98.first,at:nowIso()};',
  'var pbf178=pb98&&pb98.first?(typeof pb98.first==="function"?pb98.first(t):pb98.first):null;if(pbf178)t.pb={id:pb98.id,stage:pbf178,at:nowIso()};');
// the call form: a parcel defaults to email, says who to contact, and an email can name its recipient
R('t.facts.benefit==="Universal Credit"?"account":"phone"))','t.facts.benefit==="Universal Credit"?"account":pcl178Is(t)&&!t.call?"email":"phone"))');
R(`placeholder="The company, landlord or office"></label>';`,`placeholder="The company, landlord or office"></label>';if(pcl178Is(t)&&!m)h+='<p class="hint" style="margin:-6px 0 0">If you bought it online, it’s usually best to contact the seller rather than the courier.</p>';`);
// the form shows a default "How" (email for a parcel, the account for Universal Credit) but the submit only knew a
// tapped chip and fell back to phone; it now saves the choice shown as pressed
R('via=d.via||(t.call&&t.call.via)||"phone";','via=d.via||via178Shown()||(t.call&&t.call.via)||"phone";');
R('h+=checkPanel(via);','if(via==="email")h+=to178Field(t,d);h+=checkPanel(via);');
R('t.call={who:who,ask:ask,via:via,at:nowIso()};',
  'var to178=via==="email"&&$("#f-to")?$("#f-to").value.trim():"";if(to178&&!EM178.test(to178)){d.err="That doesn’t look like an email address. Check it, or leave it empty and choose the address in your email app.";render();return}\n    t.call={who:who,ask:ask,via:via,at:nowIso()};if(to178)t.call.to=to178;track("chase_prepared",t,{via:via,pb:(t.pb&&t.pb.id)||null,after_miss:chasing});');
// the email: who it goes to, what it shares, honest about Cc
R(`return (ra?'<p class="muted case56-small" style="margin:0">Sorted adds this case’s own address in Cc, so their reply comes back to this case.</p>':'')+'<div class="row eq"><a class="btn" data-a="mail-open" href="mailto:?'`,
  `return rev178(t,c,subj,ra)+'<div class="row eq"><a class="btn" data-a="mail-open" href="mailto:'+(c.to?esc(c.to):'')+'?'`);
R(`+sendRow(t,c)+'</div>'`,`+sendRow(t,c)+sent178(t,c)+'</div>'`);
R('case "mail-open":if(t){log(t,"Opened the message in your email app.");commit()}break;',
  'case "mail-open":if(t){log(t,"Opened the message in your email app.");if(t.call){t.call.openedAt=nowIso();track("chase_opened",t,{via:"email"})}commit()}break;\n'+
  '    case "chase-sent178":if(t&&t.call&&!t.call.sentAt){var cw178=t.call.who||"them";t.call.sentAt=nowIso();log(t,"You said you sent the "+(t.call.via==="email"?"email":t.call.via==="letter"?"letter":"message")+" to "+cw178+".");track("chase_sent_said",t,{via:t.call.via});S.view.panel="move";S.draft={mwhat:"Check for a reply from "+cw178,when:"by",date:followDate(),followUp:true};commit();window.scrollTo(0,0);toast("Noted. Save a reminder in case they don’t reply, or cancel.")}break;\n'+
  '    case "chase-notyet178":if(t&&t.call){delete t.call.openedAt;t._dirty=true;commit()}break;');
R('log(t,"Copied the message.");save()}break;','log(t,"Copied the message.");t.call.openedAt=nowIso();track("chase_opened",t,{via:"copy"});commit()}break;');
R('if(d.kept!==ptx){evidence(t,ptx,d.src||(S.view.pasteOwn?"your own words":""));d.kept=ptx}',
  'if(d.kept!==ptx){evidence(t,ptx,d.src||(S.view.pasteOwn?"your own words":""));d.kept=ptx;track("message_added",t,{after_chase:!!(t.call&&t.call.sentAt),via:S.view.pasteOwn?"own":"paste"})}');
R('if(!cmx)break;var cmt=','if(!cmx)break;track("message_added",t,{after_chase:!!(t.call&&t.call.sentAt),via:"case_address"});var cmt=');
R('"recap_copied","second_case_started"];','"recap_copied","second_case_started","chase_prepared","chase_opened","chase_sent_said","message_added"];');
R('SORTED_V="v177"','SORTED_V="v178"');
fs.writeFileSync('public/index.html',s);
const EXPECT='c8f303df258a6596d544c68c4cf7ee3b31dbba3e';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v178 ok',h(s),s.length);
