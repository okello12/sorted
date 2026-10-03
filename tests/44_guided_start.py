# v91, v92: each start choice asks at most two short questions, then goes through the normal reader. "I have a letter"
# leads with the photo button. "PCN" on its own asks for the notice. "Something else" and "your own words" keep the box.
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
def home(pg): pg.goto('https://sorted.test/'); wait(pg, 600)
def choose(pg, k): pg.locator('[data-cap82=%s]' % k).first.click(); wait(pg, 500)
def baseline(pg):
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count():
        pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    # 1 "They promised me something" asks two things, not one blank box
    choose(pg, 'promise')
    ok(pg.locator('.gi-form #gi-who').count() == 1 and pg.locator('#gi-what').count() == 1 and pg.locator('.gi-form input[type=text], .gi-form textarea').count() == 2 and pg.locator('#f-case').count() == 0, 'promise: two questions, not the blank box')
    ok(not pg.locator('.cap82').first.is_visible() and 'Nothing here yet' not in pg.inner_text('main'), 'the choices and the empty list step aside while you answer')
    ok(db(pg)['tasks'] == [], 'nothing is created yet')
    pg.click('form[data-f=gi] button[type=submit]'); wait(pg)
    ok('Say who it is' in pg.inner_text('main'), 'it asks for who, if left empty')
    pg.fill('#gi-who', 'Currys'); pg.fill('#gi-what', 'refund my £89 by Friday, ref 445566')
    pg.click('form[data-f=gi] button[type=submit]'); wait(pg, 600); baseline(pg)
    t = newest(pg)
    ok(t['title'].startswith('Currys refund') and 'Currys said they would refund my £89 by Friday, ref 445566' in t.get('said', ''), 'it becomes one sentence and a Currys refund case: %s' % t['title'])
    ok(pg.locator('[data-a=sug-yes]').count() == 1 and 'Currys' in pg.inner_text('main'), 'and Sorted proposes the promise to confirm, as before')
    pg.click('[data-a=sug-yes]'); wait(pg)
    ok(newest(pg)['promises'][-1]['ref'] == '445566', 'the reference is kept on the promise')
    # 2 "I need to chase something"
    home(pg); choose(pg, 'chase')
    ok(pg.locator('#gi-who').count() == 1 and pg.locator('#gi-what').count() == 1 and pg.locator('#gi-since').count() == 0, 'chase: who and what is outstanding')
    pg.fill('#gi-who', 'British Gas'); pg.fill('#gi-what', 'the engineer visit for the boiler')
    pg.click('form[data-f=gi] button[type=submit]'); wait(pg, 600); baseline(pg)
    ok('British Gas' in newest(pg)['title'] or 'British Gas' in newest(pg).get('said', ''), 'chase: a British Gas case')
    # 3 "I need to make a call" lands on the call, ready
    home(pg); choose(pg, 'call')
    pg.fill('#gi-who', 'the council'); pg.fill('#gi-what', 'my council tax bill')
    pg.click('form[data-f=gi] button[type=submit]'); wait(pg, 600); baseline(pg)
    ok(newest(pg).get('said', '').startswith('Call the council about my council tax bill'), 'call: the case is about the call')
    # 4 "Something's broken" asks which thing and whose job it is
    home(pg); choose(pg, 'fix')
    ok(pg.locator('input[name=gi-item]').count() == 4 and pg.locator('input[name=gi-resp]').count() == 0, 'broken: which thing and what it is doing, nothing more %s' % pg.locator('input[name=gi-item]').count())
    pg.click('label.gi-chip:has-text("Boiler or heating")'); pg.fill('#gi-what', 'no hot water, my landlord has been told')
    pg.click('form[data-f=gi] button[type=submit]'); wait(pg, 600); baseline(pg)
    t = newest(pg)
    ok(t['mode'] == 'fix' and 'landlord' in t['title'].lower(), 'broken: a repair case with the landlord: %s' % t['title'])
    # 5 "I have a letter or document" leads with the photo button
    home(pg); choose(pg, 'document')
    ok(pg.locator('.gi-photo input[type=file][data-ocr=f-case]').count() == 1 and pg.locator('#f-case').count() == 1, 'letter: a big photo button first, the box still there')
    # 6 "PCN" on its own asks for the notice
    pg.fill('#f-case', 'Pcn'); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    ok(pg.locator('.pk-short').count() == 1 and 'can’t see what needs sorting' not in pg.inner_text('main'), '"Pcn" asks for the notice, not "can’t see what needs sorting"')
    ok(pg.locator('.pk-short input[type=file]').count() == 1, 'with a photo button')
    pg.click('[data-a=pk-short-go]'); wait(pg, 500)
    ok(pg.locator('form[data-f=baseline]').count() == 1 or pg.locator('.note').count() >= 1, '"Carry on without it" carries on')
    # 7 "Something else" and "your own words" keep the box; "Choose something else" goes back
    home(pg); choose(pg, 'promise'); pg.click('[data-a=gi-own]'); wait(pg)
    ok(pg.locator('#f-case').count() == 1 and pg.locator('.gi-form').count() == 0, '"your own words" brings the box back')
    home(pg); choose(pg, 'call'); pg.click('[data-a=gi-back]'); wait(pg)
    ok(pg.locator('.gi-form').count() == 0 and pg.locator('[data-cap82]').first.is_visible(), '"Choose something else" goes back to the choices')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'nothing scrolls sideways')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
