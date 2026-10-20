# v171, from Baldwin's walk on 20 October 2026: "From hmrc" typed into the document door, then Start twice, made an
# HMRC case with nothing in it and a message form. Now the door keeps asking for the letter (a photo, or a few words)
# and creates nothing until one is there. The general box still carries on at a second Start (test 48). The door's
# copy is one line plus the PDF note, and says "letter" like its button.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
def db(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {'tasks': []}
def newest(pg): return sorted([x['data'] for x in db(pg)['tasks']], key=lambda x: x.get('created') or '')[-1]
def door(pg):
    pg.goto('https://sorted.test/'); wait(pg, 600)
    if pg.locator('[data-a=gi-back]').count(): pg.click('[data-a=gi-back]'); wait(pg)
    if pg.locator('[data-a=new-case]').count() and not pg.locator('[data-cap82=document]').first.is_visible(): pg.locator('[data-a=new-case]').first.click(); wait(pg)
    pg.locator('[data-cap82=document]').first.evaluate('e=>e.click()'); wait(pg, 500)
def submit(pg, text): pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg)
def baseline(pg):
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count():
        pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 550)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    # 1 the door's copy: one line under the photo button, "letter" not "notice", the PDF note kept
    door(pg); m = pg.inner_text('main')
    ok('Start with your document' in m and 'Take a photo or choose the letter' in m, 'the document door is open')
    ok('Sorted reads it on your phone. Nothing is uploaded. Check what it found before you continue. For a scanned PDF, only the first page is read.' in m, 'one line under the photo button, then the PDF note')
    ok('Sorted tries to read the notice' not in m and 'Check the details before continuing' not in m, 'the old overlapping sentences are gone')
    ok('notice' not in m.lower(), 'the door says letter, never notice: %s' % [l for l in m.split('\n') if 'notice' in l.lower()])
    # 2 a name alone in the door asks what the letter says, with a photo button, and creates nothing
    submit(pg, 'From hmrc'); m = pg.inner_text('main')
    ok(pg.locator('.ps-short').count() == 1 and 'Something from HMRC.' in m and 'What does the letter say?' in m, '"From hmrc" in the door asks what the letter says')
    ok(pg.locator('.ps-short input[type=file]').count() == 1 and pg.locator('form[data-f=case] button[type=submit]').count() == 1, 'with a photo button and one Start')
    ok(pg.locator('.ps-short [role=alert]').count() == 0, 'no alert yet')
    ok(db(pg)['tasks'] == [], 'nothing is created')
    # 3 Start again with the same words keeps asking, says why, and still creates nothing
    pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg); m = pg.inner_text('main')
    ok(pg.locator('.ps-short').count() == 1 and 'What does the letter say?' in m, 'a second Start keeps asking for the letter')
    ok(pg.locator('.ps-short [role=alert]').count() == 1 and 'add a photo of the letter or a few words about what it says' in m, 'and says what to do: %s' % (pg.inner_text('.ps-short [role=alert]') if pg.locator('.ps-short [role=alert]').count() else ''))
    pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg)
    ok(pg.locator('.ps-short').count() == 1 and db(pg)['tasks'] == [], 'a third Start: still asking, still nothing created')
    ok(pg.locator('form[data-f=case]').count() == 1 and pg.locator('[data-cap82]').count() == 0, 'the door stays open, no chooser underneath')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'nothing scrolls sideways')
    # 4 a few words about the letter carry on normally, as an HMRC case
    submit(pg, 'HMRC says I owe £300 tax by 31 January')
    ok(pg.locator('.ps-short').count() == 0, 'with a few words about the letter it carries on')
    baseline(pg); t = newest(pg)
    ok('HMRC' in t['title'] and '300' in (t.get('said') or '') + t['title'], 'an HMRC case with the words: %s' % t['title'])
    ok(len(db(pg)['tasks']) == 1, 'one case')
    # 5 the general box is unchanged: Start again carries on (test 48's rule)
    pg.goto('https://sorted.test/'); wait(pg, 600)
    if pg.locator('[data-a=gi-back]').count(): pg.click('[data-a=gi-back]'); wait(pg)
    if pg.locator('[data-a=new-case]').count() and not pg.locator('[data-cap82=other]').first.is_visible(): pg.locator('[data-a=new-case]').first.click(); wait(pg)
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 500)
    submit(pg, 'From hmrc'); m = pg.inner_text('main')
    ok(pg.locator('.ps-short').count() == 1 and 'What did they send or say?' in m and 'letter say' not in m, 'the general box asks what they sent or said')
    pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg); baseline(pg)
    ok(pg.locator('.ps-short').count() == 0 and len(db(pg)['tasks']) == 2 and newest(pg)['title'] == 'HMRC', 'and Start again carries on there: %s' % newest(pg)['title'])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
