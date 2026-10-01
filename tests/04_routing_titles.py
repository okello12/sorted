import os, json
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=350): pg.wait_for_timeout(ms)
CASES=[
 ("Currys promised a refund in 14 days for the laptop I returned, it's been three weeks, order 88421","call","Currys refund · 88421"),
 ("Landlord still hasn't fixed the heating, boiler off for two weeks, house freezing","fix","Heating or hot water · landlord"),
 ("DWP hasn't paid my Universal Credit and nobody has replied to my journal in 9 days","call","Universal Credit"),
 ("Washing machine stopped draining","fix","Washing machine"),
 ("Amazon parcel never arrived and they keep saying it was delivered","call",None),
 ("My bank account 12345678 was charged twice by Sky","call","Sky refund"),
]
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE+'/tests/mock.js', content_type='application/javascript'))
    ctx.route('https://fonts.googleapis.com/**', lambda r: r.fulfill(body='', content_type='text/css'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE+'/public/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear()"); pg.reload(); wait(pg,200); pg.click('[data-a=anon-start]'); wait(pg)
    for text,mode,title in CASES:
        pg.goto('https://sorted.test/'); wait(pg,400)
        if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg,150)
        pg.fill('#f-case',text); pg.click('form[data-f=case] button'); wait(pg,300)
        if pg.locator('[data-a=safe-continue]').count(): pg.click('[data-a=safe-continue]'); wait(pg,300)
        pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg,400)
        if pg.locator('[data-a=sug-no]').count(): pg.click('[data-a=sug-no]'); wait(pg,300)
        t=pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks.map(x=>x.data).find(x=>x.said===%s)"%json.dumps(text))
        ok(t is not None and t['mode']==mode,'%s… → %s route (%s)'%(text[:28],mode,t and t['mode']))
        if title: ok(t['title']==title,'  title "%s"'%t['title'])
        else: print('  title "%s"'%t['title'])
        ok(any('In your words' in e['label'] for e in t['events']),'  full sentence kept in history')
        m=pg.inner_text('main')
        if mode=='fix':
            ok("Won't drain" not in m or 'Washing' in text,'  no washing-machine options unless named')
            iv=pg.input_value('#f-item') if pg.locator('#f-item').count() else '(WM chips)'; print('  item field:',iv)
        else:
            ask=pg.input_value('#f-ask'); who=pg.input_value('#f-who'); print('  who:',who,'| ask:',ask)
            if 'Currys' in text: ok('refund' in ask and '88421' in ask and 'repair' not in ask,'  message says refund + order no.')
            if 'DWP' in text: ok('Citizens Advice' in m and 'journal' in m,'  honest DWP note shown'); ok(pg.get_attribute('[data-k=via][data-v=account]','aria-pressed')=='true','  UC defaults to app/account')
            if '12345678' in text: ok('12345678' not in ask and '12345678' not in t['title'],'  bank account number not copied')
    # landlord heating: who step preselected
    b.close()
print('ERRORS',errs); print('FAILS',fails)
