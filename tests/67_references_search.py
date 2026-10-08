# v110: memory and evidence. Labelled references (an order, claim, policy or complaint number) kept with a case, proposed
# from what comes in and confirmed by a tap, never bank details; search your own cases on Home; "they refunded half"
# proposes Only partly; a case with nothing due says so; the adviser pack lists the promises missed; your history with a
# company lists its references and how often the date moved.
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
    # Part 1: the reader
    rd = ctx.new_page(); rd.route(lambda u: u.startswith('https://sorted.test/'), lambda q: q.fulfill(path=HERE + '/tests/out/reader.html', content_type='text/html'))
    rd.goto('https://sorted.test/'); wait(rd, 500)
    RR = lambda t: rd.evaluate("s=>__read.refsRead(s)", t)
    for t, want in [("that's the claim number, the policy number is X882", [('policy', 'X882')]),
                    ("Order number 445566", [('order', '445566')]),
                    ("complaint ref C77-2", [('complaint', 'C77-2')]),
                    ("ticket #T1234 raised", [('ticket', 'T1234')]),
                    ("my policy number is x882", [('policy', 'X882')]),
                    ("Claim C123 under policy P882, by Friday", [('claim', 'C123'), ('policy', 'P882')]),
                    ("ref 123", [('ref', '123')]),
                    ("your reference is AB/9921", [('ref', 'AB/9921')]),
                    ("booking reference QX7PL2", [('booking', 'QX7PL2')]),
                    ("tracking number JD0002233", [('tracking', 'JD0002233')]),
                    ("job no 88213", [('job', '88213')]),
                    ("case number 2026-00412", [('case', '2026-00412')])]:
        got = [(x['k'], x['v']) for x in RR(t)]
        ok(got == want, 'reads "%s" as %s (%s)' % (t, want, got))
    for t in ["policy number ABC", "sort code 12-34-56 account number 12345678", "my card number 4111111111111111", "the engineer came on the 8th", "order of the day", "case 2", "in 2026 the policy changes", "passport number 123456789", "national insurance number QQ123456C"]:
        ok(RR(t) == [], 'reads nothing from: %s (%s)' % (t, RR(t)))
    OP = lambda t: rd.evaluate("s=>__read.OUT_PART.test(s)", t)
    for t in ["they refunded half", "only part of it arrived", "they paid some of it", "partly done", "still owe me £40", "only £40 came"]:
        ok(OP(t), 'partly: %s' % t)
    for t in ["they refunded me", "it arrived", "they didn't come", "all sorted"]:
        ok(not OP(t), 'not partly: %s' % t)
    rd.close()
    # Part 2: the interface
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    def start(text):
        pg.goto('https://sorted.test/'); wait(pg, 500)
        if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
        if pg.locator('[data-cap82=other]').count(): pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        return cases()[-1]['id']
    def paste(cid, text):
        if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
        if not pg.locator('[data-a=panel][data-p=paste]').count(): pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600)
        if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
        pg.locator('[data-a=panel][data-p=paste]').first.evaluate('e=>e.click()'); wait(pg, 300); pg.fill('#f-paste', text); pg.click('form[data-f=paste] button[type=submit]'); wait(pg, 600)
    fri = datetime.date.today() + datetime.timedelta(days=(4 - datetime.date.today().weekday()) % 7 or 7)
    # 1 a case started with two references: the claim is the main Ref, the policy number is proposed and kept
    cid = start("Aviva said they would pay my claim C123 by Friday, policy number P882")
    c = cases()[-1]
    ok(pg.locator('[data-a=sug-yes]').count() == 1 and 'C123' in pg.inner_text('main'), 'the promise card comes first, with the claim number')
    ok(any(r['k'] == 'policy' and r['v'] == 'P882' and r['st'] == 'proposed' for r in c.get('refs', [])) and not any(r['st'] == 'confirmed' and r['v'] == 'P882' for r in c.get('refs', [])), 'the policy number is proposed, not kept, before the tap')
    pg.click('[data-a=sug-yes]'); wait(pg, 600)
    ok(pg.locator('[data-a=refs-yes]').count() == 0, 'the email prompt that follows a first promise comes before any question about references')
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 400)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 400)
    m = pg.inner_text('main')
    ok(pg.locator('[data-a=refs-yes]').count() == 1 and 'Sorted found a policy number' in m and 'P882' in m, 'then Sorted asks about the policy number')
    pg.click('[data-a=refs-yes]'); wait(pg, 600)
    c = cases()[-1]; m = pg.inner_text('main')
    ok(any(r['k'] == 'policy' and r['v'] == 'P882' and r['st'] == 'confirmed' for r in c['refs']), 'Keep it confirms the policy number')
    ok('References' in m and 'Policy number' in m and 'P882' in m and 'Claim number' in m and 'C123' in m, 'the References block shows both, each with what it is')
    ok(any('Kept the policy number P882' in (e.get('label') or '') for e in c['events']), 'the history says so')
    ok(pg.locator('[data-a=refs-yes]').count() == 0, 'and the question is gone')
    # 2 a later message with a complaint reference: proposed; "Not that" keeps nothing
    paste(cid, "Thanks for your call. Your complaint reference is CR-5566.")
    m = pg.inner_text('main')
    ok(pg.locator('[data-a=refs-no]').count() == 1 and 'complaint reference' in m and 'CR-5566' in m, 'a pasted complaint reference is proposed')
    pg.click('[data-a=refs-no]'); wait(pg, 500)
    c = cases()[-1]
    ok(not any(r['v'] == 'CR-5566' and r['st'] == 'confirmed' for r in c['refs']) and 'CR-5566' not in pg.inner_text('.cap110-refs'), '"Not that" keeps nothing')
    paste(cid, "Your complaint reference is CR-5566. Thanks for contacting Aviva.")
    ok(pg.locator('[data-a=refs-yes]').count() == 0 and not any(r['v'] == 'CR-5566' and r['st'] == 'proposed' for r in cases()[-1]['refs']), 'a reference already turned down is not asked about again')
    # 3 a correction with a cue still wins over the reference reader
    paste(cid, "Sorry, the claim number is C124 not C123")
    ok(pg.locator('[data-a=corr-yes]').count() == 1 and pg.locator('[data-a=refs-yes]').count() == 0, 'a correction asks as a correction, not as a new reference')
    pg.click('[data-a=corr-yes]'); wait(pg, 600)
    c = cases()[-1]; op = [q for q in c['promises'] if q['status'] == 'open'][0]
    ok(op['ref'] == 'C124' and not any(r['v'] == 'C124' and r['st'] == 'proposed' for r in c['refs']), 'the main reference is corrected and nothing is left proposed')
    # 4 add one by hand, then remove it
    pg.evaluate("document.querySelector('details.case56-more').open=true"); pg.click('[data-a=panel][data-p=refadd]'); wait(pg, 300)
    pg.select_option('#f-refk', 'order'); pg.fill('#f-refv', 'no digits'); pg.click('form[data-f=refadd] button[type=submit]'); wait(pg, 300)
    ok('at least one digit' in pg.inner_text('main'), 'a reference needs a digit and no spaces')
    pg.fill('#f-refv', 'ord-9910'); pg.click('form[data-f=refadd] button[type=submit]'); wait(pg, 600)
    c = cases()[-1]
    ok(any(r['k'] == 'order' and r['v'] == 'ORD-9910' and r['st'] == 'confirmed' for r in c['refs']) and 'Order number' in pg.inner_text('.cap110-refs'), 'an order number added by hand, in capitals')
    pg.locator('[data-a=ref-del][data-v="ORD-9910"]').click(); wait(pg, 500)
    c = cases()[-1]
    ok(not any(r['v'] == 'ORD-9910' and r['st'] == 'confirmed' for r in c['refs']) and 'ORD-9910' not in pg.inner_text('.cap110-refs'), 'Remove takes it off the case')
    # 5 the chase message and the adviser pack carry the labelled reference
    pg.evaluate("(id)=>{var d=JSON.parse(localStorage.getItem('__mockdb'));var x=d.tasks.find(y=>y.data.id===id).data;x.promises.forEach(q=>{if(q.status==='open')q.dueAt=new Date(Date.now()-2*864e5).toISOString()});localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", cid)
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700)
    pg.click('[data-a=missed]'); wait(pg, 700)
    ask = pg.evaluate("document.querySelector('#f-ask')?document.querySelector('#f-ask').value:document.querySelector('main').innerText")
    ok('policy number is P882' in ask and 'C124' in ask, 'the chase message gives the claim and the policy number (%s)' % ask[-120:])
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600)
    pg.click('[data-a=panel][data-p=pack]'); wait(pg, 500); m = pg.inner_text('.pack-doc')
    ok('Claim number' in m and 'C124' in m and 'Policy number' in m and 'P882' in m, 'the adviser pack lists both references with their labels')
    ok('Promises missed' in m and 'C124' in m.split('Promises missed')[1] and 'didn’t happen' in m.split('Promises missed')[1], 'and has a Promises missed section')
    # 6 the second turn: "they refunded half" proposes Only partly
    cid2 = start("Currys said they would refund £89 by Friday, order 445566")
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
    # v143 (PASS2-002): only partly is proposed once the promise is due, so make Friday pass first
    pg.evaluate("(id)=>{var d=JSON.parse(localStorage.getItem('__mockdb'));var x=d.tasks.find(y=>y.data.id===id).data;x.promises.forEach(q=>{if(q.status==='open')q.dueAt=new Date(Date.now()-2*864e5).toISOString()});localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", cid2)
    pg.goto('https://sorted.test/?task=%s' % cid2); wait(pg, 700)
    paste(cid2, "they refunded half")
    m = pg.inner_text('main')
    ok(pg.locator('[data-a=out-yes]').count() == 1 and 'only part of it happened' in m, '"they refunded half" proposes Only partly')
    c = cases()[-1]; ok(all(q['status'] == 'open' for q in c['promises']), 'nothing recorded before the tap')
    pg.click('[data-a=out-yes]'); wait(pg, 500)
    ok(pg.locator('form[data-f=partly]').count() == 1 and 'What hasn’t happened yet?' in pg.inner_text('main'), 'Yes opens Only partly, which asks what is still outstanding')
    pg.fill('#f-left', '£44 of the £89'); pg.click('form[data-f=partly] button[type=submit]'); wait(pg, 700)
    c = cases()[-1]
    ok(c['promises'][0]['status'] == 'missed' and c['promises'][0].get('partly') and c['promises'][0].get('left') == '£44 of the £89', 'recorded as partly, with what is outstanding (after their date)')
    # 7 you and this company: references and how often the date moved
    cid3 = start("Aviva said they would call back on %s about claim C555" % fri.strftime('%A'))
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
    pg.evaluate("(id)=>{var d=JSON.parse(localStorage.getItem('__mockdb'));var x=d.tasks.find(y=>y.data.id===id).data;x.promises.push({id:'rp1',said:'Pay the claim',party:'Aviva',status:'replaced',dueAt:'2026-09-01T09:00:00.000Z',loggedAt:'2026-08-20T09:00:00.000Z'});localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", cid)
    pg.goto('https://sorted.test/?task=%s' % cid3); wait(pg, 700)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    m = pg.inner_text('main')
    ok('You and Aviva' in m and 'P882' in m and 'changed the date once before' in m, 'your history with Aviva lists the policy number and the moved date (%s)' % re.sub(r'\s+', ' ', m.split('You and Aviva')[1][:200] if 'You and Aviva' in m else ''))
    # 8 a case with nothing due says so after 2 days
    cid4 = start("Got a letter from the council about my bins and I need to sort it")
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    pg.evaluate("(id)=>{var d=JSON.parse(localStorage.getItem('__mockdb'));var x=d.tasks.find(y=>y.data.id===id).data;x.created=new Date(Date.now()-3*864e5).toISOString();x.frNew=false;localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", cid4)
    pg.goto('https://sorted.test/?task=%s' % cid4); wait(pg, 700)
    m = pg.inner_text('main')
    ok('Nothing is due on this case' in m and 'a step of your own' in m, 'a case with nothing due says so (%s)' % (pg.inner_text('.case96-health') if pg.locator('.case96-health').count() else 'no health line'))
    pg.goto('https://sorted.test/?task=%s' % cid3); wait(pg, 600)
    ok('Nothing is due' not in pg.inner_text('main'), 'a case with a live promise does not say it')
    # 9 Home search: appears with four cases, finds by reference, company and words, escapes hostile titles, says when nothing matches
    pg.goto('https://sorted.test/'); wait(pg, 700)
    ok(pg.locator('#case-search').count() == 1, 'with four cases Home has Find a case')
    def search(q):
        pg.fill('#case-search', q); wait(pg, 300); return pg.locator('#case-found .home44-row').evaluate_all('es=>es.map(e=>e.innerText)')
    r = search('P882'); ok(len(r) == 1 and 'Aviva' in r[0], 'a labelled reference finds its case (%s)' % r)
    r = search('aviva'); ok(len(r) == 2 and all('Aviva' in x for x in r), 'a company finds both its cases (%s)' % len(r))
    r = search('refund currys'); ok(len(r) == 1 and 'Currys' in r[0], 'words in any order find the case')
    r = search('445566'); ok(len(r) == 1 and 'Currys' in r[0], 'a main reference finds its case')
    search('zzzz'); ok('No case matches that' in pg.inner_text('#case-found'), 'no match says so')
    pg.locator('#case-found .home44-row').count()
    pg.fill('#case-search', 'P882'); wait(pg, 300); pg.locator('#case-found .home44-row').first.click(); wait(pg, 600)
    ok('P882' in pg.inner_text('main') and pg.locator('.cap110-refs').count() == 1, 'tapping a result opens the case')
    pg.evaluate("()=>{var d=JSON.parse(localStorage.getItem('__mockdb'));var x=d.tasks.find(y=>y.data.title&&/bins/.test(y.data.title)).data;x.title='<img src=x onerror=window.__pwned=1> bins <b>x</b>';localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}")
    pg.goto('https://sorted.test/'); wait(pg, 700); search('bins'); wait(pg, 300)
    ok(not pg.evaluate("!!window.__pwned") and pg.locator('#case-found img').count() == 0 and '<img' in pg.inner_text('#case-found'), 'a hostile title is shown as text in the results')
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    start("Sky said an engineer would come %s, ref AB123" % fri.strftime('%A'))
    pg.goto('https://sorted.test/'); wait(pg, 600)
    ok(pg.locator('#case-search').count() == 0, 'with one case there is no search box')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'nothing scrolls sideways')
    print('CHECKS', n[0]); b.close()
print('ERRORS', errs); print('FAILS', fails)
