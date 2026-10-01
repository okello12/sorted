import os, json
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from dates import A4,A5,A6,A10
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
def task(pg,text): return pg.evaluate("(t)=>JSON.parse(localStorage.getItem('__mockdb')).tasks.map(x=>x.data).find(x=>x.said===t)",text)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE+'/tests/mock.js', content_type='application/javascript'))
    ctx.route('https://fonts.googleapis.com/**', lambda r: r.fulfill(body='', content_type='text/css'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE+'/public/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg,200); pg.click('[data-a=anon-start]'); wait(pg)
    # past promise -> chase
    T1="Currys promised a refund within 14 days, it's been three weeks, order 88421"; start(pg,T1)
    pg.click('[data-a=sug-yes]'); wait(pg)
    t=task(pg,T1); ok(t['promises'] and t['promises'][0]['status']=='missed' and t['sugDone'],'past: promise recorded and marked missed')
    a=pg.input_value('#f-ask'); print('  chase:',a); ok('A refund within 14 days' in a or 'refund within 14 days' in a.lower(),'chase quotes their words')
    ok(pg.locator('.sug').count()==0,'card gone after answering')
    pg.screenshot(path=HERE+'/tests/out/sug33_chase.png')
    # future promise -> waiting
    T2="British Gas said the engineer will come on Friday morning"; start(pg,T2)
    pg.locator('.sug').scroll_into_view_if_needed(); pg.screenshot(path=HERE+'/tests/out/sug33_card.png')
    pg.click('[data-a=sug-yes]'); wait(pg)
    t=task(pg,T2); ok(t['promises'][0]['status']=='open' and t['board']=='waiting','future: promise held, case waiting')
    pg.goto('https://sorted.test/'); wait(pg,400); m=pg.inner_text('main'); ok('Waiting' in m,'home shows it under Waiting')
    # edit -> promise form prefilled
    T3="Amazon told me the refund would be paid by "+A10["dm"]; start(pg,T3)
    pg.click('[data-a=sug-edit]'); wait(pg)
    ok(pg.input_value('#f-said')=='The refund would be paid by '+A10['dm'] and pg.input_value('#f-party2')=='Amazon' and pg.input_value('#f-date')==A10['iso'],'edit: promise form prefilled')
    # no -> dismissed
    T4="Sky charged me twice and said they'd refund it within 5 working days"; start(pg,T4)
    print('  card before:',pg.locator('.sug').count()); pg.click('[data-a=sug-no]'); wait(pg,1500); print('  card after:',pg.locator('.sug').count()); print('  keys:',sorted(task(pg,T4).keys()))
    t=task(pg,T4); ok(t['sugDone'] and not t['promises'] and pg.locator('.sug').count()==0,'not a promise: dismissed, nothing recorded')
    b.close()
print('ERRORS',errs); print('FAILS',fails)
