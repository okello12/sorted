# v114: sign-out never loses work. A change that hasn't reached the server stops sign-out with three choices:
# Wait for saving, Stay signed in, or Discard (naming how many). "Saved to your account" shows only after the server
# confirms a save; before that the case says "Saving…" or "Saved on this phone, not yet sent".
# Covers: nothing pending (straight through), mid-save + Wait, failed save + Stay, offline + Wait + Try again,
# Discard, leaving Account drops the question, and no stored copy is left after any sign-out.
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
SESSION = json.dumps({'user': {'id': 'u-me', 'email': 'me@example.com'}})
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    srv_title = lambda cid: [x for x in cases() if x['id'] == cid][0]['title']
    signed_in = lambda: pg.evaluate("!!localStorage.getItem('__mocksession')")
    cache_left = lambda: [k for k in pg.evaluate("Object.keys(localStorage)") if k.startswith('sorted.cache.') and 'Currys' in (pg.evaluate("localStorage.getItem(%s)" % json.dumps(k)) or '')]
    sync = lambda: pg.inner_text('.case56-title ~ .sync114, main .sync114') if pg.locator('main .sync114').count() else ''
    def sign_in():
        pg.evaluate("localStorage.setItem('__mocksession', %s)" % json.dumps(SESSION)); pg.goto('https://sorted.test/'); wait(pg, 700)
    def open_case(cid): pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600)
    def rename(cid, name):
        open_case(cid); pg.evaluate("document.querySelectorAll('details.case56-more').forEach(d=>d.open=true)")
        pg.click('[data-a=panel][data-p=rename]'); wait(pg, 250); pg.fill('#f-rename', name)
        pg.click('form[data-f=rename] button[type=submit]'); wait(pg, 200)
    def account():
        if not pg.locator('[data-a=data]').count(): pg.goto('https://sorted.test/'); wait(pg, 500)
        pg.locator('[data-a=data]').first.click(); wait(pg, 400)
    def ask_shown(): return pg.locator('.signout114').count() == 1

    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); sign_in()
    if pg.locator('[data-cap82=other]').count(): pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg)
    elif pg.locator('[data-a=compose]').count(): pg.locator('[data-a=compose]').first.evaluate('e=>e.click()'); wait(pg)
    fri = datetime.date.today() + datetime.timedelta(days=(4 - datetime.date.today().weekday()) % 7 or 7)
    pg.fill('#f-case', 'Currys said they would refund £89 by %s, order 445566' % fri.strftime('%A')); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
    for sel in ('[data-a=match-new]',):
        if pg.locator(sel).count(): pg.click(sel); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    cid = cases()[-1]['id']
    open_case(cid)
    ok(sync() == 'Saved to your account', 'a saved case says "Saved to your account" (%r)' % sync())

    # 1 nothing pending: Sign out goes straight through, as before
    account(); ok('Everything is saved to your account.' in pg.inner_text('main'), 'Account says everything is saved')
    pg.click('[data-a=signout]'); wait(pg, 700)
    ok(not signed_in() and not ask_shown() and not cache_left(), 'with nothing pending, Sign out signs out at once and leaves no copy')

    # 2 mid-save: the case says Saving…, sign-out asks, Wait for saving signs out once the save lands
    sign_in(); pg.evaluate("localStorage.setItem('__slowWrites','2500')")
    rename(cid, 'Currys kettle refund')
    ok(sync() == 'Saving…', 'mid-save the case says "Saving…", not "Saved to your account" (%r)' % sync())
    account(); pg.click('[data-a=signout]'); wait(pg, 300)
    m = pg.inner_text('main')
    ok(ask_shown() and signed_in() and '1 case hasn’t reached your account yet' in m, 'sign-out mid-save stops and says 1 case hasn’t reached the account')
    ok(pg.evaluate("document.activeElement && document.activeElement.id") == 'so-h', 'focus moves to the question')
    ok(all(pg.locator('[data-a=%s]' % a).count() == 1 for a in ('signout-wait', 'signout-stay', 'signout-discard')) and 'Discard 1 unsaved case and sign out' in m, 'three choices: Wait for saving, Stay signed in, Discard 1 unsaved case')
    pg.click('[data-a=signout-wait]'); wait(pg, 200)
    ok('Saving now. Sorted signs you out once it’s saved.' in pg.inner_text('main') and signed_in(), 'Wait for saving says what happens and keeps you signed in meanwhile')
    wait(pg, 3200)
    ok(not signed_in() and srv_title(cid) == 'Currys kettle refund' and not cache_left(), 'once the save lands it signs out, the change is on the server and no copy is left')
    pg.evaluate("localStorage.removeItem('__slowWrites')")

    # 3 a failed save: Saved on this phone, not yet sent; Stay signed in keeps everything
    sign_in(); pg.evaluate("localStorage.setItem('__failWrites','1')")
    rename(cid, 'Currys kettle refund, second try'); wait(pg, 300)
    ok(sync().startswith('Saved on this phone, not yet sent.'), 'a save that failed says "Saved on this phone, not yet sent" (%r)' % sync())
    account(); ok('1 case saved on this phone, not yet sent' in pg.inner_text('main'), 'Account counts it')
    pg.click('[data-a=signout]'); wait(pg, 300)
    ok(ask_shown() and 'only on this phone. If you sign out now, it is lost.' in pg.inner_text('main'), 'sign-out asks and says the change would be lost')
    pg.click('[data-a=signout-stay]'); wait(pg, 300)
    ok(not ask_shown() and signed_in() and pg.locator('[data-a=signout]').count() == 1 and pg.evaluate("document.activeElement && document.activeElement.getAttribute('data-a')") == 'signout', 'Stay signed in closes the question, keeps you in and puts focus back on Sign out')
    ok(srv_title(cid) == 'Currys kettle refund' and pg.evaluate("JSON.stringify(Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).map(k=>localStorage.getItem(k)))").count('second try') >= 1, 'the unsent change is still on this phone')

    # 4 offline: Wait for saving can't send, says so, and Try again works once back
    ctx.set_offline(True); pg.click('[data-a=signout]'); wait(pg, 300)
    ok('You’re offline at the moment.' in pg.inner_text('main'), 'offline, the question says so')
    pg.click('[data-a=signout-wait]'); wait(pg, 600)
    m = pg.inner_text('main')
    ok(signed_in() and 'You’re offline, so Sorted can’t send it yet.' in m and pg.locator('[data-a=signout-wait]').inner_text() == 'Try again', 'Wait for saving while offline stays signed in, says why, and offers Try again')
    ctx.set_offline(False); pg.evaluate("localStorage.removeItem('__failWrites')")
    pg.click('[data-a=signout-wait]'); wait(pg, 900)
    ok(not signed_in() and srv_title(cid) == 'Currys kettle refund, second try' and not cache_left(), 'back online, Try again saves and signs out')

    # 5 Discard: says how many, signs out, the server keeps its last saved copy and nothing is left here
    sign_in(); pg.evaluate("localStorage.setItem('__failWrites','1')")
    rename(cid, 'Throw this away'); wait(pg, 300)
    account(); pg.click('[data-a=signout]'); wait(pg, 300)
    pg.click('[data-a=signout-discard]'); wait(pg, 800)
    ok(not signed_in() and srv_title(cid) == 'Currys kettle refund, second try' and not cache_left(), 'Discard signs out, the unsent change is gone and nothing is left on the phone')
    pg.evaluate("localStorage.removeItem('__failWrites')")

    # 6 leaving Account drops the question; nothing signs you out later by surprise
    sign_in(); pg.evaluate("localStorage.setItem('__failWrites','1')")
    rename(cid, 'Pending while I look around'); wait(pg, 300)
    account(); pg.click('[data-a=signout]'); wait(pg, 300); pg.click('[data-a=signout-wait]'); wait(pg, 300)
    pg.locator('header [data-a=home], main [data-a=home]').first.click(); wait(pg, 300)
    pg.evaluate("localStorage.removeItem('__failWrites')"); pg.evaluate("window.dispatchEvent(new Event('online'))"); wait(pg, 800)
    ok(signed_in() and srv_title(cid) == 'Pending while I look around', 'leaving Account cancels the wait: the change saves and you stay signed in')
    account(); ok(not ask_shown() and pg.locator('[data-a=signout]').count() == 1, 'back in Account, Sign out is a plain button again')

    # 7 narrow screen: the question fits at 320px
    pg.evaluate("localStorage.setItem('__failWrites','1')"); rename(cid, 'Narrow'); wait(pg, 300)
    pg.set_viewport_size({'width': 320, 'height': 700}); account(); pg.click('[data-a=signout]'); wait(pg, 300)
    ok(pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth") and all(h >= 44 for h in pg.evaluate("[...document.querySelectorAll('.signout114 button')].map(b=>b.getBoundingClientRect().height)")), 'at 320px the question fits and every button is at least 44px')
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
