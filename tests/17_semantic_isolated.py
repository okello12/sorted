import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
from dates import ahead
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m): print(('PASS ' if c else 'FAIL ')+m); fails.append(m) if not c else None
def wait(pg,ms=180): pg.wait_for_timeout(ms)
def run(pg,text):
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg); pg.click('[data-a=anon-start]'); wait(pg)
    pg.fill('#f-case',text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
    if pg.locator('[data-a=safe-continue]').count(): pg.click('[data-a=safe-continue]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg)
    return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks.map(x=>x.data).pop()")
NEG=[
"I promised myself I'd call Currys tomorrow.","I said I would call British Gas tomorrow.","I told myself to ring the landlord tomorrow.","I need to call Currys tomorrow.","My plan is to email Amazon tomorrow.","Currys said their lines are open tomorrow 9am to 5pm.","British Gas said call us tomorrow if you still need help.","The landlord said I should contact the plumber tomorrow.","They said maybe the engineer will come tomorrow.","They said the engineer might come tomorrow.","They said the engineer could possibly come tomorrow.","They said hopefully the refund arrives tomorrow.","They said if the part arrives, the engineer may come tomorrow.","No one has promised anything. I want to call Currys tomorrow.","Nobody promised a date; I will chase tomorrow.","They never promised a date. I plan to ring tomorrow.","There is no promise yet. I will email them tomorrow.","They promised nothing and told me to call tomorrow.","Currys said the shop closes tomorrow at 6pm.","British Gas said appointments are available tomorrow.","They said refunds usually take five working days.","They said a refund can take five working days.","Their website says delivery takes three days.","The email says I should contact them by tomorrow.","They said please call tomorrow.","They said check back tomorrow.","They said we'll be open tomorrow.","I told the landlord I'd be home tomorrow.","The engineer will come at 5.","I have an appointment reminder to call them tomorrow.","Currys did not promise the refund tomorrow; they only said to call.","Currys hasn't promised a refund date. I will call tomorrow.","Currys refused to promise a date and asked me to ring tomorrow.","Currys said there is no guarantee the refund arrives tomorrow."
]
POS=[
"Currys promised the refund will arrive tomorrow, order 10001.","British Gas said the engineer will come tomorrow morning, ref BG-10002.","Oakridge promised the boiler would be fixed by "+ahead(4)['dm']+", ref OA-10003.","Amazon confirmed the refund will be paid within 5 working days, order 10004.","John Lewis told me the replacement will arrive tomorrow, ref JL-10005.","EE agreed the credit will show within 3 days, ref EE-10006.","Sky booked an engineer for tomorrow between 1pm and 4pm, ref SKY-10007.","The insurer confirmed they will call me tomorrow afternoon, ref INS-10009.","DWP said the payment will arrive by "+ahead(3)['dm']+", ref DWP-10011.","The airline promised a refund within 10 working days, ref AIR-10012.","Vodafone confirmed the credit will be applied by "+ahead(7)['dm']+", ref VOD-10014.","The landlord said the plumber will come tomorrow between 8am and 12pm, ref LL-10015."
]
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London'); ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript')); ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body='')); pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))
    for i,t in enumerate(NEG):
        x=run(pg,t); ok(not x.get('sugP'),'NEG%02d %s'%(i,t))
    for i,t in enumerate(POS):
        x=run(pg,t); ok(bool(x.get('sugP')),'POS%02d %s'%(i,t))
    # XSS and long text
    x=run(pg,'<img src=x onerror="window.__pwned=1"> Currys promised the refund tomorrow, ref XSS-1.'); ok(pg.evaluate('window.__pwned||0')==0,'HTML inert')
    longt=('Background. '*450)+'Currys promised the refund by '+ahead(5)['dm']+', order LONG-1.'; x=run(pg,longt); ok(len(x.get('said',''))<=300 and bool(x.get('sugP')),'long text capped but late promise found')
    b.close()
print('ERRORS',errs); print('FAILS',fails)
