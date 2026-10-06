# v139: downloads carry the kept documents. With documents kept, "Download my cases" is one .zip made on the phone:
# "Sorted - all my cases.txt" plus a numbered folder per case with its documents as they are; the record lists each
# document with the path inside the download. A case record's "Download it" does the same for one case (a Documents
# folder). With no documents it stays one text file. A document that can't be fetched, or that would take the download
# past 60 MB, is left out and the record says so and why. The zip is valid (checked here with Python's zipfile). On a
# phone the prepared file waits behind "Save or share it", because a share sheet needs a fresh tap.
import os, sys, datetime, zipfile, io, shutil, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
OUT = HERE + '/tests/out'
open(OUT + '/letter95.pdf', 'wb').write(b'%PDF-1.4\n% a letter\n' + b'0' * 2000)
open(OUT + '/photo95.png', 'wb').write(b'\x89PNG\r\n\x1a\n' + b'0' * 2000)
fri = datetime.date.today() + datetime.timedelta(days=(4 - datetime.date.today().weekday()) % 7 or 7)
with sync_playwright() as p:
    b = p.chromium.launch()
    def context(touch=False):
        c = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844}, accept_downloads=True, has_touch=touch, is_mobile=touch)
        c.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
        c.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
        return c
    ctx = context(); pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    tap = lambda a: (pg.locator('.tab129 [data-a=%s]' % a).click(), wait(pg, 500))
    def start(text):
        tap('new-case'); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
        if pg.locator('[data-a=nudge-skip]').count(): pg.click('[data-a=nudge-skip]'); wait(pg, 300)
        return cases()[-1]['id']
    def opencase(cid):
        pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700)
        pg.evaluate("document.querySelectorAll('details.case75-group').forEach(d=>d.open=true)"); wait(pg, 200)
    def keep(cid, f): opencase(cid); pg.set_input_files('input[data-keepdoc="%s"]' % cid, f); wait(pg, 900)
    def more(): pg.goto('https://sorted.test/'); wait(pg, 600); tap('data')
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')")
    pg.goto('https://sorted.test/#start'); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    uid = pg.evaluate("JSON.parse(localStorage.getItem('__mocksession')).user.id")
    c1 = start('Currys said they would refund £89 by %s, order 445566' % fri.strftime('%A'))
    c2 = start('Evri said my parcel would arrive by %s, tracking EV1234567' % fri.strftime('%A'))
    # ---- no documents: still one text file ----
    more()
    with pg.expect_download() as dl: pg.click('[data-a=export-file]')
    d = dl.value
    ok(d.suggested_filename == 'Sorted - all my cases.txt', 'with no kept documents “Download my cases” is still one text file')
    ok('If you kept documents with your cases, it comes as one .zip file instead' in pg.inner_text('main'), 'Account says when it becomes a .zip')
    # ---- documents kept: one .zip ----
    keep(c1, OUT + '/letter95.pdf'); keep(c1, OUT + '/photo95.png'); keep(c2, OUT + '/letter95.pdf')
    st = pg.evaluate("JSON.parse(localStorage.getItem('__storage')||'[]')")
    ok(len(st) == 3, '(three documents kept, two with the first case)')
    more()
    with pg.expect_download() as dl: pg.click('[data-a=export-file]')
    d = dl.value; data = open(d.path(), 'rb').read()
    ok(d.suggested_filename == 'Sorted - all my cases.zip', 'with documents kept, it is one .zip file')
    z = zipfile.ZipFile(io.BytesIO(data)); names = z.namelist()
    ok(z.testzip() is None, 'the .zip is valid: every file’s checksum matches')
    if shutil.which('unzip'): r = subprocess.run(['unzip', '-t', d.path()], capture_output=True, text=True); ok(r.returncode == 0 and 'No errors detected' in r.stdout, 'and the ordinary unzip tool agrees: %s' % r.stdout.strip().splitlines()[-1:])
    ok('Sorted - all my cases.txt' in names, 'it holds the written record: %s' % names)
    f1 = [x for x in names if x.startswith('01 ')]; f2 = [x for x in names if x.startswith('02 ')]
    ok(len(f1) == 2 and len(f2) == 1 and any(x.endswith('/letter95.pdf') for x in f1) and any(x.endswith('/photo95.png') for x in f1) and f2[0].endswith('/letter95.pdf'), 'each case has a numbered folder with its own documents: %s' % names)
    p1 = [x for x in f1 if x.endswith('/letter95.pdf')][0]
    src = [s for s in st if s['name'].startswith('%s/%s/' % (uid, c1)) and s['name'].endswith('letter95.pdf')][0]['name']
    ok(z.read(p1) == ('mock file ' + src).encode(), 'each document is the stored file, unchanged')
    txt = z.read('Sorted - all my cases.txt').decode('utf-8')
    ok('DOCUMENTS KEPT WITH THIS CASE' in txt and ('in this download as “%s”' % p1) in txt, 'the record lists each document with where it is in the download')
    ok('Currys' in txt and 'EV1234567' in txt and 'Your cases from Sorted' in txt, 'the record has every case')
    ok(all(not x.startswith('/') and '..' not in x for x in names), 'no path in the .zip can escape its folder')
    # ---- one case: Download it ----
    opencase(c1); pg.click('[data-a=panel][data-p=pack]'); wait(pg, 400)
    with pg.expect_download() as dl: pg.click('[data-a=pack-download]')
    d = dl.value; z2 = zipfile.ZipFile(io.BytesIO(open(d.path(), 'rb').read())); n2 = z2.namelist()
    ok(d.suggested_filename.startswith('Sorted - ') and d.suggested_filename.endswith('.zip') and z2.testzip() is None, 'a case record with documents downloads as its own .zip: %s' % d.suggested_filename)
    ok(sorted(x for x in n2 if x.startswith('Documents/')) == ['Documents/letter95.pdf', 'Documents/photo95.png'] and len([x for x in n2 if x.endswith('.txt')]) == 1, 'with its record and a Documents folder: %s' % n2)
    ok('in this download as “Documents/letter95.pdf”' in z2.read([x for x in n2 if x.endswith('.txt')][0]).decode('utf-8'), 'the record points at the documents')
    # ---- a document that can't be fetched ----
    pg.evaluate("localStorage.setItem('__storageDlFail','1')")
    more()
    with pg.expect_download() as dl: pg.click('[data-a=export-file]')
    d = dl.value; t3 = open(d.path(), encoding='utf-8').read()
    ok(d.suggested_filename == 'Sorted - all my cases.txt' and 'couldn’t be added to this download; open it in Sorted' in t3, 'when no document can be fetched it falls back to the text file, and the record says which documents are missing')
    wait(pg, 300); ok('3 kept documents couldn’t be added' in pg.inner_text('#toast'), 'and the message says how many were left out')
    pg.evaluate("localStorage.removeItem('__storageDlFail')")
    # ---- too large for one download ----
    pg.evaluate("(a)=>{var s=JSON.parse(localStorage.getItem('__storage')||'[]');s.push({bucket:'originals',name:a+'/9999999999999-huge.pdf',size:70*1048576,type:'application/pdf',at:new Date().toISOString()});localStorage.setItem('__storage',JSON.stringify(s))}", '%s/%s' % (uid, c2))
    more()
    with pg.expect_download() as dl: pg.click('[data-a=export-file]')
    d = dl.value; z4 = zipfile.ZipFile(io.BytesIO(open(d.path(), 'rb').read())); t4 = z4.read('Sorted - all my cases.txt').decode('utf-8')
    ok(not any('huge.pdf' in x for x in z4.namelist()) and 'huge.pdf (70 MB' in t4 and 'too large to add to this download' in t4 and len(z4.namelist()) == 4, 'a document past the 60 MB limit is left out, and the record says so')
    ctx.close()
    # ---- on a phone: the prepared file waits for a tap ----
    ctx = context(touch=True); pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.add_init_script("window.__shared=[];navigator.canShare=function(d){return !!(d&&d.files&&d.files.length)};navigator.share=function(d){var f=d.files[0];window.__shared.push({name:f.name,type:f.type,size:f.size});return Promise.resolve()}")
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')")
    pg.goto('https://sorted.test/#start'); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    c5 = start('Amazon said they would refund £20 by %s, ref AMZ12345' % fri.strftime('%A'))
    keep(c5, OUT + '/photo95.png')
    more(); pg.click('[data-a=export-file]'); wait(pg, 900)
    ok(pg.locator('#dl139').count() == 1 and 'Your file is ready.' in pg.inner_text('#dl139') and 'Sorted - all my cases.zip' in pg.inner_text('#dl139'), 'on a phone the prepared .zip waits behind “Save or share it”')
    ok(pg.evaluate("document.activeElement&&document.activeElement.getAttribute('data-a')") == 'dl-ready' and not pg.evaluate("window.__shared.length"), 'focus is on the button, and nothing is shared before the tap')
    pg.click('[data-a=dl-ready]'); wait(pg, 500)
    sh = pg.evaluate("window.__shared")
    ok(len(sh) == 1 and sh[0]['name'] == 'Sorted - all my cases.zip' and sh[0]['type'] == 'application/zip' and pg.locator('#dl139').count() == 0, 'the tap hands the .zip to the share sheet')
    pg.click('[data-a=export-file]'); wait(pg, 900); pg.click('[data-a=dl-cancel]'); wait(pg, 300)
    ok(pg.locator('#dl139').count() == 0 and 'Not saved' in pg.inner_text('#toast') and len(pg.evaluate("window.__shared")) == 1, '“Not now” saves nothing and says so')
    ok(pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth+1"), 'nothing scrolls sideways')
    ok(not errs, 'no page errors: %s' % errs)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
