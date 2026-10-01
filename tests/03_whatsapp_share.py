import os, json, urllib.parse
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]; wa=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=350): pg.wait_for_timeout(ms)
with sync_playwright() as p:
    b=p.chromium.launch()
    for scheme in ['light','dark']:
        ctx=b.new_context(viewport={'width':390,'height':844},color_scheme=scheme)
        ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE+'/tests/mock.js', content_type='application/javascript'))
        ctx.route('https://fonts.googleapis.com/**', lambda r: r.fulfill(body='', content_type='text/css'))
        ctx.route('https://wa.me/**', lambda r: (wa.append(r.request.url), r.fulfill(body='wa')))
        ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE+'/public/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
        pg=ctx.new_page(); pg.on('pageerror',lambda e: errs.append(str(e)))
        pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear()"); pg.reload(); wait(pg,200); pg.click('[data-a=anon-start]'); wait(pg)
        pg.click('[data-a=example]'); wait(pg); pg.click('.slip-open'); wait(pg)
        ok(pg.locator('[data-a=wa-share]').count()==0,scheme+': no WhatsApp button before a link exists')
        pg.evaluate("navigator.clipboard&&(navigator.clipboard.writeText=()=>Promise.resolve())")
        pg.click('[data-a=share]'); wait(pg)
        ok(pg.locator('[data-a=wa-share]').count()==1,scheme+': WhatsApp button once the link exists')
        href=pg.get_attribute('[data-a=wa-share]','href'); db=pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))")
        tok=db['shares'][0]['token']; txt=urllib.parse.unquote(href.split('text=')[1])
        ok(href.startswith('https://wa.me/?text=') and ('/?share='+tok) in txt,scheme+': message carries the live link')
        ok('Washing machine' not in txt and 'Oakridge' not in txt,scheme+': no case details go to WhatsApp')
        col=pg.evaluate("getComputedStyle(document.querySelector('[data-a=wa-share]')).color"); print('  colour',col)
        h=pg.evaluate("document.querySelector('[data-a=wa-share]').getBoundingClientRect().height"); ok(h>=44,scheme+': tap target %d'%h)
        with ctx.expect_page() as np: pg.click('[data-a=wa-share]')
        np.value.wait_for_load_state(); np.value.close(); wait(pg)
        pg.click('[data-a=wa-share]') if False else None
        m=pg.inner_text('main'); ok(m.count('Sent the helper link on WhatsApp')==1,scheme+': logged once')
        ok(len(wa)>=1,scheme+': WhatsApp opened')
        pg.screenshot(path=HERE+'/tests/out/wa29_'+scheme+'.png',full_page=False) if pg.locator('[data-a=wa-share]').scroll_into_view_if_needed() is None else None
        pg.click('[data-a=unshare]'); wait(pg)
        ok(pg.locator('[data-a=wa-share]').count()==0,scheme+': WhatsApp button gone once switched off')
        ctx.close()
    b.close()
print('ERRORS',errs); print('FAILS',fails)
