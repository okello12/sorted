# v39: sentences from the live stress tests (1-2 October 2026). Sorted must not hear a promise where a person would hear
# their own plan, a maybe, an instruction or "nobody promised", and must not invent a day for "at 5".
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
    pg.goto('https://sorted.test/'); wait(pg,300)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg,150)
    pg.fill('#f-case',text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
    if pg.locator('[data-a=safe-continue]').count(): pg.click('[data-a=safe-continue]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg)
    return pg.evaluate("(x)=>{var t=JSON.parse(localStorage.getItem('__mockdb')).tasks.map(y=>y.data).filter(y=>y.said===x).pop();return t||null}",text)
def sug(pg,text):
    t=start(pg,text); return (t or {}).get('sugP')
def local(iso): return datetime.datetime.fromisoformat(iso.replace('Z','+00:00')).astimezone()
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE+'/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE+'/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg,200); pg.click('[data-a=anon-start]'); wait(pg)
    # not promises
    for T,why in [("I promised myself I'd call Currys on Friday.","my own plan"),
                  ("I said I would call British Gas on Friday.","my own plan"),
                  ("Currys said their lines are open Friday 9am-5pm.","opening hours"),
                  ("British Gas said call us Friday if you still need help.","an instruction"),
                  ("They said maybe the engineer will come Friday.","a maybe"),
                  ("They said the engineer might come Friday.","a might"),
                  ("No one has promised anything. I want to call Currys on Friday.","nobody promised"),
                  ("The engineer will come at 5","no day, and no am or pm")]:
        t=start(pg,T); ok(t is not None and not t.get('sugP'),'not a promise (%s): %s'%(why,T))
    # 2 October rigorous test: 7 that slipped through in v40, and the 19 it listed as correctly rejected
    for T in ["They said if the part arrives, the engineer may come tomorrow.",
              "They promised nothing and told me to call tomorrow.",
              "Currys said the shop closes tomorrow at 6pm.",
              "British Gas said appointments are available tomorrow.",
              "They said please call tomorrow.",
              "They said check back tomorrow.",
              "They said we'll be open tomorrow.",
              "I promised myself I'd call Currys tomorrow.","I said I would call British Gas tomorrow.","I need to call Currys tomorrow.",
              "My plan is to email Amazon tomorrow.","They said maybe the engineer will come tomorrow.","They said the engineer might come tomorrow.",
              "They said hopefully the refund arrives tomorrow.","No one has promised anything. I want to call Currys tomorrow.",
              "Nobody promised a date; I will chase tomorrow.","They never promised a date.","Refunds usually take five working days.",
              "A refund can take five working days.","The website says delivery takes three days.","The email says I should contact them by tomorrow.",
              "I told the landlord I'd be home tomorrow.","Currys did not promise the refund tomorrow.","Currys refused to promise a date.",
              "There is no guarantee the refund arrives tomorrow.","They wouldn't give me a date for the engineer"]:
        t=start(pg,T); ok(t is not None and not t.get('sugP'),'not a promise: %s'%T)
    # and 12 clear promises that must still be heard
    F=ahead(18)['dm']
    for T in ["Currys promised a refund by tomorrow, order 445566","British Gas said the engineer will come tomorrow morning, ref BG-2231",
              "The landlord promised the boiler will be fixed by "+F,"Amazon said the refund will be paid within 5 working days",
              "John Lewis promised a replacement tomorrow","EE said the credit will be applied within 3 days",
              "Sky said the engineer will come tomorrow between 8 and 12","Aviva said they will call me back tomorrow afternoon",
              "DWP said the payment will be made by "+F,"BA promised the refund within 10 working days",
              "Vodafone confirmed the credit will show by Friday","The letting agent said the plumber will come on Thursday at 10am"]:
        t=start(pg,T); ok(t is not None and t.get('sugP') and not t['sugP'].get('past'),'promise heard: %s'%T)
    # still promises
    r=sug(pg,"Currys promised a refund within 14 days, three weeks ago, order 88421")
    ok(r and r['past'] and r['ref']=='88421','passed Currys promise, with its reference')
    r=sug(pg,"British Gas said the engineer will come on Friday morning")
    ok(r and local(r['dueAt']).strftime('%A %H:%M')=='Friday 08:00' and r['party']=='British Gas','Friday morning is Friday 08:00 to 12:00')
    r=sug(pg,"They promised it by 5 October")
    ok(r and r['allDay'] and local(r['dueAt']).day==5,'"by 5 October" is a date, not 5 o’clock')
    r=sug(pg,"They said tomorrow between 2 and 4, ref A1842")
    ok(r and local(r['dueAt']).date()==ahead(1)['date'] and local(r['dueAt']).hour==14 and r['ref']=='A1842','tomorrow between 2 and 4 is 14:00 to 16:00, ref kept')
    r=sug(pg,"Oakridge promised the repair would be done by Friday")
    ok(r and r['party']=='Oakridge','a company Sorted doesn’t know keeps its name: %s'%(r and r['party']))
    r=sug(pg,"They said the engineer will come Friday at 5")
    ok(r is not None,'a time with a day is still offered')
    # two promises in one sentence: first kept, second mentioned
    T="Currys promised a refund by Friday and a replacement next Tuesday, order 99"; t=start(pg,T)
    card=pg.inner_text('.sug') if pg.locator('.sug').count() else ''
    ok('A refund by Friday' in card and 'replacement' not in card.split('You also mentioned')[0],'two promises: the card quotes only the first')
    ok('You also mentioned' in card and 'replacement next Tuesday' in card,'two promises: the second is mentioned')
    # a long typed sentence read like a message is not called "the message you pasted"
    T="The refund will be paid by Friday and a replacement sent out next Tuesday"; t=start(pg,T)
    card=pg.inner_text('.sug') if pg.locator('.sug').count() else ''
    ok(card and 'pasted' not in card and 'from what you wrote' in card.lower() and 'picked this date out of what you wrote' in card,'typed text is not called a pasted message')
    T="Oakridge promised the repair would be done by Friday"; t=start(pg,T)
    ok(t and len(t['title'])<=45 and t['title'].startswith('Oakridge'),'unconfirmed card: short title naming them (%s)'%(t and t['title']))
    # nonsense asks first; "Start anyway" still works
    pg.goto('https://sorted.test/'); wait(pg,300)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
    n0=len(pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks"))
    pg.fill('#f-case','The sky is blue and I like toast'); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    ok(pg.locator('[data-a=vague-go]').count()==1 and 'can’t see what needs sorting' in pg.inner_text('main'),'nonsense: Sorted asks what needs sorting')
    pg.click('[data-a=vague-edit]'); wait(pg)
    ok(pg.evaluate("document.activeElement.id")=='f-case' and pg.locator('form[data-f=case] button[type=submit]').count()==1,'"Change what I wrote" goes back to the box')
    pg.click('form[data-f=case] button[type=submit]'); wait(pg); pg.click('[data-a=vague-go]'); wait(pg)
    ok(pg.locator('form[data-f=baseline]').count()==1,'"Start anyway" still starts the case')
    # a real problem doesn't get the question
    pg.goto('https://sorted.test/'); wait(pg,300)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
    pg.fill('#f-case','My heating has been broken since Monday'); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    ok(pg.locator('[data-a=vague-go]').count()==0,'a real problem is not questioned')
    t=start(pg,'My heating has been broken since Monday'); ok(t and t['facts'].get('since')=='Monday','"since Monday" is kept for the repair report')
    t=start(pg,'No hot water for 48 hours'); ok(t and t['facts'].get('dur')=='48 hours','hours count as how long')
    b.close()
print('ERRORS',errs); print('FAILS',fails)
