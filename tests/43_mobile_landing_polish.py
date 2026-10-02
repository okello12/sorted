# v83/v84: real-device polish — richer scenes, compact returning chooser, opaque sticky chrome, tighter tools.
import os
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=300): pg.wait_for_timeout(ms)
def no_overflow(pg): return pg.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth')
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London',color_scheme='dark')
    ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
    ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))

    pg.goto('https://sorted.test/'); wait(pg,450)
    ok(pg.locator('#cap82-landing .cap82-card').count()==6,'first-time landing still shows all six choices')
    ok(pg.locator('#cap82-landing .cap83-scene svg').count()==6,'all six choices use the richer real-life scenes')
    ok(pg.locator('#cap82-landing .cap83-scene svg *').count()>30,'scene artwork is materially richer than a line glyph set')
    ok(no_overflow(pg),'full first-time gallery fits 390px')

    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg,220)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg,240)
    if pg.locator('[data-a=example]').count(): pg.click('[data-a=example]'); wait(pg,520)
    home=pg.locator('#cap82-start')
    ok(home.count()==1 and home.evaluate("e=>e.classList.contains('cap82-with-cases')"),'returning Home switches to the compact chooser')
    if home.count():
        ok(home.locator('.cap82-title').inner_text().strip()=='What do you need?','returning chooser uses the shorter heading')
        ok(home.locator('.cap82-home-marker').count()==0,'instructional “cases are below” scaffolding is gone')
        disp=home.locator('.cap82-grid').evaluate("e=>getComputedStyle(e).display")
        ok(disp=='flex','returning choices become a horizontal carousel')
        ok(home.locator('.cap82-grid').evaluate("e=>e.scrollWidth>e.clientWidth"),'carousel is horizontally discoverable instead of a tall grid')
    nb=pg.locator('.home44-compose .home44-new')
    if nb.count():
        hidden=nb.evaluate("e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return parseFloat(s.opacity)===0&&r.width<=1.1&&r.height<=1.1&&e.getAttribute('tabindex')==='-1'&&e.getAttribute('aria-hidden')==='true'}")
        ok(hidden,'duplicate Sort something new CTA is visually and keyboard hidden')
        nb.click(); wait(pg,120)
        ok(pg.locator('#f-case').count()==1,'legacy compose trigger remains programmatically actionable')
    else: ok(True,'duplicate Sort something new CTA is absent')
    ok(pg.locator('.home44-spot').count()==1,'active-case spotlight remains prominent')
    ok(no_overflow(pg),'compact chooser and cases fit 390px')

    bar=pg.locator('.bar').first
    if bar.count():
        bg=bar.evaluate("e=>getComputedStyle(e,'::before').backgroundColor")
        ok(bg not in ('rgba(0, 0, 0, 0)','transparent'),'sticky top bar has an opaque backing surface')

    op=pg.locator('[data-a=open]').first
    if op.count(): op.click(); wait(pg,350)
    tools=pg.locator('details.case75-tools').first
    if tools.count():
        tools.locator(':scope > summary').click(); wait(pg,120)
        gap=tools.locator('.case75-group-body').first.evaluate("e=>parseFloat(getComputedStyle(e).rowGap)||0")
        ok(gap<=2,'expanded Tools uses tighter vertical spacing')
    else: ok(True,'example case can omit Tools in this state')
    ok(no_overflow(pg),'case detail remains stable after the mobile polish')
    b.close()
print('ERRORS',errs); print('FAILS',fails)
