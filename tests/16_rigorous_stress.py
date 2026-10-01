# Rigorous v40 stress pass, 2 Oct 2026. Runs only against the local mocked build.
# Goal: semantic false positives/negatives, state-machine invariants, repeated actions,
# shared-input handling, reload persistence, long/unusual text, and basic render stability.
import os, sys, random, datetime, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
from dates import ahead
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=220): pg.wait_for_timeout(ms)
def db(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')||'{\"tasks\":[],\"shares\":[]}')")
def tasks(pg): return [x['data'] for x in db(pg).get('tasks',[])]
def last_for(pg,text):
    xs=[x for x in tasks(pg) if x.get('said')==text or str(x.get('said','')).startswith(text[:80])]
    return xs[-1] if xs else None
def home(pg): pg.goto('https://sorted.test/'); wait(pg,280)
def compose_open(pg):
    home(pg)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg,100)
def start(pg,text):
    compose_open(pg)
    pg.fill('#f-case',text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
    if pg.locator('[data-a=safe-continue]').count(): pg.click('[data-a=safe-continue]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count():
        pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg)
    return last_for(pg,text)
def fresh(pg):
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg,160)
    pg.click('[data-a=anon-start]'); wait(pg)
def one_open(t): return len([p for p in (t or {}).get('promises',[]) if p.get('status')=='open'])==1

def date_dm(days): return ahead(days)['dm']

NEG=[
 "I promised myself I'd call Currys tomorrow.",
 "I said I would call British Gas tomorrow.",
 "I told myself to ring the landlord tomorrow.",
 "I need to call Currys tomorrow.",
 "My plan is to email Amazon tomorrow.",
 "Currys said their lines are open tomorrow 9am to 5pm.",
 "British Gas said call us tomorrow if you still need help.",
 "The landlord said I should contact the plumber tomorrow.",
 "They said maybe the engineer will come tomorrow.",
 "They said the engineer might come tomorrow.",
 "They said the engineer could possibly come tomorrow.",
 "They said hopefully the refund arrives tomorrow.",
 "They said if the part arrives, the engineer may come tomorrow.",
 "No one has promised anything. I want to call Currys tomorrow.",
 "Nobody promised a date; I will chase tomorrow.",
 "They never promised a date. I plan to ring tomorrow.",
 "There is no promise yet. I will email them tomorrow.",
 "They promised nothing and told me to call tomorrow.",
 "Currys said the shop closes tomorrow at 6pm.",
 "British Gas said appointments are available tomorrow.",
 "They said refunds usually take five working days.",
 "They said a refund can take five working days.",
 "Their website says delivery takes three days.",
 "The email says I should contact them by tomorrow.",
 "They said please call tomorrow.",
 "They said check back tomorrow.",
 "They said we'll be open tomorrow.",
 "I told the landlord I'd be home tomorrow.",
 "The engineer will come at 5.",
 "I have an appointment reminder to call them tomorrow."
]
POS=[
 "Currys promised the refund will arrive tomorrow, order 10001.",
 "British Gas said the engineer will come tomorrow morning, ref BG-10002.",
 "Oakridge promised the boiler would be fixed by "+date_dm(4)+", ref OA-10003.",
 "Amazon confirmed the refund will be paid within 5 working days, order 10004.",
 "John Lewis told me the replacement will arrive tomorrow, ref JL-10005.",
 "EE agreed the credit will show within 3 days, ref EE-10006.",
 "Sky booked an engineer for tomorrow between 1pm and 4pm, ref SKY-10007.",
 "The garage agreed the car will be ready by "+date_dm(5)+", ref GAR-10008.",
 "The insurer confirmed they will call me tomorrow afternoon, ref INS-10009.",
 "The council confirmed an inspection for "+date_dm(6)+" at 10am, ref COU-10010.",
 "DWP said the payment will arrive by "+date_dm(3)+", ref DWP-10011.",
 "The airline promised a refund within 10 working days, ref AIR-10012.",
 "Apple said the replacement will be delivered tomorrow, ref APP-10013.",
 "Vodafone confirmed the credit will be applied by "+date_dm(7)+", ref VOD-10014.",
 "The landlord said the plumber will come tomorrow between 8am and 12pm, ref LL-10015.",
 "Argos promised the refund by "+date_dm(8)+", order 10016.",
 "HMRC said the repayment will be issued within 7 days, ref HM-10017.",
 "The courier confirmed delivery tomorrow between 2pm and 5pm, ref CUR-10018.",
 "The repair company booked the technician for "+date_dm(2)+" at 9am, ref REP-10019.",
 "The bank confirmed the chargeback credit by "+date_dm(9)+", ref BNK-10020."
]

with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE+'/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE+'/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e: errs.append(str(e))); fresh(pg)

    # 1. Semantic classifier matrix: deliberately difficult non-promises vs clear commitments.
    for i,T in enumerate(NEG):
        t=start(pg,T); ok(t is not None and not t.get('sugP'), 'negative[%02d] not heard as promise: %s'%(i,T))
    for i,T in enumerate(POS):
        t=start(pg,T); ok(t is not None and t.get('sugP') is not None, 'positive[%02d] promise found: %s'%(i,T))

    # 2. Robustness to punctuation, casing, whitespace and curly apostrophes on a clear promise.
    base="Currys promised the refund will arrive tomorrow, order 771122."
    variants=[
      base.upper(), base.lower(),
      "  Currys   promised   the refund will arrive tomorrow, order 771122.  ",
      "Currys promised: the refund will arrive tomorrow — order 771122.",
      "Currys promised the refund will arrive tomorrow! Order 771122.",
      "Currys promised the refund will arrive tomorrow; order 771122.",
      "Currys promised the refund will arrive tomorrow\norder 771122.",
      "Currys promised the refund will arrive tomorrow, order #771122.",
      "Currys promised the refund will arrive tomorrow, ref: 771122.",
      "Currys promised the refund will arrive tomorrow 🙂 order 771122."
    ]
    for i,T in enumerate(variants):
        t=start(pg,T); ok(t is not None and t.get('sugP') is not None,'variant[%02d] still finds clear promise'%i)

    # 3. Negation/tentative mutations must remain negative.
    for word in ['maybe','possibly','perhaps','might','may']:
        T="Currys said %s the refund will arrive tomorrow, order 8800."%word
        t=start(pg,T); ok(t is not None and not t.get('sugP'),'tentative %s rejected'%word)
    for T in [
      "Currys did not promise the refund tomorrow; they only said to call.",
      "Currys hasn't promised a refund date. I will call tomorrow.",
      "Currys refused to promise a date and asked me to ring tomorrow.",
      "Currys said there is no guarantee the refund arrives tomorrow."
    ]:
        t=start(pg,T); ok(t is not None and not t.get('sugP'),'explicit non-commitment rejected: '+T)

    # 4. Long text, Unicode and HTML-like input: must not crash or execute markup; useful promise at tail should survive parsing.
    longT=("Background information that should not become the case title. "*60)+"Currys promised the refund will arrive by "+date_dm(5)+", order LONG-4455."
    t=start(pg,longT); ok(t is not None,'long input creates a case without crash')
    ok(t and len(t.get('said',''))<=300,'long input retained text capped at 300 chars')
    ok(t and t.get('sugP') is not None,'long input still extracts late promise')
    evil='<img src=x onerror="window.__pwned=1"> Currys promised the refund tomorrow, ref XSS-1.'
    t=start(pg,evil); ok(pg.evaluate("window.__pwned||0")==0,'HTML-like input is rendered inert')
    ok(t is not None,'HTML-like input does not crash case creation')
    uni="🏠 Oakridge said the engineer will come tomorrow 08:00–12:00 — ref Ω-7788."
    t=start(pg,uni); ok(t is not None and t.get('sugP') is not None,'Unicode punctuation/emoji input remains usable')

    # 5. State-machine invariants under rapid confirmation and repeated rescheduling.
    T="StressCo promised the engineer will come tomorrow 9am to 12pm, ref ST-1."
    t=start(pg,T); ok(t and t.get('sugP'),'state test starts with proposed promise')
    pg.evaluate("(()=>{let b=document.querySelector('[data-a=sug-yes]'); if(b){b.click(); try{b.click()}catch(e){}}})()") ; wait(pg,450)
    t=last_for(pg,T); ok(t and len(t.get('promises',[]))==1 and one_open(t),'double confirm creates exactly one open promise')
    tid=t.get('id') if t else None
    for n,days in enumerate([3,5,7],start=2):
        # Open paste-message panel and feed a replacement commitment.
        if pg.locator('[data-a=panel][data-p=paste]').count()==0:
            pg.reload(); wait(pg,300)
        if pg.locator('[data-a=panel][data-p=paste]').count(): pg.click('[data-a=panel][data-p=paste]'); wait(pg,120)
        msg="StressCo: engineer moved to %s between 1pm and 3pm. Ref ST-%d."%(date_dm(days),n)
        pg.fill('#f-paste',msg); pg.click('form[data-f=paste] button[type=submit]'); wait(pg,250)
        ok(pg.locator('.sug').count()==1,'replacement %d produces confirmation card'%n)
        pg.click('[data-a=sug-yes]'); wait(pg,350)
        t=pg.evaluate("(id)=>JSON.parse(localStorage.getItem('__mockdb')).tasks.map(x=>x.data).find(x=>x.id===id)",tid)
        sts=[q.get('status') for q in t.get('promises',[])] if t else []
        ok(t and one_open(t) and sts.count('open')==1 and all(x=='replaced' for x in sts[:-1]),'replacement %d leaves one live promise: %s'%(n,sts))
        pg.reload(); wait(pg,300)
        t2=pg.evaluate("(id)=>JSON.parse(localStorage.getItem('__mockdb')).tasks.map(x=>x.data).find(x=>x.id===id)",tid)
        ok(t2 and one_open(t2),'replacement %d survives reload with one live promise'%n)

    # 6. Share-sheet stress: repeated hashes must not create cases until Start; latest payload wins; URL is scrubbed.
    home(pg); before=len(tasks(pg))
    for i in range(25):
        payload="Share burst %02d: BurstCo promised update tomorrow, ref B-%02d"%(i,i)
        pg.evaluate("x=>{location.hash='#new='+encodeURIComponent(x)}",payload); wait(pg,45)
    wait(pg,300)
    ok(len(tasks(pg))==before,'25 share-in events create no case before Start')
    ok('#new=' not in pg.url,'share-in text removed from URL after burst')
    ok(pg.locator('#f-case').count()==1 and 'B-24' in pg.input_value('#f-case'),'latest share-in payload wins cleanly')

    # 7. Maximum share payload is bounded and remains editable rather than silently creating a record.
    huge='Z'*6000+' Currys promised refund tomorrow ref HUGE-1'
    pg.evaluate("x=>{location.hash='#new='+encodeURIComponent(x)}",huge); wait(pg,350)
    val=pg.input_value('#f-case') if pg.locator('#f-case').count() else ''
    ok(len(val)<=4000,'shared payload capped at 4000 characters (%d)'%len(val))
    ok(len(tasks(pg))==before,'huge share payload still does not auto-save')

    # 8. Reload/page churn with many cases: no page errors and Home remains renderable.
    home(pg); wait(pg,350)
    ok(pg.locator('h1').count()>=1,'Home renders after stress corpus')
    for _ in range(5): pg.reload(); wait(pg,120)
    ok(pg.locator('main').count()==1 and pg.locator('h1').count()>=1,'five rapid reloads leave one usable app shell')

    # 9. Basic 200% text pressure: page must not acquire horizontal overflow on phone viewport.
    pg.evaluate("document.documentElement.style.fontSize='200%'"); wait(pg,120)
    dims=pg.evaluate("({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth})")
    ok(dims['sw']<=dims['cw']+3,'200% root text does not force horizontal page scroll: %s'%dims)

    b.close()
print('ERRORS',errs)
print('FAILS',fails)
