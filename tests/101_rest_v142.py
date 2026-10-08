# v142: the rest of the audit.
#   - The "Stop all reminder emails" link in an email opens a question in Sorted; nothing changes until the tap, which
#     posts the signed token to email-stop; a refusal says nothing changed. Works signed out.
#   - Reminder rows carry promise_id and use the (task_id, kind, send_at, promise_id) key, so a promise and a step due
#     at the same minute both get one.
#   - "Evri said yesterday it would come tomorrow" is today.
#   - The service worker is registered at load only on Android (for the share sheet).
#   - The CSP names jsDelivr paths, not the whole host (test 13 runs the readers under it).
import os, sys, json, datetime, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
U = '11111111-2222-3333-4444-555555555555'; T = 'a' * 32
today = datetime.date.today()
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    posts = []; answer = {'status': 200}
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: '/functions/v1/email-stop' in u, lambda r: (posts.append((r.request.method, r.request.url)), r.fulfill(status=answer['status'], body='ok', headers={'Access-Control-Allow-Origin': '*'})))
    ctx.route(lambda u: u.startswith('https://sorted.test/reader'), lambda r: r.fulfill(path=HERE + '/tests/out/reader.html', content_type='text/html'))
    ctx.route(lambda u: u.startswith('https://sorted.test/') and not u.startswith('https://sorted.test/reader'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    # ---- the stop link ----
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear()")
    pg.goto('https://sorted.test/#stop=%s.%s' % (U, T)); wait(pg, 700)
    m = pg.inner_text('main')
    ok('Stop all reminder emails?' in m and pg.locator('[data-a=estop-yes]').count() == 1 and not posts, 'the link asks first and sends nothing: %s' % m[:120])
    ok('#stop=' not in pg.url and pg.title() == 'Stop reminder emails · Sorted', 'the token leaves the address bar, and the page has its title')
    pg.click('[data-a=estop-yes]'); wait(pg, 600)
    ok(len(posts) == 1 and posts[0][0] == 'POST' and ('u=%s' % U) in posts[0][1] and ('t=%s' % T) in posts[0][1], 'the tap posts the signed token to email-stop once')
    ok('Done. No more reminder emails.' in pg.inner_text('main') and pg.evaluate("document.activeElement&&document.activeElement.id") == 'estop-h', 'it says it is done, with focus on that')
    answer['status'] = 400; posts.clear()
    pg.goto('https://sorted.test/#stop=%s.%s' % (U, 'b' * 32)); wait(pg, 700); pg.click('[data-a=estop-yes]'); wait(pg, 600)
    ok('That didn’t work.' in pg.inner_text('main') and 'Nothing has changed' in pg.inner_text('main') and len(posts) == 1, 'a refused link says nothing changed')
    pg.goto('https://sorted.test/#stop=not-a-token'); wait(pg, 700)
    ok(pg.locator('[data-a=estop-yes]').count() == 0, 'a malformed link is ignored')
    # ---- reminder rows ----
    src = open(HERE + '/public/index.html').read()
    ok('"task_id,kind,send_at,promise_id"' in src and 'remUp144(' in src, 'reminder rows use the key with promise_id')
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')")
    pg.evaluate("localStorage.setItem('__mocksession', %s)" % json.dumps(json.dumps({'user': {'id': 'u-me', 'email': 'me@example.com'}}))); pg.goto('https://sorted.test/'); wait(pg, 700)
    fri = today + datetime.timedelta(days=(4 - today.weekday()) % 7 or 7)
    pg.locator('.tab129 [data-a=new-case]').click(); wait(pg, 400); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.fill('#f-case', 'Currys said they would refund £89 by %s, order 445566' % fri.strftime('%A')); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 800)
    db = pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    rem = db.get('reminders', [])
    ok(rem and all('promise_id' in x for x in rem), 'every reminder row says which promise or step it is for: %s' % [x.get('kind') for x in rem])
    # v143: before migration 24's index exists, the old key is used and nothing fails
    pg.evaluate("localStorage.setItem('__noPromiseKey','1');var d=JSON.parse(localStorage.getItem('__mockdb'));d.reminders=[];localStorage.setItem('__mockdb',JSON.stringify(d))")
    pg.goto('https://sorted.test/'); wait(pg, 700)
    pg.locator('.tab129 [data-a=new-case]').click(); wait(pg, 400); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.fill('#f-case', 'Argos said they would refund £40 by %s, order 778899' % fri.strftime('%A')); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 800)
    rem2 = (pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}).get('reminders', [])
    ok(rem2 and 'Couldn’t set' not in (pg.inner_text('#toast') if pg.locator('#toast').count() else ''), 'without the new index on the server, reminders still go in on the old key (%d rows)' % len(rem2))
    pg.evaluate("localStorage.removeItem('__noPromiseKey')")
    # ---- the reader ----
    pg.goto('https://sorted.test/reader'); wait(pg, 500)
    r = pg.evaluate("(t)=>{var x=window.__read,p=x.readCase(t,x.caseFacts(t));return p?{d:x.ymdL(new Date(p.dueAt)),past:!!p.past}:null}", 'Evri said yesterday it would come tomorrow')
    ok(r and r['d'] == today.isoformat() and not r['past'], '“said yesterday it would come tomorrow” is today: %s' % r)
    r = pg.evaluate("(t)=>{var x=window.__read,p=x.readCase(t,x.caseFacts(t));return p?x.ymdL(new Date(p.dueAt)):null}", 'They said yesterday the engineer would come the day after tomorrow')
    ok(r == (today + datetime.timedelta(days=1)).isoformat(), '“said yesterday … the day after tomorrow” is tomorrow: %s' % r)
    # ---- the service worker only on Android ----
    ok('/Android/i.test(navigator.userAgent' in src and 'navigator.serviceWorker.register("/sw.js",{scope:"/"}).catch' in src, 'the service worker is registered at load only on Android')
    vj = json.load(open(HERE + '/vercel.json'))
    csp = [h['value'] for h in vj['headers'][0]['headers'] if h['key'] == 'Content-Security-Policy'][0]
    ok(not re.search(r'https://cdn\.jsdelivr\.net(?:[;\s]|$)', csp) and 'https://cdn.jsdelivr.net/npm/tesseract.js@5.1.1/' in csp, 'the CSP names the pinned jsDelivr paths, not the whole host')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
