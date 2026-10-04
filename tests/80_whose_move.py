# v123 (remediation Phase A items 4 and 6). Whose move: the question is "Whose move is it now?" with Mine, Theirs and
# Both; it can be asked again from What Sorted understood on any open call case; an answer that conflicts with an open
# step of yours changes nothing until the person chooses "Keep my step as well" or "Mark my step no longer needed";
# "Leave it as it was" leaves everything; their promise is never touched by the answer. The landing page: the headline,
# then the one explanation, the kinds of matter, one primary button above the fold, and the same description on a
# newcomer's Home.
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
EXPLAIN = 'Keep the details, promises, deadlines and next steps of life’s unfinished business in one place. Sorted shows what needs you, what you’re waiting for and when to follow up.'
KINDS = 'Refunds · repairs · parking notices · claims · important calls · moving home'
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    case = lambda cid: [x for x in cases() if x['id'] == cid][0]
    labels = lambda cid: [e.get('label') or '' for e in case(cid)['events']]
    main = lambda: pg.inner_text('main')
    def u():
        pg.evaluate("document.querySelectorAll('details.case117-u').forEach(d=>d.open=true)"); return pg.inner_text('details.case117-u') if pg.locator('details.case117-u').count() else ''
    # ---- 0. the landing page ----
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.goto('https://sorted.test/'); wait(pg, 700)
    hero = pg.inner_text('.hero')
    ok('Keep everyday admin moving.' in hero and 'Parking notices, delayed refunds, repairs and confusing letters.' in hero, 'the landing page leads with the everyday problem (v126 replaced the v123 headline)')
    ok(pg.get_attribute('meta[name=description]', 'content').startswith('Keep everyday admin moving.'), 'the page description matches')
    pg.goto('https://sorted.test/#start'); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    ok('Keep everyday admin moving.' in main(), 'a newcomer’s Home carries the same description')
    # ---- 1. a case with their promise: no question; "Say whose move it is" re-asks with the new wording ----
    fri = datetime.date.today() + datetime.timedelta(days=(4 - datetime.date.today().weekday()) % 7 or 7)
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.fill('#f-case', 'Currys said they would refund £89 by %s, order 445566' % fri.strftime('%A')); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
    if pg.locator('[data-a=goal-skip]').count(): pg.click('[data-a=goal-skip]'); wait(pg, 300)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    cid = cases()[-1]['id']; pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600)
    ok('Whose move is it now?' not in main() and 'Whose move\nTheirs: Currys said they would' in u(), 'a promise answers whose move; no question')
    ok(pg.locator('[data-a=turn-reset]').count() == 1 and pg.locator('[data-a=turn-reset]').inner_text() == 'Say whose move it is', 'What Sorted understood offers to say whose move it is')
    pg.click('[data-a=turn-reset]'); wait(pg, 300); m = main()
    ok('Whose move is it now?' in m and 'Mine: Currys asked me for something' in m and 'Theirs: I’m waiting for Currys' in m and 'Both' in m and 'Leave it as it is' in m, 'the question, with Mine, Theirs, Both and a way to leave it')
    n_ev = len(labels(cid)); pr = case(cid)['promises']
    pg.click('[data-a=turn-leave]'); wait(pg, 300)
    ok('Whose move is it now?' not in main() and len(labels(cid)) == n_ev and case(cid).get('turn') is None, 'Leave it changes nothing')
    # ---- 2. Mine while their promise is open: your step is asked for, the promise stays ----
    pg.click('[data-a=turn-reset]'); wait(pg, 300); pg.click('[data-a=turn-yours]'); wait(pg, 500)
    ok(pg.locator('#moveform').count() == 1 and case(cid)['turn'] == 'yours' and case(cid)['promises'] == pr and 'Their promise stays on the case.' in labels(cid)[-1], 'Mine: your step is asked for and their promise is untouched')
    pg.fill('#f-mwhat', 'Send Currys the photo of the receipt'); pg.select_option('select[data-dp=f-mdate][data-part=d]', str(fri.day)); pg.select_option('select[data-dp=f-mdate][data-part=m]', str(fri.month)); pg.select_option('select[data-dp=f-mdate][data-part=y]', str(fri.year))
    pg.click('form[data-f=move] button[type=submit]'); wait(pg, 600)
    c = case(cid); mv = [x for x in c['moves'] if x['status'] == 'open']
    ok(len(mv) == 1 and mv[0]['what'].startswith('Send Currys') and len([x for x in c['promises'] if x['status'] == 'open']) == 1, 'your step and their promise are both open')
    ok('Whose move\nYours: Currys asked you for something. Their promise is on the case too.' in u(), 'What Sorted understood says both')
    # ---- 3. Theirs while your step is open: the conflict is asked, nothing changes until a choice ----
    n2 = len(labels(cid)); pg.click('[data-a=turn-reset]'); wait(pg, 300); pg.click('[data-a=turn-theirs]'); wait(pg, 400); m = main()
    ok('You have a step open: “Send Currys the photo of the receipt”' in m and 'Nothing has changed yet.' in m and 'Keep my step as well' in m and 'Mark my step no longer needed' in m and 'Leave it as it was' in m, 'a conflict with your open step is asked, not applied')
    c = case(cid)
    ok(c['turn'] == 'yours' and [x for x in c['moves'] if x['status'] == 'open'] and len(labels(cid)) == n2, 'until a choice, the answer and the step are as they were')
    pg.click('[data-a=turn-leave]'); wait(pg, 300)
    ok(case(cid)['turn'] == 'yours' and 'You have a step open' not in main(), 'Leave it as it was leaves it')
    pg.click('[data-a=turn-reset]'); wait(pg, 300); pg.click('[data-a=turn-theirs]'); wait(pg, 400); pg.click('[data-a=turn-keep]'); wait(pg, 500)
    c = case(cid)
    ok(c['turn'] == 'theirs' and [x for x in c['moves'] if x['status'] == 'open'] and labels(cid)[-1] == 'Whose move: theirs. You’re waiting for Currys. Your step stays open.' and c['promises'] == pr, 'Keep my step as well: theirs, the step still open, the promise untouched')
    ok('Whose move\nTheirs: you’re waiting for Currys. Your step “Send Currys the photo of the receipt” is open too.' in u(), 'What Sorted understood keeps both in view')
    pg.click('[data-a=turn-reset]'); wait(pg, 300); pg.click('[data-a=turn-theirs]'); wait(pg, 400); pg.click('[data-a=turn-dropstep]'); wait(pg, 500)
    c = case(cid)
    ok(c['turn'] == 'theirs' and not [x for x in c['moves'] if x['status'] == 'open'] and c['moves'][0]['status'] == 'dropped' and 'Your step no longer needed: Send Currys the photo of the receipt.' in labels(cid) and c['promises'] == pr, 'Mark my step no longer needed: the step is dropped with a history line, the promise untouched')
    ok(pg.locator('[data-a=turn-reset]').inner_text() == 'Change whose move', 'with an answer, the button says Change whose move')
    # ---- 4. a bare case: the question leads, with the new wording ----
    pg.goto('https://sorted.test/'); wait(pg, 500); pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.fill('#f-case', 'The letting agent is dealing with the deposit'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    m = main()
    ok('Whose move is it now?' in m and pg.locator('[data-a=turn-theirs]').count() == 1 and 'Whose move is it?\n' not in m, 'a bare case asks "Whose move is it now?"')
    ok(not errs, 'no page errors: %s' % errs)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
