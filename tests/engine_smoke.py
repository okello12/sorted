# A short walk through Sorted in whichever browser engine SORTED_ENGINE names (chromium, webkit or firefox), so a
# Safari-only or Firefox-only break shows up in CI. Not part of run.sh: GitHub runs it on all three engines; here it
# runs on Chromium. The walk: first visit, a case with a promise, Home, Back, Moving home with a tracked case, a shared
# move, a correction, a reload, dark mode. No page errors and nothing scrolling sideways at any step.
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
ENGINE = os.environ.get('SORTED_ENGINE', 'chromium')
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + ENGINE + ': ' + m)
    if not c: fails.append(ENGINE + ': ' + m)
def wait(pg, ms=500): pg.wait_for_timeout(ms)
def fits(pg): return pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth+1")
with sync_playwright() as p:
    b = getattr(p, ENGINE).launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: [x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment']
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 800)
    ok(pg.locator('#cap82-start .cap82-card').count() == 6 and fits(pg), 'the first visit shows the six doors and fits')
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg)
    pg.fill('#f-case', 'Sky said an engineer would come Tuesday between 8 and 12, ref AB123'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 700)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 700)
    ok(pg.locator('[data-a=sug-yes]').count() == 1 and 'Sky' in pg.inner_text('main') and 'AB123' in pg.inner_text('main'), 'the sentence becomes a promise to confirm')
    pg.click('[data-a=sug-yes]'); wait(pg, 700)
    c = cases(); ok(len(c) == 1 and c[0]['promises'] and c[0]['promises'][0]['status'] == 'open' and c[0]['promises'][0]['ref'] == 'AB123', 'the promise is saved')
    cid = c[0]['id']
    ok('Waiting' in pg.inner_text('main') and fits(pg), 'the case shows Waiting and fits')
    pg.goto('https://sorted.test/'); wait(pg, 700)
    ok(pg.locator('main').count() == 1 and 'Sky' in pg.inner_text('main') and fits(pg), 'Home shows the case')
    pg.go_back(); wait(pg, 700)
    ok(pg.locator('main').count() == 1, 'Back renders a page')
    pg.goto('https://sorted.test/'); wait(pg, 700)
    pg.locator('[data-a=mom-start]').first.evaluate('e=>e.click()'); wait(pg, 600)
    if not pg.locator('#mv-date').count() and pg.locator('[data-a=mom-new]').count(): pg.locator('[data-a=mom-new]').first.evaluate('e=>e.click()'); wait(pg)
    pg.fill('#mv-date', (datetime.date.today() + datetime.timedelta(days=20)).isoformat()); pg.click('label.chip:has(input[name=mv-tenure][value=rent])'); pg.click('label.chip:has(input[name=mv-nation][value=sc])')
    pg.click('form[data-f=mom] button[type=submit]'); wait(pg, 700)
    ok('Moving home' in pg.inner_text('main') and 'Scotland' in pg.inner_text('main') and fits(pg), 'a move in Scotland is saved and fits')
    pg.locator('.cap99-item', has_text='Broadband').first.locator('[data-a=mom-case]').click(); wait(pg)
    pg.fill('#gi-what', 'Virgin will install on Tuesday ref V123'); pg.click('.cap103-said button[type=submit]'); wait(pg, 800)
    ok(len(cases()) == 2 and pg.locator('[data-a=sug-yes]').count() == 1, 'a case from the move, with its promise to confirm')
    pg.click('[data-a=sug-yes]'); wait(pg, 600); pg.click('[data-a=mom-open]'); wait(pg, 600)
    ok('Tracked case' in pg.inner_text('main').replace('TRACKED CASE', 'Tracked case'), 'the move shows the tracked case')
    pg.evaluate("document.querySelector('details.cap104-share').open=true"); pg.click('[data-a=mom-share]'); wait(pg, 800)
    sh = dbj().get('shares', [])
    ok(len(sh) == 1, 'the move can be shared')
    if sh:
        v = ctx.new_page(); v.on('pageerror', lambda e: errs.append(str(e))); v.goto('https://sorted.test/?share=%s' % sh[0]['token']); wait(v, 900)
        ok('Someone shared their move' in v.inner_text('main') and fits(v), 'the shared move opens and fits'); v.close()
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    pg.locator('[data-a=panel][data-p=paste]').first.evaluate('e=>e.click()'); wait(pg, 400); pg.fill('#f-paste', "Sorry, it wasn't Sky, it was Virgin Media"); pg.click('form[data-f=paste] button[type=submit]'); wait(pg, 800)
    ok(pg.locator('[data-a=corr-yes]').count() == 1, 'a correction is proposed')
    pg.click('[data-a=corr-yes]'); wait(pg, 700)
    ok([x for x in cases() if x['id'] == cid][0]['promises'][0]['party'] == 'Virgin Media', 'and applied')
    pg.reload(); wait(pg, 900)
    ok('Virgin Media' in pg.inner_text('main') and fits(pg), 'a reload keeps it')
    pg.emulate_media(color_scheme='dark'); wait(pg, 300)
    ok(fits(pg) and pg.locator('main').count() == 1, 'dark mode renders and fits')
    ok(not errs, 'no page errors: %s' % errs[:3])
    print('CHECKS', n[0]); b.close()
print('ERRORS', errs); print('FAILS', fails)
