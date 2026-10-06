# v138 (the date model). A date Sorted shows must never claim more certainty than the words it came from. Four
# invariants, run through the reader and the interface:
#   1. A calculation never increases claimed certainty ("within 15 working days" stays "within 15 working days", with
#      Sorted's working shown as "about"; it is never a bare "By Tuesday 27 October").
#   2. No invented day: a vague phrase ("by the end of the week", "by the weekend", "in the next few days", "early next
#      week") is kept in their words, never shown as a firm day; "Thursday or Friday" is a window, not Thursday.
#   3. The day you choose to check is yours: it is never shown as the day they gave.
#   4. Nothing about a case changes without a tap (a pasted update is proposed first).
# Also: a promise saved before v138 says so; "Check the app" is a next action; the notice line in the record and the
# export appears only on parking cases.
import os, sys, datetime, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
today = datetime.date.today()
DAYNAME = re.compile(r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) \d{1,2} [A-Z][a-z]+')
READ = """(xs)=>xs.map(function(t){var r=window.__read,p=r.readCase(t,r.caseFacts(t));return p?{dueAt:p.dueAt,dueEnd:p.dueEnd,win:!!p.win,by:!!p.by,prec:p.prec,phrase:p.phrase||''}:null})"""
CALC = ['HMRC said they would reply within 15 working days', 'BT said an engineer will come within 3-5 working days',
        'Amazon said the refund will be processed in 3 to 5 working days', 'Argos said they would ring me in 48 hours',
        'Currys said the refund would be with me in 10 days']
VAGUE = ['Evri said my parcel will arrive by the end of the week', 'British Gas said they would sort it by the weekend',
         'Virgin said an engineer would come in the next few days', 'The landlord said the roofer would come early next week',
         'Octopus said they would sort the bill by the end of the month']
FIRM = ['My landlord said the plumber will come on Friday', 'Currys said the refund will arrive by 9 November',
        'BT said the engineer would come tomorrow between 8am and 1pm']
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.grant_permissions(['clipboard-read', 'clipboard-write'], origin='https://sorted.test')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/reader'), lambda r: r.fulfill(path=HERE + '/tests/out/reader.html', content_type='text/html'))
    ctx.route(lambda u: u.startswith('https://sorted.test/') and not u.startswith('https://sorted.test/reader'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    # ================= the reader =================
    pg.goto('https://sorted.test/reader'); wait(pg, 500)
    rc = pg.evaluate(READ, CALC)
    ok(all(r and r['prec'] == 'calc' and r['phrase'] for r in rc), 'invariant 1: a worked-out date is marked calc and keeps their words: %s' % [(r or {}).get('phrase') for r in rc])
    rv = pg.evaluate(READ, VAGUE)
    ok(all(r and r['prec'] == 'approx' and r['phrase'] for r in rv), 'invariant 2: a vague phrase is marked approx and keeps their words: %s' % [(r or {}).get('phrase') for r in rv])
    rt = pg.evaluate(READ, ['The garage said the car will be ready on Thursday or Friday'])[0]
    ok(rt and rt['win'] and rt['prec'] == 'window' and rt['phrase'] == 'on Thursday or Friday' and rt['dueEnd'], '“Thursday or Friday” is a window from Thursday to Friday, not Thursday')
    rf = pg.evaluate(READ, FIRM)
    ok(all(r and r['prec'] == 'day' for r in rf), 'a day they actually named is a day')
    rn = pg.evaluate(READ, ['The council said they will reply soon', 'Virgin said they will be in touch shortly', 'Aviva said they would call me back'])
    ok(rn == [None, None, None], 'no date at all: no date invented')
    # ================= the interface =================
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    case = lambda cid: [c for c in cases() if c['id'] == cid][0]
    tap = lambda a: (pg.locator('.tab129 [data-a=%s]' % a).click(), wait(pg, 500))
    def start(text, keep=True):
        tap('new-case'); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        sug = pg.inner_text('.sug') if pg.locator('.sug').count() else ''
        if keep and pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
        if pg.locator('[data-a=nudge-skip]').count(): pg.click('[data-a=nudge-skip]'); wait(pg, 300)
        return cases()[-1]['id'], sug
    def opencase(cid): pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700)
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')")
    pg.goto('https://sorted.test/#start'); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    # ---- a vague phrase, start to finish ----
    c1, sug = start('Evri said my parcel will arrive by the end of the week')
    ok('By the end of the week' in sug and 'They didn’t give a day' in sug and 'isn’t confirmed' in sug, 'the promise card keeps their words and says no day was given: %s' % sug[:200])
    p1 = [q for q in case(c1)['promises'] if q['status'] == 'open'][0]
    ok(p1.get('prec') == 'approx' and p1.get('phrase') == 'by the end of the week' and not p1.get('chk'), 'saved with how precise it is and their words')
    opencase(c1); m = pg.inner_text('main')
    ok('By the end of the week (about ' in m and 'They didn’t give a day' in m, 'the case shows their words first, Sorted’s reading second, marked “about”')
    now = pg.inner_text('.now137')
    ok('“by the end of the week”, no day given' in now and not DAYNAME.search(now), 'the Now card names no day as theirs: %s' % now)
    pg.goto('https://sorted.test/'); wait(pg, 600); home = pg.inner_text('main')
    line = [l for l in home.split('\n') if 'end of the week' in l.lower()]
    ok(line and all(('about' in l or 'no day' in l.lower()) or not DAYNAME.search(l) for l in line), 'Home never shows Sorted’s reading as their day: %s' % line)
    # ---- invariant 3: your check day is yours ----
    opencase(c1); pg.click('[data-a=panel][data-p=chk138]'); wait(pg, 300)
    ok('That isn’t a confirmed day, so the day Sorted asks you is your choice' in pg.inner_text('.chk138'), 'Choose when to check says the day is yours')
    chk = today + datetime.timedelta(days=12)
    pg.fill('#f-chkday', chk.isoformat()); pg.click('form[data-f=chk138] button[type=submit]'); wait(pg, 600)
    p1 = [q for q in case(c1)['promises'] if q['status'] == 'open'][0]
    ok(p1.get('chk') is True and p1.get('phrase') == 'by the end of the week' and p1['dueAt'][:10] in (chk.isoformat(), (chk - datetime.timedelta(days=1)).isoformat()), 'the check day is saved as yours, their words unchanged')
    m = pg.inner_text('main'); cday = '%s %d %s' % (chk.strftime('%A'), chk.day, chk.strftime('%B'))
    ok(('you’ll check on ' + cday) in m and ('promised it by ' + cday) not in m and ('They promised') not in m.replace('THEY PROMISED', ''), 'the case says you’ll check on that day, never that they promised it')
    ok(any(('You chose to check on ' + cday) in e['label'] for e in case(c1)['events']), 'the history says it was your choice')
    # ---- invariant 1 in the interface ----
    c2, sug = start('HMRC said they would reply within 15 working days')
    ok('Sorted worked this out from “within 15 working days”' in sug and 'It isn’t a day they gave' in sug, 'a worked-out date says it was worked out')
    opencase(c2); m = pg.inner_text('main')
    ok('Within 15 working days (about ' in m, 'the case leads with “Within 15 working days”, Sorted’s working after it')
    # ---- a window ----
    c3, sug = start('The garage said the car will be ready on Thursday or Friday')
    ok('between' in sug.lower() or 'Sometime between' in sug, 'Thursday or Friday is shown as a window: %s' % sug[:160])
    # ---- a firm day stays a firm day, with no extra words ----
    c4, sug = start('My landlord said the plumber will come on Friday')
    ok('They didn’t give a day' not in sug and 'about' not in sug, 'a named day is shown plainly')
    opencase(c4); ok(pg.locator('.aprx138, .leg138').count() == 0, 'no reading line and no older-version line on a new, firm promise')
    # ---- invariant 4: a pasted date is proposed, nothing changes until the tap ----
    opencase(c4); due0 = [q for q in case(c4)['promises'] if q['status'] == 'open'][0]['dueAt']
    pg.click('.now137 [data-a=panel][data-p=paste]'); wait(pg, 300)
    pg.fill('#f-paste', 'Sorry, the plumber will now come by the end of next week.'); pg.click('form[data-f=paste] button[type=submit]'); wait(pg, 600)
    ok([q for q in case(c4)['promises'] if q['status'] == 'open'][0]['dueAt'] == due0, 'invariant 4: a pasted update changes nothing by itself')
    # ---- a promise saved before v138 ----
    c5, _ = start('Amazon said they would refund £20 by %s' % (today + datetime.timedelta(days=9)).strftime('%d %B'))
    pg.goto('https://sorted.test/'); wait(pg, 500)
    pg.evaluate("(cid)=>{var db=JSON.parse(localStorage.getItem('__mockdb'));db.tasks.forEach(function(r){if(r.data.id===cid)r.data.promises.forEach(function(q){delete q.prec;delete q.phrase})});localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", c5)
    opencase(c5)
    ok('Saved before Sorted recorded where each date came from' in pg.inner_text('main'), 'a promise saved before v138 says so and asks you to check the date')
    # ---- Check the app ----
    c6, _ = start('Evri said check the app for updates on my parcel', keep=False)
    opencase(c6); now = pg.inner_text('.now137') if pg.locator('.now137').count() else ''
    ok('check Evri’s app or website for an update' in now and pg.locator('.now137 [data-a=chk-app]').count() == 1, '“Check the app” is the next action, with “I’ve checked their app”: %s' % now)
    pg.click('.now137 [data-a=chk-app]'); wait(pg, 300)
    ok('What does it say now?' in pg.inner_text('main') and pg.locator('#f-paste').count() == 1, 'it asks what the app says now, with the box and a screenshot button')
    # ---- the notice line only on notices ----
    opencase(c1); pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); wait(pg, 200)
    pg.click('[data-a=panel][data-p=pack]'); wait(pg, 400)
    doc = pg.inner_text('.pack') if pg.locator('.pack').count() else ''
    ok(pg.locator('.pack-doc').count() == 1 and 'estimate from the notice' not in pg.locator('.pack-doc').inner_html(), 'a case with no notice has no notice line in its record')
    ok('doesn’t give legal advice' in pg.content() and 'their words come first' in pg.content(), 'it still says Sorted doesn’t give legal advice, and how to read a date marked “about”')
    ok(not errs, 'no page errors: %s' % errs)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
