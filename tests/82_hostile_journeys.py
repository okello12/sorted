# v124 (remediation Phase D): three hostile journeys end to end, with the ledger watched throughout.
# 1 Parking: a blurred photo fails and changes nothing; the details are typed instead; a challenge is written from what
#   was ticked, sent, then rejected in their words; at every step nothing becomes a fact without a tap and the ledger
#   keeps every version. 2 Repair: a dangerous description stops for safety first; the engineer doesn't come (a missed
#   appointment, the chase ready, the count kept); a new date is kept; the kind of case is changed away and back with
#   nothing lost. 3 Two moves in two nations: a case started in a Scottish move, a second move in Northern Ireland, the
#   case moved between them only after a question, each move's official links its own nation's and no other.
# The refund cycle lives in test 47 and the two-device case in test 66.
import os, sys, json, re, datetime
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
def uk(d): return (datetime.date.today() + datetime.timedelta(days=d)).strftime('%d/%m/%Y')
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', cdn)
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    sp = b.new_page(viewport={'width': 560, 'height': 420})
    sp.set_content('<body style="margin:0;background:#fff;font-family:Arial;font-size:20px;line-height:1.5;padding:24px;filter:blur(3.5px)"><b>LAMBETH COUNCIL</b><br><b>PENALTY CHARGE NOTICE</b><br>PCN Number: LJ12345678<br>Vehicle registration: AB12 CDE<br>Date of contravention: 03/10/2026<br>Penalty charge: £130</body>')
    sp.screenshot(path=HERE + '/tests/out/doc82_blur.png'); sp.close()
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    moms = lambda: [x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') == 'moment']
    case = lambda cid: [x for x in cases() if x['id'] == cid][0]
    labels = lambda cid: [e.get('label') or '' for e in case(cid)['events']]
    L = lambda cid: case(cid).get('ledger') or []
    main = lambda: pg.inner_text('main')
    stage = lambda cid: (case(cid).get('pk') or {}).get('stage')
    def poke(js):
        pg.goto('https://sorted.test/'); wait(pg, 700)
        pg.evaluate("(js)=>{var db=JSON.parse(localStorage.getItem('__mockdb'));(new Function('db',js))(db);localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", js)
    def settle():
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    def paste(text):
        pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
        pg.locator('[data-a=panel][data-p=paste]').first.evaluate('e=>e.click()'); wait(pg, 300); pg.fill('#f-paste', text); pg.click('form[data-f=paste] button[type=submit]'); wait(pg, 600)
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    uid = pg.evaluate("JSON.parse(localStorage.getItem('__mocksession')).user.id")
    # ================= 1. parking: bad photo, manual recovery, challenge, rejection =================
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.fill('#f-case', 'PCN'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 500)
    pg.set_input_files('input[data-ocr=f-case]', HERE + '/tests/out/doc82_blur.png')
    for _ in range(240):
        st = pg.inner_text('#ocr-status') if pg.locator('#ocr-status').count() else ''
        if re.search(r'Photo read|couldn’t|doesn’t look', st): break
        wait(pg, 500)
    ok('We couldn’t read this photo clearly. Your case hasn’t been changed.' in st and not cases() and pg.locator('form[data-f=doc]').count() == 0, 'P1 the blurred photo fails clearly and creates nothing')
    pg.click('[data-a=doc-manual]'); wait(pg, 500)
    ok(pg.locator('.doc121-fail').count() == 0 and pg.locator('.doc125-manual form[data-f=doc]').count() == 1, 'P2 "Enter the details manually" opens the notice form with the failure gone')
    pg.fill('#doc-issuer', 'Southwark Council'); pg.fill('#doc-ref', 'SK12345678'); pg.fill('#doc-vrm', 'AB12 CDE'); pg.fill('#doc-when', uk(-6)); pg.fill('#doc-amount', '130'); pg.fill('#doc-discount', '65')
    pg.click('form[data-f=doc] button[type=submit]'); wait(pg, 700); settle()
    cid = cases()[-1]['id']
    ok(case(cid).get('cf') and all(x['st'] == 'confirmed' and x['how'] == 'you' for x in case(cid)['cf']['f'].values()) and pg.locator('.cf-check').count() == 0, 'P3 what you typed into the form is confirmed as yours, with no second check')
    lg = [r for r in L(cid) if r['type'] == 'notice']
    ok(lg and all(r['st'] == 'confirmed' and r['by'] == 'you' for r in lg), 'P4 the ledger has them as yours, confirmed by you')
    ok(pg.locator('form[data-f=call]').count() == 0, 'P5 the new parking case does not open call preparation')
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600)
    pg.click('.pk-card [data-a=panel][data-p=pkbuild]'); wait(pg)
    pg.check('input[name=bdg-paid]'); pg.fill('textarea[name=bdd-paid]', 'I paid at 10:05 on RingGo, session 445821'); pg.check('input[name=bde-receipt]')
    pg.click('form[data-f=pkbuild] button[type=submit]'); wait(pg)
    draft = pg.input_value('#f-bdtext')
    ok('SK12345678' in draft and 'I paid at 10:05 on RingGo' in draft and 'sign' not in draft.lower() and stage(cid) != 'challenged', 'P6 the challenge uses the confirmed details and your words, nothing you didn’t tick, and is not sent yet')
    pg.click('form[data-f=pkdraft] button[type=submit]'); wait(pg); pg.fill('#f-pkref', 'CH-77'); pg.click('form[data-f=pksent] button[type=submit]'); wait(pg)
    ok(stage(cid) == 'challenged' and 'I paid at 10:05 on RingGo' in json.dumps(case(cid)['pk']), 'P7 "I’ve sent it" keeps the exact text and moves the stage')
    paste("Southwark Council Parking Services. Date: %s. PCN SK12345678, vehicle AB12 CDE. We have considered your challenge. We do not accept it. Our records show no valid payment was made for this vehicle at the time of the contravention. The penalty charge remains payable." % uk(0))
    rc = pg.inner_text('.rs-card') if pg.locator('.rs-card').count() else ''
    ok('said no. Is that right?' in rc and stage(cid) == 'challenged', 'P8 their rejection is proposed in their words; the stage has not moved')
    pg.click('[data-a=rs-yes]'); wait(pg)
    ok(stage(cid) == 'rejected', 'P9 confirming moves the stage to rejected')
    ok(not any(r['st'] in ('superseded',) and r['type'] == 'notice' for r in L(cid)) and all(r['st'] == 'confirmed' for r in L(cid) if r['type'] == 'notice'), 'P10 the notice details never changed under you through the whole journey')
    # ================= 2. repair: safety first, a missed appointment, a new date, the kind changed and back =================
    pg.goto('https://sorted.test/'); wait(pg, 500); pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
    n0 = len(cases())
    pg.fill('#f-case', 'The socket behind the washing machine is crackling and smells of burning. The landlord said an electrician would come on Monday'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 700)
    m = main()
    ok(pg.locator('[data-a=safe-continue]').count() == 1 and len(cases()) == n0, 'R1 a crackling, burning socket stops for safety before anything else, and no case exists yet')
    if pg.locator('[data-a=safe-continue]').count(): pg.click('[data-a=safe-continue]'); wait(pg, 600)
    settle()
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
    rid = cases()[-1]['id']; c = case(rid)
    ok(c.get('safety') is True and any('Safety stop' in l for l in labels(rid)), 'R2 the safety stop is recorded on the case')
    ok(any(q['status'] == 'open' for q in c['promises']) and c['promises'][-1]['party'].lower().startswith('landlord') or 'landlord' in json.dumps(c['promises']).lower(), 'R3 the landlord’s promise is on the case (%s)' % [(q['party'], q['status']) for q in c['promises']])
    poke("var x=db.tasks.find(y=>y.data.id==='%s').data;x.promises.forEach(q=>{if(q.status==='open')q.dueAt=new Date(Date.now()-2*864e5).toISOString()})" % rid)
    pg.goto('https://sorted.test/?task=%s' % rid); wait(pg, 600)
    ok(pg.locator('.promise [data-a=missed]').count() == 1, 'R4 once the day has passed the case asks what happened')
    pg.click('.promise [data-a=missed]'); wait(pg, 500)
    c = case(rid)
    ok(c['promises'][-1]['status'] == 'missed' and pg.locator('form[data-f=call]').count() == 1 and (c.get('pb') or {}).get('noShows', 0) >= 1, 'R5 the no-show is counted and the chase is ready (noShows %s)' % (c.get('pb') or {}).get('noShows'))
    paste('Landlord says the electrician will come on %s instead' % (datetime.date.today() + datetime.timedelta(days=3)).strftime('%A %-d %B'))
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
    c = case(rid)
    ok(c['promises'][-1]['status'] == 'open' and c['promises'][-2]['status'] == 'missed' and len([r for r in L(rid) if r['type'] == 'promise' and r['sub'] != 'proposal']) == 2, 'R6 the new date is a new promise; the missed one stays in the record and the ledger')
    snap = {k: v for k, v in c.items() if k not in ('mode', 'fix', 'renew', 'kept', 'events', 'updatedAt', 'rev', 'frNew', 'goalP', 'ledger', 'ledgerV', 'turnAt')}
    for kind in ('fix', 'call'):
        pg.goto('https://sorted.test/?task=%s' % rid); wait(pg, 500); pg.evaluate("document.querySelectorAll('details.case56-more').forEach(d=>d.open=true)")
        pg.click('[data-a=panel][data-p=kind]'); wait(pg, 300); pg.click('[data-k=kind][data-v=%s]' % kind); wait(pg, 150); pg.click('form[data-f=kind] button[type=submit]'); wait(pg, 600)
        if pg.locator('[data-a=panel][data-p=""]').count() and pg.locator('#moveform').count(): pg.locator('[data-a=panel][data-p=""]').first.click(); wait(pg, 300)
    c2 = case(rid); snap2 = {k: v for k, v in c2.items() if k not in ('mode', 'fix', 'renew', 'kept', 'events', 'updatedAt', 'rev', 'frNew', 'goalP', 'ledger', 'ledgerV', 'turnAt')}
    ok(snap2 == snap and c2['mode'] == 'call' and c2['safety'] is True, 'R7 changing the kind away and back loses nothing (%s)' % [k for k in set(snap) | set(snap2) if snap.get(k) != snap2.get(k)])
    # ================= 3. two moves, two nations, one case moved between them only after a question =================
    pg.goto('https://sorted.test/'); wait(pg, 500)
    pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300)
    if pg.locator('[data-a=mom-start]').count(): pg.locator('[data-a=mom-start]').first.evaluate('e=>e.click()'); wait(pg, 500)
    d1 = (datetime.date.today() + datetime.timedelta(days=20)).isoformat()
    pg.fill('#mv-date', d1); pg.click('label.chip:has(input[name=mv-tenure][value=rent])'); pg.click('label.chip:has(input[name=mv-car][value=yes])'); pg.click('label.chip:has(input[name=mv-nation][value=sc])')
    pg.click('form[data-f=mom] button[type=submit]'); wait(pg, 600)
    m1 = moms()[0]; hs = pg.locator('main a[href^=http]').evaluate_all('es=>es.map(e=>e.href)')
    ok(m1['ans']['nation'] == 'sc' and any('nhsinform.scot' in h for h in hs) and not any('nidirect' in h for h in hs) and not any('111.wales' in h for h in hs), 'M1 the Scottish move has NHS inform and no other nation’s page')
    # a case started inside the move, with a promise
    pg.locator('[data-a=mom-case][data-k=broadband], [data-a=mom-case]').first.evaluate('e=>e.click()'); wait(pg, 400)
    if pg.locator('#gi-what').count():
        pg.fill('#gi-what', 'Virgin will install on %s ref V123' % (datetime.date.today() + datetime.timedelta(days=18)).strftime('%A %-d %B')); pg.click('form[data-f=gi] button[type=submit]'); wait(pg, 800)
    settle()
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
    vc = [x for x in cases() if 'Virgin' in (x.get('title') or '') or 'V123' in json.dumps(x)]
    ok(vc and vc[-1].get('momentId') == m1['id'] and any(q['status'] == 'open' for q in vc[-1]['promises']), 'M2 the case started inside the move is linked to it with Virgin’s promise')
    vid = vc[-1]['id']
    # a second move, in Northern Ireland, 3 months later
    d2 = (datetime.date.today() + datetime.timedelta(days=110)).isoformat()
    pg.goto('https://sorted.test/'); wait(pg, 600)
    e = pg.locator('[data-a=mom-start]')
    if e.count(): e.first.evaluate('e=>e.click()')
    else: pg.locator('[data-a=mom-new]').first.evaluate('e=>e.click()')
    wait(pg, 500)
    if not pg.locator('#mv-date').count(): pg.locator('[data-a=mom-new]').first.evaluate('e=>e.click()'); wait(pg, 400)
    pg.fill('#mv-date', d2); pg.click('label.chip:has(input[name=mv-tenure][value=buy])'); pg.click('label.chip:has(input[name=mv-council][value=new])'); pg.click('label.chip:has(input[name=mv-nation][value=ni])')
    pg.click('form[data-f=mom] button[type=submit]'); wait(pg, 600)
    ms = moms(); m2 = [x for x in ms if x['date'] == d2]
    ok(len(ms) == 2 and m2 and m2[0]['ans']['nation'] == 'ni', 'M3 a second move, in Northern Ireland, beside the first')
    hs2 = pg.locator('main a[href^=http]').evaluate_all('es=>es.map(e=>e.href)'); mm = main()
    ok(any('nidirect' in h for h in hs2) and any('eoni' in h for h in hs2) and not any('nhsinform.scot' in h for h in hs2) and 'Land & Property Services' in mm, 'M4 the Northern Ireland move has nidirect, EONI and rates, and no Scottish page')
    # link the Virgin case to the second move: it asks first, because the case is in the first move
    pg.locator('[data-a=mom-panel][data-p=link]').first.evaluate('e=>e.click()'); wait(pg, 400)
    btn = pg.locator('[data-a=mom-link][data-id="%s"]' % vid)
    ok(btn.count() == 1, 'M5 the second move offers to link the existing case')
    if btn.count():
        btn.first.evaluate('e=>e.click()'); wait(pg, 400); mm = main()
        ok(case(vid).get('momentId') == m1['id'] and 'Tap it again to move it here' in mm, 'M6 it asks before taking a case from another move; nothing has moved yet')
        pg.locator('[data-a=mom-link][data-id="%s"]' % vid).first.evaluate('e=>e.click()'); wait(pg, 500)
        ok(case(vid).get('momentId') == m2[0]['id'] and not any(v.get('caseId') == vid for v in [x for x in moms() if x['id'] == m1['id']][0].get('items', {}).values()), 'M7 after the answer the case is in one move only, the second')
    ok(any(q['status'] == 'open' for q in case(vid)['promises']) and 'V123' in json.dumps(case(vid)), 'M8 the case kept its promise and reference through the move')
    ok(not errs, 'no page errors: %s' % errs)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
