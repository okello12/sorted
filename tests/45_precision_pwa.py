# v87: precision intake/onboarding polish and iPhone Add-to-Home-Screen controls.
import os
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); fails=[]; errs=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c:fails.append(m)
def wait(pg,ms=350):pg.wait_for_timeout(ms)
def no_overflow(pg):return pg.evaluate('document.documentElement.scrollWidth<=document.documentElement.clientWidth')
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London',color_scheme='dark')
    ctx.add_init_script("Object.defineProperty(navigator,'standalone',{configurable:true,get:()=>true})")
    ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
    ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url and 'manifest.webmanifest' not in r.request.url else r.fulfill(body='{}' if 'manifest.webmanifest' in r.request.url else ''))
    pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('https://sorted.test/#start');wait(pg,650)
    ok(pg.locator('html.cap87-standalone').count()==1,'standalone launch is detected')
    nav=pg.locator('.cap87-appnav');ok(nav.count()==1,'standalone launch gets in-app navigation controls')
    if nav.count():
        ok(nav.locator('button[data-cap87=back]').count()==1 and nav.locator('button[data-cap87=forward]').count()==1,'standalone toolbar has back and forward')
        ok(nav.locator('button[data-cap87=reload]').count()==1 and nav.locator('button[data-cap87=home]').count()==1,'standalone toolbar has refresh and home')
    if pg.locator('[data-a=anon-start]').count():pg.click('[data-a=anon-start]');wait(pg,300)
    chooser=pg.locator('#cap82-start,#cap82-landing').first
    if chooser.count() and chooser.locator('.cap82-card[data-cap82=fix]').count():
        chooser.locator('.cap82-card[data-cap82=fix]').click();wait(pg,450)
    ta=pg.locator('#f-case').first
    ok(ta.count()==1,'broken choice reaches the intake composer')
    if ta.count():
        ok(pg.locator('html.cap87-intake').count()==1,'intake precision state is active')
        heading=pg.locator('h1,h2').filter(has_text="What’s broken?")
        ok(heading.count()>=1,'broken choice carries through to a specific intake heading')
        ok(pg.locator('.hero-art:visible').count()==0,'giant decorative hero art is removed from intake')
        ok(pg.locator('.cap87-empty-cases:visible').count()==0,'empty Your cases block is hidden during first-case creation')
        ta.focus(); ring=ta.evaluate("e=>getComputedStyle(e).outlineStyle==='none'&&getComputedStyle(e).boxShadow!=='none'")
        ok(ring,'textarea uses one deliberate focus treatment')
        ta.fill('Pcn'); pg.locator('button[type=submit]').first.click(); wait(pg,250)
        more=pg.get_by_text('Add a little more detail',exact=True)
        cont=pg.get_by_text('Continue with “Pcn”',exact=True)
        ok(more.count()==1,'vague-input recovery asks for a little more detail')
        ok(cont.count()==1,'vague-input recovery names the exact text if user continues')
    ok(no_overflow(pg),'v87 precision and standalone toolbar fit 390px')
    ctx.close();b.close()
print('ERRORS',errs);print('FAILS',fails)
