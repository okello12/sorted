# v140 (the second walkthrough). A duration is counted from when they told you, and an unclear count is a choice:
#   - "last Wednesday … within ten working days" is read from that Wednesday, not today, with two readings (Wednesday
#     counted as day one, or counting from the next working day) and "Which should Sorted use?"; no confirmed deadline
#     until a tap; "I’m not sure" opens the check day; a told sentence on its own ("That was last Wednesday.") counts too;
#     "would take 3 to 5 working days" is a calculation, "refunds take 3 to 5 days" is still information;
#   - the words and the date are said apart: never "Found in the message" for a date Sorted worked out;
#   - one next action: the case and Home say the same thing ("check Evri’s app", "say which day");
#   - "Shop name not in front of me" is not a name; the company stays unknown;
#   - a half-written reminder survives the Home button, which says it was kept;
#   - a guest's case says "Saved to Sorted…", never "Saved to your account".
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
told = today - datetime.timedelta(days=((today.weekday() - 2) % 7) or 7)   # last Wednesday
yday = today - datetime.timedelta(days=1)
READ = """(xs)=>xs.map(function(t){var r=window.__read,p=r.readCase(t,r.caseFacts(t));return p?{dueAt:p.dueAt,dueEnd:p.dueEnd,win:!!p.win,prec:p.prec,phrase:p.phrase||'',told:p.told||'',toldPh:p.toldPh||'',alt:p.alt||'',altB:p.altB||'',party:p.party||''}:null})"""
ymd = lambda d: d.strftime('%Y-%m-%d')
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/reader'), lambda r: r.fulfill(path=HERE + '/tests/out/reader.html', content_type='text/html'))
    ctx.route(lambda u: u.startswith('https://sorted.test/') and not u.startswith('https://sorted.test/reader'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    # ================= the reader =================
    pg.goto('https://sorted.test/reader'); wait(pg, 500)
    exp = pg.evaluate("(t)=>{var r=window.__read,a=t.split('-').map(Number),d=new Date(a[0],a[1]-1,a[2]);return [r.ymdL(r.wdFrom(d,9)),r.ymdL(r.wdFrom(d,10))]}", ymd(told))
    S = ['The shop said last Wednesday the £40 refund should be back within ten working days',
         'Last Wednesday the shop said the £40 refund should be back within ten working days',
         'They said the £40 refund should be back within ten working days. That was last Wednesday.']
    for s, r in zip(S, pg.evaluate(READ, S)):
        ok(r and r['prec'] == 'calc' and r['told'] == ymd(told) and r['alt'] == exp[0] and r['altB'] == exp[1] and r['phrase'] == 'within ten working days',
           'counted from last Wednesday (%s), two readings %s: %r -> %s' % (ymd(told), exp, s, r and (r['told'], r['alt'], r['altB'])))
    r = pg.evaluate(READ, ['Currys told me yesterday the refund would take 3 to 5 working days'])[0]
    ok(r and r['prec'] == 'calc' and r['told'] == ymd(yday) and r['win'] and r['phrase'] == 'take 3 to 5 working days' and r['party'] == 'Currys', '“told me yesterday … would take 3 to 5 working days” is a window counted from yesterday, in their words: %s' % r)
    r = pg.evaluate(READ, ['Currys said the refund will take 5 working days', 'BT said refunds take 3 to 5 days.', 'They said they would come last Friday but nobody came'])
    ok(r[0] and r[0]['prec'] == 'calc' and not r[0]['told'], '“will take 5 working days” is a calculation from today')
    ok(r[1] is None, '“refunds take 3 to 5 days” is still information, not a promise')
    ok(r[2] and not r[2]['told'] and r[2]['prec'] == 'day', 'a missed visit “last Friday” is unchanged (a day, not a told date)')
    # ================= the interface =================
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    case = lambda cid: [c for c in cases() if c['id'] == cid][0]
    openp = lambda cid: [q for q in case(cid)['promises'] if q['status'] == 'open']
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
    def fday(y):
        d = datetime.date.fromisoformat(y); return d.strftime('%A ') + str(d.day) + d.strftime(' %B')
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')")
    pg.goto('https://sorted.test/#start'); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    # ---- the told date, start to finish ----
    c1, sug = start('The shop said last Wednesday the £40 refund should be back within ten working days')
    A, B, W = fday(exp[0]), fday(exp[1]), fday(ymd(told))
    ok('When you were told: ' + W in sug and 'Exact deadline: not confirmed' in sug and A in sug and B in sug, 'the proposal shows when you were told, both readings and no confirmed deadline: %s' % sug[:400])
    ok(not ('Found in the message' in sug and 'worked' in sug), 'the proposal never says a worked-out date was found in the message')
    pr = openp(c1)[0]
    ok(pr.get('told') == ymd(told) and pr.get('alt') == exp[0] and pr.get('altB') == exp[1] and not pr.get('dpick'), 'the promise keeps when you were told and both readings, nothing chosen')
    opencase(c1); m = pg.inner_text('main')
    ok('Which should Sorted use?' in m and pg.locator('[data-a=calc-pick]').count() == 3 and 'I’m not sure' in m, 'the case asks which day to use, with both days and “I’m not sure”')
    ok('Exact deadline: not confirmed' in m and 'Due by the end of' not in m, 'the case shows no confirmed deadline: %s' % m[m.find('Waiting for'):][:900])
    now = pg.inner_text('.now137')
    ok('say which day Sorted should use' in now and A not in now and B not in now, 'the Now card asks you to choose, naming no day as theirs: %s' % now)
    tap('go-home'); home = pg.inner_text('main')
    ok('Sorted’s working' in home or 'say which day' in home.lower(), 'Home shows the dates as Sorted’s working, not their deadline')
    opencase(c1); pg.locator('[data-a=calc-pick][data-v=alt]').click(); wait(pg, 600)
    pr = openp(c1)[0]
    ok(pr.get('dpick') == 'alt' and pr['dueAt'][:10] in (exp[0], ymd(datetime.date.fromisoformat(exp[0]) - datetime.timedelta(days=1))), 'tapping the first day makes it the deadline: %s' % pr['dueAt'])
    m = pg.inner_text('main')
    ok('Exact deadline: ' + A + ', the day you chose' in m and pg.locator('[data-a=calc-pick]').count() == 0, 'the case says it is the day you chose, and stops asking')
    ok(any('You chose ' + A in (e.get('label') or '') for e in case(c1)['events']), 'the history says which day you chose and what Sorted had worked out')
    # "I'm not sure" opens your check day
    c2, _ = start('They said the £40 refund should be back within ten working days. That was last Wednesday.')
    opencase(c2); pg.locator('[data-a=calc-pick][data-v=unsure]').click(); wait(pg, 400)
    ok(pg.locator('#f-chkday').count() == 1 and pg.input_value('#f-chkday') == exp[1] and not openp(c2)[0].get('dpick'), '“I’m not sure” opens “When do you want to check?” at the later day, choosing nothing')
    # ---- one next action ----
    c3, _ = start('Evri told me to track the parcel on their app')
    opencase(c3); now = pg.inner_text('.now137').lower()
    tap('go-home'); home = pg.inner_text('main').lower()
    ok('check evri’s app or website for an update' in now and 'check evri’s app or website for an update' in home and 'get the call ready' not in home, 'the case and Home name the same next action: %s' % now)
    # ---- an unknown name stays unknown ----
    tap('new-case'); pg.locator('[data-cap82=promise]').first.evaluate('e=>e.click()'); wait(pg, 400)
    pg.fill('#gi-who', 'Shop name not in front of me'); pg.fill('#gi-what', 'They said the £40 refund should be back within ten working days')
    pg.click('form[data-f=gi] button[type=submit]'); wait(pg, 700)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    m = pg.inner_text('main'); c4 = cases()[-1]
    ok('not in front of me' not in (c4.get('title') or '').lower() and not (c4.get('facts') or {}).get('party') and 'said they would They said' not in (c4.get('said') or ''), 'the company stays unknown and the sentence reads right: %r / %r' % (c4.get('title'), c4.get('said')))
    ok('not in front of me' not in m.lower(), '“Shop name not in front of me” is never shown as a name')
    # ---- a half-written reminder survives Home ----
    opencase(c1); pg.click('[data-a=panel][data-p=move]'); wait(pg, 300); pg.type('#f-mwhat', 'Send them the receipt'); wait(pg, 200)
    tap('go-home'); wait(pg, 200)
    ok('Kept what you were writing' in (pg.inner_text('#toast') or ''), 'Home says the half-written reminder was kept')
    opencase(c1); m = pg.inner_text('main')
    ok('You were writing something here.' in m and 'Send them the receipt' in m, 'the case offers the reminder back')
    pg.click('[data-a=keep-go]'); wait(pg, 400)
    ok(pg.locator('#f-mwhat').count() == 1 and pg.input_value('#f-mwhat') == 'Send them the receipt', '“Carry on writing” brings the words back')
    # ---- a guest's case ----
    sync = pg.inner_text('main .sync114') if pg.locator('main .sync114').count() else ''
    ok(sync == 'Saved to Sorted. You can reopen this case on this browser. Add an email to open it on another device.', 'a guest’s case says where it is saved: %r' % sync)
    ok('Saved to your account' not in pg.inner_text('body'), 'a guest never sees “Saved to your account”')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
