# v157: the saving extraction, the read side. readKind157 decides what a copy read from the server means for this
# phone (redel, revive, skip, gone, new, own, merge, adopt) and ap143 acts on it; the v145 wrappers round ap143,
# gonePersist143 and conf143 are folded in. This test applies the same server copy to the same phone state on this page
# and on the page as it was at v156 (tests/make_ref.js), for every combination of: no record here, or one that is
# saved, unsaved, mid-save, deleted here, an example, with this phone's own write id; a server copy that is missing,
# older, the same, newer, for another id, an Undo made before or after this phone's deletion; a tombstone and a
# re-delete note on this phone, old or new; a case or a move. What ap143 returns, the records left on the phone (with
# their unsaved flags), the tombstones and re-delete notes, and whether a save was started must all be identical.
import os, sys, json, subprocess, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import ok, wait, errs, fails, finish, HERE
from playwright.sync_api import sync_playwright

A_ = '\nboot();\n})();\n'
PROBE = r'''window.__rd=function(cases){var out=[];cases.forEach(function(c){
  S.user=null;S.gone={};S.tasks=[];S.moments=[];localStorage.removeItem("sorted.gone.none");localStorage.removeItem("sorted.redel.none");
  if(c.gone)localStorage.setItem("sorted.gone.none",JSON.stringify({x1:c.gone}));if(c.redel)localStorage.setItem("sorted.redel.none",JSON.stringify({x1:c.redel}));if(c.memGone)S.gone.x1=1;
  if(c.local){var t=JSON.parse(JSON.stringify(c.local));if(c.local._base)t._base=JSON.stringify(c.local._base);if(t.kind==="moment")S.moments.push(t);else S.tasks.push(t)}
  var st=window.setTimeout,n=0,ts=toast;window.setTimeout=function(f,d){if(!d)n++;return 0};toast=function(){};var k;
  try{k=ap143("x1",c.srv===null?null:JSON.parse(JSON.stringify(c.srv)))}finally{window.setTimeout=st;toast=ts}
  var recs=S.tasks.concat(S.moments).map(function(x){var o=clean(x);(o.events||[]).forEach(function(e){if(/^Merged with/.test(e.label))e.at="(now)"});return {rec:o,dirty:!!x._dirty,again:!!x._again,base:x._base||null}});
  out.push({k:k,recs:recs,gone:Object.keys(JSON.parse(localStorage.getItem("sorted.gone.none")||"{}")).map(function(k){var v=JSON.parse(localStorage.getItem("sorted.gone.none"))[k];return k+(v===c.gone?"=kept":"=new")}).join(),redel:localStorage.getItem("sorted.redel.none"),mem:JSON.stringify(S.gone),saves:n});
  persist=null});S.tasks=[];S.moments=[];return out}; var persist;'''
EXPOSE = '\n' + PROBE + '\nboot();\n})();\n'
SRC = open(HERE + '/tests/out/index.html', encoding='utf8').read(); assert SRC.count(A_) == 1
open(HERE + '/tests/out/123_hook.html', 'w', encoding='utf8').write(SRC.replace(A_, EXPOSE))
subprocess.run(['node', HERE + '/tests/make_ref.js', 'build156.js', '318ad4bb5be4745688ccf67bf7f2455bec72a722'], check=True, capture_output=True)
REF = open(HERE + '/tests/out/ref156.html', encoding='utf8').read(); assert REF.count(A_) == 1
open(HERE + '/tests/out/123_ref.html', 'w', encoding='utf8').write(REF.replace(A_, EXPOSE))

T = 1791500000000  # a fixed moment, in milliseconds
iso = lambda ms: __import__('datetime').datetime.utcfromtimestamp(ms / 1000).strftime('%Y-%m-%dT%H:%M:%S.000Z')
BASE = {'id': 'x1', 'title': 'Currys refund', 'board': 'waiting', 'rev': 3, 'events': [{'at': '2026-10-01T09:00:00.000Z', 'label': 'Started.'}], 'promises': [], 'moves': []}
LOCALS = {
    'none': None,
    'saved': dict(BASE, _base=BASE),
    'unsaved': dict(BASE, _dirty=True, _base=BASE, title='Edited here'),
    'own': dict(BASE, _dirty=True, _base=BASE, title='Edited here', _wp=[{'w': 'W-own', 'rev': 4}]),
    'saving': dict(BASE, _saving=True, _base=BASE),
    'deleted': dict(BASE, _deleted=True),
    'example': dict(BASE, example=True),
    'norev': dict(BASE, rev=0),
    'move': dict(BASE, kind='moment', title='Moving home', _base=dict(BASE, kind='moment')),
}
SRVS = {
    'missing': None,
    'older': dict(BASE, rev=2),
    'same': dict(BASE),
    'newer': dict(BASE, rev=4, title='Renamed elsewhere', wid='W-other', events=BASE['events'] + [{'at': '2026-10-02T09:00:00.000Z', 'label': 'From elsewhere'}]),
    'own-write': dict(BASE, rev=4, title='Edited here', wid='W-own'),
    'wrong-id': dict(BASE, id='x2', rev=4),
    'undo-late': dict(BASE, rev=4, revived=iso(T)),
    'undo-early': dict(BASE, rev=4, revived=iso(T - 600000)),
    'not-a-record': 'oops',
}
cases = []
for (ln, l), (sn, s), gone, redel, mem in itertools.product(LOCALS.items(), SRVS.items(), [None, T - 60000, T + 600000], [None, T - 60000, T + 600000], [False, True]):
    if ln == 'move' and s not in (None, 'oops') and isinstance(s, dict): s = dict(s, kind='moment')
    cases.append({'name': '%s/%s/g%s/r%s/m%d' % (ln, sn, gone and (gone - T), redel and (redel - T), mem), 'local': l, 'srv': s, 'gone': gone, 'redel': redel, 'memGone': mem})

def page(br, path):
    c = br.new_context(timezone_id='Europe/London')
    c.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    c.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=path, content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = c.new_page(); pg.on('pageerror', lambda e: errs.append(os.path.basename(path) + ': ' + str(e)))
    pg.goto('https://sorted.test/#about'); wait(pg, 800)
    return c, pg

with sync_playwright() as p:
    br = p.chromium.launch()
    cn, new = page(br, HERE + '/tests/out/123_hook.html')
    co, old = page(br, HERE + '/tests/out/123_ref.html')
    a = new.evaluate('cs=>__rd(cs)', cases); o = old.evaluate('cs=>__rd(cs)', cases)
    bad = [c['name'] + ': %s vs %s' % (x['k'], y['k']) for c, x, y in zip(cases, a, o) if x != y]
    kinds = sorted(set(str(x['k']) for x in a))
    ok(not bad, 'every server copy applied to every phone state gives the v156 result on all %d combinations: %s' % (len(cases), bad[:5]))
    ok(set(['0', 'gone', 'new', 'own', 'merge', 'adopt']) <= set(kinds), 'the combinations reach every outcome: %s' % kinds)
    nsav = sum(1 for x in a if x['saves']); ndrop = sum(1 for c, x in zip(cases, a) if c['redel'] and x['redel'] in (None, '{}')); nnew = sum(1 for x in a if '=new' in x['gone'])
    ok(nsav > 50 and ndrop > 0 and nnew > 10, 'and every side effect: %d started a save, %d dropped a re-delete note (an Undo after the deletion), %d added a tombstone' % (nsav, ndrop, nnew))
    cn.close(); co.close(); br.close()
PAGE = open(HERE + '/public/index.html', encoding='utf8').read()
ok(not any(x in PAGE for x in ('_ap145', '_gp145', '_cf145')) and PAGE.count('function readKind157(') == 1, 'the v145 wrappers round ap143, gonePersist143 and conf143 are folded in, and the decision is defined once')
finish()
