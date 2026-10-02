# v65: adviser pack and export. One page: summary, dates, what happened, what they say, what you say, evidence, questions.
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
def paste(pg, text):
    pg.click('[data-a=panel][data-p=paste]'); wait(pg); pg.fill('#f-paste', text); pg.click('form[data-f=paste] button[type=submit]'); wait(pg)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London', accept_downloads=True)
    ctx.grant_permissions(['clipboard-read', 'clipboard-write'], origin='https://sorted.test')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 200); pg.click('[data-a=anon-start]'); wait(pg)
    T = 'Southwark PCN · SK12345678'
    start(pg, "London Borough of Southwark PENALTY CHARGE NOTICE PCN Number: SK12345678 Vehicle Registration Mark: AB12 CDE Date of contravention: %s Location: Lordship Lane SE22 The penalty charge is £130. If paid within 14 days, reduced to £65." % uk(-6))
    pg.click('.pk-card [data-a=panel][data-p=pkbuild]'); wait(pg)
    pg.check('input[name=bdg-paid]'); pg.fill('textarea[name=bdd-paid]', 'I paid at 10:05 on RingGo'); pg.check('input[name=bde-receipt]'); pg.click('form[data-f=pkbuild] button[type=submit]'); wait(pg)
    pg.click('form[data-f=pkdraft] button[type=submit]'); wait(pg); pg.fill('#f-pkref', 'CH-77'); pg.click('form[data-f=pksent] button[type=submit]'); wait(pg)
    paste(pg, "Date: %s. We do not accept your challenge. Our records show no valid payment was made for this vehicle." % uk(0))
    pg.click('[data-a=rs-yes]'); wait(pg)
    # 1 the page
    ok(pg.locator('[data-a=panel][data-p=pack]').inner_text() == 'Prepare this for an adviser', 'every case offers "Prepare this for an adviser"')
    pg.click('[data-a=panel][data-p=pack]'); wait(pg)
    doc = pg.inner_text('.pack')
    ok('Your case on one page' in doc and 'Nothing is sent' in doc, 'it says it’s made on the phone and nothing is sent')
    ok('Reference\nSK12345678' in doc and 'Stage\nChallenge rejected' in doc and 'Vehicle\nAB12 CDE' in doc, 'case summary from confirmed facts and the stage')
    ok('Important dates' in doc and 'Reduced price may be offered again until' in doc, 'the dates that matter')
    ok('What happened, in order' in doc and 'Challenge sent on' in doc and 'They said no to the challenge' in doc, 'what happened, in order')
    ok('Their reply: “Our records show no valid payment was made for this vehicle”' in doc, 'what the other side says')
    ok('I paid for parking: I paid at 10:05 on RingGo' in doc and 'What I sent: “Dear Southwark Council,' in doc, 'what you say, including what you sent')
    ok('The notice' in doc and 'A payment receipt or app screenshot (I have this)' in doc, 'evidence')
    ok('doesn’t give legal advice' in doc, 'it says Sorted doesn’t give legal advice')
    pg.screenshot(path=HERE + '/tests/out/pack.png', full_page=True)
    # 2 your questions
    pg.fill('#f-packqs', 'Should I pay or wait for the Notice to Owner?\nWhat evidence would help most?'); pg.click('form[data-f=packqs] button[type=submit]'); wait(pg)
    ok(case(pg, T)['packQs'].startswith('Should I pay'), 'your questions are saved with the case')
    # 3 copy
    pg.click('[data-a=pack-copy]'); wait(pg)
    clip = pg.evaluate('navigator.clipboard.readText()')
    ok(clip.startswith('Southwark PCN · SK12345678\nPrepared with Sorted on ') and 'CASE SUMMARY' in clip and 'QUESTIONS I NEED ANSWERED\n- Should I pay or wait for the Notice to Owner?\n- What evidence would help most?' in clip, 'copy gives the whole page as text, with your questions')
    # 4 download
    with pg.expect_download() as dl:
        pg.click('[data-a=pack-download]')
    d = dl.value
    path = d.path(); txt = open(path, encoding='utf-8').read()
    ok(d.suggested_filename == 'Sorted - Southwark PCN · SK12345678.txt' and 'WHAT THE OTHER SIDE SAYS' in txt and 'Our records show' in txt, 'download saves the same page as a text file: %s' % d.suggested_filename)
    # 5 print shows only the page
    pg.emulate_media(media='print'); wait(pg, 200)
    vis = pg.evaluate("[getComputedStyle(document.querySelector('.pack-doc')).visibility, getComputedStyle(document.querySelector('.pack-doc .pack-title')).display, getComputedStyle(document.querySelector('[data-a=pack-copy]').closest('.no-print')).display, getComputedStyle(document.querySelector('main h1')).visibility]")
    ok(vis == ['visible', 'block', 'none', 'hidden'], 'printing shows the page with its title and hides the buttons and the rest: %s' % vis)
    pg.emulate_media(media='screen')
    # 6 an ordinary case
    start(pg, "Currys promised a refund of £89 by Friday, order 445566")
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 150)
    pg.click('[data-a=panel][data-p=pack]'); wait(pg)
    doc = pg.inner_text('.pack')
    ok('Who\nCurrys' in doc and '445566' in doc and 'Currys said: “' in doc and 'In my words: “Currys promised a refund of £89 by Friday' in doc, 'an ordinary case works too: who, reference, what they said, your words')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
