# v158/v159: pressure at 100 and 500 cases with long histories. A signed-in person with N cases (each with 30 history lines,
# two promises, a step and references) loads Sorted: Home and Cases draw, a case opens, an edit is saved, and the copy
# on this phone (localStorage, about 5 MB in most browsers) is written. When the copy no longer fits, the cases with an
# unsent edit must still be kept on the phone (they exist nowhere else), and what was left out is only what the
# account already holds (before v159 a full copy failed silently and lost the offline edit). The test's stand-in
# server keeps its own database in the same storage, so 500 cases here fill it as a much larger account would. Times are printed so a slow-down shows; the limits are generous so a busy machine passes.
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import ok, wait, errs, fails, finish, HERE
from playwright.sync_api import sync_playwright

def case(i):
    ev = [{'at': '2026-09-%02dT%02d:%02d:00.000Z' % (1 + j % 28, 8 + j % 10, j % 60), 'label': 'Message %d: they said the engineer would come between eight and twelve and to keep the reference to hand when calling again. ' % j} for j in range(30)]
    return {'id': 'case-%04d' % i, 'title': 'Case %d with Currys' % i, 'board': 'waiting', 'mode': 'call', 'rev': 2, 'created': '2026-09-01T09:00:00.000Z', 'updatedAt': '2026-09-20T09:00:00.000Z',
            'said': 'Currys said the refund would arrive by Friday', 'events': ev,
            'promises': [{'id': 'p%da' % i, 'status': 'missed', 'party': 'Currys', 'said': 'refund £40', 'dueAt': '2026-09-10T00:00:00.000Z', 'allDay': True, 'by': True, 'closedAt': '2026-09-11T09:00:00.000Z'},
                         {'id': 'p%db' % i, 'status': 'open', 'party': 'Currys', 'said': 'refund £40 by the 30th', 'dueAt': '2026-10-30T00:00:00.000Z', 'allDay': True, 'by': True, 'prec': 'day', 'loggedAt': '2026-09-12T09:00:00.000Z'}],
            'moves': [{'id': 'm%d' % i, 'what': 'Phone Currys', 'status': 'done', 'loggedAt': '2026-09-05T09:00:00.000Z'}],
            'refs': [{'k': 'order', 'v': 'AB%06d' % i, 'st': 'confirmed'}], 'facts': {'party': 'Currys'}}

def run(n):
    with sync_playwright() as p:
        b = p.chromium.launch(); c = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
        c.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
        c.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
        pg = c.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('https://sorted.test/#about')
        db = {'tasks': [{'id': x['id'], 'user_id': 'u-me', 'data': x, 'updated_at': '2026-09-20T09:00:00.000Z'} for x in (case(i) for i in range(n))]}
        pg.evaluate("d=>{localStorage.clear();localStorage.setItem('__emailReady','1');localStorage.setItem('__mocksession',JSON.stringify({user:{id:'u-me',email:'me@example.com'}}));localStorage.setItem('__mockdb',JSON.stringify(d))}", db)
        t0 = time.time(); pg.goto('https://sorted.test/'); pg.wait_for_selector('.tab129', timeout=60000); wait(pg, 1500); load = time.time() - t0
        cache = pg.evaluate("(()=>{var k=Object.keys(localStorage).filter(k=>k.indexOf('sorted.cache.')===0)[0];var v=k?localStorage.getItem(k):'';return [v.length,(JSON.parse(v||'[]')).length]})()")
        t0 = time.time(); pg.locator('.tab129 [data-a=cases]').click(); pg.wait_for_selector('#pick-q'); cases_t = time.time() - t0
        t0 = time.time(); pg.goto('https://sorted.test/#case-case-0007'); pg.wait_for_selector('main'); wait(pg, 1200); open_t = time.time() - t0
        shown = 'Case 7 with Currys' in pg.inner_text('main')
        # an unsent edit: offline, rename a case, then reload offline
        pg.evaluate("localStorage.setItem('__failWrites','1')")
        pg.locator('[data-a=panel][data-p=rename]').first.evaluate('e=>e.click()'); wait(pg, 400)
        pg.fill('form[data-f=rename] input', 'Edited while offline'); pg.locator('form[data-f=rename] button[type=submit]').click(); wait(pg, 1500)
        kept = pg.evaluate("(()=>{var k=Object.keys(localStorage).filter(k=>k.indexOf('sorted.cache.')===0)[0];var v=JSON.parse(localStorage.getItem(k)||'[]');var x=v.filter(function(r){return r.id==='case-0007'})[0];return !!(x&&x.title==='Edited while offline'&&x._dirty)})()")
        pg.reload(); pg.wait_for_selector('.tab129', timeout=60000); wait(pg, 1500); pg.goto('https://sorted.test/#case-case-0007'); wait(pg, 1500)
        after = 'Edited while offline' in pg.inner_text('main')
        c.close(); b.close()
        return {'after': after, 'load': load, 'cases': cases_t, 'open': open_t, 'cache_chars': cache[0], 'cache_n': cache[1], 'shown': shown, 'kept': kept}

for n in (100, 500):
    r = run(n)
    print('INFO %d cases: load %.1fs, Cases %.2fs, open %.2fs, phone copy %d records, %.1f MB' % (n, r['load'], r['cases'], r['open'], r['cache_n'], r['cache_chars'] / 1e6))
    ok(r['shown'] and r['load'] < 30 and r['cases'] < 10 and r['open'] < 15, '%d cases: Home, Cases and a case open in reasonable time' % n)
    ok(r['kept'], '%d cases: an edit made offline is kept in the copy on this phone' % n)
    ok(r['after'], '%d cases: and is still there after a reload' % n)
finish()
