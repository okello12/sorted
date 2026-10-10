# v164: the Phase 1.5 audit of "Something I own isn't working" (docs/PHASE1_5_AUDIT.md). Phone-like label photos
# (tilted, sheared, compressed, blurred, glare, grey on silver, noisy, a full-size 4032 px photo) through the real reader:
# whatever happens, nothing is a fact before a tap, the serial is never shown in full, no page error, and each photo
# ends as read, make only, or a clear failure with routes (the read rates print as INFO, a wrong model as a FINDING).
# Then unreadable files (text, a 12 px image, HEIC), a receipt whose date is read wrong and corrected, a reading that
# never moves the route until confirmed, the serial in "Download my cases" and the calendar file, and the whole journey
# on to a missed promise: the chase names the product and the case keeps its product.
import os, sys, re, json, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *
O = HERE + '/tests/node_modules/'; Hh = {'Access-Control-Allow-Origin': '*'}
def cdn(r):
    u = r.request.url
    if '/npm/tesseract.js@5.1.1/dist/' in u: return r.fulfill(path=O + 'tesseract.js/dist/' + u.split('/dist/')[1], content_type='application/javascript', headers=Hh)
    if '/npm/tesseract.js-core@5.1.1/' in u: f = u.split('@5.1.1/')[1]; return r.fulfill(path=O + 'tesseract.js-core/' + f, content_type='application/wasm' if f.endswith('.wasm') else 'application/javascript', headers=Hh)
    if '/npm/@tesseract.js-data/eng@1.0.0/' in u: return r.fulfill(path=O + '@tesseract.js-data/eng/4.0.0_best_int/eng.traineddata.gz', content_type='application/gzip', headers=Hh)
    return r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript')
OUT = HERE + '/tests/out/'
LABEL = ('<body style="margin:0;background:#c9cdd2;font-family:Arial;padding:30px"><div style="background:#f4f4f2;border:2px solid #333;'
         'border-radius:8px;padding:18px 24px;width:520px;font-size:22px;line-height:1.45;color:#111"><b style="font-size:30px">BOSCH</b><br>'
         'Washing machine &nbsp; Serie 6<br>E-Nr. WGG244ZCGB/01 &nbsp; FD 2309<br>S/N: 123456789<br>220-240V ~ 50Hz 2300W<br>Made in Germany</div></body>')
SER = '123456789'
# Phone-like damage, made in the browser (no image library needed): CSS for tilt, shear, blur, contrast and glare,
# a canvas for noise, the screenshot's own JPEG quality, and the device scale for low and full resolution.
FX = {'tilt': 'transform:rotate(6deg)', 'shear': 'transform:skew(-7deg,3deg)', 'blur': 'filter:blur(1.6px)', 'grey': 'filter:contrast(0.45)'}
def degrade(b, how):
    html = LABEL
    if how in FX: html = html.replace('<div style="', '<div style="%s;' % FX[how], 1)
    if how == 'glare': html = html.replace('</body>', '<div style="position:fixed;inset:0;background:radial-gradient(circle at 70% 10%,rgba(255,255,255,.85),rgba(255,255,255,0) 55%)"></div></body>')
    if how == 'noise': html = html.replace('</body>', '<canvas id=n width=640 height=330 style="position:fixed;inset:0"></canvas><script>var c=document.getElementById("n").getContext("2d"),q=7,r=function(){q=(q*1103515245+12345)%2147483648;return q/2147483648};for(var i=0;i<17000;i++){var v=Math.floor(r()*256);c.fillStyle="rgb("+v+","+v+","+v+")";c.fillRect(r()*640,r()*330,1.5,1.5)}</script></body>')
    dsf = {'lowres': 0.6, 'big': 6.3}.get(how, 2)
    sp = b.new_page(viewport={'width': 640, 'height': 330}, device_scale_factor=dsf); sp.set_content(html); wait(sp, 200)
    path = OUT + 'audit131_%s.%s' % (how, 'jpg' if how == 'jpeg' else 'png')
    if how == 'jpeg': sp.screenshot(path=path, type='jpeg', quality=30)
    else: sp.screenshot(path=path)
    sp.close(); return path
def read_wait(pg):
    st = ''
    for _ in range(300):
        st = pg.inner_text('#ocr-status') if pg.locator('#ocr-status').count() else ''
        if re.search(r'Label read|found the make|couldn’t|can’t|isn’t a picture|Receipt read', st): wait(pg, 500); return st
        wait(pg, 500)
    return st
with sync_playwright() as p:
    a = App(p, email=True); pg = a.pg
    a.ctx.route('https://cdn.jsdelivr.net/**', cdn)
    sp = a.b.new_page(viewport={'width': 640, 'height': 330}, device_scale_factor=2); sp.set_content(LABEL); sp.screenshot(path=OUT + 'audit131_clean.png'); sp.close()
    def door():
        a.home(); a.tap('new-case'); pg.locator('[data-cap82=fix]').first.evaluate('e=>e.click()'); wait(pg, 400)
    def click(sel, ms=500):
        k = pg.locator(sel).count()
        if k: pg.locator(sel).first.evaluate('e=>e.click()'); wait(pg, ms)
        return k
    # ---- 1. phone-like photos ----
    rates = {}
    for how in ('clean', 'tilt', 'shear', 'jpeg', 'lowres', 'blur', 'glare', 'grey', 'noise', 'big'):
        path = OUT + 'audit131_clean.png' if how == 'clean' else degrade(a.b, how)
        door(); n0 = len(a.cases()); e0 = len(errs)
        pg.locator('.prod161 input[data-ocr=f-prod]').last.set_input_files(path); st = read_wait(pg); m = a.main()
        model = pg.locator('.prod161-dl .mono').first.inner_text() if pg.locator('.prod161-dl .mono').count() else ''
        out = 'model' if model == 'WGG244ZCGB' else 'wrong model' if model else 'make only' if 'found the make' in st else 'failed' if 'couldn’t' in st else 'wrong model' if model else 'other'
        if model: ok('Check it letter by letter against the label.' in m or 'Sorted isn’t sure this is the model' in m, '%s photo: a model read from a photo is to be checked against the label' % how)
        rates[how] = out
        ok(len(a.cases()) == n0 and len(errs) == e0, '%s photo: no case and no page error (%s)' % (how, out))
        ok(SER not in m, '%s photo: the serial is never shown in full' % how)
        ok(out in ('model', 'make only', 'failed', 'wrong model'), '%s photo: ends as read, make only or a clear failure (%s)' % (how, st[:60]))
        if out == 'failed': ok(pg.locator('.prod161 input[data-ocr=f-prod][capture]').count() == 1 and pg.locator('[data-a=prod161-type]').count() == 1, '%s photo: a failure offers a retake and typing' % how)
        wrong = model and model != 'WGG244ZCGB'
        if wrong: print('FINDING %s photo: Sorted proposed the wrong model %s (a candidate; the person must check it)' % (how, model))
    print('INFO label reads: ' + ', '.join('%s=%s' % kv for kv in rates.items()))
    ok(rates['clean'] == 'model', 'a clean label photo reads the model')
    # ---- 2. files that can't be read ----
    door(); open(OUT + 'audit131.txt', 'w').write('not a picture')
    pg.locator('.prod161 input[data-ocr=f-prod]').last.set_input_files(OUT + 'audit131.txt'); wait(pg, 800)
    ok('isn’t a picture' in pg.inner_text('#ocr-status'), 'a text file is turned away')
    sp = a.b.new_page(viewport={'width': 12, 'height': 12}); sp.set_content('<body style="margin:0;background:#fff"></body>'); sp.screenshot(path=OUT + 'audit131_tiny.png'); sp.close()
    door(); pg.locator('.prod161 input[data-ocr=f-prod]').last.set_input_files(OUT + 'audit131_tiny.png'); st = read_wait(pg)
    ok('couldn’t' in st and pg.locator('[data-a=prod161-type]').count() == 1, 'a 12 px image fails with a way out (%s)' % st[:60])
    door(); open(OUT + 'audit131.heic', 'wb').write(b'\x00\x00\x00\x18ftypheic' + b'\x00' * 64)
    pg.locator('.prod161 input[data-ocr=f-prod]').last.set_input_files(OUT + 'audit131.heic'); wait(pg, 1500)
    st = pg.inner_text('#ocr-status')
    ok('HEIC' in st or 'couldn’t' in st or 'can’t' in st, 'a HEIC photo the browser can’t open is refused with a way out (%s)' % st[:70])
    # ---- 3. a receipt read wrong, corrected; nothing moves the route before it is confirmed ----
    door(); pg.click('[data-a=prod161-type]'); wait(pg, 200)
    pg.fill('#prod-brand', 'Bosch'); pg.fill('#prod-model', 'WGG244ZCGB'); pg.fill('#prod-serial', SER); pg.locator('input[name=prod-cat][value=washing_machine]').evaluate('e=>e.click()')
    pg.click('form[data-f=prod161] button[type=submit]'); wait(pg, 300)
    pg.fill('#gi-what', 'It won’t drain'); pg.locator('form[data-f=gi] button[type=submit]').first.click(); wait(pg, 900)
    click('[data-a=match-new]'); click('[data-a=vague-go]')
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 800)
    cid = until(pg, lambda: [c['id'] for c in a.cases() if c.get('prod')], 8000)[0]
    a.open(cid)
    if pg.locator('form[data-f=what] [data-k=fault]').count(): pg.locator('form[data-f=what] [data-k=fault]').first.click(); wait(pg, 200)
    if pg.locator('form[data-f=what]').count(): pg.locator('form[data-f=what] button[type=submit]').click(); wait(pg, 500)
    if pg.locator('form[data-f=who]').count(): pg.locator('form[data-f=who] [data-k=responsible][data-v=me]').click(); pg.locator('form[data-f=who] button[type=submit]').click(); wait(pg, 600)
    sp = a.b.new_page(viewport={'width': 560, 'height': 220}); sp.set_content('<body style="margin:0;background:#fff;font-family:Arial;font-size:24px;padding:24px"><b>CURRYS</b><br>Date: 14/02/2026<br>Washer £499.00</body>'); sp.screenshot(path=OUT + 'audit131_receipt.png'); sp.close()
    pg.locator('form[data-f=prod162b] input[data-ocr=f-rcpt]').last.set_input_files(OUT + 'audit131_receipt.png'); st = read_wait(pg)
    c = a.case(cid)
    ok(c['prod']['f']['bought']['st'] == 'candidate' and c['fix'].get('seller', '') == '', 'a receipt reading is a candidate and reaches nothing yet (%s)' % st[:40])
    pg.fill('#pb-day', '2026-02-15'); pg.locator('form[data-f=prod162b] button[type=submit]').click(); wait(pg, 700)
    c = a.case(cid); fb = c['prod']['f']['bought']; m = a.main()
    ok(fb['v'] == '2026-02-15' and fb['st'] == 'corrected' and [w['v'] for w in fb['was'] if w['st'] == 'candidate'] == ['2026-02-14'], 'the corrected date is the fact; the reading is kept')
    ok(c['prod']['f']['retailer']['st'] == 'confirmed' and '15 February 2026' in m and 'Contact Currys' in m, 'the route uses the corrected date and the shop the person kept')
    ok(any(r['type'] == 'buy_date' and r['st'] == 'superseded' for r in c.get('ledger', [])), 'the ledger keeps the reading as replaced')
    # ---- 4. the serial in the files Sorted makes ----
    a.home(); pg.locator('[data-a=data]').first.evaluate('e=>e.click()'); wait(pg, 500)
    if pg.locator('[data-a=export-file]').count():
        with pg.expect_download() as dl: pg.click('[data-a=export-file]')
        allt = open(dl.value.path(), encoding='utf-8').read()
        ok('••••6789' in allt and SER not in allt, '“Download my cases” has the serial masked')
    else: ok(False, 'Download my cases was found')
    # ---- 5. the journey on to a missed promise ----
    a.open(cid); pg.locator('.prod162-best [data-a=prod162-contact]').first.click(); wait(pg, 600)
    pg.locator('form[data-f=call] button[type=submit]').click(); wait(pg, 600)
    a.open(cid); pg.locator('[data-a=panel][data-p="paste"]').first.evaluate('e=>e.click()'); wait(pg, 400)
    pg.fill('#f-paste', 'Currys: an engineer will visit on %s between 8am and 12pm.' % long(day(3))); pg.click('form[data-f=paste] button[type=submit]'); wait(pg, 800)
    click('[data-a=sug-yes]', 800); click('[data-a=plan-wait148]'); click('[data-a=refs-no]')
    a.overdue(cid, 1); a.open(cid)
    if pg.locator('[data-a=missed]').count(): pg.locator('[data-a=missed]').first.click(); wait(pg, 700)
    c = a.case(cid); ms = [q for q in c['promises'] if q['status'] == 'missed']
    ok(ms and ms[0]['party'] == 'Currys', 'the missed visit is recorded against Currys')
    ok(c['prod']['f']['model']['v'] == 'WGG244ZCGB' and c['fix']['seller'] == 'Currys', 'the case keeps its product through the miss')
    ask = pg.input_value('#f-ask') if pg.locator('#f-ask').count() else ''
    ok('washing machine' in ask.lower() and SER not in ask, 'the chase is about the washing machine, with no serial (%s)' % ask[:80])
    a.close()
finish()
