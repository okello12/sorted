import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
from dates import ahead
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m):
 print(('PASS ' if c else 'FAIL ')+m); fails.append(m) if not c else None
def wait(pg,ms=180): pg.wait_for_timeout(ms)
def fresh(pg):
 pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg); pg.click('[data-a=anon-start]'); wait(pg)
def start(pg,text):
 pg.goto('https://sorted.test/'); wait(pg,220)
 if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg,80)
 pg.fill('#f-case',text); pg.click('form[data-f=case] button[type=submit]'); wait(pg,180)
 if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg,100)
 if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg,100)
 if pg.locator('[data-a=safe-continue]').count(): pg.click('[data-a=safe-continue]'); wait(pg,100)
 if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg,140)
 return pg.evaluate("(x)=>{let d=JSON.parse(localStorage.getItem('__mockdb'));let a=d.tasks.map(y=>y.data).filter(y=>y.said===x||String(y.said||'').startsWith(x.slice(0,80)));return a[a.length-1]||null}",text)
def dm(n): return ahead(n)['dm']
NEG=[
"I promised myself I'd call Currys tomorrow.","I said I would call British Gas tomorrow.","I told myself to ring the landlord tomorrow.","My plan is to email Amazon tomorrow.",
"Currys said their lines are open tomorrow 9am to 5pm.","British Gas said call us tomorrow if you still need help.","The landlord said I should contact the plumber tomorrow.",
"They said maybe the engineer will come tomorrow.","They said the engineer might come tomorrow.","They said the engineer could possibly come tomorrow.","They said hopefully the refund arrives tomorrow.",
"No one has promised anything. I want to call Currys tomorrow.","Nobody promised a date; I will chase tomorrow.","They never promised a date. I plan to ring tomorrow.","There is no promise yet. I will email them tomorrow.",
"Currys said the shop closes tomorrow at 6pm.","British Gas said appointments are available tomorrow.","They said refunds usually take five working days.","They said a refund can take five working days.",
"Their website says delivery takes three days.","The email says I should contact them by tomorrow.","They said please call tomorrow.","They said check back tomorrow.","They said we'll be open tomorrow.",
"I told the landlord I'd be home tomorrow.","The engineer will come at 5.","I have an appointment reminder to call them tomorrow.",
"Currys did not promise the refund tomorrow; they only said to call.","Currys hasn't promised a refund date. I will call tomorrow.","Currys refused to promise a date and asked me to ring tomorrow.",
"Currys said there is no guarantee the refund arrives tomorrow.","They said they'd try to send the refund tomorrow.","They said they hope to send an engineer tomorrow.","They said Friday is likely but not confirmed.",
"They said if the part arrives they may come tomorrow.","They said someone should call tomorrow.","They said I should call tomorrow.","I was told to call them tomorrow.","The website promised nothing; it says refunds can take 5 days."
]
POS=[
"Currys promised the refund will arrive tomorrow, order 10001.","British Gas said the engineer will come tomorrow morning, ref BG-10002.",
"Oakridge promised the boiler would be fixed by "+dm(4)+", ref OA-10003.","Amazon confirmed the refund will be paid within 5 working days, order 10004.",
"John Lewis told me the replacement will arrive tomorrow, ref JL-10005.","EE agreed the credit will show within 3 days, ref EE-10006.",
"Sky booked an engineer for tomorrow between 1pm and 4pm, ref SKY-10007.","The garage agreed the car will be ready by "+dm(5)+", ref GAR-10008.",
"The insurer confirmed they will call me tomorrow afternoon, ref INS-10009.","The council confirmed an inspection for "+dm(6)+" at 10am, ref COU-10010.",
"DWP said the payment will arrive by "+dm(3)+", ref DWP-10011.","The airline promised a refund within 10 working days, ref AIR-10012.",
"Apple said the replacement will be delivered tomorrow, ref APP-10013.","Vodafone confirmed the credit will be applied by "+dm(7)+", ref VOD-10014.",
"The landlord said the plumber will come tomorrow between 8am and 12pm, ref LL-10015.","Argos promised the refund by "+dm(8)+", order 10016.",
"HMRC said the repayment will be issued within 7 days, ref HM-10017.","The courier confirmed delivery tomorrow between 2pm and 5pm, ref CUR-10018.",
"The repair company booked the technician for "+dm(2)+" at 9am, ref REP-10019.","The bank confirmed the chargeback credit by "+dm(9)+", ref BNK-10020."
]
with sync_playwright() as p:
 b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London')
 ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
 ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
 pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(str(e))); fresh(pg)
 for i,T in enumerate(NEG):
  t=start(pg,T); ok(t is not None and not t.get('sugP'),'negative[%02d]'%i)
 for i,T in enumerate(POS):
  t=start(pg,T); ok(t is not None and t.get('sugP') is not None,'positive[%02d]'%i)
 variants=["CURRYS PROMISED THE REFUND WILL ARRIVE TOMORROW, ORDER 771122.","currys promised the refund will arrive tomorrow, order 771122.","  Currys   promised   the refund will arrive tomorrow, order 771122.  ","Currys promised: the refund will arrive tomorrow — order 771122.","Currys promised the refund will arrive tomorrow! Order 771122.","Currys promised the refund will arrive tomorrow; order #771122.","Currys promised the refund will arrive tomorrow 🙂 order 771122."]
 for i,T in enumerate(variants):
  t=start(pg,T); ok(t is not None and t.get('sugP') is not None,'variant[%02d]'%i)
 past=start(pg,"Currys promised a refund within 14 days, three weeks ago, order 88421")
 ok(past and past.get('sugP') and past['sugP'].get('past') and past['sugP'].get('ref')=='88421','past relative promise')
 two=start(pg,"Currys promised a refund by Friday and a replacement next Tuesday, order 99")
 ok(two and two.get('sugP') and two['sugP'].get('also'),'two promises surfaced without merging')
 b.close()
print('ERRORS',errs); print('FAILS',fails)
