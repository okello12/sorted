# v111: a calmer Home and case page. A newcomer sees the purpose, six fully readable ways in and one example; anyone with
# a saved case sees their cases first, with "+ New" beside the heading and the ways in under "Sort something new";
# a quiet spotlight with "Next up" and a reason only when there is one; rows that are orange only when something
# needs attention, with the word for it; dates in words; the promise in one line that wraps; quiet buttons; fewer
# headings; the timeline without the reference twice; the next action named for the task; Account; "all caught up";
# nothing scrolling sideways at 320px or at 200% text; the new controls reachable by keyboard.
import os, sys, json, datetime, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
DAYS = r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) \d{1,2} (?:January|February|March|April|May|June|July|August|September|October|November|December)'
def fits(pg): return pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth+1")
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    def poke(js): pg.evaluate("(js)=>{var d=JSON.parse(localStorage.getItem('__mockdb'));(new Function('d',js))(d);localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", js)
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    # 1 a newcomer: the purpose, six readable routes, one example, then the box
    pg.goto('https://sorted.test/'); wait(pg, 800)
    m = pg.inner_text('main'); ch = pg.locator('#cap82-start')
    ok(ch.count() == 1 and ch.evaluate("e=>getComputedStyle(e).display") != 'none', 'a newcomer sees the ways in on Home')
    ok('Keep everyday admin moving.' in m, 'the purpose comes before the choices')
    ok(m.index('Keep everyday admin moving.') < m.index("Something's broken") < m.index('Waiting for a repair? Save what they promised'), 'purpose, then the routes, then one concrete example')
    ok(ch.locator('.cap82-card').count() == 6 and ch.locator('.cap82-card').evaluate_all("es=>es.every(e=>{var s=e.querySelector('strong');return s.scrollWidth<=s.clientWidth+1&&e.getBoundingClientRect().right<=innerWidth})"), 'six routes, every label fully readable, none cut off')
    ok('Swipe for more' not in m, 'no "Swipe for more"')
    ok(pg.locator('.navq[data-a=data]').inner_text().strip() == 'Account', 'the top right says Account')
    ok(fits(pg), 'nothing scrolls sideways')
    pg.locator('[data-cap82=promise]').first.click(); wait(pg, 500)
    ok(pg.locator('.gi-form').count() == 1 or pg.locator('#gi-what').count() == 1 or pg.locator('#f-case').count() == 1, 'a route still opens its questions')
    # 2 returning: cases first; + New beside the heading; the ways in under Sort something new; every route still works
    def start(text):
        pg.goto('https://sorted.test/'); wait(pg, 500)
        if pg.locator('[data-cap82=other]').count(): pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg)
        elif pg.locator('[data-a=compose]').count(): pg.locator('[data-a=compose]').first.evaluate('e=>e.click()'); wait(pg)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
        if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
        return cases()[-1]['id']
    fri = datetime.date.today() + datetime.timedelta(days=(4 - datetime.date.today().weekday()) % 7 or 7)
    sky = start("Sky said an engineer would come %s between 8 and 12, ref AB123" % fri.strftime('%A'))
    cur = start("Currys said they would refund £89 by %s, order 445566" % fri.strftime('%A'))
    bur = start("Submit bursary documents")
    scr = start("The screen is broken")
    pg.goto('https://sorted.test/'); wait(pg, 800); m = pg.inner_text('main')
    ok(pg.locator('.home44-intro').count() == 1 and pg.locator('.home44-intro').bounding_box()['y'] < pg.locator('#home111-new').bounding_box()['y'], 'with cases, Needs you comes before the ways in')
    ok(pg.locator('.home44-intro .home111-newbtn').count() == 1, '+ New sits beside the heading')
    ok('Deal with this first' not in m and 'next up' in m.lower(), 'the spotlight says Next up; no "Deal with this first"')
    ok(pg.locator('#home111-new #cap82-start').count() == 1 and not pg.locator('#cap82-start').is_visible() and pg.locator('[data-a=compose]').is_visible(), 'the ways in live under Sort something new, closed until asked (v113)')
    y0 = pg.evaluate('scrollY'); pg.click('.home111-newbtn'); wait(pg, 900)
    ok(pg.evaluate('scrollY') > y0 and pg.evaluate("document.activeElement&&document.activeElement.classList.contains('cap82-card')"), '+ New goes to the ways in and puts focus on the first route')
    ok(pg.locator('#cap82-start .cap82-card').evaluate_all("es=>es.every(e=>{var s=e.querySelector('strong');return s.scrollWidth<=s.clientWidth+1})") and pg.locator('#cap82-start .cap82-grid').evaluate("e=>e.scrollWidth<=e.clientWidth"), 'the six routes stay fully readable for a returning person')
    for door in ['promise', 'fix', 'call', 'chase', 'document', 'renew']:
        pg.goto('https://sorted.test/'); wait(pg, 500); pg.click('.home111-newbtn'); wait(pg, 500); pg.locator('#cap82-start [data-cap82=%s]' % door).first.click(); wait(pg, 500)
        ok(pg.locator('.gi-form, #gi-what, #f-case, form[data-f=gi]').count() >= 1, 'route "%s" opens its questions from Sort something new' % door)
    pg.goto('https://sorted.test/'); wait(pg, 500); pg.locator('[data-a=compose]').first.evaluate('e=>e.click()'); wait(pg, 400)
    ok(pg.locator('#f-case').count() == 1, 'the box still opens from Sort something new')
    # 3 the spotlight: a quiet card; a reason only when there is one
    poke("var x=d.tasks.find(y=>y.data.title&&/bursary/.test(y.data.title)).data;x.mode='do';x.moves=[{id:'m1',what:'Submit the documents',dueAt:new Date(Date.now()+5*864e5).toISOString(),allDay:true,by:true,status:'open',loggedAt:new Date().toISOString()}]")
    pg.goto('https://sorted.test/'); wait(pg, 700)
    sp = pg.locator('.home44-spot'); st = sp.inner_text()
    ok(sp.count() == 1 and 'next up' in st.lower() and 'passed' not in st and 'Overdue' not in st, 'a future own step: Next up with no invented reason')
    ok(sp.evaluate("e=>{var cs=getComputedStyle(e);return cs.backgroundImage==='none'&&cs.boxShadow==='none'}"), 'the card is flat: no gradient, no shadow')
    ok(sp.evaluate("e=>{var t=e.querySelector('.home44-spot-title'),q=e.querySelector('.home44-question'),m=e.querySelector('.home44-meta');var f=x=>parseFloat(getComputedStyle(x).fontSize),w=x=>parseInt(getComputedStyle(x).fontWeight);return t&&q&&m&&f(t)>f(q)&&f(q)>f(m)&&w(t)>w(q)&&getComputedStyle(m).fontFamily===getComputedStyle(q).fontFamily}"), 'title, step and date each lighter than the last; the date in body type')
    ok(sp.locator('.home44-actions .btn').count() == 2 and abs(sp.locator('.home44-actions .btn').nth(0).bounding_box()['width'] - sp.locator('.home44-actions .btn').nth(1).bounding_box()['width']) < 2, 'the two buttons are the same width')
    poke("var x=d.tasks.find(y=>y.data.id==='%s').data;x.promises.forEach(q=>{if(q.status==='open'){q.dueAt=new Date(Date.now()-2*864e5).toISOString();if(q.dueEnd)q.dueEnd=new Date(Date.now()-2*864e5+36e5).toISOString()}})" % sky)
    pg.goto('https://sorted.test/'); wait(pg, 700); st = pg.locator('.home44-spot').inner_text()
    ok('Sky' in st and 'The date they gave has passed' in st, 'a passed date is the reason shown')
    # 4 rows: quiet unless something needs attention, and then a word
    poke("var x=d.tasks.find(y=>y.data.id==='%s').data;x.promises.forEach(q=>{if(q.status==='open'){q.status='missed';q.closedAt=new Date().toISOString()}});x.board='yours'" % cur)
    pg.goto('https://sorted.test/'); wait(pg, 700)
    rows = pg.locator('.home44-section.needs .home44-row')
    hot = pg.locator('.home44-section.needs .home44-row.home111-hot'); quiet = pg.locator('.home44-section.needs .home44-row:not(.home111-hot)')
    ok(hot.count() >= 1 and 'missed' in hot.first.locator('.home44-pill').inner_text().lower(), 'a case with a missed date is marked, with the word for it (%s)' % (hot.first.locator('.home44-pill').inner_text() if hot.count() else ''))
    ok(quiet.count() >= 1 and quiet.first.locator('.home44-pill').count() == 0 and quiet.first.evaluate("e=>getComputedStyle(e).borderLeftWidth") == '1px', 'an ordinary open case is quiet: no pill, no orange edge')
    ok(hot.first.evaluate("e=>getComputedStyle(e).borderLeftWidth") == '4px', 'the marked case has the accent edge')
    # 5 dates in words
    w = pg.locator('.home44-section.waiting').inner_text() if pg.locator('.home44-section.waiting').count() else pg.inner_text('main')
    ok(re.search(DAYS, w) and not re.search(r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),? \d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\b', w), 'dates are written out (%s)' % (re.search(DAYS, w).group(0) if re.search(DAYS, w) else w[:80]))
    # 6 the case page: one wrapping line, the quote, quiet buttons, fewer headings, no reference twice
    poke("var x=d.tasks.find(y=>y.data.id==='%s').data;x.promises.forEach(q=>{q.status='open';q.dueAt=new Date(Date.now()+3*864e5).toISOString().slice(0,10)+'T08:00:00.000Z';q.dueEnd=new Date(Date.now()+3*864e5).toISOString().slice(0,10)+'T12:00:00.000Z';q.allDay=false;q.by=false;delete q.closedAt});x.board='waiting'" % sky)
    pg.goto('https://sorted.test/?task=%s' % sky); wait(pg, 700)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    m = pg.inner_text('main'); line = pg.locator('.promise-line')
    ok(line.count() == 1 and re.search(r'^Sky, ' + DAYS + r', (?:8am|9am) to (?:12pm|1pm)$', line.inner_text().strip()) is not None, 'the promise is one line: who, day, time (%r)' % line.inner_text())
    ok(line.evaluate("e=>getComputedStyle(e).whiteSpace") in ('normal', 'pre-wrap') and pg.locator('.promise-quote').count() == 1 and '“' in pg.locator('.promise-quote').inner_text(), 'it wraps naturally, and their words are quoted beneath')
    ok(pg.locator('.promise-acts .btn.quiet').count() == 2 and pg.locator('.promise .link:visible:not(.p-cancel)').count() == 0, 'the actions are a row of quiet buttons')
    ok('Keep the proof together' not in m and 'Case memory' not in m and 'Messages & evidence' in m and 'Timeline' in m, 'fewer headings inside headings')
    tl = pg.locator('.case56-thread').inner_text(); said = [l for l in tl.split('\n') if l.startswith('An engineer would come')]
    ok(said and said[0].count('AB123') == 1 and re.search(DAYS, said[0]), 'the timeline shows the reference once and the date in words (%r)' % (said[:1]))
    inset = pg.evaluate("()=>{var b=document.querySelector('.case75-group-body');if(!b)return null;var r=b.getBoundingClientRect();var h=b.querySelector('h2');return h?h.getBoundingClientRect().left-r.left:null}")
    ok(inset is not None and inset >= 14, 'content inside an opened section has an inset (%s)' % inset)
    ok(fits(pg), 'the case page fits')
    pg.set_viewport_size({'width': 320, 'height': 844}); pg.goto('https://sorted.test/?task=%s' % sky); wait(pg, 600)
    ok(fits(pg) and pg.locator('.promise-line').evaluate("e=>e.getBoundingClientRect().height") > 24, 'at 320px the promise line wraps and the page fits')
    pg.set_viewport_size({'width': 390, 'height': 844})
    # 7 the next action named for the task
    pg.goto('https://sorted.test/?task=%s' % bur); wait(pg, 700)
    poke("var x=d.tasks.find(y=>y.data.id==='%s').data;x.moves=[]" % bur); pg.goto('https://sorted.test/?task=%s' % bur); wait(pg, 700)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 300)
    m = pg.inner_text('main')
    ok('Set a reminder to submit' in m and 'Add a reply or promise' in m and pg.locator('.home111-finish').count() == 1, 'the idle card names the action: "Set a reminder to submit", "Add a reply or promise", Finish quiet')
    # 8 all caught up
    poke("d.tasks.forEach(y=>{var x=y.data;if(x.kind!=='moment'){x.board='done';x.outcome='Sorted';(x.promises||[]).forEach(q=>{if(q.status==='open')q.status='kept'});(x.moves||[]).forEach(q=>{if(q.status==='open')q.status='done'})}})")
    pg.goto('https://sorted.test/'); wait(pg, 800); m = pg.inner_text('main')
    ok('You’re all caught up.' in m and pg.locator('#cap82-start').count() == 1 and pg.locator('.home44-done[open]').count() == 1 and pg.locator('.home111-newbtn').count() == 1, 'with every case finished: all caught up, the ways in, Done open, + New')
    ok('Keep everyday admin moving.' not in m, 'a person with finished cases is not treated as a newcomer')
    # 9 narrow and large text; keyboard
    for vw in (320, 390):
        pg.set_viewport_size({'width': vw, 'height': 844}); pg.goto('https://sorted.test/'); wait(pg, 600)
        ok(fits(pg), 'Home fits at %dpx' % vw)
        pg.evaluate("document.documentElement.style.fontSize='200%'"); wait(pg, 300)
        ok(fits(pg), 'Home fits at %dpx and 200%% text' % vw)
        pg.evaluate("document.documentElement.style.fontSize=''")
    pg.set_viewport_size({'width': 390, 'height': 844}); pg.goto('https://sorted.test/'); wait(pg, 600)
    pg.locator('.home111-newbtn').focus(); ok(pg.evaluate("document.activeElement&&document.activeElement.classList.contains('home111-newbtn')"), '+ New can take keyboard focus')
    pg.keyboard.press('Enter'); wait(pg, 900)
    ok(pg.evaluate("document.activeElement&&document.activeElement.classList.contains('cap82-card')"), 'Enter on it lands on the first route')
    pg.keyboard.press('Tab'); ok(pg.evaluate("document.activeElement&&document.activeElement.classList.contains('cap82-card')"), 'Tab moves to the next route')
    pg.evaluate("document.querySelector('.cap95-row .cap95-chip').focus()"); ok(pg.evaluate("document.activeElement&&document.activeElement.classList.contains('cap95-chip')"), 'the example strip is reachable by keyboard')
    print('CHECKS', n[0]); b.close()
print('ERRORS', errs); print('FAILS', fails)
