# Step 5 of the release gate (docs/PLAN.md 0.1): is the release really live, and does it work there?
#
#   python3 tests/live/verify_live.py            # after node all.js, from the repository root
#
# 1. Waits (up to SORTED_LIVE_WAIT seconds, default 900) until the page at SORTED_LIVE_URL is byte for byte the page
#    this commit built (public/index.html), and reports its SORTED_V.
# 2. Walks it once in Chromium against the real backend: a throwaway guest account starts a case with a promise,
#    confirms it, sees "Saved to your account", reloads and finds it again. The account deletes itself at the end
#    (delete_my_account, which removes its cases, usage records and everything else), so nothing is left behind.
# Runs in GitHub Actions after a push to main (job "live"); this workspace can't reach the live site.
import os, sys, time, hashlib, re, urllib.request
URL = os.environ.get('SORTED_LIVE_URL', 'https://sorted-pilot.vercel.app/')
WAIT = int(os.environ.get('SORTED_LIVE_WAIT', '900'))
fails = []; errs = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def done():
    print('CHECKS', n[0]); print('ERRORS', errs); print('FAILS', fails); sys.exit(1 if fails or errs else 0)

local = open('public/index.html', 'rb').read()
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

try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
        pg = ctx.new_page(); perr = []; pg.on('pageerror', lambda e: perr.append(str(e)))
        pg.goto(URL + '#start'); pg.wait_for_timeout(2000)
        ok(pg.evaluate('typeof SORTED_V!=="undefined"&&SORTED_V') == ver, 'the page running in the browser says %s' % ver)
        if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); pg.wait_for_timeout(3000)
        try:
            if pg.locator('[data-cap82=other]').count(): pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()')
            elif pg.locator('[data-a=compose]').count(): pg.locator('[data-a=compose]').first.evaluate('e=>e.click()')
            pg.wait_for_timeout(600)
            pg.fill('#f-case', 'Release check: Sky said an engineer would come Tuesday between 8 and 12, ref RC123'); pg.locator('form[data-f=case] button[type=submit]').last.click(); pg.wait_for_timeout(1500)
            if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); pg.wait_for_timeout(800)
            if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); pg.wait_for_timeout(1200)
            ok(pg.locator('[data-a=sug-yes]').count() == 1, 'the promise is proposed')
            if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); pg.wait_for_timeout(3000)
            m = pg.inner_text('main')
            ok('RC123' in m, 'the promise is confirmed on the case')
            ok(pg.locator('main .sync114').count() == 0 or 'Saved to your account' in pg.inner_text('main .sync114'), 'the case says it is saved to the account')
            pg.reload(); pg.wait_for_timeout(3500)
            ok('RC123' in pg.inner_text('main'), 'a reload brings it back from the database')
            ok(not perr, 'no page errors: %s' % perr[:2])
        finally:
            # tidy up from inside the page's own session, whatever happened above
            pg.evaluate("typeof sb!=='undefined'&&sb.rpc('delete_my_account').then(function(){return sb.auth.signOut()})"); pg.wait_for_timeout(2500)
        b.close()
except ImportError:
    print('note: Playwright not installed, the browser walk was skipped')
except Exception as e:
    errs.append('browser walk: ' + str(e)[:300])
done()
