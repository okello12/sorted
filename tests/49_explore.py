# v95: what else Sorted is for. The six doors list broader examples; "Things people use Sorted for" shows 12 examples,
# each opening its flow with the question and examples set; a line on Home after a first case; "Need help with
# something else?" on a finished case; and a Home fold of examples by part of life.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
def db(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {'tasks': []}
def newest(pg): return sorted([x['data'] for x in db(pg)['tasks']], key=lambda x: x.get('created') or '')[-1]
def home(pg):
    pg.goto('https://sorted.test/'); wait(pg, 600)
    if pg.locator('[data-a=gi-back]').count(): pg.click('[data-a=gi-back]'); wait(pg)
def chip(pg, k): pg.locator('#cap82-start [data-cap95=%s]' % k).first.click(); wait(pg, 500)
def baseline(pg):
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count():
        pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 550)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    # 1 the doors teach more, and the strip is there with 12 examples
    m = pg.inner_text('#cap82-start')
    ok('Washing machine, boiler, broadband' in m and 'HMRC, the council, your insurer' in m and 'Passport, driving licence, MOT' in m, 'the six doors list broader examples')
    ok('Things people use Sorted for' in m and pg.locator('#cap82-start .cap95-chip').count() == 32, 'the strip has 32 examples (v97)')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'the strip scrolls inside itself, not the page')
    ok(pg.locator('details.cap95-explore').count() == 1 and pg.locator('.cap95-also').count() == 0, 'the fold and search are there from the first visit (v97), the extra line is not')
    # every example opens a flow
    keys = pg.locator('#cap82-start .cap95-chip').evaluate_all("els=>els.map(e=>e.getAttribute('data-cap95'))")
    bad = []
    for k in keys:
        pg.evaluate("sessionStorage.clear()"); pg.goto("https://sorted.test/#start"); pg.reload(); wait(pg, 700); pg.locator('#cap82-start [data-cap95=%s]' % k).first.evaluate('e=>e.click()'); wait(pg, 500)
        if not (pg.locator('.gi-form').count() or pg.locator('.pk-short').count() or pg.input_value('#f-case') if pg.locator('#f-case').count() else pg.locator('.gi-form').count()): bad.append(k)
        if db(pg)['tasks']: bad.append(k + ' created a case')
    ok(not bad and len(keys) == 32, 'each of the 32 examples opens its flow and creates nothing: %s' % bad)
    home(pg)
    ok(pg.locator('[data-a=ex-all]').count() == 1, '"See all and search" under the strip')
    pg.click('[data-a=ex-all]'); wait(pg, 600)
    ok(pg.evaluate("document.getElementById('cap95-explore').open"), 'and it opens the fold')
    # 2 each example opens its flow with the context set
    chip(pg, 'refund')
    ok(pg.locator('.gi-form').count() == 1 and 'Who owes you a refund?' in pg.inner_text('main') and 'Currys, Amazon, your airline' in (pg.get_attribute('#gi-who', 'placeholder') or ''), 'refund: the promise questions, about a refund')
    pg.fill('#gi-who', 'Currys'); pg.fill('#gi-what', 'refund my £89 by Friday')
    pg.click('form[data-f=gi] button[type=submit]'); wait(pg, 600); baseline(pg)
    ok(newest(pg)['title'].startswith('Currys refund') and pg.locator('[data-a=sug-yes]').count() == 1, 'and it becomes a Currys refund with the promise to confirm')
    home(pg); chip(pg, 'landlord')
    ok('What does your landlord need to fix?' in pg.inner_text('main') and pg.locator('input[name=gi-item][value="Something else"]').is_checked(), 'landlord repair: the broken flow, "Something else" ticked')
    pg.fill('#gi-what', 'damp in the bedroom'); pg.click('form[data-f=gi] button[type=submit]'); wait(pg, 600); baseline(pg)
    t = newest(pg)
    ok(t['mode'] == 'fix' and 'landlord' in t['title'].lower(), 'and it is a repair for the landlord: %s' % t['title'])
    home(pg); chip(pg, 'parking')
    ok(pg.locator('.pk-short').count() == 1 and pg.locator('.pk-short input[type=file]').count() == 1, 'parking fine: straight to "add a photo of the notice"')
    home(pg); chip(pg, 'hmrc')
    ok(pg.input_value('#f-case').startswith('Letter from HMRC') and pg.locator('.gi-photo input[type=file]').count() == 1, 'HMRC letter: the letter box, started for you, with the photo button')
    home(pg); chip(pg, 'council')
    ok(pg.input_value('#gi-who') == 'The council' and 'What do you need from the council?' in pg.inner_text('main'), 'council: the call, to the council')
    home(pg); chip(pg, 'passport')
    ok(pg.locator('input[name=gi-item][value=Passport]').is_checked() and pg.locator('#gi-when').count() == 1, 'passport: renew, with Passport ticked')
    home(pg); chip(pg, 'subscription')
    ok('Who should have cancelled it?' in pg.inner_text('main'), 'subscription: the chase flow')
    # 3 after a first case: one line on Home, and the fold
    home(pg)
    ok(pg.locator('.cap95-also').count() == 1 and 'Sorted can also help with' in pg.inner_text('.cap95-also'), 'Home: one line saying what else it helps with (v96: fitted to the last case)')
    ok(pg.locator('details.cap95-explore').count() == 1 and pg.locator('details.cap95-explore .cap95-theme').count() == 9, 'the fold has nine parts of life')
    if not pg.evaluate("document.getElementById('cap95-explore').open"): pg.click('details.cap95-explore summary'); wait(pg, 200)
    pg.locator('details.cap95-explore [data-cap95=insurance]').first.click(); wait(pg, 600)
    ok('Who is dealing with your claim?' in pg.inner_text('main'), 'an example in the fold opens its flow too')
    # 4 a finished case suggests three others
    home(pg)
    cid = newest(pg)['id']
    pg.evaluate("(id)=>{var d=JSON.parse(localStorage.getItem('__mockdb'));var x=d.tasks.find(y=>y.data.id===id).data;x.board='done';x.outcome='Fixed';localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", cid)
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700)
    ok(pg.locator('.cap95-next').count() == 1 and pg.locator('.cap95-next .cap95-chip').count() == 3, 'a finished case: "Need help with something else?" with three examples')
    pg.locator('.cap95-next .cap95-chip').first.click(); wait(pg, 700)
    ok(pg.locator('.gi-form').count() == 1 or pg.locator('#f-case').count() == 1 or pg.locator('.pk-short').count() == 1, 'and one opens its flow')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'nothing scrolls sideways')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
