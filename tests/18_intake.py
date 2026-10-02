# v51: intake, first slice. Everything brought into an existing case goes through one reader and is kept in the
# case history as evidence, with where it came from. Nothing changes the promise without a tap.
import os, sys, json, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dates import ahead
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
def case(pg, said):
    return pg.evaluate("(x)=>JSON.parse(localStorage.getItem('__mockdb')).tasks.map(y=>y.data).find(y=>y.said===x)", said)
def labels(t): return [e['label'] for e in t['events']]
T = "Currys refund hasn't arrived, order 445566"
F1, F2, F3 = ahead(9), ahead(12), ahead(15)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', cdn)
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    # a picture of a message, made locally
    sp = b.new_page(viewport={'width': 390, 'height': 230}); sp.set_content('<body style="margin:0;background:#fff;font-family:Arial"><div style="margin:20px;padding:14px;background:#e9e9eb;border-radius:18px;font-size:17px">Currys: your refund will be paid by %s. Order 445566.</div></body>' % F3['long'])
    os.makedirs(HERE + '/tests/out', exist_ok=True); sp.screenshot(path=HERE + '/tests/out/intake_sms.png'); sp.close()
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 200); pg.click('[data-a=anon-start]'); wait(pg)
    pg.fill('#f-case', T); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg)
    # 1 a pasted message with no date is kept, and nothing else changes
    M1 = "Hi, we've passed this to our refunds team. Thanks for your patience."
    pg.click('[data-a=panel][data-p=paste]'); wait(pg); pg.fill('#f-paste', M1); pg.click('form[data-f=paste] button[type=submit]'); wait(pg)
    t = case(pg, T)
    ok("couldn’t find a date" in pg.inner_text('main') and 'Added to the case' in pg.inner_text('main'), 'no date: says it was added and nothing else changed')
    ok(any(l.startswith('Added a message: “Hi, we') for l in labels(t)), 'no date: the message is kept in the history')
    ok(not t.get('sugP') and not t['promises'], 'no date: no promise proposed or changed')
    pg.click('form[data-f=paste] button[type=submit]'); wait(pg)
    ok(sum(1 for l in labels(case(pg, T)) if l.startswith('Added a message: “Hi, we')) == 1, 'pressing Read it twice keeps it once')
    pg.click('form[data-f=paste] [data-a=panel][data-p=""]'); wait(pg)
    # 2 a pasted message with a date is kept and proposes the promise
    M2 = "Your refund will be paid by %s. Order 445566." % F1['dm']
    pg.click('[data-a=panel][data-p=paste]'); wait(pg); pg.fill('#f-paste', M2); pg.click('form[data-f=paste] button[type=submit]'); wait(pg)
    t = case(pg, T)
    ok(any(l.startswith('Added a message: “Your refund will be paid') for l in labels(t)), 'with a date: the message is kept in the history')
    ok(t.get('sugP') and t['sugP']['ref'] == '445566' and pg.locator('.sug').count() == 1, 'with a date: a promise is proposed, not saved')
    pg.click('[data-a=sug-yes]'); wait(pg)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 150)
    # 3 a screenshot read on the phone says so in the history
    pg.click('[data-a=panel][data-p=paste]'); wait(pg)
    pg.set_input_files('input[data-ocr=f-paste]', HERE + '/tests/out/intake_sms.png')
    for i in range(240):
        st = pg.inner_text('#ocr-status') if pg.locator('#ocr-status').count() else ''
        if st.startswith('Done') or st.startswith('Sorted couldn'): break
        wait(pg, 500)
    pg.click('form[data-f=paste] button[type=submit]'); wait(pg)
    t = case(pg, T)
    ok(any(l.startswith('Added a screenshot: “') for l in labels(t)), 'screenshot: kept in the history as a screenshot')
    ok(t.get('sugP') and pg.locator('.sug').count() == 1, 'screenshot: its date is proposed')
    pg.click('[data-a=sug-no]'); wait(pg)
    # 4 a new message that matches the case is added there through the same reader
    pg.click('[data-a=home]'); wait(pg)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
    M4 = "Currys said the refund will now be paid on %s, order 445566" % F2['dm']
    pg.fill('#f-case', M4); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    ok(pg.locator('[data-a=match-add]').count() == 1, 'matching message: offers to add it to the case')
    pg.click('[data-a=match-add]'); wait(pg)
    t = case(pg, T)
    ok(any(l.startswith('Added a message: “Currys said the refund will now be paid') for l in labels(t)), 'matching message: kept in that case')
    ok(t.get('sugP') and F2['dm'].split()[0] in pg.inner_text('.sug'), 'matching message: proposes the new date')
    pg.click('[data-a=sug-no]'); wait(pg)
    # 5 shared from another app, then added to the case
    M5 = "Currys: your refund is delayed. It will now be paid by %s. Order 445566." % F3['dm']
    pg.goto('https://sorted.test/?s=2#new=' + urllib.parse.quote(M5)); wait(pg, 600)
    # v53: a shared message asks where it goes, with the likely case first
    ok('Where does this go?' in pg.inner_text('main') and pg.locator('form[data-f=case] button[type=submit]').count() == 0, 'v53: shared message asks where it goes, no Start yet')
    ok('Nothing is saved until you choose where it goes' in pg.inner_text('main'), 'v53: says nothing is saved until you choose')
    tos = pg.locator('[data-a=share-to]')
    ok(tos.count() >= 1 and 'Looks like this one' in tos.nth(0).inner_text() and 'Currys' in tos.nth(0).inner_text(), 'v53: the matching case is offered first')
    ok(pg.locator('.share-pick').bounding_box()['y'] < pg.locator('.home44-intro').bounding_box()['y'] if pg.locator('.home44-intro').count() else True, 'v53: the question sits above the rest of Home')
    ok(not any('delayed' in l for l in labels(case(pg, T))), 'v53: nothing added before a tap')
    tos.nth(0).click(); wait(pg)
    t = case(pg, T)
    ok(any(l.startswith('Added a message shared from another app: “Currys') for l in labels(t)), 'shared message: kept, and says it was shared')
    ok(all(len(l) < 260 for l in labels(t)), 'evidence lines are kept short')
    # v52: "What they sent" on the case page
    if pg.locator('[data-a=sug-no]').count(): pg.click('[data-a=sug-no]'); wait(pg)
    ok(pg.locator('.evidence').count() == 1, 'v52: the case shows What they sent')
    items = pg.locator('.evidence > .ev-list > .ev-item')
    ok(items.count() == 3 and 'Show 2 more' in pg.inner_text('.ev-more summary'), 'v52: newest three shown, the rest folded (%d)' % items.count())
    first = items.nth(0).inner_text().lower()
    ok('shared' in first and 'delayed' in first, 'v52: newest first, labelled Shared')
    srcs = [x.strip().lower() for x in pg.locator('.evidence .ev-src').all_text_contents()]
    ok(srcs == ['shared', 'message', 'screenshot', 'message', 'message'], 'v52: each says where it came from: %s' % srcs)
    n = pg.evaluate("document.querySelector('main').textContent.split('passed this to our refunds team').length-1")
    ok(n == 1, 'v52: the history points to the block instead of repeating the message (%d)' % n)
    ok('It’s under What they sent' in pg.inner_text('main'), 'v52: history line says where to find it')
    pg.locator('.evidence').scroll_into_view_if_needed(); pg.screenshot(path=HERE + '/tests/out/evidence.png')
    # v53: a second case, then a share that goes to the case you pick, not the one Sorted guessed
    pg.click('[data-a=home]'); wait(pg)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
    T2 = "The landlord still hasn't fixed the boiler"
    pg.fill('#f-case', T2); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg)
    ok(case(pg, T2) is not None, 'second case made')
    M6 = "Hi, the plumber can come on %s. Thanks" % F2['dm']
    pg.goto('https://sorted.test/?s=3#new=' + urllib.parse.quote(M6)); wait(pg, 600)
    names = [x.strip() for x in pg.locator('[data-a=share-to] .share-t').all_text_contents()]
    ok(len(names) == 2 and pg.locator('.share-hint').count() == 0, 'v53: no guess when nothing matches, every open case listed: %s' % names)
    pg.fill('#f-case', M6 + " Ref PL-90")
    pg.locator('[data-a=share-to]', has_text='landlord').click(); wait(pg)
    t2 = case(pg, T2)
    ok(any(l.startswith('Added a message shared from another app: “Hi, the plumber') and 'PL-90' in l for l in labels(t2)), 'v53: goes to the chosen case, with your edits')
    ok(not any('plumber' in l for l in labels(case(pg, T))), 'v53: the other case is untouched')
    ok(t2.get('sugP') and pg.locator('.sug').count() == 1, 'v53: its date is proposed, not saved')
    ok(not t2['promises'] or all(q['status'] != 'open' or 'plumber' not in q.get('said', '') for q in t2['promises']), 'v53: the promise waits for a tap')
    pg.click('[data-a=sug-no]'); wait(pg)
    # v53: or start a new case from it
    M7 = "Amazon: your replacement kettle will arrive on %s." % F1['dm']
    pg.goto('https://sorted.test/?s=4#new=' + urllib.parse.quote(M7)); wait(pg, 600)
    n_cases = pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks.length")
    pg.click('[data-a=share-new]'); wait(pg)
    ok(pg.locator('.share-pick').count() == 0 and pg.locator('form[data-f=case] button[type=submit]').count() == 1, 'v53: Start a new case shows Start')
    ok('Nothing is saved until you press Start' in pg.inner_text('main'), 'v53: and says so')
    pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    ok(pg.locator('[data-a=match-add]').count() == 0 and pg.locator('form[data-f=baseline]').count() == 1, 'v53: no second question about which case')
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg)
    ok(pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks.length") == n_cases + 1, 'v53: a new case is made')
    pg.goto('https://sorted.test/?s=5#new=' + urllib.parse.quote(M6)); wait(pg, 600)
    pg.locator('.share-pick').scroll_into_view_if_needed(); pg.screenshot(path=HERE + '/tests/out/share_pick.png')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
