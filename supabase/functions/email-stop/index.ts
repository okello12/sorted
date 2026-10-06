import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

// One-click unsubscribe for Sorted reminder emails (RFC 8058).
// POST from the mail app stops all reminder emails for that account; GET goes back to the app's Settings.
// v2 (Sorted v141): refuses to work if the signing secret can't be read (an empty key would let anyone make a token),
// compares the token in constant time, and no longer cancels the reminders themselves: send-reminders checks the
// opt-out for each email, so lock-screen reminders on the person's phone carry on.
const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
const SITE = "https://sorted-pilot.vercel.app";

async function secret(name: string): Promise<string | null> {
  const { data } = await sb.rpc("sorted_secret", { p_name: name });
  return (data as string) || null;
}
async function sign(u: string, key: string): Promise<string> {
  const k = await crypto.subtle.importKey("raw", new TextEncoder().encode(key), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const s = new Uint8Array(await crypto.subtle.sign("HMAC", k, new TextEncoder().encode("stop:" + u)));
  return Array.from(s).map((b) => b.toString(16).padStart(2, "0")).join("").slice(0, 32);
}
function eq(a: string, b: string) { if (a.length !== b.length) return false; let r = 0; for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i); return r === 0; }

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") return Response.redirect(`${SITE}/#more-settings`, 302);
  const url = new URL(req.url);
  const u = url.searchParams.get("u") || "", t = url.searchParams.get("t") || "";
  const key = await secret("sorted_cron_secret");
  if (!key) return new Response("unavailable", { status: 503 });
  const ok = /^[0-9a-f-]{36}$/.test(u) && t.length === 32 && eq(t, await sign(u, key));
  if (!ok) return new Response("bad link", { status: 400 });
  await sb.from("email_optouts").upsert({ user_id: u });
  return new Response("ok");
});
