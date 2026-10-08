# v124 (remediation Phase B): the fact ledger. Every detail Sorted holds about a case has a row with where it came from,
# when, its status and what it replaced. Rules: nothing silently disappears (a change supersedes, the old row stays);
# a reading from the person's words, a photo or a message is never "confirmed" until the person confirms it; Sorted's
# own suggestion (the outcome wanted) is proposed until kept; a thing ruled out ("it's not the boiler") is recorded as
# ruled out, never as the thing; a reference turned down stays turned down; a replaced promise is superseded by the
# next with a link; older cases gain a ledger on opening without anything else changing; the case page and the adviser
# pack show the ledger.
import os, sys, json, datetime, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    case = lambda cid: [x for x in cases() if x['id'] == cid][0]
    L = lambda cid: case(cid).get('ledger') or []
    live = lambda cid, typ, sub=None: [r for r in L(cid) if r['type'] == typ and (sub is None or r.get('sub', '') == sub) and r['st'] not in ('superseded', 'rejected')]
    rows = lambda cid, typ, sub=None: [r for r in L(cid) if r['type'] == typ and (sub is None or r.get('sub', '') == sub)]
    main = lambda: pg.inner_text('main')
    def poke(js):
        pg.goto('https://sorted.test/'); wait(pg, 700)
        pg.evaluate("(js)=>{var db=JSON.parse(localStorage.getItem('__mockdb'))||{tasks:[],shares:[],reminders:[],helpers:[],inbound_items:[],pilot_events:[],case_notes:[]};(new Function('db',js))(db);localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", js)
    def start(text, settle=True):
        pg.goto('https://sorted.test/'); wait(pg, 500)
        if pg.locator('[data-a=new-case]').count(): pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        return cases()[-1]['id']
    def paste(cid, text):
        pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 500)
        pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
        if pg.locator('[data-a=panel][data-p=paste]').count(): pg.click('[data-a=panel][data-p=paste]'); wait(pg, 300)
        pg.fill('#f-paste', text); pg.click('form[data-f=paste] button[type=submit]'); wait(pg, 600)
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    uid = pg.evaluate("JSON.parse(localStorage.getItem('__mocksession')).user.id")
    fri = datetime.date.today() + datetime.timedelta(days=(4 - datetime.date.today().weekday()) % 7 or 7)
    # ---- 1. a refund case: the details are read, not confirmed, until the promise card is confirmed ----
    cid = start('Currys said they would refund £89 by %s, order 445566' % fri.strftime('%A'))
    wait(pg, 400)
    party = live(cid, 'party'); ref = live(cid, 'ref', ''); prom = live(cid, 'promise')
    ok(party and party[0]['v'] == 'Currys' and party[0]['st'] == 'read' and party[0]['by'] == 'sorted' and 'what you wrote' in party[0]['src'], 'who: read from your words by Sorted, not confirmed (%s)' % (party and party[0]['st']))
    ok(ref and ref[0]['v'] == '445566' and ref[0]['st'] == 'read', 'the reference: read, not confirmed')
    ok(prom and prom[0]['sub'] == 'proposal' and prom[0]['st'] == 'proposed' and 'refund' in prom[0]['v'].lower(), 'their promise: a proposal until confirmed')
    ok(all('at' in r and r.get('id') for r in L(cid)), 'every row has a time and an id')
    pg.click('[data-a=sug-yes]'); wait(pg, 700)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
    party = live(cid, 'party'); prom = live(cid, 'promise'); old = rows(cid, 'promise', 'proposal')
    ok(party and party[0]['st'] == 'confirmed' and party[0].get('cby') == 'you', 'once the promise is confirmed, who and the reference are confirmed by you')
    ok(len(prom) == 1 and prom[0]['st'] == 'confirmed' and prom[0].get('cby') == 'you' and old and old[0]['st'] == 'superseded' and prom[0].get('sup') == old[0]['id'], 'the confirmed promise supersedes the proposal, with a link; the proposal row stays')
    # ---- 2. a correction supersedes; the old value stays with a link ----
    if pg.locator('[data-a=goal-skip]').count(): pg.click('[data-a=goal-skip]'); wait(pg, 300)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    paste(cid, 'Sorry, I got the order number wrong, it should be 445577')
    if pg.locator('[data-a=corr-yes]').count(): pg.click('[data-a=corr-yes]'); wait(pg, 600)
    rr = rows(cid, 'ref', '')
    ok(case(cid)['facts']['ref'] == '445577' and len(rr) == 2 and rr[0]['v'] == '445566' and rr[0]['st'] == 'superseded' and rr[1]['v'] == '445577' and rr[1]['st'] == 'confirmed' and rr[1]['by'] == 'you' and rr[1].get('sup') == rr[0]['id'], 'a corrected reference: the new row is confirmed by you and supersedes the old, which stays (%s)' % [(r['v'], r['st']) for r in rr])
    # ---- 3. Sorted's suggested outcome is proposed until kept; "Not sure yet" turns it down ----
    cid2 = start('Aviva said they would decide my claim by %s, claim AV-7788' % fri.strftime('%A'))
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
    g = live(cid2, 'goal')
    ok(g and g[0]['st'] == 'proposed' and g[0]['by'] == 'sorted', 'the outcome Sorted suggests is proposed, not confirmed (%s)' % (g and g[0]['v']))
    ok(pg.locator('form[data-f=goal]').count() == 1, 'the outcome form is on screen')
    pg.fill('#f-goal', 'Get the claim paid in full'); pg.click('form[data-f=goal] button[type=submit]'); wait(pg, 500)
    g = rows(cid2, 'goal')
    ok(len(g) == 2 and g[0]['st'] == 'superseded' and g[1]['v'] == 'Get the claim paid in full' and g[1]['st'] == 'confirmed' and g[1]['by'] == 'you' and g[1]['src'] == 'your words', 'the outcome you typed is confirmed by you and supersedes the suggestion')
    # ---- 4. a reference turned down stays turned down ----
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    paste(cid2, 'Thanks for your call. Your complaint reference is CMP-99001.')
    if pg.locator('[data-a=cm-no]').count(): pg.click('[data-a=cm-no]'); wait(pg, 300)
    if pg.locator('[data-a=refs-no]').count(): pg.click('[data-a=refs-no]'); wait(pg, 500)
    rj = [r for r in L(cid2) if r['type'] == 'ref' and r['v'] == 'CMP-99001']
    ok(rj and rj[0]['st'] == 'rejected' and rj[0]['by'] == 'sorted' and not live(cid2, 'ref', 'complaint'), 'a reference you turned down is rejected in the ledger, never confirmed (%s)' % (rj and rj[0]['st']))
    # ---- 5. a thing ruled out is never the thing ----
    cid3 = start('The boiler isn’t broken, it’s the thermostat'); wait(pg, 300)
    it = live(cid3, 'item'); ro = rows(cid3, 'ruled_out')
    ok(it and it[0]['v'].lower() == 'thermostat', 'what it is: the thermostat (%s)' % (it and it[0]['v']))
    ok(ro and ro[0]['v'] == 'boiler' and ro[0]['st'] == 'ruled_out' and ro[0]['by'] == 'you' and not any(r['type'] == 'item' and r['v'].lower() == 'boiler' and r['st'] != 'ruled_out' for r in L(cid3)), 'the boiler is recorded as ruled out, never as the thing')
    # ---- 6. notice details: proposed from the notice, confirmed only by you ----
    cid4 = start('London Borough of Southwark PENALTY CHARGE NOTICE PCN Number: SK12345678 Vehicle Registration Mark: AB12 CDE Date of contravention: 30/09/2026 The penalty charge is £130.')
    wait(pg, 300)
    nr = live(cid4, 'notice')
    ok(nr and all(r['st'] == 'proposed' and r['by'] in ('notice', 'sorted') and not r.get('cby') for r in nr) and any(r['sub'] == 'ref' and r['v'] == 'SK12345678' for r in nr), 'notice details are proposed from the notice, none confirmed (%d rows)' % len(nr))
    for _ in range(3):
        if pg.locator('[data-a=cf-yes]').count(): pg.click('[data-a=cf-yes]'); wait(pg, 500)
        elif pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    nr = live(cid4, 'notice')
    ok(nr and all(r['st'] == 'confirmed' and r.get('cby') == 'you' for r in nr), 'after "Are they right?" every notice detail is confirmed by you')
    # ---- 7. a replaced promise is superseded by the next, with a link ----
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 500)
    paste(cid, 'Currys now say the refund will be on %s instead' % (fri + datetime.timedelta(days=7)).strftime('%A %-d %B'))
    if pg.locator('[data-a=corr-moved]').count(): pg.click('[data-a=corr-moved]'); wait(pg, 600)
    elif pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
    pr = [r for r in L(cid) if r['type'] == 'promise' and r['sub'] != 'proposal']
    ok(len(pr) == 2 and pr[0]['st'] == 'superseded' and pr[1]['st'] == 'confirmed' and pr[1].get('sup') == pr[0]['id'], 'a moved date: the old promise row is superseded and the new one links to it (%s)' % [(r['st'], r.get('sup') is not None) for r in pr])
    # ---- 8. an older case gains a ledger on opening, with nothing else changed ----
    old_case = {'id': 'old1', 'title': 'BT · broadband', 'mode': 'call', 'board': 'waiting', 'created': '2026-09-20T10:00:00.000Z', 'updatedAt': '2026-09-20T10:00:00.000Z', 'rev': 2,
                'said': 'BT said an engineer would come on Monday, ref VOL011-22334', 'facts': {'party': 'BT', 'ref': 'VOL011-22334', 'kind': 'service'},
                'promises': [{'id': 'p1', 'said': 'An engineer would come', 'party': 'BT', 'ref': 'VOL011-22334', 'dueAt': '2026-10-12T23:59:59.000Z', 'allDay': True, 'status': 'open', 'loggedAt': '2026-09-20T10:00:00.000Z', 'src': 'sentence'}],
                'refs': [{'k': 'complaint', 'v': 'C-5566', 'at': '2026-09-21T10:00:00.000Z', 'src': 'their message', 'st': 'confirmed'}], 'corr': [{'k': 'party', 'from': 'Bt', 'to': 'BT', 'at': '2026-09-21T10:00:00.000Z', 'how': 'fixed', 'src': 'your message'}],
                'goal': 'Broadband working', 'turn': 'theirs', 'moves': [], 'events': [{'at': '2026-09-20T10:00:00.000Z', 'label': 'Started.'}]}
    poke("db.tasks.push({id:'old1',user_id:%s,data:%s,updated_at:new Date().toISOString()})" % (json.dumps(uid), json.dumps(old_case)))
    pg.goto('https://sorted.test/?task=old1'); wait(pg, 900)
    c = case('old1'); keep = {k: v for k, v in c.items() if k not in ('ledger', 'ledgerV', 'rev', 'wid', 'updatedAt')}
    base = {k: v for k, v in old_case.items() if k not in ('rev', 'updatedAt')}
    ok(c.get('ledger') and c.get('ledgerV') == 1 and keep == base, 'an older case gains a ledger and nothing else changes (%s)' % [k for k in set(keep) | set(base) if keep.get(k) != base.get(k)])
    lp = live('old1', 'party'); lr = live('old1', 'ref', 'complaint'); lg = live('old1', 'goal'); lt = live('old1', 'turn'); lpr = live('old1', 'promise')
    ok(lp and lp[0]['v'] == 'BT' and lp[0]['st'] == 'confirmed' and lp[0]['by'] == 'you' and 'correction' in lp[0]['src'], 'the corrected party is confirmed by you, from the correction')
    ok(lr and lr[0]['st'] == 'confirmed' and lr[0]['src'] == 'their message' and lg and lg[0]['st'] == 'confirmed' and lt and lt[0]['v'] == 'Theirs' and lpr and lpr[0]['st'] == 'confirmed', 'its reference, outcome, whose move and promise are in the ledger with their sources')
    # ---- 9. the case page and the adviser pack show the ledger ----
    pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); m = main()
    ok('Where each detail came from' in m and 'Who\nBT' in m and 'from your correction, from your message, confirmed by you' in m and 'Sorted keeps every version' in m, 'the case page lists each detail with where it came from and whether you confirmed it')
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 500); pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); m = main()
    ok('Changed or turned down' in m and '445566' in m and 'replaced' in m, 'a superseded value is shown under Changed or turned down, never hidden')
    pg.evaluate("document.querySelectorAll('details.case56-more').forEach(d=>d.open=true)")
    if pg.locator('[data-a=panel][data-p=pack]').count(): pg.click('[data-a=panel][data-p=pack]'); wait(pg, 500)
    pk = main()
    ok('Details and where they came from' in pk and 'Reference: 445577 (from your correction' in pk and 'Reference: 445566' in pk, 'the adviser pack lists every detail, the replaced one included')
    ok(not errs, 'no page errors: %s' % errs)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
