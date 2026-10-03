# v92: after Start. Every new case opens with what Sorted makes of it (what I understand, what to do next, what Sorted
# will remember, anything better avoided). Starts ask two questions at most, renewals propose a dated step, "Something
# else" is only the box. v93: a typed renewal gets a reminder to renew, and a case with no date asks for one. Then one case goes the whole way: promise, waiting, due, missed, chase, new promise, kept, done.
import os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
def db(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {'tasks': []}
def newest(pg): return sorted([x['data'] for x in db(pg)['tasks']], key=lambda x: x.get('created') or '')[-1]
def task(pg, cid): return next(x['data'] for x in db(pg)['tasks'] if x['data']['id'] == cid)
def home(pg): pg.goto('https://sorted.test/'); wait(pg, 600)
def choose(pg, k):
    if pg.locator('[data-a=gi-back]').count(): pg.click('[data-a=gi-back]'); wait(pg)
    pg.locator('[data-cap82=%s]' % k).first.click(); wait(pg, 500)
def poke(pg, js):
    pg.evaluate("(js)=>{var db=JSON.parse(localStorage.getItem('__mockdb'));(new Function('db',js))(db);localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", js)
def baseline(pg):
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count():
        pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 550)
def typed(pg, text):
    home(pg); choose(pg, 'other')
    pg.fill('#f-case', text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=pk-short-go]').count(): pg.click('[data-a=pk-short-go]'); wait(pg)
    baseline(pg)
def fr(pg): return pg.inner_text('.fr-card') if pg.locator('.fr-card').count() else ''
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    # 1 "Something else" is only the question, the box, the photo option and Start
    choose(pg, 'other')
    m = pg.inner_text('main')
    ok(pg.locator('#f-case').count() == 1 and 'What do you need to sort out?' in m and pg.locator('input[type=file][data-ocr=f-case]').count() == 1, 'something else: the question, the box and the photo option')
    ok(pg.locator('main img, main svg.art, main .art, [data-a=example]').filter(has_not_text='x').evaluate_all("els=>els.filter(e=>e.offsetParent!==null).length") == 0 and 'For example' not in m, 'with no artwork and no examples')
    # 2 the hard examples: each opens with what Sorted makes of it
    H = [
        ("Southwark PCN", "London Borough of Southwark PENALTY CHARGE NOTICE PCN Number: SK12345678 Vehicle Registration Mark: AB12 CDE Date of contravention: 30/09/2026 The penalty charge is £130. If paid within 14 days, reduced to £65.", ['parking ticket', 'Paying usually ends your chance to challenge']),
        ("landlord", "My landlord still hasn't fixed the damp in the bedroom. I reported it 3 weeks ago.", ['There’s damp or mould, and it’s your landlord’s job', 'Don’t stop paying rent']),
        ("Currys refund", "Currys said my refund of £89 would arrive within 5 working days, order 445566", ['Currys owes you money: £89', 'Check the promise Sorted found', 'voucher']),
        ("Washing machine", "My washing machine won't drain", ['Washing machine isn’t working', 'Answer the questions just below']),
        ("Lambeth council tax", "Got a letter from Lambeth Council saying I owe £240 council tax arrears and must pay by 20 October", ['Lambeth Council says you need to act by', 'Don’t let the date pass']),
        ("passport", "My passport expires in March", ['Your passport needs renewing', 'GOV.UK']),
        ("Aviva callback", "Aviva said they'd call me back about my home insurance claim within 48 hours, claim ref HC-77812", ['You need Aviva to do something', 'Check the promise Sorted found']),
        ("BT", "BT broadband has been down for a week and they keep saying an engineer will come", ['You need BT to do something', 'They haven’t given you a date yet']),
    ]
    for title, text, want in H:
        typed(pg, text); t = newest(pg); f = fr(pg)
        ok(title.lower() in t['title'].lower() and all(w in f for w in want) and 'What Sorted will remember' in f, '%s: %s' % (title, t['title']))
    # a renewal typed in: no call form, a reminder to renew for you to confirm, nothing added until you do
    typed(pg, "My driving licence expires on 24 November")
    t = newest(pg)
    ok(pg.locator('form[data-f=call]').count() == 0 and pg.locator('[data-a=fr-renew]').count() == 1, 'typed renewal: no call form, a reminder to renew instead')
    pg.click('[data-a=fr-renew]'); wait(pg)
    vals = pg.locator('#moveform input, #moveform textarea').evaluate_all("els=>els.map(e=>e.value).join('|')")
    ok(pg.locator('#moveform').count() == 1 and 'Renew my driving licence' in vals and not (newest(pg).get('moves') or []), 'it proposes "Renew my driving licence" and adds nothing yet: %s' % vals[:80])
    pg.click('#moveform button[type=submit]'); wait(pg)
    mv = (newest(pg).get('moves') or [{}])[-1]
    ok(mv.get('what', '').startswith('Renew my driving licence') and mv.get('dueAt', '')[5:10] in ('11-23', '11-24'), 'confirmed, it is due by the expiry date: %s %s' % (mv.get('what'), mv.get('dueAt')))
    # no date yet: get one, and the message asks for it
    typed(pg, "BT broadband has been down for a week and they keep saying an engineer will come")
    ok('Ask BT for a date for the engineer' in fr(pg), 'no date yet: the next step is to get one')
    ask = pg.input_value('#f-ask') if pg.locator('#f-ask').count() else ''
    ok('Please give me a date for the engineer' in ask, 'and the message asks for it: %s' % ask[-70:])
    t = newest(pg)
    lam = next(x['data'] for x in db(pg)['tasks'] if 'Lambeth' in x['data']['title'])
    ok(not lam.get('sugP'), 'a demand on you is not proposed as their promise')
    # the card goes once read, and stays gone
    pg.click('[data-a=fr-ok]'); wait(pg)
    ok(pg.locator('.fr-card').count() == 0 and not newest(pg).get('frNew'), '"Got it" puts it away')
    pg.reload(); wait(pg, 600); ok(pg.locator('.fr-card').count() == 0, 'and it stays away')
    # the deadline gets its own reminder offer
    pg.goto('https://sorted.test/?task=%s' % lam['id']); wait(pg, 700)
    if pg.locator('[data-a=fr-remind]').count():
        pg.click('[data-a=fr-remind]'); wait(pg)
        vals = pg.locator('#moveform input, #moveform textarea').evaluate_all("els=>els.map(e=>e.value).join('|')")
        ok(pg.locator('#moveform').count() == 1 and 'Lambeth' in vals, '"Remind me before" opens your own step, for you to confirm')
    else: ok(False, 'the council letter offers a reminder before its date')
    ok(len(task(pg, lam['id']).get('moves') or []) == 0, 'nothing is added until you confirm')
    # 3 renewals: what and when, then a dated step to confirm
    home(pg); choose(pg, 'renew')
    ok(pg.locator('input[name=gi-item]').count() == 6 and pg.locator('#gi-when').count() == 1, 'renew: what and when')
    pg.click('label.gi-chip:has-text("Passport")'); pg.fill('#gi-when', '12 March')
    pg.click('form[data-f=gi] button[type=submit]'); wait(pg, 700)
    t = newest(pg)
    ok(t['mode'] == 'do' and t['title'] == 'Renew my passport' and pg.locator('#moveform').count() == 1, 'renew: a case of your own, with the step ready to confirm')
    ok('something you need to do yourself' in fr(pg), 'and it says it is yours to do')
    # 4 the whole life of a case: promise, waiting, due, missed, chase, new promise, kept, done
    home(pg); choose(pg, 'promise')
    pg.fill('#gi-who', 'Currys'); pg.fill('#gi-what', 'refund my £89 by Friday, ref 445566')
    pg.click('form[data-f=gi] button[type=submit]'); wait(pg, 600); baseline(pg)
    cid = newest(pg)['id']
    ok(pg.locator('.fr-card').count() == 1, 'new problem: the first response is there')
    ok(pg.locator('.gi-form input[type=text], .gi-form textarea').count() == 0, 'two questions were enough')
    pg.click('[data-a=sug-yes]'); wait(pg)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 150)
    t = task(pg, cid); q = t['promises'][-1]
    ok(q['status'] == 'open' and q.get('dueAt'), 'promise confirmed, with its date')
    ok(pg.locator('.fr-card').count() == 0, 'the first response steps aside once the promise is held')
    home(pg)
    ok('Waiting' in pg.inner_text('main') and 'Currys' in pg.inner_text('main'), 'waiting: on Home under Waiting')
    poke(pg, "var x=db.tasks.find(y=>y.data.id==='%s').data;x.promises.forEach(q=>{if(q.status==='open')q.dueAt=new Date(Date.now()-864e5).toISOString()})" % cid)
    home(pg)
    sec = pg.evaluate("(id)=>{var e=document.querySelector('[data-id=\"'+id+'\"]');while(e&&!/^(section|details)$/i.test(e.tagName))e=e.parentElement;return e?e.innerText.slice(0,60):''}", cid)
    ok('needs you' in sec.lower() or pg.locator('.home44-spot [data-id="%s"], [data-id="%s"].home44-spot' % (cid, cid)).count() > 0, 'due: it moves to Needs you (%s)' % sec[:30].replace('\n', ' '))
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700)
    ok(pg.locator('[data-a=missed]').count() >= 1 and pg.locator('[data-a=kept]').count() >= 1, 'due: the case asks whether it happened')
    pg.locator('[data-a=missed]').first.click(); wait(pg)
    ok(task(pg, cid)['promises'][-1]['status'] == 'missed' and pg.locator('form[data-f=call]').count() == 1, 'missed: recorded, and the chase is ready')
    ask = pg.input_value('#f-ask')
    ok('445566' in ask or 'refund' in ask.lower(), 'the chase quotes what they said: %s' % ask[:80])
    pg.click('form[data-f=call] button[type=submit]'); wait(pg)
    ok(any('chase' in e['label'].lower() or 'message' in e['label'].lower() or 'call' in e['label'].lower() or 'follow-up' in e['label'].lower() for e in task(pg, cid)['events'][-3:]), 'chase: logged on the case')
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600)
    pg.click('[data-a=panel][data-p=promise]'); wait(pg)
    pg.fill('#f-said', 'The refund will be processed'); pg.click('[data-k=when][data-v=by]'); wait(pg, 150)
    dd = datetime.date.today() + datetime.timedelta(days=3)
    for part, v in [('d', dd.day), ('m', dd.month), ('y', dd.year)]: pg.select_option('select[data-dp=f-date][data-part=%s]' % part, str(v))
    pg.click('form[data-f=promise] button[type=submit]'); wait(pg)
    t = task(pg, cid)
    ok(len(t['promises']) == 2 and t['promises'][-1]['status'] == 'open', 'a new promise after the chase')
    poke(pg, "var x=db.tasks.find(y=>y.data.id==='%s').data;x.promises.forEach(q=>{if(q.status==='open')q.dueAt=new Date(Date.now()-3600e3).toISOString()})" % cid)
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700)
    pg.locator('[data-a=kept]').first.click(); wait(pg)
    t = task(pg, cid)
    ok(t['promises'][-1]['status'] == 'kept', 'kept: recorded')
    if t['board'] != 'done':
        ok('Has all of it arrived?' in pg.inner_text('main'), 'kept: the refund playbook asks if all of it arrived (v98)')
        if pg.locator('[data-a=pb-go]').count(): pg.locator('[data-a=pb-go]').first.click(); wait(pg)
        if pg.locator('#f-outcome').count() and not pg.input_value('#f-outcome'): pg.fill('#f-outcome', 'Refund arrived')
        for sel in ['text=Mark it done']:
            if pg.locator(sel).count(): pg.locator(sel).first.click(); wait(pg); break
        if pg.locator('form[data-f=outcome]').count(): pg.click('form[data-f=outcome] button[type=submit]'); wait(pg)
    t = task(pg, cid)
    ok(t['board'] == 'done', 'resolved: the case is done (%s)' % t['board'])
    home(pg)
    ok('Done' in pg.inner_text('main'), 'and Home shows it under Done')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'nothing scrolls sideways')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
