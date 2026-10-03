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
    if pg.locator('[data-a=match-new]').count():pg.locator('[data-a=match-new]').first.click();wait(pg,180)
    if pg.locator('[data-a=vague-go]').count():pg.locator('[data-a=vague-go]').first.click();wait(pg,180)
    if pg.locator('[data-a=safe-continue]').count():pg.locator('[data-a=safe-continue]').first.click();wait(pg,180)
    if pg.locator('form[data-f=baseline]').count():
        chips=pg.locator('form[data-f=baseline] .chip')
        if chips.count():chips.first.click()
        pg.locator('form[data-f=baseline] button[type=submit]').first.click();wait(pg,220)
    if pg.locator('[data-a=sug-yes]').count():pg.locator('[data-a=sug-yes]').first.click();wait(pg,180)
    if pg.get_by_text('Not now',exact=True).count():pg.get_by_text('Not now',exact=True).first.click();wait(pg,180)
def open_other(pg):
    # return to a start surface and open generic intake
    if pg.locator('[data-cap87=home]').count():pg.locator('[data-cap87=home]').click();wait(pg,250)
    else:pg.goto('https://sorted.test/');wait(pg,350)
    card=pg.locator('[data-cap82=other]').first
    if card.count():card.click();wait(pg,300)
    elif pg.locator('[data-a=compose]').count():pg.locator('[data-a=compose]').first.click();wait(pg,250)
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London',color_scheme='light')
    ctx.add_init_script("Object.defineProperty(navigator,'standalone',{configurable:true,get:()=>true})")
    ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
    ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url and 'manifest.webmanifest' not in r.request.url else r.fulfill(body='{}' if 'manifest.webmanifest' in r.request.url else ''))
    pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('https://sorted.test/#start');pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')");pg.reload();wait(pg,500)
    if pg.locator('[data-a=anon-start]').count():pg.locator('[data-a=anon-start]').click();wait(pg,500)
    ok(pg.locator('.cap87-appnav').count()==1,'standalone toolbar survives fresh launch')
    # Width pressure: app must not require horizontal scrolling at common narrow/wide mobile widths.
    for w in (320,360,390,430):
        pg.set_viewport_size({'width':w,'height':844});wait(pg,80);ok(no_overflow(pg),'no horizontal overflow at %spx'%w)
    pg.set_viewport_size({'width':390,'height':844})
    # Hostile-looking text must remain inert and one case must be created.
    open_other(pg);n0=len(cases(pg));hostile='<img src=x onerror="window.__sortedXss=1"> My landlord said the repair will be done Friday 😬 — ref A&B-123 <script>window.__sortedXss=2</script>'
    ok(pg.locator('#f-case').count()==1,'generic intake is reachable under standalone pressure')
    pg.fill('#f-case',hostile)
    pg.locator('form[data-f=case] button[type=submit]').first.click();settle_case(pg)
    ok(len(cases(pg))==n0+1,'hostile-looking input creates exactly one case')
    ok(not pg.evaluate('window.__sortedXss===1||window.__sortedXss===2'),'HTML/script-like case text never executes')
    ok(no_overflow(pg),'hostile/unicode text does not break mobile width')
    # Synchronous duplicate submit pressure. One user action should never become two cases.
    open_other(pg);n1=len(cases(pg));pg.fill('#f-case','Currys has not sent my £42.17 refund, order DUP-991')
    pg.locator('form[data-f=case] button[type=submit]').first.evaluate('(b)=>{b.click();b.click()}');settle_case(pg)
    ok(len(cases(pg))==n1+1,'double-submit pressure does not duplicate a case')
    # Very long input should not freeze the product, execute markup, or push the layout sideways.
    open_other(pg);longtext=('British Gas said they would investigate the billing problem. Reference LONG-7788. '+('This is additional context with dates, calls, notes and £ symbols. '*90)).strip()
    ta=pg.locator('#f-case');ta.fill(longtext);accepted=len(ta.input_value())
    ok(accepted>500,'intake accepts a realistically long account of a problem')
    n2=len(cases(pg));pg.locator('form[data-f=case] button[type=submit]').first.click();settle_case(pg)
    ok(len(cases(pg))==n2+1,'long input completes without duplicate or lost case')
    ok(no_overflow(pg),'long input/result stays within 390px')
    # Repeated reloads/resumes must preserve the same number of cases and keep navigation alive.
    expected=len(cases(pg))
    for i in range(5):
        pg.reload();wait(pg,260)
        ok(len(cases(pg))==expected,'reload %d preserves all cases'%(i+1))
        ok(pg.locator('.cap87-appnav [data-cap87=home]').count()==1,'reload %d restores standalone controls'%(i+1))
    # Corrupt only the client cache; backing mock data should allow a clean recovery rather than a frozen screen.
    keys=pg.evaluate("Object.keys(localStorage).filter(k=>k.indexOf('sorted.cache.')===0)")
    if keys:
        pg.evaluate("ks=>ks.forEach(k=>localStorage.setItem(k,'{not-json'))",keys);pg.reload();wait(pg,450)
        ok(pg.locator('main').count()==1 and not pg.locator('body').inner_text().strip()=='','corrupt cache does not blank/freeze the app')
        ok(len(cases(pg))==expected,'corrupt cache recovers cases from backing data')
    else:ok(True,'no local cache key in anonymous mock session')
    # Category state must not leak between starts after Home/back navigation.
    home=pg.locator('[data-cap87=home]')
    if home.count():home.click();wait(pg,220)
    fix=pg.locator('[data-cap82=fix]').first
    if fix.count():
        fix.click();wait(pg,320);ok(pg.get_by_text("What’s broken?",exact=True).count()>=1,'broken route gets broken-specific intake under repeated use')
        pg.locator('[data-cap87=home]').click();wait(pg,220)
        call=pg.locator('[data-cap82=call]').first
        if call.count():call.click();wait(pg,320);ok(pg.get_by_text("What’s the call about?",exact=True).count()>=1,'call route replaces stale broken-route context')
    # Hammer app-home/reload controls a few times; no page errors or frozen body.
    for i in range(3):
        if pg.locator('[data-cap87=home]').count():pg.locator('[data-cap87=home]').click();wait(pg,120)
        if pg.locator('[data-cap87=reload]').count():pg.locator('[data-cap87=reload]').click();wait(pg,280)
        ok(pg.locator('main').count()==1 and len(pg.inner_text('main'))>20,'standalone navigation cycle %d remains responsive'%(i+1))
    ok(not errs,'no page errors during core pressure sequence: %s'%errs)
    ctx.close();b.close()
print('ERRORS',errs);print('FAILS',fails)
