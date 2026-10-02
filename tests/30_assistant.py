# v68: Sorted's assistant. Only when tapped, the case goes to the case-assistant function. Nothing changes unless used.
# Runs against tests/mock.js, whose functions.invoke stands in for the real function, so no model is ever called.
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
def calls(pg): return pg.evaluate("window.__ai||[]")
def start(pg, text):
    pg.goto('https://sorted.test/'); wait(pg, 400)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
    pg.fill('#f-case', text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 450)
    if pg.locator('[data-a=cf-yes]').count(): pg.click('[data-a=cf-yes]'); wait(pg)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 200); pg.click('[data-a=anon-start]'); wait(pg)
    T = 'Southwark PCN · SK12345678'
    start(pg, "London Borough of Southwark PENALTY CHARGE NOTICE PCN Number: SK12345678 Vehicle Registration Mark: AB12 CDE Date of contravention: %s The penalty charge is £130. If paid within 14 days, reduced to £65." % uk(-3))
    n_events = len(case(pg, T)['events'])
    # 1 nothing is sent until you tap, and the first time it says what will happen
    ok(calls(pg) == [], 'nothing is sent to the assistant on its own')
    pg.click('[data-a=ai-explain][data-at=said]'); wait(pg)
    intro = pg.inner_text('.ai-intro')
    ok('sends this case’s details to Anthropic' in intro and 'Nothing is sent until you tap' in intro and 'doesn’t use it to train its models' in intro and 'isn’t legal advice' in intro, 'the first time, it says exactly what is sent, to whom, and the limits')
    ok(calls(pg) == [], 'reading that still sends nothing')
    pg.click('[data-a=ai-ok]'); wait(pg); pg.click('[data-a=ai-explain-go]'); wait(pg, 500)
    c = calls(pg)
    ok(len(c) == 1 and c[0]['name'] == 'case-assistant' and c[0]['body']['task'] == 'explain', 'tapping "Explain it" makes one call')
    ok('Reference: SK12345678' in c[0]['body']['context'] and 'Stage: Notice received' in c[0]['body']['context'] and 'PENALTY CHARGE NOTICE' in c[0]['body']['text'], 'it sends the confirmed facts and the notice')
    out = pg.inner_text('.ai-out')
    ok('Sorted’s assistant' in out.upper() or 'SORTED’S ASSISTANT' in out.upper(), 'the answer is labelled as the assistant')
    ok('[assistant explain]' in out and 'It can be wrong. Check the letter itself. It isn’t legal advice.' in out, 'the answer, and that it can be wrong')
    ok(len(case(pg, T)['events']) == n_events and not case(pg, T).get('sugP'), 'the case doesn’t change')
    pg.click('[data-a=panel][data-p=""]'); wait(pg)
    # 2 ask about this case
    pg.click('[data-a=panel][data-p=aiask]'); wait(pg)
    ok('It won’t tell you what legal step to take' in pg.inner_text('main'), 'ask: it says what it won’t do')
    pg.fill('#f-aiq', 'What does the reduced price mean?'); pg.click('form[data-f=aiask] button[type=submit]'); wait(pg, 500)
    c = calls(pg)[-1]
    ok(c['body']['task'] == 'ask' and c['body']['question'] == 'What does the reduced price mean?' and '[assistant ask]' in pg.inner_text('.ai-out'), 'ask sends your question and shows the answer')
    pg.click('[data-a=panel][data-p=""]'); wait(pg)
    # 3 improve the wording, then use it or keep yours
    pg.click('.pk-card [data-a=panel][data-p=pkbuild]'); wait(pg); pg.check('input[name=bdg-paid]'); pg.click('form[data-f=pkbuild] button[type=submit]'); wait(pg)
    mine = pg.input_value('#f-bdtext')
    pg.click('[data-a=ai-improve]'); wait(pg, 500)
    ok(calls(pg)[-1]['body']['task'] == 'improve' and calls(pg)[-1]['body']['text'] == mine, 'improve sends your draft')
    ok('suggested wording' in pg.inner_text('.ai-improve').lower() and 'Check every fact is still right' in pg.inner_text('.ai-improve'), 'it shows a suggestion, with a reminder to check the facts')
    ok(pg.input_value('#f-bdtext') == mine, 'your draft isn’t changed until you choose')
    pg.click('[data-a=ai-keep]'); wait(pg)
    ok(pg.input_value('#f-bdtext') == mine, '"Keep mine" keeps yours')
    pg.click('[data-a=ai-improve]'); wait(pg, 500); pg.click('[data-a=ai-use]'); wait(pg)
    ok(pg.input_value('#f-bdtext').startswith('Dear Southwark Council,\n\nImproved:'), '"Use this wording" puts it in your draft, for you to edit')
    # 4 when it isn't available, it says so
    pg.evaluate("localStorage.setItem('__aiMode','not_ready')"); pg.click('[data-a=ai-keep]') if pg.locator('[data-a=ai-keep]').count() else None
    pg.click('[data-a=panel][data-p=""] >> nth=-1'); wait(pg)
    pg.click('[data-a=panel][data-p=aiask]'); wait(pg); pg.fill('#f-aiq', 'Hello?'); pg.click('form[data-f=aiask] button[type=submit]'); wait(pg, 500)
    ok('Sorted’s assistant isn’t switched on yet.' in pg.inner_text('main'), 'not switched on yet: it says so')
    pg.evaluate("localStorage.setItem('__aiMode','limit')"); pg.fill('#f-aiq', 'Again?'); pg.click('form[data-f=aiask] button[type=submit]'); wait(pg, 500)
    ok('You’ve used the assistant 40 times today' in pg.inner_text('main'), 'daily limit: it says so')
    pg.evaluate("localStorage.removeItem('__aiMode')")
    # 5 the privacy notice says it
    pg.goto('https://sorted.test/'); wait(pg, 400); pg.click('text=Your data'); wait(pg)
    notice = pg.inner_text('main')
    ok('Anthropic runs Sorted’s assistant. All four are US companies' in notice and 'Sorted’s assistant. If you tap one of the assistant’s buttons' in notice and 'Nothing is sent until you tap.' in notice, 'the privacy notice explains the assistant')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
