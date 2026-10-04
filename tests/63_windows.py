import re
# v107: uncertain dates stay uncertain. "Sometime next week", "in 2-4 working days", "in the next few days" become a
# window from the first day to the end of the last, shown as "Sometime between X and Y", too early to chase before it
# starts, asked about only after it ends, carried into the shared link; a firm day or a "by" is unchanged; no date at
# all offers a day of your choosing to check back, as your own step, which never counts against them.
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    rd = ctx.new_page(); rd.route(lambda u: u.startswith('https://sorted.test/'), lambda q: q.fulfill(path=HERE + '/tests/out/reader.html', content_type='text/html'))
    rd.goto('https://sorted.test/'); wait(rd, 500)
    W = lambda t, d: rd.evaluate("([s,d])=>{var w=__read.parseWhen(s,new Date(d+'T10:00:00'));return w?{date:w.date,wstart:w.wstart||'',label:w.label}:null}", [t, d])
    for t, d, ws, de in [("sometime next week", '2026-10-04', '2026-10-05', '2026-10-09'), ("sometime next week", '2026-10-07', '2026-10-12', '2026-10-16'), ("next week", '2026-10-05', '2026-10-12', '2026-10-16'),
                         ("within 2-4 working days", '2026-10-03', '2026-10-06', '2026-10-08'), ("in 3 to 5 working days", '2026-10-05', '2026-10-08', '2026-10-12'), ("in the next few days", '2026-10-05', '2026-10-06', '2026-10-08'),
                         ("in a couple of days", '2026-10-05', '2026-10-06', '2026-10-07'), ("early next week", '2026-10-07', '2026-10-12', '2026-10-14'), ("later this week", '2026-10-05', '2026-10-06', '2026-10-09'),
                         ("end of next week", '2026-10-05', '2026-10-14', '2026-10-16'), ("this week", '2026-10-05', '2026-10-05', '2026-10-09')]:
        r = W(t, d) or {}; ok(r.get('wstart') == ws and r.get('date') == de and r.get('label', '').startswith('Sometime between'), '"%s" on %s is a window %s to %s (%s)' % (t, d, ws, de, json.dumps(r)))
    for t, d in [("by Friday", '2026-10-05'), ("Tuesday between 8 and 12", '2026-10-05'), ("within 5 working days", '2026-10-05'), ("end of this week", '2026-10-05'), ("tomorrow", '2026-10-05'), ("on 12 October", '2026-10-05')]:
        r = W(t, d) or {}; ok(r and not r.get('wstart'), '"%s" is a firm day or a deadline, not a window (%s)' % (t, json.dumps(r)))
    S = lambda t: rd.evaluate("(t)=>{var f=__read.caseFacts(t),s=__read.readCase(t,f);return s?{win:!!s.win,by:!!s.by,allDay:!!s.allDay,due:s.dueAt,end:s.dueEnd}:null}", t)
    r = S("Virgin said an engineer would come out sometime next week") or {}
    ok(r.get('win') and r.get('allDay') and not r.get('by') and r.get('end') and r['end'] > r['due'], 'the promise from "sometime next week" is a window (%s)' % json.dumps(r))
    r = S("They said it would arrive within 2-4 working days") or {}; ok(r.get('win') and r.get('end'), '"within 2-4 working days" is a window too')
    r = S("Sky said they would come Tuesday between 8 and 12") or {}; ok(r and not r.get('win'), 'a slot stays a slot')
    rd.close()
    # the interface
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: [x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment']
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    def start(text):
        pg.goto('https://sorted.test/'); wait(pg, 600); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    start('Virgin said an engineer would come out sometime next week')
    m = pg.inner_text('main')
    ok(pg.locator('[data-a=sug-yes]').count() == 1 and 'Sometime between' in m and 'By ' not in m.split('Sometime between')[0][-40:], 'the card shows the window, not a Friday deadline')
    pg.click('[data-a=sug-yes]'); wait(pg, 600)
    c = cases()[0]; cid = c['id']; p = [q for q in c['promises'] if q['status'] == 'open'][0]
    ok(p.get('win') and p['allDay'] and not p.get('by') and p['dueEnd'] > p['dueAt'], 'the saved promise is a window')
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600); m = pg.inner_text('main')
    ok('Sometime between' in m and ('waits until' in m or 'Due by' in m), 'the case says it is a window and when Sorted will ask')
    mq = re.sub(r'Sorted brings it back and asks: “[^”]*”', '', m)  # saying what it will ask later is not asking now
    ok('Did they come?' not in mq and 'Nobody came' not in mq, 'it does not ask whether they came before the window ends')
    pg.goto('https://sorted.test/'); wait(pg, 600)
    ok('Sometime between' in pg.inner_text('main'), 'Home shows the window')
    # past the end of the window, it asks
    pg.evaluate("(id)=>{var d=JSON.parse(localStorage.getItem('__mockdb'));var x=d.tasks.find(y=>y.data.id===id).data;delete x.frNew;x.promises.forEach(q=>{if(q.status==='open'){q.dueAt=new Date(Date.now()-3*864e5).toISOString();q.dueEnd=new Date(Date.now()-864e5).toISOString()}});localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", cid)
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700); m = pg.inner_text('main')
    ok('Did they come?' in m and pg.locator('[data-a=missed]').count() == 1, 'after the window ends it asks "Did they come?"')
    # inside the window: due, with a firm-date route, not a missed visit
    pg.evaluate("(id)=>{var d=JSON.parse(localStorage.getItem('__mockdb'));var x=d.tasks.find(y=>y.data.id===id).data;x.promises.forEach(q=>{if(q.status==='open'){q.dueAt=new Date(Date.now()-864e5).toISOString();q.dueEnd=new Date(Date.now()+2*864e5).toISOString()}});localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", cid)
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700); m = pg.inner_text('main')
    ok('Due by' in m and 'without a firm day' in m and pg.locator('[data-a=rebook]').count() == 1 and pg.locator('[data-a=missed]').count() == 0, 'inside the window: due by its end, a firm-date route, no "Nobody came"')
    pg.evaluate("document.querySelector('details.case56-sharing').open=true"); pg.click('[data-a=share]'); wait(pg, 600)
    tok = [s for s in dbj().get('shares', []) if s['task_id'] == cid][0]['token']
    v = ctx.new_page(); v.goto('https://sorted.test/?share=%s' % tok); wait(v, 700)
    ok('Sometime between' in v.inner_text('main'), 'the shared link shows the window too'); v.close()
    # a correction into a window
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600)
    pg.evaluate("document.querySelector('details.case56-more').open=true"); pg.click('[data-a=panel][data-p=correct]'); wait(pg, 300)
    pg.fill('#f-correct', 'Sorry, I meant in the next few days'); pg.click('form[data-f=correct] button[type=submit]'); wait(pg, 500)
    ok('Sometime between' in pg.inner_text('main') and pg.locator('[data-a=corr-yes]').count() == 1, 'a correction to a window reads as a window')
    pg.click('[data-a=corr-yes]'); wait(pg, 500); p = [q for q in cases()[0]['promises'] if q['status'] == 'open'][0]
    ok(p.get('win') and p['dueEnd'] > p['dueAt'], 'and keeps it one')
    # no date: a day of your choosing, as your own step
    start('Aviva said they would call me back about my claim')
    m = pg.inner_text('main')
    ok(pg.locator('[data-a=sug-yes]').count() == 0 and 'haven’t given you a date' in m and pg.locator('[data-a=fr-check]').count() == 3 and 'not their promise' in m, 'no date: no promise card; offers 3 days, a week, 2 weeks as your own reminder')
    pg.locator('[data-a=fr-check][data-d="7"]').click(); wait(pg, 600)
    c2 = [x for x in cases() if 'Aviva' in (x.get('said') or '')][0]; mv = [x for x in c2.get('moves', []) if x['status'] == 'open'][0]
    wk = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()
    ok(mv['what'].startswith('Check back with Aviva') and mv.get('chosen') and pg.evaluate("iso=>{var d=new Date(iso);return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')}", mv['dueAt']) == wk and not c2['promises'], 'it is your own step a week out, not a promise')
    ok(any('The day was your choice' in (e.get('label') or '') for e in c2['events']), 'the history says the day was your choice')
    ok(not any(e['name'] == 'promise_created' and e['case_id'] == c2['id'] for e in dbj().get('pilot_events', [])), 'and no promise is recorded against Aviva')
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
