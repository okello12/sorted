# v161: Something I own isn't working (docs/PRODUCT_PHASE1.md). Through the real label reader (Tesseract, served
# locally) and the repair door: the start offers a photo, a chosen photo or typing; a clear label gives candidates
# ("Check what Sorted read") with the serial masked and nothing saved; Show reveals it; Change corrects a value and the
# reading stays in the history; Start makes one repair case whose product is confirmed field by field with its source,
# the repair engine's item and model follow it, the ledger has every state (the serial only masked), the history says
# where each detail came from, Sorted's own washing-machine checks are never offered, and a safety decision with its
# rule version is stored. A blurred photo fails with routes and saves nothing; a product photo without a label gives the
# brand and asks for the model (Continue without it); two models are offered as a choice; typing works with no photo; a
# refresh before Start keeps nothing; the case page shows Show and Copy and the change panel records what changed;
# nothing of the product reaches usage records yet (migration 30 comes first).
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *
O = HERE + '/tests/node_modules/'; H = {'Access-Control-Allow-Origin': '*'}
def cdn(r):
    u = r.request.url
    if '/npm/tesseract.js@5.1.1/dist/' in u: return r.fulfill(path=O + 'tesseract.js/dist/' + u.split('/dist/')[1], content_type='application/javascript', headers=H)
    if '/npm/tesseract.js-core@5.1.1/' in u: f = u.split('@5.1.1/')[1]; return r.fulfill(path=O + 'tesseract.js-core/' + f, content_type='application/wasm' if f.endswith('.wasm') else 'application/javascript', headers=H)
    if '/npm/@tesseract.js-data/eng@1.0.0/' in u: return r.fulfill(path=O + '@tesseract.js-data/eng/4.0.0_best_int/eng.traineddata.gz', content_type='application/gzip', headers=H)
    return r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript')
B = '<body style="margin:0;background:#fff;font-family:Arial;font-size:24px;line-height:1.5;padding:24px">'
LABEL = B + '<b>BOSCH</b><br>Washing machine<br>E-Nr. WGG244ZCGB/01<br>S/N: 123456789<br>220-240V 50Hz</body>'
BRAND = B + '<b style="font-size:40px">Miele</b><br>W1 Classic</body>'
TWO = B + 'Beko<br>Model: WMB71643PTE<br>Model: WTL84141W</body>'
BLUR = B.replace('padding:24px', 'padding:24px;filter:blur(4px)') + '<b>BOSCH</b><br>E-Nr. WGG244ZCGB/01<br>S/N: 123456789</body>'
def shot(b, path, html):
    sp = b.new_page(viewport={'width': 560, 'height': 300}); sp.set_content(html); sp.screenshot(path=path); sp.close()
def read_wait(pg):
    st = ''
    for _ in range(240):
        st = pg.inner_text('#ocr-status') if pg.locator('#ocr-status').count() else ''
        if re.search(r'Label read|found the make|couldn’t|can’t', st): wait(pg, 500); return st
        wait(pg, 500)
    return st
SERIAL = '123456789'

with sync_playwright() as p:
    a = App(p, email=False); pg = a.pg
    a.ctx.route('https://cdn.jsdelivr.net/**', cdn)
    P = {k: HERE + '/tests/out/prod127_%s.png' % k for k in ('label', 'brand', 'two', 'blur')}
    shot(a.b, P['label'], LABEL); shot(a.b, P['brand'], BRAND); shot(a.b, P['two'], TWO); shot(a.b, P['blur'], BLUR)
    def door():
        a.home(); a.tap('new-case'); pg.locator('[data-cap82=fix]').first.evaluate('e=>e.click()'); wait(pg, 500)
    def photo(path): pg.locator('.prod161 input[data-ocr=f-prod]').last.set_input_files(path); return read_wait(pg)
    # ---- the start ----
    door(); m = a.main()
    ok(pg.locator('.prod161').count() == 1 and 'Something you own isn’t working?' in m and 'Photograph it or tell Sorted what it is.' in m, 'the repair door leads with the product start')
    ok(pg.locator('.prod161 input[data-ocr=f-prod][capture]').count() == 1 and pg.locator('.prod161 input[data-ocr=f-prod]:not([capture])').count() == 1 and pg.locator('[data-a=prod161-type]').count() == 1, 'take a photo, choose a photo, or type it')
    ok('The photo isn’t uploaded or kept.' in m and pg.locator('form[data-f=gi]').count() == 1, 'it says the photo stays on the phone; the ordinary form is still there')
    # ---- a blurred label: nothing saved, routes ----
    n0 = len(a.cases()); st = photo(P['blur']); m = a.main()
    ok('Sorted couldn’t read that photo' in m and pg.locator('.prod161 [role=alert]').count() >= 1 and 'Nothing has been saved.' in m, 'a blurred label fails, announced (%s)' % st[:60])
    ok(pg.locator('.prod161 input[data-ocr=f-prod][capture]').count() == 1 and 'Choose another photo' in m and pg.locator('[data-a=prod161-type]').count() == 1 and len(a.cases()) == n0, 'retake, choose another, or type; no case')
    # ---- a clear label: candidates, masked, nothing saved ----
    door(); st = photo(P['label']); m = a.main()
    ok('Label read' in st and 'Check what Sorted read' in m, 'a clear label is read (%s)' % st[:60])
    ok('Bosch' in m and 'WGG244ZCGB' in m and '••••6789' in m and SERIAL not in m, 'brand, model and the serial masked')
    ok(pg.locator('input[name=prod-cat][value=washing_machine]:checked').count() == 1, 'the kind read from the label is pre-chosen')
    ok('Nothing is saved until you press Start.' in m and len(a.cases()) == n0, 'nothing saved yet')
    pg.click('[data-a=prod161-reveal]'); wait(pg, 300)
    ok(SERIAL in a.main(), 'Show reveals the serial')
    pg.click('[data-a=prod161-reveal]'); wait(pg, 300)
    ok(SERIAL not in a.main(), 'Hide masks it again')
    # Change: correct the model; the reading is kept
    pg.locator('.prod161 [data-a=prod161-edit]').last.click(); wait(pg, 300)
    ok(pg.input_value('#prod-brand') == 'Bosch' and pg.input_value('#prod-model') == 'WGG244ZCGB' and pg.input_value('#prod-serial') == '' and 'Leave this blank to keep ••••6789' in a.main(), 'Change: editable fields, the serial blank to keep it')
    pg.fill('#prod-model', 'wgg244zcgc'); pg.click('form[data-f=prod161] button[type=submit]'); wait(pg, 400)
    m = a.main()
    ok('Bosch washing machine, model WGG244ZCGC, serial ••••6789' in m and pg.locator('[data-a=prod161-edit]').count() == 1, 'the product line after saving')
    ok(pg.locator('input[name=gi-item][value="Washing machine"]:checked').count() == 1, 'the kind chooses the repair door’s chip')
    pg.fill('#gi-what', 'It won’t drain. It stopped halfway through a wash.')
    pg.locator('form[data-f=gi] button[type=submit]').first.click(); wait(pg, 800)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg, 500)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 800)
    cs = until(pg, lambda: [c for c in a.cases() if c.get('prod')], 8000)
    ok(len(cs) == 1, 'one case with a product')
    c = cs[0]; f = c['prod']['f']
    ok(f['brand']['st'] == 'confirmed' and f['brand']['src'] == 'label_photo' and f['serial']['st'] == 'confirmed' and f['serial']['v'] == SERIAL and f['category']['st'] == 'confirmed', 'brand, serial and kind confirmed from the label')
    ok(f['model']['st'] == 'corrected' and f['model']['v'] == 'WGG244ZCGC' and [w['v'] for w in f['model']['was'] if w['st'] == 'candidate'] == ['WGG244ZCGB'], 'the model corrected by the person, the reading kept')
    ok(c['fix']['item'] == 'Washing machine' and c['fix']['model'] == 'Bosch WGG244ZCGC', 'the repair engine reads the confirmed product')
    sd = c['prod'].get('safety') or {}
    ok(sd.get('result') == 'SAFE_EXTERNAL_CHECKS' and sd.get('rule_version') == 'ps-1' and sd.get('product_class') == 'washing_machine', 'the safety decision and its rule version are stored: %s' % sd.get('result'))
    labels = [e['label'] for e in c['events']]
    ok(any(l.startswith('Make: Bosch, read from the label photo and confirmed by you') for l in labels) and any('Model: WGG244ZCGC, corrected by you. Sorted had read WGG244ZCGB.' == l for l in labels) and any(l.startswith('Serial number: ••••6789') for l in labels), 'the history says where each detail came from')
    ok(not any(SERIAL in l for l in labels) and not any('safety rules' in l for l in labels), 'no full serial in the history; a safe decision is stored, not logged')
    lg = c.get('ledger') or []
    ok([r['st'] for r in lg if r['type'] == 'prod_model'] == ['superseded', 'confirmed'] and all(r['v'] == '••••6789' for r in lg if r['type'] == 'prod_serial'), 'the ledger: the model reading replaced, the serial only masked')
    ok('It won’t drain' in (c.get('said') or ''), 'the person’s words are kept as they said them')
    # the case page
    m = a.main()
    ok(pg.locator('.prod161-card').count() == 1 and '••••6789' in m and SERIAL not in m and 'read from the label, confirmed by you' in m, 'the case shows the product, the serial masked, with its source')
    ok('Try these safe checks' not in m, 'Sorted’s own checks are never offered on a product case')
    pg.locator('[data-a=prod161-reveal-case]').click(); wait(pg, 300)
    ok(SERIAL in a.main(), 'Show on the case reveals it')
    pg.locator('[data-a=prod161-copy]').click(); wait(pg, 400)
    ok(pg.evaluate('navigator.clipboard.readText()') == SERIAL and 'Serial number copied' in pg.inner_text('body'), 'Copy copies the full serial')
    cid = c['id']; a.open(cid)
    ok(SERIAL not in a.main(), 'leaving the case hides it again')
    # the change panel records what changed
    pg.locator('.prod161-card [data-a=panel][data-p=prod161c]').click(); wait(pg, 300)
    pg.fill('#prod-model', 'WGG244ZCGB'); pg.click('form[data-f=prod161c] button[type=submit]'); wait(pg, 700)
    c = until(pg, lambda: [x for x in a.cases() if x['id'] == cid and x['prod']['f']['model']['v'] == 'WGG244ZCGB'], 6000)
    ok(c and any(e['label'] == 'Model changed by you from WGG244ZCGC to WGG244ZCGB.' for e in c[0]['events']), 'a later change is in the history')
    # ---- a product photo with no label: the brand, then ask for the model ----
    door(); st = photo(P['brand']); m = a.main()
    ok('Sorted found the make but not the model.' in st and 'Miele' in m and 'To find the right support page, Sorted needs the model.' in m, 'brand only: progress, and it asks for the model')
    ok('Photograph the label' in m and 'Show me where to look' in m and 'Type the model' in m and 'Continue without it' in m, 'photograph the label, where to look, type it, or continue')
    pg.click('[data-a=prod161-where]'); wait(pg, 200)
    ok('Look for the words Model, Type or E-Nr.' in a.main(), 'where to look')
    pg.click('form[data-f=prod161] button[type=submit]'); wait(pg, 300)
    ok('Miele' in a.main() and 'model' not in pg.inner_text('.prod161 p'), 'continue without the model: the make is kept, no model invented')
    # ---- two model numbers: a choice ----
    door(); st = photo(P['two']); m = a.main()
    ok('Sorted found more than one. Which is the model?' in m and pg.locator('input[name=prod-model]').count() == 2, 'two models are offered as a choice')
    pg.locator('input[name=prod-model] >> nth=1').evaluate('e=>e.click()'); pg.click('form[data-f=prod161] button[type=submit]'); wait(pg, 300)
    ok('model WTL84141W' in a.main(), 'the chosen one is kept')
    # ---- typing, no photo ----
    door(); pg.click('[data-a=prod161-type]'); wait(pg, 300)
    ok(pg.evaluate('document.activeElement.id') == 'prod-brand', 'typing: focus on the make')
    pg.fill('#prod-brand', 'Dyson'); pg.fill('#prod-model', 'SV14'); pg.locator('input[name=prod-cat][value=vacuum]').evaluate('e=>e.click()')
    pg.click('form[data-f=prod161] button[type=submit]'); wait(pg, 300)
    ok('Dyson vacuum cleaner, model SV14' in a.main(), 'typed details make the product')
    # a refresh before Start keeps nothing
    n1 = len(a.cases()); pg.reload(); wait(pg, 800)
    ok(len(a.cases()) == n1 and 'SV14' not in json.dumps(pg.evaluate('Object.assign({},localStorage)')) and 'SV14' not in json.dumps(pg.evaluate('Object.assign({},sessionStorage)')), 'a refresh before Start saves nothing and keeps nothing on the phone')
    # ---- usage records: nothing product-shaped yet ----
    evs = a.db().get('pilot_events', [])
    ok(not any(e['name'].startswith('product_') for e in evs) and not any(SERIAL in json.dumps(e) or 'WGG244' in json.dumps(e) for e in evs), 'no product step names before migration 30, and no product text in usage records')
    a.close()
finish()
