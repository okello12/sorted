# v155: the saving extraction, step 2. save(), saveConflict() and retryPlan() now ask named decisions (savePrep155,
# savePlan155, saveOutcome155, conflictKind155, retryNeed155, retryDelay155), with the v143 and v145 wrappers folded in.
# This test tells the same saving story on this page and on the page as it was at v154 (tests/make_ref.js), each in a
# browser context of its own against the same patched mock, and compares every case write that reached the "server"
# (which case, which revision, update or insert) and the final records: a new case, an edit, a failed save then a retry,
# another device's change (a merge), a lost answer (this phone's own write), a case deleted elsewhere, a case too big to
# save that isn't sent again until it changes, and moves as well as cases. Tests 66, 71, 99, 107 and 111 walk the rest.
import os, sys, json, subprocess, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import ok, wait, errs, fails, finish, HERE, day, long
from playwright.sync_api import sync_playwright

A_ = '\nboot();\n})();\n'
EXPOSE = '\nwindow.S=S;window.__h={save:function(){return save()},log:function(t,l){return log(t,l)},render:function(){return render()},task:function(id){return task(id)},retry:function(){return retryPlan()}};\nboot();\n})();\n'
SRC = open(HERE + '/tests/out/index.html', encoding='utf8').read(); assert SRC.count(A_) == 1
open(HERE + '/tests/out/121_hook.html', 'w', encoding='utf8').write(SRC.replace(A_, EXPOSE))
subprocess.run(['node', HERE + '/tests/make_ref.js', 'build154.js', '6e08ecddc881134f6a5074665447842aa55248e9'], check=True, capture_output=True)
REF = open(HERE + '/tests/out/ref154.html', encoding='utf8').read(); assert REF.count(A_) == 1
open(HERE + '/tests/out/121_ref.html', 'w', encoding='utf8').write(REF.replace(A_, EXPOSE))

MOCK = open(HERE + '/tests/mock.js').read()
def rep(s, a, b):
    assert s.count(a) == 1, a[:60]
    return s.replace(a, b)
# every case write that reaches the server: [id, rev, op]
MOCK = rep(MOCK, 'self.then=function(a,b){', 'self.then=function(a,b){if(table==="tasks"&&(op==="update"||op==="upsert")&&payload&&!Array.isArray(payload)){var _p=payload.data||{};self._w=[_p.id||"",_p.rev||0,op]}var _rr=run;run=function(){var x=_rr();if(self._w&&x&&!x.error&&(op==="upsert"||(x.data&&x.data.length))){var W=JSON.parse(localStorage.getItem("__W")||"[]");W.push(self._w);localStorage.setItem("__W",JSON.stringify(W))}return x};')

def story(br, path):
    c = br.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    c.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(body=MOCK, content_type='application/javascript'))
    c.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=path, content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = c.new_page(); pg.on('pageerror', lambda e: errs.append(os.path.basename(path) + ': ' + str(e)))
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1');localStorage.setItem('__mocksession',JSON.stringify({user:{id:'u-me',email:'me@example.com'}}))")
    pg.goto('https://sorted.test/'); wait(pg, 900)
    db = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')||'{}')") or {}
    setdb = lambda d: pg.evaluate("d=>localStorage.setItem('__mockdb',JSON.stringify(d))", d)
    def start(text):
        before = set(x['id'] for x in db().get('tasks', []))
        pg.locator('.tab129 [data-a=new-case]').click(); wait(pg, 400)
        pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 700)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg, 400)
        if pg.locator('form[data-f=baseline]').count(): pg.click('[data-a=plan-skip]'); wait(pg, 600)
        if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 800)
        for _ in range(20):
            new = [x['id'] for x in db().get('tasks', []) if x['id'] not in before]
            if new: return new[0]
            wait(pg, 200)
        return None
    def edit(cid, label):
        pg.evaluate("([id,l])=>{var t=__h.task(id);__h.log(t,l);__h.save();__h.render()}", [cid, label]); wait(pg, 700)
    a = start('Currys said the refund of £40 would be in my account by %s' % long(day(5)))
    b = start('Evri said the parcel would arrive by %s' % long(day(3)))
    edit(a, 'Edit one')
    # a failed save, then the retry once the connection is back
    pg.evaluate("localStorage.setItem('__failWrites','1')"); edit(a, 'Edit while offline'); wait(pg, 300)
    pending = pg.evaluate("S.tasks.filter(function(x){return x._dirty}).length")
    pg.evaluate("localStorage.removeItem('__failWrites')"); pg.evaluate("__h.save()"); wait(pg, 900)
    # another device saved this case: a merge
    d = db()
    for r in d['tasks']:
        if r['id'] == a: r['data']['title'] = 'Currys refund (renamed elsewhere)'; r['data']['rev'] = r['data']['rev'] + 1; r['data']['wid'] = 'other-device'; r['data']['events'].append({'at': '2026-10-01T09:00:00.000Z', 'label': 'Note from the other device'})
    setdb(d); edit(a, 'Edit after the other device'); wait(pg, 900)
    # this phone's own write whose answer was lost
    pg.evaluate("localStorage.setItem('__dropAck','1')"); edit(b, 'Edit whose answer is lost'); wait(pg, 600)
    pg.evaluate("__h.save()"); wait(pg, 900)
    # deleted on another device
    c3 = start('BT said an engineer would come on %s' % long(day(6)))
    d = db(); d['tasks'] = [r for r in d['tasks'] if r['id'] != c3]; setdb(d); edit(c3, 'Edit after it was deleted elsewhere'); wait(pg, 900)
    gone_here = pg.evaluate("id=>!__h.task(id)", c3)
    # too big: refused once, not sent again unchanged
    pg.evaluate("id=>{var t=__h.task(id);t.events.push({at:new Date().toISOString(),label:'x'.repeat(120000)});t._dirty=true;__h.save()}", b); wait(pg, 900)
    pg.evaluate("__h.save()"); wait(pg, 600); pg.evaluate("__h.retry()"); wait(pg, 300)
    held = pg.evaluate("id=>{var t=__h.task(id);return [!!t._dirty,!!t._saving,!!t._rsig145]}", b)
    W = pg.evaluate("JSON.parse(localStorage.getItem('__W')||'[]')")
    final = db()
    c.close()
    ids = {a: 'A', b: 'B', c3: 'C'}
    def norm(rec):
        x = rec['data']; return {'id': ids.get(rec['id'], '?'), 'title': x.get('title'), 'rev': x.get('rev'), 'board': x.get('board'),
            'events': [e['label'] for e in x.get('events', []) if len(e.get('label', '')) < 2000], 'promises': [[q.get('status'), q.get('party')] for q in x.get('promises', [])]}
    return {'writes': [[ids.get(w[0], '?'), w[1], w[2]] for w in W], 'final': sorted([norm(r) for r in final.get('tasks', [])], key=lambda r: r['id']),
            'pending_offline': pending, 'gone_here': gone_here, 'held': held}

with sync_playwright() as p:
    br = p.chromium.launch()
    new = story(br, HERE + '/tests/out/121_hook.html')
    old = story(br, HERE + '/tests/out/121_ref.html')
    br.close()
ok(new['writes'] == old['writes'] and len(new['writes']) >= 6, 'every case write that reached the server is the same as v154 (case, revision, update or insert): %s' % (new['writes'] if new['writes'] != old['writes'] else len(new['writes'])))
if new['writes'] != old['writes']: print('v154:', old['writes'])
ok(new['final'] == old['final'], 'the final records are the same as v154')
if new['final'] != old['final']: print('new:', json.dumps(new['final'])[:1500]); print('v154:', json.dumps(old['final'])[:1500])
ok(new['pending_offline'] == old['pending_offline'] == 1, 'a failed save leaves the case waiting on this phone, as before')
ok(new['gone_here'] and old['gone_here'], 'a case deleted on another device is removed here, as before')
ok(new['held'] == old['held'] and new['held'][2], 'a case too big to save is held, not sent again unchanged, as before: %s' % new['held'])
A = [w for w in new['writes'] if w[0] == 'A']
ok(any('Note from the other device' in e for r in new['final'] if r['id'] == 'A' for e in r['events']) and any('Edit after the other device' in e for r in new['final'] if r['id'] == 'A' for e in r['events']), 'the merge kept both devices’ history')
PAGE = open(HERE + '/public/index.html', encoding='utf8').read()
ok('_save143=' not in PAGE and '_save143c=' not in PAGE and '_rp145=' not in PAGE and 'save=function' not in PAGE and 'retryPlan=function' not in PAGE, 'the wrappers round save() and retryPlan() are folded in')
finish()
