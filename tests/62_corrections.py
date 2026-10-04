# v106: corrections. The latest explicit correction is current everywhere Sorted shows or sends it; the old value stays
# in the history. Read from a pasted message, from "Add to that case", and from "Correct a detail". A date you mistyped
# is not a date they moved: only "They moved it" counts as a change on their side. Nothing changes until the tap.
import os, sys, json, datetime, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
NEXT_TUE = dates.next_weekday(1) if hasattr(dates, 'next_weekday') else None
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    # Part 1: the reader
    rd = ctx.new_page(); rd.route(lambda u: u.startswith('https://sorted.test/'), lambda q: q.fulfill(path=HERE + '/tests/out/reader.html', content_type='text/html'))
    rd.goto('https://sorted.test/'); wait(rd, 500)
    cur = {"party": "Sky", "ref": "AB123", "amount": 80, "item": "Boiler", "dueAt": "2026-10-06T08:00:00.000Z", "dueEnd": "2026-10-06T12:00:00.000Z", "allDay": False, "by": False}
    C = lambda t: rd.evaluate("([c,s])=>{var r=__read.corrRead(c,s);return r?{k:r.k,from:String(r.from),to:String(r.to),moved:!!r.moved}:null}", [cur, t])
    for t, k, to in [("It wasn't Sky, it was Virgin", 'party', 'Virgin'), ("not Sky, Virgin Media", 'party', 'Virgin Media'), ("Sorry, it's Virgin", 'party', 'Virgin'), ("I meant Virgin Media", 'party', 'Virgin Media'), ("Actually it was BT not Sky", 'party', 'BT'),
                     ("Reference AB132, not AB123", 'ref', 'AB132'), ("the ref is actually AB132", 'ref', 'AB132'), ("AB132 not AB123", 'ref', 'AB132'), ("my mistake, the reference is CX-8891", 'ref', 'CX-8891'),
                     ("£89 not £80", 'amount', '89'), ("sorry I meant £89", 'amount', '89'),
                     ("it's the thermostat not the boiler", 'item', 'Thermostat'), ("sorry, it's the dishwasher", 'item', 'Dishwasher'), ("I meant the radiator", 'item', 'Radiator')]:
        r = C(t) or {}; ok(r.get('k') == k and r.get('to') == to, 'reads "%s" as %s -> %s (%s)' % (t, k, to, json.dumps(r)))
    for t, day in [("Sorry, I meant Wednesday", '2026-10-07'), ("it's Wednesday not Tuesday", '2026-10-07'), ("actually it's the 8th", '2026-10-08'), ("I meant the 8th of October, not the 6th", '2026-10-08')]:
        r = C(t) or {}; ok(r.get('k') == 'date' and r.get('to', '')[:10] in (day, (datetime.date.fromisoformat(day) - datetime.timedelta(days=1)).isoformat()) and not r.get('moved'), 'reads "%s" as a date correction to %s (%s)' % (t, day, json.dumps(r)))
    r = C("sorry, 2pm not 8am") or {}; ok(r.get('k') == 'date' and r.get('to', '')[:10] == '2026-10-06' and '13:00' in r.get('to', ''), 'a time on its own keeps the day (%s)' % json.dumps(r))
    r = C("They moved it to Wednesday") or {}; ok(r.get('k') == 'date' and r.get('moved'), '"They moved it" is read as their change')
    for t in ["Sky said they'd come Wednesday instead", "They said it's not possible before Thursday", "Virgin will install on Tuesday ref V123", "Nobody came on Tuesday", "Not sure what to do", "It's not working", "I can't get through to Sky", "Please call me back on 0800 123 4567", "the engineer didn't come", "it was £89"]:
        ok(C(t) is None, 'not a correction: %s' % t)
    rd.close()
    # Part 2: the interface
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: [x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment']
    events = lambda: dbj().get('pilot_events', [])
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg)
    tue = datetime.date.today() + datetime.timedelta(days=(1 - datetime.date.today().weekday()) % 7 or 7)
    pg.fill('#f-case', 'Sky said an engineer would come %s between 8 and 12 to fix the boiler, ref AB123, and refund £80' % tue.strftime('%A')); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
    c = cases()[0]; cid = c['id']; pid = [q for q in c['promises'] if q['status'] == 'open'][0]['id']
    ok(c['promises'][0]['party'] == 'Sky' and c['promises'][0]['ref'] == 'AB123', 'a Sky promise with ref AB123 to correct')
    def paste(text):
        if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
        if not pg.locator('[data-a=panel][data-p=paste]').count(): pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600)
        pg.locator('[data-a=panel][data-p=paste]').first.evaluate('e=>e.click()'); wait(pg, 300); pg.fill('#f-paste', text); pg.click('form[data-f=paste] button[type=submit]'); wait(pg, 600)
    paste("Sorry, it wasn't Sky, it was Virgin Media")
    m = pg.inner_text('main')
    ok(pg.locator('.corr').count() == 1 and 'Did you mean Virgin Media, not Sky?' in m, 'a pasted correction asks "Did you mean Virgin Media, not Sky?"')
    c = cases()[0]; ok(c['promises'][0]['party'] == 'Sky' and (c.get('facts') or {}).get('party') == 'Sky', 'nothing changed before the tap')
    pg.click('[data-a=corr-no]'); wait(pg)
    c = cases()[0]; ok(pg.locator('.corr').count() == 0 and c['promises'][0]['party'] == 'Sky' and not c.get('corr'), '"No, leave it" leaves it')
    paste("It wasn't Sky, it was Virgin Media"); pg.click('[data-a=corr-yes]'); wait(pg, 600)
    c = cases()[0]; m = pg.inner_text('main')
    ok(c['promises'][0]['party'] == 'Virgin Media' and (c.get('facts') or {}).get('party') == 'Virgin Media' and 'Virgin Media' in c['title'] and 'Sky' not in c['title'], 'Yes puts Virgin Media on the promise, the facts and the title')
    ok(c.get('corr') and c['corr'][-1]['k'] == 'party' and c['corr'][-1]['from'] == 'Sky' and c['corr'][-1]['to'] == 'Virgin Media' and c['corr'][-1]['how'] == 'corrected', 'the ledger keeps Sky as the value before')
    ok(any('Changed who it is from Sky to Virgin Media. You corrected it.' in (e.get('label') or '') for e in c['events']), 'the history says what changed and who changed it')
    paste("Reference AB132, not AB123"); ok('Is the reference AB132, not AB123?' in pg.inner_text('main'), 'a reference correction asks'); pg.click('[data-a=corr-yes]'); wait(pg, 600)
    c = cases()[0]; ok(c['promises'][0]['ref'] == 'AB132' and (c.get('facts') or {}).get('ref') == 'AB132', 'the reference is AB132 on the promise and the facts')
    paste("Sorry, £89 not £80"); ok('Is it £89, not £80?' in pg.inner_text('main'), 'an amount correction asks'); pg.click('[data-a=corr-yes]'); wait(pg, 600)
    c = cases()[0]; ok((c.get('facts') or {}).get('amount') == 89 and '£80' not in c['promises'][0]['said'] and '£89' in c['promises'][0]['said'], 'the amount is £89 in the facts and in what they said')
    # the date, mistyped
    wed = tue + datetime.timedelta(days=1)
    paste("Sorry, I meant %s" % wed.strftime('%A')); m = pg.inner_text('main')
    ok(pg.locator('[data-a=corr-yes]').count() == 1 and pg.locator('[data-a=corr-moved]').count() == 1 and 'If they moved it, that counts as a change on their side' in m, 'a date correction asks whether they moved it or it was typed wrong')
    n_resched = len([e for e in events() if e['name'] == 'outcome_rescheduled'])
    pg.click('[data-a=corr-yes]'); wait(pg, 600)
    L = lambda iso: pg.evaluate("iso=>{var d=new Date(iso);return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')}", iso)
    c = cases()[0]; op = [q for q in c['promises'] if q['status'] == 'open'][0]
    ok(op['id'] == pid and L(op['dueAt']) == wed.isoformat() and len([q for q in c['promises'] if q['status'] == 'replaced']) == 0, 'typed wrong: the same promise, now on %s, nothing replaced (%s)' % (wed.strftime('%A'), L(op['dueAt'])))
    ok(len([e for e in events() if e['name'] == 'outcome_rescheduled']) == n_resched, 'and it does not count as a change on their side')
    # the date, moved by them
    thu = wed + datetime.timedelta(days=1)
    paste("They moved it to %s" % thu.strftime('%A'))
    # a message that reads as their new date goes the promise way; typed as a correction it leads with "They moved it"
    if pg.locator('[data-a=corr-moved]').count(): ok(pg.locator('.corr .btn.primary[data-a=corr-moved]').count() == 1, '"They moved it" leads with their change'); pg.click('[data-a=corr-moved]'); wait(pg, 600)
    else: ok(pg.locator('[data-a=sug-yes]').count() == 1, '"They moved it to Thursday" is read as their new date'); pg.click('[data-a=sug-yes]'); wait(pg, 600)
    c = cases()[0]; op = [q for q in c['promises'] if q['status'] == 'open'][0]
    ok(op['id'] != pid and L(op['dueAt']) == thu.isoformat() and [q for q in c['promises'] if q['id'] == pid][0]['status'] == 'replaced', 'moved by them: the old promise is replaced by a new one on %s' % thu.strftime('%A'))
    ok(len([e for e in events() if e['name'] == 'outcome_rescheduled']) == n_resched + 1, 'and that one does count as their change')
    fri = thu + datetime.timedelta(days=1); pid2 = op['id']
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600)
    pg.evaluate("document.querySelector('details.case56-more').open=true"); pg.click('[data-a=panel][data-p=correct]'); wait(pg, 300)
    pg.fill('#f-correct', 'They moved it to %s' % fri.strftime('%A')); pg.click('form[data-f=correct] button[type=submit]'); wait(pg, 500)
    ok(pg.locator('.corr .btn.primary[data-a=corr-moved]').count() == 1, 'typed "They moved it" leads with their change'); pg.click('[data-a=corr-moved]'); wait(pg, 600)
    c = cases()[0]; op = [q for q in c['promises'] if q['status'] == 'open'][0]
    ok(op['id'] != pid2 and L(op['dueAt']) == fri.isoformat() and len([e for e in events() if e['name'] == 'outcome_rescheduled']) == n_resched + 2, 'and it replaces the promise and counts as their change')
    # the thing, from "Correct a detail"
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600)
    pg.evaluate("document.querySelector('details.case56-more').open=true"); pg.click('[data-a=panel][data-p=correct]'); wait(pg, 300)
    pg.fill('#f-correct', 'It was a lovely day'); pg.click('form[data-f=correct] button[type=submit]'); wait(pg, 400)
    ok('couldn’t see what to change' in pg.inner_text('main'), '"Correct a detail" with nothing to change says so')
    pg.fill('#f-correct', "it's the thermostat, not the boiler"); pg.click('form[data-f=correct] button[type=submit]'); wait(pg, 500)
    ok('Is it the thermostat, not the boiler?' in pg.inner_text('main'), 'a thing correction asks'); pg.click('[data-a=corr-yes]'); wait(pg, 600)
    c = cases()[0]; ok(((c.get('fix') or {}).get('item') == 'Thermostat' or (c.get('facts') or {}).get('item') == 'Thermostat') and 'boiler' not in c['title'].lower(), 'the thing is the thermostat')
    ok(not any(re.search(r'^Added a message', e.get('label') or '') and 'thermostat' in (e.get('label') or '') for e in c['events']), 'typed corrections are not logged as something they sent')
    # the sweep: no replaced value is current anywhere Sorted shows or sends
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600)
    main = pg.inner_text('main')
    cur_lines = [l for l in main.split('\n') if not re.search(r'Changed |It was |Left |in your words|In your words|Added a message|Taken from', l)]
    old = ['Sky', 'AB123', '£80', 'Boiler', tue.strftime('%A %-d %B'), wed.strftime('%A %-d %B'), thu.strftime('%A %-d %B')]
    leaks = [(v, l) for v in old for l in cur_lines if v in l]
    ok(not leaks, 'the case page shows no replaced value as current: %s' % leaks[:4])
    pg.evaluate("document.querySelector('details.case56-sharing').open=true"); pg.click('[data-a=share]'); wait(pg, 600)
    card = json.dumps([s for s in dbj().get('shares', []) if s['task_id'] == cid][0]['card'], ensure_ascii=False)
    ok('Virgin Media' in card and 'AB132' in card and 'Sky' not in card and 'AB123' not in card, 'the shared card carries only the current values')
    if pg.locator('[data-a=panel][data-p=call]').count(): pg.locator('[data-a=panel][data-p=call]').first.evaluate('e=>e.click()'); wait(pg, 400)
    ask = pg.input_value('#f-ask') if pg.locator('#f-ask').count() else pg.inner_text('main')
    ok('AB123' not in ask and 'Sky' not in ask, 'the chase message does not use a replaced reference or name')
    pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600)
    pg.locator('[data-a=panel][data-p=pack]').first.evaluate('e=>e.click()'); wait(pg, 500)
    pack = pg.inner_text('.pack-doc')
    ok('Corrections' in pack and 'Sky → Virgin Media' in pack and 'AB123 → AB132' in pack, 'the adviser pack lists the corrections')
    cur_pack = [l for l in pack.split('\n') if not re.search(r'→|Changed |It was |In your words|in your words|^Message, |Taken from|In my words', l)]
    ok(not any('Sky' in l or 'AB123' in l for l in cur_pack), 'and nowhere else in it is a replaced value current: %s' % [l for l in cur_pack if 'Sky' in l or 'AB123' in l][:3])
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
