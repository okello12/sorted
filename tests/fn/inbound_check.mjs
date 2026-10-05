// Runs supabase/functions/inbound-email/index.ts in Node with stand-ins, and checks v134 forwarding: a signed email to
// a person's secret address is stored for them as an unassigned suggestion, whoever it claims to be from; an unknown or
// malformed address stores nothing; a bad signature is refused; 30 a day at most; case- replies still work.
// Run: node --experimental-strip-types tests/fn/inbound_check.mjs
import { readFileSync, writeFileSync } from "node:fs";
const ok = (c, m) => { console.log((c ? "PASS " : "FAIL ") + m); if (!c) fails.push(m); }, fails = [];
const here = new URL(".", import.meta.url).pathname, root = new URL("../../", import.meta.url).pathname;
writeFileSync(here + "out_in.mts", readFileSync(root + "supabase/functions/inbound-email/index.ts", "utf8")
  .replace(/^import "jsr:[^"]+";$/m, "").replace('from "npm:@supabase/supabase-js@2"', 'from "./sb_stub.mjs"').replace('from "./readers.mjs"', 'from "./out_readers.mjs"'));
writeFileSync(here + "out_readers.mjs", readFileSync(root + "supabase/functions/inbound-email/readers.mjs", "utf8"));
let handler = null;
globalThis.Deno = { serve: (h) => { handler = h; }, env: { get: (k) => ({ SUPABASE_URL: "https://x.supabase.co", SUPABASE_SERVICE_ROLE_KEY: "k" })[k] } };
globalThis.fetch = async (url) => String(url).includes("/emails/receiving/") ? new Response(JSON.stringify({ text: "Your refund will be paid by Friday. Ref ZX123456." }), { status: 200 }) : new Response("{}", { status: 200 });
const whsec = "whsec_" + Buffer.from("0123456789abcdef0123456789abcdef").toString("base64");
globalThis.__SECRETS = { resend_webhook_secret: whsec, inbound_domain: "in.example.uk", resend_api_key: "rk", case_replies_on: "yes", reminder_from: "Sorted <r@example.com>" };
globalThis.__EMAILS = {};
await import(here + "out_in.mts");
async function post(payload, sigOk = true) {
  const body = JSON.stringify(payload), id = "msg_" + Math.random(), ts = String(Math.floor(Date.now() / 1000));
  const key = await crypto.subtle.importKey("raw", Buffer.from(whsec.slice(6), "base64"), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const mac = Buffer.from(await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(`${id}.${ts}.${body}`))).toString("base64");
  const r = await handler(new Request("https://x/", { method: "POST", body, headers: { "svix-id": id, "svix-timestamp": ts, "svix-signature": "v1," + (sigOk ? mac : "AAAA") } }));
  return { status: r.status, j: await r.json().catch(() => ({})) };
}
const mail = (to, from = "Currys <help@currys.co.uk>") => ({ type: "email.received", data: { email_id: "e1", from, to: [to], cc: [], subject: "Your refund" } });
globalThis.__DB = { inbound_addresses: [{ user_id: "u1", token: "log-0123456789abcdef" }], inbound_items: [], ops_errors: [], case_mail: [{ token: "case-abc", task_id: "t9", user_id: "u2" }], email_optouts: [] };
let r = await post(mail("log-0123456789abcdef@in.example.uk"));
const it = __DB.inbound_items[0];
ok(r.j.stored === 1 && it && it.user_id === "u1" && !it.task_id && it.from_domain === "currys.co.uk" && it.body.includes("Ref ZX123456"), "an email to a person’s secret address is kept for them, unassigned, with the website it came from");
r = await post(mail("log-0123456789abcdef@in.example.uk", "Someone pretending <me@gmail.com>"));
ok(r.j.stored === 1 && __DB.inbound_items.length === 2, "whoever it claims to be from, it is only a suggestion (stored, not acted on)");
r = await post(mail("log-ffffffffffffffff@in.example.uk"));
ok(r.j.stored === 0 && __DB.ops_errors.some((e) => e.kind === "unknown_address"), "an address that isn’t anyone’s stores nothing");
r = await post(mail("log-../../x@in.example.uk"));
ok(r.j.stored === 0, "a malformed address stores nothing");
r = await post(mail("log-0123456789abcdef@other.uk"));
ok(r.j.stored === 0, "another domain stores nothing");
r = await post(mail("log-0123456789abcdef@in.example.uk"), false);
ok(r.status === 401 && __DB.inbound_items.length === 2, "a bad signature is refused");
for (let i = 0; i < 30; i++) await post(mail("log-0123456789abcdef@in.example.uk"));
ok(__DB.inbound_items.filter((x) => x.user_id === "u1").length === 30 && __DB.ops_errors.some((e) => e.kind === "daily_limit"), "at most 30 a day per person");
r = await post(mail("case-abc@in.example.uk"));
ok(r.j.stored === 1 && __DB.inbound_items.some((x) => x.task_id === "t9"), "a reply to a case’s own address still goes to that case");
console.log("FAILS", JSON.stringify(fails));
