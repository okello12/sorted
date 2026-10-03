# v74: playbooks in one format. Repairs: after a visit Sorted asks if it's fixed, counts visits and no-shows,
# points to the right rights or route, and only finishes when you say so. Other cases are unchanged.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=350): pg.wait_for_timeout(ms)
def db(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))")
def task(pg, cid): return next(x['data'] for x in db(pg)['tasks'] if x['data']['id'] == cid)
def poke(pg, js):
    pg.goto('https://sorted.test/'); wait(pg, 700)  # let the last page finish saving, so the mock store isn't overwritten
    pg.evaluate("(js)=>{var db=JSON.parse(localStorage.getItem('__mockdb'));(new Function('db',js))(db);localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", js)
def start(pg, text):
    pg.goto('https://sorted.test/'); wait(pg, 400)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
    pg.fill('#f-case', text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 450)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 150)
    return sorted([x['data'] for x in db(pg)['tasks']], key=lambda x: x.get('created') or '')[-1]['id']
def overdue_open(pg, cid):
    poke(pg, "var x=db.tasks.find(y=>y.data.id==='%s').data;x.promises.forEach(q=>{if(q.status==='open')q.dueAt=new Date(Date.now()-2*864e5).toISOString()})" % cid)
    pg.goto('https://sorted.test/'); wait(pg, 500); pg.locator('[data-a=open][data-id="%s"]' % cid).first.click(); wait(pg, 600)
def add_visit(pg, cid, said):
    poke(pg, "var x=db.tasks.find(y=>y.data.id==='%s').data;x.promises.push({id:'v'+Date.now(),said:'%s',party:'British Gas',dueAt:new Date(Date.now()-2*864e5).toISOString(),allDay:true,status:'open',loggedAt:new Date().toISOString()})" % (cid, said))
    pg.goto('https://sorted.test/'); wait(pg, 500); pg.locator('[data-a=open][data-id="%s"]' % cid).first.click(); wait(pg, 600)
def card(pg): return pg.inner_text('.pb-card') if pg.locator('.pb-card').count() else ''
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 200); pg.click('[data-a=anon-start]'); wait(pg)
    # 1 a visit happens: Sorted asks if it's fixed, rather than closing
    g = start(pg, "British Gas said the engineer will come on Friday to fix the boiler")
    overdue_open(pg, g); pg.click('.promise [data-a=kept]'); wait(pg)
    c = card(pg)
    ok('REPAIR: AFTER THE VISIT' in c.upper() and 'Did the visit fix it?' in c, 'after the visit, Sorted asks if it’s fixed')
    ok(pg.locator('form[data-f=done]').count() == 0 and task(pg, g)['board'] != 'done', 'it doesn’t close the case on its own')
    ok(task(pg, g)['pb']['visits'] == 1 and task(pg, g)['pb']['stage'] == 'check', 'visit 1 is counted')
    # 2 not fixed
    pg.click('[data-a=pb-go][data-v=notfixed]'); wait(pg)
    c = card(pg)
    ok('Still not fixed after one visit' in c and 'They’ve promised another visit' in c and 'Remind me to chase them' in c, 'not fixed: the next steps')
    ok(any(e['label'] == 'Still not fixed after one visit.' for e in task(pg, g)['events']), 'and it goes in the history')
    # 3 the next visit is missed, then one is kept and still not fixed
    add_visit(pg, g, 'The engineer will come back on Monday')
    pg.click('.promise [data-a=missed]'); wait(pg)
    ok(task(pg, g)['pb']['noShows'] == 1 and pg.locator('form[data-f=call]').count() == 1, 'a missed visit is counted and the chase is ready')
    add_visit(pg, g, 'The engineer will come on Wednesday with the part')
    pg.click('.promise [data-a=kept]'); wait(pg)
    ok('That was visit 2.' in card(pg), 'the second visit says so')
    pg.click('[data-a=pb-go][data-v=notfixed]'); wait(pg)
    c = card(pg)
    ok('Still not fixed after 2 visits' in c and 'They also missed one appointment.' in c and 'formal route' in c, 'after 2 visits: the count, the no-show and the formal route')
    ok(pg.locator('.xr-fold').count() == 1, 'and “If they still don’t sort it” shows')
    # 4 fixed: the outcome is proposed, the person finishes it
    pg.click('[data-a=pb-go][data-v=fixed]'); wait(pg)
    ok(pg.input_value('#f-outcome') == 'Fixed after 2 visits.', 'fixed: the outcome is written for you to check')
    ok(task(pg, g)['board'] != 'done', 'but nothing closes until you tap')
    pg.click('form[data-f=done] button[type=submit]'); wait(pg)
    ok(task(pg, g)['board'] == 'done' and task(pg, g)['outcome'] == 'Fixed after 2 visits.', 'tapping finishes it')
    # 5 a repair on something bought: the rights after a failed repair
    s = start(pg, "Currys said the engineer will come on Monday to repair the TV")
    overdue_open(pg, s); pg.click('.promise [data-a=kept]'); wait(pg); pg.click('[data-a=pb-go][data-v=notfixed]'); wait(pg)
    c = card(pg)
    ok('ask the seller for a refund instead' in c and pg.locator('.pb-card a[href*="citizensadvice.org.uk"]').count() == 1, 'something bought: the refund right, with Citizens Advice')
    # 6 not a repair: unchanged
    r = start(pg, "Currys promised a refund of £89 by Friday, order 445566")
    overdue_open(pg, r); pg.click('.promise [data-a=kept]'); wait(pg)
    ok('Has all of it arrived?' in (card(pg) if pg.locator('.pb-card').count() else '') and pg.locator('form[data-f=done]').count() == 0, 'a refund kept follows the refund playbook (v98): has all of it arrived?')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
