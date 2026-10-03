# v94: only a name ("From hmrc", "Letter from the council"). Sorted asks what they sent before starting. If you carry
# on, the case is named after them, the first response says what Sorted doesn't know, and the message asks what it's about.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
def db(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {'tasks': []}
def newest(pg): return sorted([x['data'] for x in db(pg)['tasks']], key=lambda x: x.get('created') or '')[-1]
def box(pg):
    pg.goto('https://sorted.test/'); wait(pg, 600)
    if pg.locator('[data-a=gi-back]').count(): pg.click('[data-a=gi-back]'); wait(pg)
    if pg.locator('[data-cap82=other]').first.is_visible(): pg.locator('[data-cap82=other]').first.click(); wait(pg)
    elif pg.locator('[data-a=compose]').count(): pg.locator('[data-a=compose]').first.click(); wait(pg)
def submit(pg, text): pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg)
def baseline(pg):
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count():
        pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 550)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    # 1 a name alone asks what they sent, with a photo button, and creates nothing
    box(pg); submit(pg, 'From hmrc')
    m = pg.inner_text('main')
    ok(pg.locator('.ps-short').count() == 1 and 'Something from HMRC.' in m and pg.locator('.ps-short input[type=file]').count() == 1, '"From hmrc" asks what HMRC sent, with a photo button')
    ok(pg.locator('form[data-f=case] button[type=submit]').count() == 1, 'and one Start button')
    ok(db(pg)['tasks'] == [], 'nothing is created yet')
    # 2 adding a few words carries on normally
    submit(pg, 'HMRC says I owe £300 tax by 31 January')
    ok(pg.locator('.ps-short').count() == 0, 'with a few more words it carries on')
    baseline(pg)
    ok('HMRC' in newest(pg)['title'], 'an HMRC case: %s' % newest(pg)['title'])
    # 3 press Start again without adding anything: named after them, honest about what it doesn't know, a message that asks
    box(pg); submit(pg, 'From hmrc'); pg.click('.ps-short button[type=submit]'); wait(pg); baseline(pg)
    t = newest(pg); f = pg.inner_text('.fr-card') if pg.locator('.fr-card').count() else ''
    ok(t['title'] == 'HMRC', 'the case is called HMRC, not "From hmrc": %s' % t['title'])
    ok('Sorted doesn’t know yet what it’s about' in f and 'Add what they sent' in f, 'the first response says what Sorted doesn’t know')
    ask = pg.input_value('#f-ask') if pg.locator('#f-ask').count() else ''
    ok(ask.startswith('I’m getting in touch about my case with you.') and 'what it’s about' in ask and 'from hmrc' not in ask.lower(), 'the message asks what it is about: %s' % ask)
    # 4 a letter from the council
    box(pg); submit(pg, 'Got a letter from the council')
    ok('Something from the council.' in pg.inner_text('main') and '“The council wants' in pg.inner_text('main'), 'the council, in plain words')
    pg.click('.ps-short button[type=submit]'); wait(pg); baseline(pg)
    t = newest(pg); ask = pg.input_value('#f-ask') if pg.locator('#f-ask').count() else ''
    ok(t['title'] == 'Council letter' and 'a letter I had from you' in ask, 'named "Council letter", and the message is about the letter: %s' % t['title'])
    # 5 a real sentence is untouched
    box(pg); submit(pg, 'Currys refund hasn’t arrived')
    ok(pg.locator('.ps-short').count() == 0, 'a sentence with more in it is never asked again')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'nothing scrolls sideways')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
