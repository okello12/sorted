# v82: the permanent start surface teaches Sorted visually without replacing the case-first workflow.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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

    # First-time landing: all six real-life visual choices are visible and selectable.
    pg.goto('https://sorted.test/'); wait(pg,450)
    ok(pg.locator('#cap82-landing .cap82-card').count()==6,'landing teaches the six visual starting points')
    ok(pg.locator('#cap82-landing .cap82-art svg').count()==6,'every starting point has its own visual scene')
    ok(pg.locator('#cap82-landing [data-cap82="other"]').count()==1,'landing keeps a freeform Something else escape hatch')
    ok(no_overflow(pg),'visual landing does not overflow at 390px')
    pg.click('#cap82-landing [data-cap82="promise"]'); wait(pg,180)
    ok('#start' in pg.url,'choosing a visual from the public landing starts the existing flow')

    # Enter the pilot and create the existing example so Home has real cases.
    pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg,220)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg,260)
    if pg.locator('[data-a=example]').count(): pg.click('[data-a=example]'); wait(pg,500)
    ok(pg.locator('#cap82-start .cap82-card').count()==6,'returning Home keeps all six visual starting points')
    ok(pg.locator('.home44-spot').count()==1,'the existing case-first spotlight remains directly below the chooser')
    ok(pg.locator('#cap82-start').evaluate("e=>e.classList.contains('cap82-with-cases')"),'chooser becomes more compact when cases exist')
    ok(no_overflow(pg),'combined chooser and case dashboard do not overflow at 390px')

    # A visual choice opens the existing composer instead of creating a parallel workflow.
    pg.click('#cap82-start [data-cap82="call"]'); wait(pg,240)
    f=pg.locator('#f-case')
    ok(f.count()==1,'visual choice opens the existing case composer')
    if f.count():
        ph=f.get_attribute('placeholder') or ''
        ok('call' in ph.lower(),'composer prompt is tailored to the chosen real-life situation')
    ok(pg.locator('.home44-spot').count()==1,'opening a new visual choice does not remove the active case')

    # Dark mode keeps the unified surface stable.
    pg.evaluate("document.documentElement.setAttribute('data-theme','dark')"); wait(pg,100)
    ok(no_overflow(pg),'unified start surface stays stable in dark mode')
    b.close()
print('ERRORS',errs); print('FAILS',fails)
