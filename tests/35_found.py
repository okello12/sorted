# v73: "Came in" on Home lists replies and helper notes waiting in any case, and each row opens its case.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=350): pg.wait_for_timeout(ms)
def db(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))")
def poke(pg, js):
    pg.evaluate("(js)=>{var db=JSON.parse(localStorage.getItem('__mockdb'));(new Function('db',js))(db);localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", js)
def start(pg, text):
    pg.goto('https://sorted.test/'); wait(pg, 400)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
    pg.fill('#f-case', text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 450)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg)
    return sorted([x['data'] for x in db(pg)['tasks']], key=lambda x: x.get('created') or '')[-1]['id']
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 200); pg.click('[data-a=anon-start]'); wait(pg)
    a = start(pg, "Currys refund hasn't arrived, order 445566")
    c = start(pg, "British Gas engineer didn't come to fix the boiler")
    pg.goto('https://sorted.test/'); wait(pg, 500)
    ok(pg.locator('.found-strip').count() == 0, 'with nothing waiting, Home has no "Came in"')
    # 1 a reply in one case and a note in another
    poke(pg, "db.inbound_items.push({id:'r1',user_id:'x',task_id:'%s',from_domain:'currys.co.uk',subject:'Refund',body:'SECRET WORDS',received_at:new Date(Date.now()-3600e3).toISOString(),used_at:null});"
             "db.inbound_items.push({id:'r0',user_id:'x',task_id:null,subject:'old',body:'old',received_at:new Date().toISOString(),used_at:null});"
             "db.case_notes.push({id:'n1',task_id:'%s',author:'Mum',body:'NOTE WORDS',created_at:new Date().toISOString()})" % (a, c))
    pg.goto('https://sorted.test/'); wait(pg, 600)
    fs = pg.inner_text('.found-strip') if pg.locator('.found-strip').count() else ''
    ok('2 things came in for you to look at' in fs, 'Home says two things came in')
    ok('A reply came in from currys.co.uk' in fs and 'Mum added a note' in fs, 'a reply and a note, each with where it came from')
    ok('SECRET WORDS' not in fs and 'NOTE WORDS' not in fs, 'the words stay in the case')
    ok(fs.index('Mum added a note') < fs.index('A reply came in'), 'newest first')
    ok('Nothing joins a case until you add it there.' in fs, 'it says nothing is added on its own')
    # 2 a row opens its case, which shows the reply as a proposal; dealing with it clears the row
    pg.locator('.found-row', has_text='currys.co.uk').click(); wait(pg, 500)
    ok(pg.locator('.cm-card').count() == 1, 'the row opens the case with the reply waiting')
    pg.click('[data-a=cm-drop]'); wait(pg)
    pg.click('[data-a=home]'); wait(pg, 400)
    fs = pg.inner_text('.found-strip') if pg.locator('.found-strip').count() else ''
    ok('Something came in for you to look at' in fs and 'currys.co.uk' not in fs, 'once handled, it goes from Home straight away')
    pg.locator('.found-row').first.click(); wait(pg, 500)
    pg.click('[data-a=note-keep]'); wait(pg)
    pg.click('[data-a=home]'); wait(pg, 400)
    ok(pg.locator('.found-strip').count() == 0, 'keeping the note clears the last one')
    pg.screenshot(path='tests/out/35_found.png')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
