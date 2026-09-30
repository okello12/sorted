import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

// One-click unsubscribe for Sorted reminder emails (RFC 8058).
// POST from the mail app stops all reminder emails for that account; GET goes back to the app.
const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
const SITE = "https://sorted-pilot.vercel.app";

async function secret(name: string): Promise<string | null> {
  const { data } = await sb.rpc("sorted_secret", { p_name: name });
  return (data as string) || null;
}
async function sign(u: string): Promise<string> {
  const k = await crypto.subtle.importKey("raw", new TextEncoder().encode((await secret("sorted_cron_secret")) || ""), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const s = new Uint8Array(await crypto.subtle.sign("HMAC", k, new TextEncoder().encode("stop:" + u)));
  return Array.from(s).map((b) => b.toString(16).padStart(2, "0")).join("").slice(0, 32);
}

Deno.serve(async (req: Request) => {
  const url = new URL(req.url);
  const u = url.searchParams.get("u") || "", t = url.searchParams.get("t") || "";
  const ok = /^[0-9a-f-]{36}$/.test(u) && t.length === 32 && t === await sign(u);
  if (req.method === "POST") {
    if (!ok) return new Response("bad link", { status: 400 });
    await sb.from("email_optouts").upsert({ user_id: u });
    await sb.from("reminders").update({ cancelled_at: new Date().toISOString(), cancel_reason: "unsubscribed" }).eq("user_id", u).is("sent_at", null).is("cancelled_at", null);
    return new Response("ok");
  }
  return Response.redirect(`${SITE}/`, 302);
});
