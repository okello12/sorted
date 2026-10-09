# v145 (audit pass 3, reviewer D): what a person sees and reads, and the engineering health under it.
# 1 Escaping: one hostile value (an <i> tag and an <img onerror>) put into every field a person or another party can fill
#   (title, their words, who, refs, holder, your step, the call, corrections, history, kept document names, the ledger,
#   the helper's question, pack questions, helper notes, emailed replies, forwarded emails, the shared card) is shown as
#   text on Home, Cases, the case, every case panel, the shared page and in the pack, summary and chase: never as markup.
# 2 A date Sorted can't read (a corrupt or hand-edited record) is said in words on Home, Cases and the case, never
#   "Invalid Date", "NaN" or "12am to 12am"; the case still opens; no calendar button is offered for it.
# 3 If drawing a screen fails, the person gets a plain screen with Go to Home (and the tab bar), the error still reaches
#   the page error handler, and Home works again.
# 4 Performance: 50 kB pastes of every awkward shape through every reader in well under a second each; Home, Cases and a
#   case drawn with 100 cases quickly.
# 5 Copy and layout: no em dash, "undefined", "NaN", "Invalid Date", "null", pilot wording or straight apostrophe in
#   anything visible (the public pages, Home, Cases, More, every case and panel, at 320, 390 and 768px) or in the
#   generated pack, summary, chase, recap and calendar file; no brackets inside brackets; "the damp or mould" is fixed,
#   not "working again"; every page has a title; every control is at least 44px tall and has a name (links inside a
#   sentence excepted); nothing scrolls sideways.
# 6 A helper-notes switch the server refuses goes back and says so.
# 7 Code health: no duplicate top-level function, no console.log, the dead v142 originals and old views are gone; the
#   edge functions' visible copy has curly apostrophes and no em dash; SORTED_SHIFT_DAYS moves "today" in Python and
#   in the browser (tests/sitecustomize.py), for finding tests that pass only on one weekday or at one time of day.
import os, sys, json, re, datetime, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
today = datetime.date.today()
PAGE = open(HERE + '/public/index.html', encoding='utf8').read()
# a copy of the test page with a few internals exposed, for this file only (never the production page)
A_ = '\nboot();\n})();\n'
assert open(HERE + '/tests/out/index.html', encoding='utf8').read().count(A_) == 1
open(HERE + '/tests/out/113_hook.html', 'w', encoding='utf8').write(open(HERE + '/tests/out/index.html', encoding='utf8').read().replace(A_, '\nwindow.__d145={S:S,render:render,packText:packText,callDefaults:callDefaults,sumText137:sumText137,recapText:recapText,icsText:icsText,calPlan:calPlan,task:task,goalOf:goalOf};\nboot();\n})();\n'))
X = '<i class=x145>X</i><img src=x onerror="window.__x=(window.__x||[]).concat(1)">'
XJ = json.dumps(X)
BADTXT = re.compile(r'Invalid Date|NaN|undefined|\bnull\b|\[object|\bpilot\b|\u2014|\b[A-Za-z]+\'(?:s|t|re|ll|ve|d|m)\b|12am to 12am')

def context(b, w=390, h=844, page='index.html', scheme='light'):
    ctx = b.new_context(viewport={'width': w, 'height': h}, timezone_id='Europe/London', color_scheme=scheme)
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/' + page, content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    return ctx, pg

class App:
    def __init__(self, b, w=390, page='index.html', scheme='light'):
        self.ctx, self.pg = context(b, w, page=page, scheme=scheme); pg = self.pg
        pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')")
        pg.evaluate("localStorage.setItem('__mocksession', JSON.stringify({user:{id:'u-me',email:'me@example.com'}}))")
        pg.goto('https://sorted.test/'); wait(pg, 800)
    def db(self): return self.pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    def cases(self): return sorted([x['data'] for x in self.db().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    def case(self, cid): return [c for c in self.cases() if c['id'] == cid][0]
    def tap(self, a): self.pg.locator('.tab129 [data-a=%s]' % a).click(); wait(self.pg, 500)
    def home(self): self.pg.goto('https://sorted.test/'); wait(self.pg, 700)
    def open(self, cid): self.pg.goto('https://sorted.test/?task=%s' % cid); wait(self.pg, 700)
    def poke(self, js):
        pg = self.pg; pg.goto('https://sorted.test/'); wait(pg, 500)
        pg.evaluate("(js)=>{var db=JSON.parse(localStorage.getItem('__mockdb'));(new Function('db',js))(db);localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", js)
        pg.goto('https://sorted.test/'); wait(pg, 700)
    def task_js(self, cid, body): self.poke("db.tasks.forEach(function(r){if(r.data.id==='%s'){var t=r.data;%s}})" % (cid, body))
    def start(self, text):
        pg = self.pg; self.tap('new-case')
        pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
        for sel in ('[data-a=match-new]', '[data-a=vague-go]'):
            if pg.locator(sel).count(): pg.click(sel); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 700)
        return self.cases()[-1]['id']
    def panel(self, cid, p):
        pg = self.pg; self.open(cid)
        pg.evaluate("p=>{var b=document.createElement('button');b.setAttribute('data-a','panel');b.setAttribute('data-p',p);document.querySelector('main').appendChild(b);b.click()}", p); wait(pg, 350)

def markup(pg):
    return pg.evaluate("document.querySelectorAll('.x145,img[src=x]').length+(window.__x?window.__x.length:0)")
def shown(pg):
    return pg.evaluate("document.body.innerText.split('<i class=x145>').length-1")
def text_issues(pg):
    t = pg.evaluate("document.body.innerText")
    return sorted(set(t[max(0, m.start() - 40):m.end() + 25].replace('\n', ' | ') for m in BADTXT.finditer(t)))
def small_controls(pg):
    # inline links inside a sentence are exempt (WCAG 2.5.8); everything else a person taps must be 44px tall
    return pg.evaluate("""[...document.querySelectorAll('a[href],a[data-a],button,summary,input:not([type=hidden]):not([type=radio]):not([type=checkbox]),select,textarea,label.chip')].filter(e=>{
      if(!e.offsetParent)return false;var r=e.getBoundingClientRect();if(!r.width||r.height>=43.5)return false;if(e.classList.contains('sr-only'))return false;
      var cs=getComputedStyle(e);if(cs.display==='inline'&&e.parentElement&&/^(P|LI|SPAN|SMALL)$/.test(e.parentElement.tagName)&&e.parentElement.textContent.trim().length>e.textContent.trim().length+12)return false;
      return true}).map(e=>e.tagName+'.'+String(e.className).slice(0,24)+': '+(e.textContent||e.value||'').trim().slice(0,30)+' '+Math.round(e.getBoundingClientRect().height))""")
def unnamed(pg):
    return pg.evaluate("""[...document.querySelectorAll('button,a[href],input:not([type=hidden]),select,textarea')].filter(e=>e.offsetParent).filter(e=>{var n=(e.getAttribute('aria-label')||e.textContent||'').trim()||e.title||(e.labels&&e.labels.length&&e.labels[0].textContent.trim())||e.getAttribute('aria-labelledby')||e.placeholder;if(e.type==='submit'&&e.value)n=1;return !n}).map(e=>e.outerHTML.slice(0,100))""")
def sideways(pg): return pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth+1")

with sync_playwright() as p:
    b = p.chromium.launch()

    # ---- 7 code health (static) ----
    sc = re.findall(r'<script(?![^>]*src)[^>]*>(.*?)</script>', PAGE, re.S)
    main_js = max(sc, key=len)
    tops = re.findall(r'(?m)^function\s+([A-Za-z_$][\w$]*)\s*\(', main_js)
    dup = sorted(set(x for x in tops if tops.count(x) > 1))
    ok(not dup, 'no top-level function is declared twice (the later one would win silently): %s' % dup)
    ok('console.log' not in PAGE and 'debugger' not in PAGE, 'no console.log or debugger in the page')
    gone = ['calTimes142', 'laterSheet142', 'snoozeOpts142', 'snoozeSet142', 'anonNoteOld', 'docName0', 'evidenceBlock', 'landingExamples', 'viewHomeLegacy', 'startBtn', 'new-case-old', 'var PLANS=']
    ok(not [g for g in gone if g in PAGE], 'the dead originals and old views are gone: %s' % [g for g in gone if g in PAGE])
    ok('\u2014' not in re.sub(r'\[[^\]\n]*\u2014[^\]\n]*\]', '', PAGE), 'no em dash anywhere in the page outside the readers\u2019 character classes')
    ok('PRODID:-//Sorted//EN' in PAGE and 'PRODID:-//Sorted pilot' not in PAGE, 'the calendar file says "Sorted", not "Sorted pilot"')
    ok('where it stays until you delete it. Cases you haven’t' not in PAGE and 'Any case you haven’t touched for 90 days is deleted, finished or not' in PAGE, 'Help no longer says a finished case stays until you delete it and, in the next sentence, that it goes after 90 days')
    fn_bad = []
    for f in ('send-reminders', 'inbound-email', 'email-stop'):
        src = open(HERE + '/supabase/functions/%s/index.ts' % f, encoding='utf8').read()
        for i, l in enumerate(src.split('\n')):
            if l.strip().startswith('//'): continue
            for m in re.finditer(r'"([^"\n]*)"|`([^`\n]*)`', l):
                s = m.group(1) or m.group(2) or ''
                if re.search(r'[A-Za-z]\'(?:s|t|re|ll|ve|d|m)\b', s) or '\u2014' in s: fn_bad.append('%s:%d %s' % (f, i + 1, s[:60]))
    ok(not fn_bad, 'edge function copy has curly apostrophes and no em dash: %s' % fn_bad[:4])
    env = dict(os.environ, SORTED_SHIFT_DAYS='3', PYTHONPATH=HERE + '/tests', TZ='Europe/London')
    out = subprocess.run([sys.executable, '-c', "import datetime;from playwright.sync_api import sync_playwright\nwith sync_playwright() as p:\n b=p.chromium.launch();c=b.new_context();pg=c.new_page();pg.goto('data:text/html,x');print(datetime.date.today().isoformat(),pg.evaluate('new Date().toISOString().slice(0,10)'),pg.evaluate('new Date(2020,0,1).getFullYear()'))"], env=env, capture_output=True, text=True, cwd=HERE).stdout.split()
    want = (today + datetime.timedelta(days=3)).isoformat()
    ok(len(out) >= 5 and out[-3] == want and out[-2] == want and out[-1] == '2020', 'SORTED_SHIFT_DAYS=3 moves today in Python and the browser, and leaves explicit dates alone: %s' % out[-3:])

    # ---- 1 escaping ----
    a = App(b); pg = a.pg
    cid = a.start('Currys said they would refund £40 by Friday, ref CU123456')
    a.open(cid)
    pg.locator('details.case56-sharing summary').click(); wait(pg, 200)
    pg.click('[data-a=share]'); wait(pg, 600)
    if not pg.locator('details.case56-sharing[open]').count(): pg.locator('details.case56-sharing summary').click(); wait(pg, 200)
    pg.locator('[data-a=notes-toggle]').click(); wait(pg, 500)
    tok = a.case(cid)['shareToken']
    a.task_js(cid, """var X=%s,now=new Date().toISOString();t.title=X;t.said=X;t.promises[0].said=X;t.promises[0].party=X;t.promises[0].ref='R1'+X;t.promises[0].phrase=X;
      t.facts.party=X;t.facts.item=X;t.holder={to:X,from:X,said:X,src:'x',at:now,st:'confirmed'};
      t.refs=[{k:'claim',v:'C9'+X,at:now,src:X,st:'confirmed'},{k:'order',v:'O9'+X,at:now,src:X,st:'proposed'}];
      t.moves=[{id:'m1',what:X,act:'check',status:'open',loggedAt:now,dueAt:new Date(Date.now()+864e5).toISOString(),allDay:true,by:true}];
      t.call={who:X,ask:X,via:'phone',at:now};t.goal=X;t.corr=[{k:'party',from:X,to:X,at:now,how:'typo',src:X}];
      t.events.push({at:now,label:'They sent: '+X});t.events.push({at:now,label:'Pasted from a screenshot: '+X});
      t.docNames={'k1':X};t.helpAsk=X;(t.ledger||[]).forEach(function(r){r.v=X;r.src=X});t.packQs=[X];
      t.corrP={k:'party',from:'Currys',to:X,src:X};t.outP={kind:'missed',said:X,src:X};""" % XJ)
    a.poke("""var X=%s;db.case_notes.push({id:'n1',task_id:'%s',author:X,body:X,created_at:new Date().toISOString()});
      db.inbound_items.push({id:'r1',user_id:'u-me',task_id:'%s',from_domain:X,subject:X,body:X,received_at:new Date().toISOString(),used_at:null});
      db.inbound_items.push({id:'r2',user_id:'u-me',task_id:null,from_domain:X,subject:X,body:X,received_at:new Date().toISOString(),used_at:null});
      db.shares.forEach(function(s){function w(o){if(Array.isArray(o)){for(var i=0;i<o.length;i++){if(typeof o[i]==='string'&&!/^\\d{4}-/.test(o[i]))o[i]=o[i]+X;else w(o[i])}}else if(o&&typeof o==='object'){for(var k in o){if(typeof o[k]==='string'&&!/^\\d{4}-/.test(o[k])&&k!=='v'&&k!=='k'&&k!=='m')o[k]=o[k]+X;else w(o[k])}}}w(s.card)});""" % (XJ, cid, cid))
    ok(markup(pg) == 0 and shown(pg) >= 1, 'Home with the hostile case, a reply and a forwarded email: shown as text (%d), never markup' % shown(pg))
    a.tap('cases'); ok(markup(pg) == 0 and shown(pg) >= 1, 'Cases: shown as text, never markup')
    a.open(cid); pg.evaluate("()=>document.querySelectorAll('details').forEach(d=>d.open=true)"); wait(pg, 200)
    ok(markup(pg) == 0 and shown(pg) >= 6, 'the case with every section open: shown as text (%d places), never markup' % shown(pg))
    bad_p = []
    for pn in ['paste', 'correct', 'rename', 'kind', 'pack', 'summary137', 'chk138', 'qdate', 'later', 'changed', 'refadd', 'call', 'partly']:
        a.panel(cid, pn)
        if markup(pg): bad_p.append(pn)
    ok(not bad_p, 'every case panel shows the hostile words as text: %s' % bad_p)
    hp = a.ctx.new_page(); hp.on('pageerror', lambda e: errs.append(str(e)))
    hp.goto('https://sorted.test/?share=' + tok); wait(hp, 900)
    ok(markup(hp) == 0 and shown(hp) >= 2, 'the shared page with hostile card fields: text (%d), never markup' % shown(hp)); hp.close()
    ctx_h, ph = context(b, page='113_hook.html')
    ph.goto('https://sorted.test/'); ph.evaluate("(d)=>{localStorage.setItem('__mockdb',d);localStorage.setItem('__emailReady','1');localStorage.setItem('__mocksession', JSON.stringify({user:{id:'u-me',email:'me@example.com'}}))}", json.dumps(a.db()))
    ph.goto('https://sorted.test/'); wait(ph, 800)
    gen = ph.evaluate("(id)=>{var D=window.__d145,t=D.task(id);return [D.packText(t),JSON.stringify(D.callDefaults(t)),D.sumText137(t,''),D.recapText(t)].join('\\n')}", cid)
    ok(X in gen, 'the pack, chase, summary and recap carry the words exactly as written (plain text files)')
    ctx_h.close(); a.ctx.close()

    # ---- 2 unreadable dates, 3 a screen that can't be drawn ----
    a = App(b); pg = a.pg
    c1 = a.start('Currys said they would refund £40 by Friday, ref CU123456')
    c2 = a.start('BT will install broadband between 8am and 1pm on Tuesday')
    a.task_js(c1, "t.promises[0].dueAt='garbage';")
    a.task_js(c2, "t.promises[0].dueAt='2026-13-45T00:00:00Z';t.promises[0].dueEnd='zzz';")
    e0 = len(errs)
    ok(not text_issues(pg) and 'can’t read' in pg.inner_text('main'), 'Home: an unreadable date is said in words, no Invalid Date or 12am to 12am: %s' % text_issues(pg)[:3])
    a.tap('cases'); ok(not text_issues(pg), 'Cases: the same: %s' % text_issues(pg)[:3])
    for c in (c1, c2):
        a.open(c); pg.evaluate("()=>document.querySelectorAll('details').forEach(d=>d.open=true)")
        m = pg.inner_text('main')
        ok(pg.evaluate("S=>!!document.querySelector('main.case56')", None) and not text_issues(pg) and 'can’t read' in m, 'the case opens and says the date can’t be read: %s' % text_issues(pg)[:3])
        ok(pg.locator('[data-a=cal]').count() == 0, 'no calendar button for a date Sorted can’t read')
    ok(len(errs) == e0, 'no page error from an unreadable date: %s' % errs[e0:])
    e0 = len(errs)
    a.task_js(c1, "t.promises='broken';t.events='broken';")
    a.open(c1); wait(pg, 300)
    m = pg.inner_text('#app')
    ok('Sorted couldn’t show this case' in m and 'Nothing in your cases has been changed' in m and pg.locator('main [data-a=go-home]').count() == 1, 'a case that can’t be drawn shows a plain screen with Go to Home: %r' % m[:120])
    ok(pg.locator('.tab129').count() == 1 and pg.title().startswith('Couldn’t show this case'), 'with the tab bar and a page title')
    ok(pg.evaluate("document.activeElement&&document.activeElement.id")=='err145d-h', 'focus is on the heading, so a screen reader says what happened')
    ok(len(errs) > e0, 'the error still reaches the page error handler (and so the error report)')
    pg.locator('main [data-a=go-home]').click(); wait(pg, 500)
    ok('Sorted couldn’t show this screen' in pg.inner_text('#app') and pg.locator('.tab129').count() == 1, 'Home with the same broken record says so too, with the tab bar, never a frozen screen')
    a.task_js(c1, "t.promises=[];t.events=[];")
    ok(pg.locator('main.home44').count() == 1, 'once the record is readable again, Home works')
    a.ctx.close()
    errs[e0:] = []   # the deliberate error above

    # ---- 4 performance ----
    ctx_r, pr = context(b, page='reader.html'); pr.goto('https://sorted.test/'); wait(pr, 500)
    base = "Hi, Currys said they would refund £40 by Friday 16 October, ref CU123456. "
    shapes = {'prose': (base * 700)[:50000], 'spaces': 'a' + ' ' * 49998 + 'b', 'newlines': 'line\n' * 10000, 'dashes': '-' * 50000,
              'separators': '-----Original Message-----\n' * 1850, 'hyphen chain': 'a-' * 25000, 'reply chain': '> On Tue, Sam wrote:\n' * 2400,
              'ocr junk': '|l1 I;: ,. ~ \u2019 ' * 3500, 'digits': '12 ' * 16666, 'underscores': '_' * 50000}
    READ = """(t)=>{var R=window.__read,o={};[['readCase',x=>R.readCase(x,R.caseFacts(x))],['intakeRead',x=>R.intakeRead(x)],['sugFromMessage',x=>R.sugFromMessage(x)],['caseFacts',x=>R.caseFacts(x)],['thingOf',x=>R.thingOf(x)],['corrRead',x=>R.corrRead({party:'Evri',ref:'EV1'},x)],['refsRead',x=>R.refsRead(x)],['docAssess',x=>R.docAssess(x,80,'any')],['ocrClean',x=>R.ocrClean(x)],['looksUnsafe',x=>R.looksUnsafe(x)],['pcnRead',x=>R.pcnRead(x)]].forEach(function(f){var t0=performance.now();try{f[1](t)}catch(e){}o[f[0]]=performance.now()-t0});return o}"""
    slow = {}
    for name, txt in shapes.items():
        # the faster of two runs, so a busy machine doesn't look like a freeze. v144 took 1.4 to 2.7 s on 50 kB of line
        # breaks (it asked about the whole message once per line) and up to 9 s on a chain of hyphenated words
        r1, r2 = pr.evaluate(READ, txt), pr.evaluate(READ, txt); r = {k: min(r1[k], r2[k]) for k in r1}
        worst = max(r.items(), key=lambda kv: kv[1])
        if worst[1] > (700 if name in ('prose', 'ocr junk', 'digits') else 1200): slow[name] = (worst[0], round(worst[1]))
        print('   %s: slowest %s %dms' % (name, worst[0], worst[1]))
    ok(not slow, 'every reader reads a 50 kB paste of every awkward shape without freezing the page: %s' % slow)
    ctx_r.close()
    ctx_h, ph = context(b, page='113_hook.html')
    ph.goto('https://sorted.test/'); ph.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1');localStorage.setItem('__mocksession', JSON.stringify({user:{id:'u-me',email:'me@example.com'}}))")
    ph.goto('https://sorted.test/'); wait(ph, 600)
    ph.evaluate("""()=>{var D=window.__d145,S=D.S,now=Date.now();for(var i=0;i<100;i++){var due=new Date(now+((i%9)-4)*864e5);due.setHours(23,59,0,0);
      S.tasks.push({id:'p'+i,mode:'call',title:'Case number '+i+' with Evri',created:new Date(now-i*36e5).toISOString(),updatedAt:new Date(now-i*36e5).toISOString(),board:i%3?'waiting':'yours',
      promises:[{id:'q'+i,said:'Deliver parcel '+i,party:['Evri','Currys','BT','Sky'][i%4],dueAt:due.toISOString(),allDay:true,by:true,ref:'EV'+(100000+i),status:i%7?'open':'kept',loggedAt:new Date(now-i*36e5).toISOString(),prec:'day'}],
      events:[{at:new Date(now-i*36e5).toISOString(),label:'Started.'}],facts:{party:'Evri',ref:'EV'+(100000+i)},said:'Evri said '+i,rev:1})}}""")
    times = ph.evaluate("""()=>{var D=window.__d145,S=D.S,o={};function m(k,v){S.view=v;var t0=performance.now();D.render();o[k]=Math.round(performance.now()-t0)}
      m('home',{name:'home'});m('home again',{name:'home'});m('cases',{name:'cases'});m('case',{name:'task',id:'p5'});return o}""")
    ok(max(times.values()) < 1500 and times['home again'] < 800, 'with 100 cases Home, Cases and a case draw quickly: %s ms' % times)
    ok(ph.locator('main').count() == 1 and 'Case number 5' in ph.inner_text('main'), 'and the case drawn is the right one')
    ctx_h.close()

    # ---- 5 copy and layout ----
    issues = {}; smalls = {}; names = {}; side = []; titles = []
    def scan(pg, where):
        t = text_issues(pg)
        if t: issues[where] = t[:3]
        s = small_controls(pg)
        if s: smalls[where] = s[:3]
        u = unnamed(pg)
        if u: names[where] = u[:2]
        if sideways(pg): side.append(where)
        if not pg.title(): titles.append(where)
    for w in (320, 390, 768):
        ctx, pg = context(b, w)
        pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear()"); pg.reload(); wait(pg, 500)
        scan(pg, '%d landing' % w)
        for h in ['about', 'how', 'help', 'privacy', 'terms', 'contact', 'start']:
            pg.goto('https://sorted.test/#' + h); wait(pg, 350); pg.evaluate("()=>document.querySelectorAll('details').forEach(d=>d.open=true)"); scan(pg, '%d #%s' % (w, h))
        ctx.close()
    a = App(b); pg = a.pg
    scan(pg, 'newcomer Home')
    ids = [a.start(s) for s in ['Currys said they would refund £40 by Friday, ref CU123456', 'BT will install broadband between 8am and 1pm on Tuesday',
                                'Camden Council: pay £65 within 14 days, PCN CD12345678', 'My washing machine is leaking', 'Aviva said they would call me back',
                                'My landlord said he would fix the damp next week']]
    a.home(); scan(pg, 'returning Home'); a.tap('cases'); scan(pg, 'Cases'); a.tap('data'); scan(pg, 'More')
    for tab in ('acct-settings', 'help'):
        if pg.locator('[data-a=acct-jump][data-v=%s]' % tab).count(): pg.locator('[data-a=acct-jump][data-v=%s]' % tab).first.click(); wait(pg, 400)
        pg.evaluate("()=>document.querySelectorAll('details').forEach(d=>d.open=true)"); scan(pg, 'More ' + tab)
    for k, c in enumerate(ids):
        a.open(c); pg.evaluate("()=>document.querySelectorAll('details').forEach(d=>d.open=true)"); scan(pg, 'case %s' % a.case(c)['title'])
        if k in (0, 2, 5):   # a refund, a notice and a repair: every panel
            for pn in ['paste', 'correct', 'rename', 'kind', 'pack', 'summary137', 'later', 'changed', 'refadd', 'call', 'partly']:
                a.panel(c, pn); scan(pg, 'panel %s %s' % (pn, a.case(c)['title']))
    damp = [c for c in a.cases() if 'damp' in (c.get('said') or '').lower()][0]['id']
    dbx = json.dumps(a.db()); a.ctx.close()
    # the same six cases in dark mode
    ctx, pg = context(b, scheme='dark')
    pg.goto('https://sorted.test/'); pg.evaluate("(d)=>{localStorage.clear();localStorage.setItem('__mockdb',d);localStorage.setItem('__emailReady','1');localStorage.setItem('__mocksession', JSON.stringify({user:{id:'u-me',email:'me@example.com'}}))}", dbx)
    pg.goto('https://sorted.test/'); wait(pg, 800); scan(pg, 'dark Home')
    pg.locator('.tab129 [data-a=cases]').click(); wait(pg, 400); scan(pg, 'dark Cases')
    for c in ids[:3]:
        pg.goto('https://sorted.test/?task=%s' % c); wait(pg, 600); pg.evaluate("()=>document.querySelectorAll('details').forEach(d=>d.open=true)"); scan(pg, 'dark case %s' % c)
    ctx.close()
    ctx_h, ph = context(b, page='113_hook.html')
    ph.goto('https://sorted.test/'); ph.evaluate("(d)=>{localStorage.setItem('__mockdb',d);localStorage.setItem('__emailReady','1');localStorage.setItem('__mocksession', JSON.stringify({user:{id:'u-me',email:'me@example.com'}}))}", dbx)
    ph.goto('https://sorted.test/'); wait(ph, 800)
    gen = ph.evaluate("""(ids)=>ids.map(function(id){var D=window.__d145,t=D.task(id),o=[];function g(f){try{o.push(String(f()))}catch(e){o.push('THROW '+e)}}
      g(()=>D.packText(t));g(()=>JSON.stringify(D.callDefaults(t)));g(()=>D.sumText137(t,'Please reply.'));g(()=>D.recapText(t));g(()=>{var c=D.calPlan(t);return c?D.icsText(c):''});return o.join('\\n')}).join('\\n=====\\n')""", ids)
    # the calendar UID keeps "@sorted-pilot": calendars match events by it, so changing it would duplicate them
    gen = re.sub(r'(?m)^UID:[^\r\n]*@sorted-pilot\r?$', 'UID:x', gen)
    gi = sorted(set(gen[max(0, m.start() - 40):m.end() + 20].replace('\n', ' | ') for m in BADTXT.finditer(gen)))
    ok(not gi and 'THROW' not in gen, 'the pack, chase, summary, recap and calendar files have no em dash, straight apostrophe, pilot wording or broken value: %s' % gi[:4])
    ok(not re.search(r'\([^()\n]*\([^()\n]*\)\)', gen), 'no brackets inside brackets in the record: %s' % re.findall(r'\([^()\n]*\([^()\n]*\)\)', gen)[:2])
    ok(ph.evaluate("(id)=>window.__d145.goalOf(window.__d145.task(id))", damp) == 'Get the damp or mould fixed', 'the damp case wants the damp or mould fixed, not "working again"')
    ok('Get the washing machine working again' in [ph.evaluate("(id)=>window.__d145.goalOf(window.__d145.task(id))", x) for x in ids], 'a washing machine still wants "working again"')
    ctx_h.close()
    ok(not issues, 'no em dash, straight apostrophe, pilot wording, "undefined", "NaN" or "Invalid Date" on any screen: %s' % json.dumps(issues, ensure_ascii=False)[:700])
    ok(not smalls, 'every control is at least 44px tall (links inside a sentence excepted): %s' % json.dumps(smalls, ensure_ascii=False)[:700])
    ok(not names, 'every control has a name: %s' % json.dumps(names)[:500])
    ok(not side, 'nothing scrolls sideways at 320, 390 or 768px: %s' % side)
    ok(not titles, 'every page has a title: %s' % titles)

    # ---- 6 a refused helper-notes switch ----
    a = App(b); pg = a.pg
    cid = a.start('Currys said they would refund £40 by Friday, ref CU123456')
    a.open(cid)
    pg.locator('details.case56-sharing summary').click(); wait(pg, 200)
    pg.click('[data-a=share]'); wait(pg, 600)
    if not pg.locator('details.case56-sharing[open]').count(): pg.locator('details.case56-sharing summary').click(); wait(pg, 200)
    pg.evaluate("localStorage.setItem('__failShareUpdate','1')")
    pg.locator('[data-a=notes-toggle]').click(); wait(pg, 900)
    c = a.case(cid); sh = a.db()['shares'][0]
    ok(not c.get('notesOn') and not sh.get('notes_on'), 'a switch the server refuses goes back: the case and the link agree notes are off')
    ok(any('couldn’t change whether your helper can add notes' in e['label'] for e in c['events']), 'the history says it couldn’t be changed')
    ok('Couldn’t change that' in pg.inner_text('#toast'), 'and the person is told: %r' % pg.inner_text('#toast'))
    if not pg.locator('details.case56-sharing[open]').count(): pg.locator('details.case56-sharing summary').click(); wait(pg, 200)
    ok(not pg.locator('[data-a=notes-toggle]').is_checked(), 'the switch shows off')
    pg.evaluate("localStorage.removeItem('__failShareUpdate')")
    pg.locator('[data-a=notes-toggle]').click(); wait(pg, 700)
    ok(a.case(cid).get('notesOn') is True and a.db()['shares'][0].get('notes_on') is True, 'once the server accepts it, it is on in both places')
    a.ctx.close()
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
