# v66: move a message to the right case, hand-offs between companies, and your own history with a company.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=350): pg.wait_for_timeout(ms)
def tasks(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks.map(y=>y.data)")
def case(pg, title): return next((x for x in tasks(pg) if x['title'] == title), None)
def labels(t): return [e['label'] for e in t['events']]
def start(pg, text):
    pg.goto('https://sorted.test/'); wait(pg, 400)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
    pg.fill('#f-case', text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 450)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 150)
def open_case(pg, title):
    pg.goto('https://sorted.test/'); wait(pg, 400); pg.locator('[data-a=open][data-id="%s"]' % case(pg, title)['id']).first.click(); wait(pg)
def paste(pg, text):
    pg.click('[data-a=panel][data-p=paste]'); wait(pg); pg.fill('#f-paste', text); pg.click('form[data-f=paste] button[type=submit]'); wait(pg)
    if pg.locator('#f-paste').count(): pg.click('form[data-f=paste] [data-a=panel][data-p=""]'); wait(pg)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 200); pg.click('[data-a=anon-start]'); wait(pg)
    C = 'Currys refund · 445566'; A = 'Argos refund · 7712345'
    start(pg, "Currys refund hasn't arrived, order 445566")
    start(pg, "Argos refund hasn't arrived, order 7712345")
    # 1 a message in the wrong case moves to the right one
    open_case(pg, C)
    paste(pg, "Argos: we have received your returned item and are checking it.")
    ok(any(l.startswith('Added a message: “Argos: we have received') for l in labels(case(pg, C))), 'the Argos message landed in the Currys case')
    pg.click('[data-a=ev-move]'); wait(pg)
    ok('Move this message' in pg.inner_text('main') and pg.locator('[data-a=ev-move-to]').count() == 1, 'it offers your other open case')
    pg.click('[data-a=ev-move-to]'); wait(pg)
    tc, ta = case(pg, C), case(pg, A)
    ok(not any(l.startswith('Added a message: “Argos') for l in labels(tc)) and 'Moved a message to “Argos refund · 7712345”.' in labels(tc), 'it leaves the Currys case, which notes the move')
    ok(any(l.startswith('Added a message: “Argos: we have received') for l in labels(ta)) and 'Moved here from “Currys refund · 445566”.' in labels(ta), 'it arrives in the Argos case, which notes where from')
    ok('Argos refund' in pg.inner_text('main h1') and 'we have received your returned item' in pg.inner_text('main'), 'you land on the Argos case with the message under evidence')
    # 2 or start a new case with it
    open_case(pg, C)
    paste(pg, "EE: your broadband engineer is booked, reference EE-5521.")
    pg.click('[data-a=ev-move]'); wait(pg); pg.click('[data-a=ev-move-new]'); wait(pg)
    ok(pg.input_value('#f-case').startswith('EE: your broadband engineer is booked'), '"Start a new case with it" puts the message in the start box')
    ok(not any(l.startswith('Added a message: “EE:') for l in labels(case(pg, C))), 'and takes it out of the Currys case')
    # 3 passed between companies
    open_case(pg, C)
    paste(pg, "Hi, we've passed your case to Knowhow, our repair partner, who will contact you.")
    hc = pg.inner_text('.ho-card') if pg.locator('.ho-card').count() else ''
    ok('This says it’s now with Knowhow. Is that right?' in hc and 'we\'ve passed your case to Knowhow' in hc, 'a hand-off is proposed, with their words')
    ok(not case(pg, C).get('holder') or case(pg, C)['holder']['st'] == 'proposed', 'nothing confirmed yet')
    pg.click('[data-a=ho-yes]'); wait(pg)
    t = case(pg, C)
    ok(t['holder']['st'] == 'confirmed' and t['holder']['to'] == 'Knowhow' and t['holder']['from'] == 'Currys', 'confirmed: with Knowhow, passed on by Currys')
    ok('Now with Knowhow.' in pg.inner_text('.ho-line') and 'Currys passed it on' in pg.inner_text('.ho-line'), 'the case says who has it now and who passed it on')
    ok(any(l.startswith('Passed to Knowhow by Currys: “') for l in labels(t)), 'the history records it')
    if pg.locator('[data-a=panel][data-p=call]').count(): pg.click('[data-a=panel][data-p=call] >> nth=0'); wait(pg)
    if pg.locator('#f-who').count():
        ok(pg.input_value('#f-who') == 'Knowhow' and pg.input_value('textarea[name=ask]').startswith('On ') and 'Currys told me that Knowhow is dealing with this' in pg.input_value('textarea[name=ask]'), 'the next message goes to Knowhow and quotes the hand-off')
    else:
        ok(False, 'the call form is reachable')
    # 4 "No" leaves it
    start(pg, "Samsung TV repair, they keep cancelling the engineer")
    paste(pg, "This is the manufacturer's responsibility, not ours.")
    ok(pg.locator('.ho-card').count() == 1, 'another hand-off proposed')
    pg.click('[data-a=ho-no]'); wait(pg)
    ok(pg.locator('.ho-card, .ho-line').count() == 0, '"No" leaves the case as it was')
    # 5 your own history with a company
    start(pg, "Currys still haven't collected the old fridge, order 556677")
    mb = pg.inner_text('.mem-block') if pg.locator('.mem-block').count() else ''
    ok('You and Currys' in mb and 'You’ve had 1 other case with Currys.' in mb and 'Reference you used: 445566.' in mb, 'your other Currys case is remembered, with its reference: %r' % mb[:160])
    ok('From your own cases on this phone only.' in mb, 'it says it’s only from your own cases')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
