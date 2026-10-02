import os,sys,json,time
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.');errs=[];fails=[];reqs=[]
def ok(c,m): print(('PASS ' if c else 'FAIL ')+m);fails.append(m) if not c else None
def wait(pg,ms=120): pg.wait_for_timeout(ms)
def ntasks(pg): return len(pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')||'{\"tasks\":[]}').tasks||[]"))
def fresh(pg):
 pg.goto('https://sorted.test/#start');pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')");pg.reload();wait(pg,180);pg.click('[data-a=anon-start]');wait(pg,180)
def make_case(pg):
 pg.goto('https://sorted.test/');wait(pg,180)
 if pg.locator('[data-a=compose]').count():pg.click('[data-a=compose]');wait(pg,60)
 pg.fill('#f-case','My heating is broken and I need to contact the landlord');pg.click('form[data-f=case] button[type=submit]');wait(pg,150)
 if pg.locator('[data-a=match-new]').count():pg.click('[data-a=match-new]');wait(pg)
 if pg.locator('[data-a=safe-continue]').count():pg.click('[data-a=safe-continue]');wait(pg)
 if pg.locator('form[data-f=baseline]').count():pg.click('form[data-f=baseline] .chip >> nth=0');pg.click('form[data-f=baseline] button[type=submit]');wait(pg)
with sync_playwright() as p:
 b=p.chromium.launch();ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London')
 ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
 def route(r):
  reqs.append(r.request.url); r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body='')
 ctx.route(lambda u:u.startswith('https://sorted.test/'),route)
 pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));fresh(pg);make_case(pg)
 before=ntasks(pg);pg.goto('https://sorted.test/');wait(pg,180)
 # 100 share-sheet events in quick succession: no accidental case creation; latest wins.
 for i in range(100):
  pg.evaluate("x=>{location.hash='#new='+encodeURIComponent(x)}",'BurstCo promised update tomorrow, ref B-%03d'%i);wait(pg,12)
 wait(pg,220)
 ok(ntasks(pg)==before,'100 share events create zero cases before Start')
 ok('#new=' not in pg.url,'share fragment scrubbed from address bar')
 ok(pg.locator('#f-case').count()==1 and 'B-099' in pg.input_value('#f-case'),'latest of 100 share payloads wins')
 ok(not any('#new=' in u or 'B-099' in u for u in reqs),'fragment payload never reaches mocked server requests')
 # Maximum payload and malformed encoding.
 huge='Z'*8000+' Currys promised refund tomorrow ref HUGE-1';pg.evaluate("x=>{location.hash='#new='+encodeURIComponent(x)}",huge);wait(pg,220)
 val=pg.input_value('#f-case');ok(len(val)==4000,'share input capped at exactly 4000 chars: %d'%len(val));ok(ntasks(pg)==before,'huge share input still not auto-saved')
 pg.evaluate("location.hash='#new=%E0%A4%A'");wait(pg,180);ok(pg.locator('#f-case').count()==1,'malformed percent encoding does not break composer')
 # Markup/script payload must stay inert.
 pg.evaluate("x=>{location.hash='#new='+encodeURIComponent(x)}",'<img src=x onerror="window.__pwned=1"> promised tomorrow');wait(pg,180)
 ok(pg.evaluate("window.__pwned||0")==0,'share-sheet HTML is inert')
 # Inflate mock account to 201 cases, then churn reloads. This does not touch production.
 pg.evaluate("""()=>{let d=JSON.parse(localStorage.getItem('__mockdb'));let base=d.tasks[0];for(let i=0;i<200;i++){let c=JSON.parse(JSON.stringify(base));let id='qa'+i.toString().padStart(10,'0');c.id=id;c.data.id=id;c.data.title='QA pressure case '+i;c.data.said='QA pressure case '+i;d.tasks.push(c)}localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}""")
 t0=time.time();pg.goto('https://sorted.test/');wait(pg,500);elapsed=time.time()-t0
 ok(pg.locator('main').count()==1 and pg.locator('h1').count()>=1,'Home renders with 200 extra cases')
 ok(len(errs)==0,'no page errors after 200-case render')
 ok(elapsed<5,'200-case initial render stays under 5s in CI: %.2fs'%elapsed)
 for i in range(10):pg.reload();wait(pg,100)
 ok(pg.locator('main').count()==1,'10 reloads keep one usable app shell')
 # Composer must still work after account pressure.
 if pg.locator('[data-a=compose]').count():pg.click('[data-a=compose]');wait(pg,80)
 ok(pg.locator('#f-case').count()==1,'composer still opens with 200+ cases')
 if pg.locator('#f-case').count():pg.fill('#f-case','Landlord promised an engineer tomorrow')
 ok(pg.input_value('#f-case')=='Landlord promised an engineer tomorrow','composer remains editable under list pressure')
 # 200% text pressure should not create horizontal page scrolling.
 pg.evaluate("document.documentElement.style.fontSize='200%'");wait(pg,160)
 dims=pg.evaluate("({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth})")
 ok(dims['sw']<=dims['cw']+3,'200% text has no horizontal page overflow: %s'%dims)
 b.close()
print('ERRORS',errs);print('FAILS',fails)
