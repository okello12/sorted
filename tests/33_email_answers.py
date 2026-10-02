# v71: answer from the reminder email. "Yes" or "No" opens the case and records it, after a fresh load, with Undo.
import os, sys, json
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
def outcomes(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__outcomes')||'[]')")
def poke(pg, js):
    pg.evaluate("(js)=>{var db=JSON.parse(localStorage.getItem('__mockdb'));(new Function('db',js))(db);localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", js)
def start(pg, text):
    pg.goto('https://sorted.test/'); wait(pg, 400)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
    pg.fill('#f-case', text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 450)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 150)
    return sorted([x['data'] for x in db(pg)['tasks']], key=lambda x: x.get('created') or '')[-1]['id']
def overdue(pg, cid):
    poke(pg, "var x=db.tasks.find(y=>y.data.id==='%s').data;x.promises.forEach(q=>{if(q.status==='open')q.dueAt=new Date(Date.now()-2*864e5).toISOString()})" % cid)
def link(cid, ans, pid): return 'https://sorted.test/?task=%s&src=email&ans=%s&p=%s' % (cid, ans, pid)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 200); pg.click('[data-a=anon-start]'); wait(pg)
    cid = start(pg, "Currys promised a refund of £89 by Friday, order 445566")
    overdue(pg, cid)
    t0 = task(pg, cid); pid = next(q['id'] for q in t0['promises'] if q['status'] == 'open'); n0 = len(t0['events'])
    # 1 "No" from the email: recorded as missed, the chase is ready, the case says what was recorded
    pg.goto(link(cid, 'no', pid)); wait(pg, 700)
    t = task(pg, cid); q = next(x for x in t['promises'] if x['id'] == pid)
    ok(q['status'] == 'missed' and t['board'] == 'yours', '"No" in the email records that it didn’t happen')
    ok(pg.locator('form[data-f=call]').count() == 1, 'and opens the chase, ready to send')
    note = pg.inner_text('.ans-note') if pg.locator('.ans-note').count() else ''
    ok('Recorded from your email: it didn’t happen.' in note and 'Not this case? Undo' in note, 'the case says what the email recorded, with Undo')
    ok(any(o['p_promise'] == pid and o['p_outcome'] == 'missed' for o in outcomes(pg)), 'the company totals get it, like any answer')
    ok(any(e.get('kind') == 'return' and e.get('src') == 'email' for e in t['events']), 'the return from the email is counted')
    # 2 Undo puts the case back exactly
    pg.click('[data-a=ans-undo]'); wait(pg, 500)
    t = task(pg, cid); q = next(x for x in t['promises'] if x['id'] == pid)
    ok(q['status'] == 'open' and len(t['events']) == n0 + 1 and t['events'][-1]['label'].startswith('Opened from the email link') and not any(o['p_promise'] == pid for o in outcomes(pg)), 'Undo puts the case back and takes it out of the totals')
    ok('Undone. Nothing was recorded.' in pg.inner_text('#toast') and pg.locator('.ans-note').count() == 0, 'and says so')
    # 3 "Yes": kept
    pg.goto(link(cid, 'yes', pid)); wait(pg, 700)
    t = task(pg, cid); q = next(x for x in t['promises'] if x['id'] == pid)
    ok(q['status'] == 'kept' and 'Recorded from your email: they kept it.' in pg.inner_text('main'), '"Yes" records that they kept it')
    pg.click('[data-a=panel][data-p=""] >> nth=-1') if pg.locator('[data-a=panel][data-p=""]').count() else None; wait(pg)
    ok(pg.locator('.ans-note').count() == 0, 'the note goes once you do something else')
    # 4 the same link again changes nothing
    n1 = len(task(pg, cid)['events'])
    pg.goto(link(cid, 'no', pid)); wait(pg, 700)
    ok(task(pg, cid)['promises'][-1]['status'] == 'kept' and len(task(pg, cid)['events']) == n1 + 1 and 'already answered' in pg.inner_text('#toast'), 'an old link changes nothing and says it was already answered')
    # 5 your own move: "Yes" marks it done, "Not yet" only opens the new-date form
    m = start(pg, "I need to ring the council about the bin collection")
    poke(pg, "var x=db.tasks.find(y=>y.data.id==='%s').data;x.moves=x.moves||[];x.moves.push({id:'mv1',what:'Ring the council',dueAt:new Date(Date.now()-3600e3).toISOString(),allDay:false,by:false,status:'open',at:new Date().toISOString()})" % m)
    pg.goto(link(m, 'no', 'mv1')); wait(pg, 700)
    ok(task(pg, m)['moves'][-1]['status'] == 'open' and pg.locator('#moveform').count() == 1 and pg.locator('.ans-note').count() == 0, '"Not yet" on your own step opens the new-date form and records nothing')
    pg.goto(link(m, 'yes', 'mv1')); wait(pg, 700)
    ok(task(pg, m)['moves'][-1]['status'] == 'done' and 'Recorded from your email: you did it.' in pg.inner_text('main'), '"Yes" marks your step done')
    # 6 signed out: it says what will happen, and keeps the answer through sign-in
    c2 = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    c2.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    c2.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html'))
    p2 = c2.new_page(); p2.on('pageerror', lambda e: errs.append(str(e)))
    p2.goto(link(cid, 'no', pid)); wait(p2, 500)
    ok('Sign in and Sorted will record your answer' in p2.inner_text('main'), 'signed out, it says it will record the answer after sign-in')
    p2.fill('#f-email', 'me@example.com'); p2.click('form[data-f=signin] button[type=submit]'); wait(p2, 400)
    redir = p2.evaluate("(window.__otp||[]).slice(-1).map(o=>(o.options&&o.options.emailRedirectTo)||'')[0]||''")
    ok(('&ans=no&p=' + pid) in redir, 'the sign-in link carries the answer: %s' % redir[-60:])
    c2.close()
    b.close()
print('ERRORS', errs); print('FAILS', fails)
