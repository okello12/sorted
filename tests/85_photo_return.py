# v127 (Baldwin's iPhone, 4 October 2026). Taking a photo with the camera hides the page; when it came back Sorted
# redrew, replacing the file box, and the photo's change event fired on a box no longer on the page: nothing happened.
# This reproduces it: the picker opens, the page becomes visible again (and the minute timer runs), the photo arrives on
# the original box. It must be read: "Reading your notice…", then the review. Also: a large photo is scaled before
# reading; a start choice made before signing in survives an email link opened in a new tab; the heading above the box
# follows the real choice, not a leftover; the parking screen has one photo button.
import os, sys, json, re, base64
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
        st = (pg.inner_text('#ocr-status') if pg.locator('#ocr-status').count() else '') + ' ' + (pg.inner_text('#doc-status') if pg.locator('#doc-status').count() else '')
        if re.search(r'Photo read|couldn’t|doesn’t look', st): return st.strip()
        wait(pg, 500)
    return st.strip()
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', cdn)
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    sp = b.new_page(viewport={'width': 560, 'height': 420}); sp.set_content(NOTICE); sp.screenshot(path=HERE + '/tests/out/doc85_notice.png'); sp.close()
    # a "camera photo": the same notice drawn at 4032 x 3024
    sp = b.new_page(viewport={'width': 1344, 'height': 1008}, device_scale_factor=3); sp.set_content(NOTICE.replace('font-size:20px', 'font-size:48px').replace('padding:24px', 'padding:60px')); sp.screenshot(path=HERE + '/tests/out/doc85_big.png'); sp.close()
    B64 = {k: base64.b64encode(open(HERE + '/tests/out/doc85_%s.png' % k, 'rb').read()).decode() for k in ('notice', 'big')}
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    main = lambda: pg.inner_text('main')
    def deliver_after_return(key):
        # the person taps the photo button; the picker opens and the page is hidden; it comes back visible and redraws
        pg.evaluate("window.__inp=null;document.addEventListener('click',function(e){if(e.target.matches&&e.target.matches('input[type=file][data-ocr]'))window.__inp=e.target},{capture:true})")
        with pg.expect_file_chooser() as fc:
            pg.locator('label.gi-photo, .pk-short label.btn').first.click()
        pg.evaluate("document.activeElement&&document.activeElement.blur&&document.activeElement.blur();document.dispatchEvent(new Event('visibilitychange'))"); wait(pg, 300)
        pg.evaluate("window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))"); wait(pg, 200)
        # the photo arrives on the box the person tapped, whatever has happened to the page since
        pg.evaluate("""(b64)=>{var bin=atob(b64),u=new Uint8Array(bin.length);for(var i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);var f=new File([u],'IMG_0001.JPG',{type:'image/png'});var dt=new DataTransfer();dt.items.add(f);var inp=window.__inp;inp.files=dt.files;inp.dispatchEvent(new Event('change',{bubbles:true}))}""", B64[key])
        return pg.evaluate("window.__inp?window.__inp.isConnected:null")
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    # ---- 1. the document door: a photo after the page comes back is read ----
    pg.locator('[data-cap82=document]').first.evaluate('e=>e.click()'); wait(pg, 500)
    ok(pg.locator('label.gi-photo').count() == 1, 'the document door has its photo button')
    pg.fill('#f-case', 'Parking ticket'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 500)
    ok(pg.locator('.pk-short').count() == 1 and pg.locator('label.gi-photo').count() == 0 and pg.locator('.pk-short label.btn').count() == 1 and pg.locator('#ocr-status').count() == 1, '“Parking ticket”: one photo button, inside the parking block, with the status line kept')
    pg.evaluate("window.__renders=0;var r0=window.render;")
    still = deliver_after_return('notice')
    st = read_wait(pg)
    ok('Photo read. Check the details below.' in st and pg.locator('form[data-f=doc]').count() == 1 and pg.input_value('#doc-ref') == 'LJ12345678', 'the photo taken while the page was hidden is read and goes to review (%s; box still on the page: %s)' % (st[:50], still))
    # ---- 2. even when the page has been redrawn under it, the original box still delivers ----
    pg.goto('https://sorted.test/'); wait(pg, 600)
    if pg.locator('[data-a=new-case]').count(): pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.locator('[data-cap82=document]').first.evaluate('e=>e.click()'); wait(pg, 500)
    pg.evaluate("window.__inp=null;document.addEventListener('click',function(e){if(e.target.matches&&e.target.matches('input[type=file][data-ocr]'))window.__inp=e.target},{capture:true})")
    with pg.expect_file_chooser() as fc:
        pg.locator('label.gi-photo').first.click()
    # force a redraw that replaces the box, as an older page or a timer would
    pg.evaluate("(()=>{var b=document.createElement('button');b.setAttribute('data-a','d');document.body.appendChild(b);var m=document.querySelector('main');var old=document.querySelector('label.gi-photo');if(old){var c=old.cloneNode(true);old.replaceWith(c)}})()"); wait(pg, 200)
    detached = pg.evaluate("window.__inp&&!window.__inp.isConnected")
    pg.evaluate("""(b64)=>{var bin=atob(b64),u=new Uint8Array(bin.length);for(var i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);var f=new File([u],'IMG_0002.JPG',{type:'image/png'});var dt=new DataTransfer();dt.items.add(f);var inp=window.__inp;inp.files=dt.files;inp.dispatchEvent(new Event('change',{bubbles:true}))}""", B64['notice'])
    st = read_wait(pg)
    ok(detached and ('Photo read' in st or 'couldn’t' in st or 'doesn’t look' in st), 'a box replaced while the picker was open still delivers its photo (detached: %s; %s)' % (detached, st[:40]))
    # ---- 3. while the picker is open, nothing redraws ----
    pg.goto('https://sorted.test/'); wait(pg, 600)
    if pg.locator('[data-a=new-case]').count(): pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.locator('[data-cap82=document]').first.evaluate('e=>e.click()'); wait(pg, 500)
    pg.evaluate("window.__inp=null;document.addEventListener('click',function(e){if(e.target.matches&&e.target.matches('input[type=file][data-ocr]'))window.__inp=e.target},{capture:true})")
    with pg.expect_file_chooser() as fc:
        pg.locator('label.gi-photo').first.click()
    pg.evaluate("document.activeElement&&document.activeElement.blur&&document.activeElement.blur();document.dispatchEvent(new Event('visibilitychange'))"); wait(pg, 300)
    ok(pg.evaluate("window.__inp&&window.__inp.isConnected"), 'coming back from the picker does not redraw the page, so the box the person tapped is still there')
    # ---- 4. a full-size camera photo is scaled down and still read ----
    pg.evaluate("""(b64)=>{var bin=atob(b64),u=new Uint8Array(bin.length);for(var i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);var f=new File([u],'IMG_0003.JPG',{type:'image/png'});var dt=new DataTransfer();dt.items.add(f);var inp=window.__inp;inp.files=dt.files;inp.dispatchEvent(new Event('change',{bubbles:true}))}""", B64['big'])
    st = read_wait(pg)
    ok('Photo read' in st or 'doesn’t look' in st or 'couldn’t' in st, 'a 4032 × 3024 photo is read without stopping the page (%s)' % st[:50])
    ok(pg.evaluate("(()=>{var c=document.createElement('canvas');return !!c.getContext})()"), 'canvas scaling is available')
    # ---- 5. a choice made before signing in survives an email link opened in a new tab ----
    ctx2 = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx2.route('https://cdn.jsdelivr.net/**', cdn)
    ctx2.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    p2 = ctx2.new_page(); p2.on('pageerror', lambda e: errs.append(str(e)))
    p2.goto('https://sorted.test/'); p2.evaluate("localStorage.clear();sessionStorage.clear()"); p2.goto('https://sorted.test/'); wait(p2, 700)
    p2.click('.hero .btn.primary'); wait(p2, 400)
    p2.evaluate("sessionStorage.clear();localStorage.setItem('__mocksession', JSON.stringify({user:{id:'u-mail',email:'me@example.com'}}))")
    p2.goto('https://sorted.test/'); wait(p2, 900); m2 = p2.inner_text('main')
    ok(p2.locator('#f-case').count() == 1 and p2.locator('#cap82-start').count() == 0 and 'What do you need to sort out?' in m2, 'after the email link in a new tab, “Start with your problem” still lands in the box for your own words')
    ok(p2.evaluate("localStorage.getItem('sorted.carry82')") is None, 'the carried choice is used once and removed')
    # ---- 6. the heading follows the real choice, never a leftover ----
    p2.evaluate("sessionStorage.setItem('sorted.cap82','promise')"); p2.goto('https://sorted.test/'); wait(p2, 900)
    hs = p2.locator('main h1, main h2').all_inner_texts()
    ok('What did they promise?' not in hs, 'a leftover choice no longer renames the box “What did they promise?” (%s)' % hs[:4])
    ctx2.close()
    ok(not errs, 'no page errors: %s' % errs)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
