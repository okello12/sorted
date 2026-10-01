# v40: sharing into Sorted from another app (Apple Shortcut opens /#new=<text>). The page fills the box and waits:
# nothing is saved until Start, the text leaves the address bar, and it never goes to the server.
import os, sys, json, urllib.parse
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]; reqs=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=350): pg.wait_for_timeout(ms)
MSG="Hi, this is Currys. Your refund of £89 will be paid within 5 working days. Order 556677."
URL='https://sorted.test/?s=1#new='+urllib.parse.quote(MSG)
def ntasks(pg): return len(pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')||'{\"tasks\":[]}').tasks||[]"))
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE+'/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: (reqs.append(r.request.url), r.fulfill(path=HERE+'/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body='')))
    pg=ctx.new_page(); pg.on('pageerror',lambda e: errs.append(str(e)))
    # signed in already
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg,200); pg.click('[data-a=anon-start]'); wait(pg)
    n0=ntasks(pg)
    pg.goto(URL); wait(pg,600)
    ok(pg.input_value('#f-case')==MSG,'shared text fills the case box')
    ok('Shared into Sorted' in pg.inner_text('main') and 'Nothing is saved until you press Start' in pg.inner_text('main'),'says where it came from and that nothing is saved yet')
    ok(ntasks(pg)==n0,'no case is created by sharing alone')
    ok('#new=' not in pg.url,'the text is taken out of the address bar')
    ok(not any('£89' in u or '556677' in u or 'refund' in u for u in reqs),'the shared text never reaches the server')
    pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg)
    ok(ntasks(pg)==n0+1,'pressing Start makes the case')
    ok(pg.locator('.sug').count()==1 and '556677' in pg.inner_text('.sug'),'the promise card reads the shared message')
    pg.click('[data-a=sug-yes]'); wait(pg)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg,150)
    ok('Afterwards, Sorted brings this back to the top of your list and asks you: “Has the money arrived?”' in pg.inner_text('main'),'Waiting says when Sorted will check and what it will ask')
    pg.goto('https://sorted.test/'); wait(pg,500)
    ok(pg.locator('#f-case').count()==0 or pg.input_value('#f-case')!=MSG,'the shared text doesn’t come back after the case is made')
    # signed out: the text waits on this phone until they start
    pg2=ctx.new_page(); pg2.on('pageerror',lambda e: errs.append(str(e)))
    pg2.goto('https://sorted.test/'); pg2.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')")
    pg2.goto(URL); wait(pg2,500)
    ok('You don’t have to keep remembering whether they got back to you.' in pg2.inner_text('body'),'landing says the relief plainly')
    ok('#new=' not in pg2.url,'signed out: text taken out of the address bar')
    pg2.goto('https://sorted.test/#start'); wait(pg2,300); pg2.click('[data-a=anon-start]'); wait(pg2,500)
    ok(pg2.locator('#f-case').count()==1 and pg2.input_value('#f-case')==MSG,'signed out: after starting, the shared text is in the box')
    # a shared link while the page is already open
    pg2.evaluate("location.hash='#new='+encodeURIComponent('Landlord promised to fix the boiler by Friday')"); wait(pg2,500)
    ok(pg2.input_value('#f-case')=='Landlord promised to fix the boiler by Friday','a share while Sorted is open fills the box too')
    b.close()
print('ERRORS',errs); print('FAILS',fails)
