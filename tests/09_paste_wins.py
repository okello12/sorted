import os, json
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from dates import A4,A5,A6,A10
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=350): pg.wait_for_timeout(ms)
def start(pg,text):
    pg.goto('https://sorted.test/'); wait(pg,400)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg,150)
    pg.fill('#f-case',text); pg.click('form[data-f=case] button'); wait(pg)
    if pg.locator('[data-a=safe-continue]').count(): pg.click('[data-a=safe-continue]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg)
def task(pg,text): return pg.evaluate("(t)=>JSON.parse(localStorage.getItem('__mockdb')).tasks.map(x=>x.data).find(x=>x.said===t)",text)
def home_next(pg,title):
    pg.goto('https://sorted.test/'); wait(pg,400)
    return pg.evaluate("(t)=>{var s=[...document.querySelectorAll('.slip')].find(x=>x.innerText.includes(t));return s?s.innerText:''}",title)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE+'/tests/mock.js', content_type='application/javascript'))
    ctx.route('https://fonts.googleapis.com/**', lambda r: r.fulfill(body='', content_type='text/css'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE+'/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg,200); pg.click('[data-a=anon-start]'); wait(pg)
    # 1 card is the whole first screen
    T1="Currys promised a refund within 14 days, it's been three weeks, order 88421"; start(pg,T1)
    ok(pg.locator('.sug').count()==1 and pg.locator('#f-who').count()==0 and pg.locator('.thread').count()==0,'card alone on the first screen')
    pg.screenshot(path=HERE+'/tests/out/c34_card.png')
    pg.click('[data-a=sug-yes]'); wait(pg); ok(pg.locator('#f-ask').count()==1,'confirm opens the chase')
    nx=home_next(pg,'Currys refund'); print('  list:',nx.replace('\n',' | ')); ok('chase them' in nx,'list says chase them before the chase is saved')
    # 2 repair case with a missed visit goes to the chase, not the repair questions
    T2="Landlord said an engineer would come on Tuesday to fix the boiler but nobody turned up"; start(pg,T2)
    ok(pg.locator('.sug').count()==1,'repair case shows the card'); pg.click('[data-a=sug-yes]'); wait(pg)
    ok(pg.locator('#f-ask').count()==1 and pg.locator('form[data-f=what]').count()==0,'repair: chase, no appliance questions')
    # 3 future promise: short title
    T3="British Gas said the engineer will come on Friday morning"; start(pg,T3); pg.click('[data-a=sug-yes]'); wait(pg)
    t=task(pg,T3); print('  title:',t['title']); ok(t['title']=='British Gas engineer visit','confirmed promise keeps a short name that says what it is (v55, no date to go stale)')
    # 4 paste a message into that case: new date replaces the old
    pg.click('[data-a=panel][data-p=paste]'); wait(pg)
    pg.fill('#f-paste',"Hi Baldwin, your engineer visit has been moved to "+A4["long"]+" between 12pm and 4pm. Your reference is BG-55123. Thanks, British Gas"); pg.click('form[data-f=paste] button[type=submit]'); wait(pg)
    c=pg.locator('.sug').inner_text() if pg.locator('.sug').count() else ''; print('  card:',c.replace('\n',' | '))
    ok(A4['short'] in c and '12:00' in c and 'BG-55123' in c,'pasted message read: new date, time and reference')
    pg.click('[data-a=sug-yes]'); wait(pg); t=task(pg,T3)
    ok([x['status'] for x in t['promises']]==['replaced','open'] and t['promises'][1]['ref']=='BG-55123','new promise replaces the old one')
    # 5 a case started from a pasted message
    T5="Hello, thank you for contacting Argos. Your refund of £249.99 has been processed. Please allow 3-5 working days for it to reach your account. Order 7712345."; start(pg,T5)
    t=task(pg,T5); print('  title:',t['title'],'| amount:',t['facts'].get('amount')); c=pg.locator('.sug').inner_text() if pg.locator('.sug').count() else ''; print('  card:',c.replace('\n',' | '))
    ok(t['title']=='Argos refund · 7712345' and 'Please allow' in c,'pasted message starts a case with a proposed promise')
    pg.click('[data-a=sug-yes]'); wait(pg)
    # 6 a message with no date
    pg.click('[data-a=panel][data-p=paste]'); wait(pg); pg.fill('#f-paste',"We are looking into this and will be in touch."); pg.click('form[data-f=paste] button[type=submit]'); wait(pg)
    ok("couldn’t find a date" in pg.inner_text('main'),'no date: says so, changes nothing')
    # 7 wins line once a case is finished
    pg.evaluate("""(t)=>{var db=JSON.parse(localStorage.getItem('__mockdb'));var x=db.tasks.find(y=>y.data.said===t).data;x.board='done';x.promises.forEach(q=>q.status='kept');localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}""",T5)
    pg.goto('https://sorted.test/'); wait(pg,600); w=pg.locator('.wins').inner_text() if pg.locator('.wins').count() else ''; print('  wins:',w.replace('\n',' | '))
    ok('1 case finished' in w and '£250' in w,'wins line counts the finished case and the refund')
    b.close()
print('ERRORS',errs); print('FAILS',fails)
