# The live suite: Sorted's server contract, run against the STAGING project (never live). Two throwaway anonymous
# accounts, A and B, created for the run and deleted at the end. It checks what the mock cannot: that row level
# security, grants and the server functions behave on a real Supabase project.
#
#   SORTED_STAGING_URL=https://<ref>.supabase.co SORTED_STAGING_ANON_KEY=<publishable key> python3 tests/live/staging.py
#
# Refuses to run against the live project. Needs anonymous sign-in switched on in the staging project's
# Authentication settings; if it is off, the first check says so and the rest are skipped.
# With Playwright installed it also walks the real page (public/index.html with the staging URL and key swapped in)
# through a first case, so the client path is tested against a real database too.
import os, sys, json, time, uuid, urllib.request, urllib.error
URL = os.environ.get('SORTED_STAGING_URL', '').rstrip('/'); KEY = os.environ.get('SORTED_STAGING_ANON_KEY', '')
URL = URL.strip(); KEY = KEY.strip()
import re as _re
if URL and KEY and not (_re.fullmatch(r'sb_publishable_[A-Za-z0-9_-]{10,}', KEY) or _re.fullmatch(r'eyJ[A-Za-z0-9_.-]{20,}', KEY)):
    # never print the value: say what is wrong with it
    bad = sorted(set(ch for ch in KEY if ord(ch) > 126 or ch.isspace()))
    print('FAIL the repository secret SORTED_STAGING_ANON_KEY is not a Supabase publishable key (%d characters, starts %r%s). Copy it again from Supabase > Project Settings > API Keys > Publishable key.' % (len(KEY), KEY[:15], (', contains ' + ' '.join(repr(c) for c in bad)) if bad else ''))
    print('ERRORS', []); print('FAILS', ['staging key secret is malformed']); sys.exit(1)
if URL and not _re.fullmatch(r'https://[a-z0-9]{20}\.supabase\.co', URL):
    print('FAIL the repository secret SORTED_STAGING_URL should look like https://<project ref>.supabase.co (%d characters)' % len(URL))
    print('ERRORS', []); print('FAILS', ['staging url secret is malformed']); sys.exit(1)
LIVE_REF = 'boxrwcuhxmimayaxzywu'
fails = []; errs = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
if not URL or not KEY:
    print('SKIP: SORTED_STAGING_URL and SORTED_STAGING_ANON_KEY are not set'); print('ERRORS', errs); print('FAILS', fails); sys.exit(0)
if LIVE_REF in URL:
    print('REFUSED: this suite never runs against the live project'); print('ERRORS', ['live project']); print('FAILS', fails); sys.exit(1)

def call(method, path, body=None, token=None, headers=None):
    h = {'apikey': KEY, 'Authorization': 'Bearer ' + (token or KEY), 'Content-Type': 'application/json'}
    if headers: h.update(headers)
    req = urllib.request.Request(URL + path, data=json.dumps(body).encode() if body is not None else None, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode(); return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try: return e.code, json.loads(raw)
        except Exception: return e.code, raw
    except urllib.error.URLError as e:
        print('NETWORK: cannot reach %s (%s). Run this where the staging project is reachable, for example the CI job.' % (URL, e.reason))
        print('ERRORS', ['network']); print('FAILS', fails); sys.exit(1)
def rest(method, path, body=None, token=None, prefer=None):
    return call(method, '/rest/v1/' + path, body, token, {'Prefer': prefer} if prefer else None)
def rpc(name, args, token=None): return call('POST', '/rest/v1/rpc/' + name, args, token)
def anon_user():
    st, r = call('POST', '/auth/v1/signup', {'data': {}, 'gotrue_meta_security': {}})
    if st != 200 or not isinstance(r, dict) or not r.get('access_token'): return None, r
    return r['access_token'], r

# --- two throwaway people --------------------------------------------------------------------------------------------
A, ra = anon_user()
if not A:
    msg = str(ra)
    ok(False, 'anonymous sign-in works on staging (switch it on under Authentication > Sign In / Providers): %s' % msg[:160])
    print('CHECKS', n[0]); print('ERRORS', errs); print('FAILS', fails); sys.exit(1)
B, rb = anon_user()
ok(bool(B), 'a second anonymous account')
uid_a = ra['user']['id']; uid_b = rb['user']['id'] if rb and isinstance(rb, dict) and rb.get('user') else None
ok(uid_a != uid_b, 'the two accounts are different people')

def case(tid, title, rev=1):
    return {'id': tid, 'title': title, 'board': 'waiting', 'rev': rev, 'events': [], 'promises': [{'id': 'p1', 'status': 'open', 'party': 'Sky', 'ref': 'AB123', 'dueAt': '2030-01-01T09:00:00.000Z'}]}

# --- A's case: only A can see or change it --------------------------------------------------------------------------
tid = 'live' + uuid.uuid4().hex[:12]
st, r = rest('POST', 'tasks', {'id': tid, 'data': case(tid, 'Sky engineer')}, A, 'return=representation')
ok(st == 201, 'A creates a case (%s)' % st)
st, r = rest('GET', 'tasks?select=id&id=eq.' + tid, None, A)
ok(st == 200 and len(r) == 1, 'A can read it back')
st, r = rest('GET', 'tasks?select=id&id=eq.' + tid, None, B)
ok(st == 200 and r == [], 'B cannot see A’s case (row level security)')
st, r = rest('GET', 'tasks?select=id', None, B)
ok(st == 200 and r == [], 'B sees no cases at all')
st, r = rest('PATCH', 'tasks?id=eq.' + tid, {'data': case(tid, 'Hijacked', 2)}, B, 'return=representation')
ok(st in (200, 204) and (r == [] or r is None), 'B’s update of A’s case changes nothing (%s)' % st)
st, r = rest('GET', 'tasks?select=data->>title&id=eq.' + tid, None, A)
ok(st == 200 and r and r[0].get('title') == 'Sky engineer', 'A’s case is unchanged')
st, r = rest('DELETE', 'tasks?id=eq.' + tid, None, B, 'return=representation')
ok(st in (200, 204) and (r == [] or r is None), 'B cannot delete A’s case')
st, r = rest('GET', 'tasks?select=id&id=eq.' + tid, None, A)
ok(st == 200 and len(r) == 1, 'it is still there')
st, r = rest('POST', 'tasks', {'id': 'live' + uuid.uuid4().hex[:12], 'user_id': uid_a, 'data': case('x', 'Planted')}, B)
ok(st in (401, 403) or (isinstance(r, dict) and r.get('code') == '42501'), 'B cannot create a case in A’s name (%s)' % st)
# the two-device rule: an update only lands if the revision is still the one this device saved
st, r = rest('PATCH', 'tasks?id=eq.%s&data->>rev=eq.1' % tid, {'data': case(tid, 'Sky engineer (phone)', 2)}, A, 'return=representation')
ok(st == 200 and len(r) == 1, 'A’s update with the current revision lands')
st, r = rest('PATCH', 'tasks?id=eq.%s&data->>rev=eq.1' % tid, {'data': case(tid, 'Sky engineer (laptop)', 2)}, A, 'return=representation')
ok(st == 200 and r == [], 'a second device holding the old revision gets no rows, so it merges instead of overwriting')

# --- the bits the page is not allowed to touch ----------------------------------------------------------------------
for tbl in ('pilot_events', 'ops_errors', 'share_opens', 'promise_outcomes', 'pilot_admins', 'pilot_carry', 'inbound_addresses', 'helper_suppress', 'assistant_usage'):
    st, r = rest('GET', tbl + '?select=*&limit=1', None, A)
    ok(st in (401, 403) or (isinstance(r, dict) and r.get('code') == '42501'), 'a signed-in person cannot read %s (%s)' % (tbl, st))
st, r = rest('POST', 'pilot_events', {'actor': uid_b, 'name': 'case_started', 'case_id': tid}, A)
ok(st in (401, 403) or (isinstance(r, dict) and r.get('code') == '42501'), 'A cannot write a step record as B')
st, r = rest('POST', 'pilot_events', {'name': 'case_started', 'case_id': tid}, A, 'return=minimal')
ok(st == 201, 'A can write a step record as A (%s)' % st)
st, r = rpc('pilot_metrics', {'include_admins': False}, A)
ok(st >= 400 and 'not allowed' in json.dumps(r), 'the numbers are admin only')
st, r = rpc('pilot_health', {}, A)
ok(st >= 400 and 'not allowed' in json.dumps(r), 'health is admin only')

# --- a share link: read by anyone with the token, counted, switched off ---------------------------------------------
tok = uuid.uuid4().hex + uuid.uuid4().hex[:8]
st, r = rest('POST', 'shares', {'token': tok, 'task_id': tid, 'card': {'v': 2, 'title': 'Sky engineer', 'rows': []}}, A, 'return=minimal')
ok(st == 201, 'A shares the case (%s)' % st)
st, r = rpc('get_share', {'p_token': tok})
ok(st == 200 and r and r[0]['card']['title'] == 'Sky engineer', 'the link opens with no account at all')
st, r = rpc('get_share', {'p_token': 'x' * 40})
ok(st == 200 and r == [], 'a wrong token shows nothing')
st, r = rpc('share_seen', {'p_token': tok})
ok(st in (200, 204), 'opening it is counted (%s)' % st)
st, r = rest('GET', 'shares?select=token&task_id=eq.' + tid, None, B)
ok(st == 200 and r == [], 'B cannot list A’s links')
st, r = rest('POST', 'shares', {'token': uuid.uuid4().hex + 'yy', 'task_id': tid, 'card': {}}, B)
ok(st in (401, 403) or (isinstance(r, dict) and r.get('code') == '42501'), 'B cannot share A’s case')
st, r = rest('DELETE', 'shares?task_id=eq.' + tid, None, A, 'return=representation')
ok(st == 200 and len(r) == 1, 'A switches the link off')
st, r = rpc('get_share', {'p_token': tok})
ok(st == 200 and r == [], 'and it stops working at once')

# --- errors the operator can see, never case text --------------------------------------------------------------------
st, r = rpc('report_page_error', {'p_source': 'page', 'p_kind': 'TypeError', 'p_detail': 'x is not a function', 'p_build': 'v109'})
ok(st in (200, 204), 'the page can report an error without an account (%s)' % st)
st, r = rpc('report_page_error', {'p_source': 'nope', 'p_kind': 'x', 'p_detail': 'y', 'p_build': 'z'})
ok(st in (200, 204), 'an unknown source is ignored, not an error')

# --- company totals: a code only ----------------------------------------------------------------------------------
st, r = rpc('record_outcome', {'p_promise': 'p1', 'p_party': 'Sky', 'p_outcome': 'kept', 'p_via': 'phone'}, A)
ok(st in (200, 204), 'an outcome is recorded (%s)' % st)
st, r = rpc('record_outcome', {'p_promise': 'p2', 'p_party': 'Not A Company Ltd', 'p_outcome': 'kept', 'p_via': ''}, A)
ok(st in (200, 204), 'a company off the list is dropped quietly')
st, r = rpc('drop_outcome', {'p_promise': 'p1'}, A)
ok(st in (200, 204), 'Undo drops it')
st, r = rpc('company_scores', {}, A)
ok(st == 200 and isinstance(r, list), 'the totals can be read by anyone signed in')

# --- guest activity (v116): opening Sorted signed in is recorded; nobody can read the table ------------------------------
st, r = rpc('touch_seen', {}, A)
ok(st in (200, 204), 'a signed-in person can record a visit (touch_seen %s)' % st)
st, r = rpc('touch_seen', {})
ok(st in (401, 403, 404) or (isinstance(r, dict) and r.get('code') in ('42501', 'PGRST202', 'PGRST301')), 'with no account it is refused (%s)' % st)
st, r = rest('GET', 'user_seen?select=user_id', None, A)
ok(st in (401, 403, 404) or (isinstance(r, dict) and r.get('code') in ('42501', 'PGRST301', 'PGRST205')) or r == [], 'the seen table cannot be read by a signed-in person (%s)' % st)
st, r = rpc('reminder_delivery_event', {'p_provider_id': 'x', 'p_event': 'email.delivered', 'p_at': '2026-01-01T00:00:00Z'}, A)
ok(st in (401, 403, 404) or (isinstance(r, dict) and r.get('code') in ('42501', 'PGRST202')), 'delivery events cannot be written by a signed-in person (%s)' % st)
# the deletion rule itself is checked by tests/live/guest_rule.sql in the SQL editor (a transaction that is rolled back)

# --- the email reminders switch (v118): a signed-in person can stop and restart their own emails, nobody else's ---
st, r = rpc('set_email_optout', {'p_off': True}, A)
ok(st == 200 and r is True, 'A switches email reminders off (%s)' % st)
st, r = rest('GET', 'email_optouts?select=user_id', None, A)
ok(st == 200 and isinstance(r, list) and len(r) == 1 and r[0].get('user_id') == uid_a, 'A can see only their own opt-out row')
if B:
    st, r = rest('GET', 'email_optouts?select=user_id', None, B)
    ok(st == 200 and r == [], 'B sees no row for A')
st, r = rpc('set_email_optout', {'p_off': False}, A)
st2, r2 = rest('GET', 'email_optouts?select=user_id', None, A)
ok(st == 200 and r is False and r2 == [], 'A switches them back on and the row goes')
st, r = rpc('set_email_optout', {'p_off': True})
ok(st in (401, 403, 404) or (isinstance(r, dict) and r.get('code') in ('42501', 'PGRST202', 'PGRST301')), 'with no account it is refused (%s)' % st)

# --- v149: every privileged function, called by the wrong person -------------------------------------------------------
# The grants matrix. Anything not deliberately exposed must refuse an anonymous caller, and the internal ones must also
# refuse a signed-in person. "Refused" is 401/403, 42501, or the function not being callable at all (PGRST202 with the
# right argument names means PostgREST has hidden it from this role).
def refused(st, r):
    return st in (401, 403, 404) or (isinstance(r, dict) and r.get('code') in ('42501', 'PGRST202', 'PGRST301', '28000'))
SERVICE_ONLY = {
    'assistant_take': {'p_user': uid_a, 'p_limit': 5}, 'claim_due_reminders': {'p_limit': 1}, 'claim_helper_invites': {'p_limit': 1},
    'doc_move_done': {'p_id': 1}, 'doc_moves_pending': {'p_limit': 1}, 'my_inbound_address': {}, 'originals_orphans': {'p_limit': 1},
    'originals_under': {'p_uid': uid_a}, 'pilot_events_cap': {}, 'push_vapid_init': {'p_jwk': '{}'}, 'reminders_cap': {},
    'reminder_delivery_event': {'p_provider_id': 'x', 'p_event': 'email.delivered', 'p_at': '2026-01-01T00:00:00Z', 'p_detail': None},
    'shares_drop_helper': {}, 'sorted_kick_moves': {}, 'sorted_kick_originals': {}, 'sorted_kick_reminders': {}, 'sorted_secret': {'p_name': 'sorted_cron_secret'},
}
SIGNED_IN_ONLY = {
    'case_reply_address': {'p_task_id': tid}, 'claim_carry': {'p_token': 'x' * 32, 'p_pairs': []}, 'company_scores': {}, 'delete_my_account': None,
    'drop_outcome': {'p_promise': 'p1'}, 'email_reminders_ready': {}, 'inbound_address_new': None, 'invite_helper': {'p_task_id': tid, 'p_email': 'x@example.com', 'p_name': 'X'},
    'is_pilot_admin': {}, 'my_inbound_address_get': {}, 'pilot_health': {}, 'pilot_metrics': {'include_admins': False}, 'push_drop': {'p_endpoint': 'https://push.example/x'},
    'push_save': {'p_endpoint': 'https://push.example/x', 'p_p256dh': 'x', 'p_auth': 'x'}, 'push_state': {'p_endpoint': 'https://push.example/x'},
    'record_outcome': {'p_promise': 'p9', 'p_party': 'Sky', 'p_outcome': 'kept', 'p_via': ''}, 'remove_helper': {'p_task_id': tid}, 'set_email_optout': {'p_off': True},
    'stash_carry': None, 'touch_seen': {},
}
for fn, args in SERVICE_ONLY.items():
    st, r = rpc(fn, args); ok(refused(st, r), 'anonymous cannot call %s (%s)' % (fn, st))
    st, r = rpc(fn, args, A); ok(refused(st, r), 'a signed-in person cannot call %s (%s)' % (fn, st))
for fn, args in SIGNED_IN_ONLY.items():
    if args is None: args = {}   # never run the real thing anonymously by accident: an anonymous call must be refused anyway
    st, r = rpc(fn, args); ok(refused(st, r), 'anonymous cannot call %s (%s)' % (fn, st))
# --- v149: B tries A's things by id ------------------------------------------------------------------------------------
if B:
    st, r = rpc('case_reply_address', {'p_task_id': tid}, B)
    ok(st >= 400 or not r, 'B gets no reply address for A’s case (%s %s)' % (st, str(r)[:60]))
    st, r = rpc('invite_helper', {'p_task_id': tid, 'p_email': 'helper@example.com', 'p_name': 'H'}, B)
    ok(st >= 400 or r in (False, None) or (isinstance(r, dict) and not r.get('ok')), 'B cannot invite a helper to A’s case (%s %s)' % (st, str(r)[:60]))
    ep = 'https://push.example/' + uuid.uuid4().hex
    st, r = rpc('push_save', {'p_endpoint': ep, 'p_p256dh': 'k', 'p_auth': 'a'}, A)
    ok(st in (200, 204), 'A saves a push address (%s)' % st)
    rpc('push_drop', {'p_endpoint': ep}, B)
    st, r = rpc('push_state', {'p_endpoint': ep}, A)
    ok(st == 200 and r not in (False, None, 'off'), 'B dropping A’s push address changes nothing for A (%s %s)' % (st, str(r)[:40]))
    st, r = rpc('push_state', {'p_endpoint': ep}, B)
    ok(st >= 400 or r in (False, None, 'off', 'none') or (isinstance(r, dict) and not r.get('on')), 'B cannot see A’s push address (%s %s)' % (st, str(r)[:40]))
    rpc('push_drop', {'p_endpoint': ep}, A)
    st, r = rest('GET', 'reminders?select=id&task_id=eq.' + tid, None, B)
    ok(st >= 400 or r == [], 'B cannot read A’s reminders (%s)' % st)
    st, r = rest('POST', 'reminders', {'task_id': tid, 'kind': 'before', 'send_at': '2030-01-01T09:00:00Z'}, B)
    ok(st >= 400, 'B cannot add a reminder to A’s case (%s)' % st)
    st, r = rest('PATCH', 'reminders?task_id=eq.' + tid, {'send_at': '2030-01-02T09:00:00Z'}, B, 'return=representation')
    ok(st >= 400 or r == [] or r is None, 'B cannot move A’s reminders (%s)' % st)
    st, r = rpc('claim_carry', {'p_token': uuid.uuid4().hex + uuid.uuid4().hex, 'p_pairs': []}, B)
    ok(st >= 400 or r in (False, None, 0, []), 'a made-up carry token claims nothing (%s %s)' % (st, str(r)[:40]))
    st, r = call('POST', '/storage/v1/object/list/originals', {'prefix': uid_a + '/', 'limit': 10}, B)
    ok(st >= 400 or r == [], 'B cannot list A’s kept documents (%s)' % st)
    st, r = call('POST', '/storage/v1/object/originals/%s/%s/planted.txt' % (uid_a, tid), None, B, {'Content-Type': 'text/plain'})
    ok(st >= 400, 'B cannot put a file in A’s folder (%s)' % st)
    big = case(tid + 'x', 'Big'); big['events'] = [{'at': '2026-01-01T00:00:00Z', 'label': 'x' * 1000}] * 700
    st, r = rest('POST', 'tasks', {'id': tid + 'x', 'data': big}, B)
    ok(st >= 400, 'a case far over the size cap is refused (%s)' % st)
# --- deleting an account removes everything -------------------------------------------------------------------------
st, r = rpc('delete_my_account', {}, A)
ok(st in (200, 204), 'A deletes their account (%s)' % st)
st, r = rest('GET', 'tasks?select=id&id=eq.' + tid, None, A)
ok(st == 401 or (isinstance(r, dict) and r.get('code') in ('PGRST301', '42501')) or r == [], 'A’s token no longer works (%s)' % st)
st, r = rpc('get_share', {'p_token': tok})
ok(st == 200 and r == [], 'nothing of A is left behind a link')
if B:
    st, r = rpc('delete_my_account', {}, B); ok(st in (200, 204), 'B deletes their account')

# --- the real page against the real database, if Playwright is here --------------------------------------------------
try:
    from playwright.sync_api import sync_playwright
    HERE = os.path.abspath('.')
    src = open(HERE + '/public/index.html', encoding='utf-8').read()
    import re
    page = re.sub(r'var SUPA_URL = "[^"]+";', 'var SUPA_URL = "%s";' % URL, src, 1)
    page = re.sub(r'var SUPA_KEY = "[^"]+";', 'var SUPA_KEY = "%s";' % KEY, page, 1)
    ok(page != src, 'the page can be pointed at staging')
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
        ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(body=page, content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
        pg = ctx.new_page(); perr = []; pg.on('pageerror', lambda e: perr.append(str(e)))
        pg.goto('https://sorted.test/#start'); pg.wait_for_timeout(1500)
        if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); pg.wait_for_timeout(2500)
        pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); pg.wait_for_timeout(500)
        pg.fill('#f-case', 'Sky said an engineer would come Tuesday between 8 and 12, ref AB123'); pg.locator('form[data-f=case] button[type=submit]').last.click(); pg.wait_for_timeout(1200)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); pg.wait_for_timeout(1000)
        if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); pg.wait_for_timeout(2500)
        ok('AB123' in pg.inner_text('main'), 'a real case with its promise, saved to staging')
        pg.reload(); pg.wait_for_timeout(3000)
        ok('AB123' in pg.inner_text('main') and 'Waiting' in pg.inner_text('main'), 'a reload brings it back from the database')
        ok(not perr, 'no page errors against the real backend: %s' % perr[:2])
        # tidy up: delete the account from inside the page's own session
        pg.evaluate("sb.rpc('delete_my_account')"); pg.wait_for_timeout(1500)
        b.close()
except ImportError:
    print('note: Playwright not installed, the browser walk was skipped')
except Exception as e:
    errs.append('browser walk: ' + str(e)[:300])

print('CHECKS', n[0]); print('ERRORS', errs); print('FAILS', fails)
sys.exit(1 if fails or errs else 0)
