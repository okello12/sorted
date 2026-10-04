# v70: replies come back into the case (own address in Cc), and helpers can add notes through the helper link.
import os, sys, datetime, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from dates import ahead
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=350): pg.wait_for_timeout(ms)
def db(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))")
def tasks(pg): return [x['data'] for x in db(pg)['tasks']]
def case(pg, title): return next((x for x in tasks(pg) if x['title'] == title), None)
def labels(t): return [e['label'] for e in t['events']]
def poke(pg, js):
    pg.evaluate("(js)=>{var db=JSON.parse(localStorage.getItem('__mockdb'));(new Function('db',js))(db);localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", js)
def open_case(pg, title):
    pg.goto('https://sorted.test/'); wait(pg, 500); pg.locator('[data-a=open][data-id="%s"]' % case(pg, title)['id']).first.click(); wait(pg, 500)
F = ahead(9)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.grant_permissions(['clipboard-read', 'clipboard-write'], origin='https://sorted.test')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1');localStorage.setItem('__replyOn','1')"); pg.reload(); wait(pg, 200); pg.click('[data-a=anon-start]'); wait(pg)
    T = 'Currys refund · 445566'
    pg.fill('#f-case', "Currys refund hasn't arrived, order 445566"); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    tid = case(pg, T)['id']
    # 1 emailing them from the case adds the case's own address in Cc
    pg.click('form[data-f=call] [data-a=d][data-k=via][data-v=email]'); wait(pg, 200)
    pg.fill('#f-who', 'Currys'); pg.click('form[data-f=call] button[type=submit]'); wait(pg, 500)
    href = pg.get_attribute('a[data-a=mail-open]', 'href') or ''
    ok(href.startswith('mailto:?cc=case-') and urllib.parse.quote('@inbound.getsorted.uk') in href, 'the email button adds the case’s own address in Cc: %s' % href[:60])
    ok('Sorted adds this case’s own address in Cc, so their reply comes back to this case.' in pg.inner_text('main'), 'and says why')
    # 2 a reply comes in: proposed, not applied
    poke(pg, "db.inbound_items.push({id:'r1',user_id:'x',task_id:'%s',from_domain:'currys.co.uk',subject:'Your refund',body:'Hello. We will pay your refund of £89 by %s. Order 445566. Kind regards, Currys',received_at:new Date().toISOString(),used_at:null});"
         "db.inbound_items.push({id:'r2',user_id:'x',task_id:'%s',from_domain:'spam.example',subject:'You won',body:'Claim your prize now',received_at:new Date().toISOString(),used_at:null})" % (tid, F['long'], tid))
    open_case(pg, T)
    cm = pg.inner_text('.cm-card') if pg.locator('.cm-card').count() else ''
    ok('A reply came in from currys.co.uk' in cm and 'Check it’s genuine before you rely on it' in cm and 'We will pay your refund' in cm, 'a reply is shown as a proposal, with where it came from and a warning')
    ok('1 more after this one.' in cm, 'it says there’s another')
    ok(not any(l.startswith('Added an email reply') for l in labels(case(pg, T))), 'nothing is added until you say so')
    pg.click('[data-a=cm-add]'); wait(pg, 500)
    t = case(pg, T)
    ok(any(l.startswith('Added an email reply: “Your refund. Hello. We will pay your refund') for l in labels(t)), 'adding it keeps it as evidence, marked as an email reply')
    ok(t.get('sugP') and F['dm'].split()[0] in pg.inner_text('.sug'), 'and its date is proposed as their promise')
    ok(next(x for x in db(pg)['inbound_items'] if x['id'] == 'r1').get('used_at'), 'the reply is marked as used')
    pg.click('[data-a=sug-no]'); wait(pg)
    cm = pg.inner_text('.cm-card') if pg.locator('.cm-card').count() else ''
    ok('spam.example' in cm, 'the next reply is offered')
    pg.click('[data-a=cm-drop]'); wait(pg)
    ok(not any(x['id'] == 'r2' for x in db(pg)['inbound_items']) and pg.locator('.cm-card').count() == 0, '"It’s not about this case" deletes it')
    ok('Email' in [x.strip() for x in pg.locator('.ev-src').all_text_contents()], 'evidence shows it as Email')
    # 3 notes from a helper
    pg.locator('details.case56-sharing summary').click(); wait(pg, 200)
    pg.click('[data-a=share]'); wait(pg, 600)
    tok = case(pg, T)['shareToken']
    ok(bool(tok) and pg.locator('[data-a=notes-toggle]').count() == 1, 'with a helper link, there’s a switch for notes')
    if not pg.locator('details.case56-sharing[open]').count(): pg.locator('details.case56-sharing summary').click(); wait(pg, 200)
    pg.locator('[data-a=notes-toggle]').click(); wait(pg, 500)
    sh = next(x for x in db(pg)['shares'] if x['token'] == tok)
    ok(sh.get('notes_on') is True and case(pg, T).get('notesOn') is True, 'switching it on is saved')
    hp = ctx.new_page(); hp.on('pageerror', lambda e: errs.append(str(e)))
    hp.goto('https://sorted.test/?share=' + tok); wait(hp, 700)
    ht = hp.inner_text('main')
    ok('Add a note for them' in ht and 'Last update:' in ht, 'the helper sees the note form and what happened last')
    hp.fill('#f-hn', 'Mum'); hp.fill('#f-hb', 'I rang Currys. They said the refund went out today.'); hp.click('form[data-f=hnote] button[type=submit]'); wait(hp, 500)
    ok('Note sent.' in hp.inner_text('main'), 'the helper is told it was sent')
    ok(len(db(pg)['case_notes']) == 1, 'the note is stored for the case')
    open_case(pg, T)
    nb = pg.inner_text('.notes-block') if pg.locator('.notes-block').count() else ''
    ok('Mum added a note' in nb and 'I rang Currys' in nb, 'the owner sees it as a note to keep or remove')
    ok(not any(l.startswith('Note from Mum') for l in labels(case(pg, T))), 'it isn’t in the case until kept')
    pg.click('[data-a=note-keep]'); wait(pg)
    ok(any(l.startswith('Note from Mum: “I rang Currys') for l in labels(case(pg, T))) and db(pg)['case_notes'] == [], 'keeping it puts it in the history and clears it')
    # 4 notes off: no form for the helper
    if not pg.locator('details.case56-sharing[open]').count(): pg.locator('details.case56-sharing summary').click(); wait(pg, 200)
    pg.locator('[data-a=notes-toggle]').click(); wait(pg, 600)
    hp.goto('https://sorted.test/?share=' + tok); wait(hp, 700)
    ok('Add a note for them' not in hp.inner_text('main'), 'with notes off, the helper has no form')
    # 5 privacy notice
    pg.goto('https://sorted.test/'); wait(pg, 400); pg.click('text=Account'); wait(pg); pg.click('.acct112-nav [data-v=help]'); pg.wait_for_timeout(400); 
    n = pg.inner_text('main')
    ok('Sorted adds that case’s own address in Cc. Their replies to it are received by Resend and kept for 30 days' in n and 'If you let a helper add notes' in n, 'the privacy notice explains replies and notes')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
