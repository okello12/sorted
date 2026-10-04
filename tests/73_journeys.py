# v117 (docs/PLAN.md Phase 2): the shared case structure, and five journeys end to end. The structure: the matter,
# the outcome wanted (proposed, confirmed or skipped, editable), who is involved, whose move it is, their date kept
# apart from a follow-up you chose, the next action. It is shown on every case as "What Sorted understood".
# The Ford journey: a guided start with "Dealer ford" and "Need to do credit check" keeps the dealer as the party,
# names the case "Dealer ford: credit check", asks whose move it is, and either keeps a follow-up you chose (never a
# promise) or your own step from what they asked for; the call form already knows who. Then repair, refund, parking,
# renewal and a sentence Sorted doesn't recognise (the general organiser), each walked to a settled state.
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
def pick(pg, d):
    for part, v in [('d', d.day), ('m', d.month), ('y', d.year)]: pg.select_option('select[data-dp=f-mdate][data-part=%s]' % part, str(v))
fri = datetime.date.today() + datetime.timedelta(days=(4 - datetime.date.today().weekday()) % 7 or 7)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    case = lambda cid: [x for x in cases() if x['id'] == cid][0]
    labels = lambda cid: [e.get('label') or '' for e in case(cid)['events']]
    def main(): return pg.inner_text('main')
    def understood():
        pg.evaluate("document.querySelectorAll('details.case117-u').forEach(d=>d.open=true)"); wait(pg, 150)
        return pg.inner_text('details.case117-u') if pg.locator('details.case117-u').count() else ''
    def settle():
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    def door(k):
        pg.goto('https://sorted.test/'); wait(pg, 500)
        if pg.locator('[data-a=new-case]').count(): pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.locator('[data-cap82=%s]' % k).first.evaluate('e=>e.click()'); wait(pg, 400)
    def sentence(text):
        door('other'); pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600); settle()
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.goto('https://sorted.test/#start'); wait(pg, 400)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)

    # ---- 1. the Ford journey, waiting on them ----
    pg.locator('[data-cap82=promise]').first.evaluate('e=>e.click()'); wait(pg, 400)
    pg.fill('#gi-who', 'Dealer ford'); pg.fill('#gi-what', 'Need to do credit check'); pg.click('form[data-f=gi] button[type=submit]'); wait(pg, 700)
    ok(pg.locator('form[data-f=baseline]').count() == 1 and pg.locator('[data-a=plan-skip]').count() == 1, 'the planning question can be skipped')
    pg.click('[data-a=plan-skip]'); wait(pg, 600)
    cid = cases()[-1]['id']; c = case(cid); m = main()
    ok(c['title'] == 'Dealer ford: credit check', 'a real title from who and what: %r' % c['title'])
    ok(c['facts'].get('party') == 'Dealer ford' and c['baseline'] == '' and 'Started.' in labels(cid) and not any('the plan was' in l for l in labels(cid)), 'the dealer is the party; a skipped question records nothing')
    ok('Whose move is it now?' in m and 'Are you waiting for Dealer ford, or have they asked you for something?' in m, 'it asks whose move it is now, naming the dealer')
    ok('Theirs: I’m waiting for Dealer ford' in m and 'Mine: Dealer ford asked me for something' in m and 'Both' in m, 'three answers: Mine, Theirs, Both')
    ok('Ask Dealer ford for a date' in m and 'say so just below' in m, 'the first response points at that question')
    ok('Save a follow-up reminder' in m and 'Choose a date' in m and 'In 3 days' in m, 'the follow-up buttons say what they do, with a date of your own')
    ok('What would you like to come out of this?' in m and pg.input_value('#f-goal') == 'Get a date from Dealer ford for what they said they would do', 'the outcome wanted is proposed, honestly: %r' % pg.input_value('#f-goal'))
    ok(pg.input_value('#f-who') == 'Dealer ford' if pg.locator('#f-who').count() else True, 'the call form already knows who')
    pg.click('[data-a=turn-theirs]'); wait(pg, 400)
    c = case(cid)
    ok(c.get('turn') == 'theirs' and any(l.startswith('Whose move: theirs') for l in labels(cid)) and 'Whose move is it now?' not in main(), 'waiting on them: recorded, and the question goes')
    pg.fill('#f-goal', 'Find out whether the credit check is complete'); pg.click('form[data-f=goal] button[type=submit]'); wait(pg, 400)
    c = case(cid)
    ok(c.get('goal') == 'Find out whether the credit check is complete' and 'Outcome wanted: “Find out whether the credit check is complete”.' in labels(cid), 'the outcome wanted is kept, in your words')
    pg.click('[data-a=fr-check-date]'); wait(pg, 400)
    ok(pg.locator('#moveform').count() == 1 and pg.input_value('#f-mwhat') == 'Check back with Dealer ford if nothing has happened' and pg.locator('form[data-f=move] button[type=submit]').inner_text() == 'Save follow-up reminder', '"Choose a date" opens your follow-up with the button saying so')
    pick(pg, fri); pg.click('form[data-f=move] button[type=submit]'); wait(pg, 600)
    c = case(cid); mv = [x for x in c.get('moves') or [] if x['status'] == 'open']
    ok(len(mv) == 1 and mv[0].get('chosen') is True and not c['promises'] and any('The day was your choice, not their promise' in l for l in labels(cid)), 'the follow-up is your own step, your choice, never their promise')
    u = understood()
    ok('The matter\nDealer ford: credit check' in u, 'What Sorted understood: the matter')
    ok('Outcome wanted\nFind out whether the credit check is complete' in u, 'the outcome wanted')
    ok('Who is involved\nDealer ford' in u, 'who is involved')
    ok('Whose move\nTheirs: you’re waiting for Dealer ford.' in u, 'whose move')
    ok('Your follow-up (your choice)' in u and 'Their date' not in u, 'your follow-up is kept apart from their date')
    ok('Change the outcome' in u and 'Change whose move' in u, 'both can be changed')
    pg.goto('https://sorted.test/'); wait(pg, 500); hm = main()
    ok('Dealer ford: credit check' in hm and 'Check back with Dealer ford if nothing has happened' in hm, 'Home shows the real title and your follow-up')

    # ---- 2. the Ford journey, they asked for something ----
    pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.locator('[data-cap82=promise]').first.evaluate('e=>e.click()'); wait(pg, 400)
    pg.fill('#gi-who', 'Ford Credit'); pg.fill('#gi-what', 'said they would send the finance agreement'); pg.click('form[data-f=gi] button[type=submit]'); wait(pg, 700); settle()
    cid2 = cases()[-1]['id']
    ok(case(cid2)['title'] == 'Ford Credit: send the finance agreement', 'a second party with its own case: %r' % case(cid2)['title'])
    pg.click('[data-a=turn-yours]'); wait(pg, 400)
    ok(pg.locator('#moveform').count() == 1 and 'What have Ford Credit asked you for, and by when?' in main() and pg.locator('form[data-f=move] button[type=submit]').inner_text() == 'Save my step', '"They’ve asked me for something" opens your step, asking what and by when')
    pg.fill('#f-mwhat', 'Send Ford Credit my proof of address'); pick(pg, fri); pg.click('form[data-f=move] button[type=submit]'); wait(pg, 600)
    c2 = case(cid2); mv2 = [x for x in c2.get('moves') or [] if x['status'] == 'open']
    ok(c2.get('turn') == 'yours' and len(mv2) == 1 and mv2[0].get('asked') is True and 'Send Ford Credit my proof of address' in main() and 'GET THE CALL READY' not in main().upper().replace('’', "'") or 'Get the call ready' not in main(), 'your step is kept as yours, not a call script')
    ok('Whose move: yours. Ford Credit asked you for something.' in labels(cid2), 'the history says whose move')
    u2 = understood()
    ok('Whose move\nYours: Ford Credit asked you for something.' in u2 and 'Your step\nSend Ford Credit my proof of address' in u2, 'What Sorted understood: your step')

    # ---- 3. repair: washing machine, engineer promised, visit, fixed ----
    sentence("My washing machine won't drain")
    cid3 = cases()[-1]['id']; m = main()
    ok(case(cid3)['mode'] == 'fix' and 'Your washing machine isn’t working' in m and 'Whose move is it now?' not in m, 'repair: the fix questions lead, no turn question')
    ok(pg.input_value('#f-goal') == 'Get the washing machine working again' if pg.locator('#f-goal').count() else False, 'repair: the outcome proposed')
    pg.click('form[data-f=goal] button[type=submit]'); wait(pg, 400)
    ok(case(cid3).get('goal') == 'Get the washing machine working again', 'repair: the outcome kept')
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    u3 = understood()
    ok('Outcome wanted\nGet the washing machine working again' in u3 and 'Next\n' in u3, 'repair: understood card with the next action')

    # ---- 4. refund: a promise with a date, kept ----
    sentence("Currys said my refund of £89 would arrive by %s, order 445566" % fri.strftime('%A'))
    cid4 = cases()[-1]['id']
    ok(pg.locator('[data-a=sug-yes]').count() == 1 and 'What would you like to come out of this?' not in main(), 'refund: the promise card first, the outcome question waits')
    pg.click('[data-a=sug-yes]'); wait(pg, 600)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
    ok(pg.input_value('#f-goal') == 'Get the refund of £89 from Currys paid' if pg.locator('#f-goal').count() else False, 'refund: the outcome proposed from the facts (%r)' % (pg.input_value('#f-goal') if pg.locator('#f-goal').count() else ''))
    pg.click('[data-a=goal-skip]'); wait(pg, 300)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    u4 = understood()
    ok('Outcome wanted' not in u4 and 'Their date' in u4 and 'from Currys' in u4 and 'Who is involved\nCurrys · order 445566' in u4 and 'Whose move\nTheirs: Currys said they would' in u4, 'refund: skipped outcome stays out; their date, who and the reference are in')
    ok(case(cid4).get('goalSkip') is True and 'Whose move is it now?' not in main(), 'refund: a promise answers whose move, so no question')

    # ---- 5. parking: the notice typed, facts confirmed ----
    sentence("London Borough of Southwark PENALTY CHARGE NOTICE PCN Number: SK12345678 Vehicle Registration Mark: AB12 CDE Date of contravention: 30/09/2026 The penalty charge is £130. If paid within 14 days, reduced to £65.")
    cid5 = cases()[-1]['id']; m = main()
    ok('parking ticket' in m and 'Whose move is it now?' not in m, 'parking: the notice leads, no turn question')
    if pg.locator('[data-a=cf-yes]').count(): pg.click('[data-a=cf-yes]'); wait(pg, 500)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    if pg.locator('#f-goal').count(): ok(pg.input_value('#f-goal') == 'Decide what to do about the notice before its dates run out', 'parking: the outcome proposed'); pg.click('form[data-f=goal] button[type=submit]'); wait(pg, 400)
    u5 = understood()
    ok('Decide what to do about the notice' in u5 and 'Who is involved' in u5, 'parking: understood card')

    # ---- 6. renewal: your own step, no outcome question ----
    pg.goto('https://sorted.test/'); wait(pg, 500); pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.locator('[data-cap82=renew]').first.evaluate('e=>e.click()'); wait(pg, 400)
    if pg.locator('input[name=gi-item][value=Passport]').count(): pg.check('input[name=gi-item][value=Passport]')
    pg.click('form[data-f=gi] button[type=submit]'); wait(pg, 700)
    cid6 = cases()[-1]['id']
    ok(case(cid6)['mode'] == 'do' and pg.locator('#moveform').count() == 1 and 'What would you like to come out of this?' not in main() and 'Whose move is it now?' not in main(), 'renewal: your own step, nothing else asked')

    # ---- 7. something Sorted doesn't recognise: the general organiser ----
    sentence("The flat below keeps flooding my balcony and the managing agent said they would look into it")
    cid7 = cases()[-1]['id']; m = main()
    ok('Whose move is it now?' in m and 'Save a follow-up reminder' in m, 'unrecognised: it still asks whose move and offers a follow-up')
    pg.click('[data-a=turn-both]'); wait(pg, 400)
    ok(pg.locator('#moveform').count() == 1, 'both: your step first')
    pg.fill('#f-mwhat', 'Send the agent photos of the balcony'); pick(pg, fri); pg.click('form[data-f=move] button[type=submit]'); wait(pg, 600)
    c7 = case(cid7)
    ok(c7.get('turn') == 'both' and len([x for x in c7.get('moves') or [] if x['status'] == 'open']) == 1, 'both: recorded with your step')
    u7 = understood()
    ok('Whose move\nBoth:' in u7, 'unrecognised: understood card says both')
    # a settled case shows no questions on reload
    pg.goto('https://sorted.test/?task=%s' % cid7); wait(pg, 600)
    ok('Something to check' not in main() and pg.locator('details.case117-u').count() == 1, 'a settled case shows the structure with nothing to check')
    ok(not errs, 'no page errors')
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
