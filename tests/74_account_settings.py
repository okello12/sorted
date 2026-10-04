# v118 (docs/PLAN.md Phase 3, part 1): Account, Settings and Help & About are three views with a selected tab, each
# showing only its own part, with focus on its heading. Settings: an email reminders switch for every case, with its
# state and destination (on, off, not set up), written to the server (set_email_optout) and read back after a reload;
# the case says the dates and times its emails go, UK time, and that arrival depends on email; usage records show
# their state. Account: the case count in ordinary text, export as "Download my cases" and "Copy to clipboard" with
# the contents and format explained, "Delete my account" restrained until tapped and then a confirmation built from
# the deletion answer. Owner only for the admin. Home shows the sync state only when something is pending or offline.
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
SESSION = json.dumps({'user': {'id': 'u-me', 'email': 'me@example.com'}})
fri = datetime.date.today() + datetime.timedelta(days=(4 - datetime.date.today().weekday()) % 7 or 7)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: [x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment']
    main = lambda: pg.inner_text('main')
    def account(tab=None):
        if not pg.locator('[data-a=data]').count(): pg.goto('https://sorted.test/'); wait(pg, 500)
        pg.locator('[data-a=data]').first.click(); wait(pg, 400)
        if tab: pg.click('.acct112-nav [data-v=%s]' % tab); wait(pg, 400)
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')")
    pg.evaluate("localStorage.setItem('__mocksession', %s)" % json.dumps(SESSION)); pg.goto('https://sorted.test/'); wait(pg, 700)
    # a case with a promise, so there are email times to show
    if pg.locator('[data-cap82=other]').count(): pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg)
    elif pg.locator('[data-a=compose]').count(): pg.locator('[data-a=compose]').first.evaluate('e=>e.click()'); wait(pg)
    pg.fill('#f-case', 'Sky said an engineer would come on %s between 8am and 12pm, ref AB123' % fri.strftime('%A')); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
    cid = cases()[-1]['id']
    # 1 the case says when its emails go
    if pg.locator('[data-a=email-on]').count(): pg.click('[data-a=email-on]'); wait(pg, 500)
    pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); wait(pg, 200)
    m = main()
    ok('Email reminders are on.' in m and fri.strftime('%A %-d %B') in m and '(UK time)' in m and 'When it arrives depends on email.' in m, 'the case lists the dates and times its emails go, UK time, and that arrival depends on email')
    # 2 three views with a selected tab
    account()
    ok(pg.locator('.acct112-nav [role=tab][aria-selected=true]').inner_text() == 'Account' and pg.locator('main h1').inner_text() == 'Account' and pg.locator('#acct-settings').count() == 0 and pg.locator('#help').count() == 0, 'Account opens on its own view, the others not rendered')
    ok('1 case, linked to that email.' in main() and 'Everything is saved to your account.' in main(), 'the case count in ordinary text, with the sync state')
    pg.click('.acct112-nav [data-v=acct-settings]'); wait(pg, 400)
    ok(pg.locator('main h1').inner_text() == 'Settings' and pg.evaluate("document.activeElement&&document.activeElement.id") == 'acct-settings-h' and pg.locator('#acct-you').count() == 0, 'Settings is its own view, focus on its heading')
    # 3 the email reminders switch
    m = main()
    ok('Email reminders' in m and 'On.' in m and 'me@example.com' in m and 'at the time shown on the case, UK time' in m and 'can be late or not arrive' in m, 'the switch shows on, the destination and the cautious wording')
    pg.click('[data-a=optout-toggle]'); wait(pg, 500)
    ok('Off for every case.' in main() and dbj().get('email_optouts') and dbj()['email_optouts'][0]['user_id'] == 'u-me', 'switching off is written to the server and shown')
    pg.reload(); wait(pg, 700); account('acct-settings')
    ok('Off for every case.' in main() and pg.locator('[data-a=optout-toggle]').inner_text() == 'Switch email reminders on', 'the state comes back from the server after a reload')
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600); pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); wait(pg, 200)
    ok('switched email reminders off for every case in Settings' in main(), 'the case says the account-wide switch is off')
    account('acct-settings'); pg.click('[data-a=optout-toggle]'); wait(pg, 500)
    ok('On.' in main() and not dbj().get('email_optouts'), 'switching on removes the server row')
    # 4 usage records show their state; Owner only for the admin
    m = main()
    ok('Usage records' in m and 'never what a case says' in m and pg.locator('[data-a=steps-toggle][aria-pressed=true]').count() == 1 and 'Owner' not in m, 'usage records on, with what is recorded; no Owner section for an ordinary person')
    pg.click('[data-a=steps-toggle]'); wait(pg, 300)
    ok('Off on this phone.' in main() and pg.locator('[data-a=steps-toggle][aria-pressed=false]').count() == 1, 'usage records off, shown')
    pg.click('[data-a=steps-toggle]'); wait(pg, 300)
    pg.evaluate("localStorage.setItem('__admin','1')"); pg.reload(); wait(pg, 800); account('acct-settings')
    ok('Owner' in main() and 'Pilot numbers' in main(), 'the admin sees an Owner section with the numbers')
    pg.evaluate("localStorage.removeItem('__admin')")
    # 5 export and deletion
    account('acct-you'); m = main()
    ok('Download my cases' in m and 'Copy to clipboard' in m and 'plain text file (.txt)' in m and 'every case with its promises, dates, references, messages and history, then your moves' in m, 'export: two buttons, the contents and format explained')
    ok(pg.locator('[data-a=wipe-ask]').inner_text() == 'Delete my account' and 'danger-quiet' in (pg.get_attribute('[data-a=wipe-ask]', 'class') or '') and pg.locator('[data-a=wipe]').count() == 0, '"Delete my account" is restrained until tapped')
    pg.click('[data-a=wipe-ask]'); wait(pg, 300); m = main()
    ok('deletes your account and your 1 case straight away, on every device' in m and 'usage records' in m and 'There is no Undo.' in m and 'stay in your inbox' in m and pg.locator('[data-a=wipe]').inner_text() == 'Delete my account', 'the confirmation is the deletion answer')
    pg.click('[data-a=wipe-cancel]'); wait(pg, 300)
    ok(pg.locator('[data-a=wipe]').count() == 0 and cases(), 'Keep it keeps it')
    # 6 Help & About is the third view; the top-bar Help lands there
    pg.goto('https://sorted.test/'); wait(pg, 500); pg.locator('.bar [data-a=help]').first.click(); wait(pg, 500)
    ok(pg.locator('main h1').inner_text() == 'Help & About' and pg.locator('.acct112-q').count() >= 9 and pg.locator('#acct-you').count() == 0, 'Help lands on Help & About, its own view')
    # 7 Home shows the sync state only when something is pending or offline
    pg.goto('https://sorted.test/'); wait(pg, 500)
    ok(pg.locator('.home118-sync').count() == 0, 'Home shows no sync line while everything is saved')
    pg.evaluate("localStorage.setItem('__failWrites','1')")
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 500)
    pg.evaluate("document.querySelectorAll('details.case56-more').forEach(d=>d.open=true)")
    pg.click('[data-a=panel][data-p=rename]'); wait(pg, 250); pg.fill('#f-rename', 'Sky engineer, renamed offline'); pg.click('form[data-f=rename] button[type=submit]'); wait(pg, 400)
    pg.locator('[data-a=home]').first.click(); wait(pg, 500)
    ok(pg.locator('.home118-sync').count() == 1 and '1 case saved on this phone, not yet sent' in pg.inner_text('.home118-sync'), 'with a change pending, Home says so')
    pg.evaluate("localStorage.removeItem('__failWrites')"); pg.evaluate("window.dispatchEvent(new Event('online'))"); wait(pg, 800)
    pg.goto('https://sorted.test/'); wait(pg, 500)
    ok(pg.locator('.home118-sync').count() == 0, 'once sent, the line goes')
    ok(not errs, 'no page errors')
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
