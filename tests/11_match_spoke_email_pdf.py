import os, json
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from dates import A4,A5,A6,A10
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); O=HERE+'/tests/node_modules/'; errs=[]; fails=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
def wait(pg,ms=350): pg.wait_for_timeout(ms)
H={'Access-Control-Allow-Origin':'*'}
def cdn(r):
    u=r.request.url
    if '/npm/tesseract.js@5.1.1/dist/' in u: return r.fulfill(path=O+'tesseract.js/dist/'+u.split('/dist/')[1], content_type='application/javascript', headers=H)
    if '/npm/tesseract.js-core@5.1.1/' in u: f=u.split('@5.1.1/')[1]; return r.fulfill(path=O+'tesseract.js-core/'+f, content_type='application/wasm' if f.endswith('.wasm') else 'application/javascript', headers=H)
    if '/npm/@tesseract.js-data/eng@1.0.0/' in u: return r.fulfill(path=O+'@tesseract.js-data/eng/4.0.0_best_int/eng.traineddata.gz', content_type='application/gzip', headers=H)
    if '/npm/pdfjs-dist@3.11.174/build/' in u: return r.fulfill(path=O+'pdfjs-dist/build/'+u.split('/build/')[1], content_type='application/javascript', headers=H)
    return r.fulfill(path=HERE+'/tests/mock.js', content_type='application/javascript')
def compose(pg,text):
    pg.goto('https://sorted.test/'); wait(pg,400)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg,150)
    pg.fill('#f-case',text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
def plan(pg):
    if pg.locator('[data-a=safe-continue]').count(): pg.click('[data-a=safe-continue]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg)
def tasks(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks.map(x=>x.data)")
with sync_playwright() as p:
    b=p.chromium.launch()
    # files: a typed letter PDF and a scanned one
    lp=b.new_page(); lp.set_content('<body style="font-family:Arial;padding:40px;font-size:15px"><p>Thames Water</p><p>Dear customer,</p><p>Thank you for reporting the leak. An engineer will visit on '+A6['long']+' between 1pm and 5pm.</p><p>Your job reference is TW-448812.</p><p>Yours faithfully</p></body>'); lp.pdf(path=HERE+'/tests/out/letter.pdf'); lp.set_viewport_size({'width':800,'height':600}); lp.screenshot(path=HERE+'/tests/out/letter.png'); lp.close()
    import base64; ip=b.new_page(); ip.set_content('<body style="margin:0"><img style="width:100%%" src="data:image/png;base64,%s"></body>'%base64.b64encode(open(HERE+'/tests/out/letter.png','rb').read()).decode()); ip.pdf(path=HERE+'/tests/out/scan.pdf'); ip.close()
    ctx=b.new_context(viewport={'width':390,'height':844})
    ctx.route('https://cdn.jsdelivr.net/**', cdn)
    ctx.route('https://fonts.googleapis.com/**', lambda r: r.fulfill(body='', content_type='text/css'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE+'/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg,200); pg.click('[data-a=anon-start]'); wait(pg)
    # 1 a message finds its case
    compose(pg,"British Gas said the engineer will come on Friday morning"); plan(pg); pg.click('[data-a=sug-yes]'); wait(pg)
    n0=len(tasks(pg))
    compose(pg,"British Gas: Your engineer visit has been moved to "+A4["long"]+" between 12pm and 4pm. Ref BG-55123.")
    m=pg.inner_text('main'); ok('This looks like it’s about your' in m and pg.locator('form[data-f=case] [type=submit]').count()==0,'match offered instead of Start')
    pg.click('[data-a=match-add]'); wait(pg)
    c=pg.locator('.sug').inner_text() if pg.locator('.sug').count() else ''; ok(A4['short'] in c and 'BG-55123' in c,'added: new date proposed in that case')
    pg.click('[data-a=sug-yes]'); wait(pg)
    t=[x for x in tasks(pg) if x['title'].startswith('British Gas')][0]
    ok(len(tasks(pg))==n0 and [q['status'] for q in t['promises']]==['replaced','open'],'no new case; old date replaced')
    ok(any(e['label'].startswith('Added a message') for e in t['events']),'message kept in that case history')
    # 1b start a new case anyway
    compose(pg,"British Gas sent me a bill for £412 that I don't recognise")
    pg.click('[data-a=match-new]'); wait(pg)
    ok(pg.locator('form[data-f=baseline]').count()==1,'start a new case anyway')
    plan(pg); ok(len(tasks(pg))==n0+1,'new case created')
    # 2 who you spoke to
    compose(pg,"Need my broadband fixed, router keeps dropping"); plan(pg)
    if pg.locator('[data-a=sug-no]').count(): pg.click('[data-a=sug-no]'); wait(pg)
    pg.fill('#f-who','Virgin Media'); pg.fill('#f-ask','My broadband keeps dropping. Please send an engineer.'); pg.click('form[data-f=call] button[type=submit]'); wait(pg)
    pg.click('[data-a=panel][data-p=promise]'); wait(pg)
    pg.fill('#f-said','An engineer will come'); pg.click('[data-k=when][data-v=by]'); wait(pg,150)
    import datetime; dd=datetime.date.today()+datetime.timedelta(days=1)
    for part,v in [('d',dd.day),('m',dd.month),('y',dd.year)]: pg.select_option('select[data-dp=f-date][data-part=%s]'%part,str(v))
    pg.fill('#f-spoke','Sarah'); pg.fill('#f-ref','VM-901'); pg.click('form[data-f=promise] button[type=submit]'); wait(pg)
    t=[x for x in tasks(pg) if x.get('call') and x['call']['who']=='Virgin Media'][0]
    ok(t['promises'][-1].get('spoke')=='Sarah' and any('spoke to Sarah' in e['label'] for e in t['events']),'spoke-to name kept and logged')
    pg.evaluate("""()=>{var db=JSON.parse(localStorage.getItem('__mockdb'));var x=db.tasks.map(y=>y.data).find(y=>y.call&&y.call.who==='Virgin Media');var p=x.promises[x.promises.length-1];var d=new Date(Date.now()-2*864e5);p.dueAt=d.toISOString();localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}""")
    pg.goto('https://sorted.test/'); wait(pg,600); pg.locator('.slip', has_text='Virgin').locator('[data-a=open]').first.click(); wait(pg)
    pg.click('[data-a=missed]'); wait(pg); a=pg.input_value('#f-ask'); print('  chase:',a); ok('I was told by Sarah' in a,'chase names who said it')
    # 3 email: open in your email app / copy
    pg.click('[data-k=via][data-v=email]'); wait(pg,150); pg.click('form[data-f=call] button[type=submit]'); wait(pg)
    hr=pg.get_attribute('[data-a=mail-open]','href') or ''; print('  mailto:',hr[:120]); ok(hr.startswith('mailto:?subject=Reference%20VM-901&body='),'email opens with subject and body')
    pg.evaluate("navigator.clipboard&&(navigator.clipboard.writeText=()=>Promise.resolve())")
    pg.evaluate("document.querySelector('[data-a=mail-open]').addEventListener('click',e=>e.preventDefault(),{once:true})"); pg.click('[data-a=mail-open]'); wait(pg)
    pg.click('[data-a=copy-ask]'); wait(pg)
    t=[x for x in tasks(pg) if x.get('call') and x['call']['who']=='Virgin Media'][0]
    ok(any(e['label']=='Opened the message in your email app.' for e in t['events']) and any(e['label']=='Copied the message.' for e in t['events']),'open and copy are logged with their time')
    # 4 PDFs
    for f,label in [('letter.pdf','typed PDF'),('scan.pdf','scanned PDF')]:
        pg.goto('https://sorted.test/'); wait(pg,400)
        if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg,150)
        pg.set_input_files('input[data-ocr=f-case]', HERE+'/tests/out/'+f)
        pg.wait_for_function("(()=>{var t=document.getElementById('ocr-status').textContent;return t.startsWith('Done')||t.startsWith('Sorted couldn')})()", timeout=120000)
        st=pg.inner_text('#ocr-status'); tx=pg.input_value('#f-case'); print('  '+label+':',st[:40],'|',tx[:150].replace('\n',' / '))
        ok(st.startswith('Done') and 'TW-448812' in tx.replace(' ','') and A6['dm'] in tx,label+' read on the phone')
    pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    plan(pg); c=pg.locator('.sug').inner_text() if pg.locator('.sug').count() else ''; print('  card:',c.replace('\n',' | ')[:220])
    ok(A6['short'] in c and '13:00' in c and 'TW-448812' in c,'letter becomes a proposed promise')
    b.close()
print('ERRORS',errs); print('FAILS',fails)
