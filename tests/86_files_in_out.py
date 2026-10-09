# v128: files in and out on a phone. Out: the adviser pack, "Download my cases" and "Add to calendar" each save a file
# with the right name, type and contents; the link stays usable for a minute (an iPhone asks "Download?" first); the
# message says what happened, never "Downloaded" before it is; on a phone with a share sheet the file goes through the
# share sheet (so "Save to Files" or the calendar can take it), and cancelling says "Not saved." In: a photo picked
# from Files or Google Drive with no type is read by its name; an iPhone HEIC photo is converted on the phone where the
# browser can open it, and refused with a way out where it can't.
import os, sys, json, re, base64, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); O = HERE + '/tests/node_modules/'; errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
H = {'Access-Control-Allow-Origin': '*'}
def cdn(r):
    u = r.request.url
    if '/npm/tesseract.js@5.1.1/dist/' in u: return r.fulfill(path=O + 'tesseract.js/dist/' + u.split('/dist/')[1], content_type='application/javascript', headers=H)
    if '/npm/tesseract.js-core@5.1.1/' in u: f = u.split('@5.1.1/')[1]; return r.fulfill(path=O + 'tesseract.js-core/' + f, content_type='application/wasm' if f.endswith('.wasm') else 'application/javascript', headers=H)
    if '/npm/@tesseract.js-data/eng@1.0.0/' in u: return r.fulfill(path=O + '@tesseract.js-data/eng/4.0.0_best_int/eng.traineddata.gz', content_type='application/gzip', headers=H)
    return r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript')
NOTICE = ('<body style="margin:0;background:#fff;font-family:Arial;font-size:20px;line-height:1.5;padding:24px"><b>LAMBETH COUNCIL</b><br><b>PENALTY CHARGE NOTICE</b><br>'
          'PCN Number: LJ12345678<br>Vehicle registration: AB12 CDE<br>Date of contravention: 03/10/2026<br>Penalty charge: £130, reduced to £65 if paid within 14 days</body>')
def read_wait(pg):
    st = ''
    for _ in range(240):
        st = (pg.inner_text('#ocr-status') if pg.locator('#ocr-status').count() else '')
        if re.search(r'Photo read|couldn’t|doesn’t look|can’t read|isn’t a picture', st): return st.strip()
        wait(pg, 500)
    return st.strip()
fri = datetime.date.today() + datetime.timedelta(days=(4 - datetime.date.today().weekday()) % 7 or 7)
with sync_playwright() as p:
    b = p.chromium.launch()
    sp = b.new_page(viewport={'width': 560, 'height': 420}); sp.set_content(NOTICE); sp.screenshot(path=HERE + '/tests/out/doc86_notice.png'); sp.close()
    PNG = open(HERE + '/tests/out/doc86_notice.png', 'rb').read()
    def context(touch=False):
        c = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844}, accept_downloads=True, has_touch=touch, is_mobile=touch)
        c.route('https://cdn.jsdelivr.net/**', cdn)
        c.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
        return c
    def start_case(pg):
        pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
        pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', 'Currys said they would refund £89 by %d %s, order 445566' % (fri.day, fri.strftime('%B'))); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
        if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
        return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks.map(x=>x.data).filter(x=>x.kind!=='moment').pop().id")
    toast = lambda pg: pg.inner_text('#toast') if pg.locator('#toast').count() else ''
    # ================= OUT, on a computer: downloads =================
    ctx = context(); pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    cid = start_case(pg)
    # the adviser pack
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600)
    pg.evaluate("window.__revoked=[];var _r=URL.revokeObjectURL;URL.revokeObjectURL=function(u){window.__revoked.push(u);return _r.call(URL,u)}")
    pg.locator('[data-a=panel][data-p=pack]').first.evaluate('e=>e.click()'); wait(pg, 400)
    with pg.expect_download() as dl: pg.click('[data-a=pack-download]')
    d = dl.value; txt = open(d.path(), encoding='utf-8').read()
    ok(d.suggested_filename.startswith('Sorted - ') and d.suggested_filename.endswith('.txt') and 'Currys' in txt and '445566' in txt, 'the adviser pack saves as a text file with the case in it (%s)' % d.suggested_filename)
    wait(pg, 1600)
    ok(pg.evaluate("window.__revoked.filter(u=>typeof u==='string'&&u.indexOf('blob:')===0).length") == 0, 'the link is still usable after more than a second, so an iPhone “Download?” question can be answered')
    t = toast(pg)
    ok('Downloaded' not in t and 'choose Download' in t and 'Files app' in t, 'the message says what to expect, not “Downloaded” (%s)' % t)
    # the calendar
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600); pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
    calb = pg.locator('[data-a=cal]')
    ok(calb.count() >= 1, 'the case offers “Add to calendar”')
    if calb.count():
        with pg.expect_download() as dl: calb.first.click()
        d = dl.value; ics = open(d.path(), encoding='utf-8').read()
        ok(d.suggested_filename == 'sorted-reminder.ics' and 'BEGIN:VCALENDAR' in ics and 'BEGIN:VEVENT' in ics, 'the calendar reminder saves as an .ics file')
        ok('calendar' in toast(pg).lower(), 'and says it should offer to add it to the calendar')
    # all my cases
    pg.goto('https://sorted.test/'); wait(pg, 600); pg.locator('[data-a=data]').first.evaluate('e=>e.click()'); wait(pg, 500)
    with pg.expect_download() as dl: pg.click('[data-a=export-file]')
    d = dl.value; allt = open(d.path(), encoding='utf-8').read()
    ok(d.suggested_filename == 'Sorted - all my cases.txt' and 'Currys' in allt and 'Your cases from Sorted' in allt, '“Download my cases” saves every case as text')
    ctx.close()
    # ================= OUT, on a phone: the share sheet =================
    ctx = context(touch=True); pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.add_init_script("window.__shared=[];window.__shareMode='ok';navigator.canShare=function(d){return !!(d&&d.files&&d.files.length)};navigator.share=function(d){var f=d.files[0];return f.text().then(function(t){window.__shared.push({name:f.name,type:f.type,size:f.size,text:t});if(window.__shareMode==='cancel'){var e=new Error('x');e.name='AbortError';throw e}})}")
    cid = start_case(pg)
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600)
    pg.locator('[data-a=panel][data-p=pack]').first.evaluate('e=>e.click()'); wait(pg, 400)
    pg.click('[data-a=pack-download]'); wait(pg, 700)
    ok(pg.locator('#dl139 [data-a=dl-ready]').count() == 1, 'v139: on a phone the prepared file waits for a tap, since a share sheet needs one')
    pg.click('[data-a=dl-ready]'); wait(pg, 600)
    sh = pg.evaluate("window.__shared")
    ok(len(sh) == 1 and sh[0]['name'].endswith('.txt') and sh[0]['type'].startswith('text/plain') and 'Currys' in sh[0]['text'], 'on a phone the pack goes to the share sheet as a text file (%s)' % (sh and sh[0]['name']))
    ok('Save to Files' in toast(pg), 'and the message points at “Save to Files”')
    pg.evaluate("window.__shareMode='cancel'"); pg.click('[data-a=pack-download]'); wait(pg, 700); pg.click('[data-a=dl-ready]'); wait(pg, 600)
    ok(toast(pg).startswith('Not saved'), 'cancelling the share sheet says “Not saved.”')
    pg.evaluate("window.__shareMode='ok'")
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600); pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
    if pg.locator('[data-a=cal]').count():
        pg.locator('[data-a=cal]').first.click(); wait(pg, 600)
        sh = pg.evaluate("window.__shared")
        ok(sh[-1]['name'] == 'sorted-reminder.ics' and sh[-1]['type'] == 'text/calendar' and 'BEGIN:VEVENT' in sh[-1]['text'], 'on a phone the calendar reminder goes to the share sheet as a calendar file')
    ctx.close()
    # ================= IN: picked files =================
    ctx = context(); pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    def parking_flow():
        pg.goto('https://sorted.test/'); wait(pg, 500)
        if pg.locator('[data-a=new-case]').count(): pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', 'PCN'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 500)
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear()"); pg.reload(); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    parking_flow()
    pg.set_input_files('input[data-ocr=f-case]', {'name': 'IMG_2044.JPG', 'mimeType': '', 'buffer': PNG}); st = read_wait(pg)
    ok('Photo read' in st and pg.input_value('#doc-ref') == 'LJ12345678', 'a photo from Files or Google Drive with no type is read by its name (%s)' % st[:40])
    parking_flow()
    pg.set_input_files('input[data-ocr=f-case]', {'name': 'IMG_2045.HEIC', 'mimeType': 'image/heic', 'buffer': PNG}); st = read_wait(pg)
    ok('Photo read' in st and pg.input_value('#doc-ref') == 'LJ12345678', 'an iPhone HEIC photo is converted on the phone and read where the browser can open it (%s)' % st[:40])
    parking_flow()
    pg.set_input_files('input[data-ocr=f-case]', {'name': 'IMG_2046.heic', 'mimeType': 'image/heic', 'buffer': b'\x00\x00\x00\x18ftypheic'}); st = read_wait(pg)
    ok('can’t read HEIC' in st and pg.locator('#ocr-status[role=alert]').count() == 1, 'where the browser can’t open HEIC, it says so with a way out (%s)' % st[:50])
    parking_flow()
    pg.set_input_files('input[data-ocr=f-case]', {'name': 'notes.docx', 'mimeType': '', 'buffer': b'PK\x03\x04'}); st = read_wait(pg)
    ok('isn’t a picture or a PDF' in st, 'a file that is neither a picture nor a PDF is turned away clearly')
    ctx.close()
    ok(not errs, 'no page errors: %s' % errs)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
