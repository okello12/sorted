# v105: fixes from the independent assurance review (3 Oct 2026), as permanent invariants.
# SEM-01 a thing ruled out never becomes the thing; SEM-02 names of up to six words with digits and hyphens survive as
# typed; SAFE-01/02 more household hazards stop for safety, negated ones don't; DATE-01/02/03 working-day ranges, UK-wide
# bank holidays and "next week" from a weekend; MOV-01 a reference alone stays "In touch"; MOV-02 moving a case between
# moves asks first; PRIV-01 a failed switch-off keeps the link and says so; STATE-01 sign-out leaves no copy of cases;
# CONTENT-01 no "hold them to it".
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    rd = ctx.new_page(); rd.route(lambda u: u.startswith('https://sorted.test/'), lambda q: q.fulfill(path=HERE + '/tests/out/reader.html', content_type='text/html'))
    rd.goto('https://sorted.test/'); wait(rd, 500)
    R = lambda t: rd.evaluate("(t)=>{var R=__read,f=R.caseFacts(t),s=R.readCase(t,f);return {item:f.item||'',ref:f.ref||'',thing:R.thingOf(t),unsafe:R.looksUnsafe(t),sug:s?{due:s.dueAt}:null}}", t)
    # SEM-01: negation scope
    for t, gone, want in [("The boiler isn't broken, it's the thermostat.", 'boiler', 'Thermostat'), ("It's not my router. The modem is broken.", 'router', 'Modem'),
                          ("The screen isn't cracked; the hinge is.", 'screen', 'Hinge'), ("Nothing is wrong with the boiler, but the thermostat has died.", 'boiler', 'Thermostat'),
                          ("The boiler is fine, the radiator is leaking.", 'boiler', 'Radiator')]:
        r = R(t); ok(r['thing'] == want and gone not in (r['thing'] + r['item']).lower() and not ('Heating' in r['item'] and gone == 'boiler' and want != 'Radiator'), 'ruled out stays out: %s -> %r / %r' % (t, r['thing'], r['item']))
    r = R("The boiler is broken, it isn't the thermostat"); ok(r['thing'] == 'Boiler', 'and the thing that is broken stays: boiler, not the thermostat')
    # SEM-02: names survive as typed, generated 1 to 6 words with digits, hyphens and apostrophes
    names = ['flux capacitor', 'temporal carbon flux capacitor', 'Wi-Fi 6 router', 'flux-capacitor', 'ZX-81 turbo flux regulator', 'Bosch Serie 4 dishwasher', 'Hive thermostat', 'nan\'s old Singer sewing machine', 'iPhone 15 Pro', 'A-frame loft ladder mechanism']
    lost = []
    for nm in names:
        for form in ['My {N} is broken.', 'The {N} has stopped working', 'Problem with my {N}', 'my {N} keeps breaking']:
            t = form.replace('{N}', nm); th = R(t)['thing']
            if th.lower() != nm.lower(): lost.append('%s -> %r' % (t, th))
    ok(not lost, 'names of 1 to 6 words survive exactly (%d checked): %s' % (len(names) * 4, lost[:5]))
    ok(R('My Wi-Fi 6 router is broken.')['thing'] == 'Wi-Fi 6 router' and R('my ZX-81 turbo flux regulator is broken')['thing'] == 'ZX-81 turbo flux regulator', 'and keep their capitals')
    ok(R('The man from the council is coming Tuesday')['thing'] == '' and R('My refund from Currys is late')['thing'] == '', 'people and money are still never things')
    # SAFE-01 and SAFE-02
    for t in ["The socket is crackling.", "the plug is buzzing and smells hot", "The cable is frayed and copper is showing.", "there are bare wires hanging out of the wall", "The carbon monoxide alarm is sounding.", "the CO alarm keeps going off", "water dripping through the ceiling light", "I got a tingle when I touched the switch", "The plug is sparking", "I can smell gas near the boiler"]:
        ok(R(t)['unsafe'], 'safety stop: %s' % t)
    for t in ["I can't smell gas.", "I cannot smell any burning", "There's no gas smell, I checked.", "There is no smoke or burning smell", "The fridge is buzzing", "no sparks, it just won't start", "I didn't see any smoke"]:
        ok(not R(t)['unsafe'], 'not a hazard: %s' % t)
    # DATE-01/02/03 against fixed starting days
    D = lambda txt, base: rd.evaluate("([t,b])=>{var w=__read.parseWhen(t,new Date(b+'T09:00:00'));return w?w.date:null}", [txt, base])
    W = lambda base, k: rd.evaluate("([b,k])=>__read.ymdL(__read.wdFrom(new Date(b+'T09:00:00'),k))", [base, k])
    ok(D('arrive within 2-4 working days', '2026-10-03') == '2026-10-08', 'Sat 3 Oct + 2-4 working days: Thu 8 Oct (%s)' % D('arrive within 2-4 working days', '2026-10-03'))
    ok(D('arrive within 4 working days', '2026-10-03') == D('arrive within 2-4 working days', '2026-10-03') == D('arrive in 2 to 4 business days', '2026-10-03'), 'a range uses the same working-day count as a single number')
    for base, k, want in [('2026-10-05', 1, '2026-10-06'), ('2026-10-09', 1, '2026-10-12'), ('2026-10-30', 2, '2026-11-03'), ('2026-12-24', 2, '2026-12-30'), ('2026-12-23', 4, '2026-12-31'), ('2027-03-25', 1, '2027-03-29'), ('2027-12-24', 1, '2027-12-29'), ('2028-12-22', 3, '2028-12-29')]:
        ok(W(base, k) == want, '%s + %d working days = %s (bank holidays skipped): %s' % (base, k, want, W(base, k)))
    for base, want in [('2026-10-03', '2026-10-09'), ('2026-10-04', '2026-10-09'), ('2026-10-05', '2026-10-16'), ('2026-10-09', '2026-10-16')]:
        ok(D('sometime next week', base) == want, '"next week" said on %s ends %s (%s)' % (base, want, D('sometime next week', base)))
    rd.close()
    # the interface
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    rows = lambda: [x['data'] for x in dbj().get('tasks', [])]
    moms = lambda: [x for x in rows() if x.get('kind') == 'moment']
    cases = lambda: [x for x in rows() if x.get('kind') != 'moment']
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    ok('hold them to' not in pg.content(), 'the page never says Sorted will "hold them to it"')
    # CO alarm: the safety stop says what to do about carbon monoxide
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg)
    pg.fill('#f-case', 'The carbon monoxide alarm is sounding in the hall'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg)
    ok('Carbon monoxide alarm going off?' in pg.inner_text('main') and '0800 111 999' in pg.inner_text('main'), 'a CO alarm reaches the safety stop, with what to do')
    def move(days):
        pg.goto('https://sorted.test/'); wait(pg, 600)
        e = pg.locator('[data-a=mom-start]')
        if e.count(): e.first.evaluate('e=>e.click()')
        else: pg.evaluate("location.hash=''"); pg.locator('[data-a=mom-new]').first.evaluate('e=>e.click()')
        wait(pg, 500)
        if not pg.locator('#mv-date').count(): pg.locator('[data-a=mom-new]').first.evaluate('e=>e.click()'); wait(pg, 400)
        pg.fill('#mv-date', (datetime.date.today() + datetime.timedelta(days=days)).isoformat()); pg.click('form[data-f=mom] button[type=submit]'); wait(pg)
        return [m for m in moms() if m['date'] == (datetime.date.today() + datetime.timedelta(days=days)).isoformat()][0]['id']
    m1 = move(20)
    # MOV-01: a reference alone is not a promise
    n0 = len(cases())
    pg.locator('.cap99-item', has_text='Broadband').first.locator('[data-a=mom-case]').click(); wait(pg)
    pg.fill('#gi-what', "I spoke to Virgin. They gave me reference V123. They haven't promised anything yet."); pg.click('.cap103-said button[type=submit]'); wait(pg, 600)
    st = [m for m in moms() if m['id'] == m1][0]['items'].get('broadband', {})
    ok(len(cases()) == n0 and st.get('st') == 'contacted' and 'V123' in st.get('said', ''), 'a reference with no promise stays "In touch", the reference kept in their words')
    # a real promise makes the case, to use below
    pg.locator('.cap99-item', has_text='Broadband').first.locator('[data-a=mom-case]').click(); wait(pg)
    pg.fill('#gi-what', 'Virgin will install on Tuesday ref V123'); pg.click('.cap103-said button[type=submit]'); wait(pg, 700)
    cid = [c for c in cases() if 'install on Tuesday' in (c.get('said') or '')][0]['id']
    # MOV-02: moving it to another move asks first
    m2 = move(60)
    pg.click('[data-a=mom-panel][data-p=link]'); wait(pg)
    ok('part of Moving home on' in pg.inner_text('main'), 'the list says which move a case is already in')
    pg.locator('[data-a=mom-link][data-id="%s"]' % cid).click(); wait(pg)
    c = [x for x in cases() if x['id'] == cid][0]
    ok(c.get('momentId') == m1 and 'Tap it again to move it here' in pg.inner_text('main'), 'the first tap only asks; the case stays where it was')
    pg.locator('[data-a=mom-link][data-id="%s"]' % cid).click(); wait(pg)
    ok([x for x in cases() if x['id'] == cid][0].get('momentId') == m2 and not [m for m in moms() if m['id'] == m1][0]['items'].get('broadband', {}).get('caseId'), 'the second tap moves it, and the first move lets it go')
    # PRIV-01: a switch-off the server refuses keeps the link, and says so (a case and a move)
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
    if not pg.locator('details.case56-sharing').count() and pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 400)
    pg.evaluate("document.querySelector('details.case56-sharing').open=true"); pg.click('[data-a=share]'); wait(pg, 600)
    tok = [s for s in dbj().get('shares', []) if s['task_id'] == cid][0]['token']
    pg.evaluate("localStorage.setItem('__failShareDelete','1')")
    pg.click('[data-a=unshare]'); wait(pg, 500)
    sh = [s for s in dbj().get('shares', []) if s['task_id'] == cid]
    ok(sh and [x for x in cases() if x['id'] == cid][0].get('shareToken') == tok and 'Couldn’t switch the link off' in pg.inner_text('body'), 'case: a refused switch-off keeps the link on, and says it couldn’t')
    v = ctx.new_page(); v.goto('https://sorted.test/?share=%s' % tok); wait(v, 700)
    ok('doesn’t open' not in v.inner_text('main'), 'and the page still shows the link as working, because it is')
    pg.evaluate("localStorage.removeItem('__failShareDelete')"); pg.click('[data-a=unshare]'); wait(pg, 500)
    ok(not [s for s in dbj().get('shares', []) if s['task_id'] == cid], 'once the server agrees, it is off')
    v.reload(); wait(v, 700); ok('doesn’t open' in v.inner_text('main'), 'and the old link shows nothing')
    pg.goto('https://sorted.test/'); wait(pg, 500); pg.locator('.cap99-row').first.click(); wait(pg)
    mid = [m for m in moms() if m.get('id') in (m1, m2)]
    pg.evaluate("document.querySelector('details.cap104-share').open=true"); pg.click('[data-a=mom-share]'); wait(pg, 600)
    pg.evaluate("localStorage.setItem('__failShareDelete','1')"); pg.click('[data-a=mom-unshare]'); wait(pg, 500)
    ok(len(dbj().get('shares', [])) == 1 and any(m.get('shareToken') for m in moms()) and 'Couldn’t switch the link off' in pg.inner_text('body'), 'move: a refused switch-off keeps the link on, and says it couldn’t')
    pg.evaluate("localStorage.removeItem('__failShareDelete')")
    # STATE-01: sign-out leaves no copy of anyone's cases on the phone
    pg.evaluate("localStorage.setItem('sorted.carry', JSON.stringify([{title:'Virgin broadband'}]))")
    ok(any('install on Tuesday' in (pg.evaluate("localStorage.getItem(%s)" % json.dumps(k)) or '') for k in pg.evaluate("Object.keys(localStorage)") if k.startswith('sorted.')), 'before sign-out the cache holds the cases')
    pg.evaluate("document.body.insertAdjacentHTML('beforeend','<button data-a=\"signout\" id=\"so\">x</button>');document.getElementById('so').click()"); wait(pg, 800)
    left = [k for k in pg.evaluate("Object.keys(localStorage).concat(Object.keys(sessionStorage))") if k.startswith('sorted.') and any(w in (pg.evaluate("localStorage.getItem(%s)||sessionStorage.getItem(%s)" % (json.dumps(k), json.dumps(k))) or '') for w in ('install on Tuesday', 'Virgin', 'carbon monoxide', 'Moving home'))]
    ok(not left, 'after sign-out no stored copy of a case or move is left: %s' % left)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
