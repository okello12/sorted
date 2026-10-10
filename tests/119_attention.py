# v150 to v153: attention(t), the attention extraction. One record per case per draw answers "what needs attention":
# state, priority, why it leads, the quick answer, your own deadline, Later, the next step and the reminder's day.
# Since v153 the old function bodies are gone from the page, so the reference is the page as it was at v152, built by
# tests/make_ref152.js and opened in a separate browser context: its ATT150.F still holds the old functions. This test
# builds a varied Home (overdue, due today, waiting, your step, a check day, a parking notice, a deadline on you,
# Later, finished) and checks: every field equals the old answers, on every case and on 1,872 variations of their
# dates; the record is kept only during a draw; each case is worked out once per draw; Home, the case page and Cases
# agree; a mutation between draws is seen at once; and the old bodies and scaffolding are gone from the page.
import os, sys, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *

FIELDS = ['state', 'prio', 'why', 'q', 'snoozed', 'next', 'own', 'due']
# the same cases, read by the new rules (attention) or the old functions (F, in the reference page)
NEWF = "(cs)=>cs.map(function(t){var a=attention(t);return {state:a.state,prio:a.prio,why:a.why,q:a.q,snoozed:a.snoozed,next:a.next,own:JSON.stringify(a.own),due:String(a.due)}})"
OLDF = "(cs)=>cs.map(function(t){return {state:F.state(t),prio:F.prio(t),why:F.why(t),q:F.q(t),snoozed:F.snoozed(t),next:F.next(t),own:JSON.stringify(F.own(t)),due:String(F.due(t))}})"
VARS = r'''(()=>{var H=36e5,D=864e5,offs=[null,-5*D,-26*H,-3*H,-1*H,0.5*H,2*H,10*H,20*H,30*H,3*D,10*D,40*D],out=[];
  S.tasks.forEach(function(base){offs.forEach(function(po){[null,-2*D,-2*H,0.5*H,6*H,30*H,5*D,35*D].forEach(function(mo){[false,true].forEach(function(miss){
    var t=JSON.parse(JSON.stringify(base));t.promises=(t.promises||[]).filter(function(q){return q.status!=='open'});
    if(miss)t.promises.push({id:'pm',status:'missed',party:'X',said:'x',dueAt:new Date(Date.now()-3*D).toISOString(),allDay:true,by:true});
    if(po!==null)t.promises.push({id:'po',status:'open',party:'X',said:'They will do it',dueAt:new Date(Date.now()+po).toISOString(),dueEnd:po%D===0?null:new Date(Date.now()+po+2*H).toISOString(),allDay:po%D===0,by:po%D===0,prec:'day'});
    t.moves=(t.moves||[]).filter(function(x){return x.status!=='open'});
    if(mo!==null)t.moves.push({id:'mo',what:'Phone them',status:'open',loggedAt:new Date().toISOString(),dueAt:new Date(Date.now()+mo).toISOString(),allDay:false});
    if(t.board==='done'&&(po!==null||mo!==null))t.board='yours';
    t.title=(t.title||'')+' p'+po+' m'+mo+(miss?' miss':'');out.push(t)})})})});return out})()'''

A_ = '\nboot();\n})();\n'
SRC = open(HERE + '/tests/out/index.html', encoding='utf8').read(); assert SRC.count(A_) == 1
open(HERE + '/tests/out/119_hook.html', 'w', encoding='utf8').write(SRC.replace(A_, '\nwindow.S=S;window.attention=attention;window.ATT150=ATT150;window.__wrapCalc=function(fn){var o=att150Calc;att150Calc=function(t){fn(t);return o(t)};return function(){att150Calc=o}};window.render=function(){return render()};window.state=function(t){return state(t)};window.go=function(v){return go(v)};\nboot();\n})();\n'))
subprocess.run(['node', HERE + '/tests/make_ref152.js'], check=True, capture_output=True)
REF = open(HERE + '/tests/out/ref152.html', encoding='utf8').read(); assert REF.count(A_) == 1
open(HERE + '/tests/out/119_ref.html', 'w', encoding='utf8').write(REF.replace(A_, '\nwindow.F=ATT150.F;window.S=S;\nboot();\n})();\n'))

def compare(pg, ref, cases):
    new = pg.evaluate(NEWF, cases); old = ref.evaluate(OLDF, cases); bad = []
    for t, a, o in zip(cases, new, old):
        for k in FIELDS:
            if a[k] != o[k]: bad.append('%s %s: %r vs %r' % (t.get('title'), k, a[k], o[k]))
    return bad

with sync_playwright() as p:
    a = App(p, email=True); pg = a.pg
    a.ctx.route(lambda u: u.startswith('https://sorted.test/') and '/art/' not in u, lambda r: r.fulfill(path=HERE + '/tests/out/119_hook.html', content_type='text/html'))
    a.home()
    # the reference: v152, in a context of its own (its own storage, nobody signed in)
    rctx = a.b.new_context(timezone_id='Europe/London')
    rctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    rctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/119_ref.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    ref = rctx.new_page(); ref.on('pageerror', lambda e: errs.append('ref: ' + str(e)))
    ref.goto('https://sorted.test/#about'); wait(ref, 800)
    ok(ref.evaluate("typeof F==='object'&&typeof F.next==='function'"), 'the v152 reference page has the old functions')
    c1 = a.start('Currys said the refund of £40 would be in my account by %s' % long(day(3)))
    c2 = a.start('BT said an engineer would come on %s between 8 and 12' % long(day(5)))
    c3 = a.start('Evri said the parcel would arrive by %s' % long(day(2))); a.overdue(c3, 2)
    c4 = a.start('Aviva said they would call me back')
    c5 = a.start('Camden Council: pay £65 within 14 days of %s' % long(day(-10)), confirm=False)
    c6 = a.start('DWP said my payment should arrive by %s' % long(day(1))); a.past_reading(c6)
    c7 = a.parking(4)
    c8 = a.start('Octopus said they would send the final bill by %s' % long(day(9)))
    a.task_js(c8, "t.snooze={until:new Date(Date.now()+864e5).toISOString(),at:new Date().toISOString()}")
    c9 = a.start('Thames Water said they would fix the leak by %s' % long(day(6)))
    a.task_js(c9, "t.board='done';t.outcome='Fixed';t.promises.forEach(function(q){q.status='kept'})")
    c10 = a.start('Screwfix said the drill would be ready to collect by %s' % long(day(1)))
    a.task_js(c10, "t.moves=(t.moves||[]).concat([{id:'m10',what:'Phone Screwfix',status:'open',loggedAt:new Date().toISOString(),dueAt:new Date(Date.now()-36e5).toISOString(),allDay:false}])")
    a.home()
    ok(pg.evaluate("typeof attention==='function'&&ATT150.memo===null"), 'attention() exists, and nothing is kept outside a draw')
    bad = compare(pg, ref, pg.evaluate('S.tasks'))
    ok(not bad, 'the record equals the old answers for every case: %s' % bad[:4])
    n = pg.evaluate("S.tasks.length")
    ok(n >= 9, 'a varied Home (%d cases)' % n)
    # once per case per draw
    calls = pg.evaluate("""(()=>{var n=0,undo=__wrapCalc(function(){n++});try{render()}finally{undo()}return n})()""")
    ok(0 < calls <= n, 'Home works each case out at most once per draw (%d for %d cases)' % (calls, n))
    ok(pg.evaluate("ATT150.memo===null&&ATT150.depth===0"), 'the record is dropped when the draw ends')
    # a change between draws is seen at once
    ch = pg.evaluate("""(()=>{var t=S.tasks.find(function(x){return x.id==='%s'});var before=state(t);t.board='done';var mid=state(t);render();var after=state(t);t.board='waiting';render();return [before,mid,after,state(t)]})()""" % c1)
    ok(ch[1] == 'done' and ch[2] == 'done' and ch[3] == ch[0], 'a change between draws is seen at once: %s' % ch)
    # Home, the case page and Cases tell the same story
    m = a.main()
    ok('Evri' in m and 'The date they gave has passed' in m, 'Home leads with the date that passed')
    ok('Back tomorrow' in m or 'Later' in m, 'Later is still Later')
    a.open(c3); mc = a.main()
    ok('tell Sorted whether' in mc.lower() or 'did they' in mc.lower() or 'did it' in mc.lower(), 'the case page asks the same question')
    a.open(c10); mc = a.main()
    ok('Phone Screwfix' in mc, 'your overdue step leads on the case')
    bad = compare(pg, ref, pg.evaluate('S.tasks')); ok(not bad, 'and the record still agrees on the case page: %s' % bad[:4])
    # every field, on 1,872 variations of the cases' dates, against the old functions
    cases = pg.evaluate(VARS); bad = compare(pg, ref, cases)
    ok(len(cases) > 1000 and not bad, 'every attention field (state, priority, why, quick answer, next step, Later, your deadline, reminder day) matches the old functions on %d variations of the cases’ dates: %s' % (len(cases), bad[:4]))
    # v153: the old bodies and the scaffolding are gone
    PAGE = open(HERE + '/public/index.html', encoding='utf8').read()
    gone = [x for x in ('ATT150.F', 'att150Use', '_hp143', '_hw143', '_ns143', '_nst144', '_snoozed143', 'ATT150.busy') if x in PAGE]
    ok(not gone, 'the old function bodies and the v150 to v152 scaffolding are gone from the page: %s' % gone)
    ok(PAGE.count('function state(t){return att152Field("state",t)}') == 1 and PAGE.count('function nextStepText(t){return att152Field("next",t)}') == 1, 'the old names are one-line calls to the attention rules')
    # 100 cases: one draw, each case once
    pg.evaluate("""(()=>{var base=S.tasks[0];for(var i=0;i<90;i++){var c=JSON.parse(JSON.stringify(base));c.id='x150-'+i;c.title='Copy '+i;S.tasks.push(c)}})()""")
    r = pg.evaluate("""(()=>{var n=0,undo=__wrapCalc(function(){n++});go({name:'home'});n=0;var t0=performance.now();render();var ms=performance.now()-t0;undo();return [n,S.tasks.length,ms]})()""")
    ok(r[0] <= r[1], 'with %d cases each case is worked out once per draw (%d), drawn in %d ms' % (r[1], r[0], r[2]))
    rctx.close(); a.close()
finish()
