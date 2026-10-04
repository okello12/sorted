# v100: hardening. The installed app's Home button really goes Home from anywhere and clears half-done state; Moving
# home is reachable before the first case and never duplicated by accident; one case belongs to one move; unfinished
# flows (refresh mid-way, Home mid-way, switching start choice, backgrounding, a failed save, repeated taps) never
# create, lose or duplicate anything.
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
def rows(pg): return [x['data'] for x in (pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')||'{}')") or {}).get('tasks', [])]
def moms(pg): return [x for x in rows(pg) if x.get('kind') == 'moment']
def cases(pg): return [x for x in rows(pg) if x.get('kind') != 'moment']
def home(pg): pg.locator('.tab129 [data-a=go-home]').click(); wait(pg, 500)
def at_home(pg): return pg.locator('main.home44').count() == 1 and pg.locator('form[data-f=gi], #moveform, form[data-f=mom], .fr-card, form[data-f=call]').count() == 0
def chooser(pg): return pg.locator('#cap82-start:visible')
def baseline(pg):
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
def start_other(pg, text):
    home(pg)
    if chooser(pg).count() and chooser(pg).locator('[data-cap82=other]:visible').count(): chooser(pg).locator('[data-cap82=other]:visible').first.click(); wait(pg)
    elif pg.locator('[data-a=compose]').count(): pg.locator('[data-a=compose]').first.click(); wait(pg)
    pg.fill('#f-case', text)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.add_init_script("Object.defineProperty(navigator,'standalone',{configurable:true,get:()=>true})")
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url and 'manifest' not in r.request.url else r.fulfill(body='{}' if 'manifest' in r.request.url else ''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    # 1 Moving home before any case, straight to the questions
    pg.goto('https://sorted.test/'); wait(pg, 700)
    ok(cases(pg) == [] and pg.locator('[data-a=mom-start]:visible').count() == 1 and 'Planning something bigger?' in pg.inner_text('main'), 'a brand-new user sees "Planning something bigger? Moving home"')
    pg.click('[data-a=mom-start]'); wait(pg)
    ok(pg.locator('form[data-f=mom]').count() == 1, 'it opens the move questions directly')
    # 2 refresh half-way through Moving home: nothing saved
    pg.fill('#mv-date', (datetime.date.today() + datetime.timedelta(days=30)).isoformat()); pg.reload(); wait(pg, 700)
    ok(moms(pg) == [], 'closing or refreshing before "Show my move" saves nothing')
    # 3 double tap "Show my move": one move; the same date again opens it
    home(pg); pg.click('[data-a=mom-start]'); wait(pg)
    d30 = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
    pg.fill('#mv-date', d30); pg.locator('form[data-f=mom] button[type=submit]').evaluate('(b)=>{b.click();b.click()}'); wait(pg, 600)
    ok(len(moms(pg)) == 1, 'a double tap makes one move')
    home(pg)
    ok(pg.locator('[data-a=mom-start]').count() == 0 and pg.locator('.cap99-row').count() == 1, 'with a move, Home shows the move instead of the entry')
    pg.click('.cap99-row'); wait(pg); mid = moms(pg)[0]['id']
    # Home from inside the move
    home(pg)
    ok(at_home(pg) and pg.evaluate('location.hash') == '#start', 'Home from Moving home goes Home')
    pg.locator('[data-a=ex-moment][data-v=moving]').first.click(); wait(pg, 600)
    pg.locator('#moment-moving [data-a=mom-new]').click(); wait(pg); pg.fill('#mv-date', d30); pg.click('form[data-f=mom] button[type=submit]'); wait(pg, 500)
    ok(len(moms(pg)) == 1 and 'You already have a move on that day' in pg.inner_text('#toast'), 'the same date again opens the move you have')
    # 4 text typed, then Home: nothing created, no stale start
    start_other(pg, 'Currys said my refund would arrive by Friday')
    home(pg)
    ok(cases(pg) == [] and at_home(pg) and pg.evaluate("sessionStorage.getItem('sorted.cap82')") is None, 'typed text then Home: nothing created, nothing half-done left')
    # 5 refresh half-way through a start: nothing created
    start_other(pg, 'British Gas engineer did not come'); pg.reload(); wait(pg, 700)
    ok(cases(pg) == [], 'refresh before Start creates nothing')
    # 6 switching start choice half-way: the new one wins
    home(pg); chooser(pg).locator('[data-cap82=fix]').first.click(); wait(pg)
    ok('What’s broken?' in pg.inner_text('main'), 'broken: its own question')
    home(pg); chooser(pg).locator('[data-cap82=call]').first.click(); wait(pg)
    ok('Who do you need to call?' in pg.inner_text('main') and pg.locator('#gi-who').count() == 1 and 'What’s broken?' not in pg.inner_text('main'), 'then call: the call question, nothing left from broken')
    home(pg); chooser(pg).locator('[data-cap82=other]').first.click(); wait(pg)
    ok('What’s broken?' not in pg.inner_text('main') and 'Who do you need to call?' not in pg.inner_text('main') and pg.locator('#f-case').count() == 1, 'then something else: the plain box, no leftover heading')
    # 7 repeated taps on Start: one case
    pg.fill('#f-case', 'Currys said my refund of £89 would arrive by Friday, order 445566')
    pg.locator('form[data-f=case] button[type=submit]').last.evaluate('(b)=>{b.click();b.click();b.click()}'); wait(pg, 500); baseline(pg)
    ok(len(cases(pg)) == 1, 'three quick taps on Start make one case')
    cid = cases(pg)[0]['id']
    # 8 Home from a case, after a missed promise, after finishing
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 150)
    home(pg); ok(at_home(pg) and 'Currys' in pg.inner_text('main'), 'Home from a case shows Home with the case')
    pg.evaluate("(id)=>{var d=JSON.parse(localStorage.getItem('__mockdb'));var x=d.tasks.find(y=>y.data.id===id).data;delete x.frNew;x.promises.forEach(q=>{if(q.status==='open'){q.dueAt=new Date(Date.now()-864e5).toISOString();q.dueEnd=null}});localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", cid)
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700); pg.locator('[data-a=missed]').first.click(); wait(pg)
    ok(pg.locator('form[data-f=call]').count() == 1, 'missed: the chase form is open')
    home(pg); ok(at_home(pg), 'Home from the chase form goes Home')
    # Back and Forward stay history-based and the page stays usable
    pg.go_back(); wait(pg, 400); pg.go_forward(); wait(pg, 400); home(pg)
    ok(at_home(pg) and pg.locator('main').count() == 1, 'after Back and Forward, Home still goes Home')
    # 9 a case in a move belongs to that move only
    pg.goto('https://sorted.test/'); wait(pg, 600); pg.click('.cap99-row'); wait(pg)
    pg.click('[data-a=mom-panel][data-p=link]'); wait(pg); pg.locator('[data-a=mom-link][data-id="%s"]' % cid).click(); wait(pg)
    home(pg); pg.locator('[data-a=ex-moment][data-v=moving]').first.click(); wait(pg, 600); pg.locator('#moment-moving [data-a=mom-new]').click(); wait(pg)
    pg.fill('#mv-date', (datetime.date.today() + datetime.timedelta(days=200)).isoformat()); pg.click('form[data-f=mom] button[type=submit]'); wait(pg, 500)
    pg.click('[data-a=mom-panel][data-p=link]'); wait(pg)
    ok(pg.locator('[data-a=mom-link][data-id="%s"]' % cid).count() == 1, 'the second move can take the case')
    pg.locator('[data-a=mom-link][data-id="%s"]' % cid).click(); wait(pg)
    ok('Tap it again to move it here' in pg.inner_text('main'), 'v105: it asks before taking it from the other move')
    pg.locator('[data-a=mom-link][data-id="%s"]' % cid).click(); wait(pg)
    c = [x for x in cases(pg) if x['id'] == cid][0]; m2 = [x for x in moms(pg) if x['id'] != mid][0]
    ok(c['momentId'] == m2['id'], 'and then it belongs to the second move only')
    pg.goto('https://sorted.test/'); wait(pg, 600); pg.locator('.cap99-row').filter(has_text='In 30 days').click(); wait(pg)
    ok('Currys' not in pg.inner_text('main'), 'the first move no longer shows it')
    # 10 a failed save is kept and retried
    home(pg); pg.evaluate("localStorage.setItem('__failWrites','1')")
    start_other(pg, 'Argos said my refund of £25 would arrive by Friday'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 500); baseline(pg)
    ok(not any('Argos' in (x.get('title') or '') + (x.get('said') or '') for x in cases(pg)), 'while saving fails, nothing reaches the database')
    ok(pg.evaluate("JSON.stringify(localStorage)").count('Argos') >= 1, 'but the case is kept on the phone')
    pg.evaluate("localStorage.removeItem('__failWrites');window.dispatchEvent(new Event('online'))"); wait(pg, 800)
    ok(sum(1 for x in cases(pg) if 'Argos' in (x.get('title') or '') + (x.get('said') or '')) == 1, 'when the connection is back it is saved once')
    # 11 the installed app goes to the background and comes back
    pg.evaluate("document.dispatchEvent(new Event('visibilitychange'));window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))"); wait(pg, 400)
    ok(pg.locator('main').count() == 1 and len(cases(pg)) == 2, 'back from the background: nothing lost or duplicated')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'nothing scrolls sideways')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
