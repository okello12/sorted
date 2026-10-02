# v69: company scores. Kept and missed promises go to anonymous company totals (company, outcome, channel; never case text).
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=350): pg.wait_for_timeout(ms)
def tasks(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks.map(y=>y.data)")
def outcomes(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__outcomes')||'[]')")
def start(pg, text):
    pg.goto('https://sorted.test/'); wait(pg, 400)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
    pg.fill('#f-case', text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 450)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 150)
    return sorted(tasks(pg), key=lambda x: x.get('created') or '')[-1]['id']
def due_and_open(pg, cid):
    pg.evaluate("""(id)=>{var db=JSON.parse(localStorage.getItem('__mockdb'));var x=db.tasks.find(y=>y.data.id===id).data;x.promises.forEach(q=>{if(q.status==='open')q.dueAt=new Date(Date.now()-2*864e5).toISOString()});
      localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}""", cid)
    pg.goto('https://sorted.test/'); wait(pg, 400); pg.locator('[data-a=open][data-id="%s"]' % cid).first.click(); wait(pg)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 200); pg.click('[data-a=anon-start]'); wait(pg)
    # 1 a missed promise from a company on the list is recorded, with nothing about the case
    a = start(pg, "Currys promised a refund of £89 by Friday, order 445566")
    due_and_open(pg, a); pg.click('.promise [data-a=missed]'); wait(pg)
    o = outcomes(pg)
    ok(len(o) == 1 and o[0]['p_party'] == 'Currys' and o[0]['p_outcome'] == 'missed', 'a missed Currys promise is added to the totals')
    ok(set(o[0].keys()) == {'p_promise', 'p_party', 'p_outcome', 'p_via'} and '445566' not in json.dumps(o[0]) and 'refund' not in json.dumps(o[0]).lower(), 'only the company, the outcome and the channel go: no reference, no case text')
    # 2 kept
    k = start(pg, "Argos said the replacement will arrive on Friday")
    due_and_open(pg, k); pg.click('.promise [data-a=kept]'); wait(pg)
    ok(outcomes(pg)[-1]['p_party'] == 'Argos' and outcomes(pg)[-1]['p_outcome'] == 'kept', 'a kept promise is added too')
    # 3 not a company on the list: nothing
    n0 = len(outcomes(pg))
    l = start(pg, "My landlord said the plumber will come on Friday")
    due_and_open(pg, l); pg.click('.promise [data-a=kept]'); wait(pg)
    ok(len(outcomes(pg)) == n0, 'a landlord or a person is never added')
    # 4 step records off: nothing
    pg.evaluate("localStorage.setItem('sorted.nosteps','1')")
    m = start(pg, "Amazon said the parcel will arrive on Friday")
    due_and_open(pg, m); pg.click('.promise [data-a=kept]'); wait(pg)
    ok(len(outcomes(pg)) == n0, 'with step records turned off, nothing is added')
    pg.evaluate("localStorage.removeItem('sorted.nosteps')")
    # 5 the totals, once there are enough
    pg.evaluate("""localStorage.setItem('__scores',JSON.stringify([{party:'Currys',kept:7,missed:3,people:4,by_via:{phone:{kept:5,n:6},email:{kept:2,n:4}}}]))""")
    c2 = start(pg, "Currys said the engineer will come on Friday to look at the TV")
    sb = pg.inner_text('.sc-block') if pg.locator('.sc-block').count() else ''
    ok('Across Sorted: Currys' in sb and 'People recorded 10 promises from Currys. 7 were kept (70%).' in sb, 'the totals show on a Currys case')
    ok('Promises made by phone were kept 83% of the time.' in sb and 'by email' not in sb, 'the channel that worked, only with enough of them')
    ok('From 4 people over the last 12 months. It isn’t a review' in sb, 'it says how many people and that it isn’t a review')
    a2 = start(pg, "Argos said the replacement will arrive on Monday")
    ok(pg.locator('.sc-block').count() == 0, 'a company without enough totals shows nothing')
    # 6 the privacy notice
    pg.goto('https://sorted.test/'); wait(pg, 400); pg.click('text=Your data'); wait(pg)
    ok('Company scores. When you record that a company kept or missed a promise' in pg.inner_text('main') and 'Never what your case is about' in pg.inner_text('main'), 'the privacy notice explains company scores')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
