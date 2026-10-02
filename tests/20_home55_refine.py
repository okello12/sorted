import os
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=300): pg.wait_for_timeout(ms)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London',color_scheme='light')
    ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
    ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg); pg.click('[data-a=anon-start]'); wait(pg)
    pg.click('[data-a=example]'); wait(pg,450)

    ok(pg.locator('.home44-state').count()==0,'spotlight does not repeat Your move')
    badge=pg.locator('.home54-count')
    ok(badge.count()==1,'header graphic keeps its decorative badge element')
    ok(pg.evaluate("getComputedStyle(document.querySelector('.home54-count')).fontSize")=='0px','header graphic no longer repeats the numeric count')
    ok(pg.locator('.home55-meta-main').count()==1,'spotlight metadata uses the softer split layout')
    spot_h=pg.locator('.home44-spot').bounding_box()['height']
    ok(spot_h < 470,'spotlight stays compact on a 390px phone viewport: %.1fpx'%spot_h)

    cases=[
      ({'said':'Currys promised the refund would be paid tomorrow','party':'Currys'},'Did the money arrive?'),
      ({'said':'British Gas said they would call back tomorrow','party':'British Gas'},'Did they get back to you?'),
      ({'said':'Amazon said the package will be delivered tomorrow','party':'Amazon'},'Did it arrive?'),
      ({'said':'The garage said they would fix the car tomorrow','party':'Garage'},'Did they fix it?'),
      ({'said':'The engineer will attend tomorrow','party':'British Gas'},'Did they turn up?'),
      ({'said':'They would deal with it tomorrow','party':'Letting agent'},'Did the letting agent do what they said?'),
    ]
    for promise,expected in cases:
        got=pg.evaluate('(x)=>home55Question(x,["Did it happen?"])',promise)
        ok(got==expected,'context question: %s'%expected)
    kept=pg.evaluate('()=>home55Question({said:"anything",party:"Someone"},["Did they come?"])')
    ok(kept=='Did they come?','an already-specific question is preserved')

    pg.screenshot(path=HERE+'/tests/out/home55-light.png',full_page=True)
    b.close()
print('ERRORS',errs); print('FAILS',fails)
