# v143 (audit pass 2, the reader): what was said, by whom, and from where, read the way a person would read it.
# PASS2-005: a demand on you (pay, reply, rent or a bill due, even after "Camden Council:") is a deadline on you, never
# their promise; receipts, return policies and validity periods are information. PASS2-007: "within 14 days of <date>"
# counts from that date and shows the working; a reply chain is read newest first, a quoted older message with its own
# date as the day they told you. PASS2-008: screen chrome ("9:41 4G 87%", "< Back", "Today 10:02", the tab bar) is
# never their words or their day, and a proposal read from a picture whose date has passed is never a one-tap miss.
# PASS2-010: corrections change whole words only, keep the other side's words as they said them (the corrected value
# beside them), keep the title and the Ref together, read "Ford Credit, not Ford", and rebuild the default chase.
# PASS2-016: where words came from (a picture, your own note) is carried to the history, the ledger and the record;
# "check their app" never comes from your own plan; "On the phone they will…" is not quoted as their words.
# PASS2-025: "before Friday" ends on Thursday, "after Friday" is no day. PASS2-033: a message already added is not
# proposed again with a new date. Dates are relative to today, on London time.
import os, sys, json, re, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates, corpus
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); O = HERE + '/tests/node_modules/'; errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
H = {'Access-Control-Allow-Origin': '*'}
def cdn(r):
    u = r.request.url
    if '/npm/tesseract.js@5.1.1/dist/' in u: return r.fulfill(path=O + 'tesseract.js/dist/' + u.split('/dist/')[1], content_type='application/javascript', headers=H)
    if '/npm/tesseract.js-core@5.1.1/' in u: f = u.split('@5.1.1/')[1]; return r.fulfill(path=O + 'tesseract.js-core/' + f, content_type='application/wasm' if f.endswith('.wasm') else 'application/javascript', headers=H)
    if '/npm/@tesseract.js-data/eng@1.0.0/' in u: return r.fulfill(path=O + '@tesseract.js-data/eng/4.0.0_best_int/eng.traineddata.gz', content_type='application/gzip', headers=H)
    return r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript')
today = datetime.date.today()
BH = {'2026-12-25', '2026-12-28', '2027-01-01', '2027-03-26', '2027-03-29', '2027-05-03', '2027-05-31', '2027-08-30', '2027-12-27', '2027-12-28'}
def wd_from(d, k):
    x = d; c = 0
    while c < k:
        x += datetime.timedelta(days=1)
        if x.weekday() < 5 and x.isoformat() not in BH: c += 1
    return x
def lday(iso):  # the London day of an ISO time
    return datetime.datetime.fromisoformat(iso.replace('Z', '+00:00')).astimezone().date()
T6 = today - datetime.timedelta(days=6); T6dm = '%d %s' % (T6.day, T6.strftime('%B'))
PHONE_HTML = ('<body style="margin:0;background:#fff;font-family:Arial;font-size:17px"><div style="padding:8px 14px;display:flex;justify-content:space-between"><b>9:41</b><span>4G 87%</span></div>'
              '<div style="padding:6px 14px;border-bottom:1px solid #ccc">&lt; Back &nbsp;&nbsp; <b>Evri</b></div><p style="text-align:center;color:#666">Today 10:02</p>'
              '<div style="margin:12px;padding:14px;background:#e9e9eb;border-radius:18px;max-width:320px">Your parcel will be delivered tomorrow between 9am and 1pm. Tracking EV123456789.</div>'
              '<div style="position:absolute;bottom:0;left:0;right:0;padding:12px;border-top:1px solid #ccc">Text Message &nbsp; Home &nbsp; Search &nbsp; Settings</div></body>')
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', cdn)
    # ---------- Part 1: the reader ----------
    rd = ctx.new_page(); rd.on('pageerror', lambda e: errs.append(str(e)))
    rd.route(lambda u: u.startswith('https://sorted.test/'), lambda q: q.fulfill(path=HERE + '/tests/out/reader.html', content_type='text/html'))
    rd.goto('https://sorted.test/'); wait(rd, 500)
    R = lambda t: rd.evaluate("(t)=>{var R=window.__read,f=R.caseFacts(t),p=R.readCase(t,f),w=R.frDeadline({said:t});return {amount:f.amount||0,party:f.party,demand:R.PDEMAND.test(t),dl:w?{date:w.date,alt:w.alt||null,phrase:w.phrase||'',told:w.told||null,prec:w.prec}:null,p:p?{said:p.said,party:p.party,dueAt:p.dueAt,dueEnd:p.dueEnd,by:p.by,prec:p.prec,phrase:p.phrase||'',told:p.told||null,alt:p.alt||null,altB:p.altB||null,cfrom:!!p.cfrom,past:!!p.past,quoted:!!p.quoted}:null}}", t)
    # 005: demands on you
    for txt, days in corpus.DEMANDS:
        r = R(txt)
        if days is None:
            ok(not r['p'] and not r['dl'] and not r['demand'], 'information, not a promise or a deadline: %s (%s)' % (txt[:60], json.dumps(r)[:160]))
        else:
            want = (today + datetime.timedelta(days=days)).isoformat()
            got = min([x for x in [r['dl'] and r['dl']['date'], r['dl'] and r['dl']['alt']] if x] or [''])
            ok(not r['p'] and r['demand'] and got == want, 'a deadline on you, not their promise: %s -> %s (wanted %s; %s)' % (txt[:60], got, want, json.dumps(r['p'])[:80]))
    r = R(corpus.DEMANDS[0][0]); ok(r['dl'] and r['dl']['told'] == T6.isoformat() and r['dl']['date'] == (T6 + datetime.timedelta(days=14)).isoformat() and r['dl']['alt'] == (T6 + datetime.timedelta(days=13)).isoformat() and 'from ' + T6dm in r['dl']['phrase'], '"within 14 days of %s" counts from that date, with both readings (%s)' % (T6dm, json.dumps(r['dl'])))
    r = R("Octopus Energy Your bill was £120.00 Discount applied -£20.00 Amount due £100.00 by " + dates.ahead(14)['dm']); ok(r['amount'] == 100, 'a bill keeps the amount due (£100), not the first figure (%s)' % r['amount'])
    for txt in ["Currys said they will pay the refund by Friday", "They said they'll pay it into my account by Thursday", "Amazon: we will reply within 8 weeks"]:
        r = R(txt); ok(r['p'] and not r['demand'], 'their payment or reply is still their promise: %s' % txt)
    # 007: a count from a stated date
    r = R("Currys said they would refund my £40 within five working days from " + T6dm)['p'] or {}
    hi, lo = wd_from(T6, 5), wd_from(T6, 4) if T6.weekday() < 5 else None
    ok(r.get('told') == T6.isoformat() and r.get('cfrom') and r.get('altB') == hi.isoformat() and r.get('prec') == 'calc', '"within five working days from %s" counts from that date, with Sorted’s working (%s)' % (T6dm, json.dumps(r)))
    if lo: ok(r.get('alt') == lo.isoformat(), 'and the earlier reading when %s may count' % T6dm)
    # 007: reply chains, newest first
    chain = "From: Currys <help@currys.co.uk>\nSent: %s\nWe're sorry, your refund has been delayed. We will contact you again.\n\n> On %s Currys wrote:\n> We will refund £89 within 5 working days. Order 445566." % (dates.ahead(-1)['dm'], T6dm)
    ok(R(chain)['p'] is None, 'a reply chain whose newest part says it is delayed proposes nothing from the old quoted promise')
    ok(R(chain.replace('\n', ' '))['p'] is None, 'the same, as one line read from a photo')
    r = R("Hi, just checking in.\n\n> On %s Currys wrote:\n> We will refund £89 within 5 working days. Order 445566." % T6dm)['p'] or {}
    ok(r.get('quoted') and r.get('told') == T6.isoformat() and r.get('altB') == wd_from(T6, 5).isoformat(), 'with nothing new on top, the quoted message is read from the day it was sent (%s)' % json.dumps(r))
    r = R("Update: your engineer is now booked for %s between 8am and 1pm.\n> On %s, John Lewis wrote:\n> Your engineer will visit tomorrow." % (dates.ahead(4)['long'], T6dm))['p'] or {}
    ok(r.get('dueAt') and lday(r['dueAt']) == dates.ahead(4)['date'] and not r.get('quoted'), 'the newest message wins over the quoted one')
    # 008: screen chrome
    shot_txt = "9:41 4G 87% < Back Evri Today 10:02 Your parcel will be delivered tomorrow between 9am and 1pm. Tracking EV123456789. Text Message Home Search Settings"
    r = R(shot_txt)['p'] or {}
    ok(r.get('party') == 'Evri' and not re.search(r'9:41|4G|87%|Today|Back|10:02', r.get('said', '')) and lday(r['dueAt']) == dates.ahead(1)['date'] and not r.get('past'), 'a screenshot: right day, no chrome in their words (%s)' % json.dumps(r))
    r = R(shot_txt.replace('Today 10:02', 'Yesterday 18:30'))['p'] or {}
    ok(r.get('dueAt') and lday(r['dueAt']) == today, 'sent yesterday, "tomorrow" is today (%s)' % (r.get('dueAt')))
    ok(rd.evaluate("__read.chrome143('They said they would come today 10:30 to fix it')") == 'They said they would come today 10:30 to fix it', 'typed words with a time are left alone')
    # 025: before and after
    r = R("Boots said they would refund my £40 before Friday")['p'] or {}
    ok(r.get('dueAt') and lday(r['dueAt']).strftime('%A') == 'Thursday' and r.get('by'), '"before Friday" is by Thursday (%s)' % r.get('dueAt'))
    ok(R("Argos said they would refund my £40 after Friday")['p'] is None, '"after Friday" is no day: no promise card')
    # 016: framing
    for txt in ["Currys said on the phone they will refund my £89 by Friday", "On the phone Currys said they will refund my £89 by Friday", "Currys said they would On the phone they will refund my £89 by Friday"]:
        r = R(txt)['p'] or {}; ok(r.get('said') == 'Refund my £89 by Friday' and r.get('party') == 'Currys', 'their quote is the commitment, not your framing: %s -> %s' % (txt, r.get('said')))
    # 010: whole tokens
    T = lambda s, a, c: rd.evaluate("([s,a,c])=>__read.tok143(s,a,c)", [s, a, c])
    ok(T('credit the debt on my bill by Friday, ref BT12345', 'BT', 'EE') == 'credit the debt on my bill by Friday, ref BT12345', 'never inside another word or a reference ("debt", "BT12345")')
    ok(T('BT said they would credit it', 'BT', 'EE') == 'EE said they would credit it', 'a whole word is changed')
    ok(T('claim 1234, policy 12345', '1234', '1239') == 'claim 1239, policy 12345', 'a number is changed only where it stands alone')
    ok(T('passed to Ford Credit by Ford', 'Ford', 'Ford Credit') == 'passed to Ford Credit by Ford Credit', '"Ford" becomes "Ford Credit" without "Ford Credit Credit"')
    cur = {"party": "Ford", "ref": "", "amount": "", "item": "", "dueAt": "", "said": "Ford said the credit check is done by Friday"}
    r = rd.evaluate("([c,s])=>{var r=__read.corrRead(c,s);return r?{k:r.k,to:String(r.to)}:null}", [cur, "It's Ford Credit now, not Ford"]) or {}
    ok(r.get('k') == 'party' and r.get('to') == 'Ford Credit', '"It’s Ford Credit now, not Ford" reads Ford Credit (%s)' % r)
    rd.close()
    # ---------- Part 2: the interface ----------
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    ctx.route(lambda u: 'gov.uk' in u, lambda r: r.fulfill(body='<title>Official page</title>', content_type='text/html'))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    case = lambda cid: [c for c in cases() if c['id'] == cid][0]
    main = lambda: pg.inner_text('main')
    labels = lambda cid: [e.get('label') or '' for e in case(cid)['events']]
    def tap(a): pg.locator('.tab129 [data-a=%s]' % a).click(); wait(pg, 500)
    def opn(cid): pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 800)
    def poke(js):
        pg.goto('https://sorted.test/'); wait(pg, 600)
        pg.evaluate("(js)=>{var db=JSON.parse(localStorage.getItem('__mockdb'));(new Function('db',js))(db);localStorage.setItem('__mockdb',JSON.stringify(db));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", js)
        pg.goto('https://sorted.test/'); wait(pg, 700)
    def submit_start(keep=True):
        pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 700)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 600)
        if keep and pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
        if keep and pg.locator('[data-a=nudge-skip]').count(): pg.click('[data-a=nudge-skip]'); wait(pg, 300)
        return cases()[-1]['id']
    def start(text, keep=True):
        tap('new-case'); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', text); return submit_start(keep)
    def panel(pn):
        if pg.locator('[data-a=panel][data-p="%s"]' % pn).count(): pg.locator('[data-a=panel][data-p="%s"]' % pn).first.evaluate('e=>e.click()')
        else: pg.evaluate("(pn)=>{var b=document.createElement('button');b.setAttribute('data-a','panel');b.setAttribute('data-p',pn);document.querySelector('main').appendChild(b);b.click()}", pn)
        wait(pg, 400)
    def paste(cid, text, own=False):
        opn(cid)
        if own: panel('changed'); pg.locator('[data-a=sc-own]').first.evaluate('e=>e.click()'); wait(pg, 300)
        else: panel('paste')
        pg.fill('#f-paste', text); pg.click('form[data-f=paste] button[type=submit]'); wait(pg, 700)
    def correct(cid, text):
        opn(cid); panel('correct'); pg.fill('#f-correct', text); pg.click('form[data-f=correct] button[type=submit]'); wait(pg, 600)
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')")
    pg.goto('https://sorted.test/#start'); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    # J1 (005) a typed demand: no promise card, a deadline on you, nobody "promised" it
    c1 = start(corpus.DEMANDS[0][0], keep=False)
    t = case(c1); m = main()
    ok(not t.get('promises') and not t.get('sugP') and pg.locator('.sug').count() == 0, 'J1 the council’s demand gives no promise card and no promise')
    ok((t.get('deadline') or {}).get('date') == (today + datetime.timedelta(days=7)).isoformat() and (t.get('deadline') or {}).get('latest') == (today + datetime.timedelta(days=8)).isoformat(), 'J1 the deadline on you is kept on the safe side, with the later reading beside it (%s)' % t.get('deadline'))
    ok('promised' not in m.lower() and 'Waiting for the council' not in m and 'Council promised' not in m, 'J1 the case never says the council promised anything')
    ok(t.get('board') != 'waiting', 'J1 the case is not waiting on them')
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 400)
    opn(c1); m = main()
    ok(('Sorted worked this out from “within 14 days from %s”' % T6dm) in m and 'if %s counts as the first day' % T6dm in m, 'J1 where the deadline is offered, Sorted shows its working and the two readings')
    home = (tap('go-home'), main())[1]
    ok('Waiting for the council' not in home and 'Council promised' not in home and 'Camden PCN' in home, 'J1 Home lists it as yours, not as waiting for the council')
    pack = pg.evaluate("(id)=>{var x=JSON.parse(localStorage.getItem('__mockdb')).tasks.find(r=>r.data.id===id);return JSON.stringify(x.data.promises||[])}", c1)
    ok(pack == '[]', 'J1 nothing in the record calls it their promise')
    # J1b a receipt: nothing to track, no deadline
    c1b = start(corpus.DEMANDS[7][0], keep=False); t = case(c1b)
    ok(not t.get('promises') and not t.get('sugP') and not t.get('deadline'), 'J1b a receipt with a returns policy: no promise, no deadline')
    # J2 (007) a count from a stated date: the working, both readings, and a choice
    c2 = start("Currys said they would refund my £40 within five working days from " + T6dm)
    t = case(c2); q = [x for x in t['promises'] if x['status'] == 'open'][0]
    ok(q.get('told') == T6.isoformat() and q.get('cfrom') and q.get('prec') == 'calc', 'J2 the promise counts from %s and is Sorted’s working (%s)' % (T6dm, {k: q.get(k) for k in ('told', 'alt', 'altB', 'prec', 'phrase')}))
    opn(c2); m = main()
    ok('Counting from:' in m and T6dm in m, 'J2 the case says what the count starts from')
    if T6.weekday() < 5: ok(pg.locator('[data-a=calc-pick]').count() == 3, 'J2 and asks which reading to use')
    # J3 (008, 016) a phone screenshot through the document door, read by Tesseract
    os.makedirs(HERE + '/tests/out', exist_ok=True); img = HERE + '/tests/out/b104_phone.png'
    sp = b.new_page(viewport={'width': 390, 'height': 560}); sp.set_content(PHONE_HTML); sp.screenshot(path=img); sp.close()
    tap('new-case'); pg.locator('[data-cap82=document]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.set_input_files('input[data-ocr=f-case]', img); st = ''
    for _ in range(240):
        st = (pg.inner_text('#ocr-status') if pg.locator('#ocr-status').count() else '') + ' ' + (pg.inner_text('#doc-status') if pg.locator('#doc-status').count() else '')
        if re.search(r'Photo read|couldn’t|doesn’t look|Done\.|can’t read', st): wait(pg, 700); break
        wait(pg, 500)
    ok('Done' in st and 'EV123456789' in pg.input_value('#f-case'), 'J3 the screenshot is read into the box (%s)' % st.strip()[:40])
    c3 = submit_start(keep=False); t = case(c3); sg = t.get('sugP') or {}; m = main()
    ok(sg and not re.search(r'9:41|4G|87%|Today|Back|10:02|Settings', sg.get('said', '')) and lday(sg['dueAt']) == dates.ahead(1)['date'] and not sg.get('past'), 'J3 the proposal has their words only and tomorrow’s date (%s, %s)' % (sg.get('said'), sg.get('dueAt')))
    ok('from the picture you added' in m.lower() and 'Yes, and it hasn’t happened' not in m and 'from what you wrote' not in m.lower() and 'Sorted read this date from the picture you added' in m, 'J3 the card says the words came from the picture')
    lb = labels(c3)
    ok(any(l.startswith('Added a screenshot: “') for l in lb) and not any(l.startswith('In your words') for l in lb), 'J3 the history files the picture as something added, not “In your words”')
    refs = t.get('refs') or []
    ok(any(r['v'] == 'EV123456789' and r['st'] == 'proposed' for r in refs) and not any(r['st'] == 'confirmed' for r in refs), 'J3 the reference read from the picture is proposed, not confirmed without a tap (%s)' % refs)
    ok(not any(r.get('src') in ('what you wrote when you started', 'what you wrote') for r in (t.get('ledger') or [])), 'J3 the ledger never says the picture’s words were what you wrote')
    ok('What happened: Added a screenshot' not in m, 'J3 the Now card doesn’t repeat the picture’s words as what happened')
    opn(c3)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
    if pg.locator('[data-a=nudge-skip]').count(): pg.click('[data-a=nudge-skip]'); wait(pg, 300)
    lb = labels(c3); ok(any('Taken from their message' in l for l in lb), 'J3 confirming it records the words as theirs')
    opn(c3); panel('pack'); pack = pg.inner_text('.pack-doc') if pg.locator('.pack-doc').count() else ''
    pl = pack.lower(); you = pl.split('\nwhat i say\n')[1].split('\nevidence\n')[0] if '\nwhat i say\n' in pl else ''
    other = pl.split('\nwhat the other side says\n')[1].split('\nwhat i say\n')[0] if '\nwhat the other side says\n' in pl else ''
    ok('ev123456789' not in you and 'in my words' not in pl and 'tracking ev123456789' in other, 'J3 the record puts the picture under what the other side says, not what I say')
    # J4 (008) a proposal from a picture whose date has passed: ask for the date, no one-tap miss
    poke("db.tasks.forEach(function(r){if(r.data.id==='%s'){var p=r.data.sugP;p.dueAt=new Date(Date.now()-3*36e5).toISOString();p.dueEnd=null;p.past=true;r.data.sugDone=false}})" % c3)
    opn(c3); m = main()
    ok('Check the date' in m and 'Yes, and it hasn’t happened' not in m and pg.locator('[data-a=sug-yes][data-v=missed]').count() == 0, 'J4 a passed date read from a picture asks for the date, never a one-tap “it didn’t happen”')
    # J5 (010) corrections keep their words and the title and Ref together
    c5 = start('BT said they would credit the debt on my bill by Friday, ref BT12345')
    correct(c5, 'Sorry, it was EE not BT'); pg.click('[data-a=corr-yes]'); wait(pg, 600)
    t = case(c5); q = t['promises'][-1]
    ok('debt' in q['said'] and 'deEE' not in json.dumps(t) and 'EE12345' not in json.dumps(t), 'J5 "debt" and "BT12345" are never rewritten (%s)' % q['said'])
    ok(q.get('words') and 'BT' not in (q.get('party') or '') and q['party'] == 'EE' and q.get('words') == q['said'] or 'BT12345' in q.get('words', ''), 'J5 their words are kept as they said them (%s)' % q.get('words'))
    ok(t['title'].find('BT12345') >= 0 and (t.get('facts') or {}).get('ref') == 'BT12345' or 'BT12345' not in t['title'], 'J5 the title and the stored Ref agree (%s, %s)' % (t['title'], (t.get('facts') or {}).get('ref')))
    correct(c5, 'the reference is EE77123 not BT12345'); pg.click('[data-a=corr-yes]'); wait(pg, 600)
    t = case(c5); q = t['promises'][-1]; m = main()
    ok(t['facts']['ref'] == 'EE77123' and 'BT12345' not in t['title'] and q['ref'] == 'EE77123', 'J5 a corrected reference changes the Ref and the title together (%s)' % t['title'])
    ok('BT12345' in q.get('words', '') and 'corrected reference: EE77123' in m, 'J5 the card quotes their words with the corrected reference beside them')
    panel('pack'); pack = pg.inner_text('.pack-doc')
    ok('“' in pack and 'ref BT12345' in pack and 'ref BT12345” (corrected reference: EE77123)' in pack, 'J5 the record quotes their words unchanged, with the corrections beside them')
    # the default chase, saved after a miss, follows a corrected reference
    c5s = start('Sky said they would refund £50 by Friday, ref SK12345')
    poke("db.tasks.forEach(function(r){if(r.data.id==='%s')r.data.promises.forEach(function(q){if(q.status==='open'){q.dueAt=new Date(Date.now()-2*864e5).toISOString();q.dueEnd=null;q.allDay=true;q.by=true}})})" % c5s)
    opn(c5s)
    pg.locator('[data-a=missed]').first.evaluate('e=>e.click()'); wait(pg, 600)
    if pg.locator('form[data-f=call]').count(): pg.locator('form[data-f=call] button[type=submit]').first.click(); wait(pg, 500)
    ask0 = (case(c5s).get('call') or {}).get('ask', '')
    correct(c5s, 'the reference is SK99999 not SK12345'); pg.click('[data-a=corr-yes]'); wait(pg, 600)
    ask1 = (case(c5s).get('call') or {}).get('ask', '')
    ok('SK12345' in ask0 and 'SK99999' in ask1 and 'SK12345' not in ask1, 'J5 the default chase is rebuilt from the current details (%s)' % ask1[:160])
    c5b = start('Aviva said they would settle claim 1234 by Friday, policy 12345')
    correct(c5b, 'the claim reference is 1239 not 1234'); pg.click('[data-a=corr-yes]'); wait(pg, 600)
    t = case(c5b); ok('12395' not in json.dumps(t) and '12345' in json.dumps(t.get('refs') or []) + json.dumps(t['promises']), 'J5 a claim number correction never touches the policy number')
    c5c = start('Ford said the credit check will be done by Friday')
    correct(c5c, "It's Ford Credit now, not Ford"); m = main()
    ok('Did you mean Ford Credit, not Ford?' in m, 'J5 "Ford Credit, not Ford" asks about Ford Credit')
    pg.click('[data-a=corr-yes]'); wait(pg, 600); t = case(c5c)
    ok(t['facts']['party'] == 'Ford Credit' and 'Credit Credit' not in json.dumps(t), 'J5 the party is Ford Credit, never "Credit" or "Ford Credit Credit"')
    # J6 (016) your own note is yours; your own plan never becomes "check their app"
    c6 = start('Argos said they would refund my £30 by Friday, order 778812')
    paste(c6, 'I rang them and they said it is on its way, I will check my card app on Friday', own=True)
    lb = labels(c6)
    ok(any(l.startswith('Added your own words: “') for l in lb) and not any(l.startswith('Added a message: “I rang') for l in lb), 'J6 a note in your own words is filed as yours')
    opn(c6); panel('pack'); pack = pg.inner_text('.pack-doc')
    pl = pack.lower(); other = pl.split('\nwhat the other side says\n')[1].split('\nwhat i say\n')[0] if '\nwhat the other side says\n' in pl else ''
    ok('i rang them' not in other and 'my note' in pl and 'i rang them' in (pl.split('\nwhat i say\n')[1] if '\nwhat i say\n' in pl else ''), 'J6 the record puts your note under what I say, never what the other side says')
    opn(c6); m = main()
    ok('Argos’s app' not in m and 'check Argos' not in m, 'J6 your own plan to check your card app never becomes "check Argos’s app"')
    c6b = start("Argos still hasn't refunded my £30. I'll check my card app tomorrow", keep=False)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 400)
    opn(c6b); m = main()
    ok('Argos’s app' not in m and pg.locator('[data-a=chk-app]').count() == 0, 'J6 "I’ll check my card app" is your plan: no "check Argos’s app or website"')
    c6c = start("Evri said I can track the parcel in their app", keep=False)
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 400)
    opn(c6c); ok(pg.locator('[data-a=chk-app]').count() == 1, 'J6 what they said about their app still leads to "I’ve checked their app"')
    # J7 (033) a message already added is not proposed again with a new date
    c7 = start('Evri said they would deliver my parcel on %s, ref EV654321' % dates.ahead(2)['long'])
    paste(c7, 'Evri: your delivery has been rescheduled to %s' % dates.ahead(4)['long'])
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
    n0 = len(case(c7)['events']); np0 = len(case(c7)['promises'])
    paste(c7, 'Evri: your delivery has been rescheduled to %s' % dates.ahead(4)['long']); m = main(); t = case(c7)
    ok('You added this message on' in m and not (t.get('sugP') and not t.get('sugDone')) and len(t['events']) == n0 and len(t['promises']) == np0, 'J7 the same message again: Sorted says it already has it and changes nothing')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
