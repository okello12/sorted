# v119 (docs/PLAN.md Phase 3, part 2). Drafts: what is typed in the start box or the guided form is kept on this phone
# until Start: a reload refills the box; leaving for Home shows "You started writing something" with Continue draft
# (the guided form refilled, focus in it) and Discard it; starting the case clears it; a draft over 7 days old is
# ignored; nothing is saved to the server until Start. The kind of case: under More, "Change the kind of case" offers
# the three kinds with the current one marked; changing a call case to a repair keeps the words, messages and history,
# adds the fix questions and the thing named, and the history says what changed; a repair to "your own task" opens
# your step; "Keep it as it is" changes nothing; a parking case has no such option.
import os, sys, json, datetime, time
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
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    case = lambda cid: [x for x in cases() if x['id'] == cid][0]
    labels = lambda cid: [e.get('label') or '' for e in case(cid)['events']]
    draft = lambda: pg.evaluate("(()=>{var k=Object.keys(localStorage).find(k=>k.startsWith('sorted.draft.'));return k?JSON.parse(localStorage.getItem(k)):null})()")
    def settle():
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
        if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
        if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.goto('https://sorted.test/#start'); wait(pg, 400)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    # ---- 1. a newcomer types, reloads, and the words are still there ----
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 400)
    pg.type('#f-case', 'The letting agent said they would send the deposit back by Friday, and I am still waiting'); wait(pg, 200)
    d = draft()
    ok(d and d['text'].startswith('The letting agent said') and not cases(), 'typing keeps a draft on this phone and saves nothing to the server')
    pg.reload(); wait(pg, 700)
    if not pg.locator('#f-case').count() and pg.locator('[data-cap82=other]').count(): pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 400)
    ok(pg.locator('#f-case').count() == 1 and pg.input_value('#f-case').startswith('The letting agent said'), 'after a reload the box still has the words')
    pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600); settle()
    cid = cases()[-1]['id']
    ok(draft() is None and case(cid)['title'], 'Start clears the draft and the case is made')
    # ---- 2. a returning person: the guided form, then Home, then Continue draft ----
    pg.goto('https://sorted.test/'); wait(pg, 500); pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.locator('[data-cap82=promise]').first.evaluate('e=>e.click()'); wait(pg, 400)
    pg.type('#gi-who', 'Aviva'); pg.type('#gi-what', 'call me back about the claim'); wait(pg, 200)
    d = draft()
    ok(d and d['gk'] == 'promise' and d['who'] == 'Aviva' and d['what'] == 'call me back about the claim', 'the guided form is kept as a draft with its choice')
    pg.locator('.bar [data-a=home]').first.click(); wait(pg, 500)
    ok(pg.locator('#gi-who').count() == 1 and pg.input_value('#gi-who') == 'Aviva' and pg.input_value('#gi-what') == 'call me back about the claim', 'a tap on Home keeps the form open with the words still in it')
    pg.reload(); wait(pg, 700); m = pg.inner_text('main')
    ok('You started writing something' in m and '“Aviva: call me back about the claim”' in m and 'Continue draft' in m and 'Discard it' in m, 'Home offers to continue or discard the draft')
    ok(len(cases()) == 1, 'nothing was saved to the server')
    pg.click('[data-a=draft-go]'); wait(pg, 500)
    ok(pg.locator('#gi-who').count() == 1 and pg.input_value('#gi-who') == 'Aviva' and pg.input_value('#gi-what') == 'call me back about the claim' and pg.evaluate("document.activeElement&&document.activeElement.id") == 'gi-what', 'Continue draft refills the guided form and puts focus in it')
    pg.click('form[data-f=gi] button[type=submit]'); wait(pg, 700); settle()
    cid2 = cases()[-1]['id']
    ok(case(cid2)['title'] in ('Aviva callback', 'Aviva: call me back about the claim') and draft() is None, 'the case starts from the draft and the draft goes (%r)' % case(cid2)['title'])
    # ---- 3. discard, and an old draft is ignored ----
    pg.goto('https://sorted.test/'); wait(pg, 500); pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 400); pg.type('#f-case', 'Something half typed'); wait(pg, 200)
    pg.reload(); wait(pg, 700)
    ok('“Something half typed”' in pg.inner_text('main'), 'after a reload the typed start is offered on Home')
    pg.click('[data-a=draft-drop]'); wait(pg, 400)
    ok(draft() is None and 'You started writing something' not in pg.inner_text('main'), 'Discard it drops the draft')
    pg.evaluate("(()=>{var k=Object.keys(localStorage).find(k=>k.startsWith('sorted.draft.'))||'sorted.draft.x';localStorage.setItem('sorted.draft.'+JSON.parse(localStorage.getItem('__mocksession')).user.id,JSON.stringify({text:'An old draft',at:Date.now()-8*86400000}))})()")
    pg.goto('https://sorted.test/'); wait(pg, 500)
    ok('An old draft' not in pg.inner_text('main'), 'a draft older than 7 days is not offered')
    pg.evaluate("Object.keys(localStorage).filter(k=>k.startsWith('sorted.draft.')).forEach(k=>localStorage.removeItem(k))")
    # ---- 4. change the kind of case ----
    pg.goto('https://sorted.test/?task=%s' % cid2); wait(pg, 600)
    pg.evaluate("document.querySelectorAll('details.case56-more').forEach(d=>d.open=true)")
    ok(pg.locator('[data-a=panel][data-p=kind]').count() == 1, 'More offers "Change the kind of case"')
    pg.click('[data-a=panel][data-p=kind]'); wait(pg, 300); m = pg.inner_text('main')
    ok('What kind of case is this?' in m and pg.locator('[data-k=kind][aria-pressed=true]').get_attribute('data-v') == 'call' and 'Keep it as it is' in m, 'the three kinds, the current one marked')
    pg.click('form[data-f=kind] button[type=submit]'); wait(pg, 400)
    ok(case(cid2)['mode'] == 'call' and not any('Changed the kind' in l for l in labels(cid2)), '"Keep it as it is" changes nothing')
    pg.evaluate("document.querySelectorAll('details.case56-more').forEach(d=>d.open=true)"); pg.click('[data-a=panel][data-p=kind]'); wait(pg, 300)
    pg.click('[data-k=kind][data-v=fix]'); wait(pg, 200)
    ok('Change it' in pg.inner_text('main') and 'who should fix it' in pg.inner_text('main'), 'picking another kind explains it and the button says Change it')
    n_ev = len(labels(cid2))
    pg.click('form[data-f=kind] button[type=submit]'); wait(pg, 500)
    c2 = case(cid2); m = pg.inner_text('main')
    ok(c2['mode'] == 'fix' and c2['fix'] and c2['fix']['step'] == 'what' and c2['title'] in ('Aviva callback', 'Aviva: call me back about the claim') and len(labels(cid2)) == n_ev + 1 and 'Changed the kind of case from “Someone else owes me the next move” to “Something needs fixing”.' in labels(cid2), 'a call case becomes a repair, keeping its words and history, and the history says so')
    ok('What is it?' in m or 'What’s happening' in m, 'the fix questions now lead')
    pg.evaluate("document.querySelectorAll('details.case56-more').forEach(d=>d.open=true)"); pg.click('[data-a=panel][data-p=kind]'); wait(pg, 300)
    pg.click('[data-k=kind][data-v=do]'); pg.click('form[data-f=kind] button[type=submit]'); wait(pg, 500)
    ok(case(cid2)['mode'] == 'do' and pg.locator('#moveform').count() == 1, 'your own task opens your step')
    # ---- 5. a parking case keeps its own flow ----
    pg.goto('https://sorted.test/'); wait(pg, 500); pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 400)
    pg.fill('#f-case', 'London Borough of Southwark PENALTY CHARGE NOTICE PCN Number: SK12345678 Vehicle Registration Mark: AB12 CDE Date of contravention: 30/09/2026 The penalty charge is £130.'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600); settle()
    for _ in range(3):
        if pg.locator('[data-a=cf-yes]').count(): pg.click('[data-a=cf-yes]'); wait(pg, 500)
        elif pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    cidp = cases()[-1]['id']; pg.goto('https://sorted.test/?task=%s' % cidp); wait(pg, 600)
    pg.evaluate("document.querySelectorAll('details.case56-more').forEach(d=>d.open=true)")
    ok(case(cidp).get('cf') and pg.locator('[data-a=panel][data-p=kind]').count() == 0, 'a parking notice offers no kind change')
    ok(not errs, 'no page errors')
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
