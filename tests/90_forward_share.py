# v134: forwarding to a secret address per person, and Android's share sheet. Settings shows your Sorted address
# with Copy and "Get a new address"; an email that arrives there shows on Home as a suggestion naming the website it
# came from, and goes into the case you choose; sharing from another app (/?st=…&sx=…) brings the words in with the
# "Where does this go?" picker; the manifest has icons and the share target; the privacy notice describes forwarding
# and lock-screen reminders. It also runs tests/fn/inbound_check.mjs (inbound-email run in Node).
import os, sys, json, datetime, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
today = datetime.date.today()
fri = today + datetime.timedelta(days=(4 - today.weekday()) % 7 or 7)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    ctx.grant_permissions(['clipboard-read', 'clipboard-write'], origin='https://sorted.test')
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    main = lambda: pg.inner_text('main')
    tap = lambda a: (pg.locator('.tab129 [data-a=%s]' % a).click(), wait(pg, 500))
    def start(text):
        tap('new-case')
        pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
        return cases()[-1]['id']
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1');localStorage.setItem('__inbound','1')")
    pg.goto('https://sorted.test/#start'); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    c1 = start('Currys said they would refund £89 by %s, order 445566' % fri.strftime('%A'))
    # ---- v141: forwarding ready but no address yet: Settings offers one, nothing is made on page load ----
    pg.evaluate("localStorage.setItem('__inbound','ready')"); pg.goto('https://sorted.test/'); wait(pg, 700)
    tap('data'); pg.click('.acct112-nav [data-v=acct-settings]'); wait(pg, 400)
    ok(pg.locator('.fwd134 [data-a=fwd-new]').count() == 1 and 'Get my Sorted address' in pg.inner_text('.fwd134') and pg.locator('#fwd-addr').count() == 0 and not pg.evaluate("localStorage.getItem('__inboundN')"), 'with no address yet, Settings offers “Get my Sorted address” and nothing is made on load')
    pg.locator('.fwd134 [data-a=fwd-new]').click(); wait(pg, 400)
    ok(pg.locator('#fwd-addr').count() == 1 and pg.input_value('#fwd-addr').startswith('log-new') and 'Your Sorted address is ready.' in (pg.inner_text('#toast') or ''), 'tapping it makes the address and says so')
    pg.evaluate("localStorage.setItem('__inbound','1');localStorage.removeItem('__inboundN')"); pg.goto('https://sorted.test/'); wait(pg, 700)
    # ---- the address in Settings ----
    tap('data'); pg.click('.acct112-nav [data-v=acct-settings]'); wait(pg, 400)
    fb = pg.locator('.fwd134')
    ok(fb.count() == 1 and pg.input_value('#fwd-addr').startswith('log-') and 'arrives on Home as a suggestion' in fb.inner_text() and 'Anyone who has the address can send to it' in fb.inner_text(), 'Settings shows your Sorted address and says what happens to what arrives')
    fb.locator('[data-a=fwd-copy]').click(); wait(pg, 300)
    ok(pg.evaluate('navigator.clipboard.readText()') == pg.input_value('#fwd-addr'), 'Copy the address copies it')
    old = pg.input_value('#fwd-addr'); fb.locator('[data-a=fwd-new]').click(); wait(pg, 400)
    ok(pg.input_value('#fwd-addr') != old and pg.input_value('#fwd-addr').startswith('log-new'), 'Get a new address replaces it')
    # ---- an email arrives: a suggestion on Home, then into the case ----
    uid = pg.evaluate("JSON.parse(localStorage.getItem('__mocksession')).user.id")
    pg.evaluate("(u)=>{var db=JSON.parse(localStorage.getItem('__mockdb'));db.inbound_items=db.inbound_items||[];db.inbound_items.push({id:'in1',user_id:u,subject:'Your refund',body:'Your refund will be paid by %s. Ref ZX123456.',received_at:new Date().toISOString(),used_at:null,from_domain:'currys.co.uk'});localStorage.setItem('__mockdb',JSON.stringify(db))}" % fri.strftime('%A'), uid)
    pg.goto('https://sorted.test/'); wait(pg, 800)
    m = main()
    ok('An email came to your Sorted address from currys.co.uk' in m and 'You forwarded' not in m, 'a forwarded email shows on Home as a suggestion naming the website it came from')
    btn = pg.locator('[data-a=inbox-add], [data-a=inbound]').first
    ok(btn.count() == 1, 'with a way to put it in a case')
    btn.click(); wait(pg, 600)
    if pg.locator('main.case56').count() == 0 and pg.locator('[data-a=inbound-pick], .pick125').count():
        pg.locator('.pick125').first.click(); wait(pg, 600)
    ok(pg.locator('.inbox-q').count() == 0 or 'An email came to your Sorted address' not in (main() if pg.locator('main.home44').count() else ''), 'once handled, it leaves Home')
    # ---- sharing from another app (Android) ----
    pg.goto('https://sorted.test/?st=Evri&sx=Your+parcel+will+arrive+by+%s&su=https%%3A%%2F%%2Fevri.com%%2Ftrack%%2FH01' % fri.strftime('%A')); wait(pg, 900)
    m = main() + (pg.input_value('#f-case') if pg.locator('#f-case').count() else '')
    ok('Your parcel will arrive by' in m and 'evri.com/track/H01' in m and 'Shared into Sorted' in m and 'st=' not in pg.url, 'words shared from another app arrive in Sorted, and the address is cleaned up')
    # ---- the manifest, icons and the notice ----
    mf = json.load(open(HERE + '/public/manifest.webmanifest'))
    ok(mf.get('share_target', {}).get('params') == {'title': 'st', 'text': 'sx', 'url': 'su'} and all(os.path.exists(HERE + '/public' + i['src']) for i in mf.get('icons', [])) and len(mf['icons']) >= 2, 'the manifest has the share target and its icons exist')
    src = open(HERE + '/public/index.html').read()
    ok('<link rel="apple-touch-icon" href="/icon-180.png">' in src and os.path.exists(HERE + '/public/icon-180.png'), 'an iPhone Home Screen icon')
    pv = src
    ok('forward emails to your own Sorted address' in pv and 'Forwarding other emails into Sorted is switched off' not in pv and 'notification address' in pv and 'doesn’t say what the case is' in pv, 'the privacy notice describes forwarding and lock-screen reminders')
    r = subprocess.run(['node', '--experimental-strip-types', HERE + '/tests/fn/inbound_check.mjs'], capture_output=True, text=True)
    ok('FAILS []' in r.stdout and r.stdout.count('PASS') == 8, 'inbound-email, run in Node: the secret address, nothing trusted, unknown addresses dropped, a daily limit (%d passes)' % r.stdout.count('PASS'))
    ok(not errs, 'no page errors: %s' % errs)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
