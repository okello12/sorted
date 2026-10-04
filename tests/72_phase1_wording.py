# v116 (docs/PLAN.md Phase 1): every public statement matches what Sorted does. The wrong sentences are gone and the
# corrected ones are pinned: deletion (a case, the account, Undo's limits, usage records that remain), who can read
# cases (technical access, not "nobody"), official links can change, guest accounts are about access and the 30-day
# activity rule, "usage records" not "step records", reminder emails sent on time but arrival unmeasured. Then:
# opening Sorted signed in records "seen" once per load; a device that was offline with an edit must not bring back a
# case deleted elsewhere; the reminder email body is built from fixed copy and links only.
import os, sys, json, re, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
WRONG = ['Sorted keeps nothing you delete', 'the official page is always right', 'Nobody running Sorted reads', 'nobody running Sorted reads', '(30 without an email)', '30 if you haven’t added an email', 'step records', 'Step records', 'deleted after 30 days away', 'can’t be recovered', 'or 30 if you haven’t added an email']
RIGHT = {
  'terms: deletion as it works': 'for two minutes Home offers Undo, and closing or refreshing the page ends that',
  'terms: usage records remain': 'Usage records about the case (its id and the steps you used, never its content) stay for up to 12 months',
  'terms: official links can change': 'Check the relevant authority’s current guidance before acting',
  'terms: reminders sent on time, arrival not promised': 'Sorted sends an email at the time it shows. When it arrives depends on email, and it can be late or not arrive',
  'privacy: technical access, not nobody': 'has technical access to the database, as with any online service, and doesn’t use it to open cases',
  'privacy: the guest activity rule': 'deleted after 30 days in which you don’t open Sorted (opening it signed in, saving a case or a live promise all count)',
  'privacy: usage records are not anonymous': 'They hold your account id and case ids with the steps you used, so they are not anonymous',
  'privacy: delivery recorded, never the address': 'whether its email provider accepted, delivered or bounced each reminder, never the address or the case',
  'help: deletion answer': 'Deleting your account removes everything at once, usage records included, with no Undo',
  'help: lost phone is about access': 'only the browser you started in can open them',
  'about: access wording': 'the person running it has technical access as any online service does and doesn’t use it to read your cases',
}
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: [x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment']
    # 1 signed out: the sign-in notice, Help & About, the full privacy notice and the terms
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.goto('https://sorted.test/#help'); wait(pg, 600)
    pg.goto('https://sorted.test/#signin'); wait(pg, 500)
    if pg.locator('[data-a=privacy]').count(): pg.locator('[data-a=privacy]').first.click(); wait(pg, 300)
    body = pg.inner_text('body')
    pg.goto('https://sorted.test/#help'); wait(pg, 500); body += '\n' + pg.inner_text('body')
    ok(pg.evaluate("localStorage.getItem('__seenTouch')") is None, 'signed out, nothing is recorded as seen')
    pg.goto('https://sorted.test/#start'); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    pg.locator('[data-a=data]').first.click(); wait(pg, 400)
    for tab in ('acct-you', 'acct-settings', 'help'):
        pg.click('.acct112-nav [data-v=%s]' % tab); wait(pg, 300)
        if pg.locator('[data-a=privacy]').count(): pg.locator('[data-a=privacy]').first.click(); wait(pg, 300)
        pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
        body += '\n' + pg.inner_text('body')
    for w in WRONG: ok(w not in body, 'gone: “%s”' % w)
    for k, v in RIGHT.items(): ok(v in body, 'present, %s' % k)
    ok('Usage records' in body and 'Don’t record my usage' in body, 'Settings calls them usage records')
    # 2 opening Sorted signed in records "seen" once per load
    ok(pg.evaluate("+localStorage.getItem('__seenTouch')") == 1, 'opening Sorted signed in calls touch_seen once')
    pg.goto('https://sorted.test/'); wait(pg, 600)
    ok(pg.evaluate("+localStorage.getItem('__seenTouch')") == 2, 'a new load calls it again, once')
    pg.locator('[data-a=data]').first.click(); wait(pg, 300); pg.locator('[data-a=home]').first.click(); wait(pg, 300)
    ok(pg.evaluate("+localStorage.getItem('__seenTouch')") == 2, 'moving around the app does not')
    # 3 a case started, then deleted, then the Undo banner says when the chance ends
    pg.goto('https://sorted.test/'); wait(pg, 500)
    if pg.locator('[data-cap82=other]').count(): pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg)
    elif pg.locator('[data-a=compose]').count(): pg.locator('[data-a=compose]').first.evaluate('e=>e.click()'); wait(pg)
    fri = datetime.date.today() + datetime.timedelta(days=(4 - datetime.date.today().weekday()) % 7 or 7)
    pg.fill('#f-case', 'Currys said they would refund £89 by %s, order 445566' % fri.strftime('%A')); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    cid = cases()[-1]['id']
    # 4 the guest copy is about access
    pg.goto('https://sorted.test/'); wait(pg, 500); m = pg.inner_text('main')
    ok('Saved on Sorted’s servers, to an account only this phone can open' in m or 'only this browser holds the key' in m, 'the guest note says the cases are on the server and only this browser can open them')
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 500)
    pg.evaluate("document.querySelectorAll('details.case56-more').forEach(d=>d.open=true)")
    pg.click('[data-a=panel][data-p=delcase]'); wait(pg, 300); pg.click('[data-a=case-del]'); wait(pg, 700)
    m = pg.inner_text('main')
    ok('Undo works for two minutes, on this page only: closing or refreshing it, or tapping anything else, ends that.' in m, 'the Undo banner says when the chance ends')
    ok(not [c for c in cases() if c['id'] == cid], 'the case left the server at once')
    pg.reload(); wait(pg, 600)
    ok(pg.locator('[data-a=del-undo]').count() == 0 and not [c for c in cases() if c['id'] == cid], 'a refresh ends the chance to undo, as the copy says')
    # 5 a device that was offline with an edit must not bring back a case deleted elsewhere
    if pg.locator('[data-cap82=other]').count(): pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg)
    elif pg.locator('[data-a=compose]').count(): pg.locator('[data-a=compose]').first.evaluate('e=>e.click()'); wait(pg)
    pg.fill('#f-case', 'Sky said an engineer would come on %s between 8 and 12, ref AB123' % fri.strftime('%A')); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    cid2 = cases()[-1]['id']
    pg.goto('https://sorted.test/?task=%s' % cid2); wait(pg, 600)
    pg.evaluate("localStorage.setItem('__failWrites','1')")     # this phone goes offline
    pg.evaluate("document.querySelectorAll('details.case56-more').forEach(d=>d.open=true)")
    pg.click('[data-a=panel][data-p=rename]'); wait(pg, 250); pg.fill('#f-rename', 'Edited while offline'); pg.click('form[data-f=rename] button[type=submit]'); wait(pg, 400)
    ok(pg.locator('main .sync114').inner_text().startswith('Saved on this phone, not yet sent'), 'the offline edit is pending on this phone')
    pg.evaluate("(id)=>{var d=JSON.parse(localStorage.getItem('__mockdb'));d.tasks=d.tasks.filter(x=>x.data.id!==id);localStorage.setItem('__mockdb',JSON.stringify(d))}", cid2)   # deleted on the laptop
    pg.evaluate("localStorage.removeItem('__failWrites')"); pg.evaluate("window.dispatchEvent(new Event('online'))"); wait(pg, 900)
    ok(not [c for c in cases() if c['id'] == cid2], 'back online, the pending edit does not bring the deleted case back to the server')
    ok('deleted on another device' in pg.inner_text('body'), 'and this phone is told')
    pg.goto('https://sorted.test/'); wait(pg, 500)
    ok('Edited while offline' not in pg.inner_text('main'), 'the case is gone from Home too')
    print('CHECKS', n[0])
    b.close()
# 6 the reminder email is built from fixed copy, the links and the ids: no field of the case reaches the body
src = open(HERE + '/supabase/functions/send-reminders/index.ts', encoding='utf8').read()
loop = src[src.index('for (const r of (due'):src.index('// 3. Nudge')]
bodies = re.findall(r'const (?:text|hb) = (.*)', loop)
used = set(re.findall(r'\$\{([^}]*)\}', ' '.join(bodies)))
bad = [u for u in used if re.match(r'\s*(t|open|openMv|target|row)\b', u)]
ok(len(bodies) == 2 and not bad, 'the reminder email body uses no case field: %s' % sorted(used))
ok('submitted_at' in loop and loop.index('submitted_at') < loop.index('await send('), 'each reminder records when it was handed to Resend, before the call')
print('ERRORS', errs); print('FAILS', fails)
