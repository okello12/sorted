import os, datetime
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=300): pg.wait_for_timeout(ms)

def setup(p,scheme='light'):
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London',color_scheme=scheme)
    ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
    ctx.route('https://fonts.googleapis.com/**',lambda r:r.fulfill(body='',content_type='text/css'))
    ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg); pg.click('[data-a=anon-start]'); wait(pg)
    return b,ctx,pg

with sync_playwright() as p:
    b,ctx,pg=setup(p)
    pg.click('[data-a=example]'); wait(pg); pg.click('.slip-open'); wait(pg)
    ok(pg.locator('main.case56').count()==1,'case detail uses compact shell')
    ok(pg.get_by_role('heading',name='Messages & evidence').count()==1,'messages and evidence has its own section')
    ok(pg.get_by_role('heading',name='Timeline').count()==1,'timeline replaces the raw audit-log heading')
    ok(pg.locator('text=What’s happened so far').count()==0,'old audit-log heading is gone')
    ok(not pg.locator('.case56-sharing').evaluate('(x)=>x.open'),'sharing is collapsed by default')
    ok(not pg.locator('.case56-more').evaluate('(x)=>x.open'),'finish and delete controls are collapsed under More')
    pg.locator('.case56-sharing > summary').click(); wait(pg,100)
    ok(pg.locator('.case56-sharing [data-a=share]').is_visible(),'share action remains available after opening Sharing')
    pg.locator('.case56-more > summary').click(); wait(pg,100)
    ok(pg.locator('.case56-more [data-p=done]').is_visible(),'finish action remains available under More')

    # Create a real move through the product and exercise the compact Next UI against real stored data.
    pg.click('[data-a=panel][data-p=move]'); wait(pg,120)
    pg.fill('#f-mwhat','Remind to apply for it')
    due=datetime.date.today()+datetime.timedelta(days=22)
    for part,v in [('d',due.day),('m',due.month),('y',due.year)]: pg.select_option('select[data-dp=f-mdate][data-part=%s]'%part,str(v))
    pg.click('form[data-f=move] button[type=submit]'); wait(pg,350)
    ok(pg.locator('.case56-next').count()==1,'real move renders in the compact Next card')
    ok(pg.locator('.case56-next .case56-overline').inner_text().strip().lower()=='next','next card uses one clear state label')
    ok('Remind to apply for it' in pg.locator('.case56-next h2').inner_text(),'next card names the action directly')
    ok(pg.locator('.case56-next').get_by_text('Your move',exact=True).count()==0,'next card does not repeat Your move')
    ok(pg.locator('.case56-next [data-a=move-done]').is_visible(),'primary completion action remains prominent')
    ok(pg.locator('.case56-next .case56-reminders').count()==1 and not pg.locator('.case56-next .case56-reminders').evaluate('(x)=>x.open'),'calendar and email machinery is folded under Reminders')

    # Convert the same mock row to a legacy driving-licence renewal. This fixture checks renewal presentation only.
    pg.evaluate("""()=>{
      var db=JSON.parse(localStorage.getItem('__mockdb')),row=db.tasks.find(x=>x.data&&x.data.example),t=row.data;
      t.example=false;t.title='My driving licence';t.mode='renew';t.board='yours';t.promises=[];t.moves=[];t.call=null;t.fix=null;
      t.renew={kind:'licence',step:'done',expiry:'2026-04-25',applied:false,provider:'DVLA',how:'self'};
      t.events=[
        {at:'2026-09-30T08:10:00.000Z',label:'Application date confirmed for 24 Oct.'},
        {at:'2026-09-30T08:00:00.000Z',label:'Tapped add to Google Calendar.'},
        {at:'2026-09-30T07:50:00.000Z',label:'Email reminders on (the default). You can turn them off.'},
        {at:'2026-09-28T12:00:00.000Z',label:'Your move: Remind to apply for it (by Sat 24 Oct).'},
        {at:'2026-09-28T11:58:00.000Z',label:'Ends Sat 25 Apr. Start by Thu 26 Mar.'},
        {at:'2026-09-28T11:55:00.000Z',label:'Renewing: Driving licence.'},
        {at:'2026-09-28T11:50:00.000Z',label:'Started. Before any advice, the plan was: “I need to apply for it”'}
      ];
      localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k));
    }""")
    pg.reload(); wait(pg,500)
    # Reload returns to Home. Re-open the only case; Home may present a cleaned title such as "Driving licence".
    if pg.locator('main.case56').count()==0:
        row=pg.locator('[data-a=open]').first
        if not row.count(): row=pg.locator('.slip-open').first
        ok(row.count()==1,'renewal case is present on Home after reload')
        if row.count(): row.click(); wait(pg,350)
    main=pg.inner_text('main')
    ok('driving licence' in main.lower(),'legacy renewal keeps a clear driving-licence title')
    renew=pg.inner_text('.case56-renew-state')
    ok('driving licence' in renew.lower() and 'expired' in renew.lower(),'renewal state is compact and clear')
    official=pg.inner_text('.case56-official')
    ok('Renew on GOV.UK' in official and 'Open GOV.UK' in official,'official route is the main renewal guidance')
    ok(not pg.locator('.case56-official .case56-fold').evaluate('(x)=>x.open'),'extra GOV.UK guidance is collapsed')
    ok(pg.locator('.case56-official [data-a=applied]').is_visible() and pg.locator('.case56-official [data-p=renewed]').is_visible(),'renewal outcome actions remain available when there is no separate move')

    timeline=pg.locator('#case56-timeline').locator('xpath=ancestor::section[1]')
    txt=timeline.inner_text()
    ok('Application date confirmed for 24 Oct.' in txt,'timeline keeps a meaningful case update')
    hidden=['Tapped add to Google Calendar','Email reminders on','Your move:','Ends Sat 25 Apr','Before any advice','Renewing:']
    ok(all(x not in txt for x in hidden),'timeline hides system and already-presented state noise by default')
    ok(timeline.locator('details.case56-fold').count()==1 and not timeline.locator('details.case56-fold').evaluate('(x)=>x.open'),'full audit history is retained but collapsed')
    timeline.locator('details.case56-fold > summary').click(); wait(pg,80)
    txt2=timeline.inner_text()
    ok('Tapped add to Google Calendar' in txt2 and 'Email reminders on' in txt2 and 'Your move:' in txt2,'full history still contains the audit trail')

    pg.evaluate("document.documentElement.style.fontSize='200%'"); wait(pg,120)
    d=pg.evaluate("({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth})")
    ok(d['sw']<=d['cw']+3,'200 percent text has no horizontal page overflow')
    pg.evaluate("document.documentElement.style.fontSize=''"); wait(pg,80)
    pg.screenshot(path=HERE+'/tests/out/case56-light.png',full_page=True)
    b.close()

print('ERRORS',errs); print('FAILS',fails)
