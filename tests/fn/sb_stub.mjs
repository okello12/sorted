// A tiny in-memory stand-in for supabase-js, enough for send-reminders: from().select/update/delete with eq, is, lt,
// maybeSingle; rpc; auth.admin.getUserById. The test fills globalThis.__DB before calling the handler.
function q(table) {
  const st = { op: "select", filters: [], vals: null, single: false };
  const rows = () => (globalThis.__DB[table] ||= []);
  const match = (r) => st.filters.every(([k, op, v]) => op === "eq" ? r[k] === v : op === "is" ? (r[k] ?? null) === v : op === "lt" ? r[k] < v : true);
  const run = () => {
    const hit = rows().filter(match);
    if (st.op === "update") { hit.forEach((r) => Object.assign(r, st.vals)); return { data: hit, error: null }; }
    if (st.op === "delete") { globalThis.__DB[table] = rows().filter((r) => !match(r)); return { data: hit, error: null }; }
    return { data: st.single ? (hit[0] ?? null) : hit, error: null };
  };
  const self = {
    select() { if (st.op === "select") st.op = "select"; return self; },
    update(v) { st.op = "update"; st.vals = v; return self; },
    delete() { st.op = "delete"; return self; },
    eq(k, v) { st.filters.push([k, "eq", v]); return self; },
    is(k, v) { st.filters.push([k, "is", v]); return self; },
    lt(k, v) { st.filters.push([k, "lt", v]); return self; },
    maybeSingle() { st.single = true; return self; },
    then(a, b) { return Promise.resolve(run()).then(a, b); },
  };
  return self;
}
export function createClient() {
  return {
    from: q,
    rpc: async (name, args) => {
      if (name === "sorted_secret") return { data: globalThis.__SECRETS[args.p_name] ?? null };
      if (name === "claim_due_reminders") return { data: (globalThis.__DB.reminders || []).filter((r) => !r.sent_at && !r.cancelled_at), error: null };
      if (name === "claim_helper_invites") return { data: [] };
      return { data: null };
    },
    auth: { admin: { getUserById: async (id) => ({ data: { user: { id, email: globalThis.__EMAILS[id] || null } } }) } },
  };
}
