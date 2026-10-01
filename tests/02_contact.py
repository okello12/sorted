import os
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE+'/tests/mock.js', content_type='application/javascript'))
    ctx.route('https://fonts.googleapis.com/**', lambda r: r.fulfill(body='', content_type='text/css'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE+'/public/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e: errs.append(str(e)))
    for where in ['','#start','#signin','#privacy']:
        pg.goto('about:blank'); pg.goto('https://sorted.test/'+where); pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(300)
        n=pg.locator('a[href="mailto:kofiniiakwei@gmail.com"]').count(); ok(n>=1,'%s: contact link shown (%d)'%(where or 'landing',n))
    m=pg.inner_text('main'); ok('by emailing kofiniiakwei@gmail.com' in m and 'Contact him at kofiniiakwei@gmail.com' in m,'full notice: contact in Who runs it and Your rights')
    pg.goto('https://sorted.test/#start'); pg.click('[data-a=anon-start]'); pg.wait_for_timeout(400); pg.click('[data-a=data]'); pg.wait_for_timeout(300)
    ok('by emailing kofiniiakwei@gmail.com' in pg.inner_text('main'),'Your data shows the contact')
    b.close()
print('ERRORS',errs); print('FAILS',fails)
