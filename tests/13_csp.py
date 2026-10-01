# The production Content-Security-Policy (from vercel.json) must not block anything the app does.
import os, sys, json, datetime
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from dates import ahead
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); O=HERE+'/tests/node_modules/'; errs=[]; fails=[]; csp=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=350): pg.wait_for_timeout(ms)
CSP=[h['value'] for h in json.load(open(HERE+'/vercel.json'))['headers'][0]['headers'] if h['key']=='Content-Security-Policy'][0]
H={'Access-Control-Allow-Origin':'*'}
def cdn(r):
    u=r.request.url
    if '/npm/tesseract.js@5.1.1/dist/' in u: return r.fulfill(path=O+'tesseract.js/dist/'+u.split('/dist/')[1], content_type='application/javascript', headers=H)
    if '/npm/tesseract.js-core@5.1.1/' in u: f=u.split('@5.1.1/')[1]; return r.fulfill(path=O+'tesseract.js-core/'+f, content_type='application/wasm' if f.endswith('.wasm') else 'application/javascript', headers=H)
    if '/npm/@tesseract.js-data/eng@1.0.0/' in u: return r.fulfill(path=O+'@tesseract.js-data/eng/4.0.0_best_int/eng.traineddata.gz', content_type='application/gzip', headers=H)
    if '/npm/pdfjs-dist@3.11.174/build/' in u: return r.fulfill(path=O+'pdfjs-dist/build/'+u.split('/build/')[1], content_type='application/javascript', headers=H)
    return r.fulfill(path=HERE+'/tests/mock.js', content_type='application/javascript')
with sync_playwright() as p:
    b=p.chromium.launch()
    A=ahead(5); os.makedirs(HERE+'/tests/out',exist_ok=True)
    sp=b.new_page(viewport={'width':390,'height':260}); sp.set_content('<body style="margin:0;background:#fff;font-family:Arial"><div style="margin:20px;padding:14px;background:#e9e9eb;border-radius:18px;font-size:17px">Your engineer visit is booked for %s between 8am and 12pm. Ref BG-1234.</div></body>'%A['long']); sp.screenshot(path=HERE+'/tests/out/csp_sms.png')
    sp.set_content('<body style="font-family:Arial;padding:40px"><p>Currys: your refund has been processed and will be paid by %s. Order 556677. Thank you for shopping with us.</p></body>'%A['dm']); sp.pdf(path=HERE+'/tests/out/csp.pdf'); sp.close()
    ctx=b.new_context(viewport={'width':390,'height':844})
    ctx.route('https://cdn.jsdelivr.net/**', cdn)
    ctx.route('https://fonts.googleapis.com/**', lambda r: r.fulfill(body='', content_type='text/css'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE+'/public/index.html', content_type='text/html', headers={'Content-Security-Policy':CSP}) if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.on('console',lambda m: csp.append(m.text) if 'Content Security Policy' in m.text or 'Refused to' in m.text else None)
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear()"); pg.reload(); wait(pg,300); pg.click('[data-a=anon-start]'); wait(pg)
    ok(pg.locator('#f-case').count()==1,'app starts under the CSP')
    pg.set_input_files('input[data-ocr=f-case]', HERE+'/tests/out/csp_sms.png')
    for i in range(240):
        st=pg.inner_text('#ocr-status')
        if st.startswith('Done') or st.startswith('Sorted couldn'): break
        wait(pg,500)
    ok(st.startswith('Done') and 'BG-1234' in pg.input_value('#f-case').replace(' ',''),'screenshot reading works under the CSP')
    pg.fill('#f-case','')
    pg.set_input_files('input[data-ocr=f-case]', HERE+'/tests/out/csp.pdf')
    for i in range(120):
        st=pg.inner_text('#ocr-status')
        if (st.startswith('Done') and '556677' in pg.input_value('#f-case')) or st.startswith('Sorted couldn'): break
        wait(pg,500)
    ok('556677' in pg.input_value('#f-case'),'PDF reading works under the CSP')
    pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg)
    ok(pg.locator('.sug').count()==1,'promise card works under the CSP')
    print('  CSP messages:',csp[:5]); ok(not csp,'nothing blocked by the CSP')
    b.close()
print('ERRORS',errs); print('FAILS',fails)
