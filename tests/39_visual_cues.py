# v80: two extra expressive cues without changing case behaviour.
import os
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=250): pg.wait_for_timeout(ms)
def no_overflow(pg): return pg.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth')
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London',color_scheme='light')
    ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
    ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg,200); pg.click('[data-a=anon-start]'); wait(pg); pg.click('[data-a=example]'); wait(pg,400)
    # Open the active case so the consolidated groups and next-step surface are present.
    op=pg.locator('[data-a=open]').first
    if op.count(): op.click(); wait(pg,300)
    happened=pg.locator('.case75-happened>summary').first
    tools=pg.locator('.case75-tools>summary').first
    ok(happened.count()==1 and tools.count()==1,'case keeps both consolidated secondary groups')
    if happened.count():
        hc=pg.evaluate("e=>getComputedStyle(e,'::before').content",happened.element_handle())
        ok('↺' in hc,'What happened has its aqua/violet section sigil')
    if tools.count():
        tc=pg.evaluate("e=>getComputedStyle(e,'::before').content",tools.element_handle())
        ok('✦' in tc,'Tools for this case has its violet/coral section sigil')
    nxt=pg.locator('.case56-next').first
    if nxt.count():
        bg=pg.evaluate("e=>getComputedStyle(e,'::after').backgroundImage",nxt.element_handle())
        ok('gradient' in bg,'current next-step card carries the ambient sheen layer')
    ok(no_overflow(pg),'v80 cues do not introduce horizontal overflow')
    b.close()

    b2=p.chromium.launch(); ctx2=b2.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London',reduced_motion='reduce')
    ctx2.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
    ctx2.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg2=ctx2.new_page(); pg2.goto('https://sorted.test/#start'); pg2.evaluate("localStorage.setItem('__emailReady','1')"); wait(pg2,120)
    # The style rule itself must disable the new decorative motion for reduced-motion users.
    ok('prefers-reduced-motion:reduce' in pg2.locator('html').evaluate("e=>e.innerHTML"),'reduced-motion fallback remains present for decorative cues')
    b2.close()
print('ERRORS',errs); print('FAILS',fails)
