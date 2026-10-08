// Runs supabase/functions/send-reminders/index.ts in Node with stand-ins for Deno, supabase-js and fetch, and checks
// v133: a guest with a phone gets a push and no email; the push decrypts to fixed words, the case link and the answer
// buttons, never the case's words; an email user gets both, and the "after" email offers Later and New date; a phone
// the push service has forgotten (410) is removed; no channel cancels the reminder.
// Run: node --experimental-strip-types tests/fn/send_reminders_check.mjs
import { readFileSync, writeFileSync } from "node:fs";
const ok = (c, m) => { console.log((c ? "PASS " : "FAIL ") + m); if (!c) fails.push(m); }, fails = [];
const here = new URL(".", import.meta.url).pathname, root = new URL("../../", import.meta.url).pathname;
// Node strips the TypeScript types itself (--experimental-strip-types); only the import paths are pointed at stand-ins.
const src = readFileSync(root + "supabase/functions/send-reminders/index.ts", "utf8")
  .replace(/^import "jsr:[^"]+";$/m, "")
  .replace('from "npm:@supabase/supabase-js@2"', 'from "./sb_stub.mjs"')
  .replace('from "./webpush.ts"', 'from "./out_webpush.mts"');
writeFileSync(here + "out_sr.mts", src);
writeFileSync(here + "out_webpush.mts", readFileSync(root + "supabase/functions/send-reminders/webpush.ts", "utf8"));
const subtle = globalThis.crypto.subtle;
const b64u = (b) => Buffer.from(b).toString("base64url"), unb = (s) => new Uint8Array(Buffer.from(s, "base64url"));
// The phone's own keys, to decrypt what arrives (RFC 8291, receiver side).
const ua = await subtle.generateKey({ name: "ECDH", namedCurve: "P-256" }, true, ["deriveBits"]);
const uaPub = new Uint8Array(await subtle.exportKey("raw", ua.publicKey)), authS = crypto.getRandomValues(new Uint8Array(16));
const hmac = async (k, d) => new Uint8Array(await subtle.sign("HMAC", await subtle.importKey("raw", k, { name: "HMAC", hash: "SHA-256" }, false, ["sign"]), d));
const cat = (...a) => { const o = new Uint8Array(a.reduce((n, x) => n + x.length, 0)); let i = 0; for (const x of a) { o.set(x, i); i += x.length; } return o; };
const te = new TextEncoder();
async function decrypt(body) {
  const salt = body.slice(0, 16), idlen = body[20], asPub = body.slice(21, 21 + idlen), ct = body.slice(21 + idlen);
  const ecdh = new Uint8Array(await subtle.deriveBits({ name: "ECDH", public: await subtle.importKey("raw", asPub, { name: "ECDH", namedCurve: "P-256" }, false, []) }, ua.privateKey, 256));
  const ikm = await hmac(await hmac(authS, ecdh), cat(te.encode("WebPush: info\0"), uaPub, asPub, new Uint8Array([1])));
  const prk = await hmac(salt, ikm);
  const cek = (await hmac(prk, cat(te.encode("Content-Encoding: aes128gcm\0"), new Uint8Array([1])))).slice(0, 16);
  const nonce = (await hmac(prk, cat(te.encode("Content-Encoding: nonce\0"), new Uint8Array([1])))).slice(0, 12);
  const pt = new Uint8Array(await subtle.decrypt({ name: "AES-GCM", iv: nonce }, await subtle.importKey("raw", cek, { name: "AES-GCM" }, false, ["decrypt"]), ct));
  return JSON.parse(new TextDecoder().decode(pt.slice(0, pt.lastIndexOf(2))));
}
const vk = await subtle.generateKey({ name: "ECDSA", namedCurve: "P-256" }, true, ["sign"]);
const vj = await subtle.exportKey("jwk", vk.privateKey);
let handler = null;
globalThis.Deno = { serve: (h) => { handler = h; }, env: { get: (k) => ({ SUPABASE_URL: "https://x.supabase.co", SUPABASE_SERVICE_ROLE_KEY: "k" })[k] } };
const calls = [];
globalThis.fetch = async (url, o) => { calls.push({ url: String(url), o }); if (String(url).includes("resend")) return new Response(JSON.stringify({ id: "re_1" }), { status: 200 }); if (String(url).includes("/gone")) return new Response("", { status: 410 }); return new Response("", { status: 201 }); };
await import(here + "out_sr.mts");
const past = new Date(Date.now() - 60000).toISOString();
const task = (id, user, words) => ({ id, user_id: user, data: { id, title: words, board: "waiting", emailRemind: undefined, promises: [{ id: "p1", status: "open", said: words, party: "Currys" }] } });
function fresh() {
  globalThis.__SECRETS = { sorted_cron_secret: "cron", resend_api_key: "rk", reminder_from: "Sorted <r@example.com>", vapid_private_jwk: JSON.stringify(vj) };
  globalThis.__EMAILS = { "u-mail": "me@example.com" };
  globalThis.__DB = {
    reminders: [{ id: "r1", task_id: "t1", user_id: "u-guest", kind: "after", send_at: past, promise_id: "p1" },
      { id: "r2", task_id: "t2", user_id: "u-mail", kind: "after", send_at: past, promise_id: "p1" },
      { id: "r3", task_id: "t3", user_id: "u-none", kind: "before", send_at: past, promise_id: "p1" }],
    tasks: [task("t1", "u-guest", "Refund of 89 pounds order 445566"), task("t2", "u-mail", "Refund of 20 pounds"), task("t3", "u-none", "Something private")],
    push_subs: [{ id: "s1", user_id: "u-guest", endpoint: "https://fcm.googleapis.com/fcm/send/abc", p256dh: b64u(uaPub), auth: b64u(authS), fails: 0 },
      { id: "s2", user_id: "u-mail", endpoint: "https://fcm.googleapis.com/fcm/send/gone", p256dh: b64u(uaPub), auth: b64u(authS), fails: 0 }],
    email_optouts: [],
  };
  calls.length = 0;
}
fresh();
const res = await (await handler(new Request("https://x/", { headers: { "x-cron-secret": "cron" } }))).json();
const push1 = calls.filter((c) => c.url.includes("/fcm/send/abc"));
ok(push1.length === 1 && push1[0].o.headers["Content-Encoding"] === "aes128gcm" && /^vapid t=.+, k=/.test(push1[0].o.headers.Authorization), "the guest’s phone gets one encrypted push with a VAPID signature");
const m = await decrypt(new Uint8Array(push1[0].o.body));
ok(m.u === "/?task=t1&src=push" && m.b === "Did it happen? Tap to answer." && m.a.yes === "/?task=t1&src=push&ans=yes&p=p1" && m.a.no.endsWith("&ans=no&p=p1") && m.x.length === 2, "it decrypts to fixed words, the case link and the two answers");
ok(!JSON.stringify(m).match(/89|445566|Currys|Refund/), "the push never carries the case’s words, reference or company");
const r1 = __DB.reminders.find((r) => r.id === "r1"), r2 = __DB.reminders.find((r) => r.id === "r2"), r3 = __DB.reminders.find((r) => r.id === "r3");
ok(r1.sent_at && r1.push_sent_at && r1.push_detail === "1 of 1" && !calls.some((c) => c.url.includes("resend") && JSON.parse(c.o.body).to[0] === undefined), "the guest’s reminder is marked sent by push, with no email");
const mail = calls.filter((c) => c.url.includes("resend"));
ok(mail.length === 1 && JSON.parse(mail[0].o.body).to[0] === "me@example.com" && r2.sent_at && r2.provider_id === "re_1", "the email user still gets the email");
const body = JSON.parse(mail[0].o.body);
ok(body.text.includes("&ans=later&p=p1") && body.text.includes("&ans=date&p=p1") && body.html.includes("Choose when Sorted reminds you") && body.html.includes("They gave a new date?"), "the after email offers Later and New date");
ok(!__DB.push_subs.find((s) => s.id === "s2") && r2.push_detail === "0 of 1", "a phone the push service has forgotten (410) is removed");
ok(r3.cancelled_at && r3.cancel_reason === "no email", "no email and no phone cancels the reminder");
ok(res.pushed === 1 && res.sent === 2, "the run reports what it sent (" + JSON.stringify(res) + ")");
// email-only still works when push isn't configured
fresh(); delete __SECRETS.vapid_private_jwk;
await (await handler(new Request("https://x/", { headers: { "x-cron-secret": "cron" } }))).json();
ok(calls.filter((c) => c.url.includes("fcm")).length === 0 && __DB.reminders.find((r) => r.id === "r2").sent_at && __DB.reminders.find((r) => r.id === "r1").cancel_reason === "no email", "without the push key, email works as before and a guest’s reminder is cancelled");
// v14 (Sorted v143): rows for the person's own attention (t.att): sent while the item is live, fixed words, no answer links
fresh();
const attTask = (id, extra) => ({ id, user_id: "u-mail", data: Object.assign({ id, title: "Evri parcel EV123456", board: "waiting", promises: [{ id: "p1", status: "open", said: "Evri said the parcel EV123456 would come in the next few days", party: "Evri" }] }, extra) });
__DB.reminders = [{ id: "a1", task_id: "a1", user_id: "u-mail", kind: "before", send_at: past, promise_id: "att-chk1" },
  { id: "a2", task_id: "a2", user_id: "u-mail", kind: "before", send_at: past, promise_id: "att-chk2" },
  { id: "a3", task_id: "a3", user_id: "u-mail", kind: "before", send_at: past, promise_id: "att-snz1" },
  { id: "a4", task_id: "a4", user_id: "u-mail", kind: "before", send_at: past, promise_id: "att-snz2" },
  { id: "a5", task_id: "a5", user_id: "u-mail", kind: "start", send_at: past, promise_id: "att-pk-discount-2026-10-08" },
  { id: "a6", task_id: "a6", user_id: "u-mail", kind: "before", send_at: past, promise_id: "att-chk6" }];
__DB.tasks = [attTask("a1", { att: [{ id: "att-chk1", kind: "check", at: past, pid: "p1" }] }),
  attTask("a2", { att: [{ id: "att-chk2", kind: "check", at: past, pid: "p1", cancelled: past }] }),
  attTask("a3", { snooze: { until: past, att: "att-snz1" }, att: [{ id: "att-snz1", kind: "snooze", at: past }] }),
  attTask("a4", { att: [{ id: "att-snz2", kind: "snooze", at: past }] }),
  attTask("a5", { att: [{ id: "att-pk-discount-2026-10-08", kind: "remind", at: "2026-10-08" }] }),
  attTask("a6", { board: "done", att: [{ id: "att-chk6", kind: "check", at: past, pid: "p1" }] })];
__DB.push_subs = [{ id: "s9", user_id: "u-mail", endpoint: "https://fcm.googleapis.com/fcm/send/abc", p256dh: b64u(uaPub), auth: b64u(authS), fails: 0 }];
await (await handler(new Request("https://x/", { headers: { "x-cron-secret": "cron" } }))).json();
const R = (id) => __DB.reminders.find((r) => r.id === id);
const am = calls.filter((c) => c.url.includes("resend")).map((c) => JSON.parse(c.o.body));
ok(R("a1").sent_at && R("a3").sent_at && R("a5").sent_at, "a live check day, a live Later and a parking deadline are sent");
ok(R("a2").cancel_reason === "superseded" && R("a4").cancel_reason === "superseded" && R("a6").cancel_reason === "task done", "a cancelled check day, a Later that has ended and a finished case are not sent");
ok(am.length === 3 && am.every((b) => !/EV123456|Evri|parcel/.test(b.text + b.html + b.subject) && !b.text.includes("&ans=")), "attention emails carry fixed words only, never the case, and no answer links");
ok(am.some((b) => b.subject.includes("your check day")) && am.some((b) => b.subject.includes("a date is coming up")) && am.some((b) => b.text.includes("You asked Sorted to bring one of your cases back now")), "each kind of attention has its own fixed words");
const ap = calls.filter((c) => c.url.includes("/fcm/send/abc"));
const apm = await Promise.all(ap.map((c) => decrypt(new Uint8Array(c.o.body))));
ok(apm.length === 3 && apm.every((x) => !x.x && !x.a && !/Evri|EV123456/.test(JSON.stringify(x))), "attention pushes have no answer buttons and no case words");
// the promise's own "after" push: answers match the email ("No, it didn't"), never "Not yet" for someone else's promise
fresh();
await (await handler(new Request("https://x/", { headers: { "x-cron-secret": "cron" } }))).json();
const pm = await decrypt(new Uint8Array(calls.filter((c) => c.url.includes("/fcm/send/abc"))[0].o.body));
ok(JSON.stringify(pm.x) === JSON.stringify([["yes", "Yes, it happened"], ["no", "No, it didn't"]]), "push answers for their promise say what the email says: " + JSON.stringify(pm.x));
console.log("FAILS", JSON.stringify(fails));
