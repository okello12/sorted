# v143 (audit pass 2: PASS2-001, 013, 014, 017, 018, 032). The person's attention is its own record (t.att), kept
# apart from what the organisation said:
#   - a check day never overwrites their promise; when it comes, "Not yet" offers another check day or a chase and
#     records no miss and no company score; Home, the case, What Sorted understood, the helper link and the adviser
#     pack all say no day was given;
#   - an estimate or a vague reading that has passed is never "the date they gave"; a firm window that has passed is;
#   - a case saved before v143 with a check day inside its promise is moved to t.att when it loads;
#   - Later makes a reminder row, ended by any real update; repeated Laters ask "Do you still need this?";
#     Tonight after 6pm and weekday choices;
#   - parking deadlines make reminder rows, the card names only reminders that exist, Later can't pass a deadline and
#     Home never says "All clear" with a deadline today;
#   - "after" reminders for all-day visits and "on Friday" promises, a second follow-up, rows of a replaced promise
#     removed by the page; a corrected day keeps the visit's time, New date on a slot asks for the times, a window
#     firmed up is "firmed up".
import os, sys, re, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *

with sync_playwright() as p:
    a = App(p); pg = a.pg
    # ================= PASS2-001: a check day is the person's =================
    c1 = a.start('Evri said my parcel would arrive in the next few days, ref EV123456')
    p0 = a.openp(c1)[0]
    ok(p0.get('prec') == 'approx' and p0.get('phrase'), 'Evri gave no day: Sorted keeps their words as an approximate reading (%s, %s)' % (p0.get('prec'), p0.get('phrase')))
    a.open(c1); pg.click('[data-a=panel][data-p=chk138]'); wait(pg, 300)
    pg.fill('#f-chkday', day(1).isoformat()); pg.click('form[data-f=chk138] button[type=submit]'); wait(pg, 700)
    p1 = a.openp(c1)[0]; chk = a.att(c1, 'check')
    ok(all(p1.get(k) == p0.get(k) for k in ('dueAt', 'dueEnd', 'win', 'by', 'prec', 'phrase')) and not p1.get('chk'), 'choosing a check day leaves their promise exactly as it was')
    ok(len(chk) == 1 and chk[0]['pid'] == p1['id'] and chk[0]['id'].startswith('att-') and L(chk[0]['at']).date() == day(1), 'the check day is its own record in t.att')
    rows = until(pg, lambda: [r for r in a.rows(c1) if r['promise_id'] != p1['id']] and a.rows(c1))
    ok([r['promise_id'] for r in rows] == [chk[0]['id']] and L(rows[0]['send_at']).date() == day(1) and L(rows[0]['send_at']).hour == 9, 'one reminder row, at 9am on the check day, tied to the check day, none for their reading: %s' % [(r['kind'], r['send_at'], r['promise_id']) for r in rows])
    m = a.main()
    ok(('you’ll check on ' + long(day(1))) in m and 'promised it' not in m, 'the case says you’ll check on that day')
    sh = a.share_view(c1)
    ok('THEY PROMISED' not in sh.upper() and 'NO DAY GIVEN' in sh.upper() and 'next few days' in sh, 'the helper link says they gave no day, never “They promised”: %s' % sh[:300].replace('\n', ' | '))
    # the check day comes
    a.task_js(c1, "t.att.forEach(function(x){if(x.kind==='check'&&!x.done&&!x.cancelled){var d=new Date();d.setHours(0,0,0,0);x.at=d.toISOString()}})")
    spot = a.spot_or_row('Evri')
    ok('Your check day' in spot and 'date they gave' not in spot, 'Home: “Your check day”, not “the date they gave”: %s' % spot.replace('\n', ' | ')[:200])
    a.open(c1); u = pg.inner_text('.case117-u') if pg.locator('.case117-u').count() else ''
    if pg.locator('.case117-u').count() and 'When they said' not in u:
        pg.locator('.case117-u summary').first.click(); wait(pg, 300); u = pg.inner_text('.case117-u')
    ok('Their date' not in u, 'What Sorted understood never calls it “Their date”: %s' % u[:300].replace('\n', ' | '))
    n0 = len(a.outcomes()); a.home()
    a.q('Evri', 'home-ans').click(); wait(pg, 700)
    p2 = a.case(c1)['promises'][-1]; lab = a.labels(c1)
    ok(p2['status'] == 'open' and len(a.outcomes()) == n0 and not any(x.startswith('It didn’t happen') for x in lab), '“Not yet” on the check day records no miss and no company score')
    ok(pg.locator('.ny143').count() == 1 and 'Nothing is missed' in pg.inner_text('.ny143') and pg.locator('.ny143 [data-p=call]').count() == 1, 'it offers another check day or a chase')
    nxt = a.att(c1, 'check')
    ok(len(nxt) == 1 and L(nxt[0]['at']).date() == day(3) and any('nothing is recorded as missed' in x for x in lab), 'Sorted will ask again in 3 days; the history says nothing was missed')
    pg.click('.ny143 [data-a=ny143]'); wait(pg, 500)
    ok(L(a.att(c1, 'check')[0]['at']).date() == day(7), '“Ask me in a week instead” moves only the check day')
    pk = a.pack(c1)
    ok('Promises missed' not in pk, 'the adviser pack has no “Promises missed”')
    sh = a.share_view(c1)
    ok('didn’t keep' not in sh and 'THEY PROMISED' not in sh.upper(), 'the helper link lists no broken promise')
    # ================= an estimate that has passed =================
    c2 = a.start('Currys said the £40 refund would come within five working days, order 445566')
    pc = a.openp(c2)[0]
    ok(pc.get('prec') == 'calc', 'within five working days is Sorted’s calculation (%s)' % pc.get('prec'))
    a.past_reading(c2)
    spot = a.spot_or_row('Currys')
    ok('The day Sorted worked out has passed' in spot and 'date they gave' not in spot, 'Home: “The day Sorted worked out has passed”: %s' % spot.replace('\n', ' | ')[:200])
    n0 = len(a.outcomes()); a.q('Currys', 'home-ans').click(); wait(pg, 700)
    ok(a.case(c2)['promises'][-1]['status'] == 'open' and len(a.outcomes()) == n0 and pg.locator('.ny143').count() == 1, '“Not yet” after an estimate passes: still waiting, no miss, no score')
    # ================= a firm window that has passed is theirs =================
    c3 = a.start('Argos said the delivery will come on %s or %s' % (nextwd(0, 2).strftime('%A'), nextwd(1, 2).strftime('%A')))
    pw = a.openp(c3)[0]
    ok(pw.get('prec') == 'window' and pw.get('win'), 'Monday or Tuesday is their window')
    a.past_reading(c3)
    spot = a.spot_or_row('Argos')
    ok('The date they gave has passed' in spot, 'Home: “The date they gave has passed” for a firm window: %s' % spot.replace('\n', ' | ')[:200])
    n0 = len(a.outcomes()); a.q('Argos', 'home-ans').click(); wait(pg, 700)
    st = a.case(c3)['promises'][-1]['status']; oc = a.outcomes()
    ok(st == 'missed' and len(oc) == n0 + 1 and oc[-1]['p_party'] == 'Argos' and oc[-1]['p_outcome'] == 'missed', 'a firm window that has passed, answered “Nobody came”: a miss and a company score')
    pk = a.pack(c3)
    ok('Promises missed' in pk, 'the pack lists a real miss')
    # ================= a case saved before v143 =================
    yest = (datetime.datetime.now() - datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).astimezone().isoformat()
    legacy = {'id': 'leg143a', 'title': 'Evri parcel', 'mode': 'call', 'board': 'waiting', 'created': '2026-01-01T00:00:00Z', 'said': 'Evri said my parcel would come in the next few days',
              'events': [{'at': '2026-10-01T10:00:00Z', 'label': 'Started.'}],
              'promises': [{'id': 'lp1', 'status': 'open', 'said': 'My parcel would come in the next few days', 'party': 'Evri', 'dueAt': yest, 'dueEnd': None, 'allDay': True, 'by': True, 'win': False, 'chk': True, 'prec': 'approx', 'phrase': 'in the next few days', 'loggedAt': '2026-10-01T10:00:00Z'},
                           {'id': 'lp0', 'status': 'missed', 'said': 'It would come in a few days', 'party': 'Evri', 'dueAt': '2026-09-20T00:00:00Z', 'allDay': True, 'by': True, 'chk': True, 'prec': 'approx', 'phrase': 'in a few days', 'closedAt': '2026-09-22T09:00:00Z'}]}
    a.poke("db.tasks.push({id:'leg143a',user_id:'u-me',data:%s})" % json.dumps(legacy)); wait(pg, 800)
    lc = a.case('leg143a'); lp = [x for x in lc['promises'] if x['id'] == 'lp1'][0]
    la = [x for x in lc.get('att', []) if x['kind'] == 'check' and x['pid'] == 'lp1']
    ok(not lp.get('chk') and lp.get('dueAt') is None and lp.get('chkMig') and la and la[0]['at'] == yest, 'an older case: the check day moves to t.att and the promise is left with no day of theirs')
    spot = a.spot_or_row('Evri parcel')
    ok('Your check day' in spot, 'Home asks on the person’s check day: %s' % spot.replace('\n', ' | ')[:160])
    sh = a.share_view('leg143a')
    ok('didn’t keep' not in sh and 'THEY PROMISED' not in sh.upper(), 'a false miss saved by an older version is not shown to a helper as a broken promise')
    ok('Promises missed' not in a.pack('leg143a'), 'nor listed in the pack as a promise missed')
    # ================= PASS2-014: Later makes a reminder, ended by a real update =================
    fri = nextwd(4, 3)
    c4 = a.start('Sky said they would refund £30 by %s, ref SK-77881' % fri.strftime('%A'))
    a.overdue(c4)
    a.q('Sky', 'q-later').click(); wait(pg, 400)
    sh = pg.inner_text('.q130-later')
    ok('Sorted sends you a reminder at the time you choose' in sh, 'Later says a reminder will come (email reminders are on): %s' % sh[-200:])
    wk = [b.get_attribute('data-v') for b in pg.locator('.q130-later [data-a=q-snooze]').all()]
    ok(any(re.match(r'^d\d$', v or '') for v in wk), 'Later offers weekdays as well: %s' % wk)
    pg.locator('.q130-later [data-a=q-snooze][data-v=tomorrow]').click(); wait(pg, 700)
    t4 = a.case(c4); sz = a.att(c4, 'snooze')
    rows = until(pg, lambda: [r for r in a.rows(c4) if r['promise_id'] == (sz[0]['id'] if sz else '')])
    ok(sz and t4['snooze'].get('att') == sz[0]['id'] and len(rows) == 1 and L(rows[0]['send_at']).date() == day(1) and L(rows[0]['send_at']).hour == 8, 'Later → tomorrow morning: one reminder row at 8am tomorrow, tied to the Later')
    ok(all(t4['promises'][-1].get(k) == a.case(c4)['promises'][-1].get(k) for k in ('dueAt', 'status')) and t4['promises'][-1]['status'] == 'open', 'Later never changes their promise')
    a.open(c4); pg.click('.q130-line [data-a=panel][data-p=later]'); wait(pg, 400); pg.click('[data-a=q-snooze][data-v=tomorrow]'); wait(pg, 600)
    a.open(c4); pg.click('.q130-line [data-a=panel][data-p=later]'); wait(pg, 400)
    ok(pg.locator('.snz143').count() == 1 and 'Do you still need it?' in pg.inner_text('.snz143'), 'putting it off again asks “Do you still need it?”')
    lab = a.labels(c4)
    ok(any('You put this off again' in x and '2 times now' in x for x in lab) and len(set(x for x in lab if 'come back to this' in x or 'put this off' in x)) == len([x for x in lab if 'come back to this' in x or 'put this off' in x]), 'repeated Laters leave different history lines: %s' % [x for x in lab if 'off' in x or 'come back' in x])
    pg.click('.q130-later [data-a=q-close]'); wait(pg, 300)
    live = a.att(c4, 'snooze')[0]['id']
    pg.click('.q130-line [data-a=panel][data-p=changed]'); wait(pg, 300); pg.click('[data-a=sc-contacted]'); wait(pg, 700)
    ok(not a.case(c4).get('snooze') and not a.att(c4, 'snooze') and not [r for r in a.rows(c4) if r['promise_id'] == live], 'a real update ends Later and removes its reminder row')
    # Tonight after 6pm
    a.open(c4)
    p3 = a.ctx.new_page(); p3.on('pageerror', lambda e: errs.append(str(e)))
    p3.clock.set_fixed_time(datetime.datetime.combine(today, datetime.time(18, 30)))
    p3.goto('https://sorted.test/?task=%s' % c4); wait(p3, 800); p3.click('.q130-line [data-a=panel][data-p=later]'); wait(p3, 400)
    tonight = [b.inner_text() for b in p3.locator('.q130-later [data-a=q-snooze]').all()]; p3.close()
    ok(tonight and tonight[0].startswith('Tonight, 9pm'), 'after 6pm, Later still offers Tonight (9pm): %s' % tonight)
    # ================= PASS2-013: parking deadlines =================
    c6 = a.parking(-12)   # the £65 price ends tomorrow
    t6 = a.case(c6)
    pa = [x for x in t6.get('att', []) if x['kind'] == 'remind']
    rows = until(pg, lambda: [r for r in a.rows(c6) if (r['promise_id'] or '').startswith('att-pk-')])
    ok(pa and rows and any(L(r['send_at']).date() <= day(1) for r in rows), 'a parking notice: reminder rows before the cheaper price ends, tied to a deadline record: %s' % [(r['kind'], r['send_at'][:16], r['promise_id']) for r in rows])
    a.open(c6); card = pg.inner_text('.pk-card') if pg.locator('.pk-card').count() else ''
    first = sorted(rows, key=lambda r: r['send_at'])[0]
    fd = L(first['send_at']); fw = '%s %d %s' % (fd.strftime('%A'), fd.day, fd.strftime('%B'))
    ok('Sorted will remind you on ' + fw in card, 'the card names the reminders that exist (%s): %s' % (fw, card[:400].replace('\n', ' | ')))
    a.home(); a.q('Southwark', 'q-later').click(); wait(pg, 400)
    lt = pg.inner_text('.q130-later')
    ok('The reminders already set for it still come' in lt and 'won’t bring this back after it' in lt, 'Later says the deadline reminders still come, because they exist')
    dis = [b.get_attribute('data-v') for b in pg.locator('.q130-later [data-a=q-snooze][disabled]').all()]
    ok('weekend' in dis or any(v.startswith('d') for v in dis), 'times after the deadline can’t be chosen: %s' % dis)
    pg.fill('form[data-f=qlater] input[type=date]', day(4).isoformat()); pg.click('form[data-f=qlater] button[type=submit]'); wait(pg, 500)
    ok('after the deadline' in pg.inner_text('.q130-later') and not a.case(c6).get('snooze'), 'a day after the deadline is refused')
    ok(pg.locator('.q130-acts [data-a=q-paid]').count() >= 1, '“Already paid” is a quick answer on the parking notice')
    # a guest with no way to be reminded is never told a reminder exists
    g = App(p, email=False); gp = g.pg
    c8 = g.parking(-12, issuer='Lambeth Council', ref='LB11223344')
    g.open(c8); card = gp.inner_text('.pk-card') if gp.locator('.pk-card').count() else ''
    ok('Sorted will remind you' not in card and 'until reminders are on' in card and not g.rows(c8), 'no reminders possible: the card doesn’t claim one, and says how to get one')
    g.home(); g.q('Lambeth', 'q-later').click(); wait(gp, 400)
    lt = gp.inner_text('.q130-later')
    ok('still come' not in lt and 'can’t remind you outside the app' in lt, 'nor does Later')
    if gp.locator('[data-a=q-pay]').count() == 0 or True:
        pass
    g.close()
    # deadline today: Later can't hide it
    a3 = App(p); pg3 = a3.pg
    c7 = a3.parking(-13, issuer='Camden Council', ref='CU87654321')
    a3.home(); a3.q('Camden', 'q-later').click(); wait(pg3, 400)
    ok('The deadline is today' in pg3.inner_text('.q130-later'), 'on the deadline day, Later says the case stays at the top')
    en = [b.get_attribute('data-v') for b in pg3.locator('.q130-later [data-a=q-snooze]:not([disabled])').all()]
    if en: pg3.locator('.q130-later [data-a=q-snooze][data-v=%s]' % en[0]).click(); wait(pg3, 600)
    else: a3.task_js(c7, "t.snooze={until:new Date(Date.now()+3*3600e3).toISOString(),at:new Date().toISOString()}")
    a3.home(); hm = a3.main()
    ok('All clear' not in hm and 'Nothing needs you right now' not in hm and 'Camden' in hm.split('Later')[0], 'Home never says “All clear” with a deadline today; the notice stays at the top')
    a3.close()
    # ================= PASS2-018: after reminders =================
    fri2 = nextwd(4, 2)
    c9 = a.start('My landlord said the plumber will come on %s %d %s' % (fri2.strftime('%A'), fri2.day, fri2.strftime('%B')))
    rows = sorted(until(pg, lambda: len([r for r in a.rows(c9) if r['kind'] == 'after']) >= 2 and a.rows(c9)) or [], key=lambda r: r['send_at'])
    af = [L(r['send_at']) for r in rows if r['kind'] == 'after']
    ok(len(af) == 2 and af[0].date() == fri2 and af[0].hour == 19 and af[1].date() == fri2 + datetime.timedelta(days=2), 'an all-day visit gets “Did they come?” that evening and a second follow-up two days later: %s' % [(r['kind'], r['send_at'][:16]) for r in rows])
    c10 = a.start('Currys said they would call me back on %s %d %s' % (fri2.strftime('%A'), fri2.day, fri2.strftime('%B')))
    af = until(pg, lambda: [L(r['send_at']) for r in a.rows(c10) if r['kind'] == 'after'])
    ok(af and min(af).date() == fri2 + datetime.timedelta(days=1) and min(af).hour == 9, '“on Friday” gets an after reminder the next morning: %s' % af)
    a.open(c10); m = a.main()
    old = a.openp(c10)[0]['id']
    pg.click('.q130-line [data-a=panel][data-p=changed]'); wait(pg, 300); pg.click('.q130-changed button:has-text("They gave me a new date")'); wait(pg, 300)
    pg.fill('form[data-f=qdate] input[type=date]', (fri2 + datetime.timedelta(days=3)).isoformat()); pg.click('form[data-f=qdate] button[type=submit]'); wait(pg, 900)
    ok(not [r for r in a.rows(c10) if r['promise_id'] == old] and [r for r in a.rows(c10) if r['promise_id'] == a.openp(c10)[0]['id']], 'a replaced promise’s unsent rows are removed by the page; the new one has its own')
    # ================= PASS2-017: times kept, slots asked, windows firmed up =================
    tue = nextwd(1, 2)
    c11 = a.start('BT said the engineer would come on %s %d %s between 8am and 12pm, ref BT556677' % (tue.strftime('%A'), tue.day, tue.strftime('%B')))
    p11 = a.openp(c11)[0]
    ok(not p11.get('allDay') and L(p11['dueAt']).hour == 8, 'a timed visit (%s)' % p11.get('dueAt'))
    a.open(c11); pg.click('.q130-line [data-a=panel][data-p=changed]'); wait(pg, 300); pg.click('.q130-changed button:has-text("The appointment changed")'); wait(pg, 300)
    ok(pg.locator('form[data-f=qdate] input[name=qfrom]').count() == 1 and pg.input_value('form[data-f=qdate] input[name=qfrom]') == '08:00' and pg.input_value('form[data-f=qdate] input[name=qto]') == '12:00', 'New date on a slot shows the times, so a different slot can be given')
    nd = tue + datetime.timedelta(days=6)
    pg.fill('form[data-f=qdate] input[type=date]', nd.isoformat()); pg.fill('form[data-f=qdate] input[name=qfrom]', '13:00'); pg.fill('form[data-f=qdate] input[name=qto]', '17:00')
    pg.click('form[data-f=qdate] button[type=submit]'); wait(pg, 900)
    p11 = a.openp(c11)[0]
    ok(L(p11['dueAt']).date() == nd and L(p11['dueAt']).hour == 13 and L(p11['dueEnd']).hour == 17, 'the new slot is 1 to 5pm, not the old 8 to 12')
    aft = until(pg, lambda: [L(r['send_at']) for r in a.rows(c11) if r['kind'] == 'after' and r['promise_id'] == p11['id']])
    ok(aft and min(aft).hour == 17 and min(aft).minute == 15, 'its “Did they come?” is at 5:15pm')
    # a correction of the day keeps the time
    nd2 = nd + datetime.timedelta(days=1)
    a.open(c11); pg.click('.now137-add'); wait(pg, 300)
    pg.fill('#f-paste', 'Sorry, I meant %s not %s' % (nd2.strftime('%A'), nd.strftime('%A'))); pg.locator('form[data-f=paste] button[type=submit]').first.click(); wait(pg, 700)
    if pg.locator('[data-a=corr-yes]').count(): pg.click('[data-a=corr-yes]'); wait(pg, 700)
    p11 = a.openp(c11)[0]
    ok(L(p11['dueAt']).date() == nd2 and L(p11['dueAt']).hour == 13 and p11.get('dueEnd') and L(p11['dueEnd']).hour == 17 and not p11.get('allDay'), 'correcting the day keeps the visit’s time: %s to %s' % (p11.get('dueAt'), p11.get('dueEnd')))
    # a window firmed up
    c12 = a.start('Argos said the sofa will come on %s or %s' % (nextwd(2, 2).strftime('%A'), nextwd(3, 2).strftime('%A')))
    thu = nextwd(3, 2)
    a.open(c12); pg.click('.q130-line [data-a=panel][data-p=changed]'); wait(pg, 300); pg.click('.q130-changed button:has-text("The appointment changed"), .q130-changed button:has-text("They gave me a new date")'); wait(pg, 300)
    pg.fill('form[data-f=qdate] input[type=date]', thu.isoformat()); pg.click('form[data-f=qdate] button[type=submit]'); wait(pg, 800)
    p12 = a.openp(c12)[0]; lab = a.labels(c12)
    ok(L(p12['dueAt']).date() == thu and not p12.get('by') and not p12.get('win') and p12.get('prec') == 'day', 'a window firmed up to %s is that day, not “by” it' % thu.strftime('%A'))
    ok(any(x.startswith('They firmed up the day') for x in lab) and not any(x.startswith('They changed the date') for x in lab), 'the history says they firmed it up, not that they changed the date')
    # ================= 032: It arrived before the due day =================
    c13 = a.start('Amazon said the refund of £12 will arrive by %s' % (today + datetime.timedelta(days=9)).strftime('%d %B'))
    a.home()
    eb = pg.locator('.q143-early [data-a=q-kept][data-qid="%s"]' % c13)
    ok(eb.count() == 1 and 'It arrived' in eb.inner_text(), '“It arrived” is one tap from Waiting, before the due day')
    eb.click(); wait(pg, 700)
    ok(a.case(c13)['promises'][-1]['status'] == 'kept' and pg.locator('[data-a=q-undo]').count() >= 1, 'it records it, with Undo')
    a.close()
finish()
