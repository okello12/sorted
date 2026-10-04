# v126 (the remaining-pages review, public pages). "Start with your problem" carries through sign-in to the box for
# your own words; a common problem ("Parking notice") carries its own start; "See an example" goes to the example on
# the page; Browse more opens the full catalogue. Contact shows the address in a field with "Copy the address", which
# copies it, and says what to do if no email app opens. Privacy points at Account and Settings, never "Your data". Terms
# describe all of Sorted (promises, your own tasks, documents, renewals). About leads with why Sorted exists. How it
# works is shorter and keeps the example. Help puts its questions first, in four groups. Nothing scrolls sideways at 320px.
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.grant_permissions(['clipboard-read', 'clipboard-write'], origin='https://sorted.test')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    main = lambda: pg.inner_text('main')
    fresh = lambda: (pg.goto('https://sorted.test/'), pg.evaluate("localStorage.clear();sessionStorage.clear()"), pg.goto('https://sorted.test/'), wait(pg, 700))
    # ---- 1. Start with your problem: through sign-in to your own words ----
    fresh()
    pg.click('.hero .btn.primary'); wait(pg, 500)
    ok(pg.locator('[data-a=anon-start]').count() == 1, '“Start with your problem” goes to starting, without an account if you like')
    pg.click('[data-a=anon-start]'); wait(pg, 900); m = main()
    ok(pg.locator('#f-case').count() == 1 and pg.locator('#cap82-start').count() == 0 and 'What do you need to sort out?' in m, 'after starting you are in the box for your own words, not another chooser')
    # ---- 2. a common problem carries its own start ----
    fresh()
    pg.click('.hero-quick [data-cap95=parking]'); wait(pg, 500)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 900)
    m = main()
    ok(pg.locator('#cap82-start').count() == 0 and ('Start with your document' in m or 'parking' in m.lower()), '“Parking notice” carries through to its own start (%s)' % m[:80].replace('\n', ' '))
    # ---- 3. See an example, Browse more ----
    fresh()
    pg.click('.hero-seeex'); wait(pg, 400)
    y = pg.evaluate("document.querySelector('#example126').getBoundingClientRect().top")
    ok(-5 < y < 200, '“See an example” takes you to the example on the page (%d)' % y)
    pg.click('#browse126 > summary'); wait(pg, 300)
    ok(pg.locator('#cap82-landing .cap82-card:visible').count() == 6 and pg.locator('#cap82-landing [data-cap95]:visible').count() >= 10, 'Browse more opens the six ways in and the examples')
    # ---- 4. Contact ----
    pg.goto('https://sorted.test/#contact'); wait(pg, 500); m = main()
    ok(pg.input_value('#contact-addr') == 'kofiniiakwei@gmail.com' and pg.locator('[data-a=copy-contact]').count() == 1 and 'doesn’t open an email app, copy the address' in m, 'Contact shows the address in a field with a copy button and says what to do if no email app opens')
    pg.click('[data-a=copy-contact]'); wait(pg, 300)
    ok(pg.evaluate('navigator.clipboard.readText()') == 'kofiniiakwei@gmail.com', '“Copy the address” copies it')
    # ---- 5. Privacy, Terms, About, How it works, Help ----
    pg.goto('https://sorted.test/#privacy'); wait(pg, 500); m = main()
    ok('Your data”' not in m and '“Your data' not in m and 'in Account, under Settings' in m and '“Download my cases” and “Delete my account”' in m, 'Privacy points at Account and Settings, not “Your data”')
    pg.goto('https://sorted.test/#terms'); wait(pg, 500); m = main()
    ok('things you need to do yourself' in m and 'parking notices' in m and 'renewals' in m and 'A place to keep track of what someone else has promised you' not in m, 'Terms describe all of Sorted')
    pg.goto('https://sorted.test/#about'); wait(pg, 500); m = main()
    ok(m.index('Why it exists.') < m.index('Who runs it.') and 'Tokio' not in m and 'TMHCC' not in m and '@gmail' not in m.split('Contact')[0], 'About leads with why Sorted exists, then a short founder introduction, with no employer or personal email')
    pg.goto('https://sorted.test/#how'); wait(pg, 500); m = main()
    ok(pg.locator('.how120 li').count() == 3 and len(pg.inner_text('.how120')) < 400 and 'Example' in m or 'EXAMPLE' in m, 'How it works: three short steps (%d characters) and the example' % len(pg.inner_text('.how120')))
    pg.goto('https://sorted.test/#help'); wait(pg, 500); m = main()
    ok(m.index('Questions people ask') < m.index('How Sorted works, with an example') and pg.locator('.how120').count() == 0 and pg.locator('.acct112-q').count() == 29, 'Help: the 29 questions first, How it works only as a link')
    # ---- 6. narrow screens ----
    pg.set_viewport_size({'width': 320, 'height': 700})
    for h in ('', '#help', '#contact', '#about'):
        pg.goto('https://sorted.test/' + h); wait(pg, 500)
        ok(pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth"), 'nothing scrolls sideways at 320px: %s' % (h or 'landing'))
    ok(not errs, 'no page errors: %s' % errs)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
