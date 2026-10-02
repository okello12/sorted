import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

// Resend webhook for email.received. A user forwards a company's email to their own
// secret Sorted address; we keep the subject and text for up to 30 days so the app
// can offer to log it as a promise. Security: signed webhook (Svix), secret address,
// and the forwarder must be the account's own email address.
// Failures and rejections are logged to ops_errors as a kind and a time only (no addresses, no content).
const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });

const FORWARDING_OFF = true;  // personal forwarding (log-) addresses stay off; case- replies are separate (v4)

async function oops(kind: string) { try { await sb.from("ops_errors").insert({ source: "inbound", kind }); } catch { /* never block mail on logging */ } }
async function secret(name: string): Promise<string | null> {
  const { data } = await sb.rpc("sorted_secret", { p_name: name });
  return (data as string) || null;
}
function b64decode(s: string): Uint8Array { return Uint8Array.from(atob(s), (c) => c.charCodeAt(0)); }
function b64encode(b: ArrayBuffer): string { return btoa(String.fromCharCode(...new Uint8Array(b))); }
function eq(a: string, b: string) { if (a.length !== b.length) return false; let r = 0; for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i); return r === 0; }

async function verify(req: Request, body: string): Promise<"ok" | "no_secret" | "bad_signature"> {
  const whsec = await secret("resend_webhook_secret");
  if (!whsec) return "no_secret";
  const id = req.headers.get("svix-id"), ts = req.headers.get("svix-timestamp"), sig = req.headers.get("svix-signature");
  if (!id || !ts || !sig) return "bad_signature";
  if (Math.abs(Date.now() / 1000 - Number(ts)) > 300) return "bad_signature";
  const key = await crypto.subtle.importKey("raw", b64decode(whsec.replace(/^whsec_/, "")), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const mac = b64encode(await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(`${id}.${ts}.${body}`)));
  return sig.split(" ").some((p) => { const [v, s] = p.split(","); return v === "v1" && !!s && eq(s, mac); }) ? "ok" : "bad_signature";
}
const addr = (s: string) => { const m = String(s || "").match(/<([^>]+)>/); return (m ? m[1] : String(s || "")).trim().toLowerCase(); };
const strip = (html: string) => html.replace(/<style[\s\S]*?<\/style>/gi, "").replace(/<br\s*\/?>/gi, "\n").replace(/<\/(p|div|tr|li|h\d)>/gi, "\n").replace(/<[^>]+>/g, "").replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&#39;/g, "'").replace(/&quot;/g, '"').replace(/\n{3,}/g, "\n\n");

async function bodyText(d: any): Promise<string> {
  const key = (await secret("resend_inbound_key")) || (await secret("resend_api_key"));
  if (!key) { await oops("no_secret"); return ""; }
  if (!d.email_id) return "";
  const r = await fetch(`https://api.resend.com/emails/receiving/${encodeURIComponent(d.email_id)}`, { headers: { Authorization: `Bearer ${key}` } });
  if (!r.ok) { await oops("fetch_failed"); return ""; }
  const j = await r.json();
  return String(j.text || (j.html ? strip(j.html) : ""));
}

// v4 (Sorted v70): replies come back into the case. Every message's signature is checked first. Each case has its own
// address case-<random>@<inbound domain>, added in Cc when the person emails a company from that case. A reply to it is
// stored for that case only, with the sender's website (domain) and never their full address, and the app shows it as
// a proposal the owner must confirm. Old personal forwarding addresses (log-...) stay switched off.
async function handle(req: Request): Promise<Response> {
  if (req.method !== "POST") return new Response("ok");
  const body = await req.text();
  const v = await verify(req, body);
  if (v !== "ok") { await oops(v); return new Response("bad signature", { status: 401 }); }
  let ev: any; try { ev = JSON.parse(body); } catch { await oops("bad_json"); return new Response("bad json", { status: 400 }); }
  if (ev?.type !== "email.received") return Response.json({ ignored: ev?.type });
  const d = ev.data || {};
  const domain = (await secret("inbound_domain") || "").toLowerCase();
  if (!domain) { await oops("no_secret"); return Response.json({ stored: 0 }); }
  const on = (await secret("case_replies_on")) === "yes";
  const from = addr(d.from), fromDomain = from.slice(from.lastIndexOf("@") + 1).slice(0, 120);
  const rcpts = ([] as string[]).concat(d.to || [], d.cc || []).map(addr);
  let stored = 0, text: string | null = null;
  for (const a of rcpts) {
    const at = a.lastIndexOf("@");
    if (at < 0 || a.slice(at + 1) !== domain) continue;
    const local = a.slice(0, at);
    if (local.startsWith("log-")) { if (FORWARDING_OFF) continue; }
    if (!local.startsWith("case-") || !on) continue;
    const { data: cm } = await sb.from("case_mail").select("task_id,user_id").eq("token", local).maybeSingle();
    if (!cm) { await oops("unknown_address"); continue; }
    const { count } = await sb.from("inbound_items").select("id", { count: "exact", head: true }).eq("task_id", cm.task_id).gte("received_at", new Date(Date.now() - 86400000).toISOString());
    if ((count ?? 0) >= 20) { await oops("daily_limit"); continue; }
    if (text === null) text = await bodyText(d);
    const { error } = await sb.from("inbound_items").insert({ user_id: cm.user_id, task_id: cm.task_id, from_domain: fromDomain, subject: String(d.subject || "").slice(0, 300), body: (text || "").slice(0, 8000) });
    if (error) { await oops("store_failed"); continue; }
    stored++;
  }
  return Response.json({ stored });
}

Deno.serve(async (req: Request) => {
  try { return await handle(req); }
  catch (e) { console.log("inbound exception", String(e).slice(0, 200)); await oops("exception"); return new Response("error", { status: 500 }); }
});
