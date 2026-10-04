# v130 (the quick actions note). When Sorted brings something back it can usually be dealt with in seconds, on Home:
# "N things need a quick answer"; one tap for the obvious answer (it arrived, then "Is this case finished now?"); "Not
# yet" goes straight to a ready chase message; "New date" asks only for the date, keeps the old one in the history and
# moves the case to Waiting; "Later" (Tonight, Tomorrow morning, This weekend, or a day) puts the case under Later until
# then, never moves a real deadline and says so, and any real update ends it. "Something changed" on every open case,
# with choices that fit a refund, a parking notice, a repair or anything else. A parking notice due within a week offers
# Pay (the official page), Review options and Later; back from paying, Sorted asks "Did you finish paying…?", and Yes
# records it with an optional confirmation number that is never a card number.
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
today = datetime.date.today()
fri = today + datetime.timedelta(days=(4 - today.weekday()) % 7 or 7)
uk = lambda k: (today + datetime.timedelta(days=k)).strftime('%d/%m/%Y')
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    ctx.route(lambda u: 'gov.uk' in u or 'tfl.gov.uk' in u, lambda r: r.fulfill(body='<title>Official page</title>', content_type='text/html'))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    case = lambda cid: [c for c in cases() if c['id'] == cid][0]
    main = lambda: pg.inner_text('main')
    tap = lambda a: (pg.locator('.tab129 [data-a=%s]' % a).click(), wait(pg, 500))
    def poke(js):
        pg.goto('https://sorted.test/'); wait(pg, 600)
        pg.evaluate("(js)=>{var db=JSON.parse(localStorage.getItem('__mockdb'));(new Function('db',js))(db);localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", js)
        pg.goto('https://sorted.test/'); wait(pg, 700)
    def overdue(cid): poke("db.tasks.forEach(function(r){if(r.data.id==='%s')r.data.promises.forEach(function(q){if(q.status==='open'){q.dueAt=new Date(Date.now()-2*864e5).toISOString();q.dueEnd=null;q.allDay=true;q.by=true}})})" % cid)
    def start(text):
        tap('new-case')
        pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
        if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
        return cases()[-1]['id']
    def q(name, a):
        return pg.locator('.home44-spot:has-text("%s"), .q130-item:has-text("%s")' % (name, name)).locator('[data-a=%s]' % a).first
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')")
    pg.goto('https://sorted.test/#start'); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    c1 = start('Currys said they would refund £89 by %s, order 445566' % fri.strftime('%A'))
    c2 = start('Amazon said they would refund £20 by %s, ref AMZ12345' % fri.strftime('%A'))
    c3 = start('Evri said they would sort out my lost parcel by %s, ref EV123456' % fri.strftime('%A'))
    for c in (c1, c2, c3): overdue(c)
    # ---- Home leads with the quick answers ----
    m = main()
    ok('3 things need a quick answer.' in m, 'Home says how many things need a quick answer')
    ok(all(q(nm, 'q-later').count() == 1 and q(nm, 'q-date').count() == 1 for nm in ('Currys', 'Amazon', 'Evri')), 'each one can be answered where it is: an answer, Not yet, New date, Later')
    ok('Did the money arrive?' in m or 'Has the money arrived?' in m, 'a refund asks whether the money arrived')
    # ---- one tap: it arrived ----
    q('Currys', 'q-kept').click(); wait(pg, 500)
    ok(pg.locator('main.home44').count() == 1 and [x for x in case(c1)['promises'] if x['status'] == 'kept'], 'It arrived is recorded on Home, without opening the case')
    ok(pg.locator('.q130-done').count() == 1 and 'Has all of it arrived?' in pg.inner_text('.q130-done'), 'and Sorted asks once whether it all arrived, which finishes the case')
    pg.click('[data-a=q-finish]'); wait(pg, 500)
    ok(case(c1)['board'] == 'done' and 'They kept it' in (case(c1).get('outcome') or ''), 'Yes, it’s sorted finishes the case')
    ok('2 things need a quick answer.' in main(), 'and the count goes down')
    # ---- ten seconds: a new date asks only for the date ----
    old = [x for x in case(c2)['promises'] if x['status'] == 'open'][0]
    q('Amazon', 'q-date').click(); wait(pg, 400)
    f = pg.locator('form[data-f=qdate]')
    ok(f.count() == 1 and f.locator('input:not([type=hidden])').count() == 1 and 'What’s the new date?' in f.inner_text(), 'New date asks one question: the date, nothing Sorted already knows')
    ok(pg.evaluate("document.activeElement&&document.activeElement.name==='qdate'"), 'with focus in the date')
    nd = today + datetime.timedelta(days=9)
    pg.fill('form[data-f=qdate] input[name=qdate]', nd.isoformat()); pg.click('form[data-f=qdate] button[type=submit]'); wait(pg, 500)
    ps = case(c2)['promises']; op = [x for x in ps if x['status'] == 'open']
    ok(pg.locator('main.home44').count() == 1 and len(op) == 1 and op[0]['id'] != old['id'] and op[0]['party'] == old['party'] and op[0]['ref'] == old['ref'] and [x for x in ps if x['id'] == old['id']][0]['status'] == 'replaced', 'the new date replaces the old promise, keeping who and the reference')
    ok(datetime.datetime.fromisoformat(op[0]['dueAt'].replace('Z', '+00:00')).astimezone().date() == nd, 'on the day chosen')
    ok(any('They changed the date' in e['label'] for e in case(c2)['events']), 'the old date stays in the history')
    ok('Waiting' in main() and 'Amazon' in pg.inner_text('.home44-section.waiting'), 'and the case waits again until then')
    # ---- Not yet: straight to a ready chase message ----
    q('Evri', 'home-ans').click(); wait(pg, 600)
    ok(pg.locator('main.case56').count() == 1 and pg.locator('form[data-f=call]').count() >= 1 and [x for x in case(c3)['promises'] if x['status'] == 'missed'], 'Not yet records the miss and opens the chase')
    ok('EV123456' in (pg.locator('form[data-f=call] textarea').first.input_value() if pg.locator('form[data-f=call] textarea').count() else main()), 'and the message already carries the reference')
    # ---- Later: an attention promise, kept apart from the real deadline ----
    c4 = start('Sky said they would call me back by %s, ref SKY778899' % fri.strftime('%A')); overdue(c4)
    q('Sky', 'q-later').click(); wait(pg, 400)
    sh = pg.locator('.q130-later')
    ok(sh.count() == 1 and 'Tomorrow morning' in sh.inner_text() and pg.locator('form[data-f=qlater] input[type=date]').count() == 1, 'Later offers Tomorrow morning (and Tonight or This weekend when they make sense) or a day')
    sh.locator('[data-a=q-snooze][data-v=tomorrow]').click(); wait(pg, 500)
    sn = case(c4).get('snooze')
    ok(sn and datetime.datetime.fromisoformat(sn['until'].replace('Z', '+00:00')).astimezone().date() == today + datetime.timedelta(days=1), 'the case is put off until tomorrow morning')
    ok(pg.locator('.home44-spot:has-text("Sky")').count() == 0 and pg.locator('.home44-section.later:has-text("Sky")').count() == 1 and 'Back tomorrow morning' in pg.inner_text('.home44-section.later'), 'it leaves the top of Home and waits under Later, saying when it comes back')
    ok([x for x in case(c4)['promises'] if x['status'] == 'open'], 'nothing about the promise changed')
    pg.goto('https://sorted.test/?task=%s' % c4); wait(pg, 600)
    ok('You chose to see this again tomorrow morning' in main(), 'the case says when you chose to see it again')
    pg.click('[data-a=q-unsnooze]'); wait(pg, 400)
    ok(not case(c4).get('snooze'), 'Bring it back now ends it')
    pg.click('.q130-line [data-a=panel][data-p=later]'); wait(pg, 400); pg.click('[data-a=q-snooze][data-v=tomorrow]'); wait(pg, 400)
    poke("db.tasks.forEach(function(r){if(r.data.id==='%s')r.data.snooze.until=new Date(Date.now()-6e4).toISOString()})" % c4)
    ok(pg.locator('.home44-spot:has-text("Sky"), .q130-item:has-text("Sky")').count() == 1, 'when the time comes it is back with a quick answer')
    pg.goto('https://sorted.test/?task=%s' % c4); wait(pg, 600); pg.click('.q130-line [data-a=panel][data-p=later]'); wait(pg, 300); pg.click('[data-a=q-snooze][data-v=tomorrow]'); wait(pg, 300)
    pg.click('.q130-line [data-a=panel][data-p=changed]'); wait(pg, 300); pg.click('[data-a=sc-contacted]'); wait(pg, 400)
    ok(not case(c4).get('snooze') and any(e['label'].startswith('You contacted Sky') for e in case(c4)['events']), 'a real update ends the Later')
    # ---- Something changed: choices that fit the case ----
    pg.goto('https://sorted.test/?task=%s' % c2); wait(pg, 600); pg.click('.q130-line [data-a=panel][data-p=changed]'); wait(pg, 400)
    t = pg.inner_text('.q130-changed')
    ok(all(x in t for x in ['The money arrived', 'They gave me a new date', 'The amount changed', 'I contacted them', 'They contacted me', 'I don’t need this any more', 'Something else']), 'a refund: money arrived, new date, amount, contacted, they contacted me, not needed, something else')
    pg.click('.q130-changed button:has-text("They gave me a new date")'); wait(pg, 400)
    ok(pg.locator('form[data-f=qdate]').count() == 1 and pg.locator('form[data-f=qdate] input:not([type=hidden])').count() == 1, 'from the case too, a new date is one question')
    pg.click('form[data-f=qdate] [data-a=q-close]'); wait(pg, 300)
    pg.click('.q130-line [data-a=panel][data-p=changed]'); wait(pg, 300); pg.click('.q130-changed button:has-text("Something else")'); wait(pg, 300)
    ok('What’s changed?' in main() and pg.locator('form[data-f=paste]').count() == 1, 'Something else asks in your own words')
    c5 = start('British Gas said the engineer will come on %s, ref BG-4455' % fri.strftime('%A'))
    pg.goto('https://sorted.test/?task=%s' % c5); wait(pg, 600); pg.click('.q130-line [data-a=panel][data-p=changed]'); wait(pg, 300)
    t = pg.inner_text('.q130-changed')
    ok(all(x in t for x in ['It’s fixed', 'The appointment changed', 'They didn’t turn up', 'Someone else is handling it', 'The problem got worse']), 'a repair: fixed, appointment changed, no-show, someone else, got worse')
    # ---- a parking notice: Pay, Review options, Later; the deadline stays the deadline ----
    pg.goto('https://sorted.test/'); wait(pg, 600); tap('new-case'); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.fill('#f-case', 'PCN'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 500)
    pg.evaluate("(()=>{var b=document.createElement('button');b.setAttribute('data-a','doc-manual');document.querySelector('main').appendChild(b);b.click()})()"); wait(pg, 500)
    pg.fill('#doc-issuer', 'Southwark Council'); pg.fill('#doc-ref', 'SK12345678'); pg.fill('#doc-vrm', 'AB12 CDE'); pg.fill('#doc-when', uk(-8)); pg.fill('#doc-amount', '130'); pg.fill('#doc-discount', '65')
    pg.click('form[data-f=doc] button[type=submit]'); wait(pg, 700)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 600)
    c6 = cases()[-1]['id']
    ok(case(c6).get('cf'), 'the notice is a case (%s)' % main()[:200].replace('\n', ' '))
    pg.goto('https://sorted.test/'); wait(pg, 700)
    pay = q('Southwark', 'q-pay')
    ok(pay.count() == 1 and pay.get_attribute('target') == '_blank' and 'gov.uk' in pay.get_attribute('href') and q('Southwark', 'open').count() == 1 and q('Southwark', 'q-later').count() == 1, 'a parking notice due this week: Pay on the official page, Review options, Later')
    q('Southwark', 'q-later').click(); wait(pg, 400)
    lt = pg.inner_text('.q130-later')
    ok('The real deadline is still' in lt and 'Sorted won’t move it' in lt, 'Later says the real deadline is still the deadline')
    pg.click('.q130-later [data-a=q-close]'); wait(pg, 300)
    with ctx.expect_page() as pi: q('Southwark', 'q-pay').click()
    pi.value.close(); pg.bring_to_front(); pg.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); wait(pg, 900)
    ok(pg.locator('.q130-pay').count() == 1 and 'Did you finish paying the' in pg.inner_text('.q130-pay') and '65' in pg.inner_text('.q130-pay'), 'back from paying, Sorted asks whether you finished paying')
    pg.click('.q130-pay [data-a=q-notpaid]'); wait(pg, 400)
    ok(pg.locator('.q130-pay').count() == 0 and case(c6)['board'] != 'done', 'No, not yet changes nothing')
    with ctx.expect_page() as pi: q('Southwark', 'q-pay').click()
    pi.value.close(); pg.goto('https://sorted.test/'); wait(pg, 700)
    pg.click('.q130-pay [data-a=q-paid]'); wait(pg, 500)
    ok(pg.locator('form[data-f=pkpaid]').count() == 1 and '65' in pg.input_value('#f-pkamt'), 'Yes, paid opens the payment record with the amount filled in')
    pg.fill('#f-pkconf', '4111 1111 1111 1111'); pg.click('form[data-f=pkpaid] button[type=submit]'); wait(pg, 400)
    ok('card number' in main() and case(c6)['board'] != 'done', 'a card number is refused, never kept')
    pg.fill('#f-pkconf', 'PAY-77881'); pg.click('form[data-f=pkpaid] button[type=submit]'); wait(pg, 500)
    cc = case(c6)
    ok(cc['board'] == 'done' and cc['outcome'].startswith('Paid £65') and any('confirmation PAY-77881' in e['label'] for e in cc['events']) and '4111' not in json.dumps(cc), 'the payment is recorded with its confirmation number and the case is finished')
    # ---- fits: 320px, 200% text ----
    c7 = start('Virgin said they would refund £40 by %s, ref VM445566' % fri.strftime('%A')); overdue(c7)
    pg.set_viewport_size({'width': 320, 'height': 640}); pg.evaluate("document.documentElement.style.fontSize='200%'"); wait(pg, 300)
    ok(pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth+1") and pg.locator('.q130-acts .btn').evaluate_all("es=>es.every(e=>e.getBoundingClientRect().height>=44)"), 'at 320px and 200% text nothing scrolls sideways and every quick answer is at least 44px')
    ok(not errs, 'no page errors: %s' % errs)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
