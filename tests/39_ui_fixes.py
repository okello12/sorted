# v78: a refund due today isn't treated as a visit, the reference shows once, Home rows line up, step 2 shows the name and Ref.
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
def poke(pg, js):
    pg.goto('https://sorted.test/'); wait(pg, 700)
    pg.evaluate("(js)=>{var db=JSON.parse(localStorage.getItem('__mockdb'));(new Function('db',js))(db);localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", js)
def start(pg, text, shot=None):
    pg.goto('https://sorted.test/'); wait(pg)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
    pg.fill('#f-case', text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if shot: shot(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 150)
    return sorted([x['data'] for x in db(pg)['tasks']], key=lambda x: x.get('created') or '')[-1]['id']
def due_today(pg, cid):
    poke(pg, "var x=db.tasks.find(y=>y.data.id==='%s').data;x.promises.forEach(q=>{if(q.status==='open'){var d=new Date();d.setHours(0,0,0,0);q.dueAt=d.toISOString();q.allDay=true;q.by=true;q.dueEnd=null}})" % cid)
    pg.goto('https://sorted.test/'); wait(pg, 500); pg.locator('[data-a=open][data-id="%s"]' % cid).first.click(); wait(pg, 600)
step2 = {}
def grab(pg): step2['h3'] = pg.inner_text('form[data-f=baseline] .h3'); step2['ref'] = pg.inner_text('form[data-f=baseline] .case75-title-ref') if pg.locator('form[data-f=baseline] .case75-title-ref').count() else ''
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 200); pg.click('[data-a=anon-start]'); wait(pg)
    # 1 step 2 shows the name and the reference on its own line
    r = start(pg, "Currys promised a refund of £89 by Friday, order 445566", grab)
    ok(step2['h3'] == 'Currys refund' and step2['ref'] == 'Ref 445566', 'step 2: name and Ref on separate lines (%s / %s)' % (step2['h3'], step2['ref']))
    # 2 a refund due today: "Due today", no "Show this", no "It didn't" yet, the reference once
    due_today(pg, r)
    c = pg.inner_text('.promise')
    ok('Due today' in c and 'Happening now' not in c, 'a refund due today says "Due today"')
    ok(pg.locator('.promise [data-p=hold]').count() == 0 and pg.locator('.promise [data-a=missed]').count() == 0, 'no "Show this", and no "It didn’t" before the day is out')
    ok('Due by the end of today. If it hasn’t happened by then, Sorted will ask you.' in c and pg.locator('.promise [data-a=kept]').inner_text() == 'It arrived', 'it says when Sorted will ask, and offers "It arrived"')
    ok(pg.locator('.promise .ref').count() == 0 and pg.inner_text('.case75-title-ref').strip() == 'Ref 445566', 'the reference shows once, under the title')
    pg.click('.promise [data-a=kept]'); wait(pg)
    ok(next(x['data'] for x in db(pg)['tasks'] if x['data']['id'] == r)['promises'][-1]['status'] == 'kept', '"It arrived" still records it')
    # 3 a visit due today keeps "Show this"
    v = start(pg, "British Gas said the engineer will come tomorrow between 8 and 12 to fix the boiler")
    poke(pg, "var x=db.tasks.find(y=>y.data.id==='%s').data;x.promises.forEach(q=>{if(q.status==='open'){q.dueAt=new Date(Date.now()-3600e3).toISOString();q.dueEnd=new Date(Date.now()+3600e3).toISOString();q.allDay=false;q.by=false}})" % v)
    pg.goto('https://sorted.test/'); wait(pg, 500); pg.locator('[data-a=open][data-id="%s"]' % v).first.click(); wait(pg, 600)
    ok('Happening now' in pg.inner_text('.promise') and pg.locator('.promise [data-p=hold]').count() == 1, 'an engineer visit happening now keeps "Show this"')
    # 4 Home: the spotlight shows the reference once, rows line up
    s2 = start(pg, "Argos promised a refund of £40 by Friday, order 778899")
    poke(pg, "var x=db.tasks.find(y=>y.data.id==='%s').data;x.promises.forEach(q=>{if(q.status==='open')q.dueAt=new Date(Date.now()-2*864e5).toISOString()})" % s2)
    start(pg, "London Borough of Southwark PENALTY CHARGE NOTICE PCN Number: SK12345678 The penalty charge is £130.")
    pg.goto('https://sorted.test/'); wait(pg, 700)
    ok(pg.inner_text('.home44-spot').count('778899') == 1, 'the spotlight shows the reference once')
    rows = pg.locator('.home44-row')
    good = True
    for i in range(rows.count()):
        rb = rows.nth(i).bounding_box(); cb = rows.nth(i).locator('.home44-row-copy').bounding_box(); ch = rows.nth(i).locator('.home44-chevron').bounding_box()
        if not (cb['x'] - rb['x'] < 50 and ch['x'] > cb['x'] + cb['width'] - 2 and ch['x'] > rb['x'] + rb['width'] - 40): good = False
    ok(rows.count() >= 2 and good, 'every Home row: words start at the left, the arrow sits at the right')
    ok(all(rows.nth(i).inner_text().count('Ref ') <= 1 for i in range(rows.count())), 'no row repeats the reference')
    pg.screenshot(path='tests/out/39_home.png', full_page=True)
    b.close()
print('ERRORS', errs); print('FAILS', fails)
