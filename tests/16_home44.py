import os,sys,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=300): pg.wait_for_timeout(ms)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
    ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg); pg.click('[data-a=anon-start]'); wait(pg)
    # The built-in missed appointment should become the spotlight case.
    pg.click('[data-a=example]'); wait(pg,450)
    ok(pg.locator('.home44').count()==1,'v44 home renders')
    ok(pg.locator('.home44-spot').count()==1,'one spotlight case is present')
    ok(pg.locator('h1').count()==1,'v47: exactly one page heading on Home (%d)'%pg.locator('h1').count())
    ok(pg.evaluate("document.querySelector('main').textContent.split('Needs you').length-1")==1,'v48: "Needs you" appears once')
    ok('One thing needs you.' in pg.inner_text('main'),'v48: one active case says it is the only thing')
    ok('The rest of your open cases are below' not in pg.inner_text('main'),'v48: no "rest of your cases are below" line')
    spot=pg.inner_text('.home44-spot')
    ok('Washing machine' in spot and 'Did they turn up?' in spot,'spotlight explains the case and outcome question')
    ok(pg.locator('.home44-spot [data-a=home-ans]').count()==3,'spotlight exposes the three outcome actions')
    # A future promise should sit quietly in Waiting rather than compete with the spotlight.
    pg.click('[data-a=compose]'); wait(pg); pg.fill('#f-case','British Gas said the engineer will come tomorrow morning, ref BG-44'); pg.click('form[data-f=case] button[type=submit]'); wait(pg); pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg,450); pg.click('[data-a=sug-yes]'); wait(pg,450); pg.click('[data-a=home]'); wait(pg,450)
    ok(pg.locator('.home44-row.waiting').count()>=1,'future promise appears as a quiet Waiting row')
    w=pg.inner_text('.home44-section')
    ok('Waiting' in w and 'British Gas' in w,'Waiting section names the held case')
    ok('You can put this down until' in pg.inner_text('main'),'Waiting state gives permission to stop thinking about it')
    ok(pg.locator('h1').count()==1,'v47: still one page heading with a Waiting case')
    ok(re.search(r'need(?:s)? you\.', pg.inner_text('main')) is not None and pg.locator('.home111-newbtn').count()==1,'v48: with other cases held, "Deal with this first"')
    ok(pg.evaluate("document.querySelector('main').textContent.split('Needs you').length-1")==1,'v48: still one "Needs you"')
    pg.screenshot(path=HERE+'/tests/out/home44.png',full_page=True)
    # Mobile enlargement must not force horizontal page scrolling.
    pg.evaluate("document.documentElement.style.fontSize='200%'"); wait(pg); d=pg.evaluate("({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth})")
    ok(d['sw']<=d['cw']+3,'200 percent text has no horizontal page overflow')
    b.close()
print('ERRORS',errs); print('FAILS',fails)
