# v158: a strict script policy. vercel.json's script-src lists the SHA-256 hash of each of the page's inline scripts
# (tools/csp_hashes.js writes them) instead of 'unsafe-inline', so an injected script or inline handler never runs.
# This test checks the hashes are current for the built page, no inline handler is left in the page, every screen a
# person reaches (landing, Help, Home, a case with its panels, Cases, More, the shared page) draws under the policy
# with nothing refused, and that an injected inline script and an injected handler are refused.
import os, sys, json, subprocess, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import ok, wait, errs, fails, finish, HERE, day, long
from playwright.sync_api import sync_playwright

r = subprocess.run(['node', HERE + '/tools/csp_hashes.js', '--check'], capture_output=True, text=True)
ok(r.returncode == 0, 'vercel.json lists the hashes of this page’s inline scripts (%s)' % r.stdout.strip())
V = json.load(open(HERE + '/vercel.json'))
CSP = [x['value'] for h in V['headers'] for x in h['headers'] if x['key'] == 'Content-Security-Policy'][0]
SS = [d for d in CSP.split('; ') if d.startswith('script-src')][0]
ok("'unsafe-inline'" not in SS and SS.count("'sha256-") >= 5, 'script-src has no unsafe-inline, only Sorted’s own scripts by hash')
PAGE = open(HERE + '/public/index.html', encoding='utf8').read()
ok(not re.search(r'\son(?:error|load|click|submit|input|change|focus|blur|mouse\w+|key\w+)=["\\\']', PAGE), 'no inline event handler anywhere in the page')

with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/public/fonts/' + r.request.url.split('/fonts/')[1], content_type='font/woff2') if '/fonts/' in r.request.url else (r.fulfill(body='', status=404) if '/art/' in r.request.url else r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html', headers={'Content-Security-Policy': CSP})))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); refused = []
    pg.on('console', lambda m: refused.append(m.text) if 'Content Security Policy' in m.text or 'Refused to' in m.text else None)
    pg.goto('https://sorted.test/'); wait(pg, 800)
    ok(pg.locator('.hero126').count() == 1, 'the landing page draws under the policy')
    ok(pg.locator('img.art').count() == 0, 'a missing illustration still removes itself, without an inline handler')
    for h in ('#help', '#about', '#privacy'): pg.goto('https://sorted.test/' + h); wait(pg, 400)
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear()"); pg.reload(); wait(pg, 500); pg.click('[data-a=anon-start]'); wait(pg, 900)
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.fill('#f-case', 'Currys said the refund of £40 would be in my account by %s, order 556677' % long(day(4))); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 900)
    if pg.locator('form[data-f=baseline]').count(): pg.click('[data-a=plan-skip]'); wait(pg, 600)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 900)
    ok('Currys' in pg.inner_text('main'), 'a case is made and shown under the policy')
    for panel in ('paste', 'call', 'pack', 'summary137', 'correct'):
        if pg.locator('[data-a=panel][data-p=%s]' % panel).count(): pg.locator('[data-a=panel][data-p=%s]' % panel).first.evaluate('e=>e.click()'); wait(pg, 400)
    for tab in ('go-home', 'cases', 'data'): pg.locator('.tab129 [data-a=%s]' % tab).click(); wait(pg, 500)
    ok(not refused, 'nothing the app does is refused: %s' % refused[:3])
    # what the policy is for: an injected script or handler does not run
    pg.evaluate("""()=>{window.__inj=0;var s=document.createElement('script');s.textContent='window.__inj=1';document.body.appendChild(s);
      var d=document.createElement('div');d.innerHTML='<img src=x onerror="window.__inj=2">';document.body.appendChild(d)}"""); wait(pg, 600)
    ok(pg.evaluate('window.__inj') == 0, 'an injected inline script and an injected onerror handler are refused')
    ctx.close(); b.close()
finish()
