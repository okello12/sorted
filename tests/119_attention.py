# v150: attention(t), the attention extraction step 1. One record per case per draw answers "what needs attention":
# state, priority, why it leads, the quick answer, your own deadline, Later, the next step and the reminder's day.
# The old functions still work and, while a screen is drawn, read the same record. This test builds a varied Home
# (overdue, due today, waiting, your step, a check day, a parking notice, a deadline on you, Later, finished) and checks:
# the record equals the old answers computed fresh; it is kept only during a draw; each case is worked out once per
# draw; Home, the case page and Cases agree; and a mutation between draws is seen at once.
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *

FIELDS = "['state','prio','why','q','snoozed','next']"
CMP = """(()=>{var F=ATT150.F,out=[];S.tasks.forEach(function(t){var a=attention(t),o={state:F.state(t),prio:F.prio(t),why:F.why(t),q:F.q(t),snoozed:F.snoozed(t),next:F.next(t)};
  %s.forEach(function(k){if(JSON.stringify(a[k])!==JSON.stringify(o[k]))out.push(t.title+' '+k+': '+JSON.stringify(a[k])+' vs '+JSON.stringify(o[k]))});
  var od=F.own(t),ad=a.own;if(JSON.stringify(od)!==JSON.stringify(ad))out.push(t.title+' own');
  var dd=F.due(t);if(String(dd)!==String(a.due))out.push(t.title+' due')});return out})()""" % FIELDS

A_ = '\nboot();\n})();\n'
SRC = open(HERE + '/tests/out/index.html', encoding='utf8').read(); assert SRC.count(A_) == 1
open(HERE + '/tests/out/119_hook.html', 'w', encoding='utf8').write(SRC.replace(A_, '\nwindow.S=S;window.attention=attention;window.ATT150=ATT150;window.render=function(){return render()};window.state=function(t){return state(t)};window.go=function(v){return go(v)};\nboot();\n})();\n'))
with sync_playwright() as p:
    a = App(p, email=True); pg = a.pg
    a.ctx.route(lambda u: u.startswith('https://sorted.test/') and '/art/' not in u, lambda r: r.fulfill(path=HERE + '/tests/out/119_hook.html', content_type='text/html'))
    a.home()
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
    bad = pg.evaluate(CMP)
    ok(not bad, 'the record equals the old answers for every case: %s' % bad[:4])
    n = pg.evaluate("S.tasks.length")
    ok(n >= 9, 'a varied Home (%d cases)' % n)
    # once per case per draw
    calls = pg.evaluate("""(()=>{var n=0,o=ATT150.F.due;ATT150.F.due=function(t){n++;return o.apply(this,arguments)};try{render()}finally{ATT150.F.due=o}return n})()""")
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
    bad = pg.evaluate(CMP); ok(not bad, 'and the record still agrees on the case page: %s' % bad[:4])
    a.tap('cases'); bad = pg.evaluate(CMP); ok(not bad, 'and on Cases: %s' % bad[:4])
    # 100 cases: one draw, each case once
    pg.evaluate("""(()=>{var base=S.tasks[0];for(var i=0;i<90;i++){var c=JSON.parse(JSON.stringify(base));c.id='x150-'+i;c.title='Copy '+i;S.tasks.push(c)}})()""")
    r = pg.evaluate("""(()=>{var n=0,o=ATT150.F.prio;ATT150.F.prio=function(t){n++;return o.apply(this,arguments)};go({name:'home'});n=0;var t0=performance.now();render();var ms=performance.now()-t0;ATT150.F.prio=o;return [n,S.tasks.length,ms]})()""")
    ok(r[0] <= r[1], 'with %d cases each priority is worked out once per draw (%d), drawn in %d ms' % (r[1], r[0], r[2]))
    a.close()
finish()
