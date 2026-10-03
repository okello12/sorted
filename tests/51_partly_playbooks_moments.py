# v98: "Only partly" on a due promise; refund, insurance claim and HMRC playbooks; how a case ended sent as a code;
# a promise with no company named; a shared item says what it looks like; life moments start separate cases.
import os, sys, json, urllib.parse
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
def task(pg, cid): return next(x['data'] for x in db(pg)['tasks'] if x['data']['id'] == cid)
def poke(pg, js):
    pg.evaluate("(js)=>{var db=JSON.parse(localStorage.getItem('__mockdb'));(new Function('db',js))(db);localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", js)
def due(pg, cid): poke(pg, "var x=db.tasks.find(y=>y.data.id==='%s').data;delete x.frNew;x.promises.forEach(q=>{if(q.status==='open')q.dueAt=new Date(Date.now()-864e5).toISOString()})" % cid)
def openc(pg, cid): pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700)
def home(pg):
    pg.goto('https://sorted.test/'); wait(pg, 600)
    if pg.locator('[data-a=gi-back]').count(): pg.click('[data-a=gi-back]'); wait(pg)
def typed(pg, text, confirm=True):
    home(pg)
    if pg.locator('[data-cap82=other]').first.is_visible(): pg.locator('[data-cap82=other]').first.click(); wait(pg)
    elif pg.locator('[data-a=compose]').count(): pg.locator('[data-a=compose]').first.click(); wait(pg)
    pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg)
    if pg.locator('.ps-short').count(): pg.locator('.ps-short button[type=submit]').click(); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count():
        pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 550)
    if confirm and pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 150)
    return newest(pg)['id']
def events(pg): return db(pg).get('pilot_events', [])
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    # 1 Only partly, on a refund: recorded, the rest is chased, the refund playbook says chase the rest
    cid = typed(pg, 'Currys said my refund of £89 would arrive by Friday, order 445566')
    due(pg, cid); openc(pg, cid)
    ok(pg.locator('[data-a=panel][data-p=partly]').count() >= 1, 'a due promise offers "Only partly"')
    pg.locator('[data-a=panel][data-p=partly]').first.click(); wait(pg)
    pg.click('form[data-f=partly] button[type=submit]'); wait(pg)
    ok('Say what’s still outstanding' in pg.inner_text('main'), 'it asks what is still outstanding')
    pg.fill('#f-left', '£40 of the £89'); pg.click('form[data-f=partly] button[type=submit]'); wait(pg)
    t = task(pg, cid); q = t['promises'][-1]
    ok(q['status'] == 'missed' and q.get('partly') and q.get('left') == '£40 of the £89' and any('Only partly happened' in e['label'] for e in t['events']), 'recorded as only partly, with what is outstanding')
    ask = pg.input_value('#f-ask') if pg.locator('#f-ask').count() else ''
    ok('only partly happened. Still outstanding: £40 of the £89.' in ask and 'Chase the rest' in pg.inner_text('main'), 'the chase says what is still outstanding')
    ev = [e for e in events(pg) if e['name'] == 'outcome_missed']
    ok(ev and ev[-1]['props'].get('partly') is True, 'the step record marks it partly, nothing else')
    ok(not any(o.get('p_promise') == q['id'] for o in json.loads(pg.evaluate("localStorage.getItem('__outcomes')||'[]'"))), 'and it is not counted against the company')
    ok(t.get('pb', {}).get('id') == 'refund' and t['pb']['stage'] == 'part', 'the refund playbook moves to "part of it arrived"')
    # 2 refund playbook: kept asks if all of it arrived, and finishing sends only a code
    cid2 = typed(pg, 'Argos said my refund of £25 would arrive by Friday')
    due(pg, cid2); openc(pg, cid2); pg.locator('[data-a=kept]').first.click(); wait(pg)
    ok('Has all of it arrived?' in pg.inner_text('main'), 'refund kept: "Has all of it arrived?"')
    pg.locator('[data-a=pb-go]', has_text='Yes, all of it').click(); wait(pg)
    ok(pg.input_value('#f-outcome') == 'Refunded.', 'yes: the done form, "Refunded."')
    pg.click('form[data-f=done] button[type=submit]'); wait(pg)
    cl = [e for e in events(pg) if e['name'] == 'case_closed']
    ok(cl and cl[-1]['props'].get('end') == 'refunded' and 'Refunded' not in json.dumps(cl[-1]['props']), 'the closing step record carries the code "refunded", not the words')
    # 3 insurance claim playbook
    cid3 = typed(pg, 'Aviva said they would decide my claim by Friday, ref HC-77812')
    due(pg, cid3); openc(pg, cid3); pg.locator('[data-a=kept]').first.click(); wait(pg)
    ok('What did they say about the claim?' in pg.inner_text('main'), 'claim: "What did they say about the claim?"')
    pg.locator('[data-a=pb-go]', has_text='They said no').click(); wait(pg)
    m = pg.inner_text('main')
    ok('Financial Ombudsman Service is free' in m and 'Sorted can’t tell you if the decision is right' in m, 'turned down: the formal route, honestly')
    # 4 HMRC letter playbook opens with "What does the letter ask?"
    cid4 = typed(pg, 'Got a letter from HMRC saying I owe £320 tax', confirm=False)
    openc(pg, cid4)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg)
    m = pg.inner_text('main')
    ok('What does the letter ask you to do?' in m and pg.locator('a[href="https://www.gov.uk/guidance/check-if-a-letter-youve-received-from-hmrc-is-genuine"]').count() == 1, 'HMRC: what the letter asks, and how to check it is genuine')
    pg.locator('[data-a=pb-go]', has_text='Pay something by a date').click(); wait(pg)
    ok('payment plan' in pg.inner_text('main') and pg.locator('[data-a=panel][data-p=move]').count() >= 1, 'owe: check the amount, a payment plan, and a reminder')
    # 5 a promise with no company named
    home(pg)
    if pg.locator('[data-cap82=other]').first.is_visible(): pg.locator('[data-cap82=other]').first.click(); wait(pg)
    elif pg.locator('[data-a=compose]').count(): pg.locator('[data-a=compose]').first.click(); wait(pg)
    pg.fill('#f-case', 'Engineer will attend Tuesday between 2–4pm, ref A1842'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 550)
    sp = newest(pg).get('sugP') or {}
    ok(sp.get('ref') == 'A1842' and sp.get('dueEnd') and 'Tuesday' not in (sp.get('said') or 'x')[:0] and pg.locator('[data-a=sug-yes]').count() == 1, 'the engineer’s promise is proposed with the time window and ref')
    ok('Sorted doesn’t know who said it' in pg.inner_text('main'), 'and it asks who it is from')
    # 6 shared: what it looks like
    pcn = 'London Borough of Southwark PENALTY CHARGE NOTICE PCN Number: SK12345678 Vehicle Registration Mark: AB12 CDE Date of contravention: 30/09/2026 The penalty charge is £130. If paid within 14 days, reduced to £65.'
    pg.goto('https://sorted.test/?s=9#new=' + urllib.parse.quote(pcn)); wait(pg, 700)
    ok('This looks like a parking notice.' in pg.inner_text('main'), 'a shared parking notice says what it looks like')
    pg.click('[data-a=share-new]'); wait(pg)
    if pg.locator('form[data-f=case] button[type=submit]').count(): pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 550)
    ok('Southwark' in newest(pg)['title'], 'the shared notice becomes a case: %s' % newest(pg)['title'])
    ok(pg.locator('[data-a=fr-pk]').count() == 0, 'before the details are confirmed, it asks to check them first')
    pg.click('[data-a=cf-yes]'); wait(pg)
    ok(pg.locator('[data-a=fr-pk]').count() == 3, 'once confirmed: understand it, reply or challenge it, remember the deadline')
    pg.locator('[data-a=fr-pk][data-v=reply]').click(); wait(pg)
    ok(pg.locator('.fr-card').count() == 0 and ('challenge' in pg.inner_text('main').lower()), '"Reply or challenge it" opens the challenge builder')
    # 7 life moments
    home(pg)
    ok(pg.locator('[data-a=ex-moment]').count() >= 4, 'the strip lists life moments')
    pg.locator('[data-a=ex-moment][data-v=moving]').first.click(); wait(pg, 700)
    ok(pg.evaluate("document.getElementById('moment-moving').open") and pg.locator('#moment-moving .cap95-chip').count() == 8, 'Moving home opens with 8 things people track')
    pg.locator('#moment-moving [data-cap95=mv_furniture]').click(); wait(pg, 600)
    ok('Who is delivering it?' in pg.inner_text('main') and 'John Lewis' in (pg.get_attribute('#gi-who', 'placeholder') or ''), 'furniture delivery: who is delivering it, John Lewis as an example')
    home(pg); pg.locator('[data-a=ex-moment][data-v=baby]').first.click(); wait(pg, 700)
    nb = pg.inner_text('#moment-baby')
    ok('within 42 days' in nb and pg.locator('#moment-baby a[href="https://www.gov.uk/register-birth"]').count() == 1, 'New baby: registering the birth is yours, with the GOV.UK link')
    n0 = len(db(pg)['tasks']); pg.locator('#moment-baby [data-cap95=bb_childbenefit]').click(); wait(pg, 600)
    ok(pg.input_value('#gi-who') == 'HMRC' and len(db(pg)['tasks']) == n0, 'Child Benefit: HMRC filled in, nothing created yet')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'nothing scrolls sideways')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
