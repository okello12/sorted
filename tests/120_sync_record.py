# v154: the saving extraction, step 1. syncState(x) and syncOf(t) answer "where is this record saved?" once, and
# syncText, syncAll and pendingRecs read them. This test compares those three with the page as it was at v153
# (tests/make_ref.js), on every combination of the flags they read: saving, not yet sent, a confirmed revision, too
# big (by flag or by the server's refusal), an example case, a move as well as a case, signed out, a guest or an
# email account, online or offline. Test 71 walks the real flow (saving, a failed save, offline, sign-out).
import os, sys, json, subprocess, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *

A_ = '\nboot();\n})();\n'
EXPOSE = '\nwindow.S=S;window.__sync={text:function(t){return syncText(t)},all:function(){return syncAll()},pending:function(){return pendingRecs().map(function(x){return x.id})}};\nboot();\n})();\n'
SRC = open(HERE + '/tests/out/index.html', encoding='utf8').read(); assert SRC.count(A_) == 1
open(HERE + '/tests/out/120_hook.html', 'w', encoding='utf8').write(SRC.replace(A_, EXPOSE))
subprocess.run(['node', HERE + '/tests/make_ref.js', 'build153.js', 'ee202b9619dc17c5dbfeaa84ceeac389f2272a01'], check=True, capture_output=True)
REF = open(HERE + '/tests/out/ref153.html', encoding='utf8').read(); assert REF.count(A_) == 1
open(HERE + '/tests/out/120_ref.html', 'w', encoding='utf8').write(REF.replace(A_, EXPOSE))

FLAGS = ['_saving', '_dirty', 'rev', '_big', '_refused', 'example']
recs = []
for i, bits in enumerate(itertools.product([0, 1], repeat=len(FLAGS))):
    r = {'id': 'r%d' % i, 'title': 'Case %d' % i, 'board': 'yours', 'promises': [], 'moves': [], 'events': []}
    for f, b in zip(FLAGS, bits):
        if b: r[f] = {'rev': 3, '_refused': '23514 data_size'}.get(f, True)
    recs.append(r)
USERS = [None, {'id': 'u-g'}, {'id': 'u-e', 'email': 'me@example.com'}]
RUN = """([recs,user,off])=>{S.user=user;S.offline=off;var t=recs.slice(0,40),m=recs.slice(40).map(function(x){var y=Object.assign({},x);y.kind='moment';return y});S.tasks=t;S.moments=m;
  var o={text:recs.map(function(r,i){return __sync.text(i<40?t[i]:m[i-40])}),all:__sync.all(),pending:__sync.pending()};S.user=null;S.tasks=[];S.moments=[];S.offline=false;return o}"""

def page(b, path):
    c = b.new_context(timezone_id='Europe/London')
    c.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    c.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=path, content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = c.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#about'); wait(pg, 800)
    return c, pg

with sync_playwright() as p:
    b = p.chromium.launch()
    cn, new = page(b, HERE + '/tests/out/120_hook.html')
    cr, ref = page(b, HERE + '/tests/out/120_ref.html')
    bad, n = [], 0
    for user in USERS:
        for off in (False, True):
            a = new.evaluate(RUN, [recs, user, off]); o = ref.evaluate(RUN, [recs, user, off]); n += len(recs)
            for i, (x, y) in enumerate(zip(a['text'], o['text'])):
                if x != y: bad.append('%s %s off=%s: %r vs %r' % (recs[i]['id'], user and user['id'], off, x, y))
            if a['all'] != o['all']: bad.append('all %s off=%s: %r vs %r' % (user and user['id'], off, a['all'], o['all']))
            if a['pending'] != o['pending']: bad.append('pending %s off=%s' % (user and user['id'], off))
    ok(n == 64 * 6 and not bad, 'syncText, syncAll and pendingRecs give the v153 answers on %d records (64 flag combinations, cases and moves, signed out, guest and email, online and offline): %s' % (n, bad[:4]))
    PAGE = open(HERE + '/public/index.html', encoding='utf8').read()
    ok('syncText142' not in PAGE and PAGE.count('function syncState(x)') == 1 and PAGE.count('function syncOf(t)') == 1, 'the v143 wrapper is gone and the record is defined once')
    cn.close(); cr.close(); b.close()
finish()
