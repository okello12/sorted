# v162: the product journey hands over to the ordinary Sorted core (docs/PRODUCT_PHASE1.md). A product repair case
# walks the case's own steps: the purchase step reads a receipt photo (Tesseract) into candidates, "Looks right"
# confirms them, a changed date is a correction with the reading kept, and nothing read changes the route until it is
# confirmed; the decision is "Best next step" from confirmed facts with its reason and source, the maker's support page
# said to be found and not read, "Have these ready" with the serial masked, and the other routes beneath; "Prepare
# contact" fills the existing message form with confirmed details only and no serial until the person adds it; saving
# the message makes no promise; their reply is proposed and, once confirmed, is an ordinary promise that Home, the
# case, the helper's link, the pack and the export all show alike. Unknown purchase details lead to the maker, an
# unknown maker to a repairer, a boiler to a Gas Safe engineer, someone else's job to them.
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
B = '<body style="margin:0;background:#fff;font-family:Arial;font-size:24px;line-height:1.5;padding:24px">'
RECEIPT = B + '<b>ARGOS</b><br>Order date: 14/02/2026<br>Bosch washing machine £499.00<br>Thank you for shopping</body>'
SER = '123456789'
def read_wait(pg):
    st = ''
    for _ in range(240):
        st = pg.inner_text('#ocr-status') if pg.locator('#ocr-status').count() else ''
        if re.search(r'Receipt read|couldn’t|can’t', st): wait(pg, 500); return st
        wait(pg, 500)
    return st
with sync_playwright() as p:
    a = App(p, email=True); pg = a.pg
    a.ctx.route('https://cdn.jsdelivr.net/**', cdn)
    sp = a.b.new_page(viewport={'width': 560, 'height': 260}); sp.set_content(RECEIPT); sp.screenshot(path=HERE + '/tests/out/prod130_receipt.png'); sp.close()
    def click(sel, ms=500):
        k = pg.locator(sel).count()
        if k: pg.locator(sel).first.evaluate('e=>e.click()'); wait(pg, ms)
        return k
    def product_case(brand, model, serial, cat, words):
        before = set(c['id'] for c in a.cases())
        a.home(); a.tap('new-case'); pg.locator('[data-cap82=fix]').first.evaluate('e=>e.click()'); wait(pg, 400)
        pg.click('[data-a=prod161-type]'); wait(pg, 200)
        pg.fill('#prod-brand', brand); pg.fill('#prod-model', model); pg.fill('#prod-serial', serial); pg.locator('input[name=prod-cat][value=%s]' % cat).evaluate('e=>e.click()')
        pg.click('form[data-f=prod161] button[type=submit]'); wait(pg, 300)
        pg.fill('#gi-what', words); pg.locator('form[data-f=gi] button[type=submit]').first.click(); wait(pg, 800)
        click('[data-a=safe-continue]'); click('[data-a=match-new]'); click('[data-a=vague-go]')
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 800)
        new = until(pg, lambda: [c['id'] for c in a.cases() if c['id'] not in before], 8000)
        return new[0]
    def to_bought(cid, resp='me'):
        a.open(cid)
        if pg.locator('form[data-f=what]').count():
            if pg.locator('form[data-f=what] [data-k=fault]').count(): pg.locator('form[data-f=what] [data-k=fault]').first.click(); wait(pg, 200)
            pg.locator('form[data-f=what] button[type=submit]').click(); wait(pg, 500)
        if pg.locator('form[data-f=who]').count():
            pg.locator('form[data-f=who] [data-k=responsible][data-v=%s]' % resp).click(); wait(pg, 200)
            pg.locator('form[data-f=who] button[type=submit]').click(); wait(pg, 600)
    # ---- the main walk ----
    cid = product_case('Bosch', 'WGG244ZCGB', SER, 'washing_machine', 'It won’t drain. It stopped halfway through a wash.')
    to_bought(cid); m = a.main()
    if os.environ.get('DBG'): print(m[:1500]); print(a.case(cid)['fix'])
    ok('Where and when did you buy it?' in m and pg.locator('form[data-f=prod162b]').count() == 1 and 'Try these safe checks' not in m, 'the purchase step is the product’s own')
    pg.locator('form[data-f=prod162b] input[data-ocr=f-rcpt]').last.set_input_files(HERE + '/tests/out/prod130_receipt.png'); st = read_wait(pg); m = a.main()
    ok('Receipt read' in st and 'Check what Sorted found' in m and 'Argos' in m and '14 February 2026' in m, 'a receipt photo gives the shop and the date as candidates (%s)' % st[:50])
    c = a.case(cid); f = c['prod']['f']
    ok(f['retailer']['st'] == 'candidate' and f['bought']['st'] == 'candidate' and f['retailer']['src'] == 'receipt' and not c['fix'].get('seller'), 'nothing read is a fact yet, and the repair engine hasn’t got it')
    pg.click('[data-a=prod162-rok]'); wait(pg, 400)
    c = a.case(cid); f = c['prod']['f']
    ok(f['retailer']['st'] == 'confirmed' and f['bought']['v'] == '2026-02-14' and f['bought']['st'] == 'confirmed', 'Looks right confirms them')
    pg.locator('form[data-f=prod162b] [data-k=cover][data-v=no]').click(); wait(pg, 200)
    pg.locator('form[data-f=prod162b] button[type=submit]').click(); wait(pg, 700)
    c = a.case(cid); m = a.main()
    ok(c['fix']['step'] == 'decide' and c['fix']['seller'] == 'Argos' and c['fix']['age'] == 'lt1', 'the repair engine reads the confirmed purchase')
    ok(any(e['label'] == 'Bought from Argos on 14 February 2026, read from the receipt and confirmed by you. Warranty or insurance: no.' for e in c['events']), 'the history says where the purchase details came from')
    ok('BEST NEXT STEP' in m.upper() and 'Contact Argos' in m and 'You bought it from Argos on 14 February 2026' in m and 'Citizens Advice says the shop that sold it should help you sort out a fault.' in m, 'Best next step: the retailer, with the confirmed facts')
    ok(pg.locator('.prod162-best a[href*="citizensadvice.org.uk"]').count() == 1 and pg.locator('.prod162-best a[href^="https://help.argos.co.uk/"]').count() == 1, 'its source and the shop’s checked help page')
    ok('Sorted found Bosch’s UK support page. It hasn’t read Bosch’s instructions for your problem' in m and pg.locator('.prod162-support a[href="https://www.bosch-home.co.uk/customer-service"]').count() == 1, 'the maker’s page: found, not read')
    ok(not re.search(r'checked (?:the|Bosch’s) instructions|Bosch says|verified', m), 'never claims to have checked the instructions')
    rd = pg.inner_text('.prod162-best ul')
    ok('Bosch WGG244ZCGB, washing machine' in rd and 'Serial ••••6789' in rd and 'Bought from Argos' in rd and 'Bought on 14 February 2026' in rd and 'It won’t drain' in rd and SER not in rd, 'Have these ready: confirmed details, the serial masked, their words')
    ok(pg.locator('details.prod162-alt').count() == 1 and 'Contact Bosch' in pg.locator('details.prod162-alt').text_content(), 'the other routes beneath')
    pg.click('.prod162-support a'); wait(pg, 300)
    pg.bring_to_front()
    # Prepare contact → the existing message form
    pg.locator('.prod162-best [data-a=prod162-contact]').first.click(); wait(pg, 600)
    if os.environ.get('DBG'): print(a.main()[:1500])
    ok(pg.input_value('#f-who') == 'Argos', 'the message form is for Argos')
    ask = pg.input_value('#f-ask')
    ok('Bosch washing machine, model WGG244ZCGB' in ask and 'I bought it from Argos on 14 February 2026' in ask and SER not in ask, 'the message: confirmed details, no serial (%s)' % ask[:90])
    pg.click('[data-a=prod162-addserial]'); wait(pg, 200)
    ok(SER in pg.input_value('#f-ask'), 'the full serial only when the person adds it')
    pg.locator('form[data-f=call] button[type=submit]').click(); wait(pg, 700)
    c = a.case(cid)
    ok(not c['promises'] and c['prod'].get('route', {}).get('key') == 'RETAILER' and any(e['label'] == 'Best next step chosen: contact Argos.' for e in c['events']), 'preparing the contact makes no promise; the choice is in the history')
    # their reply → the ordinary core
    a.open(cid); pg.locator('[data-a=panel][data-p="paste"]').first.evaluate('e=>e.click()'); wait(pg, 400)
    pg.fill('#f-paste', 'Argos: An engineer will visit on %s between 8am and 12pm. Your job reference is AR12345.' % long(day(5)))
    pg.click('form[data-f=paste] button[type=submit]'); wait(pg, 800)
    c = a.case(cid)
    ok(not [q for q in c['promises'] if q['status'] == 'open'], 'their reply is proposed, not yet a promise')
    click('[data-a=sug-yes]', 800); click('[data-a=plan-wait148]'); click('[data-a=refs-yes]')
    c = a.case(cid); op = [q for q in c['promises'] if q['status'] == 'open']
    ok(len(op) == 1 and op[0]['party'] == 'Argos', 'confirmed, it is an ordinary promise from Argos')
    ok(c['prod']['f']['serial']['v'] == SER and c['fix']['seller'] == 'Argos', 'the product is untouched by the promise')
    a.home(); hm = a.spot_or_row('Washing machine') or a.main()
    ok('Argos' in hm and SER not in a.main(), 'Home shows the case waiting on Argos, no serial')
    pk = a.pack(cid)
    ok('Product' in pk and 'Bosch WGG244ZCGB, washing machine' in pk and '••••6789' in pk and 'Bought from' in pk and 'https://www.bosch-home.co.uk/customer-service' in pk and 'Argos' in pk and SER not in pk, 'the adviser pack: the product, the serial masked, the support page Sorted found, Argos’s promise')
    tx = a.share_view(cid)
    ok('Argos' in tx and SER not in tx, 'the helper’s link agrees and has no serial')
    # ---- other routes ----
    c2 = product_case('Bosch', 'SMS6ZCI00G', '', 'dishwasher', 'It won’t start at all')
    to_bought(c2); pg.locator('form[data-f=prod162b] button[type=submit]').click(); wait(pg, 700); m = a.main()
    ok('Contact Bosch' in m and 'Sorted doesn’t know where or when you bought it.' in m and pg.locator('.prod162-best a[href^="https://www.bosch-home.co.uk/"]').count() == 1, 'unknown purchase details: the maker, said plainly')
    c3 = product_case('Acme', 'AC100', '', 'coffee', 'It leaks from the bottom')
    to_bought(c3)
    if os.environ.get('DBG'): print(a.main()[:1800]); print(a.case(c3).get('fix'), a.case(c3).get('mode'))
    pg.fill('#pb-shop', 'Argos'); pg.locator('form[data-f=prod162b] button[type=submit]').click(); wait(pg, 700); m = a.main()
    ok('Contact Argos' in m and 'Sorted doesn’t know when you bought it.' in m and 'Sorted doesn’t have a checked support page for Acme yet.' in m, 'an unknown maker with a shop: the shop, and no unchecked link')
    c4 = product_case('Acme', 'AC100', '', 'coffee', 'It leaks from the bottom')
    to_bought(c4); pg.locator('form[data-f=prod162b] button[type=submit]').click(); wait(pg, 700); m = a.main()
    ok('Get a local repairer' in m, 'no maker, no shop: a repairer')
    c5 = product_case('Worcester', 'CDi 30', '', 'boiler', 'No heating since yesterday')
    to_bought(c5)
    if pg.locator('form[data-f=prod162b]').count(): pg.locator('form[data-f=prod162b] button[type=submit]').click(); wait(pg, 700)
    m = a.main()
    ok('Get a Gas Safe registered engineer' in m and pg.locator('.prod162-best a[href*="hse.gov.uk"]').count() >= 1, 'a boiler: a Gas Safe engineer, with the HSE source')
    c6 = product_case('Bosch', 'WAN28281GB', '', 'washing_machine', 'It is leaking')
    to_bought(c6, 'landlord'); m = a.main()
    if pg.locator('[data-a=prod162-contact]').count():
        ok('You said it’s your landlord’s job to fix it' in m, 'someone else’s job: them')
    else:
        ok('landlord' in m.lower(), 'someone else’s job: the landlord route')
    a.close()
finish()
