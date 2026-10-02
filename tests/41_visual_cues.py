# v81: verify the two added visual cues without changing behaviour.
import os
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=250): pg.wait_for_timeout(ms)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London',color_scheme='light')
    ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
    ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg,180); pg.click('[data-a=anon-start]'); wait(pg); pg.click('[data-a=example]'); wait(pg,380)
    op=pg.locator('[data-a=open]').first
    if op.count(): op.click(); wait(pg,280)
    h=pg.locator('.case75-happened>summary').first; t=pg.locator('.case75-tools>summary').first
    ok(h.count()==1 and t.count()==1,'consolidated case groups remain present')
    if h.count(): ok('↺' in pg.evaluate("e=>getComputedStyle(e,'::before').content",h.element_handle()),'history group has its aqua sigil')
    if t.count(): ok('✦' in pg.evaluate("e=>getComputedStyle(e,'::before').content",t.element_handle()),'tools group has its violet sigil')
    nxt=pg.locator('.case56-next').first
    if nxt.count(): ok('gradient' in pg.evaluate("e=>getComputedStyle(e,'::after').backgroundImage",nxt.element_handle()),'current-work card has the neutral sheen layer')
    ok(pg.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth'),'no horizontal overflow at 390px')
    b.close()
print('ERRORS',errs); print('FAILS',fails)
