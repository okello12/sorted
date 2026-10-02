# v79: expressive visual system without changing the case model.
import os
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=300): pg.wait_for_timeout(ms)
def no_overflow(pg): return pg.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth')
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London',color_scheme='light')
    ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
    ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))

    pg.goto('https://sorted.test/'); wait(pg)
    hero=pg.locator('.hero')
    bg=pg.evaluate('e=>getComputedStyle(e).backgroundImage',hero.element_handle())
    rad=float(pg.evaluate('e=>parseFloat(getComputedStyle(e).borderRadius)',hero.element_handle()))
    ok('gradient' in bg and rad>=20,'landing hero has a bold gradient surface and generous radius')
    primary=pg.locator('.hero .btn.primary').first
    pbg=pg.evaluate('e=>getComputedStyle(e).backgroundImage',primary.element_handle())
    ok('linear-gradient' in pbg,'primary action uses the new violet gradient')
    ok(no_overflow(pg),'landing has no horizontal overflow at 390px')

    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg,200); pg.click('[data-a=anon-start]'); wait(pg); pg.click('[data-a=example]'); wait(pg,450)
    spot=pg.locator('.home44-spot')
    ok(spot.count()==1,'Home has an active-case spotlight')
    if spot.count():
        sbg=pg.evaluate('e=>getComputedStyle(e).backgroundImage',spot.element_handle())
        ok('gradient' in sbg,'active case spotlight carries the colourful state treatment')
    rows=pg.locator('.home44-row')
    if rows.count():
        rbg=pg.evaluate('e=>getComputedStyle(e).backgroundImage',rows.first.element_handle())
        ok('gradient' in rbg,'case rows carry state colour without changing their content')
    else:
        ok(True,'Home example can legitimately have no secondary case rows')
    ok(no_overflow(pg),'Home has no horizontal overflow at 390px')

    op=pg.locator('[data-a=open]').first
    if op.count(): op.click(); wait(pg,350)
    groups=pg.locator('details.case75-group')
    ok(groups.count()==2,'case detail still has the two consolidated secondary groups')
    if groups.count():
        br=float(pg.evaluate('e=>parseFloat(getComputedStyle(e).borderRadius)',groups.first.element_handle()))
        ok(br>=14,'case groups use the softer visual surface')
    ok(no_overflow(pg),'case detail has no horizontal overflow at 390px')

    pg.evaluate("document.documentElement.setAttribute('data-theme','dark')"); wait(pg,80)
    paper=pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--paper').trim()")
    ok(paper.upper()=='#0B0D18','dark mode uses the deeper visual canvas')
    ok(no_overflow(pg),'dark mode keeps the layout stable')
    b.close()

    b2=p.chromium.launch(); ctx2=b2.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London',color_scheme='light',reduced_motion='reduce')
    ctx2.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
    ctx2.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg2=ctx2.new_page(); pg2.goto('https://sorted.test/'); wait(pg2,150)
    anim=pg2.evaluate("e=>getComputedStyle(e).animationName",pg2.locator('.hero-art').element_handle())
    ok(anim=='none','reduced-motion users do not get decorative hero animation')
    b2.close()
print('ERRORS',errs); print('FAILS',fails)
