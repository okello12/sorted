# v61: parking playbook, release 2. Stages, dates that say what they mean, proof of what was sent, and waiting on them.
import os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates  # sets London time
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=350): pg.wait_for_timeout(ms)
T0 = datetime.date.today()
SEP = ','  # Chromium's own date format decides: some versions write "Fri, 2 Oct", newer ones "Fri 2 Oct"; set from the browser below
def d(n): return T0 + datetime.timedelta(days=n)
def uk(x): return x.strftime('%d/%m/%Y')
def iso(x): return x.isoformat()
def day(x): return x.strftime('%A %-d %B') if x.year == T0.year else x.strftime('%A %-d %B %Y')
def tasks(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks.map(y=>y.data)")
def case(pg, title): return next((x for x in tasks(pg) if x['title'] == title), None)
def poke(pg, title, js):
    pg.evaluate("""([t,js])=>{var db=JSON.parse(localStorage.getItem('__mockdb'));var x=db.tasks.find(y=>y.data.title===t).data;(new Function('x',js))(x);
      localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}""", [title, js])
def start(pg, text):
    pg.goto('https://sorted.test/'); wait(pg, 400)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
    pg.fill('#f-case', text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 450)
    if pg.locator('[data-a=cf-yes]').count(): pg.click('[data-a=cf-yes]'); wait(pg)
def open_case(pg, title):
    pg.goto('https://sorted.test/'); wait(pg, 400)
    pg.locator('[data-a=open][data-id="%s"]' % case(pg, title)['id']).first.click(); wait(pg)
def dates_block(pg): return pg.inner_text('.pk-dates') if pg.locator('.pk-dates').count() else ''
def card(pg): return pg.inner_text('.pk-card') if pg.locator('.pk-card').count() else ''
N = d(-3)
PCN = ("London Borough of Southwark PENALTY CHARGE NOTICE PCN Number: SK12345678 Vehicle Registration Mark: AB12 CDE "
       "Date of contravention: %s Time: 10:14 Location: Lordship Lane SE22 Contravention code: 12 Parked without a permit. "
       "The penalty charge is £130. If paid within 14 days of the date of this notice, the penalty charge is reduced by 50%% to £65." % uk(N))
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    SEP = ',' if ',' in pg.evaluate("new Date(2026,9,2).toLocaleDateString('en-GB',{weekday:'short',day:'numeric',month:'short'})") else ''
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 200); pg.click('[data-a=anon-start]'); wait(pg)
    T = 'Southwark PCN · SK12345678'
    start(pg, PCN)
    # 1 the notice stage: the choice and the dates that matter
    c = card(pg)
    ok('Pay it or challenge it?' in c and 'NOTICE RECEIVED' in c.upper(), 'confirmed notice opens the playbook: pay or challenge')
    ok(pg.locator('form[data-f=call]').count() == 0, 'no call form in the way')
    ok(('Reduced price (£65) ends: ' + day(d(10))) in c, 'the card leads with the reduced-price date, on the safe side (%s)' % day(d(10)))
    ok('costs £65 instead of £130' in c, 'it says what paying in time saves')
    db = dates_block(pg)
    ok('Reduced price (£65) ends' in db and day(d(10)) in db and 'Full charge (£130) due' in db and day(d(24)) in db, 'dates that matter: reduced price and full charge')
    ok('Worked out: 14 days counting the date it happened' in db and 'the notice is right' in db, 'each worked-out date says how, and that the notice wins')
    pg.screenshot(path=HERE + '/tests/out/playbook_notice.png', full_page=True)
    # 2 home says the next step
    pg.goto('https://sorted.test/'); wait(pg, 400)
    ok(('Decide by ' + day(d(10)) + ': pay or challenge') in pg.inner_text('main'), 'Home: "Decide by …: pay or challenge"')
    open_case(pg, T)
    # 3 remind me
    pg.click('[data-a=pk-remind]'); wait(pg)
    t = case(pg, T); mv = [m for m in t.get('moves', []) if m['status'] == 'open']
    ok(len(mv) == 1 and mv[0]['dueAt'][:10] in (iso(d(8)), iso(d(7))) and 'pay or challenge' in mv[0]['what'], 'a reminder two days before: %s' % (mv[0]['what'] if mv else None))
    # 4 change a date to the one on the notice
    pg.click('[data-a=pk-date][data-k=discount]'); wait(pg); pg.fill('#f-pkdt', iso(d(11))); pg.click('form[data-f=pkdate] button[type=submit]'); wait(pg)
    db = dates_block(pg)
    ok(day(d(11)) in db and 'You set this date' in db, 'you can set the date from the notice')
    # 5 proof of a challenge
    ok(pg.locator('.pk-card').count() == 1 and ('Sorted will remind you on ' + day(d(8))) in card(pg) and pg.locator('.case56-next').count() == 1, 'the reminder sits inside the parking card, which stays')
    pg.click('[data-a=panel][data-p=pksent]'); wait(pg)
    pg.click('[data-a=d][data-k=pkhow][data-v="Online form"]'); wait(pg, 200)
    pg.fill('#f-pkref', 'ABC3942'); pg.fill('#f-pktext', 'I am challenging PCN SK12345678. I had a valid permit on display.')
    pg.click('form[data-f=pksent] button[type=submit]'); wait(pg)
    t = case(pg, T); pr = [x for x in t['promises'] if x['status'] == 'open']
    ok(len(pr) == 1 and pr[0]['src'] == 'parking' and pr[0]['dueAt'][:10] in (iso(d(28)), iso(d(27))) and pr[0]['ref'] == 'ABC3942', 'sending a challenge starts waiting on them for 4 weeks, with the confirmation ref')
    ok(t['pk']['stage'] == 'challenged' and t['pk']['subs'][0]['how'] == 'Online form', 'the stage moves on and the proof is kept')
    ok(not [m for m in t.get('moves', []) if m['status'] == 'open'], 'the reminder to decide is closed')
    main = pg.inner_text('main')
    ok('Waiting for: A reply to your challenge. No date was given' in main, 'the case says what you are waiting for, not that they promised it')
    ok('What you sent' in main and 'ABC3942' in main and 'Online form' in main, 'what you sent is on the case')
    ok(any(e['label'].startswith('Challenge sent (online form) on ') and 'ref ABC3942' in e['label'] for e in t['events']), 'the history records it')
    pg.goto('https://sorted.test/'); wait(pg, 400)
    ok('Waiting' in pg.inner_text('main') and 'Southwark' in pg.inner_text('main'), 'Home holds it in Waiting')
    # 6 the date passes: did they reply?
    poke(pg, T, "x.promises.filter(q=>q.status==='open')[0].dueAt=new Date(Date.now()-864e5).toISOString()")
    pg.goto('https://sorted.test/'); wait(pg, 500)
    ok('Did they get back to you?' in pg.inner_text('main'), 'when the date passes, Home asks whether they got back to you')
    pg.click('.home44-spot [data-a=home-ans][data-v=kept]'); wait(pg, 500)
    ok('They said no' in card(pg) and 'They cancelled it' in card(pg), 'they replied: what did they decide?')
    pg.click('[data-a=panel][data-p=pkrej]'); wait(pg); pg.fill('#f-pkrj', iso(d(0))); pg.click('form[data-f=pkrej] button[type=submit]'); wait(pg)
    c = card(pg); db = dates_block(pg)
    ok('They rejected your challenge' in c and 'wait for the Notice to Owner' in c, 'a rejected informal challenge: pay, or wait for the Notice to Owner')
    ok('Reduced price may be offered again until' in db and day(d(13)) in db, 'and the reduced price may be offered again for 14 days')
    # 7 the Notice to Owner arrives
    NTO = ("London Borough of Southwark NOTICE TO OWNER PCN Number: SK12345678 Vehicle Registration Mark: AB12 CDE Date of notice: %s "
           "Date of contravention: %s The penalty charge of £130 has not been paid." % (uk(d(0)), uk(N)))
    pg.click('[data-a=panel][data-p=paste]'); wait(pg); pg.fill('#f-paste', NTO); pg.click('form[data-f=paste] button[type=submit]'); wait(pg)
    pg.click('[data-a=cf-yes]'); wait(pg)
    c = card(pg)
    ok('Pay it or make a formal challenge?' in c and ('Pay or make a formal challenge by: ' + day(d(27))) in c, 'Notice to Owner: pay or make a formal challenge, 28 days on the safe side')
    ok('Sorted can’t tell you which is right for you' in c, 'it says what Sorted doesn’t know')
    pg.click('[data-a=panel][data-p=pksent]'); wait(pg); pg.click('form[data-f=pksent] button[type=submit]'); wait(pg)
    t = case(pg, T); pr = [x for x in t['promises'] if x['status'] == 'open']
    ok(t['pk']['stage'] == 'reps' and pr and 'must reply within 56 days' in pr[0]['said'] and pr[0]['dueAt'][:10] in (iso(d(56)), iso(d(55))), 'a formal challenge waits up to 56 days')
    pg.click('[data-a=panel][data-p=pkrej]') if pg.locator('[data-a=panel][data-p=pkrej]').count() else None
    if not pg.locator('form[data-f=pkrej]').count():
        poke(pg, T, "x.promises.filter(q=>q.status==='open')[0].dueAt=new Date(Date.now()-864e5).toISOString()"); open_case(pg, T)
        pg.click('[data-a=kept]'); wait(pg); pg.click('[data-a=panel][data-p=pkrej]'); wait(pg)
    pg.fill('#f-pkrj', iso(d(0))); pg.click('form[data-f=pkrej] button[type=submit]'); wait(pg)
    db = dates_block(pg); c = card(pg)
    ok('Appeal to the tribunal by' in db and day(d(27)) in db and 'independent tribunal' in c, 'a rejected formal challenge: the tribunal, 28 days')
    # 8 paid
    pg.click('[data-a=panel][data-p=pkpaid]'); wait(pg)
    ok(pg.input_value('#f-pkamt') == '£130', 'paying suggests the amount that applies now')
    pg.click('form[data-f=pkpaid] button[type=submit]'); wait(pg)
    t = case(pg, T)
    ok(t['board'] == 'done' and t['outcome'].startswith('Paid £130 on '), 'paying finishes the case: %s' % t['outcome'])
    # 9 a private parking charge
    P = ('ParkingEye Ltd PARKING CHARGE NOTICE Notice to Keeper Reference number: 1234567 Vehicle registration: YT19 ABC Car park: Aldi Lewisham '
         'Date of event: %s Parking charge amount: £100. Reduced to £60 if paid within 14 days. Appeals: POPLA.' % uk(d(-2)))
    start(pg, P)
    TP = 'ParkingEye parking charge · 1234567'
    db = dates_block(pg)
    ok('Appeal to ParkingEye by' in db and day(d(25)) in db, 'private charge: appeal to the company within 28 days')
    pg.click('[data-a=panel][data-p=pksent]'); wait(pg); pg.click('form[data-f=pksent] button[type=submit]'); wait(pg)
    poke(pg, TP, "x.promises.filter(q=>q.status==='open')[0].dueAt=new Date(Date.now()-864e5).toISOString()"); open_case(pg, TP)
    pg.click('[data-a=kept]'); wait(pg); pg.click('[data-a=panel][data-p=pkrej]'); wait(pg); pg.fill('#f-pkrj', iso(d(0))); pg.click('form[data-f=pkrej] button[type=submit]'); wait(pg)
    db = dates_block(pg)
    ok('Appeal to the independent appeals service by' in db and day(d(20)) in db, 'private rejection: the independent appeals service, on the safe side')
    # 10 cancelled
    start(pg, 'Got a parking ticket from Hackney Council, PCN HK11223344, £130, dated %s' % uk(d(-1)))
    pg.click('.pk-card [data-a=pk-cancelled]'); wait(pg)
    t = case(pg, 'Hackney PCN · HK11223344')
    ok(t and t['board'] == 'done' and t['outcome'] == 'Cancelled by Hackney', 'they cancelled it: finished')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
