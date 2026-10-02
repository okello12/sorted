# The adversarial corpus (tests/corpus.py) through the real reader, the same way the start box uses it.
# Runs on tests/out/reader.html, a test-only copy of the page that exposes the reader (tests/make_reader.js).
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
# readCase() is exactly what the start box uses
READ = """(xs)=>xs.map(function(t){var r=window.__read,p=r.readCase(t,r.caseFacts(t));
  return p?{said:p.said,party:p.party,dueAt:p.dueAt,past:p.past}:null})"""
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/reader.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/'); pg.wait_for_timeout(500)
    ok(pg.evaluate("!!window.__read"), 'reader hook present on the test copy')
    nots = corpus.not_all()
    rn = pg.evaluate(READ, [s for _, s in nots])
    bad = [(g, s, r) for (g, s), r in zip(nots, rn) if r]
    groups = {}
    for (g, s), r in zip(nots, rn): groups.setdefault(g, [0, 0]); groups[g][0] += 1; groups[g][1] += 0 if r else 1
    for g, (n, good) in groups.items(): ok(good == n, 'not a promise, %s: %d/%d rejected' % (g, good, n))
    for g, s, r in bad: print('   false promise [%s]: %s  ->  %s' % (g, s, r['said']))
    ry = pg.evaluate(READ, corpus.YES)
    missed = [s for s, r in zip(corpus.YES, ry) if not r]
    ok(not missed, 'real promises heard: %d/%d' % (len(corpus.YES) - len(missed), len(corpus.YES)))
    for s in missed: print('   missed: %s' % s)
    past = [s for s, r in zip(corpus.YES, ry) if r and r['past']]
    ok(not past, 'real future promises are not marked as passed: %d' % len(past))
    for s in past: print('   wrongly past: %s' % s)
    rm = pg.evaluate(READ, corpus.MSG_YES); mm = [s for s, r in zip(corpus.MSG_YES, rm) if not r]
    ok(not mm, 'pasted messages with a commitment: %d/%d heard' % (len(rm) - len(mm), len(rm)))
    for s in mm: print('   missed message: %s' % s.replace('\n', ' / ')[:110])
    rn2 = pg.evaluate(READ, corpus.MSG_NOT); mb = [(s, r) for s, r in zip(corpus.MSG_NOT, rn2) if r]
    ok(not mb, 'pasted messages without a commitment: %d/%d rejected' % (len(rn2) - len(mb), len(rn2)))
    for s, r in mb: print('   false promise in message: %s  ->  %s' % (s[:90], r['said']))
    import datetime
    my = pg.evaluate(READ, [x for x, _ in corpus.MESSY_YES]); bad_m = []
    for (txt, want), r in zip(corpus.MESSY_YES, my):
        if not r: bad_m.append((txt, 'no card')); continue
        d = datetime.datetime.fromisoformat(r['dueAt'].replace('Z', '+00:00')).astimezone()
        today = datetime.date.today()
        if 'days' in want and (d.date() - today).days != want['days']: bad_m.append((txt, 'day %s' % d))
        if 'weekday' in want and d.strftime('%A') != want['weekday']: bad_m.append((txt, 'weekday %s' % d.strftime('%A')))
        if 'hour' in want and d.hour != want['hour']: bad_m.append((txt, 'hour %d' % d.hour))
        if 'dom' in want and d.day != want['dom']: bad_m.append((txt, 'day of month %d' % d.day))
        if want.get('past') and not r['past']: bad_m.append((txt, 'not marked passed'))
        if 'party' in want and r['party'] != want['party']: bad_m.append((txt, 'party %r' % r['party']))
    ok(not bad_m, 'messy real-world promises read right: %d/%d' % (len(my) - len(bad_m), len(my)))
    for t2, why in bad_m: print('   wrong: %s  (%s)' % (t2.replace('\n', ' / ')[:80], why))
    mn = pg.evaluate(READ, corpus.MESSY_NOT); bad_n = [(t2, r) for t2, r in zip(corpus.MESSY_NOT, mn) if r]
    ok(not bad_n, 'messy non-promises rejected: %d/%d' % (len(mn) - len(bad_n), len(mn)))
    for t2, r in bad_n: print('   false promise: %s  ->  %s' % (t2, r['said']))
    total = len(nots) + len(my) + len(mn) + len(corpus.YES) + len(corpus.MSG_YES) + len(corpus.MSG_NOT)
    print('  corpus size: %d sentences and messages' % total)
    b.close()
print('ERRORS', errs); print('FAILS', fails)
