# v131: Baldwin's iPhone (Safari) could not leave a case or get Home. This walks the same state in a touch phone
# (iPhone in WebKit on GitHub; a touch Chromium here): an old "Evri said they would Nothing" case with the call panel
# open, then every way out by tapping (the bar's Home, Cases, More, New; the top "← Home"; Open this case and back),
# printing what the page did after each tap so a failure says why.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]; logs = []
ENGINE = os.environ.get('SORTED_ENGINE', 'chromium')
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + ENGINE + ': ' + m)
    if not c: fails.append(ENGINE + ': ' + m)
def wait(pg, ms=600): pg.wait_for_timeout(ms)
with sync_playwright() as p:
    dev = dict(p.devices['iPhone 13']) if ENGINE == 'webkit' else {'viewport': {'width': 390, 'height': 844}, 'has_touch': True, 'is_mobile': True}
    if ENGINE == 'firefox': dev.pop('is_mobile', None)
    dev.pop('default_browser_type', None)
    b = getattr(p, ENGINE).launch(); ctx = b.new_context(timezone_id='Europe/London', color_scheme='dark', **dev)
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: logs.append(m.type + ' ' + m.text) if m.type in ('error', 'warning') else None)
    def state(): return pg.evaluate("({url:location.href.slice(-28),view:(function(){var m=document.querySelector('main');m=m?m.className:'';return /home44/.test(m)?'home':/case56/.test(m)?'task':/cases129/.test(m)?'cases':/acct112/.test(m)?'data':m})(),main:(document.querySelector('main')||{}).className||'',h1:((document.querySelector('main h1')||{}).textContent||'').slice(0,40),top:(function(){var b=document.querySelector('.tab129 [data-a=go-home]');if(!b)return 'no bar';var r=b.getBoundingClientRect(),e=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);return e?(e.closest('[data-a]')?e.closest('[data-a]').getAttribute('data-a'):e.tagName+'.'+e.className):'none'})()})")
    def tap(sel, what):
        try:
            pg.locator(sel).first.tap(timeout=5000)
        except Exception as e:
            print('TAP ERROR', what, str(e).splitlines()[0][:200])
        wait(pg, 700); s = state(); print('after', what, s); return s
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg)
    pg.locator('[data-a=anon-start]').first.tap(); wait(pg, 900)
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.fill('#f-case', 'Evri lost my parcel'); pg.locator('form[data-f=case] button[type=submit]').last.tap(); wait(pg, 800)
    if pg.locator('form[data-f=baseline]').count(): pg.locator('form[data-f=baseline] .chip').first.tap(); pg.locator('form[data-f=baseline] button[type=submit]').tap(); wait(pg, 700)
    pg.evaluate("(()=>{var db=JSON.parse(localStorage.getItem('__mockdb'));db.tasks.forEach(r=>{r.data.title='Evri said they would Nothing';r.data.said='Evri said they would Nothing'});localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))})()")
    pg.goto('https://sorted.test/'); wait(pg, 900); print('home', state())
    s = tap('.home44-spot [data-a=open]', 'Open this case'); ok(s['view'] == 'task', 'Open this case opens the case')
    if not pg.locator('form[data-f=call]').count() and pg.locator('[data-a=panel][data-p=call]').count(): tap('[data-a=panel][data-p=call]', 'Get the call ready')
    print('call form open:', pg.locator('form[data-f=call]').count())
    s = tap('.tab129 [data-a=go-home]', 'bar Home'); ok(s['view'] == 'home' and 'home44' in s['main'], 'the bar’s Home leaves the case (%s)' % s)
    tap('.home44-spot [data-a=open]', 'Open this case again')
    s = tap('.bar [data-a=home]', 'top ← Home'); ok(s['view'] == 'home', 'the top ← Home leaves the case (%s)' % s)
    tap('.home44-spot [data-a=open]', 'Open this case again')
    s = tap('.tab129 [data-a=cases]', 'bar Cases'); ok(s['view'] == 'cases', 'Cases from the case (%s)' % s)
    s = tap('.tab129 [data-a=data]', 'bar More'); ok(s['view'] == 'data', 'More from Cases (%s)' % s)
    s = tap('.tab129 [data-a=new-case]', 'bar New'); ok(s['view'] == 'home', 'New from More (%s)' % s)
    s = tap('.tab129 [data-a=go-home]', 'bar Home again'); ok(s['view'] == 'home', 'Home from New (%s)' % s)
    # the phone's own Back moves between the places, it doesn't leave Sorted or do nothing (v131)
    tap('.home44-spot [data-a=open]', 'Open this case for Back'); tap('.tab129 [data-a=cases]', 'Cases for Back')
    pg.go_back(); wait(pg, 700); s = state(); print('after Back', s); ok(s['view'] == 'task', 'Back from Cases returns to the case (%s)' % s)
    pg.go_back(); wait(pg, 700); s = state(); print('after Back', s); ok(s['view'] == 'home', 'Back again returns to Home (%s)' % s)
    pg.go_forward(); wait(pg, 700); s = state(); ok(s['view'] == 'task', 'Forward goes to the case again (%s)' % s)
    print('console', logs[-10:])
    ok(not errs, 'no page errors: %s' % errs)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
