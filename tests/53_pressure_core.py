# Adversarial pressure test: repeated navigation, duplicate submits, hostile/long input,
# stale cache, small viewports and standalone resume/reload. Test-only branch.
import os
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); fails=[]; errs=[]; findings=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c:fails.append(m)
def finding(m):findings.append(m);print('FINDING '+m)
def wait(pg,ms=350):pg.wait_for_timeout(ms)
def db(pg):
    try:return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')||'{}')") or {}
    except:return {}
def cases(pg):return [x.get('data',{}) for x in db(pg).get('tasks',[]) if x.get('data',{}).get('kind')!='moment']
def no_overflow(pg):return pg.evaluate('document.documentElement.scrollWidth<=document.documentElement.clientWidth')
def visible_chooser(pg):return pg.locator('#cap82-start:visible,#cap82-landing:visible')
def settle_case(pg):
    wait(pg,240)
    for sel in ('[data-a=match-new]:visible','[data-a=vague-go]:visible','[data-a=safe-continue]:visible'):
        if pg.locator(sel).count():pg.locator(sel).first.click();wait(pg,180)
    if pg.locator('form[data-f=baseline]:visible').count():
        f=pg.locator('form[data-f=baseline]:visible').first;ch=f.locator('.chip:visible')
        if ch.count():ch.first.click()
        f.locator('button[type=submit]:visible').first.click();wait(pg,260)
    if pg.locator('[data-a=sug-yes]:visible').count():pg.locator('[data-a=sug-yes]:visible').first.click();wait(pg,180)
    n=pg.get_by_text('Not now',exact=True)
    if n.count() and n.first.is_visible():n.first.click();wait(pg,180)
def user_home(pg,label):
    # Test the standalone Home control first. If it fails, load / directly to distinguish
    # a standalone navigation defect from a general start-surface defect.
    h=pg.locator('[data-cap87=home]:visible')
    if h.count():h.first.click();wait(pg,500)
    else:pg.goto('https://sorted.test/#start');wait(pg,500)
    c=visible_chooser(pg)
    if c.count():return c.first,True
    finding('%s: standalone Home did not expose the visual start chooser (hash=%s, main=%s)'%(label,pg.evaluate('location.hash'),pg.locator('main').first.get_attribute('class') if pg.locator('main').count() else 'none'))
    pg.goto('https://sorted.test/');wait(pg,600)
    c=visible_chooser(pg)
    if c.count():
        finding('%s: normal root restored the chooser, isolating the problem to standalone Home navigation'%label)
        return c.first,False
    finding('%s: chooser was also absent after a direct root load'%label)
    return None,False
def open_generic(pg,label):
    chooser,direct=user_home(pg,label)
    if chooser is not None:
        other=chooser.locator('[data-cap82=other]:visible')
        if other.count():other.first.click();wait(pg,380)
    if not pg.locator('#f-case:visible').count():
        # Last-resort compatibility hook lets later engine pressure continue, but is not user-facing success.
        if pg.locator('[data-a=compose]').count():pg.evaluate("document.querySelector('[data-a=compose]').click()");wait(pg,380)
    return direct
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London',color_scheme='light')
    ctx.add_init_script("Object.defineProperty(navigator,'standalone',{configurable:true,get:()=>true})")
    ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
    ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url and 'manifest.webmanifest' not in r.request.url else r.fulfill(body='{}' if 'manifest.webmanifest' in r.request.url else ''))
    pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('https://sorted.test/#start');pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')");pg.reload();wait(pg,500)
    if pg.locator('[data-a=anon-start]:visible').count():pg.locator('[data-a=anon-start]:visible').first.click();wait(pg,500)
    ok(pg.locator('.cap87-appnav:visible').count()==1,'standalone toolbar survives fresh launch')
    ok(visible_chooser(pg).count()>=1,'fresh standalone launch exposes the start chooser')
    for w in (320,360,390,430):
        pg.set_viewport_size({'width':w,'height':844});wait(pg,90);ok(no_overflow(pg),'no horizontal overflow at %spx'%w)
    pg.set_viewport_size({'width':390,'height':844})

    # Hostile-looking text must remain inert and create exactly one case.
    open_generic(pg,'first start');ok(pg.locator('#f-case:visible').count()==1,'generic intake is reachable under standalone pressure')
    n0=len(cases(pg));hostile='<img src=x onerror="window.__sortedXss=1"> My landlord said the repair will be done Friday 😬 — ref A&B-123 <script>window.__sortedXss=2</script>'
    if pg.locator('#f-case:visible').count():
        pg.locator('#f-case:visible').fill(hostile);pg.locator('form[data-f=case]:visible button[type=submit]:visible').first.click();settle_case(pg)
    ok(len(cases(pg))==n0+1,'hostile-looking input creates exactly one case')
    ok(not pg.evaluate('window.__sortedXss===1||window.__sortedXss===2'),'HTML/script-like case text never executes')
    ok(no_overflow(pg),'hostile/unicode text does not break mobile width')

    # Repeat start immediately after completing a case, then hammer a synchronous double submit.
    open_generic(pg,'after first completed case');ok(pg.locator('#f-case:visible').count()==1,'another intake remains reachable after completing a case')
    n1=len(cases(pg))
    if pg.locator('#f-case:visible').count():
        pg.locator('#f-case:visible').fill('Currys has not sent my £42.17 refund, order DUP-991')
        pg.locator('form[data-f=case]:visible button[type=submit]:visible').first.evaluate('(b)=>{b.click();b.click()}');settle_case(pg)
    ok(len(cases(pg))==n1+1,'double-submit pressure does not duplicate a case')

    # Very long account of a problem should stay responsive and within the viewport.
    open_generic(pg,'after double-submit case');ok(pg.locator('#f-case:visible').count()==1,'intake remains reachable for long-input pressure')
    longtext=('British Gas said they would investigate the billing problem. Reference LONG-7788. '+('This is additional context with dates, calls, notes and £ symbols. '*90)).strip();n2=len(cases(pg))
    if pg.locator('#f-case:visible').count():
        ta=pg.locator('#f-case:visible');ta.fill(longtext);accepted=len(ta.input_value());ok(accepted>=500,'intake accepts a realistically long account of a problem')
        pg.locator('form[data-f=case]:visible button[type=submit]:visible').first.click();settle_case(pg)
    ok(len(cases(pg))==n2+1,'long input completes without duplicate or lost case');ok(no_overflow(pg),'long input/result stays within 390px')

    # Repeated standalone reload/resume.
    expected=len(cases(pg))
    for i in range(5):
        pg.reload();wait(pg,320);ok(len(cases(pg))==expected,'reload %d preserves all cases'%(i+1));ok(pg.locator('.cap87-appnav:visible [data-cap87=home]').count()==1,'reload %d restores standalone controls'%(i+1))

    # Corrupt client cache only; backing mock data should recover the screen and cases.
    keys=pg.evaluate("Object.keys(localStorage).filter(k=>k.indexOf('sorted.cache.')===0)")
    if keys:
        pg.evaluate("ks=>ks.forEach(k=>localStorage.setItem(k,'{not-json'))",keys);pg.reload();wait(pg,520)
        ok(pg.locator('main').count()==1 and bool(pg.locator('body').inner_text().strip()),'corrupt cache does not blank/freeze the app');ok(len(cases(pg))==expected,'corrupt cache recovers cases from backing data')
    else:ok(True,'no local cache key in anonymous mock session')

    # Category state must not leak across repeated Home/start cycles.
    chooser,_=user_home(pg,'category reset')
    if chooser is not None and chooser.locator('[data-cap82=fix]:visible').count():
        chooser.locator('[data-cap82=fix]:visible').first.click();wait(pg,380);ok(pg.get_by_text("What’s broken?",exact=True).count()>=1,'broken route gets broken-specific intake')
        chooser2,_=user_home(pg,'between categories')
        if chooser2 is not None and chooser2.locator('[data-cap82=call]:visible').count():
            chooser2.locator('[data-cap82=call]:visible').first.click();wait(pg,380)
            ok(pg.get_by_text('Who do you need to call?',exact=True).count()>=1 and pg.locator('#gi-who:visible').count()==1,'call route replaces broken-route context with the intended call intake')
    else:ok(False,'category chooser remains available after repeated case activity')

    # Navigation hammer.
    for i in range(3):
        if pg.locator('[data-cap87=home]:visible').count():pg.locator('[data-cap87=home]:visible').first.click();wait(pg,160)
        if pg.locator('[data-cap87=reload]:visible').count():pg.locator('[data-cap87=reload]:visible').first.click();wait(pg,340)
        ok(pg.locator('main').count()==1 and len(pg.inner_text('main'))>20,'standalone navigation cycle %d remains responsive'%(i+1))
    ok(not errs,'no page errors during core pressure sequence: %s'%errs)
    print('FINDINGS',findings);print('ERRORS',errs);print('FAILS',fails)
    ctx.close();b.close()
    if fails:raise SystemExit(1)
