# v143 (audit pass 2: PASS2-006, 021, 022, 024, 033, 034). Unfinished work and the deadline journeys.
# 006: a deadline on the person ("HMRC … I need to pay £400 by <date>") with four other cases open, with the clock at the
#   deadline minus 4 days, on the day and 2 days after: it ranks with a pill before, leads Needs you on the day and after
#   ("Your deadline is today", "Your deadline passed on …"), and Home, Cases, the Now card, the health line and the case
#   never say "nothing due" or "what does the letter ask you to do?" while it stands.
# 021: words in every case panel survive a refresh and are offered back; "← Choose something else" and "your own words"
#   keep the typed who and what in the box; a notice under review, with a corrected value, survives Cases, New, More,
#   Back and a refresh ("Carry on checking your notice"); after "These are right" the confirmed details are kept until
#   the case starts; the summary ask, the adviser pack questions and the Moving home form survive leaving them; sign-out
#   leaves none of it on the phone.
# 022: step 2 offers "Wait until <date>" first; "they are looking into it" leads with whose move it is and, once it's
#   theirs, waiting with a follow-up, never an open call form; the Now card carries its button above the fold on
#   390x844; a money promise that will "come through" asks about money; quick answers under Also open carry their question.
# 024: the "All clear" headline isn't squeezed into a 56px column at 320, 390 or 768px.
# 033/034: Help names "Manage this case" (the bar's More is Account); a guest sees one email prompt at a time; "N things
#   need a quick answer" counts what is shown; a recovered draft is offered near the top of Home; the next action doesn't
#   repeat its date.
import os, sys, json, re, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); O = HERE + '/tests/node_modules/'; errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
today = datetime.date.today()
DL = today + datetime.timedelta(days=10)            # the deadline on the person
def dlong(d): return '%s %d %s' % (d.strftime('%A'), d.day, d.strftime('%B'))
H = {'Access-Control-Allow-Origin': '*'}
def cdn(r):
    u = r.request.url
    if '/npm/tesseract.js@5.1.1/dist/' in u: return r.fulfill(path=O + 'tesseract.js/dist/' + u.split('/dist/')[1], content_type='application/javascript', headers=H)
    if '/npm/tesseract.js-core@5.1.1/' in u: f = u.split('@5.1.1/')[1]; return r.fulfill(path=O + 'tesseract.js-core/' + f, content_type='application/wasm' if f.endswith('.wasm') else 'application/javascript', headers=H)
    if '/npm/@tesseract.js-data/eng@1.0.0/' in u: return r.fulfill(path=O + '@tesseract.js-data/eng/4.0.0_best_int/eng.traineddata.gz', content_type='application/gzip', headers=H)
    return r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript')
NOTICE_HTML = ('<body style="margin:0;background:#fff;font-family:Arial;font-size:20px;line-height:1.5;padding:24px"><b>LAMBETH COUNCIL</b><br><b>PENALTY CHARGE NOTICE</b><br>'
               'PCN Number: LJ12345678<br>Vehicle registration: AB12 CDE<br>Date of contravention: 03/10/2026<br>Time: 10:15<br>Location: Brixton Road<br>'
               'Penalty charge: £130, reduced to £65 if paid within 14 days.</body>')
def context(b, w=390, h=844, clock=None):
    ctx = b.new_context(viewport={'width': w, 'height': h}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', cdn)
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    if clock: pg.clock.install(time=clock)
    return ctx, pg
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg = context(b)
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    case = lambda cid: [c for c in cases() if c['id'] == cid][0]
    main = lambda: pg.inner_text('main')
    tap = lambda a: (pg.locator('.tab129 [data-a=%s]' % a).click(), wait(pg, 500))
    def sign_in(db=None):
        pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')")
        pg.evaluate("localStorage.setItem('__mocksession', JSON.stringify({user:{id:'u-me',email:'me@example.com'}}))")
        if db is not None: pg.evaluate("d=>localStorage.setItem('__mockdb', JSON.stringify(d))", db)
        pg.goto('https://sorted.test/'); wait(pg, 900)
    def start(text, plan=None, confirm=True):
        tap('new-case'); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 800)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count():
            if plan: pg.click('form[data-f=baseline] .chip:has-text("%s")' % plan)
            else: pg.click('form[data-f=baseline] .chip >> nth=0')
            pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 700)
        if confirm and pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
        if pg.locator('text=Not now').count(): pg.locator('text=Not now').first.click(); wait(pg, 300)
        return cases()[-1]['id']
    def poke(js):
        pg.goto('https://sorted.test/'); wait(pg, 500)
        pg.evaluate("(js)=>{var db=JSON.parse(localStorage.getItem('__mockdb'));(new Function('db',js))(db);localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", js)
        pg.goto('https://sorted.test/'); wait(pg, 800)
    def overdue(cid): poke("db.tasks.forEach(function(r){if(r.data.id==='%s')(r.data.promises||[]).forEach(function(q){if(q.status==='open'){q.dueAt=new Date(Date.now()-2*864e5).toISOString();q.dueEnd=null;q.allDay=true;q.by=true;q.prec='day'}})})" % cid)
    def open_case(cid): pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 800)
    def ss(): return pg.evaluate("JSON.stringify(Object.assign({},sessionStorage))")

    # ================= 006: a deadline on the person, with four other cases open =================
    sign_in()
    fri = today + datetime.timedelta(days=(4 - today.weekday()) % 7 or 7)
    start('Currys said on the phone they will refund my £89 within 5 working days, order 445566')
    start('BT said an engineer will come sometime next week to fix my broadband, ref BT998877')
    start('My landlord said he will send a plumber on %s about the leak under the sink' % fri.strftime('%A'))
    start('Argos said they would deliver the replacement kettle by %s, ref AR55667' % fri.strftime('%A'))
    hm = start('HMRC sent a letter saying I need to pay £400 by %d %s' % (DL.day, DL.strftime('%B')))
    ok((case(hm).get('deadline') or {}).get('date') == DL.isoformat() and not case(hm)['promises'], 'the HMRC letter is a deadline on you (%s), not their promise' % (case(hm).get('deadline')))
    tap('go-home'); wait(pg, 600)
    DB = dbj()
    for off, label in ((-4, 'minus 4 days'), (0, 'on the day'), (2, 'plus 2 days')):
        day = DL + datetime.timedelta(days=off)
        c2, pg2 = context(b, clock=datetime.datetime(day.year, day.month, day.day, 9, 0))
        pg2.goto('https://sorted.test/'); pg2.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')")
        pg2.evaluate("localStorage.setItem('__mocksession', JSON.stringify({user:{id:'u-me',email:'me@example.com'}}))"); pg2.evaluate("d=>localStorage.setItem('__mockdb', JSON.stringify(d))", DB)
        pg2.goto('https://sorted.test/'); wait(pg2, 1000)
        m = pg2.inner_text('main')
        row = pg2.locator('.home44-spot:has-text("HMRC"), .home44-row:has-text("HMRC")').first
        rt = row.inner_text()
        ok('nothing due' not in m.lower() and 'what does the letter ask' not in m.lower(), '%s: Home never says "nothing due" or "what does the letter ask you to do?"' % label)
        if off < 0:
            ok('Due ' + dlong(DL) in rt and pg2.locator('.home44-row.home111-hot:has-text("HMRC")').count() == 1, '%s: the HMRC row carries a pill, "Due %s", and ranks as needing attention: %r' % (label, dlong(DL), rt[:160]))
            ok('decide what to do before ' + dlong(DL) in rt, '%s: its next action names the deadline' % label)
            names = [x.split('\n')[0] for x in pg2.locator('main .home44-row.needs').all_inner_texts()]
            ok(names and 'Parking' not in ''.join(names) and any('HMRC' in x for x in names), '%s: ranked among the cases that need you' % label)
        elif off == 0:
            spot = pg2.inner_text('.home44-spot')
            ok('HMRC' in spot and 'Your deadline is today' in spot and 'your deadline is today' in spot, '%s: the HMRC case leads Needs you: %r' % (label, spot[:160]))
        else:
            spot = pg2.inner_text('.home44-spot')
            ok('HMRC' in spot and 'Your deadline passed on ' + dlong(DL) in spot and 'your deadline passed on ' + dlong(DL) in spot and 'contact HMRC' in spot, '%s: "Your deadline passed on %s" at the top of Needs you: %r' % (label, dlong(DL), spot[:200]))
        pg2.locator('.tab129 [data-a=cases]').click(); wait(pg2, 500)
        cm = pg2.inner_text('main')
        ok('nothing due' not in cm.lower() and 'what does the letter ask' not in cm.lower(), '%s: Cases agrees' % label)
        if off >= 0:
            first = pg2.locator('main .pick125').first.inner_text()
            ok('HMRC' in first, '%s: Cases lists the HMRC case first among Needs you: %r' % (label, first[:80]))
        pg2.goto('https://sorted.test/?task=%s' % hm); wait(pg2, 900)
        cm = pg2.inner_text('main'); now = pg2.inner_text('.now137')
        ok('nothing due' not in cm.lower() and 'what does the letter ask you to do' not in now.lower(), '%s: the case and its Now card never say "nothing due" or "what does the letter ask you to do?"' % label)
        if off < 0: ok('decide what to do before ' + dlong(DL) in now, '%s: Now names the deadline' % label)
        elif off == 0: ok('your deadline is today' in now and 'Your deadline is today.' in pg2.inner_text('.case96-health'), '%s: Now and the health line say the deadline is today' % label)
        else:
            ok('your deadline passed on ' + dlong(DL) in now and 'Your deadline passed on ' + dlong(DL) + '.' in pg2.inner_text('.case96-health'), '%s: Now and the health line say when it passed' % label)
            ok(pg2.locator('.dl143').count() == 1 and pg2.locator('.now143-go [data-p=call]').count() == 1, '%s: the case keeps the deadline, with a way to act from the Now card' % label)
        c2.close()

    # ================= 022 and 034: the next move, plainly =================
    # step 2 leads with waiting until their date (the full date: a bare weekday said on that weekday is today)
    tap('new-case'); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.fill('#f-case', 'Currys said they will refund my £40 by %s, order 778899' % fri.strftime('%A %-d %B')); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 800)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    chips = [x.strip() for x in pg.locator('form[data-f=baseline] .chip').all_inner_texts()]
    ok(chips and chips[0] == 'Wait until ' + dlong(fri) and 'Ask where the refund is' in chips, 'step 2 offers "Wait until %s" first, beside the chase options: %s' % (dlong(fri), chips))
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 700)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
    cur = cases()[-1]
    ok(cur['baseline'] == 'Wait until ' + dlong(fri) and [x for x in cur['promises'] if x['status'] == 'open'], 'the plan is kept as said and the promise is theirs')
    # an own step whose words carry its day: the date isn't said twice
    open_case(cur['id']); pg.locator('[data-a=panel][data-p=move]').first.evaluate('e=>e.click()'); wait(pg, 400)
    pg.fill('#f-mwhat', 'Send Currys the receipt by %s' % fri.strftime('%A')); pg.locator('#f-mwhat').dispatch_event('input'); wait(pg, 500)
    if pg.locator('#moveform [data-a=use-msug]').count(): pg.click('#moveform [data-a=use-msug]'); wait(pg, 300)
    pg.click('#moveform button[type=submit]'); wait(pg, 800)
    ok([x for x in case(cur['id']).get('moves') or [] if x['status'] == 'open'], 'your own step is saved')
    now = pg.inner_text('.now137 .now125')
    ok('Send Currys the receipt'.lower() in now.lower() and now.count(fri.strftime('%A')) == 1, 'the next action says its day once: %r' % now)
    u = pg.locator('details.case117-u'); u.evaluate('d=>d.open=true'); wait(pg, 200)
    ut = u.inner_text()
    ok(not re.search(r'by %s, by %s' % (fri.strftime('%A'), fri.strftime('%A')), ut), 'What Sorted understood says the step’s day once')
    # a money promise that will "come through"
    mny = start('Currys said the £40 refund would come through by %s, order 991122' % fri.strftime('%A'))
    overdue(mny)
    rowx = pg.locator('.home44-spot:has-text("991122"), .q130-item:has-text("991122")').first
    t = rowx.inner_text()
    ok('It arrived' in t and 'Not yet' in t and 'They came' not in t and 'Nobody came' not in t and ('Did the money arrive?' in t or 'Has the money arrived?' in t), 'a refund that will "come through" asks about the money: %r' % t[:200])
    open_case(mny); cm = main()
    ok('It arrived' in cm and 'Nobody came' not in cm and 'Show this' not in cm, 'the case asks about the money too')
    # quick answers under Also open carry their question
    overdue(cur['id'])
    items = pg.locator('.q130-item')
    ok(items.count() >= 1 and all(pg.locator('.q130-item').nth(i).locator('.q143-q').count() == 1 for i in range(items.count())), 'every quick answer under Also open carries its question (%d rows)' % items.count())
    # Home counts what it shows
    m = main(); quick = pg.locator('.home44-spot .q130-acts, .q130-item').count(); needs = pg.locator('.home44-spot').count() + pg.locator('main .home44-section.needs .home44-row').count()
    head = pg.inner_text('.home44-headline')
    ok(head == '%d things need you.' % needs and ('%d of them need a quick answer.' % quick) in m, 'the headline counts the %d cases shown, and says %d need a quick answer: %r' % (needs, quick, head))
    # the Now card carries its button, above the fold on 390x844
    open_case(mny); btn = pg.locator('.now137 .now143-go .btn')
    bb = btn.bounding_box() if btn.count() else None
    ok(bb is not None and bb['y'] + bb['height'] <= 844 and 'money' in btn.inner_text().lower(), 'the Now card names the next step and carries its button on screen: %r' % (btn.inner_text() if btn.count() else None))
    btn.click(); wait(pg, 400)
    ok(pg.evaluate("(()=>{var a=document.activeElement;return !!a&&a.closest('.promise-foot')!==null&&a.getAttribute('data-a')==='kept'})()"), 'its button takes you to the answer')
    # "they are looking into it"
    bc = start('Need to sort out a missing payment with Barclays, they are looking into it')
    m = main()
    ok(pg.locator('form[data-f=call]').count() == 0 and pg.locator('.turn143 .turn117').count() == 1 and pg.locator('.turn117').count() == 1, 'looking into it: whose move it is leads, no open call form, asked once')
    ok('say whether it’s your move or theirs' in pg.inner_text('.now137'), 'Now asks whose move it is')
    pg.click('.turn143 [data-a=turn-theirs]'); wait(pg, 500)
    ok(case(bc).get('turn') == 'theirs' and pg.locator('form[data-f=call]').count() == 0 and pg.locator('.wait143').count() == 1 and 'wait to hear back' in pg.inner_text('.now137'), 'theirs: waiting, with a follow-up, never an open call form')
    pg.click('.wait143 [data-a=fr-check][data-d="7"]'); wait(pg, 600)
    mv = [x for x in case(bc).get('moves') or [] if x['status'] == 'open']
    ok(len(mv) == 1 and not case(bc)['promises'], 'a follow-up a week out is your own step, never their promise')

    # ================= 033: wording, prompts =================
    open_case(mny); pg.locator('details.case56-more').evaluate('d=>d.open=true')
    ok(pg.inner_text('details.case56-more summary').startswith('Manage this case'), 'the case’s own tools are "Manage this case", not a second "More"')
    tap('data'); pg.locator('[data-v=help]').first.evaluate('e=>e.click()'); wait(pg, 500); hm_ = pg.locator('main').text_content()
    ok('under More' not in hm_ and 'in “Manage this case” at the bottom of the case page' in hm_, 'Help says where the correction tools are')

    # ================= 021: unfinished work =================
    # every case panel with words survives a refresh
    for P in ('paste', 'move', 'correct', 'rename', 'refadd', 'done', 'summary137', 'pack'):
        open_case(mny)
        pg.locator('details').evaluate_all('ds=>ds.forEach(d=>d.open=true)')
        pg.locator('main [data-a=panel][data-p=%s]' % P).first.evaluate('e=>e.click()'); wait(pg, 400)
        fld = pg.locator('main form textarea:visible, main form input[type=text]:visible, main form input:not([type]):visible, main .sum137 textarea:visible').first
        mk = 'Kept%sWords' % P
        fld.click(); fld.press('End'); fld.type(' ' + mk); wait(pg, 200)
        pg.reload(); wait(pg, 1000)
        ban = pg.locator('.keep125')
        ok(ban.count() == 1 and mk in ban.inner_text(), '%s: after a refresh the words are offered back' % P)
        if ban.count():
            pg.click('[data-a=keep-go]'); wait(pg, 500)
            vals = pg.evaluate("Array.from(document.querySelectorAll('main textarea,main input')).map(e=>e.value).join('|')")
            ok(mk in vals, '%s: "Carry on writing" puts them back in the form' % P)
        pg.locator('main [data-a=panel][data-p=""]').first.evaluate('e=>e.click()') if pg.locator('main [data-a=panel][data-p=""]').count() else None; wait(pg, 300)
        ok('sorted.form.live' not in ss() and mk not in json.dumps(case(mny)), '%s: closing the panel drops the live copy; nothing reached the case' % P)
    # the summary ask and the pack questions survive leaving
    open_case(mny); pg.locator('details').evaluate_all('ds=>ds.forEach(d=>d.open=true)')
    pg.locator('main [data-a=panel][data-p=summary137]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.fill('#sum137-ask', 'Please refund the £40 SummaryAskKept'); pg.locator('#sum137-ask').dispatch_event('input'); wait(pg, 200)
    tap('cases'); open_case(mny)
    ok('SummaryAskKept' in main(), 'the summary ask is kept when you leave the case')
    pg.click('[data-a=keep-go]'); wait(pg, 400)
    ok('SummaryAskKept' in pg.input_value('#sum137-ask') and 'SummaryAskKept' in pg.inner_text('#sum137-pre'), 'and comes back in the box and the preview')
    pg.locator('main [data-a=panel][data-p=""]').first.evaluate('e=>e.click()'); wait(pg, 300)
    # door switching keeps who and what
    tap('new-case'); pg.locator('[data-cap82=promise]').first.evaluate('e=>e.click()'); wait(pg, 400)
    pg.locator('#gi-who').type('Hotpoint'); pg.locator('#gi-what').type('send an engineer on Monday'); wait(pg, 200)
    pg.click('[data-a=gi-back]'); wait(pg, 500)
    ok(pg.locator('#f-case').count() == 1 and 'Hotpoint' in pg.input_value('#f-case') and 'send an engineer on Monday' in pg.input_value('#f-case'), '"← Choose something else" keeps what you typed, in the box: %r' % (pg.input_value('#f-case') if pg.locator('#f-case').count() else None))
    tap('new-case'); pg.locator('[data-cap82=promise]').first.evaluate('e=>e.click()'); wait(pg, 400)
    pg.fill('#gi-who', 'Hotpoint'); pg.fill('#gi-what', 'send an engineer on Monday'); pg.locator('#gi-what').dispatch_event('input'); wait(pg, 200)
    if pg.locator('[data-a=gi-own]').count():
        pg.click('[data-a=gi-own]'); wait(pg, 400)
        ok('Hotpoint' in pg.input_value('#f-case'), '"your own words" keeps them too')
    # a recovered draft is offered near the top of Home
    tap('go-home'); pg.reload(); wait(pg, 900)
    d = pg.locator('.draft119'); intro = pg.locator('.home44-intro, .home111-calm').first
    ok(d.count() == 1 and intro.count() == 1 and d.bounding_box()['y'] < intro.bounding_box()['y'], 'the recovered draft is offered at the top of Home, above Needs you')
    pg.click('[data-a=draft-drop]'); wait(pg, 300)
    # the Moving home form survives leaving it and a refresh
    tap('new-case'); pg.locator('[data-a=mom-start]').first.evaluate('e=>e.click()'); wait(pg, 500)
    if not pg.locator('#mv-date').count(): pg.locator('[data-a=mom-new]').first.evaluate('e=>e.click()'); wait(pg, 400)
    mvd = (today + datetime.timedelta(days=40)).isoformat()
    pg.click('label.chip:has(input[name=mv-nation][value=sc])'); pg.click('label.chip:has(input[name=mv-tenure][value=buy])'); pg.fill('#mv-date', mvd); wait(pg, 300)
    tap('go-home'); tap('new-case'); pg.locator('[data-a=mom-start]').first.evaluate('e=>e.click()'); wait(pg, 500)
    if not pg.locator('#mv-date').count(): pg.locator('[data-a=mom-new]').first.evaluate('e=>e.click()'); wait(pg, 400)
    nat = lambda: pg.evaluate("(document.querySelector('input[name=mv-nation]:checked')||{}).value")
    ten = lambda: pg.evaluate("(document.querySelector('input[name=mv-tenure]:checked')||{}).value")
    ok(pg.input_value('#mv-date') == mvd and nat() == 'sc' and ten() == 'buy', 'Moving home keeps the date and answers when you leave and come back')
    pg.reload(); wait(pg, 900); tap('new-case'); pg.locator('[data-a=mom-start]').first.evaluate('e=>e.click()'); wait(pg, 500)
    if not pg.locator('#mv-date').count(): pg.locator('[data-a=mom-new]').first.evaluate('e=>e.click()'); wait(pg, 400)
    ok(pg.input_value('#mv-date') == mvd and nat() == 'sc', 'and after a refresh')
    pg.click('form[data-f=mom] button[type=submit]'); wait(pg, 700)
    ok(any(x['data'].get('kind') == 'moment' for x in dbj().get('tasks', [])) and 'sorted.form.mv' not in ss(), 'saving the move drops the kept answers')

    # the notice under review, abandoned through each tab, Back and a refresh
    def parking():
        tap('new-case'); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', 'PCN'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 500)
    def read_wait():
        for _ in range(240):
            st = (pg.inner_text('#ocr-status') if pg.locator('#ocr-status').count() else '') + ' ' + (pg.inner_text('#doc-status') if pg.locator('#doc-status').count() else '')
            if re.search(r'Photo read|couldn’t|doesn’t look|Done\.|can’t read', st): wait(pg, 700); return st.strip()
            wait(pg, 500)
    sp = b.new_page(viewport={'width': 560, 'height': 420}); sp.set_content(NOTICE_HTML); sp.screenshot(path=HERE + '/tests/out/doc108_notice.png'); sp.close()
    parking(); pg.set_input_files('input[data-ocr=f-case]', HERE + '/tests/out/doc108_notice.png'); st = read_wait()
    ok(pg.locator('.doc121-review').count() == 1 and pg.input_value('#doc-ref') == 'LJ12345678', 'a notice under review (%s)' % (st or '')[:40])
    pg.fill('#doc-vrm', 'AB12 CDF'); pg.locator('#doc-vrm').dispatch_event('input'); wait(pg, 200)
    n0 = len(cases())
    for how in ('cases', 'data', 'new-case', 'back', 'refresh'):
        if how == 'back': tap('cases'); pg.go_back(); wait(pg, 700)
        elif how == 'refresh': pg.reload(); wait(pg, 1000)
        else: tap(how)
        if how != 'go-home': tap('go-home')
        k = pg.locator('.doc143-keep')
        ok(k.count() == 1 and 'Carry on checking your notice' in k.inner_text() and len(cases()) == n0, '%s: Home offers "Carry on checking your notice", and no case was made' % how)
        if not k.count(): break
        pg.click('[data-a=doc-resume143]'); wait(pg, 500)
        ok(pg.locator('.doc121-review').count() == 1 and pg.input_value('#doc-vrm') == 'AB12 CDF' and pg.input_value('#doc-ref') == 'LJ12345678', '%s: back in the review with your correction' % how)
    # after "These are right": the confirmed details are kept until the case starts
    pg.click('form[data-f=doc] button[type=submit]'); wait(pg, 700)
    ok(pg.locator('form[data-f=baseline]').count() == 1, 'confirmed: step 2')
    tap('cases'); tap('go-home')
    k = pg.locator('.doc143-keep')
    ok(k.count() == 1 and 'haven’t started the case' in k.inner_text() and len(cases()) == n0, 'leaving step 2 keeps the confirmed details, still no case')
    pg.click('[data-a=doc-resume143]'); wait(pg, 500)
    ok(pg.locator('form[data-f=baseline]').count() == 1, 'and they come back at step 2')
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 700)
    c = cases()[-1]; f = (c.get('cf') or {}).get('f') or {}
    ok(len(cases()) == n0 + 1 and f.get('vrm', {}).get('v') == 'AB12 CDF' and f['vrm']['how'] == 'you' and f['ref']['st'] == 'confirmed', 'the case starts with the confirmed details, your correction marked as yours')
    ok('sorted.form.doc' not in ss() and pg.locator('.doc143-keep').count() == 0, 'once the case starts nothing is kept')
    # discarding a kept review
    parking(); pg.set_input_files('input[data-ocr=f-case]', HERE + '/tests/out/doc108_notice.png'); read_wait()
    tap('cases'); tap('go-home'); pg.click('[data-a=doc-drop143]'); wait(pg, 400)
    ok(pg.locator('.doc143-keep').count() == 0 and 'sorted.form.doc' not in ss(), '"Discard it" removes the kept notice')
    # sign-out leaves nothing behind
    parking(); pg.set_input_files('input[data-ocr=f-case]', HERE + '/tests/out/doc108_notice.png'); read_wait(); tap('cases')
    open_case(mny); pg.locator('main [data-a=panel][data-p=paste]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.locator('main form textarea').first.type('LeakyWords'); wait(pg, 200)
    ok('LeakyWords' in ss() and 'LJ12345678' in ss(), 'while signed in, the half-written words and the notice are on this phone')
    tap('data'); pg.click('[data-a=signout]'); wait(pg, 900)
    if pg.locator('[data-a=signout-discard]').count(): pg.click('[data-a=signout-discard]'); wait(pg, 800)
    leak = pg.evaluate("JSON.stringify(Object.keys(localStorage).filter(k=>!k.startsWith('__mock')).map(k=>localStorage.getItem(k)))+JSON.stringify(Object.assign({},sessionStorage))")
    ok('LeakyWords' not in leak and 'LJ12345678' not in leak and 'AB12 CD' not in leak, 'after sign-out none of it is left on the phone')
    ctx.close()

    # ================= 033: a guest sees one email prompt at a time =================
    ctx, pg = context(b)
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')")
    pg.goto('https://sorted.test/#start'); wait(pg, 400); pg.click('[data-a=anon-start]'); wait(pg, 800)
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.fill('#f-case', 'Currys said they will refund my £89 by %s, order 445566' % fri.strftime('%A')); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 800)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 700)
    pg.click('[data-a=sug-yes]'); wait(pg, 700)
    vis = lambda: len([e for e in pg.locator('main [data-a=go-claim]').all() if e.is_visible()])
    prompts = pg.locator('#claim').count() + vis()
    ok(pg.locator('#claim').count() == 1 and prompts == 1, 'after confirming, a guest is asked for an email once (%d prompts)' % prompts)
    pg.locator('#claim [data-a=panel]').first.click(); wait(pg, 400)
    ok(pg.locator('#claim').count() == 0 and vis() == 1, 'after "Not now", one prompt remains')
    ctx.close()

    # ================= 024: the "All clear" card =================
    for w in (320, 390, 768):
        ctx, pg = context(b, w=w, h=800)
        pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')")
        pg.goto('https://sorted.test/#start'); wait(pg, 400); pg.click('[data-a=anon-start]'); wait(pg, 800)
        pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', 'Currys said they will refund my £89 by %s, order 445566' % fri.strftime('%A')); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 800)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 700)
        if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
        pg.locator('.tab129 [data-a=go-home]').click(); wait(pg, 600)
        hb = pg.locator('.home111-calm .home44-headline'); sec = pg.locator('.home111-calm')
        if hb.count():
            g = hb.evaluate("e=>{var r=e.getBoundingClientRect(),lh=parseFloat(getComputedStyle(e).lineHeight)||r.height;return {w:r.width,lines:Math.round(r.height/lh)}}")
            ok(g['w'] >= 0.5 * sec.bounding_box()['width'] and g['lines'] <= 2 and pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth+1"), '%dpx: "Nothing needs you right now." is %dpx wide on %d line(s)' % (w, g['w'], g['lines']))
        else: ok(False, '%dpx: the All clear card is shown' % w)
        ctx.close()
    ok(not errs, 'no page errors: %s' % errs[:3])
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
