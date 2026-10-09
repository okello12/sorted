# v145 (audit pass 3, reviewer A): what Sorted reads from people's words, and what it then says on every surface.
#  1 a weekday with a day of the month ("Monday 19th", "Weds 21st") is that date, never the next weekday; "on 22nd" is
#    a date; an ISO date is a date; "COB Monday" is Monday at 5pm, never today
#  2 "Rang BT today, they said Monday" is Monday: the day you contacted them is not the day they gave; their words are
#    kept without "Spoke to Octopus today they said"
#  3 "I was told", "we were told", "the landlord says" carry a promise; "said on the phone last Wednesday" counts from
#    Wednesday; "…and if not I should call again" is your own fallback, not a condition on their promise
#  4 not their promise: "Your payment of £120 to British Gas is due", "your bill will be taken on", "School: parents
#    evening is on Thursday", "Octopus: your new tariff starts on", "Surgery: please call back after 8am", "it should be
#    ready Friday, they'll try their best"; the quoted older email is not read when the reply says they're looking into it
#  5 a WhatsApp export: the time stamp is never the date they gave
#  6 a promise is written once with its date: never "in 3 to 5 working days, in 3 to 5 working days (…)" in the
#    history, the ledger, the pack or the helper's link
#  7 a deadline on you is on every surface: Home, the case, the pack and the export, the summary and the helper's
#    link, before and after it passes
#  8 a plan: waiting is not checking; reading their email or visiting their website is checking; a specific plan keeps
#    the person's own words as their step on the case and on Home
#  9 corrections never make "Amount" or "Due on Thursday" the thing
# 10 "Did your builder do what they said?", never "Did Builder …"
# 11 records from older versions migrate once and then stay still (no new revision or history on every open)
import os, sys, json, datetime, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates  # London time
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
SESSION = json.dumps({'user': {'id': 'u-me', 'email': 'me@example.com'}})
today = datetime.date.today(); D = datetime.timedelta
T0 = datetime.datetime.combine(today, datetime.time(9, 0))
def fday(d): return d.strftime('%A ') + str(d.day) + d.strftime(' %B')
def nxt(wd, skip=0):
    d = today + D(days=1 + skip)
    while d.weekday() != wd: d += D(days=1)
    return d
def ordn(n): return str(n) + ('th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))
MON1, MON2, WED2 = nxt(0), nxt(0, 7), nxt(2, 7)
A12, A20 = today + D(days=12), today + D(days=20)
src = open(HERE + '/tests/out/index.html').read(); hook = '\nboot();\n})();\n'
assert src.count(hook) == 1, 'end of the main script not found exactly once'
open(HERE + '/tests/out/truth110.html', 'w').write(src.replace(hook, '\nwindow.__T={S:S,packText:packText,shareCard:shareCard,sumText137:sumText137};' + hook))
RD = """(xs)=>xs.map(function(t){var r=window.__read,f=r.caseFacts(t),p=r.readCase(t,f);var d=r.frDeadline({said:t,facts:f});
  return {p:p?{said:p.said,party:p.party,dueAt:p.dueAt,past:p.past,told:p.told||'',prec:p.prec,when:r.whenText(p)}:null,dl:d&&d.date?r.dl143(d).date:null}})"""
def L(iso): return datetime.datetime.fromisoformat(iso.replace('Z', '+00:00')).astimezone()
with sync_playwright() as p:
    b = p.chromium.launch()
    # ================= the reader (a test-only copy that exposes it) =================
    rc = b.new_context(timezone_id='Europe/London')
    rc.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    rc.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/reader.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    rp = rc.new_page(); rp.on('pageerror', lambda e: errs.append(str(e))); rp.goto('https://sorted.test/'); wait(rp, 500)
    ok(rp.evaluate("!!(window.__read&&window.__read.checkPlan144&&window.__read.dd145a)"), 'reader hook present, with the plan and surface helpers')
    def R(xs): return rp.evaluate(RD, xs)
    # 1 dates
    cases1 = [('Sky said the engineer will come Monday %s' % ordn(MON2.day), MON2), ('Virgin said the engineer is coming Mon %s between 8 and 12' % ordn(MON2.day), MON2),
              ('the builder said he\'ll start Weds %s' % ordn(WED2.day), WED2), ('UPS said the parcel will be delivered on %s' % A12.isoformat(), A12),
              ('Sky confirmed the engineer visit for %s' % A12.isoformat(), A12), ('Currys said they will deliver it on %s' % ordn(A20.day), A20)]
    for (s, want), r in zip(cases1, R([x for x, _ in cases1])):
        ok(r['p'] and L(r['p']['dueAt']).date() == want, '1 %r is %s: %s' % (s, fday(want), r['p'] and r['p']['when']))
    r = R(['Octopus said the refund will be in my account by COB Monday', 'BT said they\'d fix the line by close of business Monday', 'The bank said the transfer will go through by end of day tomorrow'])
    ok(r[0]['p'] and L(r[0]['p']['dueAt']).date() == MON1 and L(r[0]['p']['dueAt']).hour == 17, '1 “COB Monday” is Monday at 5pm, never today: %s' % (r[0]['p'] and r[0]['p']['when']))
    ok(r[1]['p'] and L(r[1]['p']['dueAt']).date() == MON1, '1 “close of business Monday” is Monday')
    ok(r[2]['p'] and L(r[2]['p']['dueAt']).date() == today + D(days=1) and L(r[2]['p']['dueAt']).hour == 17, '1 “end of day tomorrow” is tomorrow at 5pm')
    pw = rp.evaluate("""()=>{var r=window.__read,f=function(t,n){var w=r.parseWhen(t,new Date(n));return w?w.date+(w.from?' '+w.from:'')+(w.wstart?' from '+w.wstart:''):null};
      return [f('Monday 4th','2026-12-28T10:00:00'),f('on the 2nd','2026-12-28T10:00:00'),f('by COB tomorrow','2026-12-31T10:00:00'),f('within 3 working days','2026-12-23T10:00:00'),f('within 5 working days','2026-12-31T10:00:00'),f('Monday 8-12','2026-12-28T10:00:00'),f('today or tomorrow','2026-12-31T10:00:00')]}""")
    ok(pw == ['2027-01-04', '2027-01-02', '2027-01-01 17:00', '2026-12-30', '2027-01-08', '2026-12-28', '2027-01-01 from 2026-12-31'], '1 across the year end and the Christmas bank holidays (“Monday 8-12” is never the 8th): %s' % pw)
    # 2 the day you contacted them is not their day
    two = ['Rang BT today and they said the engineer will come on Monday, ref BT1234, I have been without broadband for a week now and it is a nightmare',
           'Chatted to Evri this afternoon on the app, they said the parcel will be redelivered on Monday and to keep an eye on tracking',
           'Spoke with the landlord tonight he said the plumber will come on Thursday between 8 and 12 to sort the leak under the sink',
           'spoke to octopus today they said they will send a engineer out on the %s between 8 and 12 and also refund the £40 by next friday' % ordn(A20.day)]
    r = R(two)
    ok(r[0]['p'] and L(r[0]['p']['dueAt']).date() == MON1, '2 “Rang BT today … Monday” is Monday: %s' % (r[0]['p'] and r[0]['p']['when']))
    ok(r[1]['p'] and L(r[1]['p']['dueAt']).date() == MON1, '2 “Chatted to Evri this afternoon … Monday” is Monday')
    ok(r[2]['p'] and L(r[2]['p']['dueAt']).strftime('%A') == 'Thursday' and L(r[2]['p']['dueAt']).hour == 8, '2 “Spoke with the landlord tonight … Thursday between 8 and 12” is Thursday at 8')
    ok(r[3]['p'] and L(r[3]['p']['dueAt']).date() == A20 and L(r[3]['p']['dueAt']).hour == 8 and not r[3]['p']['said'].lower().startswith('spoke'), '2 the second half of a run-on keeps its date (the %s), and their words start with what they said: %r' % (ordn(A20.day), r[3]['p'] and r[3]['p']['said']))
    # 3 told
    r = R(['I was told the refund will be paid by Wednesday', 'We were told the repair will be done by Friday', 'I phoned Currys this morning and was told the refund will be paid by Wednesday. Order number 445566.',
           'Landlord says the gas safety check will be done on %s' % A12.strftime('%d/%m'), 'They said on the phone last Wednesday that I\'d get the refund within 10 working days',
           'On the phone last Wednesday they said the refund would come within 10 working days',
           'so i rang them and the lady said someone from the repairs team would ring me back on wednesday and if not i should call again'])
    ok(r[0]['p'] and L(r[0]['p']['dueAt']).strftime('%A') == 'Wednesday' and r[1]['p'] and r[2]['p'] and r[2]['p']['party'] == 'Currys', '3 “I was told”, “we were told” and “… and was told” are their promise')
    ok(r[3]['p'] and L(r[3]['p']['dueAt']).date() == A12, '3 “Landlord says … on %s” is their promise' % A12.strftime('%d/%m'))
    lw = today - D(days=((today.weekday() - 2) % 7) or 7)
    ok(r[4]['p'] and r[4]['p']['told'] == lw.isoformat() and r[5]['p'] and r[5]['p']['told'] == lw.isoformat(), '3 “said on the phone last Wednesday” counts from Wednesday %s: %s / %s' % (lw, r[4]['p'] and r[4]['p']['told'], r[5]['p'] and r[5]['p']['told']))
    ok(r[4]['p'] and not r[4]['p']['said'].lower().startswith('last'), '3 their words start with what they said: %r' % (r[4]['p'] and r[4]['p']['said']))
    ok(r[6]['p'] and L(r[6]['p']['dueAt']).strftime('%A') == 'Wednesday' and 'call again' not in r[6]['p']['said'], '3 “… and if not I should call again” is your fallback; their promise stands: %r' % (r[6]['p'] and r[6]['p']['said']))
    # 4 not their promise
    nots = ['Barclays: Your payment of £120.00 to BRITISH GAS is due on %s' % A12.strftime('%d/%m'), 'EE: your bill of £45.20 will be taken on %s' % A12.strftime('%d/%m'),
            'School: Parents evening is on Thursday', 'Octopus: Your new tariff starts on 1 November', 'Surgery: please call back after 8am tomorrow to book',
            'Garage said it should be ready Friday, they\'ll try their best',
            'Thanks for your patience, we are looking into this.\n\nOn 1 Oct 2026, at 10:02, BT <noreply@bt.com> wrote:\n> Your engineer will visit on 5 October.']
    r = R(nots)
    for s, x in zip(nots, r): ok(not x['p'], '4 not their promise: %r%s' % (s[:60], '' if not x['p'] else ' -> ' + x['p']['said']))
    ok(r[0]['dl'] == A12.isoformat(), '4 “Your payment … to British Gas is due on” is a deadline on you: %s' % r[0]['dl'])
    r = R(["BT said they can't come Monday but will come Wednesday instead", "British Gas said they couldn't come today but will be here tomorrow between 8 and 12", "BT said they can't come Monday", 'Sky said they will call me back on Monday, if not Tuesday', "admiral said they'd call me back on Tuesday"])
    ok(r[0]['p'] and L(r[0]['p']['dueAt']).strftime('%A') == 'Wednesday' and 'can' not in r[0]['p']['said'].lower(), '4 “can’t come Monday but will come Wednesday” is Wednesday, never Monday: %s' % (r[0]['p'] and r[0]['p']['said']))
    ok(r[1]['p'] and L(r[1]['p']['dueAt']).date() == today + D(days=1) and L(r[1]['p']['dueAt']).hour == 8, '4 “couldn’t come today but will be here tomorrow 8 to 12” is tomorrow at 8')
    ok(not r[2]['p'], '4 “they can’t come Monday” alone is no promise')
    ok(r[3]['p'] and 'between' in r[3]['p']['when'].lower() and L(r[3]['p']['dueAt']).date() == MON1, '4 “Monday, if not Tuesday” is Monday or Tuesday: %s' % (r[3]['p'] and r[3]['p']['when']))
    ok(r[4]['p'] and r[4]['p']['party'] == 'Admiral', '4 “admiral said” is Admiral’s promise')
    # 5 WhatsApp
    old = today - D(days=3)
    wa = ['[%s, 14:02] Dave Plumber: I\'ll come Monday morning to fix the tap\n[%s, 14:03] Me: thanks' % (today.strftime('%d/%m/%Y'), today.strftime('%d/%m/%Y')),
          '%s, 09:15 - Sarah (Letting Agent): The electrician will come on Wednesday between 9 and 12' % today.strftime('%d/%m/%Y'),
          '[%s, 18:40] Dave Plumber: I\'ll come tomorrow to fix the tap' % old.strftime('%d/%m/%Y')]
    r = R(wa)
    ok(r[0]['p'] and L(r[0]['p']['dueAt']).date() == MON1 and L(r[0]['p']['dueAt']).hour == 8, '5 a WhatsApp line: Monday morning, not the time stamp: %s' % (r[0]['p'] and r[0]['p']['when']))
    ok(r[1]['p'] and L(r[1]['p']['dueAt']).strftime('%A') == 'Wednesday' and L(r[1]['p']['dueAt']).hour == 9, '5 an Android export line: Wednesday 9 to 12')
    ok(not r[2]['p'] or L(r[2]['p']['dueAt']).date() < today, '5 “tomorrow” three days ago is never today or later: %s' % (r[2]['p'] and r[2]['p']['when']))
    # 6, 8, 9, 10 helpers
    ok(rp.evaluate("window.__read.dd145a('They said: The money will be back in my account in 3 to 5 working days, in 3 to 5 working days (between Wednesday 14 October and Friday 16 October).')") == 'They said: The money will be back in my account in 3 to 5 working days (between Wednesday 14 October and Friday 16 October).', '6 a repeated date phrase is written once')
    ok(rp.evaluate("window.__read.dd145a('Thank you, thank you. No, no.')") == 'Thank you, thank you. No, no.', '6 ordinary repeated words are left alone')
    plans = rp.evaluate("""()=>{var r=window.__read,t=function(b){return {baseline:b,facts:{party:'Barclays'}}};return ['Search up how I can do it','Check my bank app to see if the refund has gone in','Read the email they sent me again','Visit their website','Check my phone for their text','Wait and see what happens','See if they reply','Check back in a week','Ring them','Send them a message','Check with them on the phone','See what Citizens Advice says','Work out how much they owe me'].map(function(b){return r.checkPlan144(b)?r.planWhat144(t(b)):''})}""")
    ok(plans == ['Check Barclays’ official website or app for how to do this', 'Check my bank app to see if the refund has gone in', 'Read the email they sent me again', 'Visit their website', 'Check my phone for their text', '', '', '', '', '', '', 'See what Citizens Advice says', 'Work out how much they owe me'], '8 plans: checking keeps the person’s words; waiting and contacting are not checks: %s' % plans)
    co = rp.evaluate("""()=>{var r=window.__read,d=new Date();d.setDate(d.getDate()+6);d.setHours(0,0,0,0);var cur={party:'BT',ref:'BT12345',amount:89,item:'router',dueAt:d.toISOString(),allDay:true,said:'BT said they would fix the router'};
      return ['Actually the amount is fifty pounds','Actually it\\'s due on '+['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][d.getDay()]+', not Wednesday','sorry it\\'s the modem not the router'].map(function(x){var c=r.corrRead(cur,x);return c?c.k+':'+c.to:''})}""")
    ok(co[0] == '' and not co[1].startswith('item') and co[2] == 'item:Modem', '9 corrections never make “Amount” or “Due on …” the thing, and a real one still works: %s' % co)
    hq = rp.evaluate("[window.__read.home55Question({party:'Builder',said:'Finish the kitchen'},null),window.__read.home55Question({party:'Currys',said:'Sort the order'},null)]")
    ok(hq == ['Did your builder do what they said?', 'Did Currys do what they said?'], '10 %s' % hq)
    rc.close()

    # ================= the app: every surface, with the clock moving =================
    ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844}, accept_downloads=True)
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/truth110.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    ctx.route(lambda u: 'gov.uk' in u, lambda r: r.fulfill(body='<title>Official page</title>', content_type='text/html'))
    ctx.clock.install(time=T0)
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    case = lambda cid: [c for c in cases() if c['id'] == cid][0]
    labels = lambda cid: [e.get('label') or '' for e in case(cid)['events']]
    main = lambda: pg.inner_text('main')
    def tap(a): pg.locator('.tab129 [data-a=%s]' % a).first.click(); wait(pg, 500)
    def click(sel, ms=600):
        k = pg.locator(sel).count()
        if k: pg.locator(sel).first.evaluate('e=>e.click()'); wait(pg, ms)
        return k
    def at(days, hour=9):
        ctx.clock.set_system_time(T0 + D(days=days, hours=hour - 9)); pg.goto('https://sorted.test/'); wait(pg, 800)
    def start(text, plan=None, keep=True):
        tap('new-case'); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 700)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count():
            if plan: pg.fill('#f-baseline', plan)
            else: pg.click('form[data-f=baseline] .chip >> nth=0')
            pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 600)
        if keep and pg.locator('[data-a=sug-yes]').count(): pg.locator('[data-a=sug-yes]').first.click(); wait(pg, 600)
        if pg.locator('[data-a=nudge-skip]').count(): pg.click('[data-a=nudge-skip]'); wait(pg, 300)
        if pg.locator('[data-a=refs-yes]').count(): pg.click('[data-a=refs-yes]'); wait(pg, 300)
        return cases()[-1]['id']
    def opencase(cid): pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 800)
    def tobj(cid): return "__T.S.tasks.filter(function(x){return x.id==='%s'})[0]" % cid
    def pack(cid): return pg.evaluate("()=>__T.packText(%s)" % tobj(cid))
    def summary(cid): return pg.evaluate("()=>__T.sumText137(%s,'')" % tobj(cid))
    def home(): tap('go-home'); return main()
    def homerow(cid):
        home(); return pg.evaluate("(id)=>{var e=document.querySelector('[data-id=\"'+id+'\"]');return e?e.innerText:''}", cid)
    def understood(cid):
        opencase(cid); pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); wait(pg, 150)
        return pg.inner_text('details.case117-u') if pg.locator('details.case117-u').count() else ''
    def share(cid):
        opencase(cid)
        if not case(cid).get('shareToken'):
            pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); wait(pg, 150); click('details.case56-sharing [data-a=share]', 900)
        tok = case(cid).get('shareToken')
        if not tok: return ''
        hp = ctx.new_page(); hp.goto('https://sorted.test/?share=' + tok); wait(hp, 900); txt = hp.inner_text('main'); hp.close(); return txt
    def export():
        tap('data'); wait(pg, 300)
        try:
            with pg.expect_download(timeout=8000) as dl: click('[data-a=export-file]', 900)
            return open(dl.value.path(), encoding='utf-8').read()
        except Exception as e: return 'EXPORT FAILED ' + str(e)[:100]
    BAD = re.compile(r'\bundefined\b|\bnull\b|\bNaN\b|Invalid Date|\[object')
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')")
    pg.evaluate("localStorage.setItem('__mocksession', %s)" % json.dumps(SESSION)); pg.goto('https://sorted.test/'); wait(pg, 700)

    # 1 "Monday 19th" on every surface
    c1 = start('Sky said the engineer will come Monday %s, ref SKY778899' % ordn(MON2.day))
    p1 = [q for q in case(c1)['promises'] if q['status'] == 'open']
    ok(len(p1) == 1 and L(p1[0]['dueAt']).date() == MON2, '1 the promise is on %s, not next Monday' % fday(MON2))
    hr = homerow(c1); ok(fday(MON2) in hr and fday(MON1) not in hr, '1 Home shows %s: %r' % (fday(MON2), hr[:120]))
    opencase(c1); m = main(); ok(fday(MON2) in m and fday(MON1) not in m, '1 the case page shows %s' % fday(MON2))
    u = understood(c1); ok(fday(MON2) in u, '1 What Sorted understood has their date')
    sh = share(c1); ok(fday(MON2) in sh and fday(MON1) not in sh, '1 the helper’s link shows %s' % fday(MON2))
    pk = pack(c1); ok(fday(MON2) in pk and fday(MON1) not in pk and not BAD.search(pk), '1 the pack shows %s' % fday(MON2))

    # 2 "Rang BT today … Monday", and their words
    c2 = start('Spoke to Octopus today, they said they will send an engineer out on the %s between 8 and 12' % ordn(A20.day))
    p2 = [q for q in case(c2)['promises'] if q['status'] == 'open']
    ok(len(p2) == 1 and L(p2[0]['dueAt']).date() == A20 and L(p2[0]['dueAt']).hour == 8, '2 the engineer is on %s at 8, not today' % fday(A20))
    ok(not p2[0]['said'].lower().startswith('spoke'), '2 their words, not the call: %r' % p2[0]['said'])
    ok(fday(A20) in homerow(c2) and fday(today) not in homerow(c2), '2 Home shows %s' % fday(A20))

    # 6 an estimate written once: history, ledger, pack, helper's link
    c6 = start('Barclays said the money will be back in my account in 3 to 5 working days')
    lab = [l for l in labels(c6) if l.startswith('They said')]
    dup = re.compile(r'in 3 to 5 working days, in 3 to 5 working days', re.I)
    ok(lab and not dup.search(lab[0]) and 'in 3 to 5 working days' in lab[0], '6 the history line says the phrase once: %r' % (lab and lab[0]))
    lg = [x for x in case(c6).get('ledger', []) if x.get('type') == 'promise']
    ok(lg and all(not dup.search(x.get('v') or '') for x in lg), '6 the ledger says it once: %s' % [x.get('v') for x in lg])
    pk = pack(c6); ok('in 3 to 5 working days' in pk and not dup.search(pk), '6 the pack says it once')
    sh = share(c6); ok('in 3 to 5 working days' in sh and not dup.search(sh), '6 the helper’s link says it once')
    opencase(c6); ok(not dup.search(main()), '6 the case page says it once')

    # 7 a deadline on you, everywhere, before and after it passes
    c7 = start('Camden Council: you must pay the £80 penalty within 28 days')
    dl = today + D(days=28)
    ok(case(c7).get('deadline', {}).get('date') == dl.isoformat(), '7 the deadline is kept: %s' % case(c7).get('deadline'))
    hm = home(); ok(fday(dl) in hm, '7 Home names the deadline')
    opencase(c7); ok(fday(dl) in main(), '7 the case names the deadline')
    pk = pack(c7); ok('Your deadline: By ' + fday(dl) in pk and '“within 28 days”' in pk, '7 the pack lists the deadline with Sorted’s working')
    sm = summary(c7); ok('My deadline:\n- By ' + fday(dl) in sm, '7 the summary lists the deadline')
    sh = share(c7); ok('deadline to act' in sh.lower() and fday(dl) in sh, '7 the helper’s link shows the deadline')
    ex = export(); ok('Your deadline: By ' + fday(dl) in ex, '7 the export lists it')
    ok(not [q for q in case(c7).get('promises', []) if q['status'] == 'open'], '7 a demand is never the council’s promise')

    # 8 plans
    c8 = start('My Currys refund still hasn’t shown up', plan='Check my bank app to see if the refund has gone in')
    mv = [x for x in case(c8).get('moves', []) if x.get('src') == 'plan']
    ok(len(mv) == 1 and mv[0]['what'] == 'Check my bank app to see if the refund has gone in' and pg.locator('form[data-f=call]').count() == 0, '8 the step is the person’s own plan, in their words: %s' % [x.get('what') for x in mv])
    hm = home(); ok('bank app' in hm and 'official website' not in hm, '8 Home names their own step')
    c8b = start('Evri still haven’t delivered my parcel', plan='Wait and see what happens')
    ok(not [x for x in case(c8b).get('moves', []) if x.get('src') == 'plan'], '8 waiting is not a check step')
    c8c = start('Barclays blocked my card', plan='Read the email they sent me again')
    ok([x['what'] for x in case(c8c).get('moves', []) if x.get('src') == 'plan'] == ['Read the email they sent me again'], '8 reading their email is a check, not contacting them')

    # 10 the question on Home names the builder properly, once the date has passed
    c10 = start('Builder said he will finish the kitchen by the end of next week')
    at(16)
    hm = home(); ok('Did your builder do what they said?' in hm and 'Did Builder ' not in hm, '10 Home asks “Did your builder do what they said?”')
    pk = pack(c7); ok('Your deadline: Passed on ' + fday(dl) in pk if (today + D(days=16)) > dl else 'Your deadline: By ' + fday(dl) in pk, '7 at +16 days the pack still carries the deadline')
    at(40)
    pk = pack(c7); sm = summary(c7); sh = share(c7)
    ok('Your deadline: Passed on ' + fday(dl) in pk and 'My deadline:\n- Passed on ' + fday(dl) in sm and 'Passed on ' + fday(dl) in sh, '7 after the deadline the pack, the summary and the link say it passed')
    hm = home(); ok(fday(dl) in hm, '7 Home still names the passed deadline')
    for cid in (c1, c2, c6, c7, c8, c10):
        t = pack(cid); ok(not BAD.search(t), 'no undefined, null, NaN or Invalid Date in the pack of %s' % case(cid)['title'][:40])

    # 11 records from older versions migrate once, then stay still
    at(0)
    past = (T0 - D(days=20)).isoformat()
    def iso(n): return datetime.datetime.combine(today + D(days=n), datetime.time(0)).astimezone().isoformat()
    OLD = {
     'o99': {'id': 'o99', 'mode': 'call', 'title': 'Old Currys refund', 'baseline': 'Not sure yet', 'created': past, 'updatedAt': past, 'board': 'waiting', 'call': {'who': 'Currys', 'via': 'phone', 'ask': 'Hi'}, 'promises': [{'id': 'p99', 'said': 'Refund by Friday', 'party': 'Currys', 'dueAt': iso(3), 'dueEnd': None, 'allDay': True, 'by': True, 'ref': 'C991', 'status': 'open', 'loggedAt': past}], 'outcome': '', 'events': [{'at': past, 'label': 'Started.'}]},
     'o110': {'id': 'o110', 'mode': 'call', 'title': 'Argos refund', 'baseline': 'Ring them', 'created': past, 'updatedAt': past, 'board': 'waiting', 'facts': {'party': 'Argos', 'ref': '445566'}, 'refs': [{'k': 'order', 'v': '445566', 'at': past, 'src': 'what you wrote', 'st': 'confirmed'}], 'corr': [{'k': 'amount', 'from': '40', 'to': '45', 'at': past, 'how': 'typo', 'src': 'you'}], 'promises': [{'id': 'p110', 'said': 'Refund £45 within 5 working days', 'party': 'Argos', 'dueAt': iso(4), 'dueEnd': None, 'allDay': True, 'by': True, 'ref': '445566', 'status': 'open', 'loggedAt': past}], 'outcome': '', 'events': [{'at': past, 'label': 'Started.'}], 'rev': 3},
     'o124': {'id': 'o124', 'mode': 'fix', 'title': 'Boiler · landlord', 'baseline': 'Ring them', 'created': past, 'updatedAt': past, 'board': 'waiting', 'facts': {'party': 'the landlord'}, 'fix': {'step': 'done', 'item': 'Boiler', 'checks': {}}, 'promises': [{'id': 'p124', 'said': 'Someone will come on Thursday', 'party': 'Landlord', 'dueAt': iso(-2), 'dueEnd': None, 'allDay': True, 'by': False, 'ref': '', 'status': 'missed', 'loggedAt': past, 'closedAt': iso(-1)}, {'id': 'p124b', 'said': 'The plumber will come Monday', 'party': 'Landlord', 'dueAt': iso(5), 'dueEnd': None, 'allDay': True, 'by': False, 'ref': '', 'status': 'open', 'loggedAt': iso(-1)}], 'ledger': [{'id': 'l1', 'type': 'party', 'v': 'the landlord', 'by': 'you', 'src': 'what you wrote when you started', 'at': past, 'st': 'confirmed', 'cby': 'you'}], 'ledgerV': 1, 'outcome': '', 'events': [{'at': past, 'label': 'Started.'}], 'rev': 7},
     'o138': {'id': 'o138', 'mode': 'call', 'title': 'HMRC refund', 'baseline': 'Wait', 'created': past, 'updatedAt': past, 'board': 'waiting', 'facts': {'party': 'HMRC'}, 'promises': [{'id': 'p138', 'said': 'The refund will be processed within 6 weeks', 'party': 'HMRC', 'dueAt': iso(2), 'dueEnd': None, 'allDay': True, 'by': True, 'ref': '', 'status': 'open', 'loggedAt': past, 'prec': 'calc', 'phrase': 'within 6 weeks', 'chk': True}], 'outcome': '', 'events': [{'at': past, 'label': 'Started.'}], 'rev': 4},
     'o141': {'id': 'o141', 'mode': 'call', 'title': 'Evri parcel', 'baseline': 'Wait', 'created': past, 'updatedAt': past, 'board': 'waiting', 'facts': {'party': 'Evri'}, 'promises': [{'id': 'p141', 'said': 'Redeliver sometime next week', 'party': 'Evri', 'dueAt': iso(3), 'dueEnd': iso(8), 'allDay': True, 'by': False, 'win': True, 'ref': '', 'status': 'open', 'loggedAt': past, 'prec': 'window', 'phrase': 'sometime next week'}], 'outcome': '', 'events': [{'at': past, 'label': 'Started.'}], 'rev': 2, 'titleAuto': True},
     'o143': {'id': 'o143', 'mode': 'call', 'title': 'Barclays chargeback', 'baseline': 'Wait', 'created': past, 'updatedAt': past, 'board': 'waiting', 'facts': {'party': 'Barclays'}, 'src143': 'typed', 'promises': [{'id': 'p143', 'said': 'Resolved within 45 days', 'party': 'Barclays', 'dueAt': iso(30), 'dueEnd': None, 'allDay': True, 'by': True, 'ref': '', 'status': 'open', 'loggedAt': past, 'prec': 'calc', 'phrase': 'within 45 days'}], 'att': [{'id': 'att-x1', 'kind': 'check', 'at': iso(2), 'pid': 'p143', 'made': past}], 'deadline': {'date': (today + D(days=9)).isoformat(), 'at': past, 'src': 'start'}, 'outcome': '', 'events': [{'at': past, 'label': 'Started.'}], 'rev': 5},
    }
    pg.evaluate("(rows)=>{var d=JSON.parse(localStorage.getItem('__mockdb'))||{};d.tasks=d.tasks||[];rows.forEach(function(r){d.tasks.push({id:r.id,data:r})});localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}", list(OLD.values()))
    pg.goto('https://sorted.test/'); wait(pg, 1200)
    def snap(): return {x['data']['id']: json.dumps(x['data'], sort_keys=True) for x in dbj().get('tasks', []) if x['data']['id'] in OLD}
    for k in OLD: opencase(k); wait(pg, 300)
    s1 = snap(); ok(len(s1) == len(OLD), 'the older records are all there')
    hm = home()
    ok(all(OLD[k]['title'].split(' ')[0] in hm for k in OLD), 'Home lists every older record')
    for k in OLD: opencase(k); wait(pg, 300)
    pg.reload(); wait(pg, 900); home()
    for k in OLD: opencase(k); wait(pg, 300)
    s2 = snap()
    still = [k for k in OLD if s1.get(k) != s2.get(k)]
    ok(not still, 'after the first load, opening and reloading change nothing: no new revision, history or ledger (%s)' % still)
    ok(all((json.loads(s2[k]).get('rev') or 0) >= 1 for k in OLD), 'each older record has a revision')
    ok(len([e for e in json.loads(s2['o99'])['events']]) == 1, 'the oldest record gained no history lines')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
