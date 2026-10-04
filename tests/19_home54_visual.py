import os
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=300): pg.wait_for_timeout(ms)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London',color_scheme='dark')
    ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
    ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg); pg.click('[data-a=anon-start]'); wait(pg)
    pg.click('[data-a=example]'); wait(pg,450)

    ok(pg.locator('.home54-visual').count()==1,'v54 action graphic is present')
    ok(pg.locator('.home54-folder').count()==1 and pg.locator('.home54-clock').count()==1,'folder and clock graphic pieces render')
    ok(pg.locator('.home44-new.primary').count()==0 and pg.locator('.home44-new').count()==1,'new-case button is quieter, not primary')
    anim=pg.evaluate("getComputedStyle(document.querySelector('.home54-visual')).animationName")
    ok(anim=='home54Float','graphic has restrained motion when motion is allowed: '+anim)

    # Clone the tested case as a second Needs-you item with an intentionally raw title.
    pg.evaluate("""()=>{var db=JSON.parse(localStorage.getItem('__mockdb'));var c=JSON.parse(JSON.stringify(db.tasks[0]));c.id='qa-raw';c.data.id='qa-raw';c.data.example=false;c.data.title='TEST: Submit bursary documents tomorrow by 3pm';db.tasks.push(c);localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}""")
    pg.reload(); wait(pg,500)
    ok(pg.locator('.home44-section.needs').count()==1,'second action case sits under Also open')
    sec=pg.inner_text('.home44-section.needs')
    ok('The rest of your open cases.' not in sec,'redundant Also-open subtitle is gone')
    ok('TEST:' not in sec and 'tomorrow by 3pm' not in sec and 'Submit bursary documents' in sec,'raw case title is cleaned for Home display')
    ok(pg.locator('.home44-section.needs .home44-row:not(.home111-hot) .home44-pill').count()==0,'secondary action rows do not repeat Your move pills (v111: only a missed or overdue case carries a word)')

    # Reduced-motion preference must stop decorative animation.
    pg.emulate_media(reduced_motion='reduce'); wait(pg,100)
    reduced=pg.evaluate("getComputedStyle(document.querySelector('.home54-visual')).animationName")
    ok(reduced=='none','reduced-motion disables decorative animation: '+reduced)

    pg.screenshot(path=HERE+'/tests/out/home54-dark.png',full_page=True)
    b.close()
print('ERRORS',errs); print('FAILS',fails)
