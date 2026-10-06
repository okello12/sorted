import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

// v1 (Sorted v135): once a day (pg_cron sorted-originals-cleanup), removes kept documents whose case no longer exists:
// deleted by the person, by the retention rules, or with their account. It sees file names only, never what is in
// them, and logs counts only. Called with the cron secret, like send-reminders.
// v2 (Sorted v142): first moves the kept documents of a guest who added an email (doc_moves, recorded by claim_carry,
// which also calls this straight away with {"moves_only":true}) from <guest>/<case>/ to <account>/<case>/, using the
// new case id when the page gave one. The files themselves are never opened.
const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
function eq(a: string, b: string) { if (a.length !== b.length) return false; let r = 0; for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i); return r === 0; }
const UUID = /^[0-9a-f-]{36}$/;

async function doMoves(): Promise<{ moved: number; moveFailed: number }> {
  let moved = 0, moveFailed = 0;
  const { data: rows, error } = await sb.rpc("doc_moves_pending", { p_limit: 20 });
  if (error || !rows) return { moved, moveFailed };
  for (const m of rows as any[]) {
    if (!UUID.test(String(m.from_uid)) || !UUID.test(String(m.to_uid))) continue;
    const map = new Map<string, string>();
    if (Array.isArray(m.pairs)) for (const p of m.pairs) if (Array.isArray(p) && typeof p[0] === "string" && typeof p[1] === "string" && p[1].length <= 40 && !p[1].includes("/")) map.set(p[0], p[1]);
    const { data: names } = await sb.rpc("originals_under", { p_uid: m.from_uid });
    let bad = 0;
    for (const r of (names ?? []) as any[]) {
      const parts = String(r.name || "").split("/");
      if (parts.length !== 3 || parts[0] !== m.from_uid) continue;
      const to = `${m.to_uid}/${map.get(parts[1]) || parts[1]}/${parts[2]}`;
      const { error: e } = await sb.storage.from("originals").move(r.name, to);
      if (e) bad++; else moved++;
    }
    if (!bad) await sb.rpc("doc_move_done", { p_id: m.id });
    else { moveFailed += bad; await sb.from("ops_errors").insert({ source: "save", kind: "originals_move" }).then(() => {}, () => {}); }
  }
  return { moved, moveFailed };
}

Deno.serve(async (req: Request) => {
  const { data: cron } = await sb.rpc("sorted_secret", { p_name: "sorted_cron_secret" });
  if (!cron || !eq(req.headers.get("x-cron-secret") || "", String(cron))) return new Response("forbidden", { status: 403 });
  let body: any = {}; try { body = await req.json(); } catch { body = {}; }
  const mv = await doMoves();
  if (body && body.moves_only) return Response.json(mv);
  let removed = 0, failed = 0;
  for (let round = 0; round < 5; round++) {
    const { data, error } = await sb.rpc("originals_orphans", { p_limit: 500 });
    if (error) return Response.json({ error: "list failed", removed, ...mv }, { status: 500 });
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
  return Response.json({ removed, failed, ...mv });
});
