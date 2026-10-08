# v143 (audit pass 2, Reviewer 6's matrix): twelve transitions of a case, each checked against the locked truth on every
# surface it touches: Home, the case page and its Now card, What Sorted understood, the helper's share card, the adviser
# pack and the export.
#   1 a typo fixed is not a reschedule; a reschedule replaces the promise; the automatic title follows (PASS2-020)
#   2 three reschedules: one open promise, the title and every surface on the last date
#   3 £40 corrected to £45: the amount the rest is counted against
#   4 part then the rest (PASS2-015): a part before the date keeps the promise live; £20 then £20 ends kept; a part
#     after the date is "only part of it" with the outstanding amount, and the rest arriving is kept late
#   5 a party correction: every surface names the corrected party (word-level checks are test 62's)
#   6 two organisations (PASS2-009): a second sender's promise is offered as a second promise or a new case, never
#     replaces the first, and every surface lists both
#   7 a hand-off: asked before the promise card; the new promise is the new holder's; Home, Now and the chase use them
#   8 both owe: their promise and the person's own step; the share card calls it their own step, never "Their next step"
#   9 done outside Sorted: finishing as "Refunded" closes the open promise as kept, never "turned down by you"
#  10 a refusal on an ordinary case: proposed as "They've said no", withdrawn by them, reminders stop, next step opens
#  11 late: a promise recorded as not happening that then happens is kept late, everywhere
#  12 a no-show, a new booking, then attendance: the title follows; the share card and pack say it happened
# Dates are relative to today on a clock the test moves forward (London time).
import os, sys, json, datetime, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
SESSION = json.dumps({'user': {'id': 'u-me', 'email': 'me@example.com'}})
today = datetime.date.today()
T0 = datetime.datetime.combine(today, datetime.time(9, 0))
def fday(d): return d.strftime('%A ') + str(d.day) + d.strftime(' %B')
def dn(k): return fday(today + datetime.timedelta(days=k))
OFF = [0]  # how many days the test clock has moved on
def dd(k): return dn(OFF[0] + k)  # a day relative to the app's today
# a test-only copy of the page that exposes what the surfaces are built from (production is untouched)
src = open(HERE + '/tests/out/index.html').read(); hook = '\nboot();\n})();\n'
assert src.count(hook) == 1, 'end of the main script not found exactly once'
open(HERE + '/tests/out/truth106.html', 'w').write(src.replace(hook, '\nwindow.__T={S:S,packText:packText,shareCard:shareCard,callDefaults:callDefaults,openPs:openPs,calTimes:calTimes};' + hook))
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844}, accept_downloads=True)
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/truth106.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    ctx.route(lambda u: 'gov.uk' in u, lambda r: r.fulfill(body='<title>Official page</title>', content_type='text/html'))
    ctx.clock.install(time=T0)
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    case = lambda cid: [c for c in cases() if c['id'] == cid][0]
    P = lambda cid: case(cid)['promises']
    st = lambda cid: [(q.get('party'), q['status']) for q in P(cid)]
    labels = lambda cid: [e.get('label') or '' for e in case(cid)['events']]
    rems = lambda cid: [r for r in dbj().get('reminders', []) if r['task_id'] == cid and not r.get('sent_at')]
    main = lambda: pg.inner_text('main')
    def tap(a): pg.locator('.tab129 [data-a=%s]' % a).first.click(); wait(pg, 500)
    now = lambda: pg.inner_text('.now137') if pg.locator('.now137').count() else ''
    def click(sel, ms=600):
        k = pg.locator(sel).count()
        if k: pg.locator(sel).first.evaluate('e=>e.click()'); wait(pg, ms)
        return k
    def at(days, hour=9):  # move the clock forward and reload
        OFF[0] = days; ctx.clock.set_system_time(T0 + datetime.timedelta(days=days, hours=hour - 9)); pg.goto('https://sorted.test/'); wait(pg, 800)
    def start(text, keep=True):
        tap('new-case'); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 700)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        if keep and pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
        if pg.locator('[data-a=nudge-skip]').count(): pg.click('[data-a=nudge-skip]'); wait(pg, 300)
        if pg.locator('[data-a=refs-yes]').count(): pg.click('[data-a=refs-yes]'); wait(pg, 300)
        return cases()[-1]['id']
    def opencase(cid): pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 800)
    def panel(pn): pg.locator('[data-a=panel][data-p="%s"]' % pn).first.evaluate('e=>e.click()'); wait(pg, 400)
    def paste(cid, text):
        opencase(cid); panel('paste'); pg.fill('#f-paste', text); pg.click('form[data-f=paste] button[type=submit]'); wait(pg, 800)
    def correct(cid, text):
        opencase(cid); panel('correct'); pg.fill('#f-correct', text); pg.click('form[data-f=correct] button[type=submit]'); wait(pg, 600)
    def tobj(cid): return "__T.S.tasks.filter(function(x){return x.id==='%s'})[0]" % cid
    def pack(cid): return pg.evaluate("()=>__T.packText(%s)" % tobj(cid))
    def chase(cid): return pg.evaluate("()=>__T.callDefaults(%s)" % tobj(cid))
    def home():
        tap('go-home'); return main()
    def homerow(cid):
        home(); return pg.evaluate("(id)=>{var e=document.querySelector('[data-id=\"'+id+'\"]');return e?e.innerText:''}", cid)
    def understood(cid):
        opencase(cid); pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); wait(pg, 150)
        return pg.inner_text('details.case117-u') if pg.locator('details.case117-u').count() else ''
    def share(cid):
        opencase(cid)
        if not case(cid).get('shareToken'):
            pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); wait(pg, 150); click('details.case56-sharing [data-a=share]', 900)
        tok = case(cid).get('shareToken')
        if not tok: return ''
        hp = ctx.new_page(); hp.goto('https://sorted.test/?share=' + tok); wait(hp, 900); txt = hp.inner_text('main'); hp.close(); return txt
    def export():
        tap('data'); wait(pg, 300)
        try:
            with pg.expect_download(timeout=8000) as dl: click('[data-a=export-file]', 900)
            return open(dl.value.path(), encoding='utf-8').read()
        except Exception as e: return 'EXPORT FAILED ' + str(e)[:100]
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')")
    pg.evaluate("localStorage.setItem('__mocksession', %s)" % json.dumps(SESSION)); pg.goto('https://sorted.test/'); wait(pg, 700)

    # ================= 1. a typo is not a reschedule; a reschedule is; the title follows =================
    c1 = start('British Gas said an engineer will come on %s between 8am and 12pm, job 77123' % dn(3))
    t1 = case(c1)['title']
    correct(c1, 'Sorry, I meant %s' % dn(4).split(' ')[0])
    click('[data-a=corr-yes]')
    ok(st(c1) == [('British Gas', 'open')] and not any('They changed the date' in l for l in labels(c1)), '1 a typo fixed keeps one promise and is not a reschedule: %s' % st(c1))
    ok(dn(4) in homerow(c1) and dn(3) not in homerow(c1) and dn(3) not in case(c1)['title'], '1 Home shows the corrected day: %r' % homerow(c1))
    paste(c1, 'British Gas: your engineer visit has been moved to %s between 8am and 12pm' % dn(6))
    click('[data-a=sug-yes]')
    ok(st(c1) == [('British Gas', 'replaced'), ('British Gas', 'open')] and any('They changed the date' in l for l in labels(c1)), '1 a reschedule from the same company replaces the promise: %s' % st(c1))
    ti = case(c1)['title']
    ok(dn(4) not in ti and dn(6) in homerow(c1) and dn(4) not in homerow(c1), '1 no old day in the title, Home row on the new day: %r' % ti)
    sh = share(c1); pk = pack(c1)
    ok(dn(6) in sh and ('· ' + dn(4)) not in sh, '1 the share card is on the new day')
    ok(pk.split('\n')[0] == ti and 'Replaced by a later date.' in pk, '1 the pack has the current title and says the old date was replaced')

    # ================= 2. three reschedules =================
    c2 = start('Evri said they would deliver my parcel on %s, ref EV123456' % dn(2))
    for k in (3, 5, 7):
        paste(c2, 'Evri: your delivery has been rescheduled to %s' % dn(k)); click('[data-a=sug-yes]')
    ss = [s for (_, s) in st(c2)]
    ok(ss.count('open') == 1 and ss.count('replaced') == 3, '2 three reschedules leave one open promise: %s' % ss)
    ok(not any(dn(k) in case(c2)['title'] for k in (2, 3, 5)) and dn(7) in homerow(c2) and dn(5) not in homerow(c2), '2 no dead date in the title, Home on the last date: %r' % case(c2)['title'])
    opencase(c2); ok(dn(7) in now() and dn(5) not in now(), '2 the Now card is on the last date')
    pk = pack(c2); ok(pk.count('Replaced by a later date.') == 3 and pk.split('\n')[0] == case(c2)['title'], '2 the pack lists the three replaced dates under the current title')
    sh = share(c2); ok(dn(7) in sh and 'Their next step' not in sh, '2 the share card is on the last date')

    # ================= 3 and 4. £40 → £45, then part and the rest =================
    c3 = start('Currys said they would refund my £40 by %s, order 445566' % dn(10))
    correct(c3, 'Sorry, £45 not £40'); click('[data-a=corr-yes]')
    ok('£45' in P(c3)[-1]['said'] and str(case(c3)['facts'].get('amount')) == '45', '3 the amount is £45 on the promise and the facts')
    opencase(c3); ok(pg.locator('[data-a=panel][data-p=partly]').count() > 0, '4 a refund before its date offers “Some of it has arrived”')
    panel('partly'); ok(pg.locator('#f-got').count() == 1 and 'Save what has arrived' in main(), '4 before the date the form asks how much has arrived')
    pg.fill('#f-got', '£20'); pg.click('form[data-f=partly] button[type=submit]'); wait(pg, 700)
    q = P(c3)[-1]
    ok(q['status'] == 'open' and not q.get('partly') and (q.get('parts') or [{}])[0].get('amt') == 20, '4 a part before the date keeps the promise live, with its amount: %s %s' % (q['status'], q.get('parts')))
    ok(any('Part of it arrived: £20. Still to come: £25 of the £45' in l for l in labels(c3)), '4 the history says what arrived and what is still to come')
    ok('Waiting for Currys' in homerow(c3) and 'Only partly' not in homerow(c3), '4 Home still waits for Currys')
    ok('Promises they didn’t keep' not in share(c3), '4 the share card shows no broken promise')
    ok('That didn’t happen' not in pack(c3) and 'Arrived so far: £20' in pack(c3), '4 the pack says what has arrived so far, not a miss')
    paste(c3, 'The other £25 has arrived from Currys today')
    ok(pg.locator('[data-a=out-yes]').count() == 1 and 'the rest has arrived' in main(), '4 “The other £25 has arrived” is proposed as the rest arriving')
    ok(P(c3)[-1]['status'] == 'open', '4 nothing changes before the tap')
    click('[data-a=out-yes]', 900)
    q = P(c3)[-1]
    ok(q['status'] == 'kept' and not q.get('late'), '4 the rest arriving before the date ends kept: %s' % q['status'])
    pk = pack(c3); ok('That happened' in pk and 'Still outstanding: .' not in pk and 'didn’t happen' not in pk, '4 the pack says it happened')
    sh = share(c3); ok('Promises they kept' in sh and 'Promises they didn’t keep' not in sh, '4 the share card says it was kept')
    # £20 then £20 through the form ends kept
    c4 = start('Argos said they would refund my £40 by %s, order 556677' % dn(10))
    for _ in range(2):
        opencase(c4); panel('partly'); pg.fill('#f-got', '£20'); pg.click('form[data-f=partly] button[type=submit]'); wait(pg, 800)
    q = P(c4)[-1]
    ok(q['status'] == 'kept' and len(q.get('parts') or []) == 2, '4 £20 then £20 before the deadline ends kept: %s' % q['status'])
    ok(any('That’s all £40' in l for l in labels(c4)) and 'That happened, in parts: £20 on' in pack(c4), '4 the history and the pack say it came in two parts')
    # a part after the date: only part of it, with the amount outstanding, never blank
    c5 = start('Amazon said they would refund my £45 by %s, order 204-111' % dn(2))
    at(3)
    opencase(c5); panel('partly'); pg.fill('#f-got', '£20'); pg.click('form[data-f=partly] button[type=submit]'); wait(pg, 700)
    q = P(c5)[-1]
    ok(q['status'] == 'missed' and q.get('partly') and q.get('left') == '£25 of the £45', '4 a part after the date: only part of it, £25 outstanding: %s %r' % (q['status'], q.get('left')))
    pk = pack(c5); ok('Still outstanding: £25 of the £45' in pk and 'Still outstanding: .' not in pk and 'That didn’t happen.' not in pk, '4 the pack says only part of it happened, with the amount')
    sh = share(c5); ok('Only part of it happened' in sh and 'Still outstanding: £25 of the £45' in sh and 'Promises they didn’t keep' not in sh, '4 the share card says only part of it happened')
    ok('only partly happened. Still outstanding: £25 of the £45' in chase(c5)['ask'], '4 the chase asks for the £25')
    paste(c5, 'The other £25 has arrived today')
    ok('happened after all' in main(), '4 the rest after a part-miss is proposed as late')
    click('[data-a=out-yes]', 900)
    q = P(c5)[-1]; ok(q['status'] == 'kept' and q.get('late'), '4 the rest arriving late: kept late')
    ok('after the date they gave' in pack(c5) and 'It happened, but late' in share(c5), '4 pack and share say it was late')

    # ================= 5. a party correction: every surface agrees =================
    c6 = start('BT said they would credit my bill by %s, ref BT12345' % dn(5))
    correct(c6, 'Sorry, it was EE not BT'); click('[data-a=corr-yes]')
    ok(P(c6)[-1]['party'] == 'EE', '5 the promise is EE’s')
    ok('EE' in homerow(c6) and 'Waiting for EE' in homerow(c6), '5 Home says EE')
    ok('- Who: EE' in pack(c6) and chase(c6)['who'] == 'EE', '5 the pack and the chase say EE')

    # ================= 6. two organisations in one case =================
    c7 = start('My landlord said the plumber will come on %s to fix the leak' % dd(2))
    paste(c7, 'British Gas: we will refund £30 to your account by %s' % dd(10))
    m = main()
    ok('British Gas promised' in m and 'Landlord promised' not in m, '6 the second message is British Gas’s, not the landlord’s')
    ok(pg.locator('[data-a=sug-yes][data-m=add]').count() == 1 and pg.locator('[data-a=sug-new143]').count() == 1 and pg.locator('[data-a=sug-yes][data-m=replace]').count() == 1, '6 it offers a second promise, a new case, or a replacement')
    ok('Add as a second promise in this case' in m and 'Start a new case for British Gas' in m and 'It replaces the current one' in m, '6 the three choices say what they do')
    ok(st(c7) == [('Landlord', 'open')], '6 nothing changes before the tap')
    click('[data-a=sug-yes][data-m=add]', 800)
    ok(sorted(st(c7)) == [('British Gas', 'open'), ('Landlord', 'open')], '6 both promises are open: %s' % st(c7))
    ok(not any('They changed the date' in l for l in labels(c7)), '6 adding is never logged as a changed date')
    m = main(); ok(m.count('THEY PROMISED') + m.count('They promised') >= 2 and 'Also in this case' in m.replace('ALSO IN THIS CASE', 'Also in this case'), '6 the case page has a card for each promise')
    u = understood(c7); ok(u.count('Their date') == 2 and 'from British Gas' in u and 'from your landlord' in u, '6 What Sorted understood lists both dates')
    r = homerow(c7); ok('Landlord' in r and 'Also: British Gas' in r, '6 Home lists both: %r' % r)
    sh = share(c7); ok('The plumber will come' in sh and 'We will refund £30' in sh, '6 the share card shows both promises')
    pk = pack(c7); ok('- Who: Landlord, British Gas' in pk and 'Waiting for your landlord and British Gas' in pk and pk.count('IMPORTANT DATES') == 1 and 'British Gas: We will refund £30' in pk, '6 the pack names both and dates both')
    cal = pg.evaluate("()=>__T.calTimes(%s).map(function(x){return x.promise_id})" % tobj(c7))
    ok(all(any(pid == q['id'] for pid in cal) for q in P(c7)), '6 each promise has its own reminders')
    # the earlier one is answered; the other stays
    at(OFF[0] + 3, 10); opencase(c7)
    click('.promise [data-a=kept]', 800)
    ok(sorted(st(c7)) == [('British Gas', 'open'), ('Landlord', 'kept')], '6 answering one leaves the other open: %s' % st(c7))
    # a new case for a second sender instead
    c8 = start('Ford said they would finish the credit check by %s, ref FD5566' % dd(6))
    paste(c8, 'Santander: we will send your new card by %s' % dd(9))
    click('[data-a=sug-new143]', 800)
    ok(st(c8) == [('Ford', 'open')] and pg.input_value('#f-case').startswith('Santander:'), '6 “Start a new case” leaves this case alone and fills the box for Santander')

    # ================= 7. a hand-off =================
    c9 = start('Ford said they would finish the credit check by %s, ref FD7788' % dd(6))
    paste(c9, 'Ford: your application has been passed to Ford Credit, who will contact you within 5 working days')
    ok(pg.locator('[data-a=ho-yes]').count() == 1 and pg.locator('[data-a=sug-yes]').count() == 0, '7 the hand-off is asked before the promise card')
    click('[data-a=ho-yes]', 700)
    ok('Ford Credit promised' in main(), '7 the promise is then offered as Ford Credit’s')
    click('[data-a=sug-yes]', 800)
    ok(st(c9) == [('Ford', 'replaced'), ('Ford Credit', 'open')] and not any('They changed the date' in l for l in labels(c9)), '7 Ford Credit’s promise takes the place of Ford’s, not a date change: %s' % st(c9))
    ok('Waiting for Ford Credit' in now() and 'Waiting for Ford Credit' in homerow(c9), '7 Now and Home wait for Ford Credit')
    ch = chase(c9); ok(ch['who'] == 'Ford Credit' and 'You said you would' not in ch['ask'] and 'Ford said they would' in ch['ask'], '7 the chase goes to Ford Credit and quotes Ford as Ford: %r' % ch['ask'][:160])
    ok('Ford Credit' in pack(c9) and 'Passed to Ford Credit.' in pack(c9), '7 the pack says it was passed to Ford Credit')

    # ================= 8. both owe: their promise and my own step =================
    c10 = start('Currys said they would refund my £40 by %s, order 778811' % dd(9))
    opencase(c10); click('[data-a=panel][data-p=move]'); pg.fill('#f-mwhat', 'Send Currys the receipt by %s' % dd(8)); pg.locator('#f-mwhat').dispatch_event('input'); wait(pg, 400); click('[data-a=use-msug]', 400)
    pg.click('#moveform button[type=submit]'); wait(pg, 800)
    ok(any(m['status'] == 'open' for m in case(c10).get('moves') or []), '8 the own step is saved')
    sh = share(c10)
    ok('Their next step' not in sh and 'THEIR NEXT STEP' not in sh and ('Their own step' in sh or 'THEIR OWN STEP' in sh) and 'Send Currys the receipt' in sh, '8 the share card calls it their own step, never “Their next step”')
    ok('Your move: Send Currys the receipt' in pack(c10), '8 the pack lists it as the person’s move')
    u = understood(c10); ok('Your step' in u and 'Their date' in u, '8 What Sorted understood keeps their date and your step apart')

    # ================= 9. done outside Sorted =================
    c11 = start('Argos said they would refund my £30 by %s, order 990011' % dd(9))
    opencase(c11); panel('done'); click('[data-a=done-kind][data-v=Refunded]', 300); pg.click('form[data-f=done] button[type=submit]'); wait(pg, 800)
    q = P(c11)[-1]
    ok(q['status'] == 'kept' and case(c11)['board'] == 'done', '9 finishing as Refunded closes the open promise as kept: %s' % q['status'])
    ok(not rems(c11), '9 its reminders are gone')
    pk = pack(c11); ok('turned down by you' not in pk and 'Cancelled, or no longer needed' not in pk and 'That happened' in pk, '9 the pack says it happened, never cancelled or turned down')
    opencase(c11); click('[data-a=case-reopen]', 700)
    ok(P(c11)[-1]['status'] == 'open', '9 Reopen brings the promise back')

    # ================= 10. a refusal on an ordinary case =================
    c12 = start('Currys said they would refund my £60 by %s, order 112233' % dd(9))
    rb = len(rems(c12))
    paste(c12, 'Currys: Unfortunately we are unable to offer a refund for this order as it is outside the return window.')
    ok('they’ve said no' in main() and pg.locator('[data-a=out-yes]').count() == 1, '10 a refusal is proposed as “They’ve said no”')
    ok(P(c12)[-1]['status'] == 'open' and len(rems(c12)) == rb, '10 nothing changes before the tap')
    click('[data-a=out-yes]', 900)
    q = P(c12)[-1]
    ok(q['status'] == 'withdrawn', '10 the promise is withdrawn by them: %s' % q['status'])
    ok(not any(r.get('promise_id') == q['id'] for r in rems(c12)), '10 its reminders stop')
    ok(pg.locator('#moveform').count() == 1 and 'They’ve said no' in main(), '10 the next step opens')
    ok(case(c12)['board'] == 'yours' and 'Waiting for Currys' not in homerow(c12), '10 Home no longer waits for Currys')
    ok('They withdrew it: they said no.' in pack(c12) and 'They said no' in share(c12), '10 the pack and the share card say they said no')
    ok('Withdrawn by them' in pack(c12) or 'withdrawn by them' in pack(c12), '10 the ledger says withdrawn by them')
    c13 = start('British Gas said an engineer will come on %s between 8am and 12pm, job 66110' % dd(4))
    paste(c13, 'We never booked an engineer for you')
    ok('they’ve said no' in main(), '10 “we never booked an engineer” is proposed as a no')
    click('[data-a=out-yes]', 800); ok(P(c13)[-1]['status'] == 'withdrawn', '10 and withdrawn on yes')

    # ================= 11. late =================
    c14 = start('Amazon said they would refund my £25 by %s, order 204-999' % dd(4))
    at(OFF[0] + 5, 10); opencase(c14); click('.promise [data-a=missed]', 800)
    ok(P(c14)[-1]['status'] == 'missed', '11 recorded as not happening')
    paste(c14, 'Amazon: your refund of £25 has been processed today')
    ok('happened after all' in main() and pg.locator('[data-a=sug-yes]').count() == 0, '11 the late arrival is proposed as late, not as a new promise')
    click('[data-a=out-yes]', 900)
    q = P(c14)[-1]; ok(q['status'] == 'kept' and q.get('late'), '11 kept late')
    ok('after the date they gave' in pack(c14) and 'Promises missed' not in pack(c14), '11 the pack says it happened late')
    sh = share(c14); ok('It happened, but late' in sh and 'Promises they didn’t keep' not in sh, '11 the share card says it happened late')

    # ================= 12. no-show, new booking, attendance =================
    b15 = OFF[0]; e7, e10 = dn(b15 + 7), dn(b15 + 10)
    c15 = start('Openreach said an engineer will come on %s between 8am and 1pm, ref OR-55120' % e7)
    opencase(c15); click('[data-a=panel][data-p=move]'); pg.fill('#f-mwhat', 'Ring Openreach on %s if they still haven’t confirmed' % dd(6)); pg.locator('#f-mwhat').dispatch_event('input'); wait(pg, 400); click('[data-a=use-msug]', 400)
    pg.click('#moveform button[type=submit]'); wait(pg, 800)
    at(b15 + 7, 14); opencase(c15); click('.promise [data-a=missed]', 900)
    paste(c15, 'Openreach: Sorry we missed you. Your new appointment is %s between 8am and 12pm' % e10)
    click('[data-a=sug-yes]', 800)
    ti = case(c15)['title']
    ok(e10 in ti and e7 not in ti, '12 the automatic title follows the new booking: %r' % ti)
    ok(e10 in homerow(c15) and e7 not in homerow(c15), '12 Home is on the new booking')
    sh = share(c15); ok(e10 in sh and ('Openreach · ' + e7) not in sh, '12 the share card title is on the new booking')
    ok(pack(c15).split('\n')[0] == ti, '12 the pack title is the new booking')
    at(b15 + 10, 13); opencase(c15); click('.promise [data-a=kept]', 900)
    ok(P(c15)[-1]['status'] == 'kept', '12 attended: kept')
    sh = share(c15)
    ok('it didn’t happen' not in sh and 'Promises they kept' in sh and 'It happened' in sh, '12 the share card says it happened, no “it didn’t happen” ask')
    ok('Their next step' not in sh, '12 the own step is never their next step')
    pk = pack(c15); wst = re.search(r'Where it stands: (.*)', pk).group(1)
    ok('did what they said' in wst and wst != 'Needs you', '12 the pack’s Where it stands says it happened: %r' % wst)

    # ================= the export: every ending worded =================
    ex = export()
    for frag, why in [('That happened, in parts', 'kept in parts'), ('That happened, but after the date they gave', 'kept late'), ('They withdrew it: they said no.', 'withdrawn by them'), ('That didn’t happen.', 'missed'), ('Replaced by a later date.', 'replaced'), ('Passed to Ford Credit.', 'handed on')]:
        ok(frag in ex, 'export: %s (%s)' % (frag, why))
    ok('Still outstanding: .' not in ex and not re.search(r'Their promise: [^\n]*turned down by you', ex), 'export: no blank outstanding amount, no promise “turned down by you”')
    b.close()
print('ERRORS', errs)
print('FAILS', fails)
