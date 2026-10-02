const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='c454196b36a6cba8a9651b6fb123c365adfa118a')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+String(a).slice(0,90));s=s.split(a).join(b)}
// v86: the assistant backend can use different AI providers, so the product copy must not promise Claude/Anthropic specifically.
R('When you tap it, Sorted sends this case’s details to Anthropic, the company that makes the AI model Claude, so it can write an answer. Nothing is sent until you tap. Anthropic doesn’t use it to train its models. The answer can be wrong, and it isn’t legal advice.',
  'When you tap it, Sorted sends this case’s details to the AI provider configured for the pilot so it can write an answer. Nothing is sent until you tap. Check the provider’s privacy terms. The answer can be wrong, and it isn’t legal advice.');
R('This sends the case and your draft to Anthropic’s AI. Nothing is sent until you tap.',
  'This sends the case and your draft to the AI provider configured for the pilot. Nothing is sent until you tap.');
R('<p><strong>Who else handles it.</strong> Supabase stores your cases on servers in London. Vercel hosts the website. Resend sends Sorted’s emails. Anthropic runs Sorted’s assistant. All four are US companies, so your data may be processed in the US under their data protection terms, and none of them may use it for anything else.</p>',
  '<p><strong>Who else handles it.</strong> Supabase stores your cases on servers in London. Vercel hosts the website. Resend sends Sorted’s emails. When you choose to use Sorted’s assistant, the AI provider configured for the pilot processes that one case to write the answer. Each supplier processes data under its own commercial data protection terms.</p>');
R('<p><strong>Sorted’s assistant.</strong> If you tap one of the assistant’s buttons, such as “Explain this” or “Ask about this case”, Sorted sends that case’s details to Anthropic so its AI model, Claude, can write an answer. Nothing is sent until you tap. Anthropic doesn’t use it to train its models, and keeps it only as its commercial terms allow. Sorted doesn’t keep the answer unless you put it in your case. To limit use, Sorted counts how often each account uses the assistant each day, and deletes the counts after 30 days.</p>',
  '<p><strong>Sorted’s assistant.</strong> If you tap one of the assistant’s buttons, such as “Explain this”, “Help me resolve this” or “Ask about this case”, Sorted sends that case’s details to the AI provider configured for the pilot so it can write an answer. Nothing is sent until you tap. Sorted doesn’t keep the answer unless you put it in your case. To limit use, Sorted counts how often each account uses the assistant each day, and deletes the counts after 30 days. The provider’s own commercial API privacy and retention terms also apply.</p>');
fs.writeFileSync('public/index.html',s);
const EXPECT='0000000000000000000000000000000000000000';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v86 ok',h(s),s.length);
