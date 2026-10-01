import os, json
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from dates import A4,A5,A6,A10
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); O=HERE+'/tests/node_modules/'; errs=[]; fails=[]; hits=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=350): pg.wait_for_timeout(ms)
def cdn(r):
    u=r.request.url; hits.append(u.split('/npm/')[-1])
    if '/npm/tesseract.js@5.1.1/dist/' in u: return r.fulfill(path=O+'tesseract.js/dist/'+u.split('/dist/')[1], content_type='application/javascript', headers={'Access-Control-Allow-Origin':'*'})
    if '/npm/tesseract.js-core@5.1.1/' in u: f=u.split('@5.1.1/')[1]; return r.fulfill(path=O+'tesseract.js-core/'+f, content_type='application/wasm' if f.endswith('.wasm') else 'application/javascript', headers={'Access-Control-Allow-Origin':'*'})
    if '/npm/@tesseract.js-data/eng@1.0.0/' in u: return r.fulfill(path=O+'@tesseract.js-data/eng/4.0.0_best_int/eng.traineddata.gz', content_type='application/gzip', headers={'Access-Control-Allow-Origin':'*'})
    return r.fulfill(path=HERE+'/tests/mock.js', content_type='application/javascript')
with sync_playwright() as p:
    b=p.chromium.launch()
    # make a realistic SMS screenshot
    sp=b.new_page(viewport={'width':390,'height':300}); sp.set_content('<body style="margin:0;background:#fff;font-family:Arial"><div style="margin:20px;padding:14px 16px;background:#e9e9eb;border-radius:18px;font-size:17px;line-height:1.35;color:#111;max-width:320px">British Gas: Your engineer visit is booked for '+A5['long']+' between 8am and 12pm. Your reference is BG-77120. Reply STOP to opt out.</div></body>'); sp.screenshot(path=HERE+'/tests/out/sms.png'); sp.close()
    ctx=b.new_context(viewport={'width':390,'height':844})
    ctx.route('https://cdn.jsdelivr.net/**', cdn)
    ctx.route('https://fonts.googleapis.com/**', lambda r: r.fulfill(body='', content_type='text/css'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE+'/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    up=[]; ctx.on('request', lambda rq: up.append(rq.url) if rq.method=='POST' and 'sorted.test' not in rq.url else None)
    pg=ctx.new_page(); pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear()"); pg.reload(); wait(pg,800); print('ERR0',errs, hits, pg.inner_text('body')[:300]); pg.click('[data-a=anon-start]'); wait(pg)
    ok(pg.locator('input[data-ocr=f-case]').count()==1,'picture option on the start form')
    pg.set_input_files('input[data-ocr=f-case]', HERE+'/tests/out/sms.png')
    pg.wait_for_function("document.getElementById('ocr-status').textContent.startsWith('Done')||document.getElementById('ocr-status').textContent.startsWith('Sorted couldn')", timeout=90000)
    st=pg.inner_text('#ocr-status'); txt=pg.input_value('#f-case'); print('  status:',st); print('  text:',txt.replace('\n',' / '))
    ok(st.startswith('Done') and 'BG-77120' in txt.replace(' ',''),'screenshot read into the box')
    pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=safe-continue]').count(): pg.click('[data-a=safe-continue]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg)
    c=pg.locator('.sug').inner_text() if pg.locator('.sug').count() else ''; print('  card:',c.replace('\n',' | '))
    ok(A5['short'] in c and '08:00' in c and 'BG-77120' in c,'promise proposed from the screenshot')
    print('  cdn files:',sorted(set(hits)))
    print('  posts to other hosts:',[u for u in up if 'jsdelivr' in u])
    ok(not any('jsdelivr' in u for u in up),'picture not sent anywhere')
    b.close()
print('ERRORS',errs); print('FAILS',fails)
