# Adversarial/random stress pack for Sorted v37. QA branch only.
import os, sys, json, datetime, random
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.')
errs=[]; fails=[]; notes=[]

def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)

def wait(pg,ms=250): pg.wait_for_timeout(ms)

def boot(browser, viewport=(390,844), email_ready=True):
    ctx=browser.new_context(viewport={'width':viewport[0],'height':viewport[1]}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE+'/tests/mock.js', content_type='application/javascript'))
    ctx.route('https://fonts.googleapis.com/**', lambda r: r.fulfill(body='', content_type='text/css'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE+'/public/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); local_err=[]; dialogs=[]
    pg.on('pageerror',lambda e: local_err.append(str(e)))
    pg.on('dialog',lambda d: (dialogs.append(d.message), d.dismiss()))
    pg.goto('https://sorted.test/#start');
    setup="localStorage.clear();"+("localStorage.setItem('__emailReady','1');" if email_ready else "")
    pg.evaluate(setup); pg.reload(); wait(pg,200)
    pg.click('[data-a=anon-start]'); wait(pg)
    return ctx,pg,local_err,dialogs

def start_case(pg,text):
    pg.goto('https://sorted.test/'); wait(pg,300)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg,100)
    pg.fill('#f-case',text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('[data-a=safe-continue]').count(): pg.click('[data-a=safe-continue]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count():
        pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg)

def get_task(pg,text):
    return pg.evaluate("(t)=>{let d=JSON.parse(localStorage.getItem('__mockdb'));return d.tasks.map(x=>x.data).find(x=>x.said===t||(x.said&&x.said.indexOf(t.slice(0,60))===0))}",text)

def run(browser,text, viewport=(390,844), email_ready=True):
    ctx,pg,pe,dialogs=boot(browser,viewport,email_ready)
    try:
        start_case(pg,text); t=get_task(pg,text); body=pg.inner_text('body');
        return ctx,pg,t,body,pe,dialogs
    except Exception as e:
        pe.append('HARNESS '+repr(e)); return ctx,pg,None,'',pe,dialogs

def close_result(ctx,pe,label):
    if pe:
        errs.extend([label+': '+x for x in pe])
    ctx.close()

with sync_playwright() as p:
    b=p.chromium.launch()
    today=datetime.date.today()
    future=(today+datetime.timedelta(days=8)).strftime('%-d %B')
    past=(today-datetime.timedelta(days=4)).strftime('%-d %B')
    viewports=[(320,568),(390,844),(412,915),(1440,900)]

    cases=[
      ('past_ref',"Currys promised a refund within 14 days, it's been three weeks, order 88421", lambda t: t and t.get('sugP') and t['sugP'].get('past') and t['sugP'].get('ref')=='88421'),
      ('future_slot',"British Gas said the engineer will come on Friday morning", lambda t: t and t.get('sugP') and not t['sugP'].get('past') and t['sugP'].get('dueEnd')),
      ('self_promise',"I promised myself I'd call Currys on Friday", lambda t: t and not t.get('sugP')),
      ('user_said',"I said I would call British Gas on Friday", lambda t: t and not t.get('sugP')),
      ('opening_hours_first_sentence',"Currys said their lines are open Friday 9am to 5pm", lambda t: t and not t.get('sugP')),
      ('instruction_not_promise',"British Gas said call us Friday if you still need help", lambda t: t and not t.get('sugP')),
      ('tentative_maybe',"They said maybe the engineer will come Friday", lambda t: t and not t.get('sugP')),
      ('tentative_might',"They said the engineer might come Friday", lambda t: t and not t.get('sugP')),
      ('firm_will',"They said the engineer will come Friday", lambda t: t and t.get('sugP')),
      ('price_only',"Amazon said my refund will be £12.50", lambda t: t and not t.get('sugP') and t.get('facts',{}).get('amount')==12.5),
      ('date_not_time',"Argos promised the refund by 5 October", lambda t: t and t.get('sugP') and t['sugP'].get('allDay')),
      ('explicit_past',f"British Gas promised an engineer on {past} but nobody came", lambda t: t and t.get('sugP') and t['sugP'].get('past')),
      ('explicit_future',f"British Gas confirmed an engineer on {future}", lambda t: t and t.get('sugP') and not t['sugP'].get('past')),
      ('currency_not_time',"Argos promised a refund of £1,500.50 within 5 days", lambda t: t and t.get('sugP') and t.get('facts',{}).get('amount')==1500.5),
      ('sky_common_word',"The sky is leaking through the ceiling, landlord said they'd fix it by Friday", lambda t: t and t.get('facts',{}).get('party')!='Sky'),
      ('windows_common_word',"The windows are cracked and the landlord said they will repair them by Friday", lambda t: t and t.get('facts',{}).get('item')=='Window'),
      ('unicode_apostrophe',"John Lewis said they’ll refund me by Friday, ref JL-123", lambda t: t and t.get('sugP') and t['sugP'].get('ref')),
      ('within_hours',"EE promised the credit would appear within 48 hours", lambda t: t and t.get('sugP')),
      ('business_days',"Vodafone said the refund will arrive within two business days", lambda t: t and t.get('sugP')),
      ('tomorrow_time',"The landlord confirmed the engineer will arrive tomorrow at 9am", lambda t: t and t.get('sugP') and not t['sugP'].get('allDay')),
      ('no_promise',"No one has promised anything. I want to call Currys on Friday", lambda t: t and not t.get('sugP')),
      ('xss_text',"Currys said the refund will arrive by Friday <img src=x onerror=alert(1)>", lambda t: t and t.get('sugP')),
    ]

    for i,(name,text,expect) in enumerate(cases):
        ctx,pg,t,body,pe,dialogs=run(b,text,viewports[i%len(viewports)])
        good=False
        try: good=bool(expect(t))
        except Exception: good=False
        ok(good,name)
        ok(not pe,name+' no page errors')
        if name=='xss_text':
            ok(pg.locator('img[src="x"]').count()==0 and not dialogs,'xss text remains inert')
        close_result(ctx,pe,name)

    # Long input / storage pressure. The saved case text should be bounded and UI must stay alive.
    long_text="Currys said the refund will arrive by Friday. "+("account 12345 extra irrelevant words "*450)
    ctx,pg,t,body,pe,dialogs=run(b,long_text,(390,844))
    ok(t is not None,'long input creates a case')
    ok(t is not None and len(t.get('said',''))<=300,'long input is bounded to 300 chars in saved case text')
    ok(not pe,'long input no page errors')
    close_result(ctx,pe,'long_input')

    # No-email path: confirming a future promise must still park the case in Waiting.
    ctx,pg,t,body,pe,dialogs=run(b,"British Gas said the engineer will come next Friday",(390,844),False)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg,500)
    t=get_task(pg,"British Gas said the engineer will come next Friday")
    ok(t is not None and t.get('board')=='waiting','no-email: case still enters Waiting')
    pg.reload(); wait(pg,500); t=get_task(pg,"British Gas said the engineer will come next Friday")
    ok(t is not None and t.get('board')=='waiting','no-email: Waiting survives reload')
    ok(not pe,'no-email no page errors')
    close_result(ctx,pe,'no_email')

    # Double-confirm stress: two synthetic clicks must never create two promises.
    ctx,pg,t,body,pe,dialogs=run(b,"Amazon said the refund will arrive next Friday",(390,844))
    if pg.locator('[data-a=sug-yes]').count():
        pg.evaluate("()=>{const b=document.querySelector('[data-a=sug-yes]'); b.dispatchEvent(new MouseEvent('click',{bubbles:true})); b.dispatchEvent(new MouseEvent('click',{bubbles:true}));}")
        wait(pg,600)
    t=get_task(pg,"Amazon said the refund will arrive next Friday")
    ok(t is not None and len(t.get('promises',[]))==1,'double-confirm creates exactly one promise')
    ok(not pe,'double-confirm no page errors')
    close_result(ctx,pe,'double_confirm')

    b.close()

print('NOTES',notes)
print('ERRORS',errs)
print('FAILS',fails)
