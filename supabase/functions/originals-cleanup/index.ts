import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

// v1 (Sorted v135): once a day (pg_cron sorted-originals-cleanup), removes kept documents whose case no longer exists:
// deleted by the person, by the retention rules, or with their account. It sees file names only, never what is in
// them, and logs counts only. Called with the cron secret, like send-reminders.
const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
function eq(a: string, b: string) { if (a.length !== b.length) return false; let r = 0; for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i); return r === 0; }

Deno.serve(async (req: Request) => {
  const { data: cron } = await sb.rpc("sorted_secret", { p_name: "sorted_cron_secret" });
  if (!cron || !eq(req.headers.get("x-cron-secret") || "", String(cron))) return new Response("forbidden", { status: 403 });
  let removed = 0, failed = 0;
  for (let round = 0; round < 5; round++) {
    const { data, error } = await sb.rpc("originals_orphans", { p_limit: 500 });
    if (error) return Response.json({ error: "list failed", removed }, { status: 500 });
    const names = ((data ?? []) as any[]).map((r) => r.name).filter(Boolean);
    if (!names.length) break;
    for (let i = 0; i < names.length; i += 100) {
      const batch = names.slice(i, i + 100);
      const { error: e } = await sb.storage.from("originals").remove(batch);
      if (e) { failed += batch.length; await sb.from("ops_errors").insert({ source: "save", kind: "originals_cleanup" }).then(() => {}, () => {}); }
      else removed += batch.length;
    }
    if (failed) break;
  }
  return Response.json({ removed, failed });
});
