# v108: automated accessibility checks with axe-core (served from tests/node_modules, the pinned version) on the screens
# people use most, in light and dark mode: no serious or critical violations; moderate and minor ones are printed as
# FINDINGs. Then 200% text: Home and a case at 390px with the root font doubled must not scroll sideways, and every
# control must still be at least 44px tall. This supplements, and never replaces, a real screen reader on a real phone.
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; findings = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def finding(m): findings.append(m); print('FINDING ' + m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
AXE = open(HERE + '/tests/node_modules/axe-core/axe.min.js', encoding='utf8').read()
def axe(pg, label):
    pg.evaluate(AXE)
    r = pg.evaluate("async()=>{var r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','best-practice']}});return r.violations.map(v=>({id:v.id,impact:v.impact,help:v.help,nodes:v.nodes.slice(0,3).map(x=>x.target.join(' '))}))}")
    bad = [v for v in r if v['impact'] in ('serious', 'critical')]
    mild = [v for v in r if v['impact'] not in ('serious', 'critical')]
    ok(not bad, '%s: no serious or critical accessibility violations %s' % (label, json.dumps(bad, ensure_ascii=False)[:600]))
    # v115: the two moderate findings from v114 (no h1 on a guided start, h3 after h1 on the promise card) are fixed and must stay fixed
    ok(not [v for v in mild if v['id'] in ('page-has-heading-one', 'heading-order')], '%s: headings in order, with an h1' % label)
    for v in mild: finding('%s: %s (%s) %s' % (label, v['id'], v['impact'], v['nodes'][:2]))
with sync_playwright() as p:
    b = p.chromium.launch()
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London', color_scheme=scheme)
        ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
        ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
        pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 400)
        axe(pg, scheme + ': landing')
        if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
        axe(pg, scheme + ': first visit, the chooser')
        pg.locator('[data-cap82=promise]').first.evaluate('e=>e.click()'); wait(pg, 400)
        axe(pg, scheme + ': a guided start')
        pg.fill('#gi-who', 'Sky'); pg.fill('#gi-what', 'send an engineer Tuesday between 8 and 12, ref AB123'); pg.click('form[data-f=gi] button[type=submit]'); wait(pg, 600)
        if pg.locator('form[data-f=baseline]').count(): axe(pg, scheme + ': the baseline question'); pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        axe(pg, scheme + ': the promise card')
        if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
        axe(pg, scheme + ': a case, waiting')
        cid = [x['data'] for x in dbj().get('tasks', [])][0]['id']
        if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
        pg.locator('[data-a=panel][data-p=paste]').first.evaluate('e=>e.click()'); wait(pg, 300); axe(pg, scheme + ': the paste panel')
        pg.fill('#f-paste', "Sorry, it wasn't Sky, it was Virgin Media"); pg.click('form[data-f=paste] button[type=submit]'); wait(pg, 600); axe(pg, scheme + ': a correction card')
        pg.click('[data-a=corr-no]'); wait(pg, 300)
        if pg.locator('[data-a=panel][data-p=call]').count(): pg.locator('[data-a=panel][data-p=call]').first.evaluate('e=>e.click()'); wait(pg, 400); axe(pg, scheme + ': the chase panel')
        pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600)
        pg.locator('[data-a=panel][data-p=pack]').first.evaluate('e=>e.click()'); wait(pg, 400); axe(pg, scheme + ': the adviser pack')
        pg.goto('https://sorted.test/'); wait(pg, 600); axe(pg, scheme + ': Home with a case')
        pg.locator('[data-a=mom-start]').first.evaluate('e=>e.click()'); wait(pg, 500); axe(pg, scheme + ': the move form')
        pg.fill('#mv-date', (datetime.date.today() + datetime.timedelta(days=20)).isoformat()); pg.click('label.chip:has(input[name=mv-tenure][value=rent])'); pg.click('form[data-f=mom] button[type=submit]'); wait(pg, 600)
        axe(pg, scheme + ': Moving home')
        pg.evaluate("document.querySelector('details.cap104-share').open=true"); pg.click('[data-a=mom-share]'); wait(pg, 600)
        tok = dbj().get('shares', [])[0]['token']
        v = ctx.new_page(); v.goto('https://sorted.test/?share=%s' % tok); wait(v, 700); axe(v, scheme + ': a shared move'); v.close()
        # 200% text
        for url, label in [('https://sorted.test/', 'Home'), ('https://sorted.test/?task=%s' % cid, 'a case')]:
            pg.goto(url); wait(pg, 600); pg.evaluate("document.documentElement.style.fontSize='200%'"); wait(pg, 300)
            ok(pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth+1"), '%s: 200%% text at 390px does not scroll sideways (%s)' % (label, scheme))
            small = pg.evaluate("[...document.querySelectorAll('main button,main a.btn,main .chip')].filter(e=>e.offsetParent&&e.getBoundingClientRect().height<44).map(e=>e.className+':'+e.textContent.trim().slice(0,30))")
            ok(not small, '%s: at 200%% every control is at least 44px tall (%s): %s' % (label, scheme, small[:5]))
            pg.evaluate("document.documentElement.style.fontSize=''")
        ctx.close()
    print('CHECKS', n[0]); print('FINDINGS', len(findings))
    b.close()
print('ERRORS', errs); print('FAILS', fails)
