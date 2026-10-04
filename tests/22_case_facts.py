# v60: case facts, release 1 of the resolution engine. A parking notice that comes into a case becomes proposed facts,
# each saying where it came from. Nothing counts until the person confirms it, and they can change or remove any of it.
import os, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); O = HERE + '/tests/node_modules/'; errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=350): pg.wait_for_timeout(ms)
H = {'Access-Control-Allow-Origin': '*'}
def cdn(r):
    u = r.request.url
    if '/npm/tesseract.js@5.1.1/dist/' in u: return r.fulfill(path=O + 'tesseract.js/dist/' + u.split('/dist/')[1], content_type='application/javascript', headers=H)
    if '/npm/tesseract.js-core@5.1.1/' in u: f = u.split('@5.1.1/')[1]; return r.fulfill(path=O + 'tesseract.js-core/' + f, content_type='application/wasm' if f.endswith('.wasm') else 'application/javascript', headers=H)
    if '/npm/@tesseract.js-data/eng@1.0.0/' in u: return r.fulfill(path=O + '@tesseract.js-data/eng/4.0.0_best_int/eng.traineddata.gz', content_type='application/gzip', headers=H)
    return r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript')
def tasks(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks.map(y=>y.data)")
def case(pg, title): return next((x for x in tasks(pg) if x['title'] == title), None)
def start(pg, text):
    pg.click('[data-a=home]'); wait(pg)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
    pg.fill('#f-case', text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 450)
def rows(pg, sel='.cf-check'): return [x.strip() for x in pg.locator(sel + ' .cf-k').all_text_contents()]
NOTICE = corpus.PCN_NOTICES[0][0]
NTO = ("London Borough of Southwark NOTICE TO OWNER PCN Number: SK12345678 Vehicle Registration Mark: AB12 CDE "
       "Date of notice: 20/10/2026 Date of contravention: 02/10/2026 The penalty charge of £130 has not been paid. "
       "You must pay or make representations within 28 days of the date of service.")
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', cdn)
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    # a photo of a notice, made locally
    sp = b.new_page(viewport={'width': 560, 'height': 420})
    sp.set_content('<body style="margin:0;background:#fff;font-family:Arial;font-size:20px;line-height:1.5;padding:24px">'
                   '<b>CAMDEN COUNCIL</b><br><b>PENALTY CHARGE NOTICE</b><br>PCN Number: CU98765432<br>Vehicle registration: LK70 XYZ<br>'
                   'Date of contravention: 28/09/2026<br>Time: 14:32<br>Location: Camden High Street<br>'
                   'Penalty charge: £160, reduced to £80 if paid within 14 days.</body>')
    os.makedirs(HERE + '/tests/out', exist_ok=True); sp.screenshot(path=HERE + '/tests/out/pcn_photo.png'); sp.close()
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 200); pg.click('[data-a=anon-start]'); wait(pg)

    # 1 a notice typed or pasted into the start box
    pg.fill('#f-case', NOTICE); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 450)
    T = 'Southwark PCN · SK12345678'
    t = case(pg, T)
    ok(t is not None, 'the case is named after who sent it and the reference')
    ok(pg.locator('.sug').count() == 0, 'no "they promised" card from a notice')
    ok(pg.locator('.cf-check').count() == 1 and 'I found these details. Are they right?' in pg.inner_text('.cf-check'), 'Sorted asks whether the details are right')
    r1 = rows(pg)
    ok(r1[:4] == ['What it is', 'Who sent it', 'Reference', 'Vehicle'] and 'Amount' in r1 and 'Reduced amount' in r1, 'the details, in a sensible order: %s' % r1)
    ok(all(v['st'] == 'proposed' for v in t['cf']['f'].values()), 'nothing is confirmed yet')
    ok('All from what you wrote when you started' in pg.inner_text('.cf-check'), 'the card says where the details came from')
    ok(pg.locator('.cf-check .cf-ch').count() == len(r1) and pg.locator('.cf-check button').count() == len(r1) + 2, 'one Change button per detail, then confirm and Not now')
    ok(pg.locator('.cf-check').bounding_box()['height'] < 1350, 'the card stays compact on a phone: %dpx' % pg.locator('.cf-check').bounding_box()['height'])
    ok(pg.locator('form[data-f=call]').count() == 0, 'the details come first, before anything else on the case')
    pg.screenshot(path=HERE + '/tests/out/case_facts_check.png', full_page=True)
    # 2 remove one, change one
    pg.click('.cf-check [data-a=cf-edit][data-k=time]'); wait(pg); pg.click('[data-a=cf-rm]'); wait(pg)
    ok('Time' not in rows(pg) and case(pg, T)['cf']['f']['time']['st'] == 'rejected', '"Remove this detail" takes it out')
    pg.click('.cf-check [data-a=cf-edit][data-k=place]'); wait(pg)
    ok(pg.input_value('#f-cf') == 'Lordship Lane SE22', 'changing a detail starts from what Sorted read')
    pg.fill('#f-cf', 'Lordship Lane, East Dulwich'); pg.click('form[data-f=cf] button[type=submit]'); wait(pg)
    f = case(pg, T)['cf']['f']['place']
    ok(f['v'] == 'Lordship Lane, East Dulwich' and f['st'] == 'confirmed' and f['how'] == 'you', 'a change you make counts as confirmed')
    # 3 confirm the rest
    n = len(rows(pg)); pg.click('[data-a=cf-yes]'); wait(pg)
    t = case(pg, T)
    ok(pg.locator('.cf-check').count() == 0 and pg.locator('.cf-facts').count() == 1, 'confirmed details move to Case facts')
    ok(sum(1 for v in t['cf']['f'].values() if v['st'] == 'confirmed') == n + 1, 'every remaining detail is confirmed (%d)' % (n + 1))
    ok(any(e['label'] == 'You confirmed %d details from the notice.' % n for e in t['events']), 'the history says what you confirmed')
    facts = pg.inner_text('.cf-facts')
    ok('SK12345678' in facts and 'You entered this' in facts and 'Lordship Lane, East Dulwich' in facts, 'Case facts shows them, with where each came from')
    if pg.locator('[data-a=sug-no]').count(): pg.click('[data-a=sug-no]'); wait(pg)
    if pg.locator('.pk-card [data-a=panel][data-p=call]').count(): pg.click('.pk-card [data-a=panel][data-p=call]'); wait(pg)
    ask = pg.input_value('textarea[name=ask]') if pg.locator('textarea[name=ask]').count() else ''
    ok(ask.startswith('I’m getting in touch about penalty charge notice SK12345678 for vehicle AB12 CDE') and 'LONDON BOROUGH' not in ask, 'the call message names the notice instead of pasting it: %r' % ask[:90])
    # 4 a later letter: only what's new or different is asked about
    pg.click('[data-a=panel][data-p=paste]'); wait(pg); pg.fill('#f-paste', NTO); pg.click('form[data-f=paste] button[type=submit]'); wait(pg)
    ok(pg.locator('#f-paste').count() == 0 and pg.locator('.cf-check').count() == 1, 'a pasted letter goes straight to the details it found')
    r2 = rows(pg); chk = pg.inner_text('.cf-check')
    ok('Reference' not in r2 and 'Vehicle' not in r2, 'details you already confirmed aren\'t asked again: %s' % r2)
    ok('Date of the notice' in r2 and 'Before, it said Penalty Charge Notice from a council' in chk, 'a change of stage shows what it said before')
    ok('All from the message you pasted' in chk, 'it says the new details came from the pasted message')
    pg.click('[data-a=cf-later]'); wait(pg)
    ok(pg.locator('.cf-check').count() == 0 and pg.locator('[data-a=cf-show]').count() == 1, '"Not now" folds it to a small link')
    pg.click('[data-a=cf-show]'); wait(pg); pg.click('[data-a=cf-yes]'); wait(pg)
    ok(case(pg, T)['cf']['f']['type']['v'] == 'Notice to Owner from a council', 'confirming takes the new stage')
    # 5 a photo of a notice, read on the phone: since v121 the read is reviewed first, then the facts are confirmed
    pg.click('[data-a=home]'); wait(pg)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
    pg.set_input_files('input[data-ocr=f-case]', HERE + '/tests/out/pcn_photo.png')
    for i in range(240):
        st = pg.inner_text('#ocr-status') if pg.locator('#ocr-status').count() else ''
        if 'Photo read' in st or 'couldn’t' in st or 'doesn’t look' in st: break
        wait(pg, 500)
    ok('Photo read. Check the details below.' in st and pg.locator('form[data-f=doc]').count() == 1 and pg.input_value('#doc-ref') == 'CU98765432' and pg.input_value('#doc-vrm') == 'LK70 XYZ', 'a photo of a notice is read into a review, not into the case (%s)' % st[:50])
    pg.click('form[data-f=doc] button[type=submit]'); wait(pg, 700)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 450)
    t2 = case(pg, 'Camden PCN · CU98765432')
    ok(t2 is not None, 'a photo of a notice names the case too')
    f2 = (t2 or {}).get('cf', {}).get('f', {})
    ok(t2 is not None and pg.locator('.cf-check').count() == 0 and pg.locator('.cf-facts').count() == 1 and f2.get('ref', {}).get('v') == 'CU98765432' and f2.get('vrm', {}).get('v') == 'LK70 XYZ' and all(x.get('st') == 'confirmed' and x.get('src') == 'the photo you added' for x in f2.values()), 'the details you checked are confirmed facts from the photo, with no second "Are they right?"')
    # 6 ordinary cases are left alone
    start(pg, "Currys refund hasn't arrived, order 445566")
    t3 = case(pg, 'Currys refund · 445566')
    ok(t3 is not None and not t3.get('cf') and pg.locator('.cf-check, .cf-facts').count() == 0, 'an ordinary case gets no details card')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
