# v135: keep the original documents with a case. "Keep a document with this case" stores the file as it is under
# <user>/<case>/ in the private bucket, says so in the history, lists it with its date and size, opens it through a
# five-minute link, and removes it only after a second tap. Files that are too big, of the wrong kind or that fail to
# save are refused with a reason. Not offered on an example case. The privacy notice says what happens. The migration
# keeps the bucket private and each person in their own folder; the cleanup function removes files whose case has gone.
import os, sys, json, datetime, subprocess, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
today = datetime.date.today()
fri = today + datetime.timedelta(days=(4 - today.weekday()) % 7 or 7)
OUT = HERE + '/tests/out'
open(OUT + '/letter91.pdf', 'wb').write(b'%PDF-1.4\n% a letter\n' + b'0' * 3000)
open(OUT + '/note91.txt', 'w').write('not a document')
open(OUT + '/big91.pdf', 'wb').write(b'%PDF-1.4\n' + b'0' * (11 * 1024 * 1024))
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    store = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__storage')||'[]')")
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    tap = lambda a: (pg.locator('.tab129 [data-a=%s]' % a).click(), wait(pg, 500))
    def start(text):
        tap('new-case')
        pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
        return cases()[-1]['id']
    def opencase(cid):
        pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700)
        pg.evaluate("document.querySelectorAll('details.case75-group').forEach(d=>d.open=true)"); wait(pg, 200)
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')")
    pg.goto('https://sorted.test/#start'); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    uid = pg.evaluate("JSON.parse(localStorage.getItem('__mocksession')).user.id")
    c1 = start('Currys said they would refund £89 by %s, order 445566' % fri.strftime('%A'))
    opencase(c1)
    db = pg.locator('.docs135')
    ok(db.count() == 1 and 'None yet' in db.inner_text() and 'Only you can open it' in db.inner_text() and 'removed when this case is deleted' in db.inner_text(), 'a case offers “Keep a document with this case”, saying where it goes and who can open it')
    ok(not store(), 'nothing is stored until a document is chosen')
    pg.set_input_files('input[data-keepdoc="%s"]' % c1, OUT + '/letter91.pdf'); wait(pg, 900)
    st = store()
    ok(len(st) == 1 and st[0]['name'].startswith('%s/%s/' % (uid, c1)) and st[0]['name'].endswith('-letter91.pdf') and st[0]['type'] == 'application/pdf', 'the file is stored as it is, in this person’s folder for this case')
    c = [x for x in cases() if x['id'] == c1][0]
    ok(any(e['label'] == 'Kept a document with this case: letter91.pdf.' for e in c['events']), 'the history says a document was kept')
    opencase(c1); txt = pg.inner_text('.docs135')
    ok('letter91.pdf' in txt and 'KB' in txt, 'it is listed with its size')
    with ctx.expect_page() as pi: pg.click('.docs135 [data-a=doc-view]')
    pi.value.close()
    sg = pg.evaluate('window.__signed')
    ok(sg and sg[-1][0] == st[0]['name'] and sg[-1][1] == 300, 'Open uses a link that lasts five minutes')
    pg.click('.docs135 [data-a=doc-del]'); wait(pg, 300)
    ok(len(store()) == 1 and pg.locator('[data-a=doc-del-yes]').count() == 1, 'Remove asks once more before anything goes')
    pg.click('[data-a=doc-del-yes]'); wait(pg, 600)
    ok(not store() and any('Removed a kept document: letter91.pdf.' == e['label'] for e in [x for x in cases() if x['id'] == c1][0]['events']), 'Remove for good removes it, with a history line')
    # ---- refusals ----
    opencase(c1)
    pg.set_input_files('input[data-keepdoc="%s"]' % c1, OUT + '/note91.txt'); wait(pg, 500)
    ok('photos, screenshots and PDFs only' in pg.inner_text('.docs135') and not store(), 'another kind of file is refused with a reason')
    pg.set_input_files('input[data-keepdoc="%s"]' % c1, OUT + '/big91.pdf'); wait(pg, 700)
    ok('up to 10 MB' in pg.inner_text('.docs135') and not store(), 'a file over 10 MB is refused with its size')
    pg.evaluate("localStorage.setItem('__storageFail','1')"); pg.set_input_files('input[data-keepdoc="%s"]' % c1, OUT + '/letter91.pdf'); wait(pg, 700)
    ok('Couldn’t keep the document' in pg.inner_text('.docs135') and not store(), 'a failed save says so and keeps nothing')
    pg.evaluate("localStorage.removeItem('__storageFail')")
    # ---- an example case, and the notice ----
    pg.evaluate("(()=>{var b=document.createElement('button');b.setAttribute('data-a','example');document.body.appendChild(b);b.click()})()"); wait(pg, 700)
    ex = [x for x in cases() if x.get('example')]
    if ex:
        opencase(ex[0]['id']); ok(pg.locator('.docs135').count() == 0, 'an example case doesn’t offer to keep documents')
    src = open(HERE + '/public/index.html').read()
    ok('If you keep a document with a case, Sorted stores that file as it is, privately, so only you can open it, and removes it when the case is deleted' in src, 'the privacy notice says what happens to a kept document')
    sql = open(HERE + '/supabase/parked/21_originals_v135.sql').read()
    ok("'originals', 'originals', false, 10485760" in sql and sql.count("(storage.foldername(name))[1] = (select auth.uid())::text") == 3 and 'for update' not in sql and 'public = false' in sql, 'the bucket is private, 10 MB a file, each person only in their own folder, no updates')
    r = subprocess.run(['node', '--experimental-strip-types', HERE + '/tests/fn/originals_check.mjs'], capture_output=True, text=True)
    ok('FAILS []' in r.stdout and r.stdout.count('PASS') == 2, 'the cleanup function removes only files whose case has gone (run in Node)')
    ok(not errs, 'no page errors: %s' % errs)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
