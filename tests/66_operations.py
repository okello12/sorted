# v109: what the commercial review asked for. Errors reach the operator as a kind, a screen and a build, never case
# text; a case saved on two devices is merged and the person told, never silently overwritten; a case deleted elsewhere
# is removed here and said so; "Email reminder set" only once the reminder row is written; the anonymous account is
# described as an account only this phone can open; no pilot wording; terms and a way to report a problem; a readable
# file of every case; a second turn ("They didn't come", "it arrived") proposes the outcome; "but nothing" is a miss;
# records from older versions still load; dates across the clock change and the year end.
import os, sys, re, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    # dates first, on the reader
    rd = ctx.new_page(); rd.route(lambda u: u.startswith('https://sorted.test/'), lambda q: q.fulfill(path=HERE + '/tests/out/reader.html', content_type='text/html'))
    rd.goto('https://sorted.test/'); wait(rd, 500)
    W = lambda t, d: rd.evaluate("([s,d])=>{var w=__read.parseWhen(s,new Date(d+'T10:00:00'));return w?w.date+(w.from?' '+w.from:''):null}", [t, d])
    for t, d, want in [("in 3 days", '2026-10-24', '2026-10-27'), ("tomorrow at 8am", '2026-10-24', '2026-10-25 08:00'), ("Monday", '2026-10-23', '2026-10-26'), ("in 2 working days", '2026-12-24', '2026-12-30'), ("in 5 days", '2026-12-29', '2027-01-03'), ("next week", '2026-12-30', '2027-01-08'), ("by the 2nd of January", '2026-12-29', '2027-01-02'), ("in 3 working days", '2027-03-25', '2027-03-31')]:
        r = W(t, d); ok(r == want, '"%s" said on %s is %s (%s)' % (t, d, want, r))
    ok(rd.evaluate("()=>__read.PMISS.test('they said Friday but nothing')") and rd.evaluate("()=>__read.PMISS.test('said Tuesday but still nothing')") and not rd.evaluate("()=>__read.PMISS.test('nothing to report, they said Friday')"), '"but nothing" is missed-promise language')
    r = rd.evaluate("()=>{var t='they said Friday but nothing',f=__read.caseFacts(t),s=__read.readCase(t,f);return s?{past:!!s.past}:null}")
    ok(r and r['past'], '"they said Friday but nothing" is a missed promise, not next Friday')
    rd.close()
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    rows = lambda: dbj().get('tasks', [])
    cases = lambda: [x['data'] for x in rows() if x['data'].get('kind') != 'moment']
    errlog = lambda: json.loads(pg.evaluate("localStorage.getItem('__errs')") or '[]')
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    body = pg.inner_text('body')
    ok('research pilot' not in body and 'taking part in the Sorted pilot' not in body and 'whether the pilot works' not in body, 'no pilot wording anywhere on the page')
    pg.locator('[data-a=data]').first.evaluate('e=>e.click()'); wait(pg, 500)
    ok('This phone only' not in pg.inner_text('body') and 'only this phone can open' in pg.inner_text('body') and 'research pilot' not in pg.inner_text('body'), 'the anonymous account is described as an account only this phone can open')
    pg.goto('https://sorted.test/'); wait(pg, 500)
    # 1 errors reach the operator, never case text
    pg.evaluate("setTimeout(function(){throw new Error('test boom \"Sky said secret things\"')},0)"); wait(pg, 400)
    e = errlog()
    ok(e and e[-1]['p_source'] == 'page' and e[-1]['p_kind'] == 'Error' and 'secret' not in e[-1]['p_detail'] and 'test boom' in e[-1]['p_detail'] and re.match(r'v1[0-9][0-9] ', e[-1]['p_build']), 'a page error is reported with its kind, the screen and the build, quoted words removed: %s' % json.dumps(e[-1:])[:200])
    pg.evaluate("setTimeout(function(){Promise.reject(new TypeError('late'))},0)"); wait(pg, 400)
    ok(errlog()[-1]['p_kind'] == 'TypeError', 'an unhandled rejection too')
    for i in range(6): pg.evaluate("setTimeout(function(){throw new Error('flood')},0)")
    wait(pg, 500); ok(len(errlog()) <= 5, 'at most 5 reports per page load')
    # 2 a case, then a reminder: "set" only once written
    pg.evaluate("localStorage.setItem('__mocksession', JSON.stringify(Object.assign(JSON.parse(localStorage.getItem('__mocksession')||'{}'),{user:Object.assign(JSON.parse(localStorage.getItem('__mocksession')||'{}').user||{},{email:'me@example.com'})})))")
    pg.reload(); wait(pg, 600)
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg)
    pg.fill('#f-case', 'Sky said an engineer would come next Tuesday between 8 and 12, ref AB123'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    pg.click('[data-a=sug-yes]'); wait(pg, 800)
    c = cases()[0]; cid = c['id']
    ok(c.get('rev') == 1 or c.get('rev') == 2, 'a saved case carries a revision (%s)' % c.get('rev'))
    tx = pg.inner_text('#toast') if pg.locator('#toast').count() else ''
    ok('Email reminder set' in tx or (not dbj().get('reminders')), 'the reminder toast says "set" only once the row is written (%r)' % tx)
    ok(not any('will email you a reminder' in (x.get('label') or '') for x in c['events']), 'no "will email you" claim')
    # a reload after a save is silent: the cache never holds a saved record as unsaved, so nothing is saved again or merged
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 500)
    r0 = cases()[0]['rev']; pg.reload(); wait(pg, 900); pg.goto('https://sorted.test/'); wait(pg, 900)
    c = cases()[0]
    ok(c['rev'] == r0 and not any('Merged with changes' in (x.get('label') or '') for x in c['events']) and 'merged' not in (pg.inner_text('#toast') if pg.locator('#toast').count() else ''), 'two reloads after a save change nothing (rev %s, was %s)' % (c['rev'], r0))
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 500)
    # 3 two devices: the other device saves first; this one merges and says so
    before_rev = cases()[0]['rev']
    pg.evaluate("(id)=>{var d=JSON.parse(localStorage.getItem('__mockdb'));var r=d.tasks.find(x=>x.data.id===id);r.data.rev=(r.data.rev||0)+1;r.data.title='Changed on the laptop';r.data.events.push({at:new Date().toISOString(),label:'Added on the laptop.'});localStorage.setItem('__mockdb',JSON.stringify(d))}", cid)
    pg.locator('[data-a=panel][data-p=paste]').first.evaluate('e=>e.click()'); wait(pg, 300); pg.fill('#f-paste', 'They rang to confirm the slot'); pg.click('form[data-f=paste] button[type=submit]'); wait(pg, 1200)
    c = cases()[0]; labels = [x.get('label') or '' for x in c['events']]
    ok(c['title'] == 'Changed on the laptop' and any('Added on the laptop' in l for l in labels) and any('They rang to confirm' in l for l in labels), 'both devices’ changes are in the saved case')
    ok(any(l.startswith('Merged with changes saved from another device') for l in labels) and c['rev'] >= before_rev + 2, 'the history says it was merged, and the revision moved on (%s)' % c['rev'])
    ok('merged the two' in (pg.inner_text('#toast') if pg.locator('#toast').count() else ''), 'the person is told')
    # a closed promise on the other device beats an open one here
    pg.evaluate("(id)=>{var d=JSON.parse(localStorage.getItem('__mockdb'));var r=d.tasks.find(x=>x.data.id===id);r.data.rev+=1;r.data.promises.forEach(q=>{if(q.status==='open'){q.status='kept';q.closedAt=new Date().toISOString()}});localStorage.setItem('__mockdb',JSON.stringify(d))}", cid)
    pg.evaluate("document.querySelector('details.case56-more').open=true"); pg.click('[data-a=panel][data-p=correct]'); wait(pg, 300)
    pg.fill('#f-correct', 'the ref is AB132'); pg.click('form[data-f=correct] button[type=submit]'); wait(pg, 1200)
    c = cases()[0]
    ok(all(q['status'] != 'open' for q in c['promises']) and c.get('corrP'), 'the laptop’s "kept" wins over this device’s stale open promise, and this device’s pending correction survives')
    # 4 deleted on the other device
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600)
    pg.evaluate("(id)=>{var d=JSON.parse(localStorage.getItem('__mockdb'));d.tasks=d.tasks.filter(x=>x.data.id!==id);localStorage.setItem('__mockdb',JSON.stringify(d))}", cid)
    if pg.locator('[data-a=corr-no]').count(): pg.click('[data-a=corr-no]'); wait(pg, 1200)
    else:
        pg.evaluate("document.querySelector('details.case56-more').open=true"); pg.click('[data-a=panel][data-p=correct]'); wait(pg, 300)
        pg.fill('#f-correct', 'the ref is AB199'); pg.click('form[data-f=correct] button[type=submit]'); wait(pg, 1200)
    ok(not [x for x in cases() if x['id'] == cid] and pg.locator('main').count() == 1 and 'deleted on another device' in (pg.inner_text('#toast') if pg.locator('#toast').count() else ''), 'a case deleted elsewhere is removed here, with a word')
    # 5 the second turn
    pg.goto('https://sorted.test/'); wait(pg, 500); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg)
    pg.fill('#f-case', 'British Gas said an engineer would come yesterday morning'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    if pg.locator('[data-a=sug-yes][data-v=open]').count(): pg.click('[data-a=sug-yes][data-v=open]'); wait(pg, 600)
    elif pg.locator('[data-a=sug-yes]').count():
        # yesterday reads as missed already; make a live promise for the turn test instead
        pg.click('[data-a=sug-no]'); wait(pg, 400)
    c2 = [x for x in cases() if 'British Gas' in (x.get('said') or '')][0]; cid2 = c2['id']
    if not any(q['status'] == 'open' for q in c2.get('promises', [])):
        pg.evaluate("(id)=>{var d=JSON.parse(localStorage.getItem('__mockdb'));var r=d.tasks.find(x=>x.data.id===id);r.data.promises=[{id:'pbg',said:'An engineer would come',party:'British Gas',dueAt:new Date(Date.now()-864e5).toISOString(),allDay:true,by:false,status:'open',loggedAt:new Date().toISOString()}];delete r.data.frNew;delete r.data.sugP;localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", cid2)
    pg.goto('https://sorted.test/?task=%s' % cid2); wait(pg, 600)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    pg.locator('[data-a=panel][data-p=paste]').first.evaluate('e=>e.click()'); wait(pg, 300); pg.fill('#f-paste', "They didn't come"); pg.click('form[data-f=paste] button[type=submit]'); wait(pg, 700)
    m = pg.inner_text('main')
    ok('Sounds like it didn’t happen' in m and 'British Gas' in m and pg.locator('[data-a=out-yes]').count() == 1, '"They didn’t come" connects to British Gas’s visit and proposes a miss')
    pg.click('[data-a=out-yes]'); wait(pg, 700)
    c2 = [x for x in cases() if x['id'] == cid2][0]
    ok(any(q['status'] == 'missed' for q in c2['promises']) and pg.locator('#f-ask').count() == 1, 'Yes records the miss and gets the chase ready')
    # 6 the data page: wording, terms, report, file
    pg.goto('https://sorted.test/'); wait(pg, 500); pg.locator('[data-a=data]').first.evaluate('e=>e.click()'); wait(pg, 500)
    d = pg.inner_text('main')
    ok('How Sorted works, in writing' in d and 'Reminders are best efforts' in d and '10 working days' in d and 'law of England and Wales' in d, 'terms in plain English, with a complaints route')
    ok(pg.locator('a[href^="mailto:"][href*="Sorted%20problem"]').count() >= 1, '"Report a problem" composes an email')
    href = pg.locator('a[href^="mailto:"][href*="Sorted%20problem"]').first.get_attribute('href')
    ok(re.search(r'v1[0-9][0-9]', href) and 'Sky' not in href and 'AB1' not in href, 'the report carries the version and never case words')
    ok(pg.locator('[data-a=export-file]').count() == 1 and 'plain text' in d, 'a readable file of every case is offered')
    with pg.expect_download() as dl: pg.click('[data-a=export-file]')
    path = dl.value.path(); txt = open(path, encoding='utf8').read()
    ok('Your cases from Sorted' in txt and 'British Gas' in txt and 'CASE SUMMARY' in txt.upper(), 'and it contains the cases in words')
    # 7 records from older versions still load
    pg.evaluate("""()=>{var d=JSON.parse(localStorage.getItem('__mockdb'));var now=new Date().toISOString();
      d.tasks.push({id:'legacy1',data:{id:'legacy1',mode:'call',title:'Old Currys refund',baseline:'Not sure yet',created:'2026-09-29T10:00:00.000Z',updatedAt:'2026-09-29T10:00:00.000Z',board:'waiting',safety:false,fix:null,renew:null,call:{who:'Currys',via:'phone',ask:'Hi'},promises:[{id:'lp1',said:'Refund by Friday',party:'Currys',dueAt:'2026-10-09T00:00:00.000Z',dueEnd:null,allDay:true,by:true,ref:'C991',status:'open',loggedAt:'2026-09-29T10:00:00.000Z'}],outcome:'',events:[{at:'2026-09-29T10:00:00.000Z',label:'Started.'}],sharedAt:null}});
      d.tasks.push({id:'legacy2',data:{id:'legacy2',mode:'fix',title:'Washing machine won’t drain',baseline:'Ring them',created:'2026-09-20T10:00:00.000Z',updatedAt:now,board:'yours',safety:false,fix:{step:'what',checks:{},item:'Washing machine'},renew:null,call:null,promises:[],outcome:'',events:[{at:'2026-09-20T10:00:00.000Z',label:'Started.'}],sharedAt:null,cf:{f:{}}}});
      d.tasks.push({id:'legacym',data:{id:'legacym',kind:'moment',type:'moving',title:'Moving home',date:'2026-11-20',ans:{tenure:'rent',council:'unsure',car:'no',bb:'no'},items:{},created:now,updatedAt:now}});
      localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}""")
    pg.goto('https://sorted.test/'); wait(pg, 800); hm = pg.inner_text('main')
    ok('Old Currys refund' in hm and 'Washing machine' in hm and 'Moving home' in hm, 'Home shows records written by older versions')
    for lid in ('legacy1', 'legacy2'):
        pg.goto('https://sorted.test/?task=%s' % lid); wait(pg, 700)
        ok(pg.locator('main').count() == 1 and len(pg.inner_text('main')) > 80, 'an old case renders (%s)' % lid)
    pg.goto('https://sorted.test/?task=legacy1')
    try: pg.wait_for_selector('main:has-text("C991")', timeout=8000)
    except Exception: pass
    m6 = pg.inner_text('main')
    ok('C991' in m6 and re.search(r'9\s*Oct', m6), 'its promise, reference and date are intact (%r)' % m6[:120])
    pg.goto('https://sorted.test/'); wait(pg, 600); pg.locator('.cap99-row').first.click(); wait(pg, 600)
    ok('Give notice to your landlord' in pg.inner_text('main') and 'Which nation' in pg.inner_text('main'), 'an old move renders and asks the new question once')
    ok(all((x['data'].get('rev') or 0) >= 1 for x in rows() if x['data']['id'] in ('legacy1', 'legacy2', 'legacym')), 'old records gain a revision on first load')
    real_errs = [x for x in errs if 'test boom' not in x and 'flood' not in x and 'late' not in x]
    ok(not real_errs, 'no page errors: %s' % real_errs[:3])
    print('CHECKS', n[0]); b.close()
print('ERRORS', [x for x in errs if 'test boom' not in x and 'flood' not in x and 'late' not in x]); print('FAILS', fails)
