# v143: two devices and two tabs (audit pass 2: PASS2-003, 004, 019, 031). A laptop and a phone share one account (two
# browser contexts whose "server" is copied between them, so each can be stale); two tabs share one browser. Every
# ordering in Reviewer 7's race table: a stale phone answering "Nobody came", "They came", a new date or "Not yet" after the
# laptop moved the date or answered from the email, and a correction prepared before the move. Each is refused with the
# out-of-date banner and records nothing: one open promise per organisation, no score, no step record, nothing in the
# history that contradicts the record. Then: a save whose answer was lost (no merge line, the second edit wins), nested
# answers merged key by key with the conflict named, a redraw when the case changes elsewhere (panel closed, no page
# error from a stale repair panel), sign-out counting another tab's unsent edit, a deleted case never written back by a
# stale tab, a switched-off helper link never copied, outcomes sent only once the save is confirmed, and a case too big
# to save saying so.
import os, sys, json, datetime
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
def ld(iso):  # the London day of a stored time
    return datetime.datetime.fromisoformat(iso.replace('Z', '+00:00')).astimezone(ZoneInfo('Europe/London')).date().isoformat() if 'T' in iso else iso[:10]
today = datetime.date.today()
def nextwd(n):
    d = (n - today.weekday()) % 7 or 7
    return today + datetime.timedelta(days=d)
YEST = (today - datetime.timedelta(days=1)).isoformat() + 'T08:00:00'
THU = nextwd(3)
MOVE = 'BT text: your engineer appointment has been moved to %s %d %s.' % (THU.strftime('%A'), THU.day, THU.strftime('%B'))

with sync_playwright() as p:
    br = p.chromium.launch()
    def ctx(w=390, h=844):
        c = br.new_context(timezone_id='Europe/London', viewport={'width': w, 'height': h}, accept_downloads=True)
        c.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
        c.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
        return c
    def page(c):
        x = c.new_page(); x.on('pageerror', lambda e: errs.append(str(e))); return x
    db = lambda q: q.evaluate("JSON.parse(localStorage.getItem('__mockdb')||'{}')") or {}
    setdb = lambda q, d: q.evaluate("d=>localStorage.setItem('__mockdb',JSON.stringify(d))", d)
    def sync(src, dst): setdb(dst, db(src))   # the one "server", copied to the other device
    def srv(q, cid):
        r = [x['data'] for x in db(q).get('tasks', []) if x['id'] == cid]; return r[0] if r else None
    outcomes = lambda q: q.evaluate("JSON.parse(localStorage.getItem('__outcomes')||'[]')")
    events = lambda q, cid: [e for e in (db(q).get('pilot_events') or []) if e.get('case_id') == cid]
    labels = lambda c: [e['label'] for e in (c or {}).get('events', [])]
    opens = lambda c: [x for x in (c or {}).get('promises', []) if x['status'] == 'open']
    toast = lambda q: q.inner_text('#toast') if q.locator('#toast:not([hidden])').count() else ''
    def sign_in(q):
        q.goto('https://sorted.test/'); q.evaluate("localStorage.setItem('__mocksession',JSON.stringify({user:{id:'u-me',email:'me@example.com'}}));localStorage.setItem('__emailReady','1')"); q.goto('https://sorted.test/'); wait(q, 800)
    def fresh(q):
        q.goto('https://sorted.test/'); q.evaluate("localStorage.clear();sessionStorage.clear()"); sign_in(q)
    def click(q, sel, ms=600):
        q.locator(sel).first.evaluate('e=>e.click()'); wait(q, ms)
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
    def paste(q, text):
        click(q, '[data-a=panel][data-p=paste]', 300); q.fill('#f-paste', text); q.click('form[data-f=paste] button[type=submit]'); wait(q, 900)
    def move_on_laptop(L, cid):
        open_case(L, cid); paste(L, MOVE)
        if L.locator('[data-a=corr-moved]').count(): click(L, '[data-a=corr-moved]', 900)
        elif L.locator('[data-a=sug-yes]').count(): click(L, '[data-a=sug-yes]', 900)
    def honest(c, what):
        # one open promise per organisation; no answer in the history that contradicts the record without a line saying so
        by = {}
        for x in opens(c): by.setdefault((x.get('party') or '').lower(), []).append(x)
        ok(all(len(v) == 1 for v in by.values()), '%s: at most one open promise per organisation (%s)' % (what, [(x['status'], ld(x['dueAt'])) for x in c['promises']]))
        ls = labels(c); bad = []
        for x in c['promises']:
            s = x.get('said') or ''
            k1 = ('They kept it: %s.' % s) in ls; k2 = any(l.startswith('It didn’t happen: %s (' % s) for l in ls)
            if x['status'] == 'kept' and (x.get('late') or x.get('missedAt')): continue
            if ((k1 and x['status'] != 'kept') or (k2 and x['status'] != 'missed')) and not any(l.startswith('Two devices answered') for l in ls): bad.append(s)
        ok(not bad, '%s: the history doesn’t contradict the record (%s)' % (what, bad))
        if c.get('board') == 'done': ok(not opens(c) and not [m for m in c.get('moves', []) if m['status'] == 'open'], '%s: a finished case has nothing open' % what)

    cL = ctx(1280, 900); cP = ctx()
    L = page(cL); P = page(cP)

    # ---- 1. the race table: the laptop moves BT's visit; the phone, never reloaded, answers the old one ----
    for mode in ('missed', 'kept', 'newdate'):
        fresh(L); P.goto('https://sorted.test/'); P.evaluate("localStorage.clear()");
        cid = make_case(L, 'BT said the engineer would come on %s, ref BT445566' % nextwd(4).strftime('%A'))
        past(L, cid); sync(L, P); sign_in(P); wait(P, 400)
        ok(P.locator('[data-a=home-ans][data-v=missed]').count() > 0 or P.locator('[data-a=q-kept]').count() > 0, '%s: the phone’s Home asks about the old date' % mode)
        move_on_laptop(L, cid); sync(L, P)
        thu = opens(srv(L, cid)); ok(len(thu) == 1 and ld(thu[0]['dueAt']) == THU.isoformat(), '%s: the laptop moved it to %s' % (mode, THU))
        if mode == 'missed': click(P, '[data-a=home-ans][data-v=missed]', 1200)
        elif mode == 'kept': click(P, '[data-a=q-kept]' if P.locator('[data-a=q-kept]').count() else '[data-a=home-ans][data-v=kept]', 1200)
        else:
            click(P, '[data-a=q-date]', 400); P.fill('form[data-f=qdate] input[type=date]', nextwd(0).isoformat())
            P.locator('form[data-f=qdate] button[type=submit]').click(); wait(P, 1200)
        c = srv(P, cid); m = P.inner_text('main')
        ok(len(opens(c)) == 1 and ld(opens(c)[0]['dueAt']) == THU.isoformat() and c.get('board') != 'yours', '%s: refused, BT’s date is still %s and the case still waits (%s)' % (mode, THU, [(x['status'], ld(x['dueAt'])) for x in c['promises']]))
        ok('This screen was out of date' in m and 'the date changed' in m, '%s: the phone says what happened since (%r)' % (mode, m[:200]))
        ok('Nothing was recorded' in toast(P) or 'Nothing was recorded' in m, '%s: and that nothing was recorded' % mode)
        ok(not outcomes(P) and not outcomes(L), '%s: no company score from either device' % mode)
        ok(not [e for e in events(P, cid) if e['name'] in ('outcome_missed', 'outcome_kept')], '%s: no step record of an outcome' % mode)
        ok(not any(l.startswith('It didn’t happen') or l.startswith('They kept it') for l in labels(c)), '%s: no answer in the history' % mode)
        honest(c, mode)

    # ---- 1d. the laptop answers Yes from the email; then the stale phone taps "Not yet" ----
    fresh(L); P.goto('https://sorted.test/'); P.evaluate("localStorage.clear()")
    cid = make_case(L, 'Currys said they would refund £89 by %s, order 445566' % nextwd(4).strftime('%A'))
    past(L, cid); sync(L, P); sign_in(P)
    pid = opens(srv(L, cid))[0]['id']
    L.goto('https://sorted.test/?task=%s&src=email&ans=yes&p=%s' % (cid, pid)); wait(L, 1500)
    ok(srv(L, cid)['promises'][-1]['status'] == 'kept' and [o['p_outcome'] for o in outcomes(L)] == ['kept'], 'the email answer records kept, and one kept score once it is saved')
    sync(L, P)
    click(P, '[data-a=home-ans][data-v=missed]', 1200)
    c = srv(P, cid)
    ok(c['promises'][-1]['status'] == 'kept' and c.get('board') != 'yours' and not outcomes(P), 'the stale “Not yet” is refused: still kept, no second score (%s)' % c.get('board'))
    ok('you recorded that' in P.inner_text('main') and 'This screen was out of date' in P.inner_text('main'), 'the phone shows where the case is now')
    honest(c, 'email then stale Not yet')

    # ---- 1e. a correction prepared on the phone before the laptop moved the date ----
    fresh(L); P.goto('https://sorted.test/'); P.evaluate("localStorage.clear()")
    mon = nextwd(0)
    cid = make_case(L, 'BT said the engineer would come on %s %d %s, ref BT445566' % (mon.strftime('%A'), mon.day, mon.strftime('%B')))
    sync(L, P); sign_in(P); open_case(P, cid)
    paste(P, 'Sorry, I meant %s' % nextwd(4).strftime('%A'))
    ok(P.locator('[data-a=corr-yes]').count() > 0, 'the phone proposes the correction')
    pcp = srv(P, cid).get('corrP') or {}
    ok(pcp.get('pid') == opens(srv(P, cid))[0]['id'], 'the proposal is bound to the promise it is about')
    sync(P, L); move_on_laptop(L, cid); sync(L, P)
    click(P, '[data-a=corr-yes]', 1200)
    c = srv(P, cid)
    ok(len(opens(c)) == 1 and ld(opens(c)[0]['dueAt']) == THU.isoformat(), 'the old correction is not applied to the laptop’s new promise (%s)' % [(x['status'], ld(x['dueAt'])) for x in c['promises']])
    ok(not c.get('corrP') and ('changed since' in toast(P) or 'already answered elsewhere' in toast(P) or 'This screen was out of date' in P.inner_text('main')), 'it is refused with a word and the proposal goes (%r, %s)' % (toast(P), c.get('corrP')))
    honest(c, 'stale correction')

    # ---- 1e2. the same, bound check by itself: the laptop replaced the promise, the phone's correction and its pasted new date are refused ----
    REPL = "var o=c.promises.find(q=>q.status==='open');o.status='replaced';o.closedAt=new Date().toISOString();c.promises.push(Object.assign({},o,{id:'lap143'+Math.random().toString(16).slice(2,6),status:'open',dueAt:'%sT00:00:00',loggedAt:new Date().toISOString(),said:'come on Thursday'}));delete o.onFinish;c.events.push({at:new Date().toISOString(),label:'They changed the date. It was Monday.'})" % THU.isoformat()
    for kind, text, btn in (('correction', 'Sorry, I meant %s' % nextwd(4).strftime('%A'), 'corr-yes'), ('new date', 'BT: your appointment is now on %s %d %s.' % (nextwd(4).strftime('%A'), nextwd(4).day, nextwd(4).strftime('%B')), 'sug-yes')):
        fresh(L); P.goto('https://sorted.test/'); P.evaluate("localStorage.clear()")
        cid = make_case(L, 'BT said the engineer would come on %s %d %s, ref BT445566' % (mon.strftime('%A'), mon.day, mon.strftime('%B')))
        sync(L, P); sign_in(P); open_case(P, cid); paste(P, text)
        if not P.locator('[data-a=%s]' % btn).count() and btn == 'sug-yes' and P.locator('[data-a=corr-moved]').count(): btn = 'corr-moved'
        ok(P.locator('[data-a=%s]' % btn).count() > 0, '%s: the phone proposes it (%s)' % (kind, btn))
        sync(P, L); server_edit(L, cid, REPL); sync(L, P)
        click(P, '[data-a=%s]' % btn, 1200)
        c = srv(P, cid)
        ok(len(opens(c)) == 1 and ld(opens(c)[0]['dueAt']) == THU.isoformat() and opens(c)[0]['id'].startswith('lap143'), '%s: the laptop’s promise is untouched (%s)' % (kind, [(x['status'], ld(x['dueAt'])) for x in c['promises']]))
        ok('changed since' in toast(P) and 'This screen was out of date' in P.inner_text('main'), '%s: refused with a word (%r)' % (kind, toast(P)))
        ok(not c.get('corrP') and (not c.get('sugP') or c.get('sugDone')), '%s: the stale proposal goes' % kind)
        honest(c, 'stale ' + kind)

    # ---- 1f. a stale screen that is still right goes through, once, after reading the server ----
    fresh(L); P.goto('https://sorted.test/'); P.evaluate("localStorage.clear()")
    cid = make_case(L, 'Argos said they would refund £30 by %s, order 778899' % nextwd(4).strftime('%A'))
    past(L, cid); sync(L, P); sign_in(P)
    server_edit(L, cid, "c.events.push({at:new Date().toISOString(),label:'Laptop note.'})"); sync(L, P)
    P.evaluate("()=>{var b=document.querySelector('[data-a=q-kept]')||document.querySelector('[data-a=home-ans][data-v=kept]');b.click();b.click()}"); wait(P, 1200)
    c = srv(P, cid)
    ok(c['promises'][-1]['status'] == 'kept' and 'Laptop note.' in labels(c) and sum(l.startswith('They kept it') for l in labels(c)) == 1, 'an answer that still fits is applied once on top of the laptop’s change')
    ok([o['p_outcome'] for o in outcomes(P)] == ['kept'] and not [l for l in labels(c) if l.startswith('Merged')], 'one score, sent after the save, and no merge was needed')

    # ---- 2. outcomes wait for the save that carries them ----
    fresh(P)
    cid = make_case(P, 'Boots said they would refund £12 by %s, order 99001' % nextwd(4).strftime('%A'))
    past(P, cid); P.goto('https://sorted.test/'); wait(P, 700)
    P.evaluate("localStorage.setItem('__failWrites','1')"); click(P, '[data-a=home-ans][data-v=missed]', 1000)
    ok(not outcomes(P) and not [e for e in events(P, cid) if e['name'] == 'outcome_missed'], 'a miss whose save failed sends no score and no step record yet')
    P.evaluate("localStorage.removeItem('__failWrites')"); P.evaluate("window.dispatchEvent(new Event('online'))"); wait(P, 1500)
    ok([o['p_outcome'] for o in outcomes(P)] == ['missed'] and srv(P, cid)['promises'][-1]['status'] == 'missed', 'once the save is confirmed, the score matches the saved status')
    wait(P, 600); ok(len([e for e in events(P, cid) if e['name'] == 'outcome_missed']) == 1, 'and the step record goes once')

    # ---- 3. a save whose answer was lost (PASS2-004) ----
    cid = make_case(P, 'Currys said they would refund £89 by %s, order 445566' % nextwd(4).strftime('%A'))
    open_case(P, cid)
    P.evaluate("localStorage.setItem('__dropAck','1')")
    click(P, '[data-a=panel][data-p=rename]', 250); P.fill('#f-rename', 'Kettle refund'); P.click('form[data-f=rename] button[type=submit]'); wait(P, 700)
    ok(srv(P, cid)['title'] == 'Kettle refund', 'the first rename reached the server though its answer was lost')
    P.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
    click(P, '[data-a=panel][data-p=rename]', 250); P.fill('#f-rename', 'Kettle refund from Currys'); P.click('form[data-f=rename] button[type=submit]'); wait(P, 1500)
    c = srv(P, cid)
    ok(c['title'] == 'Kettle refund from Currys' and not [l for l in labels(c) if l.startswith('Merged')], 'the second rename wins and there is no merge line (%r)' % c['title'])
    ok('Kettle refund from Currys' in P.inner_text('main'), 'the screen shows the second title')
    wait(P, 5500); c = srv(P, cid)
    ok(c['title'] == 'Kettle refund from Currys' and not [l for l in labels(c) if l.startswith('Merged')], 'and the retry changes nothing')
    # the same with the last edit: the lost answer is found, nothing is merged or sent twice
    rv = c['rev']; P.evaluate("localStorage.setItem('__dropAck','1')")
    click(P, '[data-a=panel][data-p=rename]', 250); P.fill('#f-rename', 'Kettle refund 3'); P.click('form[data-f=rename] button[type=submit]'); wait(P, 6500)
    c = srv(P, cid)
    ok(c['title'] == 'Kettle refund 3' and c['rev'] == rv + 1 and not [l for l in labels(c) if l.startswith('Merged')], 'a lost answer for the last edit is recognised as this phone’s own (rev %s→%s)' % (rv, c['rev']))
    ok('Saved to your account' in P.inner_text('main'), 'and the case says it is saved')

    # ---- 4. nested answers merge key by key; a real conflict is named (PASS2-019) ----
    fresh(L); P.goto('https://sorted.test/'); P.evaluate("localStorage.clear()")
    now = L.evaluate("new Date().toISOString()")
    rep = {'id': 'rep143xx', 'title': 'Landlord: washing machine', 'mode': 'fix', 'board': 'yours', 'created': now, 'updatedAt': now, 'rev': 3,
           'said': 'My washing machine will not drain', 'facts': {'party': 'Landlord'},
           'fix': {'step': 'checks', 'item': 'Washing machine', 'fault': 'drain', 'checks': {}, 'party': 'Landlord'},
           'promises': [], 'refs': [], 'moves': [], 'events': [{'at': now, 'label': 'Started.'}]}
    def poke(q, r):
        q.evaluate("r=>{var d=JSON.parse(localStorage.getItem('__mockdb')||'null')||{tasks:[],shares:[],reminders:[],helpers:[],inbound_items:[]};d.tasks=d.tasks.filter(x=>x.id!==r.id);d.tasks.push({id:r.id,user_id:'u-me',data:r,updated_at:new Date().toISOString()});localStorage.setItem('__mockdb',JSON.stringify(d))}", r)
    poke(L, rep); sync(L, P); sign_in(P); open_case(L, 'rep143xx'); open_case(P, 'rep143xx')
    ch = L.evaluate("[...document.querySelectorAll('[data-a=check]')].map(e=>[e.getAttribute('data-k'),e.getAttribute('data-v')])")
    ks = []
    for k, v in ch:
        if k not in [x[0] for x in ks]: ks.append((k, v))
    ok(len(ks) >= 2, 'the repair asks at least two checks (%s)' % ks)
    k1, k2 = ks[0], ks[1]
    alt1 = [v for k, v in ch if k == k1[0] and v != k1[1]]
    P.evaluate("localStorage.setItem('__failWrites','1')")
    click(P, '[data-a=check][data-k="%s"][data-v="%s"]' % k2, 600)                 # phone answers check 2, not sent
    if alt1: click(P, '[data-a=check][data-k="%s"][data-v="%s"]' % (k1[0], alt1[0]), 600)   # and a different answer to check 1
    click(L, '[data-a=check][data-k="%s"][data-v="%s"]' % k1, 800)                 # laptop answers check 1
    sync(L, P); P.evaluate("localStorage.removeItem('__failWrites')"); P.evaluate("window.dispatchEvent(new Event('online'))"); wait(P, 1500)
    c = srv(P, 'rep143xx'); cks = (c.get('fix') or {}).get('checks') or {}
    ok(cks.get(k2[0]) == k2[1] and cks.get(k1[0]) == k1[1], 'both devices’ repair answers are kept, the laptop’s where both answered (%s)' % cks)
    ml = [l for l in labels(c) if l.startswith('Merged')]
    ok(ml and (not alt1 or 'repair answer' in ml[-1]), 'the merge line names the conflict (%s)' % ml)
    pressed = P.evaluate("[...document.querySelectorAll('[data-a=check][aria-pressed=true]')].map(e=>e.getAttribute('data-k')+'='+e.getAttribute('data-v'))")
    ok('%s=%s' % k2 in pressed and '%s=%s' % k1 in pressed, 'the phone is redrawn with both answers (%s)' % pressed)

    # ---- 5. a stale repair panel after the kind changed elsewhere: no page error, nothing recorded ----
    poke(L, rep); sync(L, P); open_case(L, 'rep143xx'); open_case(P, 'rep143xx')
    click(L, '[data-a=panel][data-p=kind]', 300); click(L, '[data-k=kind][data-v=call]', 200); L.click('form[data-f=kind] button[type=submit]'); wait(L, 800)
    ok(srv(L, 'rep143xx')['mode'] == 'call', 'the laptop made it a call')
    sync(L, P); n0 = len(errs)
    click(P, '[data-a=check][data-k="%s"][data-v="%s"]' % k1, 900)
    if P.locator('[data-a=checks-done]').count(): click(P, '[data-a=checks-done]', 900)
    c = srv(P, 'rep143xx')
    ok(len(errs) == n0, 'no page error from the stale repair panel (%s)' % errs[n0:])
    ok(c['mode'] == 'call' and not ((c.get('fix') or {}).get('checks') or {}), 'nothing was recorded into the old repair (%s)' % c.get('fix'))
    ok(not P.locator('[data-a=check]').count(), 'the phone is redrawn without the repair checks')

    # ---- 6. the page reads the server when it comes back, and redraws ----
    fresh(L); P.goto('https://sorted.test/'); P.evaluate("localStorage.clear()")
    cid = make_case(L, 'BT said the engineer would come on %s, ref BT445566' % nextwd(4).strftime('%A'))
    past(L, cid); sync(L, P); sign_in(P); open_case(P, cid)
    click(P, '.promise [data-a=missed]', 900)
    ok(P.locator('form[data-f=call], #callform, [data-a=call-send], .call').count() > 0 or srv(P, cid)['promises'][-1]['status'] == 'missed', 'the phone recorded the miss and opened the chase')
    sync(P, L); open_case(L, cid)
    if L.locator('[data-a=panel][data-p=done]').count(): click(L, '[data-a=panel][data-p=done]', 300)
    if L.locator('#f-outcome').count():
        L.fill('#f-outcome', 'BT sorted it in the end'); L.locator('form[data-f=done] button[type=submit]').click(); wait(L, 900)
    ok(srv(L, cid)['board'] == 'done', 'the laptop finished the case')
    sync(L, P); P.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); wait(P, 900)
    m = P.inner_text('main')
    ok(srv(P, cid)['board'] == 'done' and not P.locator('form[data-f=call]').count() and 'BT sorted it in the end' in m, 'coming back, the phone shows the finished case, not the chase form')
    ok('changed elsewhere' in toast(P), 'and says it changed elsewhere (%r)' % toast(P))

    # ---- 7. two tabs: one deletes, the other is stale; sign-out in one counts the other's unsent edit ----
    T1 = page(cL); T2 = page(cL)
    fresh(T1)
    Y = make_case(T1, 'Evri said they would deliver my parcel by %s' % nextwd(4).strftime('%A'))
    X = make_case(T1, 'Currys said they would refund £89 by %s, order 112233, my note ORANGE' % nextwd(4).strftime('%A'))
    T2.goto('https://sorted.test/'); wait(T2, 900)
    open_case(T1, X); click(T1, '[data-a=panel][data-p=more]', 300) if T1.locator('[data-a=panel][data-p=more]').count() else None
    T1.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); click(T1, '[data-a=panel][data-p=delcase]', 300); click(T1, '[data-a=case-del]', 900)
    ok(not srv(T1, X), 'tab 1 deleted the case')
    wait(T2, 600)
    ok('ORANGE' not in T2.inner_text('main') and 'Currys' not in T2.inner_text('main'), 'tab 2 drops it when tab 1 saves')
    # a stale tab's unsent copy of the deleted case lands in the phone copy; the next save anywhere drops it
    T2.evaluate("(id)=>{var k='sorted.cache.u-me',a=JSON.parse(localStorage.getItem(k)||'[]');a.push({id:id,title:'Currys ORANGE',said:'ORANGE',rev:5,promises:[],moves:[],events:[],_dirty:true,_tab:'stale',updatedAt:new Date().toISOString()});localStorage.setItem(k,JSON.stringify(a))}", X)
    open_case(T2, Y); click(T2, '[data-a=panel][data-p=rename]', 250); T2.fill('#f-rename', 'Evri parcel'); T2.click('form[data-f=rename] button[type=submit]'); wait(T2, 700)
    ok('ORANGE' not in (T1.evaluate("localStorage.getItem('sorted.cache.u-me')") or ''), 'a stale tab never writes a deleted case back into the phone copy')
    off = page(cL)
    off.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(body=open(HERE + '/tests/mock.js').read().replace('if(op==="select"){var fr', 'if(op==="select"&&table==="tasks")return {data:null,error:{message:"Failed to fetch"}};if(op==="select"){var fr'), content_type='application/javascript'))
    off.goto('https://sorted.test/'); wait(off, 1000)
    ok('Currys' not in off.inner_text('main') and 'Evri' in off.inner_text('main'), 'an offline start shows the copy on this phone without the deleted case')
    off.close()
    # tab 2 has an unsent edit; tab 1 signs out
    T1.evaluate("localStorage.setItem('__failWrites','1')")
    open_case(T2, Y); click(T2, '[data-a=panel][data-p=rename]', 250); T2.fill('#f-rename', 'Edit only on tab 2'); T2.click('form[data-f=rename] button[type=submit]'); wait(T2, 700)
    T1.goto('https://sorted.test/#more'); wait(T1, 700)
    if not T1.locator('[data-a=signout]').count(): click(T1, '[data-a=data]', 500)
    T1.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
    click(T1, '[data-a=signout]', 900)
    ok(T1.locator('.signout114').count() > 0 and '1 case' in T1.inner_text('main'), 'sign-out in tab 1 asks about tab 2’s unsent edit')
    T1.evaluate("localStorage.removeItem('__failWrites')")
    if T1.locator('[data-a=signout-wait]').count(): click(T1, '[data-a=signout-wait]', 1500)
    ok(srv(T1, Y) and srv(T1, Y)['title'] == 'Edit only on tab 2', 'waiting sends it before signing out (%r)' % (srv(T1, Y) or {}).get('title'))
    T1.close(); T2.close()

    # ---- 8. a helper link switched off on one device is never copied by a stale one ----
    cL.grant_permissions(['clipboard-read', 'clipboard-write'], origin='https://sorted.test'); cP.grant_permissions(['clipboard-read', 'clipboard-write'], origin='https://sorted.test')
    fresh(L); P.goto('https://sorted.test/'); P.evaluate("localStorage.clear()")
    cid = make_case(L, 'Currys said they would refund £89 by %s, order 445566' % nextwd(4).strftime('%A'))
    open_case(L, cid); click(L, '[data-a=share]', 900)
    ok(srv(L, cid).get('shareToken') and db(L).get('shares'), 'the laptop shared it')
    sync(L, P); sign_in(P); open_case(P, cid)
    L.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); click(L, '[data-a=unshare]', 900)
    ok(not srv(L, cid).get('shareToken'), 'the laptop switched it off')
    sync(L, P); P.evaluate("navigator.clipboard.writeText('nothing')")
    click(P, '[data-a=share]', 1000)
    ok(P.evaluate("navigator.clipboard.readText()") == 'nothing' and 'switched off' in toast(P), 'the stale phone copies nothing and says the link was switched off (%r)' % toast(P))
    ok(not db(P).get('shares'), 'and no new link was made')

    # ---- 9. a case too big to save says so (PASS2-031) ----
    fresh(P)
    cid = make_case(P, 'Argos said they would refund £30 by %s, order 778899' % nextwd(4).strftime('%A'))
    before = srv(P, cid)['rev']
    def grow(q, cid, n):   # a long message lands in the copy on this phone, unsent
        q.evaluate("([id,n])=>{var k='sorted.cache.u-me',a=JSON.parse(localStorage.getItem(k));var t=a.find(x=>x.id===id);t.events.push({at:new Date().toISOString(),label:'Added a message: “'+'x'.repeat(n)+'”'});t._dirty=true;t.updatedAt=new Date().toISOString();localStorage.setItem(k,JSON.stringify(a))}", [cid, n])
    grow(P, cid, 120000); open_case(P, cid); wait(P, 600)
    st = P.locator('[data-sync]').first.inner_text() if P.locator('[data-sync]').count() else ''
    ok(st.startswith('Too big to save: remove a long message'), 'a save the server refuses for size says so (%r)' % st)
    ok(srv(P, cid)['rev'] == before, 'and nothing was saved')
    P.goto('https://sorted.test/'); wait(P, 600)
    ok('not yet sent' in P.inner_text('main') or 'Too big' in P.inner_text('main'), 'Home still counts it as not sent')
    open_case(P, cid); click(P, '[data-a=ev-del]', 900)
    st = P.locator('[data-sync]').first.inner_text() if P.locator('[data-sync]').count() else ''
    ok(srv(P, cid)['rev'] > before and 'xxxxxxxxxx' not in json.dumps(srv(P, cid)) and st.startswith('Saved to your account'), 'removing the long message lets it save (%r)' % st)
    before = srv(P, cid)['rev']; grow(P, cid, 450000); open_case(P, cid); wait(P, 600)
    rec = [x for x in json.loads(P.evaluate("localStorage.getItem('sorted.cache.u-me')")) if x['id'] == cid][0]
    st = P.locator('[data-sync]').first.inner_text() if P.locator('[data-sync]').count() else ''
    ok(rec.get('_big') and not rec.get('_refused') and srv(P, cid)['rev'] == before and st.startswith('Too big to save'), 'a copy far beyond the cap is never sent (%r)' % st)

    print('ERRORS', errs)
    print('FAILS', fails)
    br.close()
