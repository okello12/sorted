# v103: Moving home, reworked. Your own steps are compact rows; things to arrange with someone say "Arrange with someone"
# and "I've contacted them", which asks "What did they say?" with the topic already known; a case starts only with a date,
# a reference or a promise, otherwise the item stays "In touch" with their words kept; Expected and Worth considering
# (optional, paid post redirection, GP "If needed"); the energy bill split; tracked cases carry the move; "← Home".
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
def rows(pg): return [x['data'] for x in (pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {'tasks': []})['tasks']]
def moms(pg): return [x for x in rows(pg) if x.get('kind') == 'moment']
def cases(pg): return [x for x in rows(pg) if x.get('kind') != 'moment']
def events(pg): return (pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}).get('pilot_events', [])
def grp(pg, g): return pg.inner_text('.cap99-%s' % g) if pg.locator('.cap99-%s' % g).count() else ''
def item(pg, label): return pg.locator('.cap99-item', has_text=label).first
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    pg.locator('[data-a=mom-start]').first.evaluate('e=>e.click()'); wait(pg, 600)
    move = (datetime.date.today() + datetime.timedelta(days=20)).isoformat()
    pg.fill('#mv-date', move); pg.click('label.chip:has(input[name=mv-tenure][value=rent])')
    pg.click('form[data-f=mom] button[type=submit]'); wait(pg)
    ok(len(moms(pg)) == 1, 'a move is saved')
    main = pg.inner_text('main'); top = pg.inner_text('.bar') if pg.locator('.bar').count() else pg.inner_text('body')
    # 1 wording and weights
    ok('owe you this' not in main and 'All cases' not in pg.inner_text('body') and '← Home' in pg.inner_text('body'), 'no "Someone else will owe you this", and the way back says "← Home"')
    arr = pg.locator('.cap103-arr'); own = pg.locator('.cap103-own')
    ok(arr.count() >= 4 and all('I’ve contacted them' in arr.nth(i).inner_text() for i in range(arr.count())), 'things to arrange are cards with "I’ve contacted them"')
    ok('arrange with someone' in item(pg, 'Broadband at the new place').inner_text().lower(), 'broadband says "Arrange with someone"')
    ok(own.count() >= 4 and pg.locator('.cap103-own .btn').count() == 0 and 'Not relevant' in own.first.inner_text(), 'your own steps are compact rows with links, not big buttons')
    ok(pg.locator('[data-a=mom-case]', has_text='Start a case').count() == 0, 'no "Start a case" before anything concrete')
    # 2 Expected and Worth considering
    ok('Expected' in grp(pg, 'coming') and 'Post redirection' not in grp(pg, 'coming'), 'Coming up is now Expected, without the optional things')
    c = grp(pg, 'consider')
    ok('Worth considering' in c and 'Post redirection' in c and 'optional' in c.lower() and 'Royal Mail charges for it.' in c and 'Furniture' in c and 'Register with a GP' in c and 'If needed' in c, 'Worth considering: post redirection (optional, paid), furniture, a GP if needed')
    # 3 the energy bill is split: your readings, then telling the supplier
    ok('Take final meter readings' in pg.inner_text('.cap103-own >> nth=0') or any('Take final meter readings' in own.nth(i).inner_text() for i in range(own.count())), 'final meter readings are yours to do')
    ok('Tell your energy supplier you’re moving' in item(pg, 'Tell your energy supplier').inner_text() and 'arrange with someone' in item(pg, 'Tell your energy supplier').inner_text().lower() and 'Final energy bill' not in main, 'telling the supplier is arranged; the bill is tracked only once they say when')
    # 4 broadband: the topic is known, so it asks only what they said
    n0 = len(cases(pg))
    item(pg, 'Broadband at the new place').locator('[data-a=mom-case]').click(); wait(pg)
    m = pg.inner_text('main')
    ok('What has your broadband provider told you?' in m and 'What is this about' not in m and 'Who is installing' not in m and len(cases(pg)) == n0, 'broadband asks "What has your broadband provider told you?", creates nothing yet')
    pg.fill('#gi-what', 'Virgin will install on Tuesday ref V123'); pg.click('.cap103-said button[type=submit]'); wait(pg, 700)
    cs = cases(pg); bb = [x for x in cs if 'V123' in (x.get('said') or '')]
    ok(len(cs) == n0 + 1 and bb and bb[0].get('momentId') == moms(pg)[0]['id'] and moms(pg)[0]['items']['broadband']['caseId'] == bb[0]['id'], 'it becomes a case in the move, linked both ways')
    m = pg.inner_text('main')
    ok(pg.locator('form[data-f=baseline]').count() == 0 and 'What were you planning' not in m and 'Who is it' not in m and 'What is it about' not in m, 'no questions about who, what service or what it concerns')
    ok(pg.locator('[data-a=sug-yes]').count() == 1 and 'Virgin' in m and 'V123' in m and 'Part of Moving home' in m, 'the promise is proposed with Virgin and the ref, and the case says it is part of the move')
    pg.click('[data-a=sug-yes]'); wait(pg)
    ok(bb and [x for x in cases(pg) if x['id'] == bb[0]['id']][0]['promises'][-1]['status'] == 'open', 'confirming it makes a normal open promise')
    pg.click('[data-a=mom-open]'); wait(pg)
    ok(pg.locator('.cap99-waiting .cap103-big').count() == 1 and 'tracked case' in grp(pg, 'waiting').lower(), 'in the move it shows as a prominent tracked case under Waiting')
    # 5 nothing concrete yet: kept as "In touch", with their words, no case
    n1 = len(cases(pg))
    item(pg, 'Book removals').locator('[data-a=mom-case]').click(); wait(pg)
    ok('What has the removal company told you?' in pg.inner_text('main'), 'removals asks what the removal company said')
    pg.fill('#gi-what', 'I rang and they’re checking availability'); pg.click('.cap103-said button[type=submit]'); wait(pg, 500)
    ok('Add who it is' in pg.inner_text('main') and len(cases(pg)) == n1, 'with no name anywhere it asks who, and saves nothing')
    pg.fill('#gi-who', 'Pickfords'); pg.click('.cap103-said button[type=submit]'); wait(pg, 600)
    st = moms(pg)[0]['items'].get('removals', {})
    ok(len(cases(pg)) == n1 and st.get('st') == 'contacted' and st.get('who') == 'Pickfords' and 'checking availability' in st.get('said', ''), 'no date, ref or promise: no case; the item keeps who and what they said')
    it = item(pg, 'Book removals').inner_text()
    ok('in touch with pickfords' in it.lower() and 'checking availability' in it and 'They’ve told me more' in it, 'it shows "In touch with Pickfords", their words, and "They’ve told me more"')
    item(pg, 'Book removals').locator('[data-a=mom-case]').click(); wait(pg)
    ok(pg.input_value('#gi-who') == 'Pickfords' and 'checking availability' in pg.input_value('#gi-what'), 'the form comes back with what was already said')
    day = (datetime.date.today() + datetime.timedelta(days=20)).strftime('%-d %B')
    pg.fill('#gi-what', 'Pickfords will arrive at 8am on %s' % day); pg.click('.cap103-said button[type=submit]'); wait(pg, 700)
    rm = [x for x in cases(pg) if 'Pickfords' in (x.get('said') or '')]
    ok(len(cases(pg)) == n1 + 1 and rm and rm[0].get('momentId') == moms(pg)[0]['id'] and pg.locator('[data-a=sug-yes]').count() == 1, 'once they give a date it becomes a case, with the promise to confirm')
    ok(any(e['name'] == 'moment_item' and e['props'].get('choice') == 'contacted' and set(e['props']) <= {'type', 'item', 'choice', 'anon'} for e in events(pg)), '"In touch" is counted as a code, never their words')
    # 6 Royal Mail is already known for post redirection
    pg.click('[data-a=mom-open]'); wait(pg)
    item(pg, 'Post redirection').locator('[data-a=mom-case]').click(); wait(pg)
    ok(pg.input_value('#gi-who') == 'Royal Mail' and 'What has Royal Mail told you?' in pg.inner_text('main'), 'post redirection already knows it is Royal Mail')
    pg.click('.cap103-said [data-a=mom-panel]'); wait(pg)
    ok(pg.locator('.cap103-said').count() == 0, 'Cancel closes it')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'nothing scrolls sideways')
    pg.locator('.bar [data-a=home], [data-a=home]').first.click(); wait(pg, 600)
    ok(pg.locator('.cap99-row').count() == 1, '"← Home" goes to Home, with the move on it')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
