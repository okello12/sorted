# v129 (the navigation note). One app shell: every signed-in screen has the bottom bar Home · + New · Cases · More, with
# the current place marked; the top bar is the logo and, on deeper screens, Back. The journeys from the note: open case
# → Home; open case → New (the ways in, focus on the first); Help → New; Account → Home; Moving home → Cases (the move is
# listed); a PCN review → Home keeps the review; start a new case → elsewhere → back: the draft survives; a repair
# question → Home → back to the case where it was; browser Back leaves an understandable screen; a refresh keeps you on
# the same case, Cases or More; 200% text and 320px keep the bar reachable; the bar never hides the last control.
# Cases: search, counts, every case. "<Who> said they would Nothing" is never shown. The guest note is one compact card.
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
fri = datetime.date.today() + datetime.timedelta(days=(4 - datetime.date.today().weekday()) % 7 or 7)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    main = lambda: pg.inner_text('main')
    bar = lambda: pg.locator('.tab129')
    cur = lambda: (pg.locator('.tab129 [aria-current=page] .tab129-l').inner_text() if pg.locator('.tab129 [aria-current=page]').count() else '')
    tap = lambda a: (pg.locator('.tab129 [data-a=%s]' % a).click(), wait(pg, 500))
    def start(text):
        tap('new-case')
        pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
        if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
        return cases()[-1]['id']
    # signed out: no app bar
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.goto('https://sorted.test/'); wait(pg, 600)
    ok(bar().count() == 0, 'the public site has no app bar')
    pg.goto('https://sorted.test/#start'); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    ok(bar().count() == 1 and [x.strip() for x in pg.locator('.tab129 .tab129-l').all_inner_texts()] == ['Home', 'New', 'Cases', 'More'] and cur() == 'Home', 'signed in: the bar reads Home · New · Cases · More, with Home marked')
    ok(pg.locator('.bar .navq').count() == 0, 'the top bar no longer carries Help and Account')
    # ---- cases to work with ----
    c1 = start('Currys said they would refund £89 by %s, order 445566' % fri.strftime('%A'))
    c2 = start('My washing machine stopped draining')
    # ---- open case → Home ----
    pg.goto('https://sorted.test/?task=%s' % c1); wait(pg, 600)
    ok(bar().count() == 1 and cur() == 'Cases' and pg.locator('.bar [data-a=home]').count() >= 1, 'a case shows the bar (Cases marked) and a way back')
    tap('go-home'); ok(pg.locator('main.home44').count() == 1 and cur() == 'Home', 'case → Home')
    # ---- open case → New ----
    pg.goto('https://sorted.test/?task=%s' % c1); wait(pg, 600); tap('new-case')
    ok(pg.locator('main.home44').count() == 1 and pg.locator('#cap82-start').is_visible() and pg.evaluate("document.activeElement&&document.activeElement.classList.contains('cap82-card')"), 'case → New: the ways in, with focus on the first')
    # ---- Help → New, Account → Home ----
    tap('data'); ok(cur() == 'More' and pg.locator('main h1').inner_text() == 'Account', 'More opens Account, Settings and Help')
    ok('How Sorted works, privacy, terms and contact are in' in main(), 'More points to How it works, privacy, terms and contact')
    pg.click('.acct112-nav [data-v=help]'); wait(pg, 400); tap('new-case')
    ok(pg.locator('#cap82-start').is_visible(), 'Help → New')
    tap('data'); tap('go-home'); ok(pg.locator('main.home44').count() == 1, 'Account → Home')
    # ---- Cases: search, counts, every case ----
    tap('cases'); m = main()
    ok(pg.locator('main h1').inner_text() == 'Cases' and 'Needs you' in m and 'Waiting' in m and pg.locator('.cases129 .pick125').count() == 2, 'Cases lists every case with the counts')
    pg.fill('#pick-q', 'currys'); wait(pg, 200)
    ok(len([x for x in pg.locator('.cases129 .pick125').all() if x.is_visible()]) == 1, 'Cases search filters as you type')
    pg.fill('#pick-q', '')
    # ---- Moving home → Cases ----
    tap('go-home'); pg.locator('[data-a=mom-start]').first.evaluate('e=>e.click()'); wait(pg, 500)
    if not pg.locator('#mv-date').count(): pg.locator('[data-a=mom-new]').first.evaluate('e=>e.click()'); wait(pg, 400)
    pg.fill('#mv-date', (datetime.date.today() + datetime.timedelta(days=30)).isoformat()); pg.click('form[data-f=mom] button[type=submit]'); wait(pg, 600)
    ok(bar().count() == 1, 'Moving home has the bar')
    tap('cases'); ok('Life moments' in main() and 'Moving home' in main(), 'Moving home → Cases: the move is listed with the cases')
    # ---- start a new case → elsewhere → back: the draft survives ----
    tap('new-case'); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.type('#f-case', 'Royal Mail lost my parcel'); wait(pg, 200)
    tap('cases'); tap('go-home')
    ok('Royal Mail lost my parcel' in main() or (pg.locator('#f-case').count() and 'Royal Mail' in pg.input_value('#f-case')), 'a half-written start survives going to Cases and back')
    # ---- a repair question → Home → back to the case where it was ----
    pg.goto('https://sorted.test/?task=%s' % c2); wait(pg, 600)
    st1 = [c for c in cases() if c['id'] == c2][0]['fix']['step']; f1 = pg.locator('form[data-f=what]').count()
    tap('go-home'); pg.goto('https://sorted.test/?task=%s' % c2); wait(pg, 600)
    ok(f1 == 1 and pg.locator('form[data-f=what]').count() == 1 and [c for c in cases() if c['id'] == c2][0]['fix']['step'] == st1, 'a repair question is where you left it after going Home (%s)' % st1)
    # ---- refresh keeps the place ----
    pg.goto('https://sorted.test/?task=%s' % c1); wait(pg, 600); pg.reload(); wait(pg, 900)
    ok('#case-%s' % c1 in pg.url and pg.locator('main.case56').count() == 1 and cur() == 'Cases', 'a refresh on a case keeps you on the case (%s)' % pg.url[-30:])
    tap('cases'); pg.reload(); wait(pg, 900); ok(pg.locator('main h1').inner_text() == 'Cases', 'a refresh on Cases keeps Cases')
    tap('data'); pg.reload(); wait(pg, 900); ok(cur() == 'More', 'a refresh on More keeps More')
    # ---- browser Back ----
    pg.go_back(); wait(pg, 700)
    ok(pg.locator('main').count() == 1 and (bar().count() == 1 or pg.locator('.hero').count() == 1), 'browser Back leaves an understandable screen')
    # ---- a PCN review → Home keeps the review ----
    pg.goto('https://sorted.test/'); wait(pg, 600); tap('new-case')
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.fill('#f-case', 'PCN'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 500)
    pg.evaluate("(()=>{var b=document.createElement('button');b.setAttribute('data-a','doc-manual');document.querySelector('main').appendChild(b);b.click()})()"); wait(pg, 500)
    ok(pg.locator('.doc125-manual').count() == 1, 'the notice form is open')
    pg.fill('#doc-ref', 'LJ12345678'); tap('go-home')
    ok(pg.locator('.doc125-manual').count() == 1 and pg.input_value('#doc-ref') == 'LJ12345678', 'tapping Home during a notice review keeps the review and what was typed')
    # ---- nothing hidden behind the bar; narrow and large text ----
    pg.goto('https://sorted.test/?task=%s' % c1); wait(pg, 600)
    pad = pg.evaluate("parseFloat(getComputedStyle(document.body).paddingBottom)"); barh = pg.evaluate("document.querySelector('.tab129').getBoundingClientRect().height")
    ok(pad >= barh, 'the page leaves room under its last control for the bar (%d ≥ %d)' % (pad, barh))
    pg.set_viewport_size({'width': 320, 'height': 640}); pg.evaluate("document.documentElement.style.fontSize='200%'"); wait(pg, 300)
    ok(pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth+1") and all(pg.locator('.tab129 [data-a=%s]' % a).is_visible() for a in ('go-home', 'new-case', 'cases', 'data')), 'at 320px and 200% text the bar fits and every item is reachable')
    pg.evaluate("document.documentElement.style.fontSize=''"); pg.set_viewport_size({'width': 390, 'height': 844})
    # ---- "said they would Nothing" ----
    pg.goto('https://sorted.test/'); wait(pg, 500); tap('new-case')
    pg.locator('[data-cap82=promise]').first.evaluate('e=>e.click()'); wait(pg, 400)
    pg.fill('#gi-who', 'Evri'); pg.fill('#gi-what', 'Nothing'); pg.click('form[data-f=gi] button[type=submit]'); wait(pg, 700)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    pg.goto('https://sorted.test/'); wait(pg, 600); tap('cases')
    ok('said they would Nothing' not in main() and 'said they would nothing' not in main().lower() and 'Evri' in main(), '“Evri said they would Nothing” is never shown')
    # ---- the guest note ----
    pg.goto('https://sorted.test/'); wait(pg, 600)
    ok(pg.locator('.anon129').count() == 1 and pg.locator('.anon129').bounding_box()['height'] < 150, 'the guest note is one compact card')
    ok(not errs, 'no page errors: %s' % errs)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
