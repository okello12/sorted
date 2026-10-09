// v145: an in-memory stand-in for supabase-js used by tests/fn/server145_check.mjs. Like sb_stub.mjs, plus upsert,
// select with head counts on any table, the RPCs originals-cleanup and resend-events call, and storage.move.
// The test fills globalThis.__DB and globalThis.__SECRETS before calling a handler.
function q(table) {
  const st = { op: "select", filters: [], vals: null, single: false, head: false };
  const rows = () => (globalThis.__DB[table] ||= []);
  const match = (r) => st.filters.every(([k, op, v]) => op === "eq" ? r[k] === v : op === "is" ? (r[k] ?? null) === v : op === "lt" ? r[k] < v : op === "gte" ? r[k] >= v : true);
  const run = () => {
    const hit = rows().filter(match);
    if (st.op === "update") { hit.forEach((r) => Object.assign(r, st.vals)); return { data: hit, error: null }; }
    if (st.op === "insert" && globalThis.__FAIL_INSERT === table) return { data: null, error: { code: "XX000", message: "test failure" } };
    if (st.op === "insert" && table === "inbound_seen" && rows().some((r) => r.key === st.vals.key)) return { data: null, error: { code: "23505", message: "duplicate key" } };
    if (st.op === "insert") { const row = Object.assign({ id: "i" + Math.random().toString(36).slice(2), received_at: new Date().toISOString(), at: new Date().toISOString() }, st.vals); rows().push(row); return { data: [row], error: null }; }
    if (st.op === "upsert") { const key = Object.keys(st.vals)[0]; const old = rows().find((r) => r[key] === st.vals[key]); if (old) Object.assign(old, st.vals); else rows().push(Object.assign({}, st.vals)); return { data: [st.vals], error: null }; }
    if (st.head) return { data: null, count: hit.length, error: null };
    if (st.op === "delete") { globalThis.__DB[table] = rows().filter((r) => !match(r)); return { data: hit, error: null }; }
    return { data: st.single ? (hit[0] ?? null) : hit, error: null };
  };
  const self = {
    select(c, o) { if (o && o.head) st.head = true; return self; },
    insert(v) { st.op = "insert"; st.vals = v; return self; },
    upsert(v) { st.op = "upsert"; st.vals = v; return self; },
    update(v) { st.op = "update"; st.vals = v; return self; },
    delete() { st.op = "delete"; return self; },
    eq(k, v) { st.filters.push([k, "eq", v]); return self; },
    is(k, v) { st.filters.push([k, "is", v]); return self; },
    lt(k, v) { st.filters.push([k, "lt", v]); return self; },
    gte(k, v) { st.filters.push([k, "gte", v]); return self; },
    maybeSingle() { st.single = true; return self; },
    then(a, b) { return Promise.resolve(run()).then(a, b); },
  };
  return self;
}
export function createClient() {
  return {
    from: q,
    rpc: async (name, args) => {
      const DB = globalThis.__DB;
      if (name === "sorted_secret") return { data: globalThis.__SECRETS[args.p_name] ?? null };
      if (name === "claim_due_reminders") return { data: (DB.reminders || []).filter((r) => !r.sent_at && !r.cancelled_at), error: null };
      if (name === "claim_helper_invites") return { data: [] };
      if (name === "doc_moves_pending") return { data: (DB.doc_moves || []).filter((m) => !m.done_at), error: null };
      if (name === "originals_under") return { data: (DB.objects || []).filter((o) => o.name.startsWith(args.p_uid + "/")).slice(0, 2000).map((o) => ({ name: o.name })), error: null };
      if (name === "doc_move_done") { (DB.doc_moves || []).forEach((m) => { if (m.id === args.p_id) m.done_at = new Date().toISOString(); }); return { data: null, error: null }; }
      if (name === "originals_orphans") return { data: [], error: null };
      if (name === "reminder_delivery_event") { (DB.delivery ||= []).push(args); return { data: true, error: null }; }
      return { data: null };
    },
    storage: { from: () => ({
      move: async (from, to) => { const o = (globalThis.__DB.objects || []).find((x) => x.name === from); if (!o) return { error: { message: "missing" } }; o.name = to; return { data: {}, error: null }; },
      remove: async (names) => { globalThis.__DB.objects = (globalThis.__DB.objects || []).filter((o) => !names.includes(o.name)); return { data: names, error: null }; },
    }) },
    auth: { admin: { getUserById: async (id) => ({ data: { user: { id, email: (globalThis.__EMAILS || {})[id] || null } } }) } },
  };
}
