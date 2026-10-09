import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

// v1 (Sorted v116): Resend's delivery webhooks. Resend accepting an email is not arrival, so each event
// (delivered, bounced, failed, delayed, complained) is written against the reminder with that provider id through
// reminder_delivery_event(). Nothing else from the payload is kept: not the address, not the subject.
// Signed by Resend with Svix headers; the signing secret is the Vault secret resend_events_secret. Without it, 503.
// verify_jwt is off: Resend does not send a Supabase JWT.
// v2 (Sorted v145): the endpoint is public, so unsigned requests could add ops_errors rows without end; a kind of
// error is now logged at most 60 times an hour.
const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
const TOL_S = 5 * 60;

async function secret(name: string): Promise<string | null> {
  const { data } = await sb.rpc("sorted_secret", { p_name: name });
  return (data as string) || null;
}
async function oops(kind: string, detail?: string) {
  try {
    const k = kind.slice(0, 40);
    const { count } = await sb.from("ops_errors").select("id", { count: "exact", head: true }).eq("source", "webhook").eq("kind", k).gte("at", new Date(Date.now() - 3600000).toISOString());
    if ((count ?? 0) >= 60) return;
    await sb.from("ops_errors").insert({ source: "webhook", kind: k, detail: detail ? detail.slice(0, 200) : null });
  } catch { /* ignore */ }
}
function eq(a: string, b: string) { if (a.length !== b.length) return false; let r = 0; for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i); return r === 0; }
const b64 = (u: Uint8Array) => btoa(String.fromCharCode(...u));
function fromB64(s: string): Uint8Array { const bin = atob(s); const u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return u; }

// Svix: signature over "<id>.<timestamp>.<body>" with the whsec_ secret (base64 after the prefix); several signatures may be listed.
async function verify(req: Request, body: string, whsec: string): Promise<boolean> {
  const id = req.headers.get("svix-id") || "", ts = req.headers.get("svix-timestamp") || "", sigs = req.headers.get("svix-signature") || "";
  if (!id || !ts || !sigs) return false;
  const age = Math.abs(Date.now() / 1000 - Number(ts));
  if (!Number.isFinite(age) || age > TOL_S) return false;
  const raw = whsec.startsWith("whsec_") ? whsec.slice(6) : whsec;
  const key = await crypto.subtle.importKey("raw", fromB64(raw), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const mac = b64(new Uint8Array(await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(`${id}.${ts}.${body}`))));
  return sigs.split(" ").some((s) => { const [v, sig] = s.split(","); return v === "v1" && sig && eq(sig, mac); });
}

const KNOWN = new Set(["email.delivered", "email.bounced", "email.failed", "email.delivery_delayed", "email.complained"]);

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") return new Response("method", { status: 405 });
  const whsec = await secret("resend_events_secret");
  if (!whsec) { await oops("no_secret"); return new Response("not configured", { status: 503 }); }
  const body = await req.text();
  if (body.length > 64 * 1024) return new Response("too large", { status: 413 });
  if (!(await verify(req, body, whsec))) { await oops("bad_signature"); return new Response("forbidden", { status: 403 }); }
  let ev: any; try { ev = JSON.parse(body); } catch { await oops("bad_json"); return new Response("bad json", { status: 400 }); }
  const type = String(ev?.type || ""), emailId = String(ev?.data?.email_id || "");
  if (!KNOWN.has(type)) return Response.json({ ignored: type.slice(0, 40) });     // sent, opened, clicked and the rest: not kept
  if (!emailId) { await oops("no_email_id", type); return Response.json({ ignored: "no id" }); }
  const at = ev?.created_at && !isNaN(Date.parse(ev.created_at)) ? new Date(ev.created_at).toISOString() : new Date().toISOString();
  // the detail is Resend's bounce classification only (e.g. "Permanent / General"); never the message or the address
  const b = ev?.data?.bounce;
  let detail: string | null = type === "email.bounced" && b ? [b.type, b.subType || b.sub_type].filter(Boolean).join(" / ").slice(0, 80) : (type === "email.failed" && ev?.data?.failed?.reason ? String(ev.data.failed.reason).slice(0, 80) : null);
  if (detail && detail.includes("@")) detail = null;
  const { data, error } = await sb.rpc("reminder_delivery_event", { p_provider_id: emailId.slice(0, 80), p_event: type, p_at: at, p_detail: detail });
  if (error) { await oops("write_failed", error.code || error.message); return new Response("write failed", { status: 500 }); }
  return Response.json({ recorded: data === true });   // false: an email that isn't a reminder (a helper nudge, a reply notice)
});
