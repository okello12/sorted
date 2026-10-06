# v104: show your move to someone you live with. Nothing is shared until you tap; the link shows the move's steps and,
# for each case in it, its name and one status line, never your other cases; it updates when a case in the move changes;
# the page is read-only; switching it off stops it; step records are codes only; opening the link is counted, not who.
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
def dbj(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
def rows(pg): return [x['data'] for x in dbj(pg).get('tasks', [])]
def moms(pg): return [x for x in rows(pg) if x.get('kind') == 'moment']
def cases(pg): return [x for x in rows(pg) if x.get('kind') != 'moment']
def shares(pg): return dbj(pg).get('shares', [])
def events(pg): return dbj(pg).get('pilot_events', [])
def item(pg, label): return pg.locator('.cap99-item', has_text=label).first
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    # a private case that is not part of the move
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg)
    if not pg.locator('#f-case').count() and pg.locator('[data-a=compose]').count(): pg.locator('[data-a=compose]').first.click(); wait(pg)
    pg.fill('#f-case', 'HMRC says I owe £450 by 12 December'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    ok(len(cases(pg)) == 1, 'a private case exists')
    # a move with a case in it, its promise not confirmed yet
    pg.goto('https://sorted.test/'); wait(pg, 600)
    pg.locator('[data-a=mom-start]').first.evaluate('e=>e.click()'); wait(pg, 600)
    if pg.locator('[data-a=mom-new]').count() and not pg.locator('#mv-date').count(): pg.locator('[data-a=mom-new]').first.evaluate('e=>e.click()'); wait(pg)
    pg.fill('#mv-date', (datetime.date.today() + datetime.timedelta(days=20)).isoformat()); pg.click('label.chip:has(input[name=mv-tenure][value=rent])')
    pg.click('form[data-f=mom] button[type=submit]'); wait(pg)
    mid = moms(pg)[0]['id']
    item(pg, 'Broadband at the new place').locator('[data-a=mom-case]').click(); wait(pg)
    pg.fill('#gi-what', 'Virgin will install on Tuesday ref V123'); pg.click('.cap103-said button[type=submit]'); wait(pg, 700)
    bbid = [c for c in cases(pg) if 'V123' in (c.get('said') or '')][0]['id']
    pg.click('[data-a=mom-open]'); wait(pg)
    # 1 nothing is shared until you tap
    m = pg.inner_text('main')
    ok(pg.locator('details.cap104-share').count() == 1 and 'Show this move to someone you live with' in m and 'Only you can see it' in m and shares(pg) == [], 'the move offers "Show this move to someone you live with"; nothing shared yet')
    pg.click('details.cap104-share summary'); wait(pg, 200)
    t = pg.inner_text('details.cap104-share')
    ok('can’t change anything' in t and 'Not your other cases' in t and 'reference' in t, 'it says what they will and won’t see before you share')
    pg.click('[data-a=mom-share]'); wait(pg, 600)
    sh = shares(pg)
    ok(len(sh) == 1 and sh[0]['task_id'] == mid and len(sh[0]['token']) >= 24 and moms(pg)[0].get('shareToken') == sh[0]['token'], 'one link for the move itself')
    card = sh[0]['card'] if sh else {}; cj = json.dumps(card, ensure_ascii=False)
    ok(card.get('k') == 'moment' and 'Give notice to your landlord' in cj and 'Broadband at the new place' in cj, 'the card has the move’s steps and its case')
    ok('HMRC' not in cj and '450' not in cj and 'V123' not in json.dumps([g for g in card.get('g', []) if g[1] not in ('needs', 'waiting')]), 'the private case is never in it')
    ok(any(e['name'] == 'moment_item' and e['props'].get('item') == 'share' and e['props'].get('choice') == 'link' and set(e['props']) <= {'type', 'item', 'choice', 'anon'} for e in events(pg)), 'sharing is counted as a code')
    ok(pg.locator('[data-a=mom-wa]').count() == 1 and pg.locator('[data-a=mom-unshare]').count() == 1 and 'Shared' in pg.inner_text('details.cap104-share summary'), 'then WhatsApp, switch off, and "Shared"')
    tok = sh[0]['token']
    # 2 the shared page: read-only, the move only
    v = ctx.new_page(); v.on('pageerror', lambda e: errs.append(str(e)))
    v.goto('https://sorted.test/?share=%s' % tok); wait(v, 800)
    vm = v.inner_text('main')
    ok('Someone shared their move' in vm and 'Needs doing' in vm and 'Needs you' not in vm and 'Moving home' in vm and 'Broadband at the new place' in vm and 'Give notice to your landlord' in vm, 'the link opens the move')
    ok('HMRC' not in vm and v.locator('main [data-a^=mom-]').count() == 0 and v.locator('main form').count() == 0, 'no other cases, no buttons to change it')
    ok(tok in json.loads(v.evaluate("localStorage.getItem('__seen')") or '[]'), 'opening it is counted (the token, never who)')
    ok(v.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'the shared page fits the phone')
    # 3 a change inside a case in the move updates the link
    pg.goto('https://sorted.test/?task=%s' % bbid); wait(pg, 700)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 700)
    v.reload(); wait(v, 800)
    ok('Waiting for Virgin' in v.inner_text('main'), 'confirming the promise in the case shows "Waiting for Virgin" on the shared move')
    # 4 a step marked done in the move updates it too
    pg.click('[data-a=mom-open]'); wait(pg)
    item(pg, 'Give notice to your landlord').locator('[data-a=mom-done]').click(); wait(pg, 600)
    v.reload(); wait(v, 800)
    ok('Give notice to your landlord' in (v.inner_text('.cap99-done') if v.locator('.cap99-done').count() else ''), 'a step done shows under Done')
    # 5 switch it off
    pg.click('details.cap104-share summary') if not pg.evaluate("document.querySelector('details.cap104-share').open") else None
    pg.click('[data-a=mom-unshare]'); wait(pg, 600)
    ok(shares(pg) == [] and not moms(pg)[0].get('shareToken') and 'Only you can see it' in pg.inner_text('main'), 'switching it off removes the link')
    v.reload(); wait(v, 800)
    ok('doesn’t open' in v.inner_text('main') and 'Broadband' not in v.inner_text('main'), 'the old link shows nothing')
    ok(any(e['props'].get('item') == 'share' and e['props'].get('choice') == 'off' for e in events(pg) if e['name'] == 'moment_item'), 'switching off is counted as a code')
    # 6 sharing again, then deleting the move (the database removes its link with it: shares.task_id cascades)
    if not pg.evaluate("document.querySelector('details.cap104-share').open"): pg.click('details.cap104-share summary'); wait(pg, 200)
    pg.click('[data-a=mom-share]'); wait(pg, 600)
    ok(len(shares(pg)) == 1, 'sharing again makes a new link')
    pg.click('[data-a=mom-del]'); wait(pg, 200); pg.click('[data-a=mom-del]'); wait(pg, 600)
    ok(moms(pg) == [] and len(cases(pg)) == 2, 'deleting the move keeps the cases')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
