# Adversarial pressure test: repeated navigation, duplicate submits, long/hostile input,
# stale cache, small viewports and standalone resume/reload. This file is intentionally
# kept on a pressure-test branch until findings are reviewed.
import os, json
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); fails=[]; errs=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c:fails.append(m)
def wait(pg,ms=350):pg.wait_for_timeout(ms)
def db(pg):
    try:return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')||'{}')") or {}
    except:return {}
def cases(pg):return [x.get('data',{}) for x in db(pg).get('tasks',[]) if x.get('data',{}).get('kind')!='moment']
def no_overflow(pg):return pg.evaluate('document.documentElement.scrollWidth<=document.documentElement.clientWidth')
def settle_case(pg):
    wait(pg,220)
    for sel in ('[data-a=match-new]:visible','[data-a=vague-go]:visible','[data-a=safe-continue]:visible'):
        if pg.locator(sel).count():pg.locator(sel).first.click();wait(pg,180)
    if pg.locator('form[data-f=baseline]:visible').count():
        form=pg.locator('form[data-f=baseline]:visible').first;chips=form.locator('.chip:visible')
        if chips.count():chips.first.click()
        form.locator('button[type=submit]:visible').first.click();wait(pg,220)
    if pg.locator('[data-a=sug-yes]:visible').count():pg.locator('[data-a=sug-yes]:visible').first.click();wait(pg,180)
    notnow=pg.get_by_text('Not now',exact=True)
    if notnow.count() and notnow.first.is_visible():notnow.first.click();wait(pg,180)
def open_other(pg):
    h=pg.locator('[data-cap87=home]:visible')
    if h.count():h.first.click();wait(pg,250)
    else:pg.goto('https://sorted.test/');wait(pg,350)
    card=pg.locator('[data-cap82=other]:visible')
    if card.count():card.first.click();wait(pg,300);return
    compose=pg.locator('[data-a=compose]:visible')
    if compose.count():compose.first.click();wait(pg,250)
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London',color_scheme='light')
    ctx.add_init_script("Object.defineProperty(navigator,'standalone',{configurable:true,get:()=>true})")
    ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
    ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url and 'manifest.webmanifest' not in r.request.url else r.fulfill(body='{}' if 'manifest.webmanifest' in r.request.url else ''))
    pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('https://sorted.test/#start');pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')");pg.reload();wait(pg,500)
    if pg.locator('[data-a=anon-start]:visible').count():pg.locator('[data-a=anon-start]:visible').first.click();wait(pg,500)
    ok(pg.locator('.cap87-appnav').count()==1,'standalone toolbar survives fresh launch')
    for w in (320,360,390,430):
        pg.set_viewport_size({'width':w,'height':844});wait(pg,80);ok(no_overflow(pg),'no horizontal overflow at %spx'%w)
    pg.set_viewport_size({'width':390,'height':844})
    open_other(pg);n0=len(cases(pg));hostile='<img src=x onerror="window.__sortedXss=1"> My landlord said the repair will be done Friday 😬 — ref A&B-123 <script>window.__sortedXss=2</script>'
    ok(pg.locator('#f-case:visible').count()==1,'generic intake is reachable under standalone pressure')
    pg.locator('#f-case:visible').fill(hostile)
    pg.locator('form[data-f=case]:visible button[type=submit]:visible').first.click();settle_case(pg)
    ok(len(cases(pg))==n0+1,'hostile-looking input creates exactly one case')
    ok(not pg.evaluate('window.__sortedXss===1||window.__sortedXss===2'),'HTML/script-like case text never executes')
    ok(no_overflow(pg),'hostile/unicode text does not break mobile width')
    open_other(pg);n1=len(cases(pg));ok(pg.locator('#f-case:visible').count()==1,'generic intake remains reachable after completing a case')
    pg.locator('#f-case:visible').fill('Currys has not sent my £42.17 refund, order DUP-991')
    pg.locator('form[data-f=case]:visible button[type=submit]:visible').first.evaluate('(b)=>{b.click();b.click()}');settle_case(pg)
    ok(len(cases(pg))==n1+1,'double-submit pressure does not duplicate a case')
    open_other(pg);longtext=('British Gas said they would investigate the billing problem. Reference LONG-7788. '+('This is additional context with dates, calls, notes and £ symbols. '*90)).strip()
    ta=pg.locator('#f-case:visible');ok(ta.count()==1,'generic intake remains reachable for long-input pressure');ta.fill(longtext);accepted=len(ta.input_value())
    ok(accepted>500,'intake accepts a realistically long account of a problem')
    n2=len(cases(pg));pg.locator('form[data-f=case]:visible button[type=submit]:visible').first.click();settle_case(pg)
    ok(len(cases(pg))==n2+1,'long input completes without duplicate or lost case')
    ok(no_overflow(pg),'long input/result stays within 390px')
    expected=len(cases(pg))
    for i in range(5):
        pg.reload();wait(pg,260)
        ok(len(cases(pg))==expected,'reload %d preserves all cases'%(i+1))
        ok(pg.locator('.cap87-appnav [data-cap87=home]').count()==1,'reload %d restores standalone controls'%(i+1))
    keys=pg.evaluate("Object.keys(localStorage).filter(k=>k.indexOf('sorted.cache.')===0)")
    if keys:
        pg.evaluate("ks=>ks.forEach(k=>localStorage.setItem(k,'{not-json'))",keys);pg.reload();wait(pg,450)
        ok(pg.locator('main').count()==1 and not pg.locator('body').inner_text().strip()=='','corrupt cache does not blank/freeze the app')
        ok(len(cases(pg))==expected,'corrupt cache recovers cases from backing data')
    else:ok(True,'no local cache key in anonymous mock session')
    home=pg.locator('[data-cap87=home]:visible')
    if home.count():home.first.click();wait(pg,220)
    fix=pg.locator('[data-cap82=fix]:visible')
    if fix.count():
        fix.first.click();wait(pg,320);ok(pg.get_by_text("What’s broken?",exact=True).count()>=1,'broken route gets broken-specific intake under repeated use')
        if pg.locator('[data-cap87=home]:visible').count():pg.locator('[data-cap87=home]:visible').first.click();wait(pg,220)
        call=pg.locator('[data-cap82=call]:visible')
        if call.count():call.first.click();wait(pg,320);ok(pg.get_by_text("What’s the call about?",exact=True).count()>=1,'call route replaces stale broken-route context')
    for i in range(3):
        if pg.locator('[data-cap87=home]:visible').count():pg.locator('[data-cap87=home]:visible').first.click();wait(pg,120)
        if pg.locator('[data-cap87=reload]:visible').count():pg.locator('[data-cap87=reload]:visible').first.click();wait(pg,280)
        ok(pg.locator('main').count()==1 and len(pg.inner_text('main'))>20,'standalone navigation cycle %d remains responsive'%(i+1))
    ok(not errs,'no page errors during core pressure sequence: %s'%errs)
    ctx.close();b.close()
print('ERRORS',errs);print('FAILS',fails)
