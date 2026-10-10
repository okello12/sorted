# v156: the saving extraction, step 3. The merge's decisions are a pure function, mergeRec156(mine, server, base,
# kind), and mergeInto applies the result. This test generates thousands of three-way changes (the last copy both
# devices agreed on, this phone's and the server's) from a real case and a move: titles, boards and outcomes changed on
# one side or both, messages added on either side or removed with evDel, promises added, closed on one side, closed
# differently on both, steps, corrections, references, the repair answers (fix), the parking state (pk), whose move,
# Later, case facts (cf), kept document names, Moving home items, proposals, and no agreed copy at all. Each is merged
# by this page and by the page as it was at v155 (tests/make_ref.js); the merged records, the count of this phone's
# changes kept and the fields both changed must be identical. Tests 66, 99, 107 and 111 walk merges end to end.
import os, sys, json, subprocess, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import ok, wait, errs, fails, finish, HERE
from playwright.sync_api import sync_playwright

A_ = '\nboot();\n})();\n'
# both pages run the same probe: merge a clone of the case, report the record (minus the history line's time) and the line
PROBE = r'''window.__m=function(cases){return cases.map(function(c){var t=JSON.parse(JSON.stringify(c.mine));t._base=c.base===null?undefined:JSON.stringify(c.base);if(c.kind)t.kind=c.kind;
  var lines=[];var tst=toast;toast=function(m){lines.push(m)};try{mergeInto(t,JSON.parse(JSON.stringify(c.srv)))}finally{toast=tst}
  var o=clean(t);(o.events||[]).forEach(function(e){if(/^Merged with changes/.test(e.label))e.at="(now)"});return {rec:o,rev:t.rev,base:t._base,toast:lines}})};'''
EXPOSE = '\n' + PROBE + '\nboot();\n})();\n'
SRC = open(HERE + '/tests/out/index.html', encoding='utf8').read(); assert SRC.count(A_) == 1
open(HERE + '/tests/out/122_hook.html', 'w', encoding='utf8').write(SRC.replace(A_, EXPOSE))
subprocess.run(['node', HERE + '/tests/make_ref.js', 'build155.js', '11d2a597bbec9ae9fe3f00db19c18dbf2b713f90'], check=True, capture_output=True)
REF = open(HERE + '/tests/out/ref155.html', encoding='utf8').read(); assert REF.count(A_) == 1
open(HERE + '/tests/out/122_ref.html', 'w', encoding='utf8').write(REF.replace(A_, EXPOSE))

T0 = '2026-10-01T09:00:00.000Z'
BASE = {'id': 'c1', 'title': 'Currys refund', 'board': 'waiting', 'mode': 'call', 'rev': 3, 'wid': 'w-base', 'created': T0, 'said': 'Currys said the refund would arrive by Friday',
    'events': [{'at': T0, 'label': 'Started.'}, {'at': '2026-10-02T09:00:00.000Z', 'label': 'Confirmed Currys said they would refund £40.'}],
    'promises': [{'id': 'p1', 'status': 'open', 'party': 'Currys', 'said': 'refund £40', 'dueAt': '2026-10-12T00:00:00.000Z', 'allDay': True, 'by': True, 'loggedAt': T0}],
    'moves': [], 'refs': [{'k': 'order', 'v': 'AB123', 'st': 'confirmed'}], 'corr': [], 'facts': {'party': 'Currys'},
    'fix': {'step': 'done', 'item': 'Kettle'}, 'turn': 'theirs', 'goal': {'v': 'Get my money back'}, 'docNames': {'a1': 'receipt.jpg'}}
MOVE = {'id': 'm1', 'kind': 'moment', 'type': 'move', 'title': 'Moving home', 'date': '2026-11-01', 'rev': 2, 'ans': {'tenure': 'rent'}, 'items': {'gp': {'st': 'done', 'at': T0}, 'council': {'st': 'case', 'caseId': 'c9', 'at': T0}}}

def edits(rnd, rec, who):
    r = json.loads(json.dumps(rec)); at = '2026-10-0%dT1%d:00:00.000Z' % (rnd.randint(3, 9), rnd.randint(0, 9))
    if r.get('kind') == 'moment':
        for _ in range(rnd.randint(0, 3)):
            k = rnd.choice(['gp', 'council', 'post', 'tv'])
            r.setdefault('items', {})[k] = {'st': rnd.choice(['done', 'irrelevant', 'case', 'contacted']), 'at': at}
        if rnd.random() < .3: r['title'] = 'Move (%s)' % who
        if rnd.random() < .3: r['ans'] = dict(r.get('ans') or {}, bb=rnd.choice(['yes', 'no']))
        return r
    for _ in range(rnd.randint(0, 5)):
        x = rnd.random()
        if x < .1: r['title'] = 'Currys refund (%s)' % who
        elif x < .17: r['board'] = rnd.choice(['yours', 'waiting', 'done'])
        elif x < .22: r['outcome'] = 'Refunded (%s)' % who; r['board'] = 'done'
        elif x < .35: r['events'].append({'at': at, 'label': 'Note from %s %d' % (who, rnd.randint(1, 99))})
        elif x < .4 and r['events']: from_ = rnd.choice(r['events']); r.setdefault('evDel', []).append(from_['at'] + '|x')
        elif x < .5:
            p = rnd.choice(r['promises']) if r['promises'] else None
            if p: p['status'] = rnd.choice(['kept', 'missed', 'replaced', 'cancelled']); p['closedAt'] = at
        elif x < .58: r['promises'].append({'id': 'p%s%d' % (who, rnd.randint(1, 9)), 'status': 'open', 'party': rnd.choice(['Currys', 'Evri']), 'said': 'new date', 'dueAt': '2026-10-20T00:00:00.000Z', 'allDay': True, 'by': True, 'loggedAt': at})
        elif x < .65: r['moves'].append({'id': 'mv%s%d' % (who, rnd.randint(1, 9)), 'what': 'Phone them', 'status': rnd.choice(['open', 'done']), 'loggedAt': at})
        elif x < .7: r['corr'].append({'at': at, 'k': 'ref', 'from': 'AB123', 'to': 'AB124'})
        elif x < .74: r['refs'].append({'k': 'claim', 'v': 'CL%d' % rnd.randint(1, 9), 'st': 'proposed'})
        elif x < .79: r['fix'] = dict(r.get('fix') or {}, step=rnd.choice(['done', 'checks']), visits=rnd.randint(0, 3))
        elif x < .83: r['pk'] = {'stage': rnd.choice(['notice', 'challenged', 'paid']), 'subs': [], 'at': at}
        elif x < .86: r['turn'] = rnd.choice(['mine', 'theirs', 'both'])
        elif x < .89: r['snooze'] = {'until': '2026-10-15T08:00:00.000Z', 'at': at}
        elif x < .92: r['cf'] = {'f': {'vrm': {'v': 'AB12 CDE', 'st': rnd.choice(['proposed', 'confirmed'])}}, 'at': at}
        elif x < .95: r['docNames'] = dict(r.get('docNames') or {}, **{'d%d' % rnd.randint(1, 5): 'photo.jpg'})
        elif x < .97: r['sugP'] = {'party': 'Currys', 'said': 'refund', 'pid': ''}
        else: r['goal'] = {'v': 'Refund (%s)' % who}
    r['rev'] = rec['rev'] + (1 if who == 'srv' else 0)
    if who == 'srv': r['wid'] = 'w-srv'
    return r

rnd = random.Random(156)
cases = []
for i in range(3000):
    base = MOVE if i % 6 == 5 else BASE
    m, s = edits(rnd, base, 'mine'), edits(rnd, base, 'srv')
    cases.append({'mine': m, 'srv': s, 'base': None if i % 10 == 9 else base, 'kind': base.get('kind')})

def page(br, path):
    c = br.new_context(timezone_id='Europe/London')
    c.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    c.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=path, content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = c.new_page(); pg.on('pageerror', lambda e: errs.append(os.path.basename(path) + ': ' + str(e)))
    pg.goto('https://sorted.test/#about'); wait(pg, 800)
    return c, pg

with sync_playwright() as p:
    br = p.chromium.launch()
    cn, new = page(br, HERE + '/tests/out/122_hook.html')
    co, old = page(br, HERE + '/tests/out/122_ref.html')
    bad, merged, kept_mine, named = [], 0, 0, 0
    for k in range(0, len(cases), 500):
        chunk = cases[k:k + 500]
        a = new.evaluate('cs=>__m(cs)', chunk); o = old.evaluate('cs=>__m(cs)', chunk)
        for i, (x, y) in enumerate(zip(a, o)):
            if x != y: bad.append(k + i)
            if x['toast']: merged += 1
            if any('the other device’s' in e.get('label', '') for e in x['rec'].get('events', [])): named += 1
    ok(not bad, 'the merge gives exactly the v155 result (record, revision, agreed copy and message) on all %d generated three-way changes: %s' % (len(cases), bad[:5]))
    ok(merged > 1000 and named > 100, 'the cases cover real merges (%d said they merged, %d named a field both devices changed)' % (merged, named))
    cn.close(); co.close(); br.close()
PAGE = open(HERE + '/public/index.html', encoding='utf8').read()
i = PAGE.index('function mergeRec156('); j = PAGE.index('function mergeInto(', i)
core = PAGE[i:j]
import re
ok(not re.search(r'[^A-Za-z0-9_.]t\.|[^A-Za-z0-9_]t\[|S\.|toast\(|nowIso\(', core), 'mergeRec156 reads only its three copies and the kind: no case, no app state, no clock, no message')
finish()
