# Step 5 of the release gate (docs/PLAN.md 0.1): is the release really live, and does it work there?
#
#   python3 tests/live/verify_live.py            # after node all.js, from the repository root
#   python3 tests/live/verify_live.py --cleanup  # delete a guest account a cut-short run left behind (see below)
#
# 1. Waits (up to SORTED_LIVE_WAIT seconds, default 900) until the page at SORTED_LIVE_URL is byte for byte the page
#    this commit built (public/index.html), and reports its SORTED_V.
# 2. Walks it once in Chromium against the real backend as a throwaway guest: starts a case with a promise, confirms
#    it, requires "Saved to Sorted" (a guest; v140), checks the case on the server with the guest's own session (not the page),
#    clears the page's local copy and reloads so the case must come back from the database, then deletes the account
#    through Account > Delete my account and cases and proves it is gone: the session no longer belongs to a user and
#    the case can no longer be read with it.
# 3. The guest's session is kept in a file (SORTED_LIVE_SESSION, default tests/out/live-session.json; never printed)
#    from sign-in until the deletion is proven, then removed. If a run is cut short, `--cleanup` reads that file,
#    deletes the account with the server function and proves it the same way; CI runs it in a step that always runs.
# The only credential used is the publishable key the page itself ships with.
import os, sys, time, json, hashlib, re, urllib.request, urllib.error
URL = os.environ.get('SORTED_LIVE_URL', 'https://sorted-pilot.vercel.app/')
WAIT = int(os.environ.get('SORTED_LIVE_WAIT', '900'))
SESSION_FILE = os.environ.get('SORTED_LIVE_SESSION', os.path.join('tests', 'out', 'live-session.json'))
fails = []; errs = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def done():
    print('CHECKS', n[0]); print('ERRORS', errs); print('FAILS', fails)
    if os.environ.get('GITHUB_ACTIONS'):
        for m in (fails + errs)[:8]: print('::error title=live::%s' % m.replace('\n', ' ')[:900])
        if not fails and not errs: print('::notice title=live::%d checks passed on %s' % (n[0], URL))
    sys.exit(1 if fails or errs else 0)

local = open('public/index.html', 'rb').read()
SUPA_URL = re.search(rb'var SUPA_URL = "([^"]+)"', local).group(1).decode()
SUPA_KEY = re.search(rb'var SUPA_KEY = "([^"]+)"', local).group(1).decode()

def call(method, path, body=None, token=None):
    h = {'apikey': SUPA_KEY, 'Authorization': 'Bearer ' + (token or SUPA_KEY), 'Content-Type': 'application/json'}
    req = urllib.request.Request(SUPA_URL + path, data=json.dumps(body).encode() if body is not None else None, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode(); return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try: return e.code, json.loads(raw)
        except Exception: return e.code, raw

def account_gone(token, case_id):
    """True only if the server no longer knows the user behind this session, and the case can't be read with it."""
    st_u, _ = call('GET', '/auth/v1/user', token=token)
    st_t, rows = call('GET', '/rest/v1/tasks?select=id&id=eq.' + case_id, token=token)
    return st_u != 200 and (st_t != 200 or not rows), 'user %s, case read %s %s' % (st_u, st_t, (len(rows) if isinstance(rows, list) else '-'))

def session_write(sess):
    os.makedirs(os.path.dirname(SESSION_FILE) or '.', exist_ok=True)
    with open(SESSION_FILE, 'w') as f: json.dump(sess, f)
def session_drop():
    try: os.remove(SESSION_FILE)
    except FileNotFoundError: pass

if '--cleanup' in sys.argv:
    if not os.path.exists(SESSION_FILE):
        print('cleanup: no guest session left behind'); done()
    sess = json.load(open(SESSION_FILE)); tok = sess.get('access_token'); cid = sess.get('case_id', 'none')
    if sess.get('refresh_token'):
        st, r = call('POST', '/auth/v1/token?grant_type=refresh_token', {'refresh_token': sess['refresh_token']})
        if st == 200 and isinstance(r, dict) and r.get('access_token'): tok = r['access_token']
    gone, why = account_gone(tok, cid)
    if gone:
        ok(True, 'cleanup: the guest from the cut-short run was already gone (%s)' % why); session_drop(); done()
    st, r = call('POST', '/rest/v1/rpc/delete_my_account', {}, token=tok)
    gone, why = account_gone(tok, cid)
    ok(gone, 'cleanup: the guest account from a cut-short run is deleted (rpc %s; %s)' % (st, why))
    if gone: session_drop()
    done()

want = hashlib.sha1(local).hexdigest()
ver = (re.search(rb'var SORTED_V="([^"]+)"', local) or [None, b'?'])[1].decode()
t0 = time.time(); got = None; live = b''
while time.time() - t0 < WAIT:
    try:
        req = urllib.request.Request(URL + ('&' if '?' in URL else '?') + 'v=' + str(int(time.time())), headers={'Cache-Control': 'no-cache'})
        live = urllib.request.urlopen(req, timeout=30).read(); got = hashlib.sha1(live).hexdigest()
        if got == want: break
    except Exception as e:
        print('waiting: %s' % str(e)[:120])
    time.sleep(20)
live_v = (re.search(rb'var SORTED_V="([^"]+)"', live) or [None, b'?'])[1].decode()
ok(got == want, 'the live page is this build (%s, %s); live has %s, %s, after %.0fs' % (ver, want[:12], live_v, (got or '-')[:12], time.time() - t0))
if got != want: done()

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    pg = ctx.new_page(); perr = []; pg.on('pageerror', lambda e: perr.append(str(e)))
    tok = None; cid = None
    try:
        pg.goto(URL + '#start'); pg.wait_for_timeout(2000)
        ok(('var SORTED_V="%s"' % ver) in pg.content(), 'the page in the browser is %s' % ver)
        if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); pg.wait_for_timeout(3000)
        sess = pg.evaluate("(()=>{var k=Object.keys(localStorage).find(function(k){return /^sb-.*-auth-token$/.test(k)});if(!k)return null;try{var s=JSON.parse(localStorage.getItem(k));return {access_token:s.access_token,refresh_token:s.refresh_token,uid:s.user&&s.user.id}}catch(e){return null}})()")
        ok(bool(sess and sess.get('access_token')), 'a guest account was created for the walk')
        if sess:
            tok = sess['access_token']; session_write(sess)
        if pg.locator('[data-cap82=other]').count(): pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()')
        elif pg.locator('[data-a=compose]').count(): pg.locator('[data-a=compose]').first.evaluate('e=>e.click()')
        pg.wait_for_timeout(600)
        pg.fill('#f-case', 'Release check: Sky said an engineer would come Tuesday between 8 and 12, ref RC123'); pg.locator('form[data-f=case] button[type=submit]').last.click(); pg.wait_for_timeout(1500)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); pg.wait_for_timeout(800)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); pg.wait_for_timeout(1200)
        ok(pg.locator('[data-a=sug-yes]').count() == 1, 'the promise is proposed')
        if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]')
        try: pg.locator('main .sync114', has_text='Saved to Sorted').first.wait_for(timeout=15000)
        except Exception: pass
        ok('RC123' in pg.inner_text('main'), 'the promise is confirmed on the case')
        ok(pg.locator('main .sync114').count() == 1 and pg.inner_text('main .sync114') == 'Saved to Sorted. You can reopen this case on this browser. Add an email to open it on another device.', 'the guest case says "Saved to Sorted" (%r)' % (pg.inner_text('main .sync114') if pg.locator('main .sync114').count() else ''))
        cid = pg.evaluate("(()=>{var k=Object.keys(localStorage).find(function(k){return k.indexOf('sorted.cache.')===0});try{var v=JSON.parse(localStorage.getItem(k)||'[]');var t=v.filter(function(x){return x&&x.kind!=='moment'})[0];return t&&t.id}catch(e){return null}})()")
        ok(bool(cid), 'the case has an id')
        if sess and cid:
            sess['case_id'] = cid; session_write(sess)
            st, rows = call('GET', '/rest/v1/tasks?select=id&id=eq.' + cid, token=tok)
            ok(st == 200 and isinstance(rows, list) and len(rows) == 1, 'the server holds the case for this guest (%s, %s rows)' % (st, len(rows) if isinstance(rows, list) else '-'))
        # the local copy goes, so the reload must come back from the database
        pg.evaluate("Object.keys(localStorage).filter(function(k){return k.indexOf('sorted.cache.')===0}).forEach(function(k){localStorage.removeItem(k)})")
        pg.reload(); pg.wait_for_timeout(3500)
        ok('RC123' in pg.inner_text('main'), 'with the local copy cleared, a reload brings the case back from the database')
        ok(not perr, 'no page errors: %s' % perr[:2])
    except Exception as e:
        errs.append('walk: ' + str(e)[:300])
    finally:
        # tidy up the way a person would, whatever happened above: Account > Delete my account and cases
        try:
            pg.goto(URL); pg.wait_for_timeout(2500)
            pg.locator('[data-a=data]').first.click(); pg.wait_for_timeout(800)
            pg.locator('[data-a=wipe-ask]').first.click(); pg.wait_for_timeout(500)
            pg.locator('[data-a=wipe]').first.click(); pg.wait_for_timeout(4000)
            ok(not pg.evaluate("Object.keys(localStorage).some(function(k){return /^sb-.*-auth-token$/.test(k)})"), 'the page signed the guest out after deleting')
        except Exception as e:
            errs.append('tidy up: ' + str(e)[:200])
        if tok:
            gone, why = account_gone(tok, cid or 'none')
            ok(gone, 'the guest account and its case are gone from the server (%s)' % why)
            if gone: session_drop()
            else: print('the guest session file is kept for --cleanup')
        else:
            errs.append('no guest session was captured, so nothing could be checked or cleaned up')
    b.close()
done()
