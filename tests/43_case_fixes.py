# v83: your own step on the Home spotlight (and GOV.UK on an existing renewal step), a reference must have a digit,
# and complaints are named after the company. Renewals typed in stay on the general path.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
def db(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))")
def tasks(pg): return [x['data'] for x in (db(pg) or {'tasks':[]})['tasks']]
def newest(pg): return sorted(tasks(pg), key=lambda x: x.get('created') or '')[-1]
def type_case(pg, text):
    pg.goto('https://sorted.test/'); wait(pg)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
    pg.fill('#f-case', text); pg.click('form[data-f=case] button[type=submit]'); wait(pg, 500)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 200); pg.click('[data-a=anon-start]'); wait(pg, 600)
    # 3 a renewal typed in stays on the general path (renewals and to-dos are out of the pilot's scope)
    type_case(pg, "My driving licence expires on 24 November")
    ok(pg.locator('#moveform').count() == 0 and pg.locator('form[data-f=baseline]').count() == 1, 'a renewal typed in is not turned into a to-do')
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    # 4 your own step on the Home spotlight: the step and its date, with a button that ticks it off
    pg.goto('https://sorted.test/'); wait(pg, 700)
    pg.evaluate("()=>{var d=JSON.parse(localStorage.getItem('__mockdb'));d.tasks.forEach(y=>{var x=y.data;x.mode='do';x.title='Renew my driving licence';x.moves=[{id:'m1',what:'Renew my driving licence before it runs out',act:'renew',dueAt:new Date(Date.now()+864e5).toISOString(),allDay:true,by:true,status:'open',loggedAt:new Date().toISOString()}]});localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}")
    pg.goto('https://sorted.test/'); wait(pg, 700)
    sp = pg.inner_text('.home44-spot')
    ok('Renew my driving licence before it runs out' in sp and sp.count('Your move') == 0 and 'Due tomorrow' in sp, 'the spotlight shows the step and "Due tomorrow", not "Your move" twice')
    pg.screenshot(path='tests/out/43_spot.png', full_page=True)
    pg.locator('.home44-spot [data-a=open]').click(); wait(pg, 500)
    ok(pg.locator('.note a[href="https://www.gov.uk/renew-driving-licence"]').count() == 1, 'an existing renewal step points to the official GOV.UK page')
    pg.goto('https://sorted.test/'); wait(pg, 600)
    pg.click('.home44-spot [data-a=home-move]'); wait(pg, 500)
    ok(newest(pg)['moves'][-1]['status'] == 'done', 'the spotlight button marks the step done')
    # 6 references need a digit; complaints are named after the company
    type_case(pg, "Landlord still hasn't fixed the heating")
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    ok(pg.locator('.case75-title-ref').count() == 0 and 'landlord' in pg.inner_text('h1').lower(), '"landlord" is part of the name, never a "Ref"')
    type_case(pg, "I complained to Thames Water two weeks ago and they haven't replied")
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    ok(newest(pg)['title'] == 'Thames Water complaint', 'a long complaint is named "Thames Water complaint"')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'nothing scrolls sideways')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
