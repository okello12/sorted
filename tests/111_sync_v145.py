# v145 (audit pass 3, reviewer B): saving and reading. Two devices (two browser contexts whose "server" is copied between
# them) and two tabs (one context). The mock is served with a write counter and four switches added here: a lapsed
# session (row level security hides every row, as it does for a request without this person's session), a re-delete that
# fails, and the old reminder constraint still in place beside the new key.
#  1. A lapsed session reads no rows: nothing is removed from the screen or the copy on this phone, an edit made then is
#     kept and sent once the session is back, and an answer is applied once, with one score after the save.
#  2. Delete then Undo: the other tab and the other device show the case again, keep it in their copy and see later
#     edits; the revision keeps counting up.
#  3. A case deleted while its first save was on the way, whose late save landed and whose re-delete failed, stays hidden
#     and is deleted again on the next load.
#  4. Company totals and step records waiting for a save survive closing the page, and two tabs send them once.
#  5. A refresh on a case or a move that isn't in the copy on this phone opens it.
#  6. Reminder rows are written while the old (task_id, kind, send_at) constraint is still there.
#  7. A case too big to save isn't sent again and again until it changes.
#  8. A guest's kept document on its way to the email account is never shown as "None yet".
#  9. No write when nothing changed; one write for a lost answer and a reload; the sign-in line names the notification.
import os, sys, json, datetime
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m, flush=True)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
today = datetime.date.today()
def nextwd(n):
    d = (n - today.weekday()) % 7 or 7
    return today + datetime.timedelta(days=d)
FRI = nextwd(4).strftime('%A')
YEST = (today - datetime.timedelta(days=1)).isoformat() + 'T08:00:00'

MOCK = open(HERE + '/tests/mock.js').read()
def rep(s, a, b):
    assert s.count(a) == 1, a[:60]
    return s.replace(a, b)
# every case write that reaches the server: [id, rev, op]
MOCK = rep(MOCK, 'self.then=function(a,b){', 'self.then=function(a,b){if(table==="tasks"&&(op==="update"||op==="upsert")&&payload&&!Array.isArray(payload)){var _p=payload.data||{};self._w=[_p.id||"",_p.rev||0,op]}var _rr=run;run=function(){var x=_rr();if(self._w&&x&&!x.error&&(op==="upsert"||(x.data&&x.data.length))){var W=JSON.parse(localStorage.getItem("__W")||"[]");W.push(self._w);localStorage.setItem("__W",JSON.stringify(W))}return x};')
# __rls: a lapsed session; __failDel: case deletes fail; __oldKeyToo: the old reminder constraint is still there
MOCK = rep(MOCK, 'if(op==="select"){var fr', 'if(table==="tasks"&&localStorage.getItem("__rls")==="1"){if(op==="select")return {data:[],error:null};if(op==="update")return {data:[],error:null}}if(op==="delete"&&table==="tasks"&&localStorage.getItem("__failDel")==="1")return {data:null,error:{message:"Failed to fetch"}};if(op==="select"){var fr')
MOCK = rep(MOCK, 'getSession:function(){return Promise.resolve({data:{session:session}})}', 'getSession:function(){return Promise.resolve({data:{session:localStorage.getItem("__rls")==="1"?null:session}})}')
MOCK = rep(MOCK, 'if(op==="upsert"&&Array.isArray(payload)){payload.forEach(', 'if(op==="upsert"&&Array.isArray(payload)&&table==="reminders"&&localStorage.getItem("__oldKeyToo")==="1"&&/promise_id/.test(self._oc||"")){var all=rows.concat(payload);for(var i=0;i<all.length;i++)for(var j=i+1;j<all.length;j++){var a1=all[i],b1=all[j];if(a1.task_id===b1.task_id&&a1.kind===b1.kind&&a1.send_at===b1.send_at&&(a1.promise_id||null)!==(b1.promise_id||null))return {data:null,error:{message:"duplicate key value violates unique constraint",code:"23505"}}}}if(op==="upsert"&&Array.isArray(payload)){payload.forEach(')

with sync_playwright() as p:
    br = p.chromium.launch()
    def ctx(w=390, h=844):
        c = br.new_context(timezone_id='Europe/London', viewport={'width': w, 'height': h})
        c.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(body=MOCK, content_type='application/javascript'))
        c.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
        return c
    def page(c):
        x = c.new_page(); x.on('pageerror', lambda e: errs.append(str(e))); x.goto('https://sorted.test/'); return x
    db = lambda q: q.evaluate("JSON.parse(localStorage.getItem('__mockdb')||'{}')") or {}
    setdb = lambda q, d: q.evaluate("d=>localStorage.setItem('__mockdb',JSON.stringify(d))", d)
    def sync(src, dst): setdb(dst, db(src))
    def srv(q, cid):
        r = [x['data'] for x in db(q).get('tasks', []) if x['id'] == cid]; return r[0] if r else None
    W = lambda q, cid=None: [w for w in q.evaluate("JSON.parse(localStorage.getItem('__W')||'[]')") if cid is None or w[0] == cid]
    Wclear = lambda q: q.evaluate("localStorage.removeItem('__W')")
    labels = lambda c: [e['label'] for e in (c or {}).get('events', [])]
    opens = lambda c: [x for x in (c or {}).get('promises', []) if x['status'] == 'open']
    toast = lambda q: q.inner_text('#toast') if q.locator('#toast:not([hidden])').count() else ''
    outcomes = lambda q: q.evaluate("JSON.parse(localStorage.getItem('__outcomes')||'[]')")
    steps = lambda q, cid, n: [e for e in (db(q).get('pilot_events') or []) if e.get('case_id') == cid and e['name'] == n]
    has = lambda q, i: q.locator('[data-id="%s"]' % i).count() > 0
    cache = lambda q, uid='u-me': json.loads(q.evaluate("u=>localStorage.getItem('sorted.cache.'+u)", uid) or '[]')
    def local(q, cid): return ([x for x in cache(q) if x['id'] == cid] or [None])[0]
    def sync_line(q): return q.locator('[data-sync]').first.inner_text() if q.locator('[data-sync]').count() else ''
    def sign_in(q, uid='u-me', email='me@example.com'):
        q.goto('https://sorted.test/'); q.evaluate("([u,e])=>{localStorage.setItem('__mocksession',JSON.stringify({user:{id:u,email:e}}));localStorage.setItem('__emailReady','1')}", [uid, email]); q.goto('https://sorted.test/'); wait(q, 800)
    def fresh(q):
        q.goto('https://sorted.test/'); q.evaluate("localStorage.clear();sessionStorage.clear()"); sign_in(q)
    def nav(q, url):   # a real load, never a hash change inside the page
        q.goto('about:blank'); q.goto(url)
    def click(q, sel, ms=600):
        q.locator(sel).first.evaluate('e=>e.click()'); wait(q, ms)
    def press(q, a, p=None, ms=600):   # a button the page would show under "Manage this case"
        q.evaluate("([a,p])=>{var b=document.createElement('button');b.setAttribute('data-a',a);if(p)b.setAttribute('data-p',p);document.querySelector('main').appendChild(b);b.click()}", [a, p]); wait(q, ms)
    def make_case(q, text):
        q.goto('https://sorted.test/'); wait(q, 500)
        if not q.locator('[data-cap82=other]').count() and q.locator('[data-a=new-case]').count(): click(q, '[data-a=new-case]', 300)
        click(q, '[data-cap82=other]', 300)
        q.fill('#f-case', text); q.locator('form[data-f=case] button[type=submit]').last.click(); wait(q, 700)
        if q.locator('[data-a=match-new]').count(): click(q, '[data-a=match-new]')
        if q.locator('form[data-f=baseline]').count(): q.click('form[data-f=baseline] .chip >> nth=0'); q.click('form[data-f=baseline] button[type=submit]'); wait(q, 500)
        if q.locator('[data-a=plan-skip]').count(): click(q, '[data-a=plan-skip]', 500)
        if q.locator('[data-a=sug-yes]').count(): click(q, '[data-a=sug-yes]', 700)
        if q.locator('text=Not now').count(): q.locator('text=Not now').first.click(); wait(q, 300)
        if q.locator('[data-a=fr-ok]').count(): click(q, '[data-a=fr-ok]', 300)
        ts = sorted([x['data'] for x in db(q).get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
        return ts[-1]['id']
    def open_case(q, cid):
        q.goto('https://sorted.test/?task=%s' % cid); wait(q, 800); q.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
    def server_edit(q, cid, js):
        q.evaluate("""([id,f])=>{var d=JSON.parse(localStorage.getItem('__mockdb'));var r=d.tasks.find(x=>x.id===id);(new Function('c',f))(r.data);r.data.rev=(r.data.rev||0)+1;localStorage.setItem('__mockdb',JSON.stringify(d))}""", [cid, js])
    def past(q, cid):
        server_edit(q, cid, "var p=c.promises.find(q=>q.status==='open');p.dueAt='%s';p.allDay=true;p.by=true;p.dueEnd=null;p.prec='day'" % YEST)
    def rename(q, name, ms=700):
        q.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
        click(q, '[data-a=panel][data-p=rename]', 250); q.fill('#f-rename', name); q.click('form[data-f=rename] button[type=submit]'); wait(q, ms)
    def answer(q, v):
        sel = '[data-a=q-kept]' if v == 'kept' and q.locator('[data-a=q-kept]').count() else '[data-a=home-ans][data-v=%s]' % v
        click(q, sel, 1200)

    cL = ctx(1280, 900); cP = ctx()
    L = page(cL); P = page(cP)

    # ---- 1. a lapsed session reads no rows ----
    fresh(P)
    a = make_case(P, 'Currys said they would refund £89 by %s, order 445566' % FRI)
    b = make_case(P, 'Evri said they would deliver my parcel by %s' % FRI)
    P.goto('https://sorted.test/'); wait(P, 800)
    ok(has(P, a) and has(P, b), '1: both cases on Home')
    P.evaluate("localStorage.setItem('__rls','1')")
    P.evaluate("window.dispatchEvent(new Event('focus'))"); wait(P, 1200)
    ok(has(P, a) and has(P, b), '1: a refetch that reads no rows without this person’s session removes nothing from the screen')
    ok(not P.evaluate("localStorage.getItem('sorted.gone.u-me')") and {a, b} <= {x['id'] for x in cache(P)}, '1: and nothing from the copy on this phone')
    P.evaluate("localStorage.removeItem('__rls')"); open_case(P, a); P.evaluate("localStorage.setItem('__rls','1')")
    rename(P, 'Kettle refund', 1500)
    ok('deleted on another device' not in toast(P) and 'Kettle refund' in P.inner_text('main'), '1: an edit made then is not called “deleted on another device” (%r)' % toast(P))
    ok((local(P, a) or {}).get('title') == 'Kettle refund' and (local(P, a) or {}).get('_dirty'), '1: the edit stays on this phone, unsent')
    ok(sync_line(P).startswith('Saved on this phone, not yet sent'), '1: and the case says so (%r)' % sync_line(P))
    Wclear(P); P.evaluate("localStorage.removeItem('__rls')"); P.evaluate("window.dispatchEvent(new Event('online'))"); wait(P, 1500)
    c = srv(P, a)
    ok(c['title'] == 'Kettle refund' and len(W(P, a)) == 1 and not [l for l in labels(c) if l.startswith('Merged')], '1: once the session is back it is sent once, with no merge (%s)' % W(P, a))
    ok(sum(1 for l in labels(c) if l.startswith('Renamed')) == 1, '1: one history line for the rename')
    # an answer tapped while the session has lapsed: applied once here, one score once it is saved
    past(P, b); P.goto('https://sorted.test/'); wait(P, 800)
    P.evaluate("localStorage.setItem('__rls','1')"); answer(P, 'kept')
    ok(not outcomes(P) and 'deleted' not in toast(P), '1: no score while it can’t be saved, and nothing called deleted')
    P.evaluate("localStorage.removeItem('__rls')"); P.evaluate("window.dispatchEvent(new Event('online'))"); wait(P, 1800)
    c = srv(P, b)
    ok(c['promises'][-1]['status'] == 'kept' and sum(l.startswith('They kept it') for l in labels(c)) == 1, '1: the answer is saved once (%s)' % [l for l in labels(c) if 'kept' in l])
    ok([o['p_outcome'] for o in outcomes(P)] == ['kept'], '1: one score, after the save (%s)' % outcomes(P))
    wait(P, 600); ok(len(steps(P, b, 'outcome_kept')) == 1, '1: one step record')

    # ---- 2. delete then Undo: other tabs and devices ----
    T1 = page(cL); T2 = page(cL)
    fresh(T1)
    X = make_case(T1, 'Argos said they would refund £30 by %s, order 778899' % FRI)
    open_case(T1, X); rename(T1, 'Argos one'); rename(T1, 'Argos two'); rv = srv(T1, X)['rev']
    sync(T1, P); sign_in(P); open_case(P, X)                 # another device holding the case
    T2.goto('https://sorted.test/'); wait(T2, 900)
    ok(has(T2, X), '2: tab 2 shows the case')
    open_case(T1, X); press(T1, 'panel', 'delcase', 300); click(T1, '[data-a=case-del]', 900)
    wait(T2, 900); ok(not has(T2, X), '2: tab 2 drops it once it is deleted')
    click(T1, '[data-a=del-undo]', 1000)
    c = srv(T1, X)
    ok(c and c['rev'] > rv and c.get('revived') and sum(1 for l in labels(c) if l.startswith('Put back after being deleted')) == 1, '2: Undo puts it back with the revision counting on (%s -> %s) and one history line' % (rv, c and c['rev']))
    wait(T2, 600); T2.evaluate("window.dispatchEvent(new Event('focus'))"); wait(T2, 1200)
    ok(has(T2, X), '2: tab 2 shows it again')
    ok(not json.loads(T1.evaluate("localStorage.getItem('sorted.gone.u-me')") or '{}').get(X), '2: no tombstone is left for it on this phone')
    open_case(T1, X); rename(T1, 'After undo', 900)
    ok(X in [x['id'] for x in cache(T1)], '2: the copy on this phone keeps it')
    off = cL.new_page(); off.on('pageerror', lambda e: errs.append(str(e)))
    off.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(body=MOCK.replace('if(op==="select"){var fr', 'if(op==="select"&&table==="tasks")return {data:null,error:{message:"Failed to fetch"}};if(op==="select"){var fr'), content_type='application/javascript'))
    off.goto('https://sorted.test/'); wait(off, 1000)
    ok(has(off, X), '2: an offline start shows the case put back')
    off.close()
    sync(T1, P); P.evaluate("window.dispatchEvent(new Event('focus'))"); wait(P, 1200)
    ok('After undo' in P.inner_text('main'), '2: the other device shows the edit made after the Undo')
    Wclear(P); wait(P, 800); ok(not W(P), '2: and writes nothing back (%s)' % W(P))
    T1.close(); T2.close()

    # ---- 3. a late save after the delete, and a failed re-delete ----
    fresh(P)
    make_case(P, 'Evri said they would deliver my parcel by %s' % FRI)
    P.evaluate("localStorage.setItem('__slowWrites','5000')")
    P.goto('https://sorted.test/'); wait(P, 500)
    click(P, '[data-a=new-case]', 300); click(P, '[data-cap82=other]', 300)
    P.fill('#f-case', 'Boots said they would refund £12 by %s, order 99001' % FRI); P.locator('form[data-f=case] button[type=submit]').last.click(); wait(P, 300)
    if P.locator('[data-a=match-new]').count(): click(P, '[data-a=match-new]', 200)
    if P.locator('form[data-f=baseline]').count(): P.click('form[data-f=baseline] .chip >> nth=0'); P.click('form[data-f=baseline] button[type=submit]'); wait(P, 200)
    nid = P.evaluate("(location.hash.match(/case-(\\w+)/)||[])[1]||''")
    if P.locator('[data-a=sug-yes]').count(): click(P, '[data-a=sug-yes]', 200)
    press(P, 'panel', 'delcase', 100); click(P, '[data-a=case-del]', 100)
    P.evaluate("localStorage.setItem('__failDel','1')"); wait(P, 9000)
    ok(nid and srv(P, nid) is not None, '3: the late save landed after the delete and the re-delete failed (the set-up)')
    ok(nid in json.loads(P.evaluate("localStorage.getItem('sorted.redel.u-me')") or '{}'), '3: this phone remembers to delete it again (an id only)')
    P.evaluate("localStorage.removeItem('__failDel');localStorage.removeItem('__slowWrites')")
    P.goto('https://sorted.test/'); wait(P, 1500)
    ok(not has(P, nid) and nid not in [x['id'] for x in cache(P)], '3: it doesn’t come back on the next load')
    ok(srv(P, nid) is None and not json.loads(P.evaluate("localStorage.getItem('sorted.redel.u-me')") or '{}'), '3: it is deleted again and the note is cleared')

    # ---- 4. totals and step records waiting for a save survive closing the page ----
    fresh(P)
    cid = cid4 = make_case(P, 'Boots said they would refund £12 by %s, order 99001' % FRI)
    past(P, cid); P.goto('https://sorted.test/'); wait(P, 800)
    P.evaluate("localStorage.setItem('__failWrites','1')"); answer(P, 'missed')
    ok(not outcomes(P) and not steps(P, cid, 'outcome_missed'), '4: nothing is sent while the miss is unsaved')
    P.goto('https://sorted.test/'); wait(P, 300)
    q = json.loads(P.evaluate("localStorage.getItem('sorted.oq145.u-me')") or '{}')
    ok(q and cid in q.get('o', {}) and all(set(x) <= {'pid', 'o', 'at'} for x in q['o'][cid]), '4: closing the page keeps the waiting score on this phone, ids and codes only (%s)' % q.get('o'))
    ok(all(set(x['x']) <= {'promise_id', 'src', 'after_due', 'partly'} for x in sum(q.get('t', {}).values(), [])), '4: and the waiting step records carry no words')
    P.evaluate("localStorage.removeItem('__failWrites')"); P.goto('https://sorted.test/'); wait(P, 2000)
    ok(srv(P, cid)['promises'][-1]['status'] == 'missed' and [o['p_outcome'] for o in outcomes(P)] == ['missed'], '4: reopened, the miss is saved and one score sent (%s)' % outcomes(P))
    wait(P, 600)
    ok(len(steps(P, cid, 'outcome_missed')) == 1 and len(steps(P, cid, 'promise_due_return')) == 1, '4: one step record of the miss, and the return is counted')
    ok(not P.evaluate("localStorage.getItem('sorted.oq145.u-me')"), '4: nothing is left waiting')
    # two tabs: the tab that answered is hidden, another is shown; the score goes once
    T1 = page(cL); T2 = page(cL)
    fresh(T1)
    cid = make_case(T1, 'Argos said they would refund £30 by %s, order 778899' % FRI)
    past(T1, cid); T1.goto('https://sorted.test/'); wait(T1, 800); T2.goto('https://sorted.test/'); wait(T2, 800)
    T1.evaluate("localStorage.setItem('__failWrites','1')"); answer(T1, 'kept')
    T1.evaluate("window.dispatchEvent(new Event('pagehide'))"); wait(T1, 200)
    T2.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); wait(T2, 1200)
    T1.evaluate("localStorage.removeItem('__failWrites')"); T1.evaluate("window.dispatchEvent(new Event('online'))"); wait(T1, 1500)
    T2.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); wait(T2, 1200)
    ok(srv(T1, cid)['promises'][-1]['status'] == 'kept' and [o['p_outcome'] for o in outcomes(T1)] == ['kept'], '4: two tabs send one score (%s)' % outcomes(T1))
    wait(T1, 600); ok(len(steps(T1, cid, 'outcome_kept')) == 1, '4: and one step record')
    T1.close(); T2.close()

    # ---- 5. a refresh on a case or a move with no copy on this phone ----
    P.goto('https://sorted.test/'); wait(P, 400)
    now = P.evaluate("new Date().toISOString()")
    P.evaluate("([id,now])=>{var d=JSON.parse(localStorage.getItem('__mockdb'));d.tasks.push({id:id,data:{id:id,kind:'moment',type:'moving',title:'Moving home',date:'2026-12-04',ans:{tenure:'rent',nation:'en'},items:{},rev:1,created:now},updated_at:now});localStorage.setItem('__mockdb',JSON.stringify(d))}", ['mv145xx', now])
    P.evaluate("Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))")
    nav(P, 'https://sorted.test/#case-%s' % cid4); wait(P, 1400)
    ok(P.url.endswith('#case-%s' % cid4) and 'Boots' in P.inner_text('main') and 'isn’t in Sorted any more' not in toast(P), '5: a refresh on a case this phone had no copy of opens the case (%s)' % P.url)
    P.evaluate("Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))")
    nav(P, 'https://sorted.test/#move-mv145xx'); wait(P, 1400)
    ok(P.url.endswith('#move-mv145xx') and 'Moving home' in P.inner_text('main'), '5: and a move too (%s)' % P.url)
    nav(P, 'https://sorted.test/#case-nothere145'); wait(P, 1400)
    ok('isn’t in Sorted any more' in toast(P) and not P.url.endswith('#case-nothere145'), '5: a case that isn’t there still says so (%r)' % toast(P))

    # ---- 6. reminder rows while the old constraint is still there ----
    fresh(P); P.evaluate("localStorage.setItem('__oldKeyToo','1')")
    cid = make_case(P, 'Currys said they would refund £89 by %s, order 445566' % FRI)
    server_edit(P, cid, "var o=c.promises.find(q=>q.status==='open');c.promises.push(Object.assign({},o,{id:'pp145b',party:'Argos',said:'refund £20',loggedAt:new Date().toISOString()}));c.emailRemind=true")
    P.evaluate("Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k));var d=JSON.parse(localStorage.getItem('__mockdb'));d.reminders=[];localStorage.setItem('__mockdb',JSON.stringify(d))")
    open_case(P, cid); rename(P, 'Two refunds', 1200)
    rows = [r for r in db(P).get('reminders', []) if r['task_id'] == cid]
    rerr = [e for e in P.evaluate("JSON.parse(localStorage.getItem('__errs')||'[]')") if e.get('p_source') == 'reminder']
    ok(len(rows) >= 2 and not rerr, '6: two promises due the same minute still get reminder rows (%d rows, %s)' % (len(rows), rerr))
    P.evaluate("localStorage.removeItem('__oldKeyToo')")

    # ---- 7. a case too big to save isn't sent again and again ----
    fresh(P)
    cid = make_case(P, 'Argos said they would refund £30 by %s, order 778899' % FRI)
    P.evaluate("([id,n])=>{var k='sorted.cache.u-me',a=JSON.parse(localStorage.getItem(k));var t=a.find(x=>x.id===id);t.events.push({at:new Date().toISOString(),label:'Added a message: “'+'x'.repeat(n)+'”'});t._dirty=true;t.updatedAt=new Date().toISOString();localStorage.setItem(k,JSON.stringify(a))}", [cid, 120000])
    P.evaluate("localStorage.removeItem('__errs')"); open_case(P, cid); wait(P, 600)
    for i in range(4):
        P.evaluate("document.dispatchEvent(new Event('visibilitychange'));window.dispatchEvent(new Event('online'))"); wait(P, 400)
    n = P.evaluate("JSON.parse(localStorage.getItem('__errs')||'[]').filter(e=>e.p_source==='save').length")
    ok(n == 1 and sync_line(P).startswith('Too big to save'), '7: refused once, not sent again unchanged (%d tries), and it says so' % n)
    click(P, '[data-a=ev-del]', 1000)
    ok('xxxxxxxxxx' not in json.dumps(srv(P, cid)) and sync_line(P).startswith('Saved to your account'), '7: removing the long message lets it save (%r)' % sync_line(P))

    # ---- 8. a guest's kept document on its way to the email account ----
    G = page(cP)
    G.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); nav(G, 'https://sorted.test/#start'); wait(G, 400); G.click('[data-a=anon-start]'); wait(G, 800)
    guid = G.evaluate("JSON.parse(localStorage.getItem('__mocksession')).user.id")
    gc = make_case(G, 'Lambeth council sent a parking fine, I need to challenge it')
    open_case(G, gc)
    pdf = HERE + '/tests/out/notice145.pdf'
    open(pdf, 'wb').write(b'%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n')
    G.set_input_files('input[data-keepdoc="%s"]' % gc, pdf); wait(G, 1200)
    ok(G.locator('.docs135 [data-a=doc-view]').count() == 1, '8: the guest kept a document')
    press(G, 'claim-signin', None, 900)
    sign_in(G, 'u-mail', 'mail@example.com'); wait(G, 1000)
    c = srv(G, gc)
    ok(c and c.get('docNames') and json.loads(G.evaluate("localStorage.getItem('__claimed')") or '{}').get('p_pairs') == [], '8: claimed, the case keeps its id and its document names')
    open_case(G, gc); wait(G, 600)
    m = G.inner_text('main')
    ok('1 document kept with this case isn’t showing yet' in m and 'being moved to your account' in m and 'None yet' not in m, '8: until it arrives the case says it is on its way, never “None yet”')
    # the server moves the file to the email account's folder
    G.evaluate("([g,u])=>{var a=JSON.parse(localStorage.getItem('__storage')||'[]');a.forEach(x=>{if(x.name.indexOf(g+'/')===0)x.name=u+x.name.slice(g.length)});localStorage.setItem('__storage',JSON.stringify(a))}", [guid, 'u-mail'])
    click(G, '[data-a=docs-recheck145]', 900)
    m = G.inner_text('main')
    ok(G.locator('.docs135 [data-a=doc-view]').count() == 1 and 'isn’t showing yet' not in m, '8: once moved, “Check again” shows it')
    G.close()

    # ---- 9. writes: none when nothing changed, one for a lost answer and a reload; the sign-in line ----
    fresh(L)
    cid = make_case(L, 'BT said the engineer would come on %s, ref BT445566' % FRI)
    wait(L, 800); r0 = srv(L, cid)['rev']; Wclear(L)
    for i in range(3):
        open_case(L, cid); L.goto('https://sorted.test/'); wait(L, 400)
        L.evaluate("window.dispatchEvent(new Event('focus'));document.dispatchEvent(new Event('visibilitychange'));window.dispatchEvent(new Event('online'))"); wait(L, 500)
        L.goto('https://sorted.test/#cases'); wait(L, 400)
    ok(srv(L, cid)['rev'] == r0 and not W(L), '9: opening, refreshing and coming back write nothing (%s)' % W(L))
    open_case(L, cid); r0 = srv(L, cid)['rev']; Wclear(L)
    L.evaluate("localStorage.setItem('__dropAck','1')"); rename(L, 'BT visit', 300)
    L.goto('https://sorted.test/?task=%s' % cid); wait(L, 2500)
    c = srv(L, cid)
    ok(c['title'] == 'BT visit' and c['rev'] == r0 + 1 and len(W(L, cid)) == 1 and not [l for l in labels(c) if l.startswith('Merged')], '9: a lost answer then a reload: one write, no merge (%s)' % W(L, cid))
    L.evaluate("localStorage.removeItem('__mocksession');Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))")
    nav(L, 'https://sorted.test/?task=%s&src=push' % cid); wait(L, 900)
    ok('Sign in to open the case from the notification.' in L.inner_text('main'), '9: signed out, a notification link says “from the notification”')
    nav(L, 'https://sorted.test/?task=%s&src=email' % cid); wait(L, 900)
    ok('Sign in to open the case from your email.' in L.inner_text('main'), '9: an email link still says “from your email”')
    # sign-out leaves no note of what to delete again or what waits to be sent
    sign_in(L); L.evaluate("localStorage.setItem('sorted.redel.u-me','{\"x\":1}');localStorage.setItem('sorted.oq145.u-me','{\"o\":{}}')")
    nav(L, 'https://sorted.test/#more'); wait(L, 900); click(L, '[data-a=signout]', 1200)
    ok(not L.evaluate("localStorage.getItem('sorted.redel.u-me')") and not L.evaluate("localStorage.getItem('sorted.oq145.u-me')"), '9: sign-out clears both notes')

    print('ERRORS', errs)
    print('FAILS', fails)
    br.close()
