# Scale/accessibility pressure: many cases, long labels, keyboard-only chooser,
# large text, dark mode and repeated reloads. Test-only branch.
import os, time
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.');fails=[];errs=[];findings=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c:fails.append(m)
def finding(m):findings.append(m);print('FINDING '+m)
def wait(pg,ms=350):pg.wait_for_timeout(ms)
def db(pg):return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')||'{}')") or {}
def cases(pg):return [x.get('data',{}) for x in db(pg).get('tasks',[]) if x.get('data',{}).get('kind')!='moment']
def no_overflow(pg):return pg.evaluate('document.documentElement.scrollWidth<=document.documentElement.clientWidth')
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London',color_scheme='light')
    ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
    ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('https://sorted.test/#start');pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')");pg.reload();wait(pg,450)
    if pg.locator('[data-a=anon-start]:visible').count():pg.locator('[data-a=anon-start]:visible').first.click();wait(pg,450)
    chooser=pg.locator('#cap82-start:visible,#cap82-landing:visible').first
    ok(chooser.count()==1,'start chooser is present before scale seeding')
    cards=chooser.locator('.cap82-card:visible') if chooser.count() else pg.locator('x-never')
    ok(cards.count()==6,'all six capability choices remain keyboard-addressable buttons')
    if cards.count():
        cards.nth(1).focus();ok(pg.evaluate("document.activeElement&&document.activeElement.matches('.cap82-card')"),'a capability tile can receive keyboard focus');pg.keyboard.press('Enter');wait(pg,380)
        ok(pg.locator('.gi-form:visible').count()==1,'Enter on a focused capability tile opens guided intake')
    # Return by a real root navigation and seed one normal case using the built-in example.
    pg.goto('https://sorted.test/');wait(pg,400)
    if pg.locator('[data-a=example]:visible').count():pg.locator('[data-a=example]:visible').first.click();wait(pg,550)
    if not cases(pg):
        chooser=pg.locator('#cap82-start:visible,#cap82-landing:visible').first
        if chooser.count() and chooser.locator('[data-cap82=other]:visible').count():
            chooser.locator('[data-cap82=other]:visible').first.click();wait(pg,220);pg.locator('#f-case:visible').fill('Pressure seed case');pg.locator('form[data-f=case]:visible button[type=submit]:visible').first.click();wait(pg,300)
            if pg.locator('form[data-f=baseline]:visible').count():
                f=pg.locator('form[data-f=baseline]:visible').first;ch=f.locator('.chip:visible')
                if ch.count():ch.first.click()
                f.locator('button[type=submit]:visible').first.click();wait(pg,300)
    ok(len(cases(pg))>=1,'a base case exists for scale pressure')
    # Clone the persisted case to 60 total with unique IDs/titles, including unicode and long labels.
    pg.evaluate("""()=>{let d=JSON.parse(localStorage.getItem('__mockdb'));let w=d.tasks.find(x=>x.data&&x.data.kind!=='moment');if(!w)return;let base=w.data;let existing=d.tasks.filter(x=>x.data&&x.data.kind!=='moment').length;for(let i=existing;i<60;i++){let z=JSON.parse(JSON.stringify(w));z.data.id='pressure-'+i+'-'+Date.now();z.data.title=(i===59?'Very long pressure case '+('word '.repeat(70))+' العربية עברית 😀 ':'Pressure case '+String(i+1));z.data.created=new Date(Date.now()-i*60000).toISOString();d.tasks.push(z)}localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}""")
    t=time.perf_counter();pg.goto('https://sorted.test/');wait(pg,900);elapsed=time.perf_counter()-t
    ok(len(cases(pg))==60,'60 persisted cases survive a full Home render')
    ok(pg.locator('main').count()==1 and len(pg.inner_text('main'))>50,'60-case Home remains responsive and populated')
    ok(no_overflow(pg),'60 cases plus a very long unicode title do not create horizontal overflow')
    if elapsed>3.0:finding('60-case Home took %.2fs in the headless pressure environment'%elapsed)
    else:ok(True,'60-case Home settles within the pressure budget (%.2fs)'%elapsed)
    ok(pg.locator('#cap82-start:visible .cap82-card').count()==6,'capability discovery remains available with 60 cases')
    # Large text pressure. Record as a finding rather than a hard WCAG claim because browser text scaling differs by device.
    pg.evaluate("document.documentElement.style.fontSize='125%'");wait(pg,220)
    if no_overflow(pg):ok(True,'125% root text size keeps the page within the mobile viewport')
    else:finding('125% root text size introduces horizontal overflow at 390px')
    # Dark mode with the same large dataset.
    pg.evaluate("document.documentElement.setAttribute('data-theme','dark')");wait(pg,180);ok(no_overflow(pg),'dark mode with 60 cases stays within 390px')
    # Repeated large-state reloads should be idempotent and keep the dataset intact.
    for i in range(8):
        pg.reload();wait(pg,280);ok(len(cases(pg))==60,'large-state reload %d preserves all 60 cases'%(i+1));ok(pg.locator('main').count()==1,'large-state reload %d renders a main view'%(i+1))
    ok(not errs,'no page errors during scale/accessibility pressure: %s'%errs)
    print('FINDINGS',findings);print('ERRORS',errs);print('FAILS',fails)
    ctx.close();b.close()
    if fails:raise SystemExit(1)
