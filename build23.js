const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='b799478ad188030ef08e1315c3e7a6c3230c65a3')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v23: a notice that says everything, share links with a lifetime ----

// 1. the full notice: who, what, why, who else handles it, how long, your rights
R(`  '<p>Sorted is a small UK research pilot run by Baldwin Thompson-Addo. It keeps the cases you add, and your email address if you add one, stored on servers in London.</p>'+
  '<p><strong>Your cases are private.</strong> Nobody running the pilot reads them. The pilot numbers come only from step records, which hold no case details. The person running the pilot has technical access to the database, as with any online service, and doesn’t use it to open cases. If you send`,`  '<p><strong>Who runs it.</strong> Sorted is a small UK research pilot run by Baldwin Thompson-Addo, who decides how your data is used.</p>'+
  '<p><strong>What it keeps, and why.</strong> The cases you add and, if you add one, your email address, so Sorted can hold your cases and remind you. That is the service you asked for. It also keeps step records, explained below, to learn whether the pilot works.</p>'+
  '<p><strong>Your cases are private.</strong> Nobody running the pilot reads them, unless you ask for help with one or the law requires it. The pilot numbers come only from step records, which hold no case details. The person running the pilot has technical access to the database, as with any online service, and doesn’t use it to open cases otherwise. If you send`);
R(`  '<p class="muted" style="font-size:16px">Please don’t add bank details or medical information.</p></section>';
}`,`  '<p><strong>Who else handles it.</strong> Supabase stores your cases on servers in London. Vercel hosts the website. Resend sends Sorted’s emails and receives emails you forward. Vercel and Resend are US companies, so your email address, and any email you forward, may be processed in the US under their data protection terms. None of them may use your data for anything else.</p>'+
  '<p><strong>Your rights.</strong> You can copy or delete everything yourself in “Your data”. You can also ask for a copy, a correction or deletion, and you can complain to the Information Commissioner’s Office at ico.org.uk.</p>'+
  '<p class="muted" style="font-size:16px">Please don’t add bank details or medical information.</p></section>';
}`);
// the short notice before Start carries the essentials, the full one is a tap away
R(`<p>By continuing, you’re taking part in the Sorted pilot. Your cases are private: nobody running the pilot reads them. Sorted records which steps you use, without case details, and deletes idle cases after 90 days.</p><button type="button" class="link" data-a="privacy" style="text-align:left">'+(d.showPrivacy?"Hide":"Read")+' how Sorted handles your data</button>`,`<p>By continuing, you’re taking part in the Sorted pilot, a UK research pilot run by Baldwin Thompson-Addo. Sorted keeps your cases in London to hold them and remind you. Nobody running the pilot reads them. It records which steps you use, without case details. Idle cases are deleted after 90 days, or 30 if you haven’t added an email. You can copy or delete everything at any time.</p><button type="button" class="link" data-a="privacy" style="text-align:left">'+(d.showPrivacy?"Hide":"Read")+' the full notice: who else handles your data, and your rights</button>`,2);
R(`<meta name="description" content="Fix it, renew it, follow it up. One calm place`,`<meta name="description" content="They said Tuesday. Sorted remembers Tuesday. One calm place`);

// 2. share links have a lifetime, and say so
R(`<p class="muted" style="font-size:16px">They see this case only, and it updates as you do. They can’t change anything, and they don’t see your plan or the rest of your list.</p>`,`<p class="muted" style="font-size:16px">They see this case only, and it updates as you do. They can’t change anything, and they don’t see your plan or the rest of your list. The link stops working after 30 days without a change to the case, or as soon as you switch it off.</p>`);
R(`copy(url,"Link copied. Send it to them.");`,`copy(url,"Link copied. Send it to them.");if(!fresh)sb.from("shares").update({card:shareCard(t)}).eq("task_id",t.id).then(function(){},function(){});`);
R(`<p class="h3">This link doesn’t open a case.</p><p class="muted">It may have been switched off, or cut short when it was sent. Ask for it again.</p>`,`<p class="h3">This link doesn’t open a case.</p><p class="muted">It may have been switched off, gone 30 days without a change, or been cut short when it was sent. Ask for it again.</p>`);

fs.writeFileSync('public/index.html',s);
const EXPECT='af747368d541145f0b658e7746fd2a07e7b875c6';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v23 ok',h(s),s.length);
