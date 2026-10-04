# v121: a photo is evidence, what Sorted reads from it is a candidate. Through the real reader (Tesseract, served
# locally): a clear notice goes to "Check the notice" with every field editable, nothing is a case fact until "These
# are right, continue", and the case then carries confirmed facts from the photo (no proposal card, no promise, no
# refund reading); a partial notice shows what was found and asks for the rest without inventing it; a blurry photo
# and a near-blank photo say "We couldn’t read this photo clearly. Your case hasn’t been changed." with retake, another
# file and manual entry, and create nothing; retail text in the parking flow says it doesn't look like a notice and
# never becomes a refund case; an SMS screenshot in the ordinary flow still fills the box; a PDF notice gets the same
# review; a double tap on continue makes one case; manual entry after a failed read and a better photo after a failed
# read both recover; a refresh during review creates nothing; the original image is never sent anywhere; HEIC is
# refused with a way out; the status lives in a live region and a failure is an alert; the copy no longer promises
# that notices are read in full. docAssess() is also checked directly on garbled text over 8 characters.
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); O = HERE + '/tests/node_modules/'; errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
H = {'Access-Control-Allow-Origin': '*'}
posted = []
def cdn(r):
    u = r.request.url
    if '/npm/tesseract.js@5.1.1/dist/' in u: return r.fulfill(path=O + 'tesseract.js/dist/' + u.split('/dist/')[1], content_type='application/javascript', headers=H)
    if '/npm/tesseract.js-core@5.1.1/' in u: f = u.split('@5.1.1/')[1]; return r.fulfill(path=O + 'tesseract.js-core/' + f, content_type='application/wasm' if f.endswith('.wasm') else 'application/javascript', headers=H)
    if '/npm/@tesseract.js-data/eng@1.0.0/' in u: return r.fulfill(path=O + '@tesseract.js-data/eng/4.0.0_best_int/eng.traineddata.gz', content_type='application/gzip', headers=H)
    if '/npm/pdfjs-dist@' in u: f = u.split('/npm/pdfjs-dist@3.11.174/')[1]; return r.fulfill(path=O + 'pdfjs-dist/' + f, content_type='application/javascript', headers=H)
    return r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript')
def shot(b, path, html, w=560, h=420):
    sp = b.new_page(viewport={'width': w, 'height': h}); sp.set_content(html); sp.screenshot(path=path); sp.close()
def read_wait(pg):
    for _ in range(240):
        st = (pg.inner_text('#ocr-status') if pg.locator('#ocr-status').count() else '') + ' ' + (pg.inner_text('#doc-status') if pg.locator('#doc-status').count() else '')
        if re.search(r'Photo read|couldn’t|doesn’t look|Done\.|can’t read', st): wait(pg, 700); return st.strip()
        wait(pg, 500)
    return st
NOTICE_HTML = ('<body style="margin:0;background:#fff;font-family:Arial;font-size:20px;line-height:1.5;padding:24px"><b>LAMBETH COUNCIL</b><br><b>PENALTY CHARGE NOTICE</b><br>'
               'PCN Number: LJ12345678<br>Vehicle registration: AB12 CDE<br>Date of contravention: 03/10/2026<br>Time: 10:15<br>Location: Brixton Road<br>'
               'Penalty charge: £130, reduced to £65 if paid within 14 days.</body>')
PARTIAL_HTML = ('<body style="margin:0;background:#fff;font-family:Arial;font-size:20px;line-height:1.5;padding:24px"><b>WESTMINSTER CITY COUNCIL</b><br><b>PENALTY CHARGE NOTICE</b><br>'
                'PCN Number: WT12345678<br>Date of contravention: 04/10/2026</body>')
RETAIL_HTML = ('<body style="margin:0;background:#fff;font-family:Arial;font-size:20px;line-height:1.5;padding:24px">Currys<br>Thank you for your order 445566.<br>'
               'Your refund of £89 will be processed within 5 working days.<br>Keep this receipt for your records.</body>')
BLUR_HTML = ('<body style="margin:0;background:#fff;font-family:Arial;font-size:20px;line-height:1.5;padding:24px;filter:blur(3.5px)"><b>LAMBETH COUNCIL</b><br><b>PENALTY CHARGE NOTICE</b><br>'
             'PCN Number: LJ12345678<br>Vehicle registration: AB12 CDE<br>Date of contravention: 03/10/2026<br>Penalty charge: £130</body>')
GLARE_HTML = ('<body style="margin:0;background:linear-gradient(135deg,#fff 20%,#eee 45%,#777 60%,#fff 75%);font-family:Arial;font-size:11px;line-height:1.1;padding:4px;color:#bbb;letter-spacing:4px">'
              'P E N A L T Y   N O T I C E<br>' + 'x ' * 40 + '<br>1l|l1 0O0 Il1| |l0O <br>' + '~ ` ^ ; : , . ' * 12 + '</body>')
SMS_HTML = '<body style="margin:0;background:#fff;font-family:Arial"><div style="margin:20px;padding:14px 16px;background:#e9e9eb;border-radius:18px;font-size:17px;line-height:1.35;color:#111;max-width:320px">British Gas: Your engineer visit is booked for Tuesday 13 October between 8am and 12pm. Your reference is BG-77120. Reply STOP to opt out.</div></body>'
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', cdn)
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    ctx.on('request', lambda rq: posted.append(rq.url) if rq.method in ('POST', 'PUT') and 'sorted.test' not in rq.url else None)
    os.makedirs(HERE + '/tests/out', exist_ok=True)
    P = {k: HERE + '/tests/out/doc77_%s.png' % k for k in ('notice', 'partial', 'retail', 'blur', 'glare', 'sms')}
    shot(b, P['notice'], NOTICE_HTML); shot(b, P['partial'], PARTIAL_HTML); shot(b, P['retail'], RETAIL_HTML); shot(b, P['blur'], BLUR_HTML); shot(b, P['glare'], GLARE_HTML, 400, 260); shot(b, P['sms'], SMS_HTML, 390, 300)
    pdfp = b.new_page(); pdfp.set_content(NOTICE_HTML); pdfp.pdf(path=HERE + '/tests/out/doc77_notice.pdf'); pdfp.close()
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    events = lambda: [e['name'] for e in dbj().get('pilot_events', [])]
    main = lambda: pg.inner_text('main')
    def parking_flow():
        pg.goto('https://sorted.test/'); wait(pg, 500)
        if pg.locator('[data-a=new-case]').count(): pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', 'PCN'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 500)
        assert pg.locator('.pk-short').count() == 1
    def photo(path): pg.set_input_files('input[data-ocr=f-case]', path); return read_wait(pg)
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    # 0 the copy
    pg.locator('[data-cap82=document]').first.evaluate('e=>e.click()'); wait(pg, 300); m = main()
    ok('read in full' not in m and 'Sorted tries to read the notice. Check the details before continuing.' in m, 'the document door no longer promises notices are read in full')
    ok(pg.locator('#ocr-status[role=status]').count() == 1, 'the document door has its own status region')
    # 1 a clear notice: review, every field editable, nothing until confirmed
    parking_flow(); n0 = len(cases()); st = photo(P['notice'])
    ok('Photo read. Check the details below.' in st, 'a clear notice: "Photo read. Check the details below." (%s)' % st[:60])
    m = main()
    ok('Check the notice' in m and 'Sorted found these. Check them against the notice before continuing.' in m and 'Nothing becomes a case fact until you confirm.' in m, 'the review screen')
    vals = {k: pg.input_value('#doc-' + k) for k in ('issuer', 'ref', 'vrm', 'when', 'amount', 'discount')}
    ok(vals['issuer'] == 'Lambeth Council' and vals['ref'] == 'LJ12345678' and vals['vrm'] == 'AB12 CDE' and '3 Oct' in vals['when'] and vals['amount'] == '£130' and vals['discount'].startswith('£65'), 'issuer, PCN number, vehicle, date, amount and discount read as candidates: %s' % vals)
    ok(len(cases()) == n0 and pg.input_value('#f-case') == 'PCN' and 'document_read_succeeded' in events() and 'document_review_confirmed' not in events(), 'nothing is a case yet, the box is untouched, the read is counted')
    ok(not any(re.search(r'LJ12345678|Lambeth', json.dumps(e.get('props') or {})) for e in dbj().get('pilot_events', [])), 'no OCR text or PCN number in usage records')
    pg.fill('#doc-vrm', 'AB12 CDF')
    pg.click('form[data-f=doc] button[type=submit]'); pg.click('form[data-f=doc] button[type=submit]') if pg.locator('form[data-f=doc]').count() else None; wait(pg, 700)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 600)
    cs = cases()
    ok(len(cs) == n0 + 1, 'one case from a double tap on continue')
    c = cs[-1]; f = c.get('cf', {}).get('f', {})
    ok(f.get('ref', {}).get('v') == 'LJ12345678' and f['ref']['st'] == 'confirmed' and f['vrm']['v'] == 'AB12 CDF' and f['vrm']['how'] == 'you' and f['issuer']['v'] == 'Lambeth Council' and f['amount']['v'] == '£130' and all(x['src'] == 'the photo you added' for x in f.values()), 'the case carries the confirmed candidates, the corrected vehicle marked as yours, all from the photo')
    ok(pg.locator('.cf-check').count() == 0 and pg.locator('.cf-facts').count() == 1 and not c['promises'] and 'refund' not in c['title'].lower() and 'Currys' not in c['title'], 'no proposal card, no promise, a parking case: %r' % c['title'])
    ok(any('checked by you' in (e.get('label') or '') for e in c['events']) and 'document_review_confirmed' in events(), 'the history says the details came from a photo and were checked')
    # 2 a partial notice: found fields shown, missing asked for, nothing invented
    parking_flow(); st = photo(P['partial'])
    ok('Photo read' in st and 'Sorted read part of it' in main() and pg.input_value('#doc-issuer') == 'Westminster City Council' and pg.input_value('#doc-ref') == 'WT12345678' and pg.input_value('#doc-vrm') == '' and 'not found' in main(), 'a partial read shows what was found and asks for the rest')
    ok('document_read_partial' in events(), 'counted as partial')
    pg.click('form[data-f=doc] button[type=submit]'); wait(pg, 700)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 600)
    c2 = cases()[-1]; f2 = c2['cf']['f']
    ok('vrm' not in f2 and 'amount' not in f2 and f2['ref']['v'] == 'WT12345678', 'the missing fields stay missing, never invented')
    # 3 a blurry notice, and a glare-and-noise photo: failure, nothing changed
    for key in ('blur', 'glare'):
        parking_flow(); n0 = len(cases()); st = photo(P[key]); m = main()
        failed = 'couldn’t read this photo clearly' in st or 'doesn’t look like a parking notice' in st
        ok(failed and pg.locator('.doc121-fail [role=alert]').count() == 1 and 'Your case hasn’t been changed.' in m, '%s photo: a clear failure, announced (%s)' % (key, st[:70]))
        ok(pg.locator('.doc121-fail input[capture]').count() == 1 and 'Choose another file' in m and 'Enter the details manually' in m and 'continue' not in pg.inner_text('.doc121-fail').lower(), '%s photo: retake, another file or manual entry, and no Continue' % key)
        ok(len(cases()) == n0 and pg.input_value('#f-case') == 'PCN' and 'Currys' not in m and pg.locator('.doc121-review').count() == 0, '%s photo: no case, no title, no review, the box untouched' % key)
    ok('document_read_failed' in events(), 'failures are counted')
    # 4 manual entry after a failed read recovers; a better photo after a failed read recovers
    pg.click('[data-a=doc-manual]'); wait(pg, 700)
    ok(pg.locator('.doc121').count() == 0 and pg.evaluate("document.activeElement&&document.activeElement.id") == 'f-case' and 'document_manual_fallback' in events(), 'manual entry puts you in the box with the failure gone')
    pg.fill('#f-case', 'Lambeth Council PCN LJ22223333, vehicle AB12 CDE, contravention 03/10/2026, £130'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
    if pg.locator('[data-a=pk-short-go]').count(): pg.click('[data-a=pk-short-go]'); wait(pg, 500)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 600)
    ok(cases()[-1].get('cf') and cases()[-1]['cf']['f'].get('ref', {}).get('v') == 'LJ22223333', 'typed details after a failed read make the case as usual')
    parking_flow(); photo(P['glare']); ok(pg.locator('.doc121-fail').count() == 1, 'a failed read')
    st = photo(P['notice'])
    ok('Photo read' in st and pg.locator('.doc121-fail').count() == 0 and pg.input_value('#doc-ref') == 'LJ12345678', 'a better photo replaces the failure; nothing of the bad read survives')
    # 5 retail text in the parking flow never becomes a refund
    parking_flow(); n0 = len(cases()); st = photo(P['retail']); m = main()
    ok('doesn’t look like a parking notice' in st and 'This doesn’t look like a parking notice. Your case hasn’t been changed.' in m and len(cases()) == n0, 'retail text in the parking flow: not a notice, nothing created')
    ok('Currys' not in m and 'refund' not in pg.inner_text('.doc121-fail').lower() and pg.locator('form[data-f=baseline], .sug-card, .cf-check').count() == 0 and pg.input_value('#f-case') == 'PCN', 'and it never becomes a refund case')
    # 6 a refresh during review creates nothing and leaves a clean start
    parking_flow(); photo(P['notice']); ok(pg.locator('.doc121-review').count() == 1, 'review on screen'); n0 = len(cases())
    pg.reload(); wait(pg, 800)
    ok(len(cases()) == n0 and pg.locator('.doc121-review').count() == 0 and pg.locator('.cf-check').count() == 0, 'a refresh during review: no case, no half-review')
    # 7 the ordinary document flow: an SMS screenshot still fills the box for checking
    pg.goto('https://sorted.test/'); wait(pg, 500)
    if pg.locator('[data-a=new-case]').count(): pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.locator('[data-cap82=document]').first.evaluate('e=>e.click()'); wait(pg, 300)
    st = photo(P['sms'])
    ok(st.startswith('Done') and 'BG-77120' in pg.input_value('#f-case') and pg.locator('.doc121').count() == 0, 'an SMS screenshot in the ordinary flow fills the box to check, as before')
    # 8 a PDF notice: the same review
    parking_flow(); pg.set_input_files('input[data-ocr=f-case]', HERE + '/tests/out/doc77_notice.pdf'); st = read_wait(pg)
    ok('Photo read' in st and pg.locator('.doc121-review').count() == 1 and pg.input_value('#doc-ref') == 'LJ12345678', 'a PDF notice gets the same review (%s)' % st[:50])
    # 9 HEIC is refused with a way out; privacy
    parking_flow(); pg.set_input_files('input[data-ocr=f-case]', {'name': 'IMG_1.heic', 'mimeType': 'image/heic', 'buffer': b'\x00\x00\x00\x18ftypheic'}); wait(pg, 400)
    ok('can’t read HEIC' in (pg.inner_text('#ocr-status') if pg.locator('#ocr-status').count() else '') and pg.locator('#ocr-status[role=alert]').count() == 1, 'HEIC is refused with a way out, as an alert')
    ok(not [u for u in posted if 'sorted.test' not in u and 'cdn.jsdelivr' not in u], 'no image or text was posted anywhere: %s' % posted[:3])
    # 10 the quality judgement on garbled text over 8 characters, directly
    rp = ctx.new_page(); rp.route(lambda u: u.startswith('https://sorted.test/'), lambda q: q.fulfill(path=HERE + '/tests/out/reader.html', content_type='text/html'))
    rp.goto('https://sorted.test/'); rp.wait_for_function('window.__read&&window.__read.docAssess')
    rd = rp.evaluate("""()=>{
      var fn=window.__read.docAssess;
      if(!fn)return null;
      return {garble:fn('a;lskdjf 09q8w e0r98 ∆˚¬ 1l|Il| ,.;: ~ ^ ;; qwpeoi zxcvm',52,'pcn').status, short:fn('PCN £130',90,'pcn').status, retail:fn('Currys. Thank you for your order 445566. Your refund of £89 will be processed within 5 working days.',92,'pcn').status, good:fn('LAMBETH COUNCIL PENALTY CHARGE NOTICE PCN Number: LJ12345678 Vehicle registration: AB12 CDE Date of contravention: 03/10/2026 Penalty charge: £130',90,'pcn').status, lowconf:fn('LAMBETH COUNCIL PENALTY CHARGE NOTICE PCN Number LJ12345678 vehicle AB12 CDE',20,'pcn').status}
    }""")
    ok(rd is not None and rd['garble'] == 'failed' and rd['short'] == 'failed' and rd['retail'] == 'notpcn' and rd['good'] == 'ok', 'docAssess: garbled text over 8 characters fails, a few words fail, retail text is not a notice, a real notice is ok (%s)' % rd)
    ok(rd is not None and rd['lowconf'] in ('failed', 'partial', 'ok'), 'docAssess: a low-confidence read is never promoted to ok without the fields (%s)' % (rd and rd['lowconf']))
    ok(not errs, 'no page errors: %s' % errs[:2])
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
