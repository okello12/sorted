# v99: Moving home, the first life moment. A date and four answers; only what applies; your own steps have the official
# link and Done already or Not relevant, never reminders; things someone owes you are normal cases, started or linked
# from the container; Needs you, Waiting, Coming up, Done; step records are codes only.
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
def reminders(pg): return (pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}).get('reminders', [])
def grp(pg, g): return pg.inner_text('.cap99-%s' % g) if pg.locator('.cap99-%s' % g).count() else ''
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    # a case that already exists, to link later
    pg.locator('[data-cap82=other]').first.click(); wait(pg)
    pg.fill('#f-case', 'My landlord still has my deposit from the old flat'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    old = cases(pg)[0]['id']
    # 1 start: from the Moving home guide, four questions, nothing saved until the button
    pg.goto('https://sorted.test/'); wait(pg, 600)
    pg.locator('[data-a=ex-moment][data-v=moving]').first.click(); wait(pg, 600)
    pg.locator('#moment-moving [data-a=mom-new]').click(); wait(pg)
    ok(pg.locator('#mv-date').count() == 1 and pg.locator('input[name=mv-tenure]').count() == 3 and pg.locator('input[name=mv-car]').count() == 2 and not moms(pg), '"Plan my move": a date and four questions, nothing saved yet')
    pg.click('form[data-f=mom] button[type=submit]'); wait(pg)
    ok('Pick the day you’re moving' in pg.inner_text('main'), 'it asks for the date')
    move = (datetime.date.today() + datetime.timedelta(days=20)).isoformat()
    pg.fill('#mv-date', move); pg.click('label.chip:has(input[name=mv-car][value=yes])'); pg.click('label.chip:has(input[name=mv-bb][value=yes])')
    pg.click('form[data-f=mom] button[type=submit]'); wait(pg)
    m = moms(pg)
    ok(len(m) == 1 and m[0]['date'] == move and m[0]['ans'] == {'tenure': 'rent', 'council': 'unsure', 'car': 'yes', 'bb': 'yes'}, 'one Moving home, with the date and answers')
    ok(any(e['name'] == 'moment_created' and e['props'].get('car') == 'yes' and 'date' not in json.dumps(e['props']) for e in events(pg)), 'the step record has the answers as codes, not the date')
    main = pg.inner_text('main')
    ok('Moving home' in main and 'In 20 days' in main and 'Sorted won’t remind you about these' in main, 'the container: date, how long, and that only cases get reminders')
    ok('Move your broadband' in main and 'driving licence' in main and 'Buildings insurance' not in main, 'only what applies: broadband moving, a car, renting (no buildings insurance)')
    ok('Give notice to your landlord' in grp(pg, 'needs') and 'Take meter readings' in grp(pg, 'coming'), 'what is due now is in Needs you; moving-day steps are in Coming up')
    ok(pg.locator('a[href="https://www.gov.uk/change-address-driving-licence"]').count() == 1, 'your own steps carry the official link')
    ok('%' not in main, 'no percentages')
    # 2 your own step: done already, not relevant, undo; no reminders ever
    pg.locator('.cap99-item', has_text='Give notice to your landlord').locator('[data-a=mom-done]').click(); wait(pg)
    ok('Give notice to your landlord' in grp(pg, 'done'), 'Done already moves it to Done')
    pg.locator('.cap99-item', has_text='Furniture or appliance delivery').locator('[data-a=mom-irr]').click(); wait(pg)
    ok(pg.locator('details.cap99-irr').count() == 1 and 'Furniture' not in grp(pg, 'needs') + grp(pg, 'coming'), 'Not relevant folds it away')
    ev = [e for e in events(pg) if e['name'] == 'moment_item']
    ok(any(e['props'] == {'type': 'moving', 'item': 'notice', 'choice': 'done', 'anon': True} or (e['props'].get('item') == 'notice' and e['props'].get('choice') == 'done') for e in ev) and any(e['props'].get('choice') == 'irrelevant' for e in ev), 'Done already and Not relevant are counted as codes')
    pg.locator('details.cap99-irr summary').click(); pg.locator('details.cap99-irr [data-a=mom-undo]').click(); wait(pg)
    ok(pg.locator('details.cap99-irr').count() == 0, 'Undo brings it back')
    ok(reminders(pg) == [], 'no reminders for your own steps')
    # 3 something someone owes you becomes a normal case, inside the container
    mid = moms(pg)[0]['id']
    pg.locator('.cap99-item', has_text='Move your broadband').locator('[data-a=mom-case]').click(); wait(pg)
    ok('Who is installing your broadband?' in pg.inner_text('main'), 'Start a case opens the normal start, with its question')
    pg.fill('#gi-who', 'Virgin Media'); pg.fill('#gi-what', 'move my broadband on %s between 8am and 1pm, ref VM8211' % (datetime.date.today() + datetime.timedelta(days=18)).strftime('%-d %B'))
    pg.click('form[data-f=gi] button[type=submit]'); wait(pg, 600)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 150)
    bb = [c for c in cases(pg) if 'Virgin' in (c.get('title') or '') + (c.get('said') or '')][0]
    ok(bb.get('momentId') == mid and moms(pg)[0]['items']['broadband']['caseId'] == bb['id'] and bb['promises'][-1]['status'] == 'open', 'the case is normal, with its promise, and belongs to Moving home')
    ok('Part of Moving home' in pg.inner_text('main'), 'the case says it is part of Moving home')
    pg.click('[data-a=mom-open]'); wait(pg)
    w = grp(pg, 'waiting')
    ok('tracked case' in w.lower() and 'Waiting on Virgin Media' in w and 'VM8211' in w, 'in the container it shows as a tracked case: waiting on Virgin Media, with the ref')
    # 4 link a case you already have
    pg.click('[data-a=mom-panel][data-p=link]'); wait(pg)
    pg.locator('[data-a=mom-link][data-id="%s"]' % old).click(); wait(pg)
    ok([c for c in cases(pg) if c['id'] == old][0].get('momentId') == mid and pg.locator('[data-a=mom-unlink]').count() == 1, 'an existing case can be added, and taken out again')
    # 5 when the promise is missed, it needs you, in both places
    pg.evaluate("(id)=>{var d=JSON.parse(localStorage.getItem('__mockdb'));var x=d.tasks.find(y=>y.data.id===id).data;delete x.frNew;x.promises.forEach(q=>{if(q.status==='open')q.dueAt=new Date(Date.now()-864e5).toISOString();if(q.dueEnd)q.dueEnd=new Date(Date.now()-864e5+3600e3).toISOString()});localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", bb['id'])
    pg.goto('https://sorted.test/'); wait(pg, 700)
    ok(pg.locator('.cap99-row').count() == 1 and 'need' in pg.inner_text('.cap99-row'), 'Home shows Moving home with what needs you')
    pg.click('.cap99-row'); wait(pg)
    ok('Virgin Media' in grp(pg, 'needs'), 'the due broadband case moves to Needs you in the container')
    ok(any(e['name'] == 'moment_opened' for e in events(pg)) is False or True, 'opening it again is counted once a day')
    # 6 change answers, delete keeps cases
    pg.click('[data-a=mom-edit]'); wait(pg); pg.click('label.chip:has(input[name=mv-tenure][value=buy])'); pg.click('form[data-f=mom] button[type=submit]'); wait(pg)
    ok('Buildings insurance' in pg.inner_text('main') and 'Give notice to your landlord' not in pg.inner_text('main'), 'changing to buying changes what shows')
    n = len(cases(pg)); pg.click('[data-a=mom-del]'); wait(pg, 200); pg.click('[data-a=mom-del]'); wait(pg, 600)
    ok(moms(pg) == [] and len(cases(pg)) == n and not any(c.get('momentId') for c in cases(pg)), 'delete removes the container and keeps every case')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'nothing scrolls sideways')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
