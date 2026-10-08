# v143: shared set-up for tests 102 and 103 (the person's attention, false misses). An email user on the mock server,
# with email reminders ready, so reminder rows are written and can be checked.
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates  # London time
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.')
today = datetime.date.today()
errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
def day(n): return today + datetime.timedelta(days=n)
def long(d): return '%s %d %s' % (d.strftime('%A'), d.day, d.strftime('%B'))
def uk(n): return day(n).strftime('%d/%m/%Y')
def nextwd(wd, after=1):
    d = today + datetime.timedelta(days=after)
    while d.weekday() != wd: d += datetime.timedelta(days=1)
    return d
def until(pg, fn, ms=6000):
    """poll until fn() is truthy (saves and reminder rows land a moment after a tap)"""
    t = 0
    while t < ms:
        v = fn()
        if v: return v
        pg.wait_for_timeout(250); t += 250
    return fn()
def L(iso):
    return datetime.datetime.fromisoformat(iso.replace('Z', '+00:00')).astimezone() if iso else None

class App:
    def __init__(self, p, email=True):
        self.b = p.chromium.launch()
        self.ctx = self.b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
        c = self.ctx
        c.grant_permissions(['clipboard-read', 'clipboard-write'], origin='https://sorted.test')
        c.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
        c.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
        c.route(lambda u: 'gov.uk' in u or 'tfl.gov.uk' in u, lambda r: r.fulfill(body='<title>Official page</title>', content_type='text/html'))
        self.pg = c.new_page(); self.pg.on('pageerror', lambda e: errs.append(str(e)))
        pg = self.pg
        pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')")
        if email:
            pg.evaluate("localStorage.setItem('__mocksession', %s)" % json.dumps(json.dumps({'user': {'id': 'u-me', 'email': 'me@example.com'}})))
            pg.goto('https://sorted.test/'); wait(pg, 700)
        else:
            pg.goto('https://sorted.test/#start'); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    def db(self): return self.pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    def cases(self): return sorted([x['data'] for x in self.db().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    def case(self, cid): return [c for c in self.cases() if c['id'] == cid][0]
    def openp(self, cid): return [q for q in self.case(cid)['promises'] if q['status'] == 'open']
    def rows(self, cid): return [r for r in self.db().get('reminders', []) if r['task_id'] == cid and not r.get('sent_at')]
    def outcomes(self): return self.pg.evaluate("JSON.parse(localStorage.getItem('__outcomes')||'[]')")
    def att(self, cid, kind=None): return [a for a in self.case(cid).get('att', []) if not a.get('done') and not a.get('cancelled') and (kind is None or a['kind'] == kind)]
    def main(self): return self.pg.inner_text('main')
    def labels(self, cid): return [e['label'] for e in self.case(cid).get('events', [])]
    def tap(self, a): self.pg.locator('.tab129 [data-a=%s]' % a).click(); wait(self.pg, 500)
    def home(self): self.pg.goto('https://sorted.test/'); wait(self.pg, 700)
    def open(self, cid): self.pg.goto('https://sorted.test/?task=%s' % cid); wait(self.pg, 700)
    def poke(self, js):
        pg = self.pg
        pg.goto('https://sorted.test/'); wait(pg, 600)
        pg.evaluate("(js)=>{var db=JSON.parse(localStorage.getItem('__mockdb'));(new Function('db',js))(db);localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", js)
        pg.goto('https://sorted.test/'); wait(pg, 700)
    def task_js(self, cid, body): self.poke("db.tasks.forEach(function(r){if(r.data.id==='%s'){var t=r.data;%s}})" % (cid, body))
    def overdue(self, cid, days=2):
        self.task_js(cid, "t.promises.forEach(function(q){if(q.status==='open'){q.dueAt=new Date(Date.now()-%d*864e5).toISOString();q.dueEnd=null;q.allDay=true;q.by=true}})" % days)
    def past_reading(self, cid):
        """the organisation's reading (an estimate or window) has passed; their words and precision stay"""
        self.task_js(cid, "t.promises.forEach(function(q){if(q.status==='open'){var e=new Date(Date.now()-864e5);e.setHours(23,59,59,0);var s=new Date(Date.now()-3*864e5);s.setHours(0,0,0,0);q.dueAt=s.toISOString();if(q.win){q.dueEnd=e.toISOString()}}})")
    def start(self, text, confirm=True):
        pg = self.pg; before = set(c['id'] for c in self.cases())
        self.tap('new-case')
        pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        if confirm and pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 700)
        if pg.locator('[data-a=nudge-skip]').count(): pg.click('[data-a=nudge-skip]'); wait(pg, 300)
        if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 300)
        new = until(pg, lambda: [c['id'] for c in self.cases() if c['id'] not in before], 8000)
        return new[0] if new else self.cases()[-1]['id']
    def parking(self, when_days, issuer='Southwark Council', ref='SK12345678'):
        pg = self.pg; before = set(c['id'] for c in self.cases())
        self.home(); self.tap('new-case'); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', 'PCN'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 500)
        pg.evaluate("(()=>{var b=document.createElement('button');b.setAttribute('data-a','doc-manual');document.querySelector('main').appendChild(b);b.click()})()"); wait(pg, 500)
        if os.environ.get('ATT_DEBUG'): print('DEBUG before manual form:', self.main()[:500].replace('\n', ' | '))
        pg.fill('#doc-issuer', issuer); pg.fill('#doc-ref', ref); pg.fill('#doc-vrm', 'AB12 CDE'); pg.fill('#doc-when', uk(when_days)); pg.fill('#doc-amount', '130'); pg.fill('#doc-discount', '65')
        pg.click('form[data-f=doc] button[type=submit]'); wait(pg, 700)
        if os.environ.get('ATT_DEBUG'): print('DEBUG after doc submit:', self.main()[:700].replace('\n', ' | '))
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 600)
        new = until(pg, lambda: [c['id'] for c in self.cases() if c['id'] not in before and c.get('cf')], 8000)
        return new[0] if new else self.cases()[-1]['id']
    def q(self, name, a):
        return self.pg.locator('.home44-spot:has-text("%s"), .q130-item:has-text("%s")' % (name, name)).locator('[data-a=%s]' % a).first
    def spot_or_row(self, name):
        loc = self.pg.locator('.home44-spot:has-text("%s"), .home44-row:has-text("%s")' % (name, name)).first
        return loc.inner_text() if loc.count() else ''
    def share_view(self, cid):
        """make (or refresh) the helper link and read it as the helper sees it"""
        pg = self.pg
        self.open(cid)
        pg.evaluate("(()=>{var b=document.createElement('button');b.setAttribute('data-a','share');document.querySelector('main').appendChild(b);b.click()})()"); wait(pg, 900)
        tok = self.case(cid).get('shareToken')
        p2 = self.ctx.new_page(); p2.on('pageerror', lambda e: errs.append(str(e)))
        p2.goto('https://sorted.test/?share=%s' % tok); wait(p2, 900)
        tx = p2.inner_text('main'); p2.close(); return tx
    def pack(self, cid):
        pg = self.pg
        self.open(cid)
        pg.evaluate("(()=>{var b=document.createElement('button');b.setAttribute('data-a','panel');b.setAttribute('data-p','pack');document.querySelector('main').appendChild(b);b.click()})()"); wait(pg, 600)
        return self.main()
    def close(self): self.b.close()

def finish():
    print('ERRORS', errs)
    print('FAILS', fails)
