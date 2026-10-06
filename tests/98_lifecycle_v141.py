# v141 (the lifecycle audit). What happens to a case after its promise closes, when a date changes, and at the finish:
#   - one next action that matches the card: a refund that arrived asks "Has all of it arrived?", a repair visit asks
#     "Did the visit fix it?", a cancelled or kept last promise asks whether the case is finished (never the empty call
#     form), a typed parking notice asks you to check its details, an HMRC demand names its deadline;
#   - the deadline on a demand is kept as a date, and its reminder is offered until answered;
#   - a title built from a date follows the date (They changed the date, Correct a detail);
#   - a changed date takes the old date out of their words (promise card, history, chase) and out of your own step;
#   - editing a window proposal without touching the date keeps the window; "They've given a firm date" asks "By a day";
#   - "It was always Thursday" on a by-Friday refund stays a by-day deadline, with its 9am reminder;
#   - reminders: a by-day deadline asks the morning after, a window only the morning after it ends;
#   - finished money counts as refunds only when it came back; finishing closes what is open; Reopen brings it back;
#   - renewals offer the earlier start date, and a step months away waits under Later;
#   - "That's not a promise" isn't contradicted; Correct a detail says "From what you typed";
#   - "Only part of it" after "It arrived" records partly, with no company total; pickers start this year;
#     "Nothing agreed yet" offers a follow-up; a confirmed proposal isn't "replaced" in the ledger.
import os, sys, json, datetime, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
SESSION = json.dumps({'user': {'id': 'u-me', 'email': 'me@example.com'}})
today = datetime.date.today()
def lday(iso):  # London date of an ISO timestamp
    return datetime.datetime.fromisoformat(iso.replace('Z', '+00:00')).astimezone().date()
def fday(d): return d.strftime('%A ') + str(d.day) + d.strftime(' %B')
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    ctx.route(lambda u: 'gov.uk' in u, lambda r: r.fulfill(body='<title>Official page</title>', content_type='text/html'))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    case = lambda cid: [c for c in cases() if c['id'] == cid][0]
    openp = lambda cid: [q for q in case(cid)['promises'] if q['status'] == 'open']
    labels = lambda cid: [e.get('label') or '' for e in case(cid)['events']]
    rems = lambda cid: sorted([(r['kind'], r['send_at']) for r in dbj().get('reminders', []) if r['task_id'] == cid and not r.get('sent_at')], key=lambda x: x[1])
    main = lambda: pg.inner_text('main')
    tap = lambda a: (pg.locator('.tab129 [data-a=%s]' % a).click(), wait(pg, 500))
    now = lambda: pg.inner_text('.now137') if pg.locator('.now137').count() else ''
    def poke(js):
        pg.goto('https://sorted.test/'); wait(pg, 600)
        pg.evaluate("(js)=>{var db=JSON.parse(localStorage.getItem('__mockdb'));(new Function('db',js))(db);localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", js)
        pg.goto('https://sorted.test/'); wait(pg, 700)
    def overdue(cid): poke("db.tasks.forEach(function(r){if(r.data.id==='%s')r.data.promises.forEach(function(q){if(q.status==='open'){q.dueAt=new Date(Date.now()-2*864e5).toISOString();q.dueEnd=null;q.allDay=true;q.by=true;delete q.win}})})" % cid)
    def start(text, keep=True):
        tap('new-case'); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        if keep and pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
        if pg.locator('[data-a=nudge-skip]').count(): pg.click('[data-a=nudge-skip]'); wait(pg, 300)
        return cases()[-1]['id']
    def opencase(cid): pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700)
    def pickdate(prefix, d):  # the day / month / year selects of dateField
        pg.select_option('select[data-dp=%s][data-part=d]' % prefix, str(d.day)); pg.select_option('select[data-dp=%s][data-part=m]' % prefix, str(d.month)); pg.select_option('select[data-dp=%s][data-part=y]' % prefix, str(d.year)); wait(pg, 150)
    def panel(pn): pg.locator('[data-a=panel][data-p="%s"]' % pn).first.evaluate('e=>e.click()'); wait(pg, 400)
    def homespot(name):
        tap('go-home'); return pg.inner_text('main')
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')")
    pg.evaluate("localStorage.setItem('__mocksession', %s)" % json.dumps(SESSION)); pg.goto('https://sorted.test/'); wait(pg, 700)

    # ================= 1. one next action after a promise closes =================
    c1 = start('Currys said they would refund my £89 by Friday, order 445566')
    overdue(c1); opencase(c1); pg.click('.promise [data-a=kept]'); wait(pg, 600)
    ok('Has all of it arrived?' in main() and 'has all of it arrived?' in now().lower() and 'get the call ready' not in now().lower(), 'refund, It arrived: the Now line asks what the card asks: %r' % now())
    u = pg.inner_text('details.case117-u') if pg.locator('details.case117-u').count() else ''
    ok('get the call ready' not in u.lower(), 'What Sorted understood doesn’t say “get the call ready”')
    h = homespot('Currys'); ok('has all of it arrived?' in h.lower() and 'get the call ready' not in h.lower(), 'Home says the same')
    # 13. Only part of it: recorded as partly, no company total
    outs = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__outcomes')||'[]')")
    pid = case(c1)['promises'][-1]['id']
    ok(any(x.get('p_promise') == pid for x in outs()), 'It arrived recorded a company total (before)')
    opencase(c1); pg.locator('[data-a=pb-go][data-v=part]').click(); wait(pg, 600)
    lp = case(c1)['promises'][-1]
    ok(lp['status'] == 'missed' and lp.get('partly') and case(c1)['pb']['stage'] == 'part', '“Only part of it” marks the promise partly: %s %s' % (lp['status'], lp.get('partly')))
    ok(not any(x.get('p_promise') == pid for x in outs()), 'and drops its company total, as the Only partly route never records one')
    ok('chase the rest' in now().lower(), 'the Now line follows the stage: %r' % now())

    c2 = start('British Gas said an engineer will come on Thursday between 8am and 12pm, job 77123')
    overdue(c2); opencase(c2); pg.click('.promise [data-a=kept]'); wait(pg, 600)
    ok('Did the visit fix it?' in main() and 'did the visit fix it?' in now().lower(), 'repair, They came: the Now line asks whether the visit fixed it: %r' % now())

    c3 = start('Evri said they would deliver my parcel on Thursday, ref EV123456')
    opencase(c3); pg.click('[data-a=p-cancel]'); wait(pg, 500)
    ok(pg.locator('form[data-f=done]').count() == 1, 'They cancelled it opens the finish form')
    pg.click('form[data-f=done] [data-a=panel][data-p=""]'); wait(pg, 500)
    ok(pg.locator('form[data-f=call]').count() == 0 and pg.locator('.settled141').count() == 1 and 'Is this case finished?' in main(), 'Not yet: no empty call form, the case asks whether it is finished')
    ok('finish this case' in now().lower(), 'and the Now line says so: %r' % now())
    pg.click('.settled141 [data-a=panel][data-p=done]'); wait(pg, 300)
    ok(pg.locator('form[data-f=done]').count() == 1, 'Finish this case opens the finish form')

    c4 = start('Penalty Charge Notice WK12345678 from Camden Council for £130, vehicle AB12 CDE, contravention on 1 October 2026')
    h = homespot('Camden')
    ok('check the notice details' in h.lower() and 'get the call ready' not in h.lower(), 'a typed parking notice: Home says check the notice details')

    # ================= 8. the deadline on a demand =================
    c5 = start('Letter from HMRC says I owe £340 and must pay by 31 October, ref 123/AB45678')
    dl = case(c5).get('deadline') or {}
    ok(dl.get('date', '')[5:] == '10-31', 'the deadline is kept on the case as a date: %s' % dl)
    ok('31 October' in now() and 'get the call ready' not in now().lower(), 'the Now line names the deadline: %r' % now())
    h = homespot('HMRC'); ok('before Saturday 31 October' in h or 'before ' + fday(datetime.date(today.year if today <= datetime.date(today.year, 10, 31) else today.year + 1, 10, 31)) in h, 'Home names it too')
    opencase(c5)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    opencase(c5)
    ok(pg.locator('.dl141 [data-a=fr-remind]').count() == 1, 'after leaving, the reminder before the deadline is still offered')
    pg.click('.dl141 [data-a=fr-remind]'); wait(pg, 400)
    ok(pg.locator('#moveform').count() == 1 and pg.input_value('#f-mdate')[5:] == '10-31', 'it opens your own step at the deadline')
    pg.click('#moveform button[type=submit]'); wait(pg, 500)
    ok((case(c5).get('deadline') or {}).get('ans') == 'remind' and pg.locator('.dl141').count() == 0, 'once saved, it isn’t offered again')
    c5b = start('Letter from the council says I owe £120 council tax arrears and must pay by 30 November')
    opencase(c5b)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    opencase(c5b)
    if pg.locator('.dl141 [data-a=dl-skip]').count(): pg.click('.dl141 [data-a=dl-skip]'); wait(pg, 400)
    ok((case(c5b).get('deadline') or {}).get('ans') == 'no' and pg.locator('.dl141').count() == 0 and any('No reminder for your deadline' in l for l in labels(c5b)), '“No reminder” answers it, and the deadline stays on the case')

    # ================= 2, 4. a window: title follows, edits keep it a window =================
    c6 = start('Aviva said they would call me back sometime next week, claim AV12345')
    p6 = openp(c6)[0]; t6 = case(c6)['title']
    ok(p6.get('win') and re.match(r'^Aviva · by \w+day \d+ \w+$', t6), 'the window promise and its title: %r' % t6)
    opencase(c6); pg.click('[data-a=rebook]'); wait(pg, 400)
    ok(pg.locator('[data-a=d][data-k=when][data-v=by][aria-pressed=true]').count() == 1, '“They’ve given a firm date” on a window asks for “By a day”, not a time')
    nd = today + datetime.timedelta(days=12)
    pickdate('f-date', nd); pg.click('form[data-f=promise] button[type=submit]'); wait(pg, 600)
    t6b = case(c6)['title']
    ok(t6b == 'Aviva · ' + fday(nd), 'the title follows the new date: %r' % t6b)
    nd2 = today + datetime.timedelta(days=15)
    opencase(c6); panel('correct')
    pg.fill('#f-correct', 'They moved it to %d %s' % (nd2.day, nd2.strftime('%B'))); pg.click('form[data-f=correct] button[type=submit]'); wait(pg, 500)
    ok('from what you typed' in main().lower() and 'from the message you added' not in main().lower(), 'Correct a detail says the words came from what you typed')
    pg.click('[data-a=corr-moved]'); wait(pg, 500)
    ok(case(c6)['title'] == 'Aviva · ' + fday(nd2), 'Correct a detail moves the title with the date: %r' % case(c6)['title'])
    # a renamed case keeps its own name
    c6r = start('Aviva said they would call me back sometime next week, claim AV99999')
    opencase(c6r); panel('rename')
    pg.fill('#f-rename', 'Home insurance claim'); pg.click('form[data-f=rename] button[type=submit]'); wait(pg, 400)
    opencase(c6r); pg.click('[data-a=rebook]'); wait(pg, 400); pickdate('f-date', nd); pg.click('form[data-f=promise] button[type=submit]'); wait(pg, 600)
    ok(case(c6r)['title'] == 'Home insurance claim', 'a name you chose is never replaced')
    # editing the proposal without touching the date keeps the window
    c7 = start('Aviva said they would call me back sometime next week, claim AV55555', keep=False)
    opencase(c7); pg.click('[data-a=sug-edit]'); wait(pg, 400)
    ok(pg.locator('[data-a=d][data-k=when][data-v=by][aria-pressed=true]').count() == 1 and pg.locator('#f-from').count() == 0, 'Change the details on a window starts at “By a day” on its last day')
    pg.click('form[data-f=promise] button[type=submit]'); wait(pg, 600)
    p7 = openp(c7)[0]
    ok(p7.get('win') and p7.get('prec') == 'window' and p7.get('dueEnd') and lday(p7['dueAt']) < lday(p7['dueEnd']), 'saved unchanged, it is still the window: %s' % {k: p7.get(k) for k in ('win', 'prec', 'dueAt', 'dueEnd')})
    # 6. a window asks the morning after it ends, nothing before it starts
    r7 = rems(c7)
    ok(r7 and all(k == 'after' for k, _ in r7) and lday(r7[0][1]) == lday(p7['dueEnd']) + datetime.timedelta(days=1) and r7[0][1][11:13] in ('08', '09'), 'a window: one “after” reminder, 9am the morning after it ends: %s' % r7)

    # ================= 3. a changed date takes the old date out of their words =================
    c8 = start('Currys said they would refund my £89 by Friday, order 445566')
    p8 = openp(c8)[0]; d8 = lday(p8['dueAt'])
    r8 = rems(c8)
    ok(('before', ) and any(k == 'before' for k, _ in r8) and any(k == 'after' and lday(s) == d8 + datetime.timedelta(days=1) for k, s in r8), 'a by-day deadline: 9am on the day and an “after” the morning after: %s' % r8)
    sun = today + datetime.timedelta(days=(6 - today.weekday()) % 7 or 7) + datetime.timedelta(days=7)
    opencase(c8); pg.click('[data-a=rebook]'); wait(pg, 400)
    pickdate('f-date', sun); pg.click('form[data-f=promise] button[type=submit]'); wait(pg, 600)
    np8 = openp(c8)[0]
    ok('Friday' not in np8['said'] and '£89' in np8['said'] and '445566' in np8['said'], 'their words lose the old date: %r' % np8['said'])
    nl8 = [l for l in labels(c8) if l.startswith('They said:')][-1]
    ok('Friday' not in nl8 and nl8.count('445566') == 1, 'the history line for the new date has one date and one reference: %r' % nl8)
    q = pg.inner_text('.promise-quote') if pg.locator('.promise-quote').count() else ''
    ok('Friday' not in q, 'the promise card quotes no old date: %r' % q)
    # 5. "It was always Thursday" keeps a by-day deadline
    c9 = start('Currys said they would refund my £40 by Friday, order 778899')
    opencase(c9); panel('correct')
    pg.fill('#f-correct', 'Sorry, I meant Thursday not Friday'); pg.click('form[data-f=correct] button[type=submit]'); wait(pg, 500)
    pg.click('[data-a=corr-yes]'); wait(pg, 600)
    p9 = openp(c9)[0]
    ok(p9.get('by') and lday(p9['dueAt']).weekday() == 3 and 'any time' not in main(), 'It was always Thursday stays “by Thursday”: by=%s %s' % (p9.get('by'), p9['dueAt']))
    r9 = rems(c9)
    ok(r9 and not [s for k, s in r9 if k == 'before' and s[11:13] in ('17', '18')], 'and no 6pm-the-evening-before reminder: %s' % r9)
    # your own step: Change date drops the old day from its words
    c10 = start('I need to send Aviva the photos of the damage')
    opencase(c10); pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
    if pg.locator('[data-a=turn-yours]').count(): pg.locator('[data-a=turn-yours]').first.click(); wait(pg, 400)
    if pg.locator('#f-mwhat').count() == 0: panel('move')
    pg.fill('#f-mwhat', 'Send them the photos by Thursday'); pg.click('[data-a=use-msug]') if pg.locator('[data-a=use-msug]').count() else None; wait(pg, 300)
    pg.click('#moveform button[type=submit]'); wait(pg, 500)
    opencase(c10); pg.click('[data-a=move-rebook]'); wait(pg, 400)
    mon = today + datetime.timedelta(days=(0 - today.weekday()) % 7 or 7) + datetime.timedelta(days=7)
    pickdate('f-mdate', mon); pg.click('#moveform button[type=submit]'); wait(pg, 500)
    mv = [m for m in case(c10)['moves'] if m['status'] == 'open'][0]
    ok('Thursday' not in mv['what'] and 'photos' in mv['what'], 'your own step loses the old day: %r' % mv['what'])
    # 14. the pickers start this year
    opencase(c10); pg.click('[data-a=move-rebook]'); wait(pg, 300)
    ys = pg.locator('select[data-dp=f-mdate][data-part=y] option').evaluate_all("o=>o.map(x=>x.value).filter(Boolean)")
    ok(ys and int(ys[0]) == today.year, 'the step’s year picker starts this year: %s' % ys)

    # ================= 7, 9. finishing =================
    c11 = start('Amazon said they would refund my £25 by Friday, ref AMZ11111')
    opencase(c11); panel('done')
    pg.fill('#f-outcome', 'Gave up'); pg.click('form[data-f=done] button[type=submit]'); wait(pg, 500)
    c11d = case(c11)
    ok(not [q for q in c11d['promises'] if q['status'] == 'open'] and any(l.startswith('Closed when you finished the case') for l in labels(c11)), 'finishing closes the open promise, with a history line')
    ok(not rems(c11), 'and its unsent reminders go')
    tap('go-home'); w = pg.inner_text('.wins') if pg.locator('.wins').count() else ''
    ok('£25' not in w, 'a money case finished “Gave up” isn’t counted as a refund: %r' % w)
    c12 = start('Argos said they would refund my £30 by Friday, ref ARG22222')
    overdue(c12); opencase(c12); pg.click('.promise [data-a=kept]'); wait(pg, 500)
    if pg.locator('[data-a=pb-go][data-v=refunded]').count(): pg.click('[data-a=pb-go][data-v=refunded]'); wait(pg, 400)
    pg.click('form[data-f=done] button[type=submit]'); wait(pg, 500)
    tap('go-home'); w = pg.inner_text('.wins') if pg.locator('.wins').count() else ''
    ok('£30' in w, 'a refund that arrived is counted: %r' % w)
    opencase(c11); pg.locator('[data-a=case-reopen]').first.click(); wait(pg, 600)
    ok(openp(c11) and any(l.startswith('Reopened.') and 'Open again' in l for l in labels(c11)), 'Reopen brings back what was open when it finished')
    ok(rems(c11), 'and sets its reminders again')

    # ================= 10. renewals =================
    tap('new-case'); pg.locator('[data-cap82=renew]').first.evaluate('e=>e.click()'); wait(pg, 400)
    exp = today + datetime.timedelta(days=200)
    pg.click('label.gi-chip:has-text("Passport")'); pg.fill('#gi-when', '%d %s %d' % (exp.day, exp.strftime('%B'), exp.year))
    pg.click('form[data-f=gi] button[type=submit]'); wait(pg, 700)
    sb = exp - datetime.timedelta(days=90)
    ok(pg.locator('.sb141 [data-a=move-sb]').count() == 1 and fday(sb) in pg.inner_text('.sb141'), 'the renewal offers starting earlier, by %s' % fday(sb))
    pg.click('.sb141 [data-a=move-sb]'); wait(pg, 300)
    ok(pg.input_value('#f-mdate') == sb.isoformat() and 'Renew my passport' in pg.input_value('#f-mwhat'), 'one tap uses it, keeping the words')
    pg.click('#moveform button[type=submit]'); wait(pg, 500)
    cr = cases()[-1]
    tap('go-home'); spot = pg.inner_text('.home44-spot') if pg.locator('.home44-spot').count() else ''
    ok('Renew my passport' not in spot, 'a step months away isn’t “Next up” on Home: %r' % spot[:120])

    # ================= 11. That's not a promise =================
    c13 = start('Currys said they would refund my £89 by Friday', keep=False)
    opencase(c13); pg.click('[data-a=sug-no]'); wait(pg, 500)
    fr = pg.inner_text('.fr-card') if pg.locator('.fr-card').count() else ''
    ok('haven’t given you a date' not in fr and 'isn’t a promise' in fr, 'the first response doesn’t say they gave no date: %r' % fr[:300])

    # ================= 15. Nothing agreed yet =================
    c14 = start('Evri said they would deliver my parcel on Thursday, ref EV654321')
    opencase(c14); pg.click('[data-a=p-cancel]'); wait(pg, 400); pg.click('form[data-f=done] [data-a=panel][data-p=""]'); wait(pg, 400)
    pg.locator('.settled141 [data-a=panel][data-p=call]').click(); wait(pg, 400)
    pg.locator('form[data-f=call] button[type=submit]').first.click(); wait(pg, 500)
    pg.click('[data-a=no-promise]'); wait(pg, 500)
    ok(pg.locator('#moveform').count() == 1 and 'Chase Evri' in pg.input_value('#f-mwhat') and pg.input_value('#f-mdate'), '“Nothing agreed yet” offers a follow-up reminder, dated')
    pg.click('#moveform button[type=submit]'); wait(pg, 500)
    mv14 = [m for m in case(c14)['moves'] if m['status'] == 'open']
    ok(mv14 and mv14[0].get('chosen'), 'saved as your own follow-up, never their promise')

    # ================= 16. the ledger =================
    c15 = start('Currys said they would refund my £15 by Friday, order 990011')
    opencase(c15); pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); lg = pg.inner_text('.lg124') if pg.locator('.lg124').count() else ''
    ok(lg and 'Changed or turned down' not in lg and 'replaced' not in lg, 'a just-confirmed proposal isn’t shown as a replaced promise: %r' % lg[-300:])
    rows = [r for r in case(c15).get('ledger', []) if r['type'] == 'promise' and r['sub'] == 'proposal']
    ok(rows and rows[0]['st'] == 'superseded' and rows[0].get('cnf'), 'the proposal row stays in the record, marked as confirmed into the promise')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
