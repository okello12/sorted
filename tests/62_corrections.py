# v106 / SEM-03: corrections are proposed, confirmed, versioned and reflected in every current view.
import os, datetime
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c:fails.append(m)
def wait(pg,ms=420):pg.wait_for_timeout(ms)
def db(pg):return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')||'{}')") or {}
def cases(pg):return [x.get('data',{}) for x in db(pg).get('tasks',[]) if x.get('data',{}).get('kind')!='moment']
def one(pg):
    xs=cases(pg);return xs[0] if xs else None
def open_case(pg,cid):
    pg.goto('https://sorted.test/');wait(pg,650);x=pg.locator('[data-a=open][data-id="%s"]:visible'%cid)
    if x.count():x.first.click();wait(pg,500)
def paste(pg,text):
    p=pg.locator('[data-a=panel][data-p=paste]:visible')
    if not p.count():
        d=pg.locator('details.case56-tools summary:visible')
        if d.count():d.first.click();wait(pg,150);p=pg.locator('[data-a=panel][data-p=paste]:visible')
    ok(p.count()>0,'paste/message tool is available')
    if not p.count():return
    p.first.click();wait(pg,180);pg.fill('#f-paste',text);pg.locator('form[data-f=paste] button[type=submit]:visible').first.click();wait(pg,550)
def confirm_general(pg):
    ok(pg.locator('.sem-correction:visible').count()==1,'a correction is proposed before changing the case')
    if pg.locator('[data-a=sem-yes]:visible').count():pg.locator('[data-a=sem-yes]:visible').first.click();wait(pg,450);return True
    return False
def current_promise(t):
    for p in reversed(t.get('promises',[])):
        if p.get('status')=='open':return p
    return None
now=datetime.date.today(); d1=now+datetime.timedelta(days=8); d2=now+datetime.timedelta(days=9); d3=now+datetime.timedelta(days=10)
D1=d1.strftime('%-d %B %Y'); D2=d2.strftime('%-d %B %Y'); D3=d3.strftime('%-d %B %Y')
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London',color_scheme='light')
    ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
    ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('https://sorted.test/#start');pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1');localStorage.setItem('__replyOn','1')");pg.reload();wait(pg,300)
    if pg.locator('[data-a=anon-start]:visible').count():pg.locator('[data-a=anon-start]:visible').first.click();wait(pg,600)
    # Start with a real promise containing party, amount, ref and date.
    text='Currys said my £80 refund would arrive on %s. Ref C123'%D1
    if not pg.locator('#f-case:visible').count():
        other=pg.locator('#cap82-start [data-cap82=other]:visible')
        if other.count():other.first.click();wait(pg,250)
    pg.fill('#f-case',text);pg.locator('form[data-f=case] button[type=submit]:visible').first.click();wait(pg,400)
    if pg.locator('[data-a=match-new]:visible').count():pg.locator('[data-a=match-new]:visible').first.click();wait(pg,180)
    if pg.locator('[data-a=vague-go]:visible').count():pg.locator('[data-a=vague-go]:visible').first.click();wait(pg,180)
    if pg.locator('form[data-f=baseline]:visible').count():
        ch=pg.locator('form[data-f=baseline]:visible .chip:visible')
        if ch.count():ch.first.click()
        pg.locator('form[data-f=baseline]:visible button[type=submit]:visible').first.click();wait(pg,500)
    if pg.locator('[data-a=sug-yes]:visible').count():pg.locator('[data-a=sug-yes]:visible').first.click();wait(pg,500)
    t=one(pg);ok(t is not None,'base promise case exists')
    cid=t['id']; led=t.get('factLedger',{})
    ok(bool(led) and led.get('v')==1,'opening a case lazily creates the v1 fact ledger')
    f=led.get('f',{})
    ok(f.get('who',{}).get('value')=='Currys' and f.get('reference',{}).get('value')=='C123','party and reference are seeded as current facts')
    ok(f.get('amount',{}).get('value')=='£80' and f.get('promise_date',{}).get('value'),'amount and promise date are seeded')
    ok(all(f[k].get('source') and f[k].get('time') and f[k].get('status')=='confirmed' for k in f),'seeded facts carry source, time and confirmed status')
    # Who: "it wasn't X, it was Y".
    paste(pg,"Sorry, it wasn't Currys, it was Argos.")
    ok('Change Currys to Argos?' in pg.inner_text('.sem-correction') if pg.locator('.sem-correction').count() else False,'who correction names old and new values')
    confirm_general(pg);t=one(pg);p0=current_promise(t)
    ok(p0 and p0.get('party')=='Argos','confirmed who correction updates the live promise')
    wh=t['factLedger']['f']['who'];ok(wh['value']=='Argos' and any(x['value']=='Currys' and x['status']=='replaced' for x in wh['history']),'old who becomes replaced history')
    ok('Argos' in t.get('title','') and 'Currys' not in t.get('title',''),'the current case title uses the replacement')
    # Reference.
    paste(pg,'Actually, the reference is A999.')
    confirm_general(pg);t=one(pg);p0=current_promise(t)
    ok(p0 and p0.get('ref')=='A999','reference correction updates the live promise')
    rf=t['factLedger']['f']['reference'];ok(rf['value']=='A999' and any(x['value']=='C123' and x['status']=='replaced' for x in rf['history']),'old reference is retained only as replaced history')
    # Amount.
    paste(pg,'I meant £89, not £80.')
    confirm_general(pg);t=one(pg);p0=current_promise(t)
    ok(t['factLedger']['f']['amount']['value']=='£89','amount correction becomes current')
    ok('£89' in (p0.get('said') or '') and '£80' not in (p0.get('said') or ''),'current promise wording uses the corrected amount')
    # Reject a proposed correction: current value must stay authoritative and proposal is recorded rejected.
    paste(pg,'Actually, the reference is B777.')
    ok(pg.locator('[data-a=sem-no]:visible').count()==1,'a proposed correction can be rejected')
    if pg.locator('[data-a=sem-no]:visible').count():pg.locator('[data-a=sem-no]:visible').first.click();wait(pg,400)
    t=one(pg);ok(t['factLedger']['f']['reference']['value']=='A999','rejecting leaves the current reference unchanged')
    ok(any(x.get('to')=='B777' and x.get('status')=='rejected' for x in t['factLedger'].get('rejected',[])),'rejected proposal is retained with rejected status')
    # Date: wrong date vs company reschedule are deliberately different.
    old=current_promise(t);oldid=old['id'];old_due=old['dueAt']
    paste(pg,'Sorry, I meant %s.'%D2)
    # A correction sentence may also surface a "what they said" proposal first. Reject unrelated proposals until the date card is current.
    for _ in range(4):
        if pg.locator('[data-a=sem-date-correct]:visible').count():break
        if pg.locator('[data-a=sem-no]:visible').count():pg.locator('[data-a=sem-no]:visible').first.click();wait(pg,250)
    ok(pg.locator('[data-a=sem-date-correct]:visible').count()==1 and pg.locator('[data-a=sem-date-moved]:visible').count()==1,'date correction asks whether they changed it or you meant it all along')
    if pg.locator('[data-a=sem-date-correct]:visible').count():pg.locator('[data-a=sem-date-correct]:visible').first.click();wait(pg,450)
    t=one(pg);cur=current_promise(t)
    ok(cur and cur['id']==oldid and cur['status']=='open' and cur['dueAt']!=old_due,'"I meant it all along" corrects the existing promise instead of creating a missed/rescheduled outcome')
    ok(not any(x.get('status')=='missed' for x in t['promises']),'a correction never counts as a missed promise')
    # Then the company genuinely moves the corrected date.
    paste(pg,'Actually, they moved it to %s.'%D3)
    for _ in range(4):
        if pg.locator('[data-a=sem-date-moved]:visible').count():break
        if pg.locator('[data-a=sem-no]:visible').count():pg.locator('[data-a=sem-no]:visible').first.click();wait(pg,250)
    ok(pg.locator('[data-a=sem-date-moved]:visible').count()==1,'a later date change reaches the reschedule choice')
    if pg.locator('[data-a=sem-date-moved]:visible').count():pg.locator('[data-a=sem-date-moved]:visible').first.click();wait(pg,450)
    t=one(pg);cur=current_promise(t);repl=[x for x in t['promises'] if x.get('status')=='replaced' and x.get('changeKind')=='reschedule']
    ok(cur and cur['status']=='open' and repl,'company move creates a new open promise and marks the previous one as a reschedule')
    ok(not any(x.get('status')=='missed' for x in t['promises']),'a reschedule is distinct from a missed promise')
    # Current surfaces: promise card and helper share must use the replacements, not stale values.
    ptxt=pg.inner_text('.promise') if pg.locator('.promise').count() else pg.inner_text('main')
    ok('Argos' in ptxt and 'A999' in ptxt and '£89' in ptxt,'current promise card uses corrected who, reference and amount')
    det=pg.locator('details.case56-sharing summary:visible')
    if det.count():det.first.click();wait(pg,120)
    sh=pg.locator('[data-a=share]:visible')
    if sh.count():sh.first.click();wait(pg,600)
    shares=db(pg).get('shares',[]);card=shares[0].get('card',{}) if shares else {};raw=str(card)
    ok('Argos' in raw and 'A999' in raw and '£89' in raw and 'Currys' not in raw and 'C123' not in raw and '£80' not in raw,'helper share contains only current replacements')
    # Email reply path: correction language in a kept reply must produce the same proposal.
    pg.evaluate("cid=>{var d=JSON.parse(localStorage.getItem('__mockdb'));d.inbound_items=d.inbound_items||[];d.inbound_items.push({id:'sem-mail',user_id:'x',task_id:cid,from_domain:'argos.co.uk',subject:'Correction',body:'Sorry, actually the reference is MAIL-55.',received_at:new Date().toISOString(),used_at:null});localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}",cid)
    open_case(pg,cid)
    if pg.locator('[data-a=cm-add]:visible').count():pg.locator('[data-a=cm-add]:visible').first.click();wait(pg,450)
    ok(pg.locator('.sem-correction:visible').count()==1,'a kept email reply can propose a correction')
    if pg.locator('[data-a=sem-yes]:visible').count():pg.locator('[data-a=sem-yes]:visible').first.click();wait(pg,400)
    ok(one(pg)['factLedger']['f']['reference']['value']=='MAIL-55','email-reply correction updates the same fact ledger')
    # History is explicit and current values do not masquerade as the replaced ones.
    ev=[x.get('label','') for x in one(pg).get('events',[])]
    ok(any('Changed from Currys to Argos. You corrected it on' in x for x in ev),'case history records the correction and date')
    ok(not errs,'no page errors during correction sequence: %s'%errs)
    print('ERRORS',errs);print('FAILS',fails)
    ctx.close();b.close()
    if fails:raise SystemExit(1)
