# v136: a first visit meets one question. A newcomer's Home leads with what needs sorting (the ways in and the box);
# the ideas fold stays closed, Moving home sits after it rather than straight under the box, and the guest note waits
# until there is a case to keep. A returning Home is unchanged.
import os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear()")
    pg.goto('https://sorted.test/#start'); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 800)
    fold = pg.locator('#cap95-explore')
    ok(pg.locator('#cap82-start .cap82-card').count() == 6 and pg.locator('#f-case').count() == 1, 'a newcomer meets the ways in and the box first')
    ok(fold.count() == 1 and not fold.evaluate('d=>d.open'), 'the ideas wait in their closed fold')
    pos = pg.evaluate("(()=>{var f=document.querySelector('#f-case'),x=document.querySelector('#cap95-explore'),m=document.querySelector('.more136 [data-a=mom-start]');return [f.getBoundingClientRect().top,x.getBoundingClientRect().top,m?m.getBoundingClientRect().top:-1]})()")
    ok(pos[0] < pos[1] < pos[2], 'the box, then the ideas, then Moving home')
    ok(pg.locator('.anon129').count() == 0, 'the guest note waits until there is a case')
    pg.locator('.more136 [data-a=mom-start]').first.click(); wait(pg, 500)
    ok(pg.locator('#mv-date').count() == 1 or pg.locator('[data-a=mom-new]').count() >= 1, 'Moving home still opens from there')
    ok(pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth+1"), 'nothing scrolls sideways')
    ok(not errs, 'no page errors: %s' % errs)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
