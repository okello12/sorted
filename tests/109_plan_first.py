# v144: a plan to check is the person's own next step (found in real use on 8 October 2026).
# "I need to switch my TSB student account to a Spend and Save account", plan "Search up how I can do it": Sorted left
# the party blank, titled it "I need to switch my tsb student account to a…" and opened a message form to "The company".
# Now: TSB (and the other UK banks and common organisations) is known; the title keeps its capitals and never ends on a
# joining word; a plan to look up, search, read, find out, check, verify or compare (not to contact them) becomes the
# person's step, the case and Home lead with it, no message form opens, "Or get a message ready" stays one tap away; once
# checked, "What did you find?" offers the next step, keeping something, contacting them or finishing. A plan to
# contact them still opens the message form.
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/reader'), lambda r: r.fulfill(path=HERE + '/tests/out/reader.html', content_type='text/html'))
    ctx.route(lambda u: u.startswith('https://sorted.test/') and not u.startswith('https://sorted.test/reader'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    cases = lambda: sorted([x['data'] for x in (pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}).get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    main = lambda: pg.inner_text('main')
    def start(text, plan, chip=False):
        pg.locator('.tab129 [data-a=new-case]').click(); wait(pg)
        pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 700)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg, 300)
        ok(pg.locator('form[data-f=baseline]').count() == 1, 'the plan question is asked for “%s”' % text)
        if chip: pg.locator('form[data-f=baseline] [data-a=plan][data-v="%s"]' % plan).click()
        else: pg.fill('#f-baseline', plan)
        wait(pg, 200); pg.locator('form[data-f=baseline] button[type=submit]').click(); wait(pg, 800)
        return cases()[-1]
    # ---- the reader knows the banks ----
    pg.goto('https://sorted.test/reader'); wait(pg, 500)
    names = pg.evaluate("(xs)=>xs.map(function(x){return window.__read.caseFacts(x).party})", ["switch my tsb account", "Barclays blocked my card", "HSBC sent a letter", "Lloyds froze my account", "nationwide mortgage offer", "Nationwide said the offer would come by Friday", "Monzo refunded me", "Santander won't reply", "NatWest app is down", "First Direct called me"])
    ok(names == ['TSB', 'Barclays', 'HSBC', 'Lloyds', '', 'Nationwide', 'Monzo', 'Santander', 'NatWest', 'first direct'], 'banks people name are known (and “nationwide” as an ordinary word is not): %s' % names)
    # ---- the journey ----
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear()")
    pg.goto('https://sorted.test/#start'); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    t = start('I need to switch my tsb student account to a spend and save account', 'Search up how I can do it')
    ok((t.get('facts') or {}).get('party') == 'TSB', 'TSB is the organisation')
    ok('TSB' in t['title'] and 'tsb' not in t['title'] and not t['title'].rstrip('…').rstrip().endswith((' a', ' to', ' the')), 'the title keeps TSB’s capitals and doesn’t end on a joining word: %s' % t['title'])
    mv = [x for x in t.get('moves', []) if x.get('src') == 'plan']
    ok(len(mv) == 1 and mv[0]['status'] == 'open' and mv[0]['what'] == 'Check TSB’s official website or app for how to do this', 'the plan is kept as the person’s step: %s' % [x.get('what') for x in mv])
    ok(not t.get('call') and pg.locator('form[data-f=call]').count() == 0, 'no message form opens and no call is saved')
    m = main()
    ok('Next: check TSB’s official website or app for how to do this' in m and 'The company' not in m and 'Get the call ready' not in m, 'the case leads with the check, never “The company” or the call')
    ok('Your plan was: “Search up how I can do it”' in m, 'what happened says it was their plan, in their words')
    ok(pg.locator('.plan144-alt [data-a=panel][data-p=call]').count() == 1 and 'Or get a message ready for TSB' in m, 'contacting TSB stays one tap away')
    ok('Whose move is it now?' not in m, 'no “Whose move” question: the check is theirs')
    pg.locator('.tab129 [data-a=go-home]').click(); wait(pg, 500)
    hm = main()
    ok('check TSB’s official website' in hm.replace('Check', 'check') and 'The company' not in hm, 'Home names the check as the next step')
    # the alternative still works
    pg.locator('.tab129 [data-a=cases]').click(); wait(pg, 400); pg.locator('.pick125').first.click(); wait(pg, 600)
    pg.locator('.plan144-alt [data-a=panel][data-p=call]').click(); wait(pg, 500)
    ok(pg.locator('form[data-f=call]').count() == 1 and 'TSB' in (pg.input_value('form[data-f=call] input[name=who]') if pg.locator('form[data-f=call] input[name=who]').count() else 'TSB'), 'Or get a message ready opens the message form for TSB')
    pg.locator('[data-a=panel][data-p=""]').first.click() if pg.locator('[data-a=panel][data-p=""]').count() else None; wait(pg, 400)
    pg.locator('[data-a=move-done]').first.click(); wait(pg, 600)
    m = main()
    ok('What did you find?' in m and pg.locator('#plan144 [data-p=move]').count() == 1 and pg.locator('#plan144 [data-p=call]').count() == 1 and 'I need to contact TSB' in m, 'once checked: What did you find?, with a next step, contacting TSB, keeping something or finishing')
    t = cases()[-1]
    ok([x['status'] for x in t['moves']] == ['done'] and not t.get('call') and not t.get('promises'), 'checking changes nothing else')
    pg.reload(); wait(pg, 800)
    m = main()
    ok('What did you find?' in m and pg.locator('form[data-f=call]').count() == 0, 'after a reload the case still asks what they found, not a message form')
    pg.locator('#plan144 [data-p=move]').click(); wait(pg, 500)
    ok(pg.locator('#moveform').count() == 1, 'I know what I need to do next opens their next step')
    # ---- other check plans ----
    t = start('Need to change the address on my driving licence with DVLA', 'find out how to change my address')
    ok([x['what'] for x in t.get('moves', [])] == ['Check DVLA’s official website or app for how to do this'] and pg.locator('form[data-f=call]').count() == 0, '“find out how” is a check for DVLA')
    t = start('Octopus have put my direct debit up to £140 a month', 'compare the tariffs first')
    ok([x['what'] for x in t.get('moves', [])] == ['Compare the options Octopus Energy offers before deciding'] and pg.locator('form[data-f=call]').count() == 0, '“compare the tariffs first” is a comparison, kept as their step')
    t = start('Barclays blocked my card', 'Check what they’ve already said', chip=True)
    ok([x['what'] for x in t.get('moves', [])] == ['Check what Barclays has already said'], 'the “Check what they’ve already said” answer is a check too')
    # ---- a plan to contact them is unchanged ----
    t = start('BT broadband keeps dropping out', 'Contact them', chip=True)
    ok(not t.get('moves') and pg.locator('form[data-f=call]').count() == 1, 'a plan to contact them still opens the message form')
    t = start('Santander froze my account', 'check with them on the phone')
    ok(not t.get('moves'), '“check with them on the phone” is contacting them, not a check')
    t = start('Currys said they would refund my £89 by Friday, order 445566', 'check what they already said in the email')
    ok([(x.get('kind'), x['what']) for x in t.get('moves', []) if x.get('src') == 'plan'] == [('check', 'Check what they already said in the email')], 'v148: with their promise proposed, a plan to check is kept as your step in your words, next to the promise: %s' % [x.get('what') for x in t.get('moves', [])])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
