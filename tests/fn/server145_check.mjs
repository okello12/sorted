// v145 (audit pass 3, area C): the server functions against the page's contract, run in Node with stand-ins for Deno,
// supabase-js (sb_stub145.mjs) and fetch. Run: node --experimental-strip-types tests/fn/server145_check.mjs
// - send-reminders v15: two open promises in one case (two organisations): the reminder for the one added first is sent
//   with answer links for that promise, not cancelled as "superseded"; a closed promise's row still is.
// - inbound-email v8: the "a reply came in" email has the stop link and RFC 8058 one-click headers, and its token is
//   the one email-stop accepts; an opted-out person gets none; an HTML-only email loses head, script, style and
//   comments and has its entities decoded; an address in To and Cc is stored once; rejected mail logs at most 60 an hour.
// - email-stop v3: GET never changes anything (a valid link goes to the app's question, anything else to Settings);
//   OPTIONS answers CORS; the mail app's one-click POST and the page's POST record the opt-out with the CORS header;
//   a bad token is refused, with the CORS header; no signing secret is 503.
// - resend-events v2: unsigned requests log at most 60 an hour; a signed event is recorded.
// - originals-cleanup v3: a guest's documents move, and a move with a full listing (2000) is not marked done.
// - public/sw.js: a notification tap opens the case in a new window if the open window refuses navigate().
import { readFileSync, writeFileSync } from "node:fs";
const ok = (c, m) => { console.log((c ? "PASS " : "FAIL ") + m); if (!c) fails.push(m); }, fails = [];
const here = new URL(".", import.meta.url).pathname, root = new URL("../../", import.meta.url).pathname, gen = root + "tests/out/";  // generated copies go to tests/out (ignored)
import { mkdirSync } from "node:fs"; mkdirSync(gen, { recursive: true });
const load = async (fn, extra = {}) => {
  let src = readFileSync(root + `supabase/functions/${fn}/index.ts`, "utf8").replace(/^import "jsr:[^"]+";$/m, "").replace('from "npm:@supabase/supabase-js@2"', `from "${here}sb_stub145.mjs"`);
  for (const [a, b] of Object.entries(extra)) src = src.replace(a, b);
  const out = gen + `out145_${fn}.mts`; writeFileSync(out, src);
  let h = null; globalThis.Deno = { serve: (f) => { h = f; }, env: { get: (k) => ({ SUPABASE_URL: "https://x.supabase.co", SUPABASE_SERVICE_ROLE_KEY: "k" })[k] } };
  await import(out + "?v=" + Math.random()); return h;
};
const calls = [];
globalThis.fetch = async (url, o) => {
  calls.push({ url: String(url), o });
  if (String(url).includes("/emails/receiving/")) { const id = String(url).split("/").pop(); return new Response(JSON.stringify(globalThis.__BODIES[id] || { text: "" }), { status: 200 }); }
  if (String(url).includes("resend")) return new Response(JSON.stringify({ id: "re_" + calls.length }), { status: 200 });
  return new Response("", { status: 201 });
};
globalThis.__BODIES = {}; globalThis.__EMAILS = {};
const hmacHex = async (key, msg) => { const k = await crypto.subtle.importKey("raw", new TextEncoder().encode(key), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]); return Buffer.from(await crypto.subtle.sign("HMAC", k, new TextEncoder().encode(msg))).toString("hex").slice(0, 32); };
const past = new Date(Date.now() - 60000).toISOString(), soon = new Date(Date.now() + 2 * 86400000).toISOString(), later = new Date(Date.now() + 6 * 86400000).toISOString();
const U1 = "11111111-2222-3333-4444-555555555555";

// ---- send-reminders v15 ----
writeFileSync(gen + "out145_webpush.mts", readFileSync(root + "supabase/functions/send-reminders/webpush.ts", "utf8"));
const sr = await load("send-reminders", { 'from "./webpush.ts"': `from "${gen}out145_webpush.mts"` });
globalThis.__SECRETS = { sorted_cron_secret: "cron", resend_api_key: "rk", reminder_from: "Sorted <r@example.com>" };
globalThis.__EMAILS = { [U1]: "me@example.com" };
globalThis.__DB = {
  tasks: [{ id: "t2p", user_id: U1, data: { id: "t2p", title: "Broadband move", board: "waiting", promises: [
    { id: "pBT", status: "open", party: "BT", said: "BT said they would switch it on by Friday", dueAt: past, by: true, prec: "day" },
    { id: "pOR", status: "open", party: "Openreach", said: "Openreach said an engineer would come next week", dueAt: later, prec: "day" },
    { id: "pOld", status: "replaced", party: "BT", said: "BT said Monday", dueAt: past }] } }],
  reminders: [{ id: "r1", task_id: "t2p", user_id: U1, kind: "after", send_at: past, promise_id: "pBT" },
    { id: "r2", task_id: "t2p", user_id: U1, kind: "before", send_at: past, promise_id: "pOR" },
    { id: "r3", task_id: "t2p", user_id: U1, kind: "after", send_at: past, promise_id: "pOld" }],
  email_optouts: [], push_subs: [],
};
calls.length = 0;
await (await sr(new Request("https://x/", { headers: { "x-cron-secret": "cron" } }))).json();
const R = (id) => __DB.reminders.find((r) => r.id === id);
const mails = calls.filter((c) => c.url.includes("api.resend.com/emails")).map((c) => JSON.parse(c.o.body));
ok(R("r1").sent_at && !R("r1").cancelled_at, "the reminder for the first of two open promises is sent, not cancelled as superseded (" + (R("r1").cancel_reason || "sent") + ")");
ok(mails.some((m) => m.text.includes("&ans=yes&p=pBT") && m.text.includes("&ans=no&p=pBT")), "its answer links are for that promise");
ok(R("r2").sent_at, "the second open promise’s reminder is sent too");
ok(R("r3").cancel_reason === "superseded" && !R("r3").sent_at, "a replaced promise’s reminder is still cancelled");
ok(mails.length === 2 && mails.every((m) => !/\bBT\b|Openreach|[Bb]roadband|engineer/.test(m.text + m.html + m.subject)), "no email carries the case’s words or companies");

// ---- inbound-email v8 ----
writeFileSync(gen + "out145_readers.mjs", readFileSync(root + "supabase/functions/inbound-email/readers.mjs", "utf8"));
const ib = await load("inbound-email", { 'from "./readers.mjs"': `from "${gen}out145_readers.mjs"` });
const whsec = "whsec_" + Buffer.from("0123456789abcdef0123456789abcdef").toString("base64");
globalThis.__SECRETS = { resend_webhook_secret: whsec, inbound_domain: "in.example.uk", resend_api_key: "rk", case_replies_on: "yes", reminder_from: "Sorted <r@example.com>", sorted_cron_secret: "cron" };
async function svixPost(h, payload, secret, sigOk = true) {
  const body = JSON.stringify(payload), id = "msg_" + Math.random(), ts = String(Math.floor(Date.now() / 1000));
  const key = await crypto.subtle.importKey("raw", Buffer.from(secret.slice(6), "base64"), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const mac = Buffer.from(await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(`${id}.${ts}.${body}`))).toString("base64");
  const r = await h(new Request("https://x/", { method: "POST", body, headers: { "svix-id": id, "svix-timestamp": ts, "svix-signature": "v1," + (sigOk ? mac : "AAAA") } }));
  return { status: r.status, j: await r.json().catch(() => ({})) };
}
globalThis.__DB = { inbound_addresses: [{ user_id: U1, token: "log-0123456789abcdef" }], inbound_items: [], ops_errors: [], case_mail: [{ token: "case-abc", task_id: "t9", user_id: U1 }], email_optouts: [] };
globalThis.__BODIES = { e1: { text: "We have reviewed your complaint and we are unable to accept it. Ref ZX123456." }, e1b: { text: "We have reviewed your complaint and we are unable to accept it. Ref ZX123456." },
  e2: { html: '<html><head><title>Big Sale</title><style>p{color:red}</style><script>alert("x")</script></head><body><!--[if mso]><p>Outlook junk</p><![endif]--><p>Your refund of &#163;40 will be paid by Friday &#x2014; thanks.</p></body></html>' } };
calls.length = 0;
let r = await svixPost(ib, { type: "email.received", data: { email_id: "e1", from: "Currys <help@currys.co.uk>", to: ["case-abc@in.example.uk"], cc: [], subject: "Your complaint" } }, whsec);
const note = calls.filter((c) => c.url === "https://api.resend.com/emails").map((c) => JSON.parse(c.o.body))[0];
const tok = await hmacHex("cron", "stop:" + U1), stopUrl = `https://boxrwcuhxmimayaxzywu.supabase.co/functions/v1/email-stop?u=${U1}&t=${tok}`;
ok(r.j.stored === 1 && note && note.headers && note.headers["List-Unsubscribe"] === `<${stopUrl}>` && note.headers["List-Unsubscribe-Post"] === "List-Unsubscribe=One-Click", "the reply notice has one-click unsubscribe headers with a signed stop link (RFC 8058)");
ok(note && note.text.includes("Stop all reminder emails: " + stopUrl) && note.html.includes("Stop all reminder emails") && note.text.includes("#more-settings"), "and a visible stop link and the Settings link, worded as in the app");
ok(note && !/ZX123456|Currys|complaint/i.test(note.text + note.html), "the notice still never says which case or what the reply says");
__DB.email_optouts.push({ user_id: U1 }); __DB.inbound_items.length = 0; calls.length = 0;
r = await svixPost(ib, { type: "email.received", data: { email_id: "e1b", from: "help@currys.co.uk", to: ["case-abc@in.example.uk"], cc: [] } }, whsec);
ok(r.j.stored === 1 && !calls.some((c) => c.url === "https://api.resend.com/emails"), "after the stop, the reply is kept but no notice is sent");
__DB.inbound_items.length = 0;
r = await svixPost(ib, { type: "email.received", data: { email_id: "e2", from: "Shop <news@shop.co.uk>", to: ["log-0123456789abcdef@in.example.uk"], cc: ["LOG-0123456789ABCDEF@in.example.uk"], subject: "Refund" } }, whsec);
const kept = __DB.inbound_items[0] || {};
ok(r.j.stored === 1 && __DB.inbound_items.length === 1, "an address in both To and Cc is stored once (" + __DB.inbound_items.length + ")");
ok(kept.body && kept.body.includes("Your refund of £40 will be paid by Friday — thanks.") && !/Big Sale|alert|color:red|Outlook junk/.test(kept.body), "an HTML-only email keeps only its words, with entities decoded: " + JSON.stringify(kept.body));
__DB.ops_errors.length = 0;
for (let i = 0; i < 70; i++) await svixPost(ib, { type: "email.received", data: { email_id: "e1", to: ["x@in.example.uk"] } }, whsec, false);
ok(__DB.ops_errors.filter((e) => e.kind === "bad_signature").length === 60, "70 forged requests leave 60 log rows, not 70 (" + __DB.ops_errors.length + ")");

// ---- email-stop v3 ----
const es = await load("email-stop");
globalThis.__SECRETS = { sorted_cron_secret: "cron" }; globalThis.__DB = { email_optouts: [] };
let x = await es(new Request(stopUrl));
ok(x.status === 302 && x.headers.get("location") === `https://sorted-pilot.vercel.app/#stop=${U1}.${tok}` && __DB.email_optouts.length === 0, "opening the link (GET) changes nothing and goes to the app’s question, the token in the # part");
x = await es(new Request(`https://x/email-stop?u=${U1}&t=zz`));
ok(x.status === 302 && x.headers.get("location") === "https://sorted-pilot.vercel.app/#more-settings", "a malformed link goes to Settings");
x = await es(new Request(stopUrl, { method: "OPTIONS" }));
ok(x.status === 204 && x.headers.get("access-control-allow-origin") === "https://sorted-pilot.vercel.app" && /POST/.test(x.headers.get("access-control-allow-methods") || ""), "OPTIONS answers CORS for the site");
x = await es(new Request(stopUrl, { method: "POST", body: "List-Unsubscribe=One-Click", headers: { "content-type": "application/x-www-form-urlencoded" } }));
ok(x.status === 200 && __DB.email_optouts.some((o) => o.user_id === U1), "the mail app’s one-click POST (the token from the reply notice) stops reminder emails");
x = await es(new Request(stopUrl, { method: "POST", headers: { origin: "https://sorted-pilot.vercel.app" } }));
ok(x.status === 200 && x.headers.get("access-control-allow-origin") === "https://sorted-pilot.vercel.app" && __DB.email_optouts.length === 1, "the page’s POST works again with the CORS header, and records one opt-out");
x = await es(new Request(`https://x/email-stop?u=${U1}&t=${"0".repeat(32)}`, { method: "POST" }));
ok(x.status === 400 && x.headers.get("access-control-allow-origin") === "https://sorted-pilot.vercel.app", "a wrong token is refused, with the CORS header so the page can say so");
globalThis.__SECRETS = {};
x = await es(new Request(stopUrl, { method: "POST" }));
ok(x.status === 503, "without the signing secret nothing is accepted (503)");

// ---- resend-events v2 ----
const re = await load("resend-events");
const rsec = "whsec_" + Buffer.from("abcdefabcdefabcdefabcdefabcdefab").toString("base64");
globalThis.__SECRETS = { resend_events_secret: rsec }; globalThis.__DB = { ops_errors: [] };
for (let i = 0; i < 70; i++) await re(new Request("https://x/", { method: "POST", body: "{}" }));
ok(__DB.ops_errors.filter((e) => e.kind === "bad_signature").length === 60, "70 unsigned webhook calls leave 60 log rows (" + __DB.ops_errors.length + ")");
r = await svixPost(re, { type: "email.delivered", created_at: new Date().toISOString(), data: { email_id: "re_9", to: ["me@example.com"] } }, rsec);
ok(r.status === 200 && __DB.delivery && __DB.delivery[0].p_provider_id === "re_9" && !JSON.stringify(__DB.delivery).includes("@"), "a signed delivery event is recorded, without the address");

// ---- originals-cleanup v3 ----
const oc = await load("originals-cleanup");
const G = "99999999-8888-7777-6666-555555555555", A = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", G2 = "12121212-3434-5656-7878-909090909090";
globalThis.__SECRETS = { sorted_cron_secret: "cron" };
globalThis.__DB = { tasks: [], ops_errors: [], doc_moves: [{ id: 1, from_uid: G, to_uid: A, pairs: [["c1", "c1new"]] }, { id: 2, from_uid: G2, to_uid: A, pairs: [] }],
  objects: [{ name: `${G}/c1/1-a.pdf` }, { name: `${G}/c2/2-b.jpg` }].concat(Array.from({ length: 2001 }, (_, i) => ({ name: `${G2}/c9/${i}.jpg` }))) };
r = await (await oc(new Request("https://x/", { method: "POST", body: '{"moves_only":true}', headers: { "x-cron-secret": "cron" } }))).json();
const names = __DB.objects.map((o) => o.name);
ok(names.includes(`${A}/c1new/1-a.pdf`) && names.includes(`${A}/c2/2-b.jpg`) && __DB.doc_moves[0].done_at, "a guest’s documents move to the account, to the new case id where the page gave one, and the move is done");
ok(!__DB.doc_moves[1].done_at && names.filter((n) => n.startsWith(G2 + "/")).length === 1, "a move with more files than one listing is not marked done; the rest wait for the next run");
await oc(new Request("https://x/", { method: "POST", body: '{"moves_only":true}', headers: { "x-cron-secret": "cron" } }));
ok(__DB.doc_moves[1].done_at && !__DB.objects.some((o) => o.name.startsWith(G2 + "/")), "the next run moves the rest and marks it done");

// ---- public/sw.js ----
const swsrc = readFileSync(root + "public/sw.js", "utf8"), L = {}, opened = [];
const mkClient = (nav) => ({ url: "https://sorted-pilot.vercel.app/#start", navigate: nav });
let clientList = [];
const self = { addEventListener: (k, f) => { L[k] = f; }, location: { origin: "https://sorted-pilot.vercel.app" }, registration: {},
  clients: { matchAll: async () => clientList, openWindow: async (u) => { opened.push(u); return null; } }, skipWaiting() {} };
new Function("self", swsrc)(self);
async function tap(data, action) { let p = null; L.notificationclick({ action, notification: { data, close() {} }, waitUntil: (x) => { p = x; } }); try { await p; } catch (e) { /* the tap did nothing */ } }
clientList = [mkClient(() => Promise.reject(new TypeError("not controlled")))];
await tap({ u: "/?task=t1&src=push", a: {} });
ok(opened.length === 1 && opened[0] === "https://sorted-pilot.vercel.app/?task=t1&src=push", "a window that refuses navigate(): the case opens in a new window");
let focused = 0; clientList = [mkClient((u) => Promise.resolve({ focus() { focused++; } }))];
await tap({ u: "/?task=t1&src=push", a: { yes: "/?task=t1&src=push&ans=yes&p=p1" } }, "yes");
ok(opened.length === 1 && focused === 1, "an open window is sent to the case and focused, with no second window");

console.log("ERRORS []"); console.log("FAILS", JSON.stringify(fails));
