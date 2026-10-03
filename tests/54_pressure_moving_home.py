# Adversarial pressure test for v99 Moving Home. Focuses on state survival and container isolation,
# not the happy path already covered by 52_moving_home.py.
import os, datetime
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.');fails=[];errs=[]
def ok(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c:fails.append(m)
def wait(pg,ms=350):pg.wait_for_timeout(ms)
def db(pg):
    try:return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')||'{}')") or {}
    except:return {}
def rows(pg):return [x.get('data',{}) for x in db(pg).get('tasks',[])]
def moms(pg):return [x for x in rows(pg) if x.get('kind')=='moment']
def cases(pg):return [x for x in rows(pg) if x.get('kind')!='moment']
def open_moving_guide(pg):
    pg.goto('https://sorted.test/');wait(pg,450)
    x=pg.locator('[data-a=ex-moment][data-v=moving]:visible')
    ok(x.count()>=1,'Moving home discovery control is visible')
    if x.count():x.first.click();wait(pg,350)
def create_move(pg,date,tenure='rent',council='unsure',car='yes',bb='yes'):
    open_moving_guide(pg)
    pg.locator('#moment-moving [data-a=mom-new]:visible').first.click();wait(pg,200)
    pg.locator('#mv-date:visible').fill(date)
    for name,val in [('mv-tenure',tenure),('mv-council',council),('mv-car',car),('mv-bb',bb)]:
        lab=pg.locator('label.chip:visible:has(input[name=%s][value=%s])'%(name,val))
        if lab.count():lab.first.click()
    pg.locator('form[data-f=mom]:visible button[type=submit]:visible').first.click();wait(pg,450)
    return moms(pg)[-1] if moms(pg) else None
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
    ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('https://sorted.test/#start');pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')");pg.reload();wait(pg,300)
    if pg.locator('[data-a=anon-start]:visible').count():pg.locator('[data-a=anon-start]:visible').first.click();wait(pg,500)
    today=datetime.date.today();d1=(today+datetime.timedelta(days=10)).isoformat()
    m1=create_move(pg,d1,'rent','new','yes','yes')
    ok(m1 is not None,'first Moving Home container can be created under pressure')
    mid1=m1['id'] if m1 else ''
    licence=pg.locator('.cap99-item:visible',has_text='driving licence')
    if licence.count():licence.first.locator('[data-a=mom-done]:visible').click();wait(pg,200)
    furniture=pg.locator('.cap99-item:visible',has_text='Furniture or appliance delivery')
    if furniture.count():furniture.first.locator('[data-a=mom-irr]:visible').click();wait(pg,200)
    before=[m for m in moms(pg) if m['id']==mid1][0]
    ok(before.get('items',{}).get('licence',{}).get('st')=='done','Done already is stored on the container')
    ok(before.get('items',{}).get('furniture',{}).get('st')=='irrelevant','Not relevant is stored on the container')
    pg.locator('[data-a=mom-edit]:visible').first.click();wait(pg,150)
    pg.locator('label.chip:visible:has(input[name=mv-car][value=no])').click();pg.locator('form[data-f=mom]:visible button[type=submit]:visible').click();wait(pg,300)
    ok('driving licence' not in pg.inner_text('main'),'car=no removes car-only steps from the visible plan')
    pg.locator('[data-a=mom-edit]:visible').first.click();wait(pg,150)
    pg.locator('label.chip:visible:has(input[name=mv-car][value=yes])').click();pg.locator('form[data-f=mom]:visible button[type=submit]:visible').click();wait(pg,300)
    after=[m for m in moms(pg) if m['id']==mid1][0]
    ok(after.get('items',{}).get('licence',{}).get('st')=='done','Done state survives hiding and restoring a conditional step')
    ok(after.get('items',{}).get('furniture',{}).get('st')=='irrelevant','Not relevant state survives unrelated answer edits')
    for i in range(3):
        pg.locator('[data-a=mom-edit]:visible').first.click();wait(pg,80);pg.locator('form[data-f=mom]:visible button[type=submit]:visible').first.click();wait(pg,180)
    ok(len([m for m in moms(pg) if m['id']==mid1])==1,'repeated edits never duplicate the same Moving Home container')
    d2=(today+datetime.timedelta(days=180)).isoformat();m2=create_move(pg,d2,'buy','same','no','no')
    ok(len(moms(pg))==2,'two separate moves can coexist without overwriting each other')
    mid2=m2['id'] if m2 else ''
    ok(mid1!=mid2 and any(m['date']==d1 for m in moms(pg)) and any(m['date']==d2 for m in moms(pg)),'each move retains its own identity and date')
    pg.goto('https://sorted.test/');wait(pg,400)
    visible_rows=pg.locator('.cap99-row:visible')
    ok(visible_rows.count()==2,'Home shows both life-moment containers')
    ok(pg.evaluate('document.documentElement.scrollWidth<=innerWidth'),'two life moments do not create horizontal overflow')
    firstrow=pg.locator('.cap99-row:visible').filter(has_text='In 10 days')
    ok(firstrow.count()==1,'first move remains distinguishable on Home')
    if firstrow.count():firstrow.first.click();wait(pg,300)
    broadband=pg.locator('.cap99-item:visible',has_text='Move your broadband')
    if broadband.count():
        broadband.first.locator('[data-a=mom-case]:visible').click();wait(pg,220)
        if pg.locator('#gi-who:visible').count():
            pg.locator('#gi-who:visible').fill('Sky');pg.locator('#gi-what:visible').fill('install broadband in 8 days, ref SKY-PRESS-1');pg.locator('form[data-f=gi]:visible button[type=submit]:visible').click();wait(pg,320)
            if pg.locator('form[data-f=baseline]:visible').count():
                ch=pg.locator('form[data-f=baseline]:visible .chip:visible')
                if ch.count():ch.first.click()
                pg.locator('form[data-f=baseline]:visible button[type=submit]:visible').click();wait(pg,250)
            if pg.locator('[data-a=sug-yes]:visible').count():pg.locator('[data-a=sug-yes]:visible').first.click();wait(pg,220)
    linked=[c for c in cases(pg) if c.get('momentId')==mid1]
    ok(len(linked)>=1,'a tracked case created inside first move belongs to first container')
    cid=linked[0]['id'] if linked else ''
    ok(not any(c.get('id')==cid and c.get('momentId')==mid2 for c in cases(pg)),'one case cannot silently belong to two moves at once')
    pg.goto('https://sorted.test/');wait(pg,300)
    secondrow=pg.locator('.cap99-row:visible').filter(has_text='In 180 days')
    ok(secondrow.count()==1,'second move remains distinguishable on Home')
    if secondrow.count():secondrow.first.click();wait(pg,250)
    if pg.locator('[data-a=mom-panel][data-p=link]:visible').count():
        pg.locator('[data-a=mom-panel][data-p=link]:visible').click();wait(pg,180)
        cand=pg.locator('[data-a=mom-link][data-id="%s"]:visible'%cid) if cid else pg.locator('x-never')
        if cand.count():
            cand.click();wait(pg,250)
            c=[x for x in cases(pg) if x.get('id')==cid][0]
            ok(c.get('momentId') in (mid1,mid2),'re-linking leaves exactly one authoritative momentId')
            pg.goto('https://sorted.test/');wait(pg,250)
            counts=0
            rows_now=pg.locator('.cap99-row:visible').count()
            for i in range(rows_now):
                pg.locator('.cap99-row:visible').nth(i).click();wait(pg,120)
                if cid and pg.locator('[data-a=open][data-id="%s"]:visible'%cid).count():counts+=1
                pg.goto('https://sorted.test/');wait(pg,120)
            ok(counts==1,'re-linked case renders in one life moment, never both')
        else:ok(True,'already-linked case is excluded from second move link candidates')
    pg.goto('https://sorted.test/');wait(pg,250)
    first=pg.locator('.cap99-row:visible').filter(has_text='In 10 days')
    if first.count():
        first.first.click();wait(pg,200);ncase=len(cases(pg));pg.locator('[data-a=mom-del]:visible').first.click();wait(pg,100);pg.locator('[data-a=mom-del]:visible').first.click();wait(pg,300)
        ok(len(moms(pg))==1 and moms(pg)[0]['id']==mid2,'deleting first move leaves second move intact');ok(len(cases(pg))==ncase,'deleting a move never deletes normal cases')
    past=(today-datetime.timedelta(days=30)).isoformat();before_n=len(moms(pg))
    open_moving_guide(pg);pg.locator('#moment-moving [data-a=mom-new]:visible').first.click();wait(pg,150);pg.locator('#mv-date:visible').fill(past);pg.locator('form[data-f=mom]:visible button[type=submit]:visible').click();wait(pg,300)
    if len(moms(pg))>before_n:
        txt=pg.inner_text('main');ok('Moved 30 days ago' in txt or 'Moved' in txt,'accepted past move date is described coherently');ok('NaN' not in txt and 'Invalid' not in txt,'past move never leaks invalid date text')
    else:ok(pg.locator('#mv-date:visible').count()==1,'past date is blocked without losing the form')
    ok(pg.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Moving Home pressure sequence remains within mobile width')
    ok(not errs,'no page errors during Moving Home pressure sequence: %s'%errs)
    ctx.close();b.close()
print('ERRORS',errs);print('FAILS',fails)
