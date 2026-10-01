import os
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=350): pg.wait_for_timeout(ms)
def start(pg,text):
    pg.goto('https://sorted.test/'); wait(pg,400)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg,150)
    pg.fill('#f-case',text); pg.click('form[data-f=case] button'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=sug-no]').count(): pg.click('[data-a=sug-no]'); wait(pg)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE+'/tests/mock.js', content_type='application/javascript'))
    ctx.route('https://fonts.googleapis.com/**', lambda r: r.fulfill(body='', content_type='text/css'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE+'/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear()"); pg.reload(); wait(pg,200); pg.click('[data-a=anon-start]'); wait(pg)
    # heating, phrased differently
    start(pg,"Landlord still hasn't fixed the heating, boiler's been off two weeks, house freezing")
    pg.click('form[data-f=what] button[type=submit]'); wait(pg); pg.click('form[data-f=who] button[type=submit]'); wait(pg)
    pg.click('text=Get the report ready'); wait(pg); a=pg.input_value('#f-ask'); print('ASK:',a)
    ok('It has been like this for two weeks' in a,'heating report says two weeks')
    # gas stop screen leads with gas
    start(pg,"Boiler not working, landlord won't answer")
    pg.click('form[data-f=what] [data-a=unsafe]'); wait(pg)
    lis=pg.locator('.safety li').all_inner_texts(); ok(lis and lis[0].startswith('Smell gas'),'heating stop screen leads with gas')
    start(pg,"Washing machine stopped draining")
    pg.click('[data-k=fault][data-v=drain]'); pg.click('form[data-f=what] [data-a=unsafe]'); wait(pg)
    lis=pg.locator('.safety li').all_inner_texts(); ok(lis and lis[0].startswith('If you can reach the socket'),'washing machine stop screen leads with the socket')
    # British Gas: someone else, plain advice; landlord choice clears the guessed company
    start(pg,"British Gas engineer didn't turn up to fix the boiler")
    pg.click('form[data-f=what] button[type=submit]'); wait(pg)
    ok(pg.input_value('#f-party')=='British Gas' if pg.locator('#f-party').count() else True,'British Gas offered as who')
    pg.click('[data-k=responsible][data-v=landlord]'); wait(pg,150)
    ok(pg.input_value('#f-party')=='','choosing landlord clears the guessed company')
    pg.click('[data-k=responsible][data-v=other]'); wait(pg,150); pg.fill('#f-party','British Gas')
    pg.click('form[data-f=who] button[type=submit]'); wait(pg)
    m=pg.inner_text('main'); i=m.find('OUR SUGGESTION'); print(m[i:i+300])
    ok('supplied' not in m and 'British Gas' in m,'someone-else advice has no landlord framing')
    b.close()
print('ERRORS',errs); print('FAILS',fails)
