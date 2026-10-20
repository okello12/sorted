# v173: a driving licence is not always a renewal. From Baldwin's case of 20 October 2026: his own step said "apply for
# it", but the licence record only knew an expiry, so the case led with "Expired Saturday 25 April" and "Renew on GOV.UK".
# Reapplying after a ban and after a health condition are different GOV.UK pages. Sorted asks once, in the person's
# words' light, and shows the page for the answer. Nothing is assumed from a hint alone.
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
BAN = 'https://www.gov.uk/reapply-licence-revoked'; HEALTH = 'https://www.gov.uk/reapply-driving-licence-health-condition'; RENEW = 'https://www.gov.uk/renew-driving-licence'
def seed(pg, cases):
    pg.evaluate("""(cases)=>{var db={tasks:[],shares:[],reminders:[],helpers:[],inbound_items:[],pilot_events:[],case_notes:[]};
      cases.forEach(function(t){t.mode='renew';t.board='yours';t.promises=t.promises||[];t.moves=t.moves||[];t.call=null;t.fix=null;t.outcome='';t.baseline='Not sure yet';t.created='2026-09-28T11:50:00.000Z';t.updatedAt='2026-09-30T08:10:00.000Z';t.safety=false;t.sharedAt=null;t.rev=1;
        t.events=t.events||[{at:'2026-09-28T11:55:00.000Z',label:'Renewing: Driving licence.'}];db.tasks.push({id:t.id,user_id:'u-me',data:t})});
      localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}""", cases)
def case(pg, cid): return [x['data'] for x in pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))")['tasks'] if x['data']['id'] == cid][0]
def opencase(pg, cid): pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700)
def state(pg): return pg.inner_text('.case56-renew-state')
def official(pg): return pg.inner_text('.case56-official')
def links(pg): return pg.evaluate("Array.from(document.querySelectorAll('.case56-official a[href]')).map(a=>a.getAttribute('href'))")
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')")
    pg.evaluate("localStorage.setItem('__mocksession', %s)" % json.dumps(json.dumps({'user': {'id': 'u-me', 'email': 'me@example.com'}})))
    move = {'id': 'm1', 'what': 'Remind to apply for it', 'dueAt': '2026-10-24T22:59:59.000Z', 'allDay': True, 'by': True, 'status': 'open', 'loggedAt': '2026-09-28T12:00:00.000Z'}
    seed(pg, [
        {'id': 'lic-apply', 'title': 'My driving licence', 'said': 'My driving licence', 'renew': {'kind': 'licence', 'step': 'done', 'expiry': '2026-04-25', 'applied': False, 'provider': 'DVLA', 'how': 'self'}, 'moves': [dict(move)]},
        {'id': 'lic-ban', 'title': 'Driving licence after my ban', 'said': 'I was banned from driving for 12 months and need to get my licence back', 'renew': {'kind': 'licence', 'step': 'done', 'expiry': '2026-04-25', 'applied': False, 'provider': 'DVLA', 'how': 'self'}},
        {'id': 'lic-plain', 'title': 'Renew my driving licence', 'said': 'Renew my driving licence', 'renew': {'kind': 'licence', 'step': 'done', 'expiry': '2026-04-25', 'applied': False, 'provider': 'DVLA', 'how': 'self'}},
        {'id': 'lic-soon', 'title': 'Driving licence', 'said': 'My driving licence runs out next year', 'renew': {'kind': 'licence', 'step': 'done', 'expiry': '2027-06-01', 'applied': False, 'provider': 'DVLA', 'how': 'self'}},
    ])
    pg.goto('https://sorted.test/'); wait(pg, 700)
    # 1 Baldwin's case: an expired licence whose own step says "apply" is asked about, not called a renewal
    opencase(pg, 'lic-apply'); st = state(pg); of = official(pg)
    ok('Check which page fits' in st and 'Expired' not in st and 'You gave Saturday 25 April as the date.' in st, 'an expired licence with "apply for it" is not called expired or a renewal: %s' % st.replace('\n', ' | '))
    ok('Why do you need a licence?' in of and 'Renew on GOV.UK' not in of and links(pg) == [], 'the official card asks which page fits and shows no link yet')
    chips = pg.locator('.lic173-ask .chip')
    ok(chips.count() == 3 and chips.nth(0).inner_text() == 'It ran out' and pg.locator('.lic173-ask .chip[aria-pressed=true]').count() == 0, 'three choices, nothing chosen for the person')
    ok(pg.locator('.case56-next').count() == 1 and 'Remind to apply for it' in pg.inner_text('.case56-next'), 'the person’s own step is untouched')
    ok(case(pg, 'lic-apply')['renew'].get('why') is None, 'nothing is saved before a tap')
    pg.locator('.lic173-ask .chip[data-v=ban]').click(); wait(pg, 600); st = state(pg); of = official(pg); t = case(pg, 'lic-apply')
    ok(t['renew']['why'] == 'ban' and any('after a driving ban' in e['label'] and 'Your choice' in e['label'] for e in t['events']), 'the tap saves the reason with a history line')
    ok('After a driving ban' in st and 'Expired' not in st, 'the state says after a driving ban: %s' % st.replace('\n', ' | '))
    ok('Reapply on GOV.UK' in of and links(pg) == [BAN] and 'D27' in of and 'can’t drive until the ban has ended' in of and 'Renew on GOV.UK' not in of, 'the route is the reapply-after-a-ban page')
    ok(pg.locator('.case56-official [data-p=renewed]').inner_text() == 'I’ve got it back' and pg.locator('.case56-official [data-a=applied]').count() == 0, 'the actions fit (the open step already says apply)')
    pg.reload(); wait(pg, 700)
    if pg.locator('.case56-official').count() == 0: opencase(pg, 'lic-apply')
    ok(links(pg) == [BAN], 'the reason is kept after a reload')
    pg.click('.case56-official [data-a=lic173-ask]'); wait(pg)
    ok(pg.locator('.lic173-ask .chip[aria-pressed=true][data-v=ban]').count() == 1, '"Not right?" reopens the question with the current answer marked')
    pg.locator('.lic173-ask .chip[data-v=health]').click(); wait(pg, 600)
    ok(links(pg) == [HEALTH] and 'After a health condition' in state(pg) and 'doctor' in official(pg) and case(pg, 'lic-apply')['renew']['why'] == 'health', 'changed to the health-condition page')
    pg.click('.case56-official [data-a=lic173-ask]'); wait(pg); pg.locator('.lic173-ask .chip[data-v=expired]').click(); wait(pg, 600)
    ok(links(pg)[0] == RENEW and 'Renew on GOV.UK' in official(pg) and 'Expired Saturday 25 April' in state(pg) and case(pg, 'lic-apply')['renew']['why'] == 'expired', '"It ran out" gives the ordinary renewal back')
    # 2 words about a ban: the ban choice leads and Sorted says why it asks
    opencase(pg, 'lic-ban'); of = official(pg)
    ok('Your words mention a ban' in of and pg.locator('.lic173-ask .chip').nth(0).get_attribute('data-v') == 'ban' and links(pg) == [] and 'Check which page fits' in state(pg), 'a ban in the words puts that choice first and still asks')
    ok(case(pg, 'lic-ban')['renew'].get('why') is None, 'a hint saves nothing')
    # 3 a plain renewal is as it was, with one quiet way to the question
    opencase(pg, 'lic-plain'); st = state(pg); of = official(pg)
    ok('Expired Saturday 25 April' in st and 'Renew on GOV.UK' in of and links(pg)[0] == RENEW and 'Why do you need a licence?' not in of, 'a plain expired renewal is unchanged')
    ok(pg.locator('.case56-official [data-a=lic173-ask]').count() == 1 and 'Taken away after a ban or for a health condition?' in of, 'with one quiet link to the question')
    pg.click('.case56-official [data-a=lic173-ask]'); wait(pg)
    ok('Renewing, reapplying after a ban and reapplying after a health condition are different GOV.UK pages.' in official(pg) and pg.locator('.lic173-ask .chip').nth(0).get_attribute('data-v') == 'expired', 'the link opens the question with "It ran out" first')
    # 4 a licence still in date is untouched
    opencase(pg, 'lic-soon'); st = state(pg)
    ok('Start by' in st and 'Nothing to do yet' in st and 'Why do you need a licence?' not in official(pg), 'an upcoming renewal is untouched')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'nothing scrolls sideways')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
