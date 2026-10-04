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
        ok(hero.count()==1 and chooser.count()==1,scheme+': hero and the visual chooser both render')
        ok(pg.locator('html.cap85-public').count()==1,scheme+': public landing gets the v85 styling')
        hb=hero.bounding_box()
        ok(hb is not None and hb['height']<620,scheme+': the hero is compact (v126: headline, one explanation, one main action, three problems)')
        cta=hero.locator('.btn.primary')
        cb=cta.bounding_box() if cta.count() else None
        ok(cta.count()==1 and cta.inner_text().strip()=='Start with your problem' and cb is not None and cb['y']+cb['height']<520,scheme+': one primary action, "Start with your problem", high on the first screen')
        ok('Describe it in your own words, or add a document.' in hero.inner_text() and hero.locator('[data-a=see-example]').count()==1,scheme+': it says how to start and offers "See an example"')
        ok([c.strip() for c in hero.locator('.hero-quick .chip').all_inner_texts()]==['Parking notice','Missing refund','Repair problem'],scheme+': three familiar problems, not the full catalogue')
        ok(hero.locator('.h1').evaluate("e=>getComputedStyle(e).hyphens")=='none',scheme+': the headline cannot hyphenate')
        ok(pg.locator('#browse126:not([open]) #cap82-landing').count()==1 and not chooser.is_visible(),scheme+': the six ways in, 32 examples and life moments are behind "Browse more", closed')
        ex=pg.locator('#example126')
        ok(ex.count()==1 and 'example' in ex.inner_text().lower() and ex.bounding_box()['y']<pg.locator('#browse126').bounding_box()['y'],scheme+': one short worked example, labelled, before Browse more')
        ok('14:00' not in pg.inner_text('body') and 'Tue ' not in pg.inner_text('main'),scheme+': no clipped sample dates like "Tue 14:00–16:00"')
        pg.click('#browse126 > summary'); wait(pg,250)
        ok(chooser.is_visible() and chooser.locator('.cap82-card').count()==6 and chooser.locator('.cap85-scene svg').count()==6,scheme+': Browse more opens the six starting points with their scenes')
        foot=pg.inner_text('footer')
        ok('stored in London' in foot and '90 days' in foot and 'small UK service' in foot,scheme+': the service and retention information stays in the footer')
        ok(no_overflow(pg),scheme+': hierarchy and 3D scenes do not create page-level horizontal scrolling')
        ctx.close()
    b.close()
print('ERRORS',errs); print('FAILS',fails)
