# v166: from Baldwin's vacuum cleaner walk on his iPhone. A product case doesn't ask again what it is or what's
# happening: its first step is only the safety question with an optional detail; a product washing machine needs no
# fault chip. A product started without its label offers "Photograph the label" on the case; the read is candidates on
# the card ("Check what Sorted read", the serial masked), "Looks right" confirms them with history lines, "Not right"
# turns them down; the details are rows; the title keeps the person's words as typed.
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *
O = HERE + '/tests/node_modules/'; Hh = {'Access-Control-Allow-Origin': '*'}
def cdn(r):
    u = r.request.url
    if '/npm/tesseract.js@5.1.1/dist/' in u: return r.fulfill(path=O + 'tesseract.js/dist/' + u.split('/dist/')[1], content_type='application/javascript', headers=Hh)
    if '/npm/tesseract.js-core@5.1.1/' in u: f = u.split('@5.1.1/')[1]; return r.fulfill(path=O + 'tesseract.js-core/' + f, content_type='application/wasm' if f.endswith('.wasm') else 'application/javascript', headers=Hh)
    if '/npm/@tesseract.js-data/eng@1.0.0/' in u: return r.fulfill(path=O + '@tesseract.js-data/eng/4.0.0_best_int/eng.traineddata.gz', content_type='application/gzip', headers=Hh)
    return r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript')
LABEL = '<body style="margin:0;background:#fff;font-family:Arial;font-size:26px;line-height:1.5;padding:24px"><b>DYSON</b><br>Model: SV14<br>S/N: AB12345678<br>21.6V</body>'
def read_wait(pg):
    st = ''
    for _ in range(240):
        st = pg.inner_text('#ocr-status') if pg.locator('#ocr-status').count() else ''
        if re.search(r'Label read|didn’t find|couldn’t', st): wait(pg, 500); return st
        wait(pg, 500)
    return st
with sync_playwright() as p:
    a = App(p, email=False); pg = a.pg
    a.ctx.route('https://cdn.jsdelivr.net/**', cdn)
    sp = a.b.new_page(viewport={'width': 560, 'height': 260}); sp.set_content(LABEL); sp.screenshot(path=HERE + '/tests/out/prod132_label.png'); sp.close()
    def click(sel, ms=500):
        k = pg.locator(sel).count()
        if k: pg.locator(sel).first.evaluate('e=>e.click()'); wait(pg, ms)
        return k
    def start(cat, words, brand='', model=''):
        before = set(c['id'] for c in a.cases())
        a.home(); a.tap('new-case'); pg.locator('[data-cap82=fix]').first.evaluate('e=>e.click()'); wait(pg, 400)
        pg.click('[data-a=prod161-type]'); wait(pg, 200)
        if brand: pg.fill('#prod-brand', brand)
        if model: pg.fill('#prod-model', model)
        pg.locator('input[name=prod-cat][value=%s]' % cat).evaluate('e=>e.click()'); pg.click('form[data-f=prod161] button[type=submit]'); wait(pg, 300)
        pg.fill('#gi-what', words); pg.locator('form[data-f=gi] button[type=submit]').first.click(); wait(pg, 800)
        click('[data-a=match-new]'); click('[data-a=vague-go]')
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 800)
        return until(pg, lambda: [c['id'] for c in a.cases() if c['id'] not in before], 8000)[0]
    cid = start('vacuum', 'It’s not working')
    c = a.case(cid)
    ok(c['title'] == 'My vacuum cleaner: It’s not working', 'the title keeps the person’s words as typed (%r)' % c['title'])
    a.open(cid); m = a.main()
    ok('Before anything else' in m and 'You said: “It’s not working”' in m and 'Is anything burning, smoking or sparking' in m, 'the first step is the safety question, with what they said')
    ok(pg.locator('form[data-f=what] [data-k=item]').count() == 0 and pg.locator('form[data-f=what] input#f-item[type=text]').count() == 0 and 'Sorted asks its own questions only for a washing machine' not in m, 'it doesn’t ask again what it is')
    ok(pg.evaluate("getComputedStyle(document.querySelector('.prod161-row')).display") == 'flex', 'the product’s details are rows')
    ok('To find the right support page, Sorted needs the model.' in m and pg.locator('.prod161-card input[data-ocr=f-prodc][capture]').count() == 1, 'with no model, the case offers a photo of the label')
    pg.click('[data-a=prod166-where]'); wait(pg, 200)
    ok('Where the label usually is' in a.main() and 'Vacuum cleaner: underneath, or behind the bin' in a.main(), 'and where the label usually is')
    pg.locator('form[data-f=what] button[type=submit]').click(); wait(pg, 600)
    ok(a.case(cid)['fix']['step'] == 'who', '“No, carry on” moves to who fixes it')
    # the label on the case
    a.open(cid); pg.locator('.prod161-card input[data-ocr=f-prodc]').set_input_files(HERE + '/tests/out/prod132_label.png'); st = read_wait(pg); m = a.main()
    ok('Label read' in st and 'Check what Sorted read' in m and 'SV14' in m and '••••5678' in m and 'AB12345678' not in m, 'the read is candidates on the card, the serial masked (%s)' % st[:40])
    c = a.case(cid); f = c['prod']['f']
    ok(f['model']['st'] == 'candidate' and f['brand']['v'] == 'Dyson' and f['brand']['st'] == 'candidate', 'nothing is a fact before Looks right')
    pg.click('form[data-f=prod166c] button[type=submit]'); wait(pg, 600)
    c = a.case(cid); f = c['prod']['f']
    ok(f['model']['st'] == 'confirmed' and f['model']['src'] == 'label_photo' and f['serial']['v'] == 'AB12345678' and f['brand']['st'] == 'confirmed', 'Looks right confirms them, from the label photo')
    ok(any(e['label'] == 'Model: SV14, read from the label photo and confirmed by you.' for e in c['events']) and not any('AB12345678' in e['label'] for e in c['events']), 'the history says so, with no full serial')
    ok('To find the right support page' not in a.main() and 'Dyson vacuum cleaner' in a.main(), 'the card now shows the Dyson vacuum cleaner')
    # Not right turns a reading down
    cid2 = start('vacuum', 'Lost suction')
    a.open(cid2); pg.locator('.prod161-card input[data-ocr=f-prodc]').set_input_files(HERE + '/tests/out/prod132_label.png'); read_wait(pg)
    pg.click('[data-a=prod166-no]'); wait(pg, 500)
    f2 = a.case(cid2)['prod']['f']
    ok(f2['model']['st'] == 'rejected' and f2['serial']['v'] == '••••5678' and 'To find the right support page' in a.main(), 'Not right turns the reading down, keeps the serial only masked, and offers the photo again')
    # a product washing machine needs no fault chip
    cid3 = start('washing_machine', 'It won’t drain', 'Bosch', 'WGG244ZCGB')
    a.open(cid3); pg.locator('form[data-f=what] button[type=submit]').click(); wait(pg, 600)
    ok(a.case(cid3)['fix']['step'] == 'who' and 'Pick what it’s doing' not in a.main(), 'a product washing machine carries on without a fault chip')
    a.close()
finish()
