# v137 (the review of 5 October 2026). An open case leads with one "Now" card: what happened, who acts next, and
# "Add what they just said" (plus "Something changed" and "Can’t do this now"), with the one main button straight after
# it. An old reminder (email or notification) for a promise that has moved on changes nothing and says what happened.
# The public page has "Try an example": four steps of a refund that hasn’t arrived, without signing in, saving nothing.
# "Send this summary" previews the issue, what was promised, what happened, the reference and what you are asking for
# now (yours to change), then copies it. A helper link can carry "What I’m asking them to do"; the helper sees it first,
# replies with their name, and the owner keeps or removes the reply. A guest is told what losing the phone means.
import os, sys, datetime
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
nxt = fri + datetime.timedelta(days=7)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.grant_permissions(['clipboard-read', 'clipboard-write'], origin='https://sorted.test')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
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
        if pg.locator('[data-a=nudge-skip]').count(): pg.click('[data-a=nudge-skip]'); wait(pg, 300)
        return cases()[-1]['id']
    def opencase(cid):
        pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700)
    def openfolds(): pg.evaluate("document.querySelectorAll('details.case75-group,details.case56-fold').forEach(d=>d.open=true)"); wait(pg, 200)
    # ================= 3. Try an example, signed out =================
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.goto('https://sorted.test/'); wait(pg, 600)
    ok(pg.locator('.hero126 [data-a=see-example]').inner_text().strip() == 'Try an example', 'the landing page offers “Try an example”')
    pg.click('.hero126 [data-a=see-example]'); wait(pg, 300)
    ex = lambda: pg.inner_text('#example126')
    ok('Step 1 of 4' in ex() and 'Nothing here is saved or sent' in ex() and 'Currys said my £89 refund would arrive by Friday. Order 445566.' in ex() and '445566' in pg.inner_text('#example126 dl'), 'step 1: what you type, and what Sorted picks out')
    pg.click('#example126 [data-a=demo][data-v="1"]'); wait(pg, 200)
    ok('Step 2 of 4' in ex() and 'Has the money arrived?' in ex() and 'Friday has passed' in ex(), 'step 2: Friday passes and Sorted asks one question')
    ok(pg.evaluate("document.activeElement&&document.activeElement.id") == 'demo137-step', 'focus moves to the step, for a screen reader')
    pg.click('#example126 [data-a=demo][data-v=arrived]'); wait(pg, 200)
    ok('moves to Done' in ex(), 'It arrived: the case is done, with its record')
    pg.click('#example126 [data-a=demo][data-v="2"]'); wait(pg, 200)
    ok('Step 3 of 4' in ex() and 'Not arrived. Recorded by you.' in ex(), 'step 3: you record that it hasn’t arrived, in the history')
    pg.click('#example126 [data-a=demo][data-v="3"]'); wait(pg, 200)
    msg = pg.inner_text('.demo137-msg')
    ok('Step 4 of 4' in ex() and 'order 445566' in msg and 'by Friday' in msg and 'send it yourself' in ex(), 'step 4: the follow-up quotes what they said and the order number, and you send it')
    ok(pg.locator('#example126 [data-cap82=other]').count() == 1 and pg.locator('#browse126').count() == 1, 'it ends with “Start with your own problem”, and the rest of the page is still there')
    ok(pg.evaluate("Object.keys(localStorage).filter(k=>k.startsWith('sorted.')).length") == 0 and not dbj().get('tasks'), 'nothing was saved, and no account was made')
    ok('—' not in ex(), 'no em dashes')
    pg.click('#example126 [data-a=demo][data-v="0"]'); wait(pg, 200)
    ok('Step 1 of 4' in ex(), '“Start the example again” goes back to the start')
    ok(pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth+1"), 'nothing scrolls sideways')
    # ================= sign in as a guest =================
    pg.goto('https://sorted.test/#start'); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    c1 = start('Currys said they would refund £89 by %s, order 445566' % fri.strftime('%A'))
    # ================= 4. the guest is told what a lost phone means =================
    pg.goto('https://sorted.test/'); wait(pg, 600)
    an = pg.inner_text('.anon129') if pg.locator('.anon129').count() else ''
    ok('Keep your cases if you lose this phone.' in an and 'only this phone can open them' in an and 'Add an email' in an, 'after the first case, a guest is told how to keep cases if the phone is lost')
    # ================= 1. the Now card =================
    opencase(c1)
    now = pg.inner_text('.now137') if pg.locator('.now137').count() else ''
    ok('What happened: Currys promised it by %s' % fri.strftime('%A') in now and 'Waiting for Currys: nothing for you to do until' in now, 'a waiting case: what happened, and who acts next')
    order = pg.evaluate("(()=>{var a=[...document.querySelectorAll('main *')],q=s=>a.indexOf(document.querySelector(s));return [q('.now137'),q('.promise'),q('#case56-timeline')]})()")
    ok(order[0] >= 0 and order[0] < order[1] and (order[2] < 0 or order[1] < order[2]), 'the Now card, then the action, then the history')
    ok(pg.locator('.now137 [data-a=panel][data-p=paste]').inner_text().strip() == 'Add what they just said', '“Add what they just said” is a visible button on the case')
    overdue(c1); opencase(c1)
    now = pg.inner_text('.now137')
    ok('That time has passed.' in now and 'Next: tell Sorted whether Currys did it' in now and pg.locator('.now137-hot').count() == 1, 'when their date has passed: what happened, and that it’s your turn')
    ok(pg.locator('.promise [data-a=kept]').count() == 1, 'the main answer button follows straight after')
    # ================= 4b. Add what they just said =================
    pid = [q for q in case(c1)['promises'] if q['status'] == 'open'][0]['id']; due0 = [q for q in case(c1)['promises'] if q['status'] == 'open'][0]['dueAt']
    pg.click('.now137 [data-a=panel][data-p=paste]'); wait(pg, 300)
    ok(pg.locator('#f-paste').count() == 1, 'it opens the box for their message, with a screenshot button')
    pg.fill('#f-paste', 'Hi, sorry for the delay. Your refund of £89 will now be paid by %s. Order 445566. Currys' % nxt.strftime('%A %d %B'))
    pg.click('form[data-f=paste] button[type=submit]'); wait(pg, 600)
    q0 = [q for q in case(c1)['promises'] if q['id'] == pid][0]
    ok(q0['status'] == 'open' and q0['dueAt'] == due0, 'reading it changes nothing by itself')
    ok(pg.locator('.sug, [data-a=corr-moved], [data-a=corr-yes], [data-a=sug-yes]').count() >= 1, 'it proposes the change for you to confirm')
    # ================= 2. an old reminder =================
    opencase(c1)
    if pg.locator('[data-a=sug-no]').count(): pg.click('[data-a=sug-no]'); wait(pg, 300)
    if pg.locator('[data-a=corr-no]').count(): pg.click('[data-a=corr-no]'); wait(pg, 300)
    pg.locator('.promise [data-a=kept]').click(); wait(pg, 600)
    ok([q for q in case(c1)['promises'] if q['id'] == pid][0]['status'] == 'kept', '(it arrived, recorded on the case)')
    nev = len(case(c1)['events'])
    pg.goto('https://sorted.test/?task=%s&src=push&ans=later&p=%s' % (c1, pid)); wait(pg, 900)
    st = pg.inner_text('.stale137') if pg.locator('.stale137').count() else ''
    ok('That reminder is out of date.' in st and 'you recorded that Currys did it' in st and 'Nothing has been changed' in st, 'an old notification says what happened since and changes nothing')
    ok(pg.locator('.q130-later, [data-a=q-snooze]').count() == 0 and not case(c1).get('snooze'), 'it doesn’t open “Later” for a promise already answered')
    ok([q for q in case(c1)['promises'] if q['id'] == pid][0]['status'] == 'kept', 'the answer stands')
    pg.goto('https://sorted.test/?task=%s&src=email&ans=no&p=%s' % (c1, pid)); wait(pg, 900)
    ok([q for q in case(c1)['promises'] if q['id'] == pid][0]['status'] == 'kept' and 'already answered' in pg.inner_text('#toast') and pg.locator('.stale137').count() == 1, '“No” from an old email changes nothing and says why')
    tap('go-home'); wait(pg, 300)
    opencase(c1)
    ok(pg.locator('.stale137').count() == 0, 'the note goes once you move on')
    # a moved date
    c2 = start('Amazon said they would refund £20 by %s, ref AMZ12345' % fri.strftime('%A'))
    p2 = [q for q in case(c2)['promises'] if q['status'] == 'open'][0]['id']
    opencase(c2); pg.click('.now137 [data-a=panel][data-p=changed]'); wait(pg, 300)
    pg.click('.q130-changed [data-a=panel][data-p=qdate]'); wait(pg, 300)
    pg.fill('form[data-f=qdate] [name=qdate]', nxt.isoformat()); pg.click('form[data-f=qdate] button[type=submit]'); wait(pg, 600)
    pg.goto('https://sorted.test/?task=%s&src=email&ans=date&p=%s' % (c2, p2)); wait(pg, 900)
    st = pg.inner_text('.stale137') if pg.locator('.stale137').count() else ''
    ok('the date changed' in st and nxt.strftime('%A') in st, 'a reminder for a date that has since moved says the new date')
    # ================= 5. Send this summary =================
    opencase(c2); openfolds()
    pg.click('[data-a=panel][data-p=summary137]'); wait(pg, 400)
    pre = pg.inner_text('#sum137-pre')
    ok(pre.startswith('Summary: ') and 'What was promised:' in pre and 'Amazon said:' in pre and 'What happened:' in pre and 'They changed the date.' in pre and 'Reference: AMZ12345' in pre and 'What I’m asking for now: Please confirm this is still on track for' in pre, 'the summary has the issue, the promises, what happened, the reference and the ask')
    ok('—' not in pre, 'no em dashes')
    ok(case(c2).get('events') == case(c2).get('events') and 'sumAsk' not in case(c2), 'opening it changes nothing on the case')
    pg.fill('#sum137-ask', 'Please pay the £20 this week.'); wait(pg, 200)
    ok('What I’m asking for now: Please pay the £20 this week.' in pg.inner_text('#sum137-pre'), 'what you are asking for is yours to change, and the preview follows')
    pg.click('[data-a=sum-copy]'); wait(pg, 300)
    clip = pg.evaluate('navigator.clipboard.readText()')
    ok(clip == pg.inner_text('#sum137-pre') and 'Summary copied' in pg.inner_text('#toast'), 'Copy copies exactly what was previewed')
    ok(pg.locator('#sum137-pre').evaluate("e=>e.scrollWidth<=e.clientWidth+1"), 'the preview wraps on a phone')
    # ================= 6. a helper request =================
    opencase(c2); openfolds()
    pg.click('details.case56-sharing [data-a=share]'); wait(pg, 700)
    tok = case(c2)['shareToken']; openfolds()
    pg.fill('#f-helpask', 'Could you call Amazon about this?'); pg.click('form[data-f=helpask] button[type=submit]'); wait(pg, 600)
    t2 = case(c2)
    ok(t2.get('helpAsk') == 'Could you call Amazon about this?' and t2.get('notesOn') is True and any(e['label'] == 'Asked your helper: “Could you call Amazon about this”.' for e in t2['events']), 'the request is saved, in the history, and lets them reply')
    sh = [x for x in dbj().get('shares', []) if x['token'] == tok][0]
    ok(sh['card'].get('q') == 'Could you call Amazon about this?' and sh.get('notes_on') is True, 'the helper link carries the request')
    hp = ctx.new_page(); hp.on('pageerror', lambda e: errs.append(str(e)))
    hp.goto('https://sorted.test/?share=' + tok); wait(hp, 800)
    ht = hp.inner_text('main').replace('WHAT THEY’RE ASKING YOU', 'What they’re asking you')
    ok('What they’re asking you' in ht and 'Could you call Amazon about this?' in ht and 'Reply to them' in ht, 'the helper sees what is asked of them first, and a reply form')
    ok(ht.index('What they’re asking you') < ht.index('Reply to them'), 'the request comes before everything else they can do')
    hp.fill('#f-hn', 'Mum'); hp.fill('#f-hb', 'I rang Amazon. They said the £20 goes back on Monday.'); hp.click('form[data-f=hnote] button[type=submit]'); wait(hp, 500)
    opencase(c2)
    nb = pg.inner_text('.notes-block') if pg.locator('.notes-block').count() else ''
    ok('You asked: “Could you call Amazon about this”' in nb and 'Mum' in nb and 'I rang Amazon' in nb, 'the reply comes back with their name, under what you asked')
    ok(not any(e['label'].startswith('Note from Mum') for e in case(c2)['events']), 'it isn’t in the case until you keep it')
    pg.click('[data-a=note-keep]'); wait(pg, 500)
    ok(any(e['label'].startswith('Note from Mum: “I rang Amazon') for e in case(c2)['events']), 'kept, it is attributed to them in the history')
    opencase(c2); openfolds()
    pg.fill('#f-helpask', ''); pg.click('form[data-f=helpask] button[type=submit]'); wait(pg, 600)
    ok('helpAsk' not in case(c2) and 'q' not in [x for x in dbj().get('shares', []) if x['token'] == tok][0]['card'], 'clearing the request takes it off the link')
    ok(pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth+1"), 'nothing scrolls sideways')
    ok(not errs, 'no page errors: %s' % errs)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
