# v75/v76: case UI consolidation. Current state stays first; the record and tools fold away.
import os
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=350): pg.wait_for_timeout(ms)
def clear_cache(pg):
    pg.evaluate("Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))")
def task0(pg):
    return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks[0].data")
def start_case(pg,text):
    pg.goto('https://sorted.test/'); wait(pg,350)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
    pg.fill('#f-case',text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count():
        pg.locator('form[data-f=baseline] .chip').first.click(); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg,450)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London',color_scheme='light')
    ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
    ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))

    # Landing hierarchy: the product promise is the headline, the generic line is secondary.
    pg.goto('https://sorted.test/'); wait(pg,250)
    ok('They said Tuesday.' in pg.inner_text('.hero .h1') and 'Sorted remembers Tuesday.' in pg.inner_text('.hero .h1'),'landing uses the sharp promise as the headline')
    ok('Life gets messy. Sorted keeps up.' in pg.inner_text('.hero .eyebrow'),'generic landing line is secondary')
    choices=pg.evaluate("planChoices('call','Currys refund')")
    ok('Ask where the refund is' in choices and 'Try to fix it myself' not in choices,'research baseline choices fit a refund case')

    # Anonymous Home warning: full once, then one slim line.
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg,200); pg.click('[data-a=anon-start]'); wait(pg)
    pg.click('[data-a=example]'); wait(pg,450)
    ok(pg.locator('.note').filter(has_text='Without an email, only this phone can open your cases.').count()==1,'no-email warning is full on first exposure')
    ok(pg.locator('.case75-email-slim').count()==0,'slim warning is not shown at the same time')
    pg.reload(); wait(pg,450)
    ok(pg.locator('.case75-email-slim').count()==1,'later visits get the slim no-email line')
    ok(pg.locator('.note').filter(has_text='Without an email, only this phone can open your cases.').count()==0,'large no-email warning does not dominate later visits')

    # Title/reference separation and the two-group case hierarchy.
    pg.evaluate("""()=>{var db=JSON.parse(localStorage.getItem('__mockdb'));var t=db.tasks[0].data;t.title='Currys refund · 445566';localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}""")
    pg.reload(); wait(pg,350)
    tid=task0(pg)['id']; pg.locator('[data-a=open][data-id="%s"]'%tid).first.click(); wait(pg,400)
    ok(pg.inner_text('.case56-title').strip()=='Currys refund','case heading keeps the reference out of the title')
    ok(pg.inner_text('.case75-title-ref').strip()=='Ref 445566','reference sits on its own smaller line')
    groups=pg.locator('details.case75-group')
    ok(groups.count()==2,'case has only two top-level secondary groups')
    ok('What’s happened' in groups.nth(0).inner_text() and 'Tools for this case' in groups.nth(1).inner_text(),'secondary content is grouped as What’s happened and Tools for this case')
    ok(not groups.nth(0).get_attribute('open') and not groups.nth(1).get_attribute('open'),'both secondary groups start collapsed')

    # A confirmed promise stays above the email setup prompt.
    open_said=pg.evaluate("openPromise(task(S.view.id)).said")
    pg.evaluate("S.view.panel='claim';render()") ; wait(pg,200)
    claim=pg.locator('#claim'); promise_text=pg.get_by_text(open_said,exact=True).first
    ok(claim.count()==1 and promise_text.count()==1,'claim screen still shows the promise being held')
    if claim.count() and promise_text.count():
        ok(promise_text.bounding_box()['y'] < claim.bounding_box()['y'],'promise is above the email setup prompt')
    ok('Add email reminders?' in claim.inner_text() and 'promise is already saved' in claim.inner_text().lower(),'email prompt is clearly optional after the promise is saved')

    # An incoming reply keeps the old promise in view and does not hide the rest of the case.
    pg.evaluate("""()=>{var t=task(S.view.id);S.view.panel=null;S.cxAt=S.cxAt||{};S.cxAt[t.id]=Date.now();S.caseMail={};S.caseMail[t.id]=[{id:'mail-1',subject:'Refund update',body:'We have looked at your refund and will write again.',received_at:new Date().toISOString(),from_domain:'currys.co.uk'}];render()}""") ; wait(pg,200)
    ok(pg.locator('.cm-card .case75-promise-context').count()==1,'reply card includes what Sorted was already holding')
    if pg.locator('.cm-card .case75-promise-context').count():
        ok(open_said in pg.inner_text('.cm-card .case75-promise-context'),'reply can be judged against the earlier promise')
    ok(pg.locator('details.case75-group').count()==2,'reply no longer hides the rest of the case')

    # Secondary actions share one quiet row treatment.
    pg.locator('details.case75-tools > summary').click(); wait(pg,100)
    links=pg.locator('details.case75-tools .case75-group-body > section .link')
    if links.count():
        ok(pg.evaluate("e=>getComputedStyle(e).textDecorationLine",links.first.element_handle())=='none','secondary action rows use one quiet, non-underlined treatment')
    else:
        ok(False,'secondary action row is available inside Tools')

    # Parking: Not now stays a parking state rather than falling into the generic contact form.
    pg.click('[data-a=home]'); wait(pg,250)
    pcn='Southwark Council PENALTY CHARGE NOTICE PCN Number: SK12345678 Vehicle Registration Mark: AB12 CDE Date of notice: 29/09/2026 The penalty charge is £130. Reduced to £65 if paid within 14 days.'
    start_case(pg,pcn)
    ok(pg.locator('[data-a=cf-later]').count()==1,'parking details can be deferred')
    pg.click('[data-a=cf-later]'); wait(pg,250)
    ok(pg.locator('.case75-parking-pending').count()==1,'deferred parking details stay in a parking-specific state')
    ok(pg.locator('form[data-f=call]').count()==0,'deferred parking notice does not fall back to Who are you contacting')
    if pg.locator('.case75-parking-pending').count():
        tx=pg.inner_text('.case75-parking-pending')
        ok('Parking notice' in tx and 'Nothing counts until you confirm it.' in tx,'parking pending card explains what remains to check')

    b.close()
print('ERRORS',errs); print('FAILS',fails)
