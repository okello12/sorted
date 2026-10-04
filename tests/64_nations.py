# v108: Moving home for all four nations. A fifth question; the official links for the licence, voting, the GP and the
# council chosen by nation, every link on the page checked by hand; Northern Ireland tells LPS about rates instead of
# the council about council tax; a move with no nation yet is asked once; a step shown for any nation always has a link.
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
LINKS = {
    'en': {'licence': 'https://www.gov.uk/change-address-driving-licence', 'vote': 'https://www.gov.uk/register-to-vote', 'gp': 'https://www.nhs.uk/nhs-services/gps/how-to-register-with-a-gp-surgery/', 'council': 'https://www.gov.uk/find-local-council', 'v5c': 'https://www.gov.uk/change-address-v5c'},
    'wa': {'licence': 'https://www.gov.uk/change-address-driving-licence', 'vote': 'https://www.gov.uk/register-to-vote', 'gp': 'https://111.wales.nhs.uk/localservices/gpfaq/', 'council': 'https://www.gov.uk/find-local-council', 'v5c': 'https://www.gov.uk/change-address-v5c'},
    'sc': {'licence': 'https://www.gov.uk/change-address-driving-licence', 'vote': 'https://www.gov.uk/register-to-vote', 'gp': 'https://www.nhsinform.scot/care-support-and-rights/nhs-services/doctors/registering-with-a-gp-practice/', 'council': 'https://www.gov.uk/find-local-council', 'v5c': 'https://www.gov.uk/change-address-v5c'},
    'ni': {'licence': 'https://www.nidirect.gov.uk/services/change-address-your-driving-licence-online', 'vote': 'https://www.eoni.org.uk/register-to-vote/electoral-registration/', 'gp': 'https://www.nidirect.gov.uk/articles/your-local-doctor-gp', 'council': 'https://www.nidirect.gov.uk/services/create-or-update-your-rate-account', 'v5c': 'https://www.gov.uk/change-address-v5c'},
}
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    moms = lambda: [x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') == 'moment']
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    pg.locator('[data-a=mom-start]').first.evaluate('e=>e.click()'); wait(pg, 600)
    m = pg.inner_text('main')
    ok('Where is the new home?' in m and pg.locator('input[name=mv-nation]').count() == 4 and 'Northern Ireland' in m, 'the move form asks which nation the new home is in, with four choices')
    pg.fill('#mv-date', (datetime.date.today() + datetime.timedelta(days=20)).isoformat()); pg.click('label.chip:has(input[name=mv-car][value=yes])'); pg.click('label.chip:has(input[name=mv-council][value=new])')
    pg.click('form[data-f=mom] button[type=submit]'); wait(pg)
    mv = moms()[0]; mid = mv['id']
    ok('nation' not in mv['ans'] and 'Which nation is the new home in?' in pg.inner_text('main') and pg.locator('.cap108-nation [data-a=mom-edit]').count() == 1, 'with no answer the move asks once, and the answer is not invented')
    links = {h.split('/')[2] for h in pg.locator('main a[href^=http]').evaluate_all('es=>es.map(e=>e.href)')}
    ok('www.gov.uk' in links and 'www.nhs.uk' in links, 'until then it uses the GOV.UK and NHS England pages')
    def hrefs(): return pg.locator('main a[href^=http]').evaluate_all('es=>es.map(e=>e.href)')
    def set_nation(code):
        pg.click('[data-a=mom-edit]'); wait(pg); pg.click('label.chip:has(input[name=mv-nation][value=%s])' % code); pg.click('form[data-f=mom] button[type=submit]'); wait(pg, 600)
    for code, name in [('ni', 'Northern Ireland'), ('sc', 'Scotland'), ('wa', 'Wales'), ('en', 'England')]:
        set_nation(code); m = pg.inner_text('main'); hs = hrefs()
        ok(moms()[0]['ans'].get('nation') == code and name in m and 'Which nation' not in m, '%s is saved and shown, and the question goes' % name)
        want = LINKS[code]
        missing = [k for k, u in want.items() if u not in hs]
        wrong = [u for o, L in LINKS.items() if o != code for k, u in L.items() if u != want[k] and u in hs]
        ok(not missing and not wrong, '%s: every official link is that nation’s (missing %s, wrong %s)' % (name, missing, wrong))
        own = pg.locator('.cap103-own').evaluate_all('es=>es.map(e=>({t:e.innerText,a:e.querySelectorAll("a[href]").length}))')
        linked = [x for x in own if any(w in x['t'] for w in ('licence', 'log book', 'vote', 'GP', 'council', 'Land & Property'))]
        ok(linked and all(x['a'] >= 1 for x in linked), '%s: every official step shown has a link' % name)
        if code == 'ni':
            ok('Tell Land & Property Services you’ve moved' in m and 'rates, not council tax' in m and 'council tax' not in m.replace('rates, not council tax', '') and 'DVA can fine you' in m, 'Northern Ireland: rates with LPS instead of council tax, and DVA not DVLA')
        else:
            ok('Land & Property' not in m and 'DVLA can fine you' in m, '%s: council tax and DVLA' % name)
    pg.evaluate("document.querySelector('details.cap104-share').open=true"); pg.click('[data-a=mom-share]'); wait(pg, 600)
    card = json.dumps([s for s in dbj().get('shares', []) if s['task_id'] == mid][0]['card'], ensure_ascii=False)
    ok('Tell your old and new council' in card and 'Land & Property' not in card, 'the shared card follows the nation too')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'nothing scrolls sideways')
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
