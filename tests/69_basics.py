# v112: the basics. Rename a case; reopen a finished one; remove a saved message and put it back; a promise cancelled
# or no longer needed (not a miss, nothing sent to company totals, no chase); Undo after deleting a case; Account in
# three parts (Account, Settings with reminders and appearance, Help & About with nine questions and who runs Sorted);
# Help & About on the signed-out site.
import os, sys, json, datetime, re
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
    case = lambda cid: [x for x in cases() if x['id'] == cid]
    labels = lambda cid: [e.get('label') or '' for e in case(cid)[0]['events']]
    # signed out: Help & About
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.goto('https://sorted.test/'); wait(pg, 600)
    ok(pg.locator('footer a[href="#help"]').count() == 1, 'the signed-out footer links to Help & About')
    pg.goto('https://sorted.test/#help'); wait(pg, 500); m = pg.inner_text('main')
    ok('Questions people ask' in m, 'Help opens before signing in')
    pg.goto('https://sorted.test/#about'); wait(pg, 500); m = pg.inner_text('main')
    ok('About Sorted' in m and 'Baldwin Thompson-Addo' in m, 'About opens before signing in')
    ok('07311' not in m and 'Tokio' not in m and 'HSBC' not in m and 'bthompsonaddo' not in m, 'the About text carries no phone number, personal email or employer names')
    pg.goto('https://sorted.test/#start'); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    def start(text):
        pg.goto('https://sorted.test/'); wait(pg, 500)
        if pg.locator('[data-cap82=other]').count(): pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg)
        elif pg.locator('[data-a=compose]').count(): pg.locator('[data-a=compose]').first.evaluate('e=>e.click()'); wait(pg)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
        if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
        if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
        return cases()[-1]['id']
    def more(): pg.evaluate("document.querySelectorAll('details.case56-more').forEach(d=>d.open=true)")
    fri = datetime.date.today() + datetime.timedelta(days=(4 - datetime.date.today().weekday()) % 7 or 7)
    cid = start("Currys said they would refund £89 by %s, order 445566" % fri.strftime('%A'))
    # 1 rename
    more(); pg.click('[data-a=panel][data-p=rename]'); wait(pg, 300)
    ok(pg.input_value('#f-rename') == case(cid)[0]['title'], 'Rename opens with the current name')
    pg.fill('#f-rename', 'x'); pg.click('form[data-f=rename] button[type=submit]'); wait(pg, 300)
    ok('Give it a name' in pg.inner_text('main'), 'a name needs a few words')
    pg.fill('#f-rename', 'Currys kettle refund'); pg.click('form[data-f=rename] button[type=submit]'); wait(pg, 500)
    c = case(cid)[0]
    ok(c['title'] == 'Currys kettle refund' and 'Currys kettle refund' in pg.inner_text('main') and any(l.startswith('Renamed from “') and 'Currys kettle refund' in l for l in labels(cid)), 'the case is renamed and the history says from what to what')
    ok(c['promises'][0]['said'] and c['promises'][0]['ref'] == '445566', 'nothing else about the case changes')
    # 2 a message removed and put back
    pg.locator('[data-a=panel][data-p=paste]').first.evaluate('e=>e.click()'); wait(pg, 300); pg.fill('#f-paste', 'Thanks for getting in touch, we are looking into it.'); pg.click('form[data-f=paste] button[type=submit]'); wait(pg, 600)
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600)
    pg.evaluate("document.querySelectorAll('details.case75-group').forEach(d=>d.open=true)"); wait(pg, 200)
    n_ev = len([l for l in labels(cid) if l.startswith('Added a message')])
    ok(n_ev == 1 and pg.locator('[data-a=ev-del]').count() == 1, 'a pasted message has Remove')
    pg.locator('[data-a=ev-del]').first.click(); wait(pg, 500)
    ok(not [l for l in labels(cid) if l.startswith('Added a message')] and 'Removed a message you added.' in labels(cid) and pg.locator('[data-a=ev-undo]').count() == 1, 'Remove takes the message off, the history says so without its words, and offers Undo')
    ok('looking into it' not in json.dumps(case(cid)[0]), 'the removed words are gone from the saved case')
    pg.click('[data-a=ev-undo]'); wait(pg, 500)
    ok(len([l for l in labels(cid) if l.startswith('Added a message')]) == 1 and 'Removed a message you added.' not in labels(cid), 'Undo puts it back exactly')
    # 3 a promise cancelled or no longer needed
    outs0 = pg.evaluate("JSON.parse(localStorage.getItem('__outcomes')||'[]').length")
    ev0 = len(dbj().get('pilot_events', []))
    ok(pg.locator('[data-a=p-cancel]').count() == 1, 'the promise offers "They cancelled it, or it’s not needed now"')
    pg.click('[data-a=p-cancel]'); wait(pg, 600)
    c = case(cid)[0]
    ok(c['promises'][0]['status'] == 'cancelled' and any(l.startswith('No longer needed:') for l in labels(cid)), 'the promise is recorded as cancelled, in plain words')
    ok(pg.evaluate("JSON.parse(localStorage.getItem('__outcomes')||'[]').length") == outs0 and not [e for e in dbj().get('pilot_events', [])[ev0:] if e['name'] in ('outcome_missed', 'outcome_kept')], 'it is not a miss: nothing goes to company totals or the miss count')
    ok(pg.locator('form[data-f=call]').count() == 0 and pg.locator('#f-outcome').count() == 1, 'no chase message; Sorted asks how it ended instead')
    pg.locator('form [data-a=panel][data-p=""]').first.click() if pg.locator('form [data-a=panel][data-p=""]').count() else None; wait(pg, 300)
    pg.click('[data-a=panel][data-p=pack]'); wait(pg, 400)
    ok('Cancelled, or no longer needed.' in pg.inner_text('.pack-doc') and 'Promises missed' not in pg.inner_text('.pack-doc'), 'the adviser pack says it was cancelled, not missed')
    # 4 finish, then reopen
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 500); more(); pg.click('[data-a=panel][data-p=done]'); wait(pg, 300)
    pg.fill('#f-outcome', 'Bought it elsewhere'); pg.locator('form[data-f=done] button[type=submit]').click(); wait(pg, 600)
    ok(case(cid)[0]['board'] == 'done', 'finished')
    more(); ok(pg.locator('[data-a=case-reopen]').count() == 1, 'a finished case offers Reopen')
    pg.click('[data-a=case-reopen]'); wait(pg, 600); c = case(cid)[0]
    ok(c['board'] != 'done' and not c.get('outcome') and any(l.startswith('Reopened.') and 'Bought it elsewhere' in l for l in labels(cid)), 'Reopen brings it back and the history keeps how it had ended')
    pg.goto('https://sorted.test/'); wait(pg, 600)
    ok('Currys kettle refund' in pg.inner_text('main') and pg.locator('.home44-done').count() == 0, 'it is back among the open cases on Home')
    # 5 delete, then Undo
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 500); more(); pg.click('[data-a=panel][data-p=delcase]'); wait(pg, 300); pg.click('[data-a=case-del]'); wait(pg, 700)
    ok(not case(cid) and pg.locator('[data-a=del-undo]').count() == 1 and 'Deleted “' in pg.inner_text('main'), 'deleting goes Home and offers Undo')
    pg.click('[data-a=del-undo]'); wait(pg, 900)
    c = case(cid)
    ok(c and c[0]['title'] == 'Currys kettle refund' and any(l.startswith('Put back after being deleted.') for l in labels(cid)) and 'Currys kettle refund' in pg.inner_text('main'), 'Undo puts the whole case back, saved again')
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 500); more(); pg.click('[data-a=panel][data-p=delcase]'); wait(pg, 300); pg.click('[data-a=case-del]'); wait(pg, 700)
    pg.click('.navq'); wait(pg, 500)
    ok(pg.locator('[data-a=del-undo]').count() == 0 and not case(cid), 'any other tap lets the deletion stand')
    # 6 Account in three parts
    pg.goto('https://sorted.test/'); wait(pg, 400); pg.click('[data-a=data]'); wait(pg, 600); m = pg.inner_text('main')
    ok(pg.locator('.acct112-nav [data-a=acct-jump]').all_inner_texts() == ['Account', 'Settings', 'Help & About'] and pg.locator('main h2.h2').all_inner_texts() == ['Your account'], 'Account has three parts, one shown at a time: Your account first')
    ok(pg.locator('.acct112-nav [data-a=acct-jump]').count() == 3, 'three tabs switch between them')
    ok('Sign out' in m or 'Add my email' in m, 'sign-in details sit under Your account')
    pg.click('.acct112-nav [data-v=acct-settings]'); wait(pg, 500); m = pg.inner_text('main')
    ok('Email reminders' in m and 'Appearance' in m and 'Usage records' in m and 'Your account' not in m, 'Settings has reminders, appearance and usage records, and only those')
    pg.click('.acct112-nav [data-v=help]'); wait(pg, 700); m = pg.inner_text('main')
    ok(pg.evaluate("document.activeElement&&document.activeElement.id==='help-h'"), 'a tab puts focus on that part’s heading')
    ok(pg.locator('.acct112-q').count() >= 9 and 'Report a problem' in m and 'kofiniiakwei@gmail.com' in m and 'How Sorted works, in writing' in m and 'How your data is handled' in m, 'Help & About has the questions, contact, Report a problem, privacy and terms')
    ok('Why it exists.' in m and 'Who runs it.' in m and 'data protection' in m and 'doesn’t use it to read your cases' in m and m.index('Why it exists.') < m.index('Who runs it.'), 'About Sorted says why it exists first, then who runs it and why that matters for your data (v126)')
    pg.locator('.acct112-q summary').first.click(); wait(pg, 200)
    ok(pg.locator('.acct112-q[open]').count() == 1, 'a question opens to its answer')
    # 7 appearance
    pg.click('.acct112-nav [data-v=acct-settings]'); wait(pg, 400)
    pg.click('[data-a=theme-set][data-v=light]'); wait(pg, 300)
    ok(pg.evaluate("document.documentElement.getAttribute('data-theme')") == 'light' and pg.locator('[data-a=theme-set][data-v=light]').get_attribute('aria-pressed') == 'true', 'Light sets the page light and shows as chosen')
    pg.reload(); wait(pg, 600)
    ok(pg.evaluate("document.documentElement.getAttribute('data-theme')") == 'light', 'the choice survives a reload')
    if not pg.locator('[data-a=theme-set]').count(): pg.click('[data-a=data]'); wait(pg, 500); pg.click('.acct112-nav [data-v=acct-settings]'); wait(pg, 400)
    pg.click('[data-a=theme-set][data-v=dark]'); wait(pg, 300)
    ok(pg.evaluate("document.documentElement.getAttribute('data-theme')") == 'dark' and pg.evaluate("getComputedStyle(document.body).backgroundColor") != 'rgb(246, 243, 236)', 'Dark makes the page dark')
    pg.click('[data-a=theme-set][data-v=system]'); wait(pg, 300)
    ok(pg.evaluate("document.documentElement.getAttribute('data-theme')") is None, 'Follow my phone removes the choice')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), 'nothing scrolls sideways')
    print('CHECKS', n[0]); b.close()
print('ERRORS', errs); print('FAILS', fails)
