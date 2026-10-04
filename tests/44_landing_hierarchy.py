# v85: the public landing leads with the product chooser, not a full-screen marketing hero.
import os
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=450): pg.wait_for_timeout(ms)
def no_overflow(pg): return pg.evaluate('document.documentElement.scrollWidth<=document.documentElement.clientWidth')
with sync_playwright() as p:
    b=p.chromium.launch()
    for scheme in ['light','dark']:
        ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London',color_scheme=scheme)
        ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
        ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
        pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('https://sorted.test/'); wait(pg,700)
        hero=pg.locator('.hero'); chooser=pg.locator('#cap82-landing')
        ok(hero.count()==1 and chooser.count()==1,scheme+': hero and visual chooser both render')
        ok(pg.locator('html.cap85-public').count()==1,scheme+': public landing gets v85 hierarchy')
        if hero.count() and chooser.count():
            hb=hero.bounding_box(); cb=chooser.bounding_box()
            ok(hb is not None and hb['height']<720,scheme+': hero is compact enough to stop owning the first screen (v123: headline, explanation, kinds, one button, art, a quiet line; the harness has no web fonts, so this is pessimistic)')
            cta=hero.locator('a.btn.primary').bounding_box(); ok(cta is not None and cta['y']+cta['height']<700,scheme+': the one primary button sits above the fold')
            ok(hb is not None and cb is not None and cb['y']-(hb['y']+hb['height'])<35,scheme+': chooser follows the proposition immediately')
            hyp=hero.locator('.h1').evaluate("e=>getComputedStyle(e).hyphens")
            ok(hyp=='none',scheme+': headline cannot hyphenate remembers mid-word')
            top=hero.locator('.cap85-top-cta')
            ok(top.count()==1 and top.evaluate("e=>getComputedStyle(e).display")!='none' and hero.locator('.btn.primary').count()==1,scheme+': one primary CTA in the hero, shown (v123)')
            ok(hero.locator('.cap85-pilot-note').count()==0,scheme+': pilot retention notice no longer interrupts the opening proposition')
        ok(chooser.locator('.cap82-card').count()==6,scheme+': all six real-life starting points remain')
        ok(chooser.locator('.cap85-scene svg').count()==6,scheme+': each starting point uses the new miniature 3D scene')
        ok(chooser.locator('.cap85-scene linearGradient').count()>=30,scheme+': scenes use layered material gradients rather than flat glyphs')
        ex=pg.locator('section[aria-labelledby="ex-h"]')
        ok(ex.count()==1 and ex.locator('#ex-h').inner_text().strip()=='See how Sorted handles it',scheme+': examples are framed as product behaviour, not another feature list')
        if ex.count():
            ok(ex.locator('.cap85-ex-rail .slip').count()==3,scheme+': examples are limited to three concise cases')
            ok(ex.locator('.cap85-ex-rail').evaluate("e=>e.scrollWidth>e.clientWidth"),scheme+': example cases use their own compact horizontal rail')
        foot=pg.inner_text('footer')
        ok('stored in London' in foot and '90 days' in foot and 'small UK service' in foot,scheme+': the service and retention information is preserved lower on the page, in the footer (v123)')
        if ex.count():
            py=pg.locator('footer').bounding_box()['y']; ey=ex.bounding_box()['y']
            ok(py>ey,scheme+': that information comes after the product examples')
        ok(no_overflow(pg),scheme+': hierarchy and 3D scenes do not create page-level horizontal scrolling')
        ctx.close()
    b.close()
print('ERRORS',errs); print('FAILS',fails)
