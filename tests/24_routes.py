# v62: official routes, release 3. The right official pages for the kind of notice, the stage and the region.
import os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=350): pg.wait_for_timeout(ms)
T0 = datetime.date.today()
def uk(n): return (T0 + datetime.timedelta(days=n)).strftime('%d/%m/%Y')
def tasks(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks.map(y=>y.data)")
def case(pg, title): return next((x for x in tasks(pg) if x['title'] == title), None)
def start(pg, text):
    pg.goto('https://sorted.test/'); wait(pg, 400)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
    pg.fill('#f-case', text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 450)
    if pg.locator('[data-a=cf-yes]').count(): pg.click('[data-a=cf-yes]'); wait(pg)
import re
def links(pg): return {a.get_attribute('href'): re.sub(r'\s*\(opens a new tab\)', '', a.inner_text()).strip() for a in pg.locator('.rt-routes a.rt-link').all()}
def reject(pg):
    cid = sorted(tasks(pg), key=lambda x: x.get('created') or '')[-1]['id']
    pg.click('[data-a=panel][data-p=pksent]'); wait(pg); pg.click('form[data-f=pksent] button[type=submit]'); wait(pg)
    pg.evaluate("""()=>{var db=JSON.parse(localStorage.getItem('__mockdb'));db.tasks.forEach(y=>(y.data.promises||[]).forEach(q=>{if(q.status==='open'&&q.src==='parking'){q.status='kept'}}));localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}""")
    pg.goto('https://sorted.test/'); wait(pg, 500); pg.locator('[data-a=open][data-id="%s"]' % cid).first.click(); wait(pg)
    pg.click('[data-a=panel][data-p=pkrej]'); wait(pg); pg.click('form[data-f=pkrej] button[type=submit]'); wait(pg)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 200); pg.click('[data-a=anon-start]'); wait(pg)
    # 1 a London council ticket
    start(pg, "London Borough of Southwark PENALTY CHARGE NOTICE PCN Number: SK12345678 Vehicle Registration Mark: AB12 CDE Date of contravention: %s The penalty charge is £130. If paid within 14 days, reduced to £65." % uk(-2))
    L = links(pg)
    ok(L.get('https://www.gov.uk/find-local-council') == 'Pay or challenge on Southwark Council’s website', 'the council’s own site, found through GOV.UK')
    ok('https://www.gov.uk/parking-tickets/challenging-a-ticket' in L and any('citizensadvice.org.uk' in u for u in L), 'the official guide and free advice')
    ok(not any('tribunal' in u.lower() for u in L), 'no tribunal before there is anything to appeal: %s' % list(L))
    ok(all(a.get_attribute('target') == '_blank' and 'noopener' in a.get_attribute('rel') for a in pg.locator('.rt-routes a').all()), 'links open safely in a new tab')
    ok('checked by a person on 2 Oct 2026' in pg.inner_text('.rt-routes') and 'doesn’t pay or send anything for you' in pg.inner_text('.rt-routes'), 'says when they were checked and what Sorted doesn’t do')
    pg.screenshot(path=HERE + '/tests/out/routes_notice.png', full_page=True)
    # 2 an informal challenge turned down: still the council, not the tribunal
    reject(pg)
    L = links(pg)
    ok('https://www.gov.uk/find-local-council' in L and not any('londontribunals' in u for u in L), 'an informal challenge turned down: back to the council, no tribunal yet')
    # 3 Notice to Owner, formal challenge turned down: the London tribunal
    T = 'Southwark PCN · SK12345678'
    pg.click('[data-a=panel][data-p=paste]'); wait(pg)
    pg.fill('#f-paste', 'London Borough of Southwark NOTICE TO OWNER PCN Number: SK12345678 Date of notice: %s The penalty charge of £130 has not been paid.' % uk(0))
    pg.click('form[data-f=paste] button[type=submit]'); wait(pg); pg.click('[data-a=cf-yes]'); wait(pg)
    reject(pg)
    L = links(pg)
    ok('https://www.londontribunals.gov.uk/' in L and 'https://www.trafficpenaltytribunal.gov.uk/' not in L, 'formal challenge turned down in London: London Tribunals, not the Traffic Penalty Tribunal')
    ok('https://www.gov.uk/appeal-against-a-penalty-charge-notice' in L, 'and the GOV.UK appeal page')
    ok(pg.locator('.rt-else').count() == 1 and 'generalregulatorychamber.scot' in pg.inner_html('.rt-else') and 'justice-ni.gov.uk' in pg.inner_html('.rt-else'), 'Scotland and Northern Ireland folded away underneath')
    # 4 outside London
    start(pg, "Bristol City Council PENALTY CHARGE NOTICE PCN Number: BR12345678 Date of contravention: %s Penalty charge: £70" % uk(-1))
    pg.click('[data-a=panel][data-p=paste]'); wait(pg)
    pg.fill('#f-paste', 'Bristol City Council NOTICE TO OWNER PCN Number: BR12345678 Date of notice: %s' % uk(0)); pg.click('form[data-f=paste] button[type=submit]'); wait(pg); pg.click('[data-a=cf-yes]'); wait(pg)
    reject(pg)
    L = links(pg)
    ok('https://www.trafficpenaltytribunal.gov.uk/' in L and 'https://www.londontribunals.gov.uk/' not in L, 'outside London: the Traffic Penalty Tribunal')
    # 5 TfL
    start(pg, "Transport for London Penalty Charge Notice - Bus Lane. PCN number: LB12345678 Date: %s Penalty charge £160" % uk(-1))
    L = links(pg)
    ok('https://tfl.gov.uk/modes/driving/red-routes/penalty-charge-notices/pay-a-pcn' in L and 'https://www.gov.uk/find-local-council' not in L, 'TfL: TfL’s own page, not a council search')
    # 6 private, POPLA named on the notice
    start(pg, "ParkingEye Ltd PARKING CHARGE NOTICE Reference number: 1234567 Date of event: %s Parking charge amount: £100. Appeals: POPLA." % uk(-1))
    ok('Appeal to ParkingEye first' in pg.inner_text('.rt-routes') and not any('popla' in u for u in links(pg)), 'private: the company first, the independent service later')
    reject(pg)
    L = links(pg)
    ok('https://www.popla.co.uk/how-to-appeal' in L and 'https://www.theias.org/appeal' not in L, 'private, turned down: POPLA, because the notice names it')
    # 7 not a parking case: nothing
    start(pg, "Currys refund hasn't arrived, order 445566")
    ok(pg.locator('.rt-routes').count() == 0, 'an ordinary case has no routes block')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
