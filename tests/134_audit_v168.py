# v168, from the external audit of 11 October 2026. 1. Every repair goes through the product safety rules (ps-3) as well
# as the page's own danger words: hedged, past and paused danger, smells, electrical noises, discoloured sockets, hedged
# gas and carbon monoxide signs stop, through the page's reader and through the start box; ordinary faults don't.
# 2. A model read from an unclear photo on the case is doubted ("Sorted isn’t sure it read the model correctly") with
# Retake photo first; nothing is a fact before Looks right.
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
LABEL = ('<body style="margin:0;background:#c9cdd2;font-family:Arial;padding:30px"><div style="filter:blur(1.6px);background:#f4f4f2;border:2px solid #333;'
         'border-radius:8px;padding:18px 24px;width:520px;font-size:22px;line-height:1.45;color:#111"><b style="font-size:30px">BOSCH</b><br>'
         'Washing machine &nbsp; Serie 6<br>E-Nr. WGG244ZCGB/01 &nbsp; FD 2309<br>S/N: 123456789<br>220-240V ~ 50Hz 2300W<br>Made in Germany</div></body>')
STOP = ["I don't think it's smoking, but it smells strange", "It's not sparking any more but it did earlier", "it isn't smoking now but it was last night",
        "didn't see any sparks but heard crackling from the socket", "not burning, but there is a strange electrical smell", "the socket is discoloured brown",
        "I can't tell if that's gas I'm smelling", "there's a smell of rotten eggs by the cooker", "black marks around the boiler and I feel dizzy",
        "the consumer unit keeps tripping", "the light switch is warm and buzzing", "the battery got hot and hissed"]
SAFE = ["My washing machine won't drain", "The dishwasher smells of fish", "the fridge hums loudly", "no sparks, no smoke, nothing strange, it just won't start",
        "The boiler has no hot water", "The printer clicks and stops", "My phone gets warm while charging"]
with sync_playwright() as p:
    a = App(p, email=False); pg = a.pg
    a.ctx.route('https://cdn.jsdelivr.net/**', cdn)
    rd = a.ctx.new_page(); rd.route(lambda u: u.startswith('https://sorted.test/'), lambda q: q.fulfill(path=HERE + '/tests/out/reader.html', content_type='text/html'))
    rd.goto('https://sorted.test/'); wait(rd, 500)
    U = lambda t: rd.evaluate("(t)=>__read.looksUnsafe(t)", t)
    for t in STOP: ok(U(t), 'stops for safety: %s' % t)
    for t in SAFE: ok(not U(t), 'not a hazard: %s' % t)
    rd.close()
    # through the start box: a hedged smell stops before any case exists; an ordinary fault doesn't
    a.home(); a.tap('new-case'); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300); n0 = len(a.cases())
    pg.fill('#f-case', "My tumble dryer stopped. I don't think it's smoking, but it smells strange"); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 700)
    ok(pg.locator('[data-a=safe-continue]').count() == 1 and len(a.cases()) == n0, 'the start box stops for a hedged smell before any case exists')
    a.home()
    cid = a.start('My dishwasher has stopped working', False)
    a.open(cid); pg.fill('#f-detail', 'No sparks any more but there were some earlier'); pg.locator('form[data-f=what] button[type=submit]').click(); wait(pg, 600)
    ok(pg.locator('[data-a=safe-continue]').count() == 1, 'the repair step stops for danger that is only paused')
    a.home()
    cid2 = a.start('My dishwasher has stopped working', False)
    a.open(cid2); pg.fill('#f-detail', 'It just stops with water in the drum'); pg.locator('form[data-f=what] button[type=submit]').click(); wait(pg, 600)
    ok(a.case(cid2)['fix']['step'] == 'who' and pg.locator('[data-a=safe-continue]').count() == 0, 'an ordinary fault carries on')
    # the label photographed on a product case, blurred: doubted, Retake photo first, nothing confirmed
    sp = a.b.new_page(viewport={'width': 640, 'height': 330}, device_scale_factor=2); sp.set_content(LABEL); wait(sp, 200); sp.screenshot(path=HERE + '/tests/out/v168_blur.png'); sp.close()
    before = set(c['id'] for c in a.cases())
    a.home(); a.tap('new-case'); pg.locator('[data-cap82=fix]').first.evaluate('e=>e.click()'); wait(pg, 400)
    pg.click('[data-a=prod161-type]'); wait(pg, 200); pg.locator('input[name=prod-cat][value=washing_machine]').evaluate('e=>e.click()'); pg.click('form[data-f=prod161] button[type=submit]'); wait(pg, 300)
    pg.fill('#gi-what', 'It won’t drain'); pg.locator('form[data-f=gi] button[type=submit]').first.click(); wait(pg, 800)
    for s in ('[data-a=match-new]', '[data-a=vague-go]'):
        if pg.locator(s).count(): pg.click(s); wait(pg, 400)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 800)
    pid = until(pg, lambda: [c['id'] for c in a.cases() if c['id'] not in before], 8000)[0]
    a.open(pid); pg.locator('.prod161-card input[data-ocr=f-prodc]').set_input_files(HERE + '/tests/out/v168_blur.png')
    st = ''
    for _ in range(240):
        st = pg.inner_text('#ocr-status') if pg.locator('#ocr-status').count() else ''
        if re.search(r'Label read|didn’t find|too unclear', st): break
        wait(pg, 500)
    wait(pg, 400); m = a.main(); f = a.case(pid)['prod']['f']
    model = (f.get('model') or {})
    print('INFO blurred label on the case: %s / %s' % (st[:70], model.get('v')))
    if model.get('v') and model.get('v') != 'WGG244ZCGB':
        ok('isn’t sure it read the model correctly' in m and pg.locator('.prod168-doubt input[data-ocr=f-prodc][capture]').count() == 1, 'a doubtful model on the case comes with the warning and Retake photo')
    ok(not model or model.get('st') != 'confirmed', 'nothing read from the photo is confirmed before Looks right')
    ok('123456789' not in m, 'the serial is never shown in full')
    a.close()
finish()
