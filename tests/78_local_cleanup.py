# v122 (remediation Phase A item 2): one function, clearLocalUserData(), removes what Sorted keeps on this phone for a
# person. After sign-out, after deleting the account, after a guest moves to an email account, after a draft expires
# and after a failed photo read, no case words, draft words or read words are left in localStorage or sessionStorage.
# Settings has "Remove the copy from this phone", which clears the copy and reloads the cases from the account.
# Preferences that say nothing about a case (appearance, usage records) stay.
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
def cdn(r):
    u = r.request.url
    if '/npm/tesseract.js@5.1.1/dist/' in u: return r.fulfill(path=O + 'tesseract.js/dist/' + u.split('/dist/')[1], content_type='application/javascript', headers=H)
    if '/npm/tesseract.js-core@5.1.1/' in u: f = u.split('@5.1.1/')[1]; return r.fulfill(path=O + 'tesseract.js-core/' + f, content_type='application/wasm' if f.endswith('.wasm') else 'application/javascript', headers=H)
    if '/npm/@tesseract.js-data/eng@1.0.0/' in u: return r.fulfill(path=O + '@tesseract.js-data/eng/4.0.0_best_int/eng.traineddata.gz', content_type='application/gzip', headers=H)
    return r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript')
def shot(b, path, html, w=560, h=420):
    sp = b.new_page(viewport={'width': w, 'height': h}); sp.set_content(html); sp.screenshot(path=path); sp.close()
NOTICE_HTML = ('<body style="margin:0;background:#fff;font-family:Arial;font-size:20px;line-height:1.5;padding:24px"><b>LAMBETH COUNCIL</b><br><b>PENALTY CHARGE NOTICE</b><br>'
               'PCN Number: LJ12345678<br>Vehicle registration: AB12 CDE<br>Date of contravention: 03/10/2026<br>Penalty charge: £130, reduced to £65 if paid within 14 days</body>')
BLUR_HTML = NOTICE_HTML.replace('padding:24px"', 'padding:24px;filter:blur(3.5px)"')
SESSION = lambda uid, em: json.dumps({'user': {'id': uid, 'email': em}})
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', cdn)
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    P = {k: HERE + '/tests/out/doc78_%s.png' % k for k in ('notice', 'blur')}
    shot(b, P['notice'], NOTICE_HTML); shot(b, P['blur'], BLUR_HTML)
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: [x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment']
    # every stored value except the mock's own database and session
    def stored():
        return pg.evaluate("(()=>{var o={};[localStorage,sessionStorage].forEach(function(st,i){for(var j=0;j<st.length;j++){var k=st.key(j);if(/^__/.test(k))continue;o[(i?'s:':'l:')+k]=st.getItem(k)}});return o})()")
    def leaks(word):
        return [k for k, v in stored().items() if word.lower() in (v or '').lower()]
    def signed_in(): return pg.evaluate("!!localStorage.getItem('__mocksession')")
    def sign_in(uid='u-me', em='me@example.com'):
        pg.evaluate("localStorage.setItem('__mocksession', %s)" % json.dumps(SESSION(uid, em))); pg.goto('https://sorted.test/'); wait(pg, 700)
    def start(text):
        pg.goto('https://sorted.test/'); wait(pg, 500)
        if pg.locator('[data-a=new-case]').count(): pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
        if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
        if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    def account(tab=None):
        pg.goto('https://sorted.test/'); wait(pg, 500); pg.locator('[data-a=data]').first.evaluate('e=>e.click()'); wait(pg, 400)
        if tab: pg.locator('.acct112-nav [data-v=%s]' % tab).evaluate('e=>e.click()'); wait(pg, 400)
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); sign_in()
    pg.evaluate("localStorage.setItem('sorted.theme','dark')")
    # ---- 1. a case and a draft, then sign out: nothing recoverable ----
    start('Zephyrine Plumbing said they would refund £240 by Friday, ref ZP-7781')
    ok(any('Zephyrine' in (x.get('title') or '') + json.dumps(x) for x in cases()), 'the case is on the server')
    ok(leaks('Zephyrine'), 'while signed in the copy on this phone has the case (%d values)' % len(leaks('Zephyrine')))
    pg.goto('https://sorted.test/'); wait(pg, 500); pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300); pg.type('#f-case', 'Quokka Dental still owe me a crown fitting'); wait(pg, 300)
    ok(leaks('Quokka'), 'a draft is kept on this phone while signed in')
    account(); pg.click('[data-a=signout]'); wait(pg, 800)
    ok(not signed_in() and not leaks('Zephyrine') and not leaks('Quokka') and not leaks('ZP-7781'), 'after sign-out no case words, reference or draft words are left in localStorage or sessionStorage')
    ok(pg.evaluate("localStorage.getItem('sorted.theme')") == 'dark', 'the appearance setting stays')
    # ---- 2. delete the account: the same ----
    sign_in(); wait(pg, 300)
    ok(leaks('Zephyrine'), 'signing in again brings the copy back from the account')
    pg.goto('https://sorted.test/'); wait(pg, 500); pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300); pg.type('#f-case', 'Quokka Dental again'); wait(pg, 300)
    account(); pg.click('[data-a=wipe-ask]'); wait(pg, 300); pg.click('[data-a=wipe]'); wait(pg, 900)
    ok(not signed_in() and not cases() and not leaks('Zephyrine') and not leaks('Quokka'), 'after deleting the account nothing of the cases or drafts is left on this phone')
    # ---- 3. an expired draft is removed, not just ignored ----
    sign_in('u-two', 'two@example.com')
    pg.evaluate("localStorage.setItem('sorted.draft.u-two', JSON.stringify({text:'Marmoset Removals lost my sofa', at: Date.now()-8*86400000}))")
    pg.goto('https://sorted.test/'); wait(pg, 600)
    ok('Marmoset' not in pg.inner_text('main') and pg.evaluate("localStorage.getItem('sorted.draft.u-two')") is None, 'a draft older than 7 days is removed from the phone when Sorted looks for it')
    # ---- 4. a photo read: a failed read keeps no words; a review that is left keeps none after sign-out ----
    pg.goto('https://sorted.test/'); wait(pg, 500)
    if pg.locator('[data-a=new-case]').count(): pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.fill('#f-case', 'PCN'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 500)
    pg.set_input_files('input[data-ocr=f-case]', P['blur'])
    for _ in range(240):
        st = pg.inner_text('#ocr-status') if pg.locator('#ocr-status').count() else ''
        if re.search(r'Photo read|couldn’t|doesn’t look', st): break
        wait(pg, 500)
    ok(pg.locator('.doc121-fail').count() == 1 and not leaks('LAMBETH') and not leaks('LJ12345678'), 'a failed read leaves no words from the photo on this phone')
    pg.set_input_files('input[data-ocr=f-case]', P['notice'])
    for _ in range(240):
        st = pg.inner_text('#ocr-status') if pg.locator('#ocr-status').count() else ''
        if re.search(r'Photo read|couldn’t|doesn’t look', st): break
        wait(pg, 500)
    ok(pg.locator('form[data-f=doc]').count() == 1 and pg.input_value('#doc-ref') == 'LJ12345678', 'a clear read is on screen for review')
    account(); pg.click('[data-a=signout]'); wait(pg, 800)
    ok(not signed_in() and not leaks('LJ12345678') and not leaks('Lambeth'), 'signing out during a review leaves nothing read from the photo')
    # ---- 5. a guest moves to an email account: the carried copy is for the new account, the guest's copy goes ----
    pg.goto('https://sorted.test/#start'); wait(pg, 400)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    guest = pg.evaluate("JSON.parse(localStorage.getItem('__mocksession')).user.id")
    start('Pangolin Gas said the engineer comes on Tuesday, job PG-4412')
    ok(pg.evaluate("!!localStorage.getItem('sorted.cache.'+%s)" % json.dumps(guest)) and leaks('Pangolin'), 'the guest has a copy on this phone')
    pg.evaluate("(()=>{var b=document.createElement('button');b.setAttribute('data-a','claim-signin');document.querySelector('main').appendChild(b);b.click()})()"); wait(pg, 800)
    st = stored()
    ok(not signed_in() and 'l:sorted.carry' in st and 'Pangolin' in st['l:sorted.carry'] and pg.evaluate("localStorage.getItem('sorted.cache.'+%s)" % json.dumps(guest)) is None and [k for k in leaks('Pangolin') if k != 'l:sorted.carry'] == [], 'moving to an email account keeps only the carried copy; the guest’s own copy and everything else go')
    sign_in('u-mail', 'mail@example.com'); wait(pg, 800)
    ok(signed_in() and any('Pangolin' in (x.get('title') or '') for x in cases()) and pg.evaluate("localStorage.getItem('sorted.carry')") is None and pg.evaluate("localStorage.getItem('sorted.cache.'+%s)" % json.dumps(guest)) is None, 'the email account takes the case across and nothing of the guest is left')
    # ---- 6. signing in removes copies another account left on this phone ----
    pg.evaluate("localStorage.setItem('sorted.cache.u-old', JSON.stringify([{id:'x1',title:'Wombat Windows refund',events:[],promises:[]}]));localStorage.setItem('sorted.draft.u-old', JSON.stringify({text:'Wombat again',at:Date.now()}))")
    pg.reload(); wait(pg, 700)
    ok(not leaks('Wombat') and pg.evaluate("!!localStorage.getItem('sorted.cache.u-mail')"), 'a signed-in load removes copies left by another account and keeps this one')
    # ---- 7. Settings: remove the copy from this phone ----
    account('acct-settings'); m = pg.inner_text('main')
    ok('This phone' in m and 'Remove the copy from this phone' in m and 'What is saved on Sorted’s servers is not affected' in m, 'Settings offers to remove the copy and says the account is not affected')
    pg.click('[data-a=local-reset]'); wait(pg, 1500)
    ok(signed_in() and any('Pangolin' in (x.get('title') or '') for x in cases()) and pg.evaluate("!!localStorage.getItem('sorted.cache.u-mail')") and 'Pangolin' in pg.inner_text('main'), 'the copy is removed and the cases come back from the account')
    pg.evaluate("localStorage.setItem('__failWrites','1')")
    pg.goto('https://sorted.test/?task=%s' % [x for x in cases() if 'Pangolin' in (x.get('title') or '')][0]['id']); wait(pg, 600)
    pg.evaluate("document.querySelectorAll('details.case56-more').forEach(d=>d.open=true)")
    pg.click('[data-a=panel][data-p=rename]'); wait(pg, 250); pg.fill('#f-rename', 'Pangolin Gas engineer'); pg.click('form[data-f=rename] button[type=submit]'); wait(pg, 400)
    account('acct-settings')
    ok(pg.locator('[data-a=local-reset]').count() == 0 and 'A change is still being saved' in pg.inner_text('main'), 'with a change not yet saved, the copy can’t be removed and Settings says why')
    pg.evaluate("localStorage.removeItem('__failWrites')")
    ok(not errs, 'no page errors: %s' % errs)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
