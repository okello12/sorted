import os,sys,datetime
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m): print(('PASS ' if c else 'FAIL ')+m); fails.append(m) if not c else None
def wait(pg,ms=220): pg.wait_for_timeout(ms)
def fresh(pg):
 pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg); pg.click('[data-a=anon-start]'); wait(pg)
def task(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks.map(x=>x.data).filter(x=>x.said&&x.said.startsWith('StressCo')).pop()")
def open_count(t): return len([p for p in (t or {}).get('promises',[]) if p.get('status')=='open'])
def start(pg):
 pg.goto('https://sorted.test/'); wait(pg)
 if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg,80)
 T='StressCo promised the engineer will come tomorrow 9am to 12pm, ref ST-1.'
 pg.fill('#f-case',T); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
 if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
 if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg)
 return T
def force_past(pg):
 pg.evaluate("""()=>{let d=JSON.parse(localStorage.getItem('__mockdb'));let t=d.tasks.map(x=>x.data).find(x=>x.said&&x.said.startsWith('StressCo'));let p=[...(t.promises||[])].reverse().find(x=>x.status==='open');let a=new Date(Date.now()-86400000);a.setHours(9,0,0,0);let e=new Date(a);e.setHours(12);p.dueAt=a.toISOString();p.dueEnd=e.toISOString();localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}""")
def open_case(pg):
 pg.goto('https://sorted.test/'); wait(pg,300)
 if pg.locator('.slip-open').count(): pg.locator('.slip-open').first.click(); wait(pg,250)
with sync_playwright() as p:
 b=p.chromium.launch();ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London')
 ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
 ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
 pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));fresh(pg);start(pg)
 ok(pg.locator('[data-a=sug-yes]').count()==1,'promise confirmation offered once')
 pg.evaluate("()=>{let b=document.querySelector('[data-a=sug-yes]');b&&b.click();b&&b.click()}");wait(pg,500)
 t=task(pg);ok(t and len(t.get('promises',[]))==1 and open_count(t)==1,'double confirm creates one promise')
 for n,days in enumerate([3,5,7],start=2):
  force_past(pg);open_case(pg)
  ok(pg.locator('.promise [data-a=rebook]').count()==1,'reschedule control available %d'%n)
  pg.click('.promise [data-a=rebook]');wait(pg,160)
  ok(pg.locator('select[data-dp=f-date][data-part=d]').count()==1,'reschedule form opens %d'%n)
  nd=datetime.date.today()+datetime.timedelta(days=days)
  pg.select_option('select[data-dp=f-date][data-part=d]',str(nd.day));pg.select_option('select[data-dp=f-date][data-part=m]',str(nd.month));pg.select_option('select[data-dp=f-date][data-part=y]',str(nd.year))
  pg.fill('#f-from','13:00');pg.fill('#f-to','15:00');pg.click('text=Save the promise');wait(pg,400)
  if pg.locator('text=Not now').count(): pg.click('text=Not now');wait(pg,100)
  t=task(pg);sts=[x.get('status') for x in t.get('promises',[])] if t else []
  ok(t and open_count(t)==1 and sts[-1]=='open' and all(x=='replaced' for x in sts[:-1]),'reschedule %d leaves one live promise: %s'%(n,sts))
  pg.reload();wait(pg,250);t=task(pg);ok(t and open_count(t)==1,'reschedule %d survives reload'%n)
 # Churn navigation/reload while Waiting must not duplicate a promise.
 for i in range(12):
  pg.goto('https://sorted.test/');wait(pg,90);pg.reload();wait(pg,90)
 t=task(pg);ok(t and open_count(t)==1,'12 navigation/reload cycles preserve one live promise')
 # Outcome path: mark latest window passed, confirm missed once, reload, and keep one coherent case.
 force_past(pg);open_case(pg)
 ok(pg.locator('.promise [data-a=missed]').count()==1,'missed outcome control appears after due window')
 pg.click('.promise [data-a=missed]');wait(pg,350)
 t=task(pg);ok(t is not None and open_count(t)<=1,'missed outcome cannot create multiple live promises')
 pg.reload();wait(pg,250);ok(pg.locator('main').count()==1,'case remains renderable after missed outcome and reload')
 b.close()
print('ERRORS',errs);print('FAILS',fails)
