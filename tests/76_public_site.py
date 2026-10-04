# v120 (docs/PLAN.md Phase 4): the public site and Help say one thing, and only what Sorted does. One description on
# the landing page, on Home for a newcomer and in Help; "How it works" in three steps with one worked example
# labelled Example; separate pages with stable addresses and a date (about, how, help, privacy, terms, contact), each
# reachable from the footer; the hero and footer carry no wrong wording; the full FAQ, with the answers that matter
# pinned; and the signed-in Help & About carries the same steps, example, contact and date.
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
D1 = 'Keep everyday admin moving.'
D2 = 'Parking notices, delayed refunds, repairs and confusing letters.'
WRONG = ['nobody running Sorted reads', 'Nobody running Sorted reads', '(30 without an email)', '30 if you haven’t added an email', 'research pilot', 'step records']
PAGES = {'#about': ['About Sorted', 'Baldwin Thompson-Addo', 'About updated 4 October 2026'], '#how': ['How Sorted works', 'Tell Sorted what is happening.', 'Example', 'How it works updated 4 October 2026'], '#help': ['Help', 'Questions people ask', 'Help updated 4 October 2026'], '#privacy': ['How Sorted handles your data', 'Who runs it.', 'The privacy notice updated 4 October 2026'], '#terms': ['Terms of use', 'Version 1, 4 October 2026'], '#contact': ['Contact', 'kofiniiakwei@gmail.com', 'Report a problem', 'Contact updated 4 October 2026']}
FAQ_MUST = {
  'What does Sorted cost?': 'Sorted is free to use.',
  'Can I use Sorted without an internet connection?': 'It needs a connection to load.',
  'Where are my cases saved?': 'On Sorted’s servers in London',
  'What if they haven’t given me a date?': 'Sorted won’t invent one.',
  'Can I change or stop a reminder?': 'Turning reminders off never deletes the case.',
  'What information should I avoid adding?': 'Sorted never reads account, card, National Insurance or passport numbers as references.',
  'Does Sorted deal with everything for me?': 'It doesn’t contact organisations, make payments, or submit claims or challenges for you.',
  'Can I use Sorted for a parking notice (PCN)?': 'It never decides whether a challenge will succeed.',
  'How do I get help or report a problem?': 'You’ll get a reply within 10 working days.',
}
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.goto('https://sorted.test/'); wait(pg, 600)
    body = pg.inner_text('body')
    ok(D1.lower() in body.lower() and D2 in body, 'the landing page carries the description')
    ok('See an example' in body and pg.locator('main a[href="#how"]').count() >= 1 and pg.locator('footer a[href="#how"]').count() == 1, 'the landing page points at the example and How it works')
    for w in WRONG: ok(w not in body, 'landing: gone, “%s”' % w)
    ok(all(pg.locator('footer a[href="%s"]' % h).count() == 1 for h in PAGES), 'the footer links to every page')
    for h, must in PAGES.items():
        pg.goto('https://sorted.test/' + h); wait(pg, 500); m = pg.inner_text('main')
        ok(all(x in m for x in must) and pg.locator('main h1').count() == 1, 'page %s: its heading, content and date (%s)' % (h, [x for x in must if x not in m]))
        for w in WRONG: ok(w not in m, '%s: gone, “%s”' % (h, w))
        ok(not any(pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth") for _ in [0]), '%s fits the screen' % h)
    pg.goto('https://sorted.test/#how'); wait(pg, 500); m = pg.inner_text('main')
    ok(pg.locator('.how120 li').count() == 3 and 'Choose the next step.' in m and 'Keep it moving.' in m, 'three steps')
    ok('Example' in m and 'Currys said my refund of £89 would arrive by Friday 9 October, order 445566' in m and 'Sample details, labelled Example.' in m and 'Has the money arrived?' in m, 'one worked example, labelled')
    pg.goto('https://sorted.test/#help'); wait(pg, 500)
    qs = pg.locator('.acct112-q summary').all_inner_texts()
    ok(len(qs) == 29 and qs[0] == 'What is Sorted for?' and qs[-1] == 'How do I get help or report a problem?', 'the full FAQ: %d questions' % len(qs))
    pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); m = pg.inner_text('main')
    for q, a in FAQ_MUST.items(): ok(q in qs and a in m, 'FAQ pins: %s' % q)
    ok('Sorted keeps everyday admin moving.' in m and m.index('Questions people ask') < m.index('How Sorted works, with an example') and [h.strip() for h in pg.locator('.help126-g').all_inner_texts()] == ['Starting', 'Documents', 'Reminders', 'Account and your data'], 'Help: the questions first, in four groups, with the same description (v126)')
    # a newcomer's Home: the same description before the routes
    pg.goto('https://sorted.test/#start'); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 800); m = pg.inner_text('main')
    ok(D1 in m and D2 in m, 'a newcomer’s Home carries the description')
    # signed in: Help & About has the steps, the example, contact and the date
    pg.locator('.tab129 [data-a=data]').first.click(); wait(pg, 500); pg.click('.acct112-nav [data-v=help]'); wait(pg, 500); pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); m = pg.inner_text('main')
    ok('How it works' in m and pg.locator('.how120 li').count() == 3 and 'Example' in m and 'Contact and problems' in m and 'Help & About updated 4 October 2026' in m and len(pg.locator('.acct112-q').all_inner_texts()) == 29, 'signed in: Help & About has the same steps, example, contact, questions and date')
    for w in WRONG: ok(w not in m, 'help & about: gone, “%s”' % w)
    ok(not errs, 'no page errors')
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
