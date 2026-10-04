# v101: "The screen is broken" keeps the thing named: the first response says "Your screen isn't working" and the
# repair step's "What is it?" is filled in. A start choice made on the landing page opens its own questions after
# sign-in, and is forgotten once a case starts.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
def rows(pg): return [x['data'] for x in (pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')||'{}')") or {}).get('tasks', [])]
def newest(pg): return sorted(rows(pg), key=lambda x: x.get('created') or '')[-1]
def baseline(pg):
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 550)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London', color_scheme='dark')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    # 1 a choice on the landing page carries through sign-in to its own questions
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 700)
    pg.click('#browse126 > summary'); wait(pg, 150); pg.locator('#cap82-landing [data-cap82=fix]').first.click(); wait(pg, 900)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 900)
    ok(pg.locator('.gi-form').count() == 1 and pg.locator('input[name=gi-item]').count() == 4, '"Something’s broken" on the landing page opens the broken questions after sign-in')
    # 2 the screen: kept, said back, filled in
    pg.click('label.gi-chip:has-text("Something else")'); pg.fill('#gi-what', 'The screen is broken')
    pg.click('form[data-f=gi] button[type=submit]'); wait(pg, 600); baseline(pg)
    t = newest(pg)
    ok(t.get('fix', {}).get('item') == 'Screen', 'the case knows it is the screen: %s' % t.get('fix', {}).get('item'))
    f = pg.inner_text('.fr-card') if pg.locator('.fr-card').count() else ''
    ok('Your screen isn’t working.' in f and 'Something isn’t working' not in f, 'the first response says "Your screen isn’t working"')
    ok(pg.input_value('#f-item') == 'Screen' if pg.locator('#f-item').count() else False, '"What is it?" is filled in with Screen')
    ok('burning, smoking or sparking' in pg.inner_text('main'), 'the safety question is still asked')
    # 3 once a case has started, Home does not reopen the broken questions
    pg.goto('https://sorted.test/'); wait(pg, 700)
    ok(pg.locator('.gi-form').count() == 0 and pg.evaluate("sessionStorage.getItem('sorted.cap82')") is None, 'after starting a case, Home is Home, not the broken questions again')
    # a reload in the middle of a start restores saved work only, not the half-done questions
    pg.locator('#cap82-start [data-cap82=fix]').first.click(); wait(pg, 500)
    ok(pg.locator('.gi-form').count() == 1, 'choosing broken opens its questions')
    pg.reload(); wait(pg, 800)
    ok(pg.locator('.gi-form').count() == 0 and 'What’s broken?' not in pg.inner_text('main'), 'after a reload they are gone, with no leftover heading')
    # 4 other wordings, straight through the reader (tests/out/reader.html)
    r = ctx.new_page(); r.route(lambda u: u.startswith('https://sorted.test/'), lambda q: q.fulfill(path=HERE + '/tests/out/reader.html', content_type='text/html'))
    r.goto('https://sorted.test/'); wait(r, 500)
    for text, want in [('The screen is broken', 'Screen'), ('My fridge door won’t close', 'Fridge door'), ('The front door lock is broken', 'Front door lock'), ('My laptop has stopped charging', 'Laptop'), ('The light in the bathroom isn’t working', ''), ('The landlord hasn’t fixed it', ''), ('My order hasn’t arrived', '')]:
        got = r.evaluate("(x)=>window.__read.thingOf(x)", text)
        ok(got == want, '"%s" names: %r' % (text, got))
    r.close()
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'nothing scrolls sideways')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
