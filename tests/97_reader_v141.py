# v141 (the reader audit of 6 October 2026). Each line is a sentence the reader used to get wrong:
#   - "said yesterday it would come tomorrow" is tomorrow; a told day only counts where it hangs on the telling
#     ("My boiler broke 3 days ago" isn't); "said on Monday … within 5 working days" counts from Monday; a past date beside
#     a duration is when it was ordered or said, never the deadline;
#   - times: "07:00", "between 7 and 11", "7.30-9.30" and "8-12pm" are the morning; money ("14.50") is not a time;
#     "14.10.26" is a date; "1/2 of it" and "24/7" are not dates; "4 Mayfield Road" is not May;
#   - "a week on Monday", "Monday week", "a week today", "the day after tomorrow"; "between Monday and Wednesday",
#     "Mon-Wed next week" and pasted "in 7-10 working days" are windows; number words, "a fortnight", "2-3 weeks",
#     "within 2 hours"; "last Tuesday" is in the past, even on a Tuesday;
#   - no promise from: "they never said", "not until Friday", a question, the rent being due, money taken or charged,
#     cut-offs, eviction, bailiffs; but "they said they'd pay the refund by Friday" and "they said I'd get a refund" are;
#   - a pasted update that already happened ("The refund arrived this morning") proposes "Sounds like it happened",
#     never a new promise; "in progress" is not kept; "came but couldn't fix it" and "£40 of the £89" are only partly;
#   - corrections never turn a sentence into a thing; "X not Y" takes X; "it's my landlord" is who; phone numbers are not
#     references; dates, years and floors are not references; "Marks and Spencer" is M&S; safety reads "won't fire"
#     and "water near the electrics" correctly.
import os, sys, datetime, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
today = datetime.date.today(); D = datetime.timedelta
ymd = lambda d: d.isoformat()
def nxt(wd, skip=False):            # the next weekday (Mon=0), today counts unless skip
    k = (wd - today.weekday()) % 7
    return today + D(days=k or (7 if skip else 0))
def prev(wd, strict=False):         # the most recent weekday, today counts unless strict
    k = (today.weekday() - wd) % 7
    return today - D(days=k or (7 if strict else 0))
MON = ['January','February','March','April','May','June','July','August','September','October','November','December']
dm = lambda d: '%d %s' % (d.day, MON[d.month - 1])
P = """function P(p){if(!p)return null;var a=new Date(p.dueAt),e=p.dueEnd?new Date(p.dueEnd):null,f=function(d){return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2)},h=function(d){return ('0'+d.getHours()).slice(-2)+':'+('0'+d.getMinutes()).slice(-2)};
  return {day:f(a),from:p.allDay?'':h(a),end:e?f(e):'',to:e&&!p.allDay?h(e):'',win:!!p.win,prec:p.prec||'',phrase:p.phrase||'',told:p.told||'',party:p.party||'',past:!!p.past,said:p.said||''}}"""
RC = "(xs)=>{" + P + ";var r=window.__read;return xs.map(function(t){return P(r.readCase(t,r.caseFacts(t)))})}"
SM = "(xs)=>{" + P + ";var r=window.__read;return xs.map(function(t){return P(r.sugFromMessage(t,null,r.caseFacts(t)))})}"
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/reader'), lambda r: r.fulfill(path=HERE + '/tests/out/reader.html', content_type='text/html'))
    ctx.route(lambda u: u.startswith('https://sorted.test/') and not u.startswith('https://sorted.test/reader'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/reader'); wait(pg, 500)
    rc = lambda xs: pg.evaluate(RC, xs)
    sm = lambda xs: pg.evaluate(SM, xs)
    wd = lambda d, n: pg.evaluate("([t,n])=>{var r=window.__read,a=t.split('-').map(Number);return r.ymdL(r.wdFrom(new Date(a[0],a[1]-1,a[2]),n))}", [ymd(d), n])
    FRI, THU, MONd, TUE = nxt(4), nxt(3), nxt(0), nxt(1)
    # 1 yesterday is when they said it
    r = rc(['Evri said yesterday it would come tomorrow', 'Sky said yesterday that the engineer would come Thursday', 'They told me today they would come tomorrow'])
    ok(r[0] and r[0]['day'] == ymd(today) and not r[0]['past'], '“said yesterday it would come tomorrow” is today (v142: tomorrow counted from yesterday): %s' % r[0])
    ok(r[1] and r[1]['day'] == ymd(THU) and not r[1]['past'], '“said yesterday … Thursday” is Thursday: %s' % r[1])
    ok(r[2] and r[2]['day'] == ymd(today + D(days=1)), '“told me today … tomorrow” is tomorrow: %s' % r[2])
    # 2 times
    T = [('They said the engineer will come between 07:00 and 13:00 on Friday', '07:00', '13:00'), ("They said they'd deliver on Friday 07:00 - 19:00", '07:00', '19:00'),
         ('They said the engineer would come Friday between 07:30 and 09:30', '07:30', '09:30'), ("They said they'd come on Friday between 7 and 11", '07:00', '11:00'),
         ("They said they'd come on Friday 7.30-9.30", '07:30', '09:30'), ('They said they would come Friday 8-12pm', '08:00', '12:00'),
         ('They said they would come Friday between 8-12pm', '08:00', '12:00'), ("They said they'd come on Friday between 1 and 3", '13:00', '15:00')]
    for (s, a, z), x in zip(T, rc([t[0] for t in T])):
        ok(x and x['day'] == ymd(FRI) and x['from'] == a and x['to'] == z, '%r is Friday %s to %s: %s' % (s, a, z, x and (x['from'], x['to'])))
    # 3, 4, 5 the told day
    r = rc(["My boiler broke 3 days ago, British Gas said they'll come within 2 days", "British Gas told me today they'll come within 2 days"])
    ok(r[0] and r[0]['day'] == ymd(today + D(days=2)) and not r[0]['told'] and not r[0]['past'], '“broke 3 days ago” is not when they said it: %s' % r[0])
    ok(r[1] and r[1]['day'] == ymd(today + D(days=2)) and not r[1]['told'], '“told me today … within 2 days” counts from today: %s' % r[1])
    m0, f0 = prev(0), prev(4)
    r = rc(["They said on Monday they'd refund within 5 working days", 'They told me on Friday the refund would take 5 working days'])
    ok(r[0] and r[0]['told'] == ymd(m0) and r[0]['prec'] == 'calc' and r[0]['day'] == wd(m0, 5), '“said on Monday … within 5 working days” counts from Monday %s: %s' % (m0, r[0]))
    ok(r[1] and r[1]['told'] == ymd(f0) and r[1]['day'] == wd(f0, 5), '“told me on Friday … would take 5 working days” counts from Friday %s: %s' % (f0, r[1]))
    od, sd = today - D(days=8), today - D(days=5)
    r = rc(['They told me yesterday the refund for my %s order would take 5 working days' % dm(od), 'Currys said on %s that the refund would take 10 working days' % dm(sd)])
    ok(r[0] and r[0]['told'] == ymd(today - D(days=1)) and r[0]['day'] == wd(today - D(days=1), 5), 'the order date is not the deadline: %s' % r[0])
    ok(r[1] and r[1]['told'] == ymd(sd) and r[1]['day'] == wd(sd, 10) and r[1]['party'] == 'Currys', '“said on %s … 10 working days” counts from that day: %s' % (dm(sd), r[1]))
    # 6 their payment is their promise; yours is a demand
    r = rc(["They said they'd pay the refund by Friday", 'Currys promised to pay £50 compensation by Friday', 'The insurer said they will pay the claim by %s' % dates.ahead(14)['dm'],
            "They said they'll pay it into my account by Thursday", 'You must pay £70 by Friday', 'I have to pay the fine by Friday'])
    ok(all(r[:4]) and r[1]['party'] == 'Currys' and r[3]['day'] == ymd(THU), 'a company paying you is their promise: %s' % [x and x['day'] for x in r[:4]])
    ok(r[4] is None and r[5] is None, 'paying is still a demand on you when you pay')
    # 7, 8, 15, 18 not promises
    NOT = ['They never said they would refund by Friday', "They never told me they'd come on Friday", 'The landlord said the rent is due on Friday',
           'British Gas said they will take £120 from my account on Friday', "The bank said they'd charge me £25 on Friday", 'Thames Water said they would cut off the water on Friday',
           "The landlord said he's going to evict me by the end of the month", 'The landlord said they will send a bailiff on Friday', 'The debt collector said they will visit on Friday',
           'The landlord said the rent goes up from 1 November', 'They said they will not be able to come until Friday', "They said they can't come before Friday",
           'When they said Friday did they mean this Friday?']
    for s, x in zip(NOT, rc(NOT)): ok(x is None, 'no promise: %r -> %s' % (s, x))
    ok(rc(["Currys said they'd stop charging me twice by Friday"])[0] is not None, 'stopping a charge is still their promise')
    # 9, 10, 11 numbers that aren't dates or times
    d8 = today + D(days=8)
    r = rc(["The engineer said he'd come to 4 Mayfield Road tomorrow between 8 and 12", "The plumber said he'd come to 12 Market Street on Friday", 'Currys said they will refund 14.50 by Friday',
            "They said they'd come on %02d.%02d.%02d" % (d8.day, d8.month, d8.year % 100), "They said they'd come on %d.%d.%d" % (d8.day, d8.month, d8.year), "They said they'd come on %d-%d-%d" % (d8.day, d8.month, d8.year),
            'They said they would refund 1/2 of it by Friday', "They said support is 24/7 and they'd call me back on Friday"])
    ok(r[0] and r[0]['day'] == ymd(today + D(days=1)) and r[0]['from'] == '08:00' and r[0]['to'] == '12:00', '“4 Mayfield Road tomorrow” is tomorrow, not 4 May: %s' % r[0])
    ok(r[1] and r[1]['day'] == ymd(FRI), '“12 Market Street on Friday” is Friday, not 12 March: %s' % r[1])
    ok(r[2] and r[2]['day'] == ymd(FRI) and not r[2]['from'], '“refund 14.50 by Friday” has no time: %s' % r[2])
    ok(all(x and x['day'] == ymd(d8) and not x['from'] for x in r[3:6]), 'dotted and dashed dates are dates: %s' % [x and (x['day'], x['from']) for x in r[3:6]])
    ok(r[6] and r[6]['day'] == ymd(FRI) and r[7] and r[7]['day'] == ymd(FRI), '“1/2 of it” and “24/7” are not dates: %s %s' % (r[6], r[7]))
    # 12, 13 weeks and windows
    r = rc(["They said they'd come a week on Monday", "They said they'd come Monday week", "They said they'd come a week today", "They said they'd come a week tomorrow", "They said they'd come the day after tomorrow"])
    want = [nxt(0) + D(days=7), nxt(0) + D(days=7), today + D(days=7), today + D(days=8), today + D(days=2)]
    ok([x and x['day'] for x in r] == [ymd(w) for w in want], 'a week on Monday, Monday week, a week today, a week tomorrow, the day after tomorrow: %s' % [x and x['day'] for x in r])
    nm = today + D(days=(7 - today.weekday()) or 7)
    r = rc(["They said they'd come between Monday and Wednesday", "They said they'd come Mon-Wed next week"])
    ok(r[0] and r[0]['win'] and r[0]['prec'] == 'window' and r[0]['day'] == ymd(nxt(0)) and r[0]['end'] == ymd(nxt(0) + D(days=2)), '“between Monday and Wednesday” is a window: %s' % r[0])
    ok(r[1] and r[1]['win'] and r[1]['day'] == ymd(nm) and r[1]['end'] == ymd(nm + D(days=2)), '“Mon-Wed next week” is a window next week: %s' % r[1])
    # 14 pasted windows
    r = sm(['Your new card will arrive in 7-10 working days.', 'Your order will arrive sometime next week.', 'Your refund will be with you within 3-5 working days.'])
    ok(r[0] and r[0]['win'] and r[0]['day'] == wd(today, 7) and r[0]['end'] == wd(today, 10) and r[0]['prec'] == 'calc', 'a pasted “in 7-10 working days” is a window: %s' % r[0])
    ok(all(x and x['win'] for x in r[1:]), 'pasted “sometime next week” and “within 3-5 working days” are windows')
    # 16, 17 the promise is theirs
    r = rc(['They said I would get a refund by Friday', "They said I'll get a call back on Friday", "They told me I'd receive a letter within 10 working days", "Hi, it's Dave the plumber. I'll be round Thursday morning"])
    ok(r[0] and r[0]['day'] == ymd(FRI) and r[1] and r[1]['day'] == ymd(FRI) and r[2] and r[2]['day'] == wd(today, 10), '“they said I’d get …” is their promise')
    ok(r[3] and r[3]['party'] == 'Dave' and r[3]['day'] == ymd(THU) and r[3]['from'] == '08:00', 'a message from Dave the plumber is Dave’s promise: %s' % r[3])
    r = sm(["We tried to deliver your parcel today. We'll try again tomorrow."])
    ok(r[0] and r[0]['day'] == ymd(today + D(days=1)), 'the attempt today is skipped; the next try is tomorrow: %s' % r[0])
    # 23, 24 number words and last Tuesday
    r = rc(['They said they would refund me within a fortnight', 'They said they would refund me within 2-3 weeks', 'They said they would refund me within five to seven working days',
            'They said they would refund within eight working days', 'They said they would refund within twelve days', 'They said they would call within 2 hours'])
    ok(r[0] and r[0]['day'] == ymd(today + D(days=14)) and r[0]['prec'] == 'calc' and r[0]['phrase'] == 'within a fortnight', 'a fortnight is 14 days: %s' % r[0])
    ok(r[1] and r[1]['win'] and r[1]['day'] == ymd(today + D(days=14)) and r[1]['end'] == ymd(today + D(days=21)), '2-3 weeks is a window: %s' % r[1])
    ok(r[2] and r[2]['win'] and r[2]['day'] == wd(today, 5) and r[2]['end'] == wd(today, 7) and r[2]['phrase'] == 'within five to seven working days', 'five to seven working days: %s' % r[2])
    ok(r[3] and r[3]['day'] == wd(today, 8) and r[4] and r[4]['day'] == ymd(today + D(days=12)), 'eight working days, twelve days')
    ok(r[5] and r[5]['prec'] == 'calc' and r[5]['from'] and r[5]['phrase'] == 'within 2 hours', 'within 2 hours has a time: %s' % r[5])
    r = rc(['Evri said they would deliver my parcel last Tuesday but nothing came', 'They said they would deliver last Tuesday'])
    ok(r[0] and r[0]['day'] == ymd(prev(1, True)) and r[0]['past'], '“last Tuesday … but nothing came” is a missed promise for %s: %s' % (prev(1, True), r[0]))
    ok(r[1] is None, '“would deliver last Tuesday” with no miss is not a promise for today')
    # 20 corrections
    cur = {"item": "Washing machine", "party": "British Gas", "ref": "AB123", "amount": 40, "dueAt": (datetime.datetime.combine(FRI, datetime.time()) ).isoformat(), "allDay": True}
    C = lambda t, c=cur: pg.evaluate("([c,s])=>{var r=__read.corrRead(c,s);return r?{k:r.k,from:String(r.from),to:String(r.to)}:null}", [c, t])
    for s in ['Sorry, I meant to say thank you', 'Actually I spoke to Sarah', 'sorry wrong case', 'Actually, it\'s urgent now', 'Actually, I paid £40 not £45', 'Sorry the ref is 07700 900123']:
        x = C(s); ok(not x or x['k'] not in ('item', 'amount', 'ref'), 'no nonsense correction from %r: %s' % (s, x))
    x = C('Sorry, it\'s not British Gas, it\'s my landlord'); ok(x and x['k'] == 'party' and x['to'] == 'Landlord', '“not British Gas, it’s my landlord” is who: %s' % x)
    x = C('Actually they said Friday the 16th', dict(cur, dueAt='2026-10-09T00:00:00')); ok(x and x['k'] == 'date', '“Actually they said Friday the 16th” is a date: %s' % x)
    x = C('£45 not £40'); ok(x and x['k'] == 'amount' and x['to'] == '45', '“£45 not £40” takes £45')
    x = C('AB132 not AB123'); ok(x and x['k'] == 'ref' and x['to'] == 'AB132', '“AB132 not AB123” takes AB132')
    x = C('Sorry, it\'s the dishwasher not the washing machine'); ok(x and x['k'] == 'item' and x['to'] == 'Dishwasher', 'a real thing is still corrected')
    # 21 references and names
    R = pg.evaluate("(xs)=>xs.map(function(t){var r=window.__read,f=r.caseFacts(t);return {ref:f.ref,party:f.party,refs:r.refsRead(t).map(function(x){return x.v})}})",
                    ['Your case number: CAS-12345-X1Y2', 'Booking 14/10/2026 they will call Friday', 'claim reference 2026', 'Reference: 1st floor', 'Marks and Spencer said they would refund me by Friday'])
    ok(R[0]['ref'] == 'CAS-12345-X1Y2', 'the whole case number: %s' % R[0])
    ok(not R[1]['ref'] and not R[1]['refs'] and not R[2]['ref'] and not R[3]['ref'], 'a date, a year and a floor are not references: %s' % R[1:4])
    ok(R[4]['party'] == 'M&S', 'Marks and Spencer is M&S')
    r = rc(['Policy number PX-99821 Aviva will call me on Friday'])
    ok(r[0] and r[0]['party'] == 'Aviva', 'a reference is not part of the name: %s' % r[0])
    # 22 safety
    U = pg.evaluate("(xs)=>xs.map(function(t){return window.__read.looksUnsafe(t)})", ["no gas smell, the boiler just won't fire", 'water leaking near the electrics', 'I can smell gas', 'the socket is crackling', 'no smoke or burning smell'])
    ok(U == [False, True, True, True, False], '“won’t fire” is not a fire, water near the electrics is a danger: %s' % U)

    # ================= 19 the paste panel =================
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    case = lambda cid: [c for c in cases() if c['id'] == cid][0]
    tap = lambda a: (pg.locator('.tab129 [data-a=%s]' % a).click(), wait(pg, 500))
    def start(text):
        tap('new-case'); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
        if pg.locator('[data-a=nudge-skip]').count(): pg.click('[data-a=nudge-skip]'); wait(pg, 300)
        return cases()[-1]['id']
    def paste(cid, text):
        pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700)
        pg.locator('[data-a=panel][data-p=paste]').first.evaluate('e=>e.click()'); wait(pg, 300); pg.fill('#f-paste', text); pg.click('form[data-f=paste] button[type=submit]'); wait(pg, 700)
        c = case(cid); m = pg.inner_text('main')
        if pg.locator('[data-a=out-no]').count(): pg.click('[data-a=out-no]'); wait(pg, 400)
        if pg.locator('[data-a=sug-no]').count(): pg.click('[data-a=sug-no]'); wait(pg, 400)
        return c, m
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')")
    pg.goto('https://sorted.test/#start'); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    c1 = start('Currys said they would refund my £89 by Friday')
    p0 = [q for q in case(c1)['promises'] if q['status'] == 'open']
    ok(len(p0) == 1, 'the refund case has its promise')
    for s, want in [('The refund arrived this morning', 'Sounds like it happened'), ('Refund came through on Monday', 'Sounds like it happened'),
                    ('Engineer came this morning and fixed it', 'Sounds like it happened'), ('They called me this afternoon', None), ('Nothing yet, I will call them tomorrow', None),
                    ('Your refund is in progress', None), ('The engineer came but couldn\'t fix it', 'only part of it happened'),
                    ('They refunded £40 but the rest is still missing', 'only part of it happened'), ('They paid £40 of the £89', 'only part of it happened')]:
        c, m = paste(c1, s)
        sp = c.get('sugP') and not c.get('sugDone')
        ok(not sp, 'no new promise proposed from %r: %s' % (s, c.get('sugP')))
        if want: ok(want in m, '%r proposes “%s”' % (s, want))
        else: ok('Sounds like it happened' not in m and 'only part of it happened' not in m, '%r proposes no outcome' % s)
    op = [q for q in case(c1)['promises'] if q['status'] == 'open']
    ok(len(op) == 1 and op[0]['id'] == p0[0]['id'] and op[0]['dueAt'] == p0[0]['dueAt'], 'the real promise is untouched')
    c, m = paste(c1, 'They emailed to say the refund will now be paid on %s' % dates.ahead(9)['long'])
    ok(c.get('sugP') or c.get('corrP'), 'an update that says what happens next is still read')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
