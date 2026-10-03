# v96: discovery fitted to what you just did, a search for examples, a health line on the case, one-tap endings.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
def db(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {'tasks': []}
def newest(pg): return sorted([x['data'] for x in db(pg)['tasks']], key=lambda x: x.get('created') or '')[-1]
def poke(pg, js):
    pg.evaluate("(js)=>{var db=JSON.parse(localStorage.getItem('__mockdb'));(new Function('db',js))(db);localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", js)
def home(pg):
    pg.goto('https://sorted.test/'); wait(pg, 600)
    if pg.locator('[data-a=gi-back]').count(): pg.click('[data-a=gi-back]'); wait(pg)
def typed(pg, text):
    home(pg)
    if pg.locator('[data-cap82=other]').first.is_visible(): pg.locator('[data-cap82=other]').first.click(); wait(pg)
    elif pg.locator('[data-a=compose]').count(): pg.locator('[data-a=compose]').first.click(); wait(pg)
    pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg)
    if pg.locator('.ps-short').count(): pg.locator('.ps-short button[type=submit]').click(); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count():
        pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 550)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    # 1 discovery fits what you just did
    typed(pg, 'Got a letter from HMRC saying my tax code is wrong')
    home(pg)
    a = pg.inner_text('.cap95-also') if pg.locator('.cap95-also').count() else ''
    ok('council letters, fines, forms and deadlines' in a and pg.locator('.cap95-also .cap95-chip').count() == 3 and 'HMRC letter' not in a, 'after an HMRC case: council letters, fines and forms, with 3 examples, not HMRC again')
    pg.locator('.cap95-also [data-cap95=parking]').click(); wait(pg, 600)
    ok(pg.locator('.pk-short').count() == 1, 'and an example opens its flow')
    pg.evaluate("localStorage.removeItem('__mockdb')"); pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    typed(pg, 'Currys said my refund of £89 would arrive within 5 working days')
    home(pg)
    ok('complaints, subscriptions and missing deliveries' in pg.inner_text('.cap95-also'), 'after a refund: complaints, subscriptions and deliveries')
    # 2 search
    pg.click('details.cap95-explore summary'); wait(pg, 200)
    for q, k in [('DVLA', 'passport'), ('my landlord', 'landlord'), ('Amazon refund', 'refund'), ('parcel', 'delivery'), ('school application', 'application')]:
        pg.fill('#ex-search', q); wait(pg, 150)
        ok(pg.locator('#ex-found [data-cap95=%s]' % k).count() == 1, 'search "%s" finds %s' % (q, k))
    pg.fill('#ex-search', 'my neighbour’s tree'); wait(pg, 150)
    ok(pg.locator('#ex-found [data-a=ex-own]').count() == 1, 'nothing matching: "Tell Sorted what happened"')
    pg.click('#ex-found [data-a=ex-own]'); wait(pg, 500)
    ok(pg.input_value('#f-case') == 'my neighbour’s tree', 'and the box starts with what you typed')
    home(pg); pg.click('details.cap95-explore summary'); wait(pg, 200); pg.fill('#ex-search', 'DVLA'); wait(pg, 150)
    pg.locator('#ex-found [data-cap95=passport]').click(); wait(pg, 600)
    ok(pg.locator('input[name=gi-item][value=Passport]').is_checked(), 'a search result opens its flow')
    # 3 health line on an older case
    cid = newest(pg)['id']
    poke(pg, "var x=db.tasks.find(y=>y.data.id==='%s').data;x.created=new Date(Date.now()-11*864e5).toISOString();delete x.frNew;x.sugDone=true;x.promises=[{id:'p1',said:'Refund',party:'Currys',dueAt:new Date(Date.now()-2*864e5).toISOString(),status:'missed',closedAt:new Date().toISOString()}];x.facts=x.facts||{};delete x.facts.ref" % cid)
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700)
    hl = pg.inner_text('.case96-health') if pg.locator('.case96-health').count() else ''
    ok('They missed the date they gave you.' in hl and ('Open for 11 days' in hl or 'No reference saved yet' in hl), 'an older case says what matters: %s' % hl)
    poke(pg, "var x=db.tasks.find(y=>y.data.id==='%s').data;x.promises=[{id:'p2',said:'Refund',party:'Currys',dueAt:new Date(Date.now()+5*864e5).toISOString(),status:'open'}]" % cid)
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700)
    hl = pg.inner_text('.case96-health') if pg.locator('.case96-health').count() else ''
    ok('You’ve been waiting 11 days.' in hl, 'waiting: how long: %s' % hl)
    # 4 one-tap endings
    pg.locator('[data-a=panel][data-p=done]').first.evaluate('e=>e.click()'); wait(pg)
    ok(pg.locator('[data-a=done-kind]').count() == 4, 'How did it end: four one-tap answers')
    pg.locator('[data-a=done-kind][data-v=Refunded]').click(); wait(pg, 150)
    ok(pg.input_value('#f-outcome') == 'Refunded.', 'tapping one fills the answer')
    pg.fill('#f-outcome', pg.input_value('#f-outcome') + ' Took 3 weeks.'); pg.locator('[data-a=done-kind][data-v=Cancelled]').click(); wait(pg, 150)
    ok(pg.input_value('#f-outcome') == 'Cancelled. Took 3 weeks.', 'changing it keeps your own words')
    pg.click('form[data-f=done] button[type=submit]'); wait(pg, 500)
    ok(newest(pg)['board'] == 'done' and 'Cancelled.' in (newest(pg).get('outcome') or ''), 'and the case is done with that ending')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'nothing scrolls sideways')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
