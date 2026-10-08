# v143 (audit pass 2: PASS2-002, 032). No false misses from natural taps:
#   - a pasted "hasn't come yet" before the promise is due proposes nothing; once due, the button says
#     "Record it as missed"; for a promise with no firm day it says "Still waiting" and records no miss;
#   - a lock-screen answer waits for one tap on the case it was about ("Not now" records nothing); the banner names the
#     notification; an email answer still records straight away and says "email";
#   - Home answers have Undo for two minutes (status, history and the company total restored), and "That was a
#     mistake" afterwards;
#   - a company score only for an organisation's dated promise: never for Sorted's calculation;
#   - "Already paid" on a parking notice is one tap to the payment record.
import os, sys, re, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *

def paste(a, cid, text):
    pg = a.pg; a.open(cid); pg.click('.now137-add'); wait(pg, 300)
    pg.fill('#f-paste', text); pg.locator('form[data-f=paste] button[type=submit]').first.click(); wait(pg, 800)

with sync_playwright() as p:
    a = App(p); pg = a.pg
    # ================= a pasted update before and after the due date =================
    due = day(10)
    c1 = a.start('Argos said the refund of £20 will arrive by %d %s, order 9911' % (due.day, due.strftime('%B')))
    p1 = a.openp(c1)[0]
    ok(p1.get('prec') == 'day', 'Argos gave a day (%s)' % p1.get('prec'))
    n0 = len(a.outcomes())
    paste(a, c1, 'The Argos refund hasn’t come yet')
    m = a.main()
    ok('Sounds like it didn’t happen' not in m and a.openp(c1) and len(a.outcomes()) == n0, 'before the due date, “hasn’t come yet” proposes nothing and changes nothing')
    ok(not a.case(c1).get('outP'), 'no proposal is stored')
    a.overdue(c1)
    paste(a, c1, 'Still nothing from Argos')
    m = a.main()
    ok('Sounds like it didn’t happen' in m and pg.locator('[data-a=out-yes]').inner_text() == 'Record it as missed', 'once due, the proposal’s button says what it does: “Record it as missed”')
    pg.click('[data-a=out-yes]'); wait(pg, 700)
    oc = a.outcomes()
    ok(a.case(c1)['promises'][-1]['status'] == 'missed' and len(oc) == n0 + 1 and oc[-1]['p_outcome'] == 'missed', 'tapping it records the miss and the company total')
    # once due, a part payment is proposed as "only partly"; before, it isn't
    c1b = a.start('Boots said they would refund £20 by %d %s, order 7788' % (day(6).day, day(6).strftime('%B')))
    paste(a, c1b, 'They paid £10 of the £20')
    ok('only part of it happened' not in a.main() and a.openp(c1b), 'before the due date a part payment proposes nothing')
    a.overdue(c1b); paste(a, c1b, 'Boots have paid £10 of the £20 so far')  # different words: the same message twice is recognised (v143 B1)
    ok('only part of it happened' in a.main(), 'once due, it proposes “only part of it happened”')
    # no firm day: "Still waiting", never a miss
    c2 = a.start('Evri said the parcel would arrive in the next few days, ref EV998877')
    a.past_reading(c2)
    n0 = len(a.outcomes())
    paste(a, c2, 'It hasn’t arrived')
    ok(pg.locator('[data-a=out-yes]').count() == 1 and pg.locator('[data-a=out-yes]').inner_text() == 'Still waiting' and 'nothing would be missed' in a.main(), 'with no firm day, the proposal says “Still waiting”')
    pg.click('[data-a=out-yes]'); wait(pg, 700)
    ok(a.case(c2)['promises'][-1]['status'] == 'open' and len(a.outcomes()) == n0 and pg.locator('.ny143').count() == 1, 'tapping it records no miss and offers a check day or a chase')
    # ================= lock-screen answers wait for a tap =================
    c3 = a.start('Currys said they would refund £89 by %d %s, order 445566' % (day(5).day, day(5).strftime('%B')))
    a.overdue(c3); pid = a.openp(c3)[0]['id']; n0 = len(a.outcomes())
    a.pg.goto('https://sorted.test/?task=%s&src=push&ans=no&p=%s' % (c3, pid)); wait(pg, 1200)
    ok(pg.locator('.pa143').count() == 1 and a.openp(c3) and len(a.outcomes()) == n0, 'a notification “No” opens the case and records nothing yet')
    card = pg.inner_text('.pa143')
    ok('Currys' in card or 'refund' in card.lower(), 'it shows which case it was about: %s' % card.replace('\n', ' | '))
    ok(pg.locator('[data-a=pa143-yes]').inner_text() == 'Record it as missed', 'the button says what it records')
    pg.click('[data-a=pa143-yes]'); wait(pg, 800)
    ok(a.case(c3)['promises'][-1]['status'] == 'missed' and len(a.outcomes()) == n0 + 1, 'one tap records it')
    ok('Recorded from your notification' in a.main(), 'the banner names the notification, not email')
    c4 = a.start('Amazon said the refund of £15 would arrive by %d %s' % (day(5).day, day(5).strftime('%B')))
    a.overdue(c4); pid4 = a.openp(c4)[0]['id']; n0 = len(a.outcomes())
    a.pg.goto('https://sorted.test/?task=%s&src=push&ans=yes&p=%s' % (c4, pid4)); wait(pg, 1200)
    pg.click('[data-a=pa143-no]'); wait(pg, 500)
    ok(a.openp(c4) and len(a.outcomes()) == n0 and pg.locator('.pa143').count() == 0, '“Not now” records nothing')
    a.pg.goto('https://sorted.test/?task=%s&src=email&ans=yes&p=%s' % (c4, pid4)); wait(pg, 1200)
    ok(a.case(c4)['promises'][-1]['status'] == 'kept' and 'Recorded from your email' in a.main(), 'an email answer still records once the case loads, and says “email”')
    # a notification "No" for a promise with no firm day
    c5 = a.start('Hermes said the parcel would come in the next few days')
    a.open(c5); pg.click('[data-a=panel][data-p=chk138]'); wait(pg, 300); pg.fill('#f-chkday', day(1).isoformat()); pg.click('form[data-f=chk138] button[type=submit]'); wait(pg, 600)
    a.task_js(c5, "t.att.forEach(function(x){if(x.kind==='check'){var d=new Date();d.setHours(0,0,0,0);x.at=d.toISOString()}})")
    pid5 = a.openp(c5)[0]['id']; n0 = len(a.outcomes())
    a.pg.goto('https://sorted.test/?task=%s&src=push&ans=no&p=%s' % (c5, pid5)); wait(pg, 1200)
    ok(pg.locator('[data-a=pa143-yes]').inner_text() == 'Yes, still waiting', 'for a promise with no firm day, the notification answer is “still waiting”')
    pg.click('[data-a=pa143-yes]'); wait(pg, 800)
    ok(a.case(c5)['promises'][-1]['status'] == 'open' and len(a.outcomes()) == n0 and not any(x.startswith('It didn’t happen') for x in a.labels(c5)), 'and records no miss')
    # ================= Home answers can be undone =================
    c6 = a.start('Sky said they would refund £30 by %d %s, ref SK-1234' % (day(4).day, day(4).strftime('%B')))
    a.overdue(c6); n0 = len(a.outcomes()); ev0 = a.labels(c6)
    a.q('Sky', 'q-kept').click(); wait(pg, 800)
    ok(a.case(c6)['promises'][-1]['status'] == 'kept' and len(a.outcomes()) == n0 + 1, 'a Home answer records at once')
    u = pg.locator('.q130-done [data-a=q-undo]')
    ok(u.count() == 1, 'with an Undo on the “Recorded” card')
    u.click(); wait(pg, 800)
    t6 = a.case(c6)
    ok(t6['promises'][-1]['status'] == 'open' and [e['label'] for e in t6['events']] == ev0 and len(a.outcomes()) == n0, 'Undo restores the status, the history and the company total')
    a.home(); a.q('Sky', 'home-ans').click(); wait(pg, 800)
    ok(a.case(c6)['promises'][-1]['status'] == 'missed' and pg.locator('.qu143 [data-a=q-undo]').count() == 1, '“Not yet” on Home records the miss, with Undo on the case')
    pg.click('.qu143 [data-a=q-undo]'); wait(pg, 800)
    ok(a.case(c6)['promises'][-1]['status'] == 'open' and len(a.outcomes()) == n0 and not any(x.startswith('It didn’t happen') for x in a.labels(c6)), 'Undo takes the miss and the total back')
    a.home(); a.q('Sky', 'q-kept').click(); wait(pg, 800)
    a.open(c6)   # a fresh load: the two-minute Undo has gone
    ok(pg.locator('[data-a=q-mistake]').count() == 1, 'afterwards the case still offers “That was a mistake”')
    pg.click('[data-a=q-mistake]'); wait(pg, 800)
    ok(a.case(c6)['promises'][-1]['status'] == 'open' and len(a.outcomes()) == n0 and any('was a mistake' in x for x in a.labels(c6)), '“That was a mistake” reopens it and drops the total, with a history line')
    # ================= scores only for an organisation's dated promise =================
    c7 = a.start('Currys said the £40 refund would come within five working days, order 445566')
    a.past_reading(c7); n0 = len(a.outcomes())
    a.open(c7)
    k = pg.locator('.promise [data-a=kept]')
    if k.count(): k.first.click(); wait(pg, 700)
    else: a.home(); a.q('Currys', 'q-kept').click(); wait(pg, 700)
    ok(a.case(c7)['promises'][-1]['status'] == 'kept' and len(a.outcomes()) == n0, 'a kept promise dated by Sorted’s calculation adds nothing to the company totals')
    # ================= Already paid =================
    c8 = a.parking(-8)
    a.home(); a.q('Southwark', 'q-paid').click(); wait(pg, 700)
    ok(pg.locator('form[data-f=pkpaid]').count() == 1, '“Already paid” goes straight to the payment record')
    a.close()
finish()
