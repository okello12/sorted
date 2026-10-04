# v90: exact iPhone standalone handoff shown in real-device screenshots.
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
    ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London',color_scheme='light')
    ctx.add_init_script("Object.defineProperty(navigator,'standalone',{configurable:true,get:()=>true})")
    ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
    ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url and 'manifest.webmanifest' not in r.request.url else r.fulfill(body='{}' if 'manifest.webmanifest' in r.request.url else ''))
    pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('https://sorted.test/#start');wait(pg,650)
    if pg.locator('[data-a=anon-start]').count():pg.click('[data-a=anon-start]');wait(pg,280)
    chooser=pg.locator('#cap82-start,#cap82-landing').first
    ok(chooser.count()==1,'standalone start has the visual chooser')

    # Something else remains generic, but should go straight to a compact composer with no giant art.
    other=chooser.locator('[data-cap82=other]')
    if other.count():other.click();wait(pg,500)
    ta=pg.locator('#f-case').first
    ok(ta.count()==1,'Something else opens the case composer')
    if ta.count():
        h=pg.locator('main h1,main h2').filter(has_text='What do you need to sort out?').first
        ok(h.count()==1,'Something else keeps the generic intake question')
        large=pg.evaluate("""()=>{const ta=document.querySelector('#f-case'),m=ta&&ta.closest('main'),h=m&&Array.from(m.querySelectorAll('h1,h2')).find(x=>(x.textContent||'').includes('What do you need to sort out?'));if(!m||!h)return -1;const hy=h.getBoundingClientRect().top;return Array.from(m.querySelectorAll('img,picture,figure,svg,[class*=hero-art],[class*=illustration],[class*=artwork]')).filter(x=>{const r=x.getBoundingClientRect(),s=getComputedStyle(x);return s.display!=='none'&&r.width>=170&&r.height>=100&&r.bottom<=hy+50}).length}""")
        ok(large==0,'Something else has no large decorative artwork above the intake question')
    ok(pg.locator('.tab129:visible').count()==1,'standalone navigation remains available on the composer (v129: the app bar)')

    # Home returns to chooser, and a named tile carries its category into intake.
    pg.locator('.tab129 [data-a=go-home]').click();wait(pg,350)
    chooser=pg.locator('#cap82-start,#cap82-landing').first
    fix=chooser.locator('[data-cap82=fix]')
    if fix.count():fix.click();wait(pg,500)
    ok(pg.locator('.gi-form').count()==1,'broken tile opens the guided start (v91)')
    ok(pg.get_by_text('What’s broken?',exact=True).count()>=1,'broken tile carries through to What’s broken?')
    ok('drain' in (pg.locator('#gi-what').get_attribute('placeholder') or '').lower(),'broken tile asks what it is doing, with examples')
    large2=pg.evaluate("""()=>{const ta=document.querySelector('#f-case,.gi-form'),m=ta&&ta.closest('main'),h=m&&Array.from(m.querySelectorAll('h1,h2')).find(x=>(x.textContent||'').trim()==='What’s broken?');if(!m||!h)return -1;const hy=h.getBoundingClientRect().top;return Array.from(m.querySelectorAll('img,picture,figure,svg,[class*=hero-art],[class*=illustration],[class*=artwork]')).filter(x=>{const r=x.getBoundingClientRect(),s=getComputedStyle(x);return s.display!=='none'&&r.width>=170&&r.height>=100&&r.bottom<=hy+50}).length}""")
    ok(large2==0,'category-specific intake also has no large decorative artwork')
    ok(no_overflow(pg),'standalone compact intake fits 390px')
    ctx.close();b.close()
print('ERRORS',errs);print('FAILS',fails)
