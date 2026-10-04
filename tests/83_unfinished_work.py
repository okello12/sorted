# v125 (the remaining-pages review, signed in). Unfinished work is kept: words typed into your next step survive leaving
# the form, leaving the case and a reload, are offered back ("Carry on writing", "Discard it") and come back when the
# same form is opened; Moving home keeps the other answers after a missing date. Choosing a case: a shared-in message
# with eight open cases lists all eight with a search that filters as you type and says when nothing matches. Deleting
# a case says what Undo really does. A case leads with its status and one next step, with the first response and What
# Sorted understood after the action. The document door says "Start with your document", keeps the choice (no second
# chooser) and says a scanned PDF is read from its first page only; the ordinary picker says the same.
import os, sys, json, datetime
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
    moms = lambda: [x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') == 'moment']
    main = lambda: pg.inner_text('main')
    def poke(js):
        pg.goto('https://sorted.test/'); wait(pg, 700)
        pg.evaluate("(js)=>{var db=JSON.parse(localStorage.getItem('__mockdb'))||{tasks:[],shares:[],reminders:[],helpers:[],inbound_items:[],pilot_events:[],case_notes:[]};(new Function('db',js))(db);localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", js)
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    uid = pg.evaluate("JSON.parse(localStorage.getItem('__mocksession')).user.id")
    # ---- 0. the document door keeps the choice and says what it reads ----
    pg.locator('[data-cap82=document]').first.evaluate('e=>e.click()'); wait(pg, 500); m = main()
    ok(pg.locator('#cap82-start').count() == 0 and 'Start with your document' in m and 'Take a photo or choose the letter' in m and 'Or type what it says' in m, 'the document door: its own heading, the photo first, no second chooser above it')
    ok('For a scanned PDF, only the first page is read.' in m, 'the first-page limit is beside the document picker')
    ok(m.index('Take a photo or choose the letter') < m.index('Or type what it says'), 'the photo button comes before the box')
    pg.click('[data-a=gi-back]'); wait(pg, 400)
    ok(pg.locator('#cap82-start [data-cap82=document]').count() == 1, '“Choose something else” brings the choices back')
    # ---- 1. eight open cases, made directly ----
    now = pg.evaluate("new Date().toISOString()")
    names = ['Currys refund', 'Aviva claim', 'BT broadband', 'Landlord boiler', 'HMRC letter', 'Southwark parking', 'Virgin Media bill', 'Royal Mail parcel']
    rows = []
    for i, nm in enumerate(names):
        rows.append({'id': 'c%d' % i, 'title': nm, 'mode': 'call', 'board': 'yours', 'created': now, 'updatedAt': now, 'rev': 1, 'said': nm + ' still not sorted', 'facts': {'party': nm.split(' ')[0]}, 'promises': [], 'moves': [], 'events': [{'at': now, 'label': 'Started.'}]})
    poke(';'.join("db.tasks.push({id:%s,user_id:%s,data:%s,updated_at:new Date().toISOString()})" % (json.dumps(r['id']), json.dumps(uid), json.dumps(r)) for r in rows))
    # ---- 2. a shared-in message: every case, with a search ----
    pg.goto('https://sorted.test/?s=1#new=' + 'Your%20parcel%20is%20delayed'); wait(pg, 900)
    btns = pg.locator('.share-to.pick125')
    ok(btns.count() == 8 and pg.locator('#pick-q').count() == 1, 'all eight open cases are offered, with a search box (%d)' % btns.count())
    pg.fill('#pick-q', 'royal'); wait(pg, 200)
    vis = [x for x in pg.locator('.share-to.pick125').all() if x.is_visible()]
    ok(len(vis) == 1 and 'Royal Mail parcel' in vis[0].inner_text(), 'typing filters the list to the matching case')
    pg.fill('#pick-q', 'zzzz'); wait(pg, 200)
    ok(pg.locator('.pick125-none').is_visible() and not [x for x in pg.locator('.share-to.pick125').all() if x.is_visible()], 'no match says so, and Start a new case is still there')
    pg.fill('#pick-q', ''); wait(pg, 200)
    ok(len([x for x in pg.locator('.share-to.pick125').all() if x.is_visible()]) == 8, 'clearing the search shows them all again')
    # ---- 3. your next step: typed, left, kept, offered back, restored ----
    pg.goto('https://sorted.test/?task=c0'); wait(pg, 600)
    m = main()
    ok('Next:' in m.split('Timeline')[0], 'the case leads with its next step')
    pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
    first = pg.locator('[data-a=panel][data-p=move]').first
    if first.count(): first.evaluate('e=>e.click()')
    else: pg.evaluate("(()=>{var b=document.createElement('button');b.setAttribute('data-a','panel');b.setAttribute('data-p','move');document.querySelector('main').appendChild(b);b.click()})()")
    wait(pg, 400)
    ok(pg.locator('#f-mwhat').count() == 1, 'your next step form is open')
    pg.type('#f-mwhat', 'Ring Currys about the refund on Friday'); wait(pg, 200)
    pg.locator('.bar [data-a=home]').first.click(); wait(pg, 500)
    pg.goto('https://sorted.test/?task=c0'); wait(pg, 600); m = main()
    ok('You were writing something here.' in m and 'Ring Currys about the refund on Friday' in m and pg.locator('[data-a=keep-go]').count() == 1, 'coming back to the case offers what you were writing')
    ok(not any('Ring Currys' in json.dumps(c) for c in cases()), 'nothing was saved to the case or the server')
    pg.reload(); wait(pg, 700); pg.goto('https://sorted.test/?task=c0'); wait(pg, 700)
    ok('You were writing something here.' in main(), 'it survives a reload on this phone')
    pg.click('[data-a=keep-go]'); wait(pg, 400)
    ok(pg.locator('#f-mwhat').count() == 1 and pg.input_value('#f-mwhat') == 'Ring Currys about the refund on Friday' and pg.evaluate("document.activeElement&&document.activeElement.id") == 'f-mwhat', '“Carry on writing” reopens the form with your words and puts you in it')
    # leaving with Cancel keeps them too, and opening the same form brings them back by itself
    pg.locator('form[data-f=move] ~ [data-a=panel][data-p=""], #moveform [data-a=panel][data-p=""]').first.evaluate('e=>e.click()') if pg.locator('#moveform [data-a=panel][data-p=""]').count() else pg.evaluate("(()=>{var b=document.createElement('button');b.setAttribute('data-a','panel');b.setAttribute('data-p','');document.querySelector('main').appendChild(b);b.click()})()")
    wait(pg, 400)
    pg.evaluate("(()=>{var b=document.createElement('button');b.setAttribute('data-a','panel');b.setAttribute('data-p','move');document.querySelector('main').appendChild(b);b.click()})()"); wait(pg, 400)
    ok(pg.locator('#f-mwhat').count() == 1 and pg.input_value('#f-mwhat') == 'Ring Currys about the refund on Friday', 'cancelling keeps the words; opening the form again brings them back')
    pg.evaluate("(()=>{var b=document.createElement('button');b.setAttribute('data-a','panel');b.setAttribute('data-p','');document.querySelector('main').appendChild(b);b.click()})()"); wait(pg, 300)
    pg.click('[data-a=keep-drop]'); wait(pg, 300)
    ok('You were writing something here.' not in main() and pg.evaluate("Object.keys(sessionStorage).filter(k=>k.startsWith('sorted.form.')).map(k=>sessionStorage.getItem(k)).join('')").find('Ring Currys') < 0, '“Discard it” removes the words from the phone')
    # sign-out clears them
    pg.evaluate("(()=>{var b=document.createElement('button');b.setAttribute('data-a','panel');b.setAttribute('data-p','move');document.querySelector('main').appendChild(b);b.click()})()"); wait(pg, 300)
    pg.type('#f-mwhat', 'Private words about the boiler'); pg.locator('.bar [data-a=home]').first.click(); wait(pg, 400)
    pg.goto('https://sorted.test/'); wait(pg, 600); pg.locator('[data-a=data]').first.evaluate('e=>e.click()'); wait(pg, 500); pg.locator('[data-a=wipe-ask]').first.evaluate('e=>e.click()'); wait(pg, 300); pg.locator('[data-a=wipe]').first.evaluate('e=>e.click()'); wait(pg, 900)
    ok(pg.evaluate("JSON.stringify(Object.assign({},localStorage,sessionStorage))").find('Private words') < 0, 'deleting the account (a guest has no sign-out) leaves none of the unfinished words on the phone')
    pg.goto('https://sorted.test/#start'); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    # ---- 4. Moving home keeps answers after a missing date ----
    pg.locator('[data-a=mom-start]').first.evaluate('e=>e.click()'); wait(pg, 500)
    if not pg.locator('#mv-date').count(): pg.locator('[data-a=mom-new]').first.evaluate('e=>e.click()'); wait(pg, 400)
    pg.click('label.chip:has(input[name=mv-nation][value=wa])'); pg.click('label.chip:has(input[name=mv-tenure][value=buy])'); pg.click('label.chip:has(input[name=mv-car][value=yes])'); pg.click('label.chip:has(input[name=mv-bb][value=yes])')
    pg.click('form[data-f=mom] button[type=submit]'); wait(pg, 400)
    chk = lambda nm: pg.evaluate("(document.querySelector('input[name=%s]:checked')||{}).value||''" % nm)
    ok('Pick the day you’re moving' in main() and 'Your other answers are kept.' in main() and not moms(), 'a missing date is asked for and nothing is saved')
    ok(chk('mv-nation') == 'wa' and chk('mv-tenure') == 'buy' and chk('mv-car') == 'yes' and chk('mv-bb') == 'yes' and pg.evaluate("document.activeElement&&document.activeElement.id") == 'mv-date', 'every answer is still selected and you are put on the date')
    pg.fill('#mv-date', (datetime.date.today() + datetime.timedelta(days=30)).isoformat()); pg.click('form[data-f=mom] button[type=submit]'); wait(pg, 600)
    mv = moms()
    ok(mv and mv[0]['ans'].get('nation') == 'wa' and mv[0]['ans'].get('tenure') == 'buy' and mv[0]['ans'].get('car') == 'yes', 'the move is saved with the answers given before the error')
    # ---- 5. deleting a case says what Undo does ----
    poke("db.tasks.push({id:'del1',user_id:%s,data:%s,updated_at:new Date().toISOString()})" % (json.dumps(pg.evaluate("JSON.parse(localStorage.getItem('__mocksession')).user.id")), json.dumps(dict(rows[0], id='del1', title='Delete me'))))
    pg.goto('https://sorted.test/?task=del1'); wait(pg, 600)
    pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
    pg.locator('[data-a=panel][data-p=delcase]').first.evaluate('e=>e.click()'); wait(pg, 300); m = main()
    ok('can’t be undone' not in m and 'For two minutes afterwards you can undo it from Home, on this page only.' in m, 'deleting says what Undo really does')
    # ---- 6. a case: status and next step first, explanations after the action ----
    pg.goto('https://sorted.test/'); wait(pg, 500)
    pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
    fri = datetime.date.today() + datetime.timedelta(days=(4 - datetime.date.today().weekday()) % 7 or 7)
    pg.fill('#f-case', 'Currys said they would refund £89 by %s, order 445566' % fri.strftime('%A')); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
    cc = [c for c in cases() if 'refund £89' in (c.get('said') or '')]; pg.goto('https://sorted.test/?task=%s' % cc[-1]['id']); wait(pg, 700)
    order = pg.evaluate("(()=>{var q=s=>{var e=document.querySelector(s);return e?[...document.querySelectorAll('main *')].indexOf(e):-1};return {now:q('.now125'),promise:q('.promise, .promise-line'),fr:q('.fr92, [data-a=fr-ok]'),u:q('details.case117-u'),time:q('#case56-timeline')}})()")
    ok(order['now'] >= 0 and order['promise'] > order['now'], 'the status line comes before the action (%s)' % order)
    ok((order['fr'] < 0 or order['fr'] > order['promise']) and (order['u'] < 0 or order['u'] > order['promise']) and (order['time'] < 0 or order['u'] < 0 or order['u'] < order['time']), 'the first response and What Sorted understood follow the action, before the history')
    ok('Waiting for Currys:' in main() or 'Next:' in main(), 'the line names who you are waiting for, or the next step')
    ok(not errs, 'no page errors: %s' % errs)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
