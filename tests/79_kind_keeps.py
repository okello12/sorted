# v122 (remediation Phase A item 3): changing the kind of case never destroys what the case knows. A mature repair
# (the thing, the fault, the checks answered, who is responsible, two visits and a no-show, a kept and an open promise,
# labelled references, a goal and whose move it is) is cycled through every kind and back: promises, references,
# facts, playbook counts, title, goal, turn and history are untouched; the repair's own answers go dormant while the
# case is another kind and come back exactly when it is a repair again; the fix questions resume where they were,
# not from "What is it?"; a case that was never a repair still gets the thing from its words.
import os, sys, json, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
def db(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))")
def task(pg, cid): return next(x['data'] for x in db(pg)['tasks'] if x['data']['id'] == cid)
def poke(pg, js):
    pg.goto('https://sorted.test/'); wait(pg, 700)
    pg.evaluate("(js)=>{var db=JSON.parse(localStorage.getItem('__mockdb'))||{tasks:[],shares:[],reminders:[],helpers:[],inbound_items:[],pilot_events:[],case_notes:[]};(new Function('db',js))(db);localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", js)
def open_case(pg, cid): pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 600)
def change_kind(pg, cid, kind):
    open_case(pg, cid); pg.evaluate("document.querySelectorAll('details.case56-more').forEach(d=>d.open=true)")
    pg.click('[data-a=panel][data-p=kind]'); wait(pg, 300); pg.click('[data-k=kind][data-v=%s]' % kind); wait(pg, 150)
    pg.click('form[data-f=kind] button[type=submit]'); wait(pg, 600)
VOLATILE = {'mode', 'fix', 'renew', 'kept', 'events', 'updatedAt', 'rev', 'frNew', 'goalP', 'lastReturnAt', 'turnAt'}
def core(t): return {k: v for k, v in t.items() if k not in VOLATILE and not k.startswith('_')}
def kind_lines(t): return [e['label'] for e in t['events'] if e['label'].startswith('Changed the kind')]
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 200); pg.click('[data-a=anon-start]'); wait(pg, 600)
    uid = pg.evaluate("JSON.parse(localStorage.getItem('__mocksession')).user.id")
    now = pg.evaluate("new Date().toISOString()")
    # a mature repair, written as the app would have saved it
    mature = {
        'id': 'rep1', 'title': 'Landlord: boiler', 'mode': 'fix', 'board': 'waiting', 'created': now, 'updatedAt': now, 'rev': 3,
        'said': 'The boiler has no heating and the landlord said an engineer would come', 'party': 'Landlord',
        'fix': {'step': 'decide', 'item': 'Boiler', 'fault': 'no heating', 'checks': {'pressure': 'yes', 'thermostat': 'yes'}, 'responsible': 'landlord', 'party': 'Landlord', 'age': '3-6', 'detail': 'Radiators cold since Monday'},
        'pb': {'id': 'repair', 'stage': 'waiting', 'visits': 2, 'noShows': 1},
        'promises': [
            {'id': 'p1', 'said': 'The engineer will come on Monday', 'party': 'Landlord', 'dueAt': '2026-09-28T23:59:59.000Z', 'allDay': True, 'status': 'kept', 'loggedAt': now, 'closedAt': now},
            {'id': 'p2', 'said': 'The engineer will come back on Friday with the part', 'party': 'Landlord', 'ref': 'JOB-5521', 'dueAt': '2026-10-09T23:59:59.000Z', 'allDay': True, 'status': 'open', 'loggedAt': now}],
        'refs': [{'k': 'job', 'v': 'JOB-5521', 'at': now, 'src': 'start', 'st': 'confirmed'}],
        'goal': 'The boiler fixed and heating back on', 'turn': 'theirs', 'turnAt': now,
        'holder': None, 'moves': [],
        'events': [{'at': now, 'label': 'Started.'}, {'at': now, 'label': 'Visit 1 happened.'}, {'at': now, 'label': 'Still not fixed after one visit.'}, {'at': now, 'label': 'Promise missed: the engineer didn’t come.'}, {'at': now, 'label': 'Visit 2 happened.'}]}
    poke(pg, "db.tasks.push({id:'rep1',user_id:%s,data:%s,updated_at:new Date().toISOString()})" % (json.dumps(uid), json.dumps(mature)))
    open_case(pg, 'rep1'); t0 = task(pg, 'rep1'); c0 = core(t0); f0 = copy.deepcopy(t0['fix'])
    ok(t0['fix']['item'] == 'Boiler' and t0['pb']['visits'] == 2, 'the mature repair loads')
    # ---- 1. repair -> call: the repair's answers go dormant, everything else untouched ----
    change_kind(pg, 'rep1', 'call'); t1 = task(pg, 'rep1')
    ok(t1['mode'] == 'call' and t1['fix'] is None and t1.get('kept', {}).get('fix', {}).get('fix') == f0, 'as a call case, the repair answers are kept on the case, not deleted')
    ok(core(t1) == c0, 'promises, references, playbook counts, title, goal and whose move are untouched (%s)' % [k for k in set(c0) | set(core(t1)) if c0.get(k) != core(t1).get(k)])
    ok(len(t1['events']) == len(t0['events']) + 1 and kind_lines(t1) == ['Changed the kind of case from “Something needs fixing” to “Someone else owes me the next move”.'], 'the history gains one line and loses none')
    ok(t1['turn'] == 'theirs', 'whose move it is, which the person said, is not forgotten')
    # ---- 2. call -> do -> call -> fix: back to the repair, with the same answers ----
    change_kind(pg, 'rep1', 'do')
    if pg.locator('#moveform').count(): pg.locator('[data-a=panel][data-p=""]').first.click(); wait(pg, 300)
    t2 = task(pg, 'rep1')
    ok(t2['mode'] == 'do' and t2['fix'] is None and t2['kept']['fix']['fix'] == f0 and core(t2) == c0, 'your own task: still nothing lost')
    change_kind(pg, 'rep1', 'call'); change_kind(pg, 'rep1', 'fix'); t3 = task(pg, 'rep1')
    ok(t3['mode'] == 'fix' and t3['fix'] == f0, 'back as a repair, the thing, fault, checks, who is responsible and detail are exactly as they were')
    ok(core(t3) == c0 and len(t3['events']) == len(t0['events']) + 4, 'after the whole cycle the case is the same, plus four history lines')
    m = pg.inner_text('main')
    ok('What is it, and what’s it doing?' not in m and 'What is it?' not in m, 'the fix questions do not start again from "What is it?"')
    # ---- 3. a case that was never a repair gets the thing from its words, and keeps it on the way back ----
    poke(pg, "db.tasks.push({id:'call1',user_id:%s,data:%s,updated_at:new Date().toISOString()})" % (json.dumps(uid), json.dumps({
        'id': 'call1', 'title': 'Currys: dishwasher', 'mode': 'call', 'board': 'yours', 'created': now, 'updatedAt': now, 'rev': 1,
        'said': 'My dishwasher keeps leaking and Currys said they would call me back', 'party': 'Currys', 'promises': [], 'refs': [], 'moves': [], 'events': [{'at': now, 'label': 'Started.'}]})))
    change_kind(pg, 'call1', 'fix'); t4 = task(pg, 'call1')
    ok(t4['mode'] == 'fix' and t4['fix']['item'].lower() == 'dishwasher' and t4['fix']['step'] == 'what', 'a call case made a repair takes the thing from its words and starts the fix questions')
    pg.evaluate("localStorage.setItem('__failWrites','0')")
    # answer one fix question, leave, come back: the answer is still there
    if pg.locator('form[data-f=what]').count():
        pg.fill('#f-fault', 'keeps leaking') if pg.locator('#f-fault').count() else None
        pg.click('form[data-f=what] button[type=submit]'); wait(pg, 500)
    t5 = task(pg, 'call1'); fx = copy.deepcopy(t5['fix'])
    change_kind(pg, 'call1', 'call'); change_kind(pg, 'call1', 'fix'); t6 = task(pg, 'call1')
    ok(t6['fix'] == fx and t6['fix']['item'].lower() == 'dishwasher', 'an answer given, then a change away and back, is still there (%s)' % t6['fix'].get('step'))
    ok(not errs, 'no page errors: %s' % errs)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
