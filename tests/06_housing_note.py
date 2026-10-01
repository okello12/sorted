import os, json
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=350): pg.wait_for_timeout(ms)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE+'/tests/mock.js', content_type='application/javascript'))
    ctx.route('https://fonts.googleapis.com/**', lambda r: r.fulfill(body='', content_type='text/css'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE+'/public/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear()"); pg.reload(); wait(pg,200); pg.click('[data-a=anon-start]'); wait(pg)
    pg.fill('#f-case',"Landlord still hasn't fixed the heating, boiler off for two weeks"); pg.click('form[data-f=case] button'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg)
    pg.click('form[data-f=what] button[type=submit]'); wait(pg)
    pg.click('form[data-f=who] button[type=submit]'); wait(pg)
    pg.click('text=Get the report ready'); wait(pg)
    ask=pg.input_value('#f-ask'); who=pg.input_value('#f-who'); print('who:',who,'| ask:',ask)
    ok('two weeks' in ask and who=='My landlord','report says how long and goes to the landlord')
    ok('If your landlord still' not in pg.inner_text('main'),'no housing note before anything is missed')
    pg.click('form[data-f=call] button[type=submit]'); wait(pg)
    # a promise they gave, now missed
    pg.evaluate("""()=>{var db=JSON.parse(localStorage.getItem('__mockdb'));var t=db.tasks[0].data;var d=new Date(Date.now()-2*864e5);
      t.promises=[{id:'p1',said:'An engineer will come',party:'Landlord',dueAt:d.toISOString(),allDay:true,by:false,status:'open',loggedAt:new Date(Date.now()-5*864e5).toISOString()}];
      localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}""")
    pg.goto('https://sorted.test/'); wait(pg,600); pg.locator('[data-a=open]').first.click(); wait(pg); pg.click('[data-a=missed]'); wait(pg)
    if pg.locator('form[data-f=call]').count()==0 and pg.locator('text=Chase it up').count(): pg.click('text=Chase it up'); wait(pg)
    print(pg.inner_text('main')[:700]); print([pg.locator('[data-a]').nth(i).get_attribute('data-a') for i in range(min(15,pg.locator('[data-a]').count()))])
    print('ASK:', pg.input_value('#f-ask') if pg.locator('#f-ask').count() else 'no ask field')
    m=pg.inner_text('main'); ok('If your landlord still' in m and 'Shelter' in m,'housing note after the landlord missed it')
    ok('an engineer will come' in pg.input_value('#f-ask').lower() if pg.locator('#f-ask').count() else False,'chase quotes their promise')
    pg.locator('.note').last.scroll_into_view_if_needed(); pg.screenshot(path=HERE+'/tests/out/house31.png')
    b.close()
print('ERRORS',errs); print('FAILS',fails)
