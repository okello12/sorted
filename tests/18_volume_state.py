import os,sys,time
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
from dates import ahead
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m): print(('PASS ' if c else 'FAIL ')+m); fails.append(m) if not c else None
def wait(pg,ms=140): pg.wait_for_timeout(ms)
def db(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')||'{\"tasks\":[]}')")
def fresh(pg):
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg); pg.click('[data-a=anon-start]'); wait(pg)
def start_case(pg,text):
    pg.goto('https://sorted.test/'); wait(pg)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg,60)
    if pg.locator('#f-case').count()!=1: return False
    pg.fill('#f-case',text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
    if pg.locator('[data-a=safe-continue]').count(): pg.click('[data-a=safe-continue]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg)
    return True
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London'); ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript')); ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body='')); pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(str(e))); fresh(pg)
    made=0; worst=0
    for i in range(40):
        st=time.perf_counter(); good=start_case(pg,'My heating issue number %02d is still unresolved and I need to contact the landlord'%i); worst=max(worst,time.perf_counter()-st)
        if not good: break
        made+=1
    ok(made==40,'created 40 cases through UI (%d)'%made)
    ok(worst<4.0,'worst case-create interaction under 4s (%.2fs)'%worst)
    pg.goto('https://sorted.test/'); wait(pg,350); ok(pg.locator('main').count()==1 and pg.locator('h1').count()>=1,'Home renders with 40 cases')
    for _ in range(10): pg.reload(); wait(pg,80)
    ok(pg.locator('main').count()==1,'10 rapid reloads keep one app shell')
    pg.evaluate("document.documentElement.style.fontSize='200%'"); wait(pg); d=pg.evaluate("({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth})"); ok(d['sw']<=d['cw']+3,'200 percent text no horizontal page overflow %s'%d)
    pg.evaluate("document.documentElement.style.fontSize=''")
    before=len(db(pg).get('tasks',[]))
    for i in range(50): pg.evaluate("x=>{location.hash='#new='+encodeURIComponent(x)}",'BurstCo promised update tomorrow ref B-%02d'%i); wait(pg,15)
    wait(pg,250); after=len(db(pg).get('tasks',[])); ok(after==before,'50 share events do not auto-create cases'); ok('#new=' not in pg.url,'share text scrubbed from URL'); ok(pg.locator('#f-case').count()==1 and 'B-49' in pg.input_value('#f-case'),'latest share payload wins')
    huge='Z'*8000; pg.evaluate("x=>{location.hash='#new='+encodeURIComponent(x)}",huge); wait(pg,250); v=pg.input_value('#f-case'); ok(len(v)==4000,'share payload capped exactly at 4000 (%d)'%len(v))
    fresh(pg); T='StressCo promised the engineer tomorrow 9am to 12pm ref ST-1'; start_case(pg,T); ok(pg.locator('.sug').count()==1,'initial promise card present'); pg.click('[data-a=sug-yes]'); wait(pg,250)
    tid=pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks.map(x=>x.data).pop().id")
    for n in range(2,9):
        if pg.locator('[data-a=panel][data-p=paste]').count()==0: pg.reload(); wait(pg,180)
        pg.click('[data-a=panel][data-p=paste]'); wait(pg,80); pg.fill('#f-paste','StressCo: engineer moved to %s between 1pm and 3pm. Ref ST-%d.'%(ahead(n+1)['dm'],n)); pg.click('form[data-f=paste] button[type=submit]'); wait(pg,160); ok(pg.locator('.sug').count()==1,'replacement %d card'%n); pg.click('[data-a=sug-yes]'); wait(pg,220)
        t=pg.evaluate("id=>JSON.parse(localStorage.getItem('__mockdb')).tasks.map(x=>x.data).find(x=>x.id===id)",tid); sts=[x.get('status') for x in t.get('promises',[])]; ok(sts.count('open')==1 and all(s=='replaced' for s in sts[:-1]),'replacement %d one-live invariant %s'%(n,sts))
    b.close()
print('ERRORS',errs); print('FAILS',fails)
if errs or fails: sys.exit(1)
