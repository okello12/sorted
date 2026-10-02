# v67: escalation route. When a case has gone round, the next formal step for its sector, offered and folded away.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=350): pg.wait_for_timeout(ms)
def tasks(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks.map(y=>y.data)")
def case(pg, title): return next((x for x in tasks(pg) if x['title'] == title), None)
def start(pg, text):
    pg.goto('https://sorted.test/'); wait(pg, 400)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
    pg.fill('#f-case', text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 450)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg)
    if pg.locator('[data-a=cf-yes]').count(): pg.click('[data-a=cf-yes]'); wait(pg)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 150)
    return sorted(tasks(pg), key=lambda x: x.get('created') or '')[-1]['id']
def age(pg, cid, days, missed):
    pg.evaluate("""([id,days,missed])=>{var db=JSON.parse(localStorage.getItem('__mockdb'));var x=db.tasks.find(y=>y.data.id===id).data;
      x.created=new Date(Date.now()-days*864e5).toISOString();for(var i=0;i<missed;i++)x.promises.push({id:'m'+i,said:'call back',party:x.promises[0]?x.promises[0].party:'',status:'missed',dueAt:new Date(Date.now()-3*864e5).toISOString(),closedAt:new Date().toISOString()});
      localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}""", [cid, days, missed])
def view(pg, cid):
    pg.goto('https://sorted.test/'); wait(pg, 400); pg.locator('[data-a=open][data-id="%s"]' % cid).first.click(); wait(pg)
    return pg.inner_text('.xr-fold') if pg.locator('.xr-fold').count() else ''
def hrefs(pg): return [a.get_attribute('href') for a in pg.locator('.xr-fold a').all()]
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 200); pg.click('[data-a=anon-start]'); wait(pg)
    # 1 a fresh case: nothing
    e = start(pg, "Octopus Energy said they will fix my bill by Friday")
    ok(view(pg, e) == '', 'a fresh case doesn’t show escalation')
    # 2 gone round: energy
    age(pg, e, 20, 2); x = view(pg, e)
    ok('If they still don’t sort it' in x and pg.locator('.xr-fold[open]').count() == 0, 'once it has gone round, the next step is offered, folded away')
    pg.click('.xr-fold summary'); wait(pg, 150); x = pg.inner_text('.xr-fold')
    ok('They’ve missed 2 promises.' in x and '8 weeks after you first complained' in x and 'deadlock letter' in x and '12 months' in x, 'energy: the 8 weeks, deadlock letter and 12 months')
    ok('https://www.energyombudsman.org/we-may-be-able-to-help-resolve-your-energy-dispute' in hrefs(pg), 'energy: the Energy Ombudsman’s own page')
    ok('Keeping on chasing is fine too' in x and 'can’t tell you whether a complaint will succeed' in x and 'checked by a person on 2 Oct 2026' in x, 'offered, not pushed, honest, and dated')
    # 3 telecoms: six weeks and the schemes
    t = start(pg, "EE said they would fix my broadband by Tuesday"); age(pg, t, 45, 0); view(pg, t); pg.click('.xr-fold summary'); wait(pg, 150); x = pg.inner_text('.xr-fold')
    ok('6 weeks after you first formally complained' in x and 'https://www.commsombudsman.org/' in hrefs(pg) and 'https://www.cedr.com/consumer/cisas/' in hrefs(pg), 'telecoms: 6 weeks and both schemes')
    ok('It’s been 6 weeks since you started this case.' in x, 'it says how long the case has run')
    # 4 a shop: no ombudsman
    s = start(pg, "Currys refund hasn't arrived, it's been three weeks, order 445566"); age(pg, s, 30, 1); view(pg, s); pg.click('.xr-fold summary'); wait(pg, 150); x = pg.inner_text('.xr-fold')
    ok('Most shops and couriers don’t have an ombudsman' in x and 'https://www.gov.uk/make-court-claim-for-money' in hrefs(pg), 'a shop: Citizens Advice and the small claims court')
    ok('Ofcom' not in x, '"three weeks" isn’t mistaken for the network Three')
    # 5 council, DWP
    c = start(pg, "The council still hasn't collected my bins after I reported it"); age(pg, c, 50, 0); view(pg, c); pg.click('.xr-fold summary'); wait(pg, 150)
    ok('https://www.lgo.org.uk/' in hrefs(pg) and 'within 12 months' in pg.inner_text('.xr-fold'), 'council: the Local Government and Social Care Ombudsman')
    d = start(pg, "Universal Credit payment is late, DWP said they'd sort it by Monday"); age(pg, d, 50, 1); view(pg, d); pg.click('.xr-fold summary'); wait(pg, 150)
    ok(any('independent-case-examiner' in h for h in hrefs(pg)) and 'Your MP can help at any time' in pg.inner_text('.xr-fold'), 'DWP: the Independent Case Examiner and your MP')
    # 6 parking cases use their own routes
    k = start(pg, "Hackney Council PENALTY CHARGE NOTICE PCN HK11223344 Penalty charge: £130"); age(pg, k, 60, 0)
    ok(view(pg, k) == '', 'parking cases use their own routes, not this')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
