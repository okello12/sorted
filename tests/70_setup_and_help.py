# v113: a repair starts from the thing named (never a washing machine nobody mentioned); an unknown thing gets an honest
# general route; "Sort something new" stays closed on a returning Home until asked, with the discovery fold inside it and
# nothing repeated; an unfinished case says "Finish setting up this case" and the health line waits; Help sits beside
# Account and lands on Help & About; every chosen chip looks the same.
import os, sys, json, datetime, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    def poke(js): pg.evaluate("(js)=>{var d=JSON.parse(localStorage.getItem('__mockdb'));(new Function('d',js))(d);localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", js)
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    def start(text, door='other'):
        pg.goto('https://sorted.test/'); wait(pg, 500)
        if pg.locator('.home111-newbtn').count(): pg.click('.home111-newbtn'); wait(pg, 400)
        pg.locator('[data-cap82=%s]' % door).first.evaluate('e=>e.click()'); wait(pg)
        if door != 'other' and pg.locator('.gi-own, [data-a=gi-own]').count(): pg.locator('[data-a=gi-own]').first.click(); wait(pg)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
        return cases()[-1]['id']
    # 1 the alarm: its own name, no washing machine questions
    aid = start("My alarm is making too much noise")
    m = pg.inner_text('main'); c = cases()[-1]
    ok((c.get('fix') or {}).get('item') == 'Alarm', 'the thing is kept as Alarm (%s)' % (c.get('fix') or {}).get('item'))
    if pg.locator('form[data-f=what]').count():
        ok('What’s happening with the alarm?' in m and 'Won’t drain' not in m and 'Won’t spin' not in m, 'the questions are about the alarm, not draining or spinning')
        ok(pg.input_value('#f-item') == 'Alarm' and pg.locator('.chip[aria-pressed=true]').inner_text() == 'Something else', '"What is it?" says Alarm and "Something else" is the choice shown')
        ok('Sorted asks its own questions only for a washing machine' in m, 'it says honestly that it has no special questions for this thing')
    else:
        ok('Won’t drain' not in m, 'no washing machine questions')
    ok('Nothing is due on this case' not in m and 'No reference saved yet' not in m, 'no health line while the case is being set up')
    # 2 nothing named at all: an empty "What is it?", never a washing machine
    poke("var x=d.tasks.find(y=>y.data.id==='%s').data;x.fix.item=undefined;delete x.fix.item" % aid)
    pg.goto('https://sorted.test/?task=%s' % aid); wait(pg, 600)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    ok(pg.input_value('#f-item') == '' and 'Won’t drain' not in pg.inner_text('main'), 'with no thing named, "What is it?" is empty and no washing machine is assumed')
    pg.locator('form[data-f=what] button[type=submit]').click(); wait(pg, 300)
    ok('Say what it is.' in pg.inner_text('main'), 'it asks for the thing before carrying on')
    pg.fill('#f-item', 'Alarm'); pg.fill('#f-detail', 'Beeps every few minutes'); pg.locator('form[data-f=what] button[type=submit]').click(); wait(pg, 500)
    ok(cases()[-1]['fix']['item'] == 'Alarm' and cases()[-1]['fix']['step'] == 'who', 'with the thing named it moves on to who fixes it')
    wm = start("Washing machine stopped draining")
    ok('Won’t drain' in pg.inner_text('main') or cases()[-1]['fix'].get('item') == 'Washing machine', 'a washing machine still gets its own questions')
    # 3 one look for a choice; hover changes nothing on a phone
    pg.goto('https://sorted.test/?task=%s' % wm); wait(pg, 500)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    if pg.locator('form[data-f=what] .chip[data-k=fault]').count():
        pg.locator('form[data-f=what] .chip[data-k=fault]').first.click(); wait(pg, 300)
        on = pg.locator('.chip[aria-pressed=true]').evaluate_all("es=>es.map(e=>getComputedStyle(e).backgroundColor+'|'+getComputedStyle(e).color)")
        off = pg.locator('form[data-f=what] .chip[aria-pressed=false]').first.evaluate("e=>getComputedStyle(e).backgroundColor")
        ok(len(set(on)) == 1 and on[0].split('|')[1] == 'rgb(255, 255, 255)' and off != on[0].split('|')[0], 'every chosen chip has the same filled look; an unchosen one does not (%s)' % on)
    # 4 an unfinished case on Home says so
    pg.goto('https://sorted.test/'); wait(pg, 700)
    ok('Finish setting up this case' in pg.inner_text('main') and 'a few quick questions' not in pg.inner_text('main'), 'an unfinished case says "Finish setting up this case"')
    # 5 Home: Sort something new closed until asked; the discovery fold inside it; nothing repeated
    for t in ["Sky said an engineer would come next Friday, ref AB123", "Currys refund for order 445566 hasn't arrived"]: start(t)
    pg.goto('https://sorted.test/'); wait(pg, 700); m = pg.inner_text('main')
    ok(not pg.locator('#cap82-start').is_visible() and pg.locator('[data-a=compose]').is_visible(), 'returning Home: the six routes are closed, "+ Sort something new" shows')
    ok('What else can Sorted help you sort?' not in m and 'Things people use Sorted for' not in m and 'See all 32' not in m, 'no discovery card or strip repeated beneath the cases')
    ok(pg.locator('[data-a=compose]').get_attribute('aria-expanded') == 'false', 'the button says it is closed')
    pg.click('.home111-newbtn'); wait(pg, 700)
    ok(pg.locator('#cap82-start').is_visible() and pg.evaluate("document.activeElement&&document.activeElement.classList.contains('cap82-card')"), '+ New opens the routes and focuses the first')
    ok(pg.locator('details.cap95-explore').count() == 1 and pg.locator('#home111-new details.cap95-explore').count() == 1, 'the search and browse fold is inside Sort something new, once')
    pg.click('[data-a=ex-all]'); wait(pg, 600)
    ok(pg.evaluate("document.getElementById('cap95-explore').open"), '"See all 32 and search" opens it')
    pg.click('[data-a=home]'); wait(pg, 600)
    ok(not pg.locator('#cap82-start').is_visible(), 'Home again closes it')
    pg.click('[data-a=compose]'); wait(pg, 500)
    ok(pg.locator('#f-case').is_visible() and pg.locator('#cap82-start').is_visible(), '"+ Sort something new" opens the box with the routes above it')
    # 6 Help beside Account
    pg.goto('https://sorted.test/'); wait(pg, 600)
    ok([x.strip() for x in pg.locator('.bar .navq').all_inner_texts()] == ['Help', 'Account'], 'the top bar has Help and Account')
    pg.click('.bar [data-a=help]'); wait(pg, 700)
    ok(pg.evaluate("document.activeElement&&document.activeElement.id==='help-h'") and pg.locator('#help').is_visible(), 'Help lands on Help & About with focus on its heading')
    pg.set_viewport_size({'width': 320, 'height': 700}); pg.goto('https://sorted.test/'); wait(pg, 500)
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), 'the top bar fits at 320px')
    print('CHECKS', n[0]); b.close()
print('ERRORS', errs); print('FAILS', fails)
