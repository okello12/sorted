// Runs supabase/functions/originals-cleanup/index.ts in Node with stand-ins: only files whose case is gone are removed,
// and it refuses without the cron secret. Run: node --experimental-strip-types tests/fn/originals_check.mjs
import { readFileSync, writeFileSync } from "node:fs";
const ok = (c, m) => { console.log((c ? "PASS " : "FAIL ") + m); if (!c) fails.push(m); }, fails = [];
const here = new URL(".", import.meta.url).pathname, root = new URL("../../", import.meta.url).pathname;
writeFileSync(here + "out_oc.mts", readFileSync(root + "supabase/functions/originals-cleanup/index.ts", "utf8").replace(/^import "jsr:[^"]+";$/m, "").replace('from "npm:@supabase/supabase-js@2"', 'from "./sb_stub.mjs"'));
let handler = null;
globalThis.Deno = { serve: (h) => { handler = h; }, env: { get: (k) => ({ SUPABASE_URL: "https://x.supabase.co", SUPABASE_SERVICE_ROLE_KEY: "k" })[k] } };
globalThis.__SECRETS = { sorted_cron_secret: "cron" }; globalThis.__EMAILS = {};
globalThis.__DB = { tasks: [{ id: "t1", user_id: "u1" }], objects: [{ name: "u1/t1/1-letter.pdf" }, { name: "u1/t2/1-gone.jpg" }, { name: "u9/t1/1-other.pdf" }], ops_errors: [] };
await import(here + "out_oc.mts");
let r = await handler(new Request("https://x/", { headers: { "x-cron-secret": "nope" } }));
ok(r.status === 403 && !globalThis.__REMOVED, "without the cron secret it does nothing");
r = await (await handler(new Request("https://x/", { headers: { "x-cron-secret": "cron" } }))).json();
ok(r.removed === 2 && JSON.stringify(__REMOVED.sort()) === JSON.stringify(["u1/t2/1-gone.jpg", "u9/t1/1-other.pdf"]) && __DB.objects.length === 1 && __DB.objects[0].name === "u1/t1/1-letter.pdf", "it removes only files whose case (for that person) no longer exists");
console.log("FAILS", JSON.stringify(fails));
