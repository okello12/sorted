# v64: response reader, release 5. A reply is compared with the case: what kind of decision, their reasons, what it skips.
import os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=350): pg.wait_for_timeout(ms)
T0 = datetime.date.today()
SEP = ','  # Chromium's own date format decides: some versions write "Fri, 2 Oct", newer ones "Fri 2 Oct"; set from the browser below
def uk(n): return (T0 + datetime.timedelta(days=n)).strftime('%d/%m/%Y')
def day(n): x = T0 + datetime.timedelta(days=n); return x.strftime('%a' + SEP + ' %-d %b') if x.year == T0.year else x.strftime('%a' + SEP + ' %-d %b %Y')
def tasks(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks.map(y=>y.data)")
def case(pg, title): return next((x for x in tasks(pg) if x['title'] == title), None)
def start(pg, text):
    pg.goto('https://sorted.test/'); wait(pg, 400)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
    pg.fill('#f-case', text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 450)
    if pg.locator('[data-a=cf-yes]').count(): pg.click('[data-a=cf-yes]'); wait(pg)
def paste(pg, text):
    pg.click('[data-a=panel][data-p=paste]'); wait(pg); pg.fill('#f-paste', text); pg.click('form[data-f=paste] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=panel][data-p=""]').count() and pg.locator('#f-paste').count(): pg.click('form[data-f=paste] [data-a=panel][data-p=""]'); wait(pg)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    SEP = ',' if ',' in pg.evaluate("new Date(2026,9,2).toLocaleDateString('en-GB',{weekday:'short',day:'numeric',month:'short'})") else ''
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 200); pg.click('[data-a=anon-start]'); wait(pg)
    T = 'Southwark PCN · SK12345678'
    start(pg, "London Borough of Southwark PENALTY CHARGE NOTICE PCN Number: SK12345678 Vehicle Registration Mark: AB12 CDE Date of contravention: %s The penalty charge is £130. If paid within 14 days, reduced to £65." % uk(-6))
    pg.click('.pk-card [data-a=panel][data-p=pkbuild]'); wait(pg)
    pg.check('input[name=bdg-paid]'); pg.check('input[name=bdg-signs]'); pg.check('input[name=bde-receipt]'); pg.click('form[data-f=pkbuild] button[type=submit]'); wait(pg)
    pg.click('form[data-f=pkdraft] button[type=submit]'); wait(pg); pg.click('form[data-f=pksent] button[type=submit]'); wait(pg)
    ok(case(pg, T)['pk']['stage'] == 'challenged', 'challenge sent')
    # 1 an acknowledgement changes nothing
    paste(pg, "Thank you. We have received your challenge for PCN SK12345678 and will respond in due course.")
    ok(pg.locator('.rs-card').count() == 0 and case(pg, T)['pk']['stage'] == 'challenged', 'an acknowledgement is kept but changes nothing')
    # 2 a rejection that skips one of your points
    paste(pg, ("Southwark Council Parking Services. Date: %s. PCN SK12345678, vehicle AB12 CDE. We have considered your challenge. "
               "We do not accept it. Our records show no valid payment was made for this vehicle at the time of the contravention. "
               "The penalty charge remains payable. We will hold the reduced rate of £65 for a further 14 days.") % uk(0))
    rc = pg.inner_text('.rs-card') if pg.locator('.rs-card').count() else ''
    ok('This looks like Southwark said no. Is that right?' in rc and 'Nothing changes until you say so' in rc, 'a rejection is proposed, not applied')
    ok('Our records show no valid payment was made for this vehicle' in rc, 'it shows their reason in their words')
    ok('“the signs or road markings were unclear or missing”. Their reply doesn’t seem to mention it.' in rc, 'it spots the point their reply skips')
    ok('“i paid for parking”' not in rc.lower(), 'it doesn’t flag the point they did answer (payment)')
    ok('You sent evidence. Their reply doesn’t seem to mention it.' in rc, 'it notes they don’t mention your evidence')
    ok('seems to offer the reduced price again' in rc, 'it notices the reduced price is offered again')
    ok(case(pg, T)['pk']['stage'] == 'challenged', 'still nothing changed before you confirm')
    pg.screenshot(path=HERE + '/tests/out/response_card.png', full_page=True)
    pg.click('[data-a=rs-yes]'); wait(pg)
    t = case(pg, T)
    ok(t['pk']['stage'] == 'rejected' and t['pk']['rejectedOn'] == T0.isoformat() and t['pk']['rejFrom'] == 'challenged', 'confirming moves the case to "rejected", dated from their letter')
    ok(not [q for q in t['promises'] if q['status'] == 'open'], 'waiting on them is over: they replied')
    main = pg.inner_text('main')
    ok('Their reply' in main and 'Our records show no valid payment' in main and 'doesn’t seem to mention' in main, 'the case keeps what they said and what they skipped')
    ok(('Reduced price may be offered again until') in main and day(13) in main, 'and the next date')
    ok(any('They said no to the challenge (from their reply, dated' in e['label'] for e in t['events']), 'the history says where it came from')
    # 3 not that: nothing changes
    start(pg, "Camden Council PENALTY CHARGE NOTICE PCN number: CU98765432 Date of contravention: %s Penalty charge: £160" % uk(-3))
    TC = 'Camden PCN · CU98765432'
    pg.click('.pk-card [data-a=panel][data-p=pksent]'); wait(pg); pg.click('form[data-f=pksent] button[type=submit]'); wait(pg)
    paste(pg, "We regret that we are unable to accept your challenge at this time because the vehicle was parked in a suspended bay.")
    ok(pg.locator('.rs-card').count() == 1, 'another rejection is proposed')
    pg.click('[data-a=rs-no]'); wait(pg)
    ok(pg.locator('.rs-card').count() == 0 and case(pg, TC)['pk']['stage'] == 'challenged', '"No, that’s not it" leaves the case as it was')
    # 4 cancelled
    paste(pg, "Your challenge has been accepted and the PCN has been cancelled. No further action is needed.")
    ok('This looks like Camden cancelled it' in pg.inner_text('.rs-card'), 'a cancellation is proposed')
    pg.click('[data-a=rs-yes]'); wait(pg)
    t = case(pg, TC)
    ok(t['board'] == 'done' and t['outcome'] == 'Cancelled by Camden', 'confirming it finishes the case: %s' % t['outcome'])
    # 5 not a parking case
    start(pg, "Currys refund hasn't arrived, order 445566")
    paste(pg, "We have rejected your refund request because the item was used.")
    ok(pg.locator('.rs-card').count() == 0, 'ordinary cases aren’t read as parking decisions')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
