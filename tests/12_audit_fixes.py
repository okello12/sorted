# v37: fixes from the full audit
import os, sys, json, datetime
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from dates import ahead
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=350): pg.wait_for_timeout(ms)
def start(pg,text):
    pg.goto('https://sorted.test/'); wait(pg,400)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg,150)
    pg.fill('#f-case',text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('[data-a=safe-continue]').count(): pg.click('[data-a=safe-continue]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg)
def task(pg,text): return pg.evaluate("(t)=>JSON.parse(localStorage.getItem('__mockdb')).tasks.map(x=>x.data).find(x=>x.said===t||x.said.indexOf(t.slice(0,60))===0)",text)
def due(t): return datetime.datetime.fromisoformat(t['sugP']['dueAt'].replace('Z','+00:00')).astimezone().date() if t.get('sugP') else None
today=datetime.date.today()
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE+'/tests/mock.js', content_type='application/javascript'))
    ctx.route('https://fonts.googleapis.com/**', lambda r: r.fulfill(body='', content_type='text/css'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE+'/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg,200); pg.click('[data-a=anon-start]'); wait(pg)
    # unrelated duration doesn't back-date
    T="My boiler has been broken for two weeks. British Gas said the engineer would come in 3 days"; start(pg,T); t=task(pg,T)
    ok(t.get('sugP') and not t['sugP']['past'] and due(t)>=today,'unrelated duration: promise stays in the future (%s)'%due(t))
    # "haven't confirmed" is not a missed visit
    T="They said they'd come Thursday but haven't confirmed a time"; start(pg,T); t=task(pg,T)
    ok(t.get('sugP') and not t['sugP']['past'],'"haven’t confirmed" keeps Thursday ahead')
    # prices are not times
    T="We have refunded £12.50 to your card. It will show in 3-5 working days."; start(pg,T); t=task(pg,T)
    ok(t.get('sugP') and t['sugP']['allDay'] and t['sugP']['by'],'£12.50 is not read as 12:50')
    T="Argos promised a refund of £12.50 within 5 days"; start(pg,T); t=task(pg,T)
    ok(t.get('sugP') is not None,'a decimal price doesn’t cut the sentence')
    ok(t['facts'].get('amount')==12.5,'amount with pence read')
    T="Refund of £1500 from Currys still not here"; start(pg,T); t=task(pg,T); ok(t['facts'].get('amount')==1500,'£1500 read as 1500')
    # ordinary words are not companies
    T="The sky is leaking through the ceiling, landlord said they'd fix it by Friday"; start(pg,T); t=task(pg,T)
    ok(t['facts'].get('party')!='Sky','"the sky" is not Sky')
    T="My order number is 12345678 and Currys promised a refund by Friday"; start(pg,T); t=task(pg,T); ok(t['facts'].get('ref')=='12345678','"order number is" gives the reference')
    # opening hours are skipped
    A=ahead(12); T="Your engineer is booked for %s between 8am and 12pm. Our lines are open Monday to Friday 8am to 6pm."%A['long']; start(pg,T); t=task(pg,T)
    ok(due(t)==A['date'],'opening hours are not the promise')
    # an explicit past date gives a missed-promise card
    P=today-datetime.timedelta(days=3); T="British Gas promised an engineer on %d %s but nobody came"%(P.day,P.strftime('%B')); start(pg,T); t=task(pg,T)
    ok(t.get('sugP') and t['sugP']['past'] and due(t)==P,'explicit past date: card says it has passed')
    # change the details, then cancel: the card comes back
    pg.click('[data-a=sug-edit]'); wait(pg); pg.click('form[data-f=promise] [data-a=panel][data-p=""]'); wait(pg)
    ok(pg.locator('.sug').count()==1,'cancel after "Change the details" brings the card back')
    # a long pasted message keeps at most 300 characters
    T="Hello, "+("thank you for your patience while we look into this. "*12)+"Your refund will be paid by "+ahead(9)['dm']+"."; start(pg,T)
    t=pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks.map(x=>x.data).find(x=>x.said&&x.said.indexOf('Hello, thank you')===0)")
    ok(t and len(t['said'])<=300 and t.get('sugP') and due(t)==ahead(9)['date'],'long message: 300 characters kept, date still found')
    # a11y: opening a panel focuses its field; an empty submit focuses the field with an announced error
    pg.goto('https://sorted.test/'); wait(pg,400); pg.locator('[data-a=open]').first.click(); wait(pg)
    if pg.locator('[data-a=sug-no]').count(): pg.click('[data-a=sug-no]'); wait(pg)
    pg.focus('[data-a=panel][data-p=paste]'); pg.keyboard.press('Enter'); wait(pg)
    ok(pg.evaluate("document.activeElement.id")=='f-paste','opening "Paste a message" focuses the box')
    pg.click('form[data-f=paste] button[type=submit]'); wait(pg)
    ok(pg.evaluate("document.activeElement.id")=='f-paste' and pg.get_attribute('#f-paste','aria-invalid')=='true' and pg.get_attribute('form[data-f=paste] .err','role')=='alert','error: field focused, marked, announced')
    ok(pg.evaluate("getComputedStyle(document.getElementById('f-paste')).outlineStyle")=='solid','text fields show a visible focus ring')
    pg.click('form[data-f=paste] [data-a=panel][data-p=""]'); wait(pg)
    # delete one case
    n0=len(pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks"))
    pg.click('[data-a=panel][data-p=delcase]'); wait(pg)
    ok(pg.evaluate("document.activeElement.getAttribute('data-a')")=='case-del','delete: confirm button focused')
    pg.click('[data-a=case-del]'); wait(pg,600)
    ok(len(pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks"))==n0-1 and 'Case deleted' in pg.inner_text('#toast'),'delete: case removed')
    ok(pg.locator('h1').count()>=1,'Home has a page heading')
    b.close()

# v38: the database library's fingerprint matches the exact npm file; Google Fonts is gone; step source
import hashlib, base64, re
PAGE=open(HERE+'/public/index.html',encoding='utf8').read()
lib=open(HERE+'/tests/node_modules/@supabase/supabase-js/dist/umd/supabase.js','rb').read()
want='sha384-'+base64.b64encode(hashlib.sha384(lib).digest()).decode()
m=re.search(r'supabase-js@([0-9.]+)/dist/umd/supabase.js" integrity="([^"]+)"',PAGE)
ok(m and m.group(2)==want,'supabase-js integrity matches the npm package')
ok(m and m.group(1)==json.load(open(HERE+'/tests/node_modules/@supabase/supabase-js/package.json'))['version'],'test copy of supabase-js is the same version as the page')
ok('fonts.googleapis' not in PAGE and 'fonts.gstatic' not in PAGE and 'Google Fonts' not in PAGE,'no Google Fonts left in the page or the notice')
ok(all(os.path.exists(HERE+'/public'+u) for u in re.findall(r'url\((/fonts/[^)]+)\)',PAGE)) and PAGE.count('@font-face')==5,'every self-hosted font file exists')
ok('src:sp.fromMsg&&!sp.typed?"message":"sentence"' in PAGE,'step record says where a confirmed suggestion came from')
ok('scrambled, one-way copy' in PAGE and '12 months without a sign-in' in PAGE,'v41: notice covers the stop list and idle accounts')
ok('S.inboundAddr=null;S.inbox=[];return;' in PAGE,'v42: the page no longer asks for a forwarding address')
print('ERRORS',errs); print('FAILS',fails)
