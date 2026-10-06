# v141: saving and syncing, from the sync audit. Two devices merge field by field against the last copy both agreed on
# (references, notice details, a date corrected in place, Moving home steps), a removed message never comes back, a case
# deleted mid-save stays deleted, a guest's cases and moves carry to an email account (or back to a new guest) and the
# carried copy lasts a day, a failed save is tried again while online, two tabs keep each other's unsent edits, nothing
# but an unsent edit stays on the phone when the session ends, kept documents are stored under a plain key with their
# name kept on the case, error reports never carry quoted words or storage paths, download names keep their extension,
# half-written words go with their case, and signing out stops this phone's lock-screen reminders for that account.
import os, sys, json, re, datetime, zipfile, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); OUT = HERE + '/tests/out'; errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
today = datetime.date.today()
fri = today + datetime.timedelta(days=(4 - today.weekday()) % 7 or 7)
SESSION = lambda uid, em: json.dumps({'user': {'id': uid, 'email': em}})
STUB = open(HERE + '/tests/89_push.py').read().split('STUB = """', 1)[1].split('"""', 1)[0]
os.makedirs(OUT, exist_ok=True)
open(OUT + '/Résumé – Zoë’s 包裹.pdf', 'wb').write(b'%PDF-1.4\n% a letter\n' + b'0' * 2000)
with sync_playwright() as p:
    b = p.chromium.launch()
    def new_ctx(init=None):
        c = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844}, accept_downloads=True)
        if init: c.add_init_script(init)
        c.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
        c.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
        return c
    ctx = new_ctx()
    def page(c=None):
        x = (c or ctx).new_page(); x.on('pageerror', lambda e: errs.append(str(e))); return x
    pg = page()
    dbj = lambda q=None: (q or pg).evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    def cases(q=None): return sorted([x['data'] for x in dbj(q).get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    def srv(cid, q=None):
        r = [x['data'] for x in dbj(q).get('tasks', []) if x['id'] == cid]; return r[0] if r else None
    def stored(q=None):
        return (q or pg).evaluate("(()=>{var o={};[localStorage,sessionStorage].forEach(function(st,i){for(var j=0;j<st.length;j++){var k=st.key(j);if(/^__/.test(k))continue;o[(i?'s:':'l:')+k]=st.getItem(k)}});return o})()")
    def sign_in(q=None, uid='u-me', em='me@example.com'):
        q = q or pg; q.evaluate("localStorage.setItem('__mocksession', %s)" % json.dumps(SESSION(uid, em))); q.goto('https://sorted.test/'); wait(q, 700)
    def fresh(q=None):
        q = q or pg; q.goto('https://sorted.test/'); q.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); sign_in(q)
    def guest(q=None):
        q = q or pg; q.goto('https://sorted.test/#start'); wait(q, 400); q.click('[data-a=anon-start]'); wait(q, 800)
        return q.evaluate("JSON.parse(localStorage.getItem('__mocksession')).user.id")
    def make_case(text, q=None):
        q = q or pg; q.goto('https://sorted.test/'); wait(q, 500)
        if not q.locator('[data-cap82=other]').count() and q.locator('[data-a=new-case]').count(): q.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(q)
        q.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(q)
        q.fill('#f-case', text); q.locator('form[data-f=case] button[type=submit]').last.click(); wait(q, 600)
        if q.locator('[data-a=match-new]').count(): q.click('[data-a=match-new]'); wait(q)
        if q.locator('form[data-f=baseline]').count(): q.click('form[data-f=baseline] .chip >> nth=0'); q.click('form[data-f=baseline] button[type=submit]'); wait(q, 500)
        if q.locator('[data-a=plan-skip]').count(): q.locator('[data-a=plan-skip]').first.evaluate('e=>e.click()'); wait(q, 500)
        if q.locator('[data-a=sug-yes]').count(): q.click('[data-a=sug-yes]'); wait(q, 600)
        if q.locator('text=Not now').count(): q.locator('text=Not now').first.click(); wait(q, 300)
        if q.locator('[data-a=fr-ok]').count(): q.click('[data-a=fr-ok]'); wait(q, 300)
        return cases(q)[-1]['id']
    def open_case(cid, q=None):
        q = q or pg; q.goto('https://sorted.test/?task=%s' % cid); wait(q, 700); q.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
    def other(cid, js, q=None):
        # another device saves the case: change it in the "server" and move its revision on
        (q or pg).evaluate("""([id,f])=>{var d=JSON.parse(localStorage.getItem('__mockdb'));var r=d.tasks.find(x=>x.id===id);(new Function('c',f))(r.data);r.data.rev=(r.data.rev||0)+1;localStorage.setItem('__mockdb',JSON.stringify(d))}""", [cid, js])
    def rename(cid, name, q=None):
        q = q or pg; open_case(cid, q); q.click('[data-a=panel][data-p=rename]'); wait(q, 250); q.fill('#f-rename', name); q.click('form[data-f=rename] button[type=submit]'); wait(q, 700)
    def paste(cid, text, q=None):
        q = q or pg; open_case(cid, q); q.locator('[data-a=panel][data-p=paste]').first.evaluate('e=>e.click()'); wait(q, 300); q.fill('#f-paste', text); q.click('form[data-f=paste] button[type=submit]'); wait(q, 800)
    merged = lambda c: [e['label'] for e in c['events'] if e['label'].startswith('Merged with changes saved from another device')]

    # ---- 1. merging field by field ----
    fresh()
    cid = make_case('Currys said they would refund £89 by %s, order 445566' % fri.strftime('%A'))
    open_case(cid)
    other(cid, "c.events.push({at:new Date().toISOString(),label:'Other device note.'});c.refs=(c.refs||[]).concat([{k:'policy',v:'POL999',at:new Date().toISOString(),src:'you',st:'confirmed'}])")
    pg.click('[data-a=panel][data-p=refadd]'); wait(pg, 300); pg.fill('#f-refv', 'CLM7788'); pg.select_option('#f-refk', 'claim'); pg.click('form[data-f=refadd] button[type=submit]'); wait(pg, 1200)
    c = srv(cid); vs = [r['v'] for r in c.get('refs') or []]
    ok('CLM7788' in vs and 'POL999' in vs and '445566' in vs and any(e['label'] == 'Other device note.' for e in c['events']) and merged(c), 'a reference added here and one added on another device are both kept, with the other device’s message and a merge line (%s)' % vs)
    pg.reload(); wait(pg, 700); open_case(cid); m = pg.inner_text('main')
    ok('CLM7788' in m and 'POL999' in m, 'after a reload the case shows both references')
    # a date corrected in place on an open promise (same promise) survives a save from another device
    p0 = [q for q in srv(cid)['promises'] if q['status'] == 'open'][0]
    open_case(cid)
    other(cid, "c.events.push({at:new Date().toISOString(),label:'Other device note 2.'})")
    wed = fri - datetime.timedelta(days=2)
    if wed <= today: wed = fri + datetime.timedelta(days=5)
    pg.locator('[data-a=panel][data-p=paste]').first.evaluate('e=>e.click()'); wait(pg, 300); pg.fill('#f-paste', 'Sorry, I meant %s' % wed.strftime('%A')); pg.click('form[data-f=paste] button[type=submit]'); wait(pg, 800)
    if pg.locator('[data-a=corr-yes]').count(): pg.click('[data-a=corr-yes]'); wait(pg, 1200)
    c = srv(cid); p1 = [q for q in c['promises'] if q['status'] == 'open'][0]
    ok(p1['id'] == p0['id'] and p1['dueAt'] != p0['dueAt'] and any(e['label'] == 'Other device note 2.' for e in c['events']) and (c.get('corr') or []), 'a date corrected in place on the open promise is kept when another device saved meanwhile (%s → %s)' % (p0['dueAt'][:10], p1['dueAt'][:10]))
    # only this device renamed: this device's title wins
    open_case(cid); other(cid, "c.events.push({at:new Date().toISOString(),label:'Other device note 3.'})")
    pg.click('[data-a=panel][data-p=rename]'); wait(pg, 250); pg.fill('#f-rename', 'Currys kettle refund'); pg.click('form[data-f=rename] button[type=submit]'); wait(pg, 1000)
    ok(srv(cid)['title'] == 'Currys kettle refund', 'a field only this device changed keeps this device’s value')
    # both renamed: the other device's title is kept and the history says so
    open_case(cid); other(cid, "c.title='Other device title'")
    pg.click('[data-a=panel][data-p=rename]'); wait(pg, 250); pg.fill('#f-rename', 'This device title'); pg.click('form[data-f=rename] button[type=submit]'); wait(pg, 1000)
    c = srv(cid)
    ok(c['title'] == 'Other device title' and any('the other device’s title was kept' in x for x in merged(c)), 'where both changed the title, the other device’s is kept and the history says so')
    # notice details (cf.f) merge by key
    open_case(cid)
    other(cid, "c.cf=c.cf||{f:{}};c.cf.f=c.cf.f||{};c.cf.f.issuer={v:'Lambeth',st:'confirmed',at:new Date().toISOString(),how:'you',src:'test'}")
    pg.click('[data-a=panel][data-p=rename]'); wait(pg, 250); pg.fill('#f-rename', 'Currys kettle refund again'); pg.click('form[data-f=rename] button[type=submit]'); wait(pg, 1000)
    c = srv(cid)
    ok(((c.get('cf') or {}).get('f') or {}).get('issuer', {}).get('v') == 'Lambeth' and c['title'] == 'Currys kettle refund again', 'details the other device added are kept beside this device’s change')

    # ---- 2. a removed message never comes back ----
    cid2 = make_case('Argos said they would refund £30 by %s, order 778899' % fri.strftime('%A'))
    paste(cid2, 'Hi, my private phone is 07700 900123, my neighbour Jo has the key. Thanks')
    ok('07700' in json.dumps(srv(cid2)), 'the message is saved')
    pg2 = page(); pg2.goto('https://sorted.test/?task=%s' % cid2); wait(pg2, 900)
    open_case(cid2); pg.locator('[data-a=ev-del]').first.click(); wait(pg, 900)
    ok('07700' not in json.dumps(srv(cid2)), 'removing it takes it off the server')
    pg2.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
    pg2.click('[data-a=panel][data-p=rename]'); wait(pg2, 250); pg2.fill('#f-rename', 'Argos refund B'); pg2.click('form[data-f=rename] button[type=submit]'); wait(pg2, 1200)
    c = srv(cid2)
    ok('07700' not in json.dumps(c) and c['title'] == 'Argos refund B' and merged(c), 'a save from a device that still had it merges without bringing it back, and keeps no words of it')
    pg2.close()
    open_case(cid2); pg.locator('[data-a=panel][data-p=paste]').first.evaluate('e=>e.click()'); wait(pg, 300); pg.fill('#f-paste', 'Second message, kept: order 778899 delivered'); pg.click('form[data-f=paste] button[type=submit]'); wait(pg, 800)
    open_case(cid2); pg.locator('[data-a=ev-del]').first.click(); wait(pg, 500)
    if pg.locator('[data-a=ev-undo]').count(): pg.click('[data-a=ev-undo]'); wait(pg, 800)
    ok('Second message, kept' in json.dumps(srv(cid2)) and len(srv(cid2).get('evDel') or []) == 1, 'Undo puts the message back and forgets its removal')

    # ---- 3. a case deleted while its first save is on the way stays deleted ----
    pg.evaluate("localStorage.setItem('__slowWrites','2500')")
    pg.goto('https://sorted.test/'); wait(pg, 500)
    if pg.locator('[data-a=new-case]').count() and not pg.locator('[data-cap82=other]').count(): pg.locator('[data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg)
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg)
    pg.fill('#f-case', 'Boots said they would refund £12 by %s, order 99887' % fri.strftime('%A')); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 400)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 200)
    for a in ('plan-skip', 'sug-yes', 'fr-ok'):
        if pg.locator('[data-a=%s]' % a).count(): pg.locator('[data-a=%s]' % a).first.evaluate('e=>e.click()'); wait(pg, 250)
    pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
    pg.locator('[data-a=panel][data-p=delcase]').first.evaluate('e=>e.click()'); wait(pg, 200); pg.locator('[data-a=case-del]').first.evaluate('e=>e.click()'); wait(pg, 300)
    wait(pg, 6500)
    ok(not [x for x in cases() if 'Boots' in (x.get('title') or '')], 'after the save lands, the deleted case is not on the server')
    pg.evaluate("localStorage.removeItem('__slowWrites')"); pg.reload(); wait(pg, 900)
    ok('Boots' not in pg.inner_text('main') and 'Boots' not in json.dumps(stored()), 'nor on Home or anywhere on this phone after a reload')

    # ---- 4. half-written words go with their case ----
    cid3 = make_case('Halfords said they would call back by %s' % fri.strftime('%A'))
    open_case(cid3); pg.locator('[data-a=panel][data-p=paste]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.fill('#f-paste', 'Private: my bank said the chargeback failed, call Sam on 07700900111')
    pg.evaluate("document.querySelector('#f-paste').dispatchEvent(new Event('input',{bubbles:true}))"); wait(pg, 200)
    pg.locator('.tab129 [data-a=go-home]').click(); wait(pg, 500)
    ok([k for k, v in stored().items() if '07700900111' in v], 'words typed into a form are kept when leaving it')
    open_case(cid3); pg.locator('[data-a=panel][data-p=delcase]').first.evaluate('e=>e.click()'); wait(pg, 200); pg.locator('[data-a=case-del]').first.evaluate('e=>e.click()'); wait(pg, 600)
    ok(not [k for k, v in stored().items() if '07700900111' in v], 'deleting the case removes them')
    # deleted on another device: the same
    cid4 = make_case('Dyson said they would send a part by %s' % fri.strftime('%A'))
    open_case(cid4); pg.locator('[data-a=panel][data-p=paste]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.fill('#f-paste', 'Note to self 07700900222'); pg.evaluate("document.querySelector('#f-paste').dispatchEvent(new Event('input',{bubbles:true}))"); wait(pg, 200)
    pg.locator('.tab129 [data-a=go-home]').click(); wait(pg, 500)
    pg.evaluate("(id)=>{var d=JSON.parse(localStorage.getItem('__mockdb'));d.tasks=d.tasks.filter(x=>x.id!==id);localStorage.setItem('__mockdb',JSON.stringify(d))}", cid4)
    pg.locator('.tab129 [data-a=cases]').click(); wait(pg, 400)
    pg.locator('[data-a=open][data-id="%s"]' % cid4).first.evaluate('e=>e.click()'); wait(pg, 500)
    pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
    pg.click('[data-a=panel][data-p=rename]'); wait(pg, 250); pg.fill('#f-rename', 'Dyson part'); pg.click('form[data-f=rename] button[type=submit]'); wait(pg, 1000)
    ok(not [k for k, v in stored().items() if '07700900222' in v], 'a case deleted on another device takes its half-written words with it')

    # ---- 5. a failed save is tried again ----
    cid5 = make_case('Ikea said they would deliver the wardrobe by %s, order 5544' % fri.strftime('%A'))
    pg.evaluate("localStorage.setItem('__failWrites','2')")
    rename(cid5, 'Refused once')
    sync = pg.locator('main [data-sync="%s"]' % cid5).first.inner_text() if pg.locator('main [data-sync="%s"]' % cid5).count() else ''
    ok(sync == 'Saved on this phone, not yet sent.' and pg.evaluate("!document.getElementById('netbar')||document.getElementById('netbar').hidden"), 'a save the server refused while online says “not yet sent”, not “when you’re back online” (%r)' % sync)
    pg.evaluate("localStorage.removeItem('__failWrites')"); wait(pg, 6500)
    ok(srv(cid5)['title'] == 'Refused once', 'it is tried again by itself after a few seconds')
    pg.evaluate("localStorage.setItem('__failWrites','1')")
    rename(cid5, 'Lost connection'); wait(pg, 6000)
    pg.evaluate("localStorage.removeItem('__failWrites')")
    pg.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); wait(pg, 1200)
    ok(srv(cid5)['title'] == 'Lost connection', 'coming back to the page sends it at once')
    pg.evaluate("localStorage.setItem('__failWrites','1')"); rename(cid5, 'Back online')
    pg.evaluate("localStorage.removeItem('__failWrites')"); pg.evaluate("window.dispatchEvent(new Event('online'))"); wait(pg, 1000)
    ok(srv(cid5)['title'] == 'Back online' and pg.evaluate("!document.getElementById('netbar')||document.getElementById('netbar').hidden"), 'back online it sends and the offline bar goes')

    # ---- 6. two tabs keep each other's unsent edits ----
    x = make_case('Very said they would refund £40 by %s, order 1212' % fri.strftime('%A'))
    y = make_case('My washing machine won’t drain')
    pt = page(); pt.goto('https://sorted.test/'); wait(pt, 800)
    pg.evaluate("localStorage.setItem('__failWrites','1')")
    rename(x, 'Tab A rename of X')
    pt.evaluate("location.hash='#case-%s'" % y); wait(pt, 600)
    if not pt.locator('[data-a=panel][data-p=rename]').count(): pt.locator('[data-a=open][data-id="%s"]' % y).first.evaluate('e=>e.click()'); wait(pt, 500)
    pt.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
    pt.click('[data-a=panel][data-p=rename]'); wait(pt, 250); pt.fill('#f-rename', 'Tab B rename of Y'); pt.click('form[data-f=rename] button[type=submit]'); wait(pt, 500)
    ok('Tab A rename' in (pg.evaluate("localStorage.getItem('sorted.cache.u-me')") or ''), 'another tab saving its own case keeps this tab’s unsent edit in the copy on this phone')
    pg.close(); pg = page()
    pt.evaluate("localStorage.removeItem('__failWrites')"); pt.reload(); wait(pt, 1500)
    ok(srv(x, pt)['title'] == 'Tab A rename of X' and srv(y, pt)['title'] == 'Tab B rename of Y', 'once a tab loads again, both edits reach the account')
    pt.close()

    # ---- 7. when the session ends without Sign out, only an unsent edit stays, for a week ----
    pg.goto('https://sorted.test/'); wait(pg, 700)
    pg.evaluate("localStorage.setItem('__failWrites','1')"); rename(x, 'Unsent when the session ended')
    pg.evaluate("localStorage.removeItem('__mocksession')"); pg.reload(); wait(pg, 900)
    st = stored(); cache = json.loads(st.get('l:sorted.cache.u-me') or '[]')
    ok('Currys' not in json.dumps(st) and len(cache) == 1 and cache[0]['title'] == 'Unsent when the session ended' and cache[0].get('_orphanAt'), 'signed out by the server: the copy of the cases is gone except the unsent edit')
    pg.evaluate("localStorage.removeItem('__failWrites')"); sign_in(); wait(pg, 600)
    ok(srv(x)['title'] == 'Unsent when the session ended', 'signing in again sends that edit')
    pg.evaluate("localStorage.setItem('__failWrites','1')"); rename(x, 'Old unsent edit')
    pg.evaluate("localStorage.removeItem('__mocksession')"); pg.reload(); wait(pg, 700)
    pg.evaluate("(()=>{var v=JSON.parse(localStorage.getItem('sorted.cache.u-me'));v.forEach(x=>x._orphanAt=Date.now()-8*86400000);localStorage.setItem('sorted.cache.u-me',JSON.stringify(v))})()")
    pg.reload(); wait(pg, 700)
    ok(pg.evaluate("localStorage.getItem('sorted.cache.u-me')") is None, 'after a week it is removed too')
    pg.evaluate("localStorage.removeItem('__failWrites')")

    # ---- 8. kept documents: a plain key in storage, the name on the case; reports carry no words or paths ----
    sign_in(); cid6 = make_case('Lambeth council sent a parking fine, I need to challenge it')
    open_case(cid6)
    pg.set_input_files('input[data-keepdoc="%s"]' % cid6, OUT + '/Résumé – Zoë’s 包裹.pdf'); wait(pg, 1000)
    sto = json.loads(pg.evaluate("localStorage.getItem('__storage')") or '[]')
    key = sto[-1]['name'] if sto else ''
    ok(re.match(r"^[\w/!\-.*'() &$@=;:+,?]+$", key) and key.startswith('u-me/%s/' % cid6) and key.endswith('.pdf'), 'the file is stored under a key Supabase accepts (%s)' % key)
    c = srv(cid6); nm = 'Résumé – Zoë’s 包裹.pdf'
    ok((c.get('docNames') or {}).get(key.split('/')[-1]) == nm and any(e['label'] == 'Kept a document with this case: %s.' % nm for e in c['events']), 'its own name is kept with the case and in the history')
    open_case(cid6); ok(nm in pg.inner_text('.docs135'), 'the case lists it by its own name')
    pg.locator('.docs135 [data-a=doc-del]').first.click(); wait(pg, 300); pg.locator('[data-a=doc-del-yes]').first.click(); wait(pg, 800)
    c = srv(cid6); ok(not (c.get('docNames') or {}) and any(e['label'] == 'Removed a kept document: %s.' % nm for e in c['events']), 'removing it says its name and drops it from the case')
    pg.evaluate("localStorage.setItem('__storageFail','1');localStorage.removeItem('__errs')")
    open_case(cid6); pg.set_input_files('input[data-keepdoc="%s"]' % cid6, OUT + '/Résumé – Zoë’s 包裹.pdf'); wait(pg, 800)
    er = json.loads(pg.evaluate("localStorage.getItem('__errs')") or '[]')
    ok(er and er[-1]['p_kind'] == 'document_keep' and 'Zo' not in json.dumps(er) and 'row-level' not in json.dumps(er) and cid6 not in json.dumps(er), 'a failed keep is reported without the storage message, the path or the name (%s)' % er)
    pg.evaluate("localStorage.removeItem('__storageFail');localStorage.removeItem('__errs')")
    pg.evaluate("window.dispatchEvent(new ErrorEvent('error',{message:\"Can't read 'Currys secret words' of x\",error:new TypeError('x')}))"); wait(pg, 300)
    er = json.loads(pg.evaluate("localStorage.getItem('__errs')") or '[]')
    ok(er and 'secret' not in er[-1]['p_detail'] and er[-1]['p_detail'].startswith('Can…'), 'an apostrophe in an error never lets quoted words through (%r)' % (er[-1]['p_detail'] if er else None))

    # ---- 9. download names keep their extension and never end in a dot or a space ----
    base = srv(cid6)
    pg.evaluate("""([base])=>{var d=JSON.parse(localStorage.getItem('__mockdb'));var st=[];
      ['..','Refund.','x'.repeat(68)+'🙂🙂 tail'].forEach((t,i)=>{var c=JSON.parse(JSON.stringify(base));c.id='zz'+i+'case';c.title=t;c.rev=1;c.docNames={};c.created=new Date(Date.now()+i*1000).toISOString();d.tasks.push({id:c.id,data:c});
        ['photo.jpg','a'.repeat(90)+'🙂.png'].forEach((n,j)=>st.push({bucket:'originals',name:'u-me/'+c.id+'/'+(1000+j)+'-'+n,size:20,type:'image/jpeg',at:new Date().toISOString()}))});
      localStorage.setItem('__mockdb',JSON.stringify(d));localStorage.setItem('__storage',JSON.stringify(st))}""", [base])
    pg.reload(); wait(pg, 1000)
    pg.locator('.tab129 [data-a=data]').click(); wait(pg, 500)
    if not pg.locator('[data-a=export-file]').count(): pg.locator('[data-a=acct-jump]').nth(1).click(); wait(pg, 400)
    with pg.expect_download(timeout=60000) as dl: pg.click('[data-a=export-file]')
    path = OUT + '/sync99.zip'; dl.value.save_as(path)
    names = zipfile.ZipFile(path).namelist(); parts = [q for nm2 in names for q in nm2.split('/')]
    longs = [q for q in parts if q.startswith('aaaa')]
    ok(not [q for q in parts if q != q.rstrip('. ') or q.startswith('.')] and longs and all(q.endswith('.png') and len(q) <= 70 for q in longs) and any(q.endswith('🙂🙂') or len(q) <= 70 for q in parts), 'no folder or file name ends in a dot or space, long names keep their extension within 70 characters (%s)' % [q for q in parts if q.startswith('0')][:6])
    ok('No errors detected' in subprocess.run(['unzip', '-t', path], capture_output=True, text=True).stdout, 'the zip is valid')

    # ---- 10. guest to email: cases and moves carry, ids kept when the guest is claimed ----
    def carry_setup(q):
        q.goto('https://sorted.test/'); q.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); q.reload(); wait(q, 500)
        g = guest(q); cid = make_case('Pangolin Gas said the engineer comes on %s, job PG-4412' % fri.strftime('%A'), q)
        q.evaluate("""(cid)=>{var d=JSON.parse(localStorage.getItem('__mockdb'));d.tasks.push({id:'mv1guest',data:{id:'mv1guest',kind:'moment',type:'moving',title:'Moving home',date:'2026-11-20',ans:{tenure:'rent'},items:{bb:{st:'case',caseId:cid,at:new Date().toISOString()}},rev:1,created:new Date().toISOString()}});var r=d.tasks.find(x=>x.id===cid);r.data.momentId='mv1guest';r.data.rev=(r.data.rev||0)+1;localStorage.setItem('__mockdb',JSON.stringify(d))}""", cid)
        q.reload(); wait(q, 900)
        q.evaluate("(()=>{var b=document.createElement('button');b.setAttribute('data-a','claim-signin');document.querySelector('main').appendChild(b);b.click()})()"); wait(q, 800)
        return g, cid
    g, gc = carry_setup(pg)
    car = json.loads(pg.evaluate("localStorage.getItem('sorted.carry')") or '{}')
    ok(isinstance(car, dict) and car.get('at') and [t['id'] for t in car.get('tasks', [])] == [gc] and [m['id'] for m in car.get('moments', [])] == ['mv1guest'], 'the carried copy holds the cases and the move, with the time it was made')
    sign_in(pg, 'u-mail', 'mail@example.com'); wait(pg, 800)
    c = srv(gc); mv = srv('mv1guest')
    ok(c and c.get('momentId') == 'mv1guest' and mv and mv.get('kind') == 'moment' and pg.evaluate("localStorage.getItem('sorted.carry')") is None and json.loads(pg.evaluate("localStorage.getItem('__claimed')"))['p_pairs'] == [], 'claimed: the case and the move keep their ids, still linked, and the carried copy is gone')
    # without the claim token the ids change and the links follow
    g, gc = carry_setup(pg)
    pg.evaluate("localStorage.removeItem('sorted.carrytok')")
    before = set(x['id'] for x in dbj().get('tasks', []))
    sign_in(pg, 'u-mail2', 'mail2@example.com'); wait(pg, 900)
    newt = [x['data'] for x in dbj().get('tasks', []) if x['id'] not in before]
    nc = [x for x in newt if x.get('kind') != 'moment']; nm_ = [x for x in newt if x.get('kind') == 'moment']
    ok(len(nc) == 1 and len(nm_) == 1 and nc[0]['id'] != gc and nc[0].get('momentId') == nm_[0]['id'] and nm_[0]['items']['bb']['caseId'] == nc[0]['id'] and 'Pangolin' in nc[0]['title'], 'not claimed: new ids, and the case and its move still point at each other')
    # gave up on the email: a new guest on this phone takes the cases back
    g, gc = carry_setup(pg)
    before = set(x['id'] for x in dbj().get('tasks', []))
    g2 = guest(pg); wait(pg, 600)
    newt = [x['data'] for x in dbj().get('tasks', []) if x['id'] not in before]
    ok(g2 != g and pg.evaluate("localStorage.getItem('sorted.carry')") is None and any('Pangolin' in (x.get('title') or '') and any(e['label'].startswith('Brought back') for e in x['events']) for x in newt) and any(x.get('kind') == 'moment' for x in newt), 'a new guest session on this phone takes the carried cases and move back')
    # the carried copy lasts a day
    g, gc = carry_setup(pg)
    pg.evaluate("(()=>{var c=JSON.parse(localStorage.getItem('sorted.carry'));c.at=Date.now()-2*86400000;localStorage.setItem('sorted.carry',JSON.stringify(c))})()")
    pg.goto('https://sorted.test/'); wait(pg, 700)
    ok(pg.evaluate("localStorage.getItem('sorted.carry')") is None and pg.evaluate("localStorage.getItem('sorted.carrytok')") is None, 'a carried copy older than a day is removed')

    # ---- 11. Moving home steps merge per step ----
    fresh()
    pg.evaluate("""()=>{var d=JSON.parse(localStorage.getItem('__mockdb'))||{};d.tasks=d.tasks||[];d.tasks.push({id:'mv1',data:{id:'mv1',kind:'moment',type:'moving',title:'Moving home',date:'2026-11-20',ans:{tenure:'rent',council:'yes',car:'yes',bb:'yes',nation:'en'},items:{},rev:1,created:new Date().toISOString()}});localStorage.setItem('__mockdb',JSON.stringify(d))}""")
    pg.goto('https://sorted.test/#move-mv1'); pg.reload(); wait(pg, 1200)
    if pg.locator('[data-a=mom-open]').count(): pg.locator('[data-a=mom-open]').first.click(); wait(pg, 700)
    pg.evaluate("""()=>{var d=JSON.parse(localStorage.getItem('__mockdb'));var r=d.tasks.find(x=>x.id==='mv1');r.data.items={tvl:{st:'irrelevant',at:new Date().toISOString()}};r.data.rev=(r.data.rev||0)+1;localStorage.setItem('__mockdb',JSON.stringify(d))}""")
    btn = pg.locator('[data-a=mom-done]').first; k = btn.get_attribute('data-k'); btn.click(); wait(pg, 1200)
    it = srv('mv1').get('items') or {}
    ok(it.get('tvl', {}).get('st') == 'irrelevant' and it.get(k, {}).get('st') == 'done', 'a step marked here and one marked on another device are both kept (%s)' % it)

    # ---- 12. signing out stops this phone's lock-screen reminders for the account ----
    pctx = new_ctx(STUB); pp = page(pctx)
    pp.goto('https://sorted.test/'); pp.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1');localStorage.setItem('__pushReady','1')")
    sign_in(pp, 'u-push', 'push@example.com')
    pc = make_case('Currys said they would refund £89 by %s, order 445566' % fri.strftime('%A'), pp)
    pp.goto('https://sorted.test/?task=%s' % pc); wait(pp, 800)
    if pp.locator('[data-a=push-on]').count(): pp.locator('[data-a=push-on]').first.click(); wait(pp, 900)
    subs = dbj(pp).get('push_subs', [])
    ok(len(subs) == 1 and subs[0]['user_id'] == 'u-push', 'reminders are on for this phone')
    pp.locator('.tab129 [data-a=data]').click(); wait(pp, 500)
    pp.locator('[data-a=signout]').first.click(); wait(pp, 1200)
    ok(not dbj(pp).get('push_subs') and pp.evaluate("localStorage.getItem('__mocksession')") is None and pp.evaluate("navigator.serviceWorker.getRegistration('/').then(r=>r?r.pushManager.getSubscription():null).then(s=>!s)"), 'sign-out removes this phone’s push address from the account and unsubscribes it')
    pctx.close()
    ok(not errs, 'no page errors: %s' % errs)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
