import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

// v1 (Sorted v137): makes the Web Push signing key inside Supabase, so no person ever sees or types it. Called once
// with the cron secret (from the SQL editor through net.http_post). If `vapid_private_jwk` is not yet in Vault it
// generates a P-256 key pair, stores the private key through push_vapid_init() (service role only) and returns the
// public key; if it is already there it only returns the public key. It never returns or logs the private part.
const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
function eq(a: string, b: string) { if (a.length !== b.length) return false; let r = 0; for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i); return r === 0; }
function b64u(b: Uint8Array) { let s = ""; for (let i = 0; i < b.length; i++) s += String.fromCharCode(b[i]); return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, ""); }
function unb64u(s: string) { const t = s.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((s.length + 3) % 4); const bin = atob(t); const o = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) o[i] = bin.charCodeAt(i); return o; }
function pubOf(j: { x?: string; y?: string }) { const x = unb64u(j.x || ""), y = unb64u(j.y || ""); const o = new Uint8Array(65); o[0] = 4; o.set(x, 1); o.set(y, 33); return b64u(o); }

Deno.serve(async (req: Request) => {
  const { data: cron } = await sb.rpc("sorted_secret", { p_name: "sorted_cron_secret" });
  if (!cron || !eq(req.headers.get("x-cron-secret") || "", String(cron))) return new Response("forbidden", { status: 403 });
  const { data: have } = await sb.rpc("sorted_secret", { p_name: "vapid_private_jwk" });
  if (have) return Response.json({ made: false, pub: pubOf(JSON.parse(String(have))) });
  const kp = await crypto.subtle.generateKey({ name: "ECDSA", namedCurve: "P-256" }, true, ["sign", "verify"]);
  const jwk = await crypto.subtle.exportKey("jwk", kp.privateKey) as JsonWebKey;
  const keep = { kty: jwk.kty, crv: jwk.crv, x: jwk.x, y: jwk.y, d: jwk.d };
  const { data: made, error } = await sb.rpc("push_vapid_init", { p_jwk: JSON.stringify(keep) });
  if (error) return Response.json({ error: "store failed" }, { status: 500 });
  if (!made) { const { data: again } = await sb.rpc("sorted_secret", { p_name: "vapid_private_jwk" }); return Response.json({ made: false, pub: again ? pubOf(JSON.parse(String(again))) : null }); }
  return Response.json({ made: true, pub: pubOf(keep) });
});
