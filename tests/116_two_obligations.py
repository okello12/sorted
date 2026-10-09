# v148: two obligations at once (the refund, TSB and garage tests, 8 and 9 October).
# The rule: what they owe (their promise) and what you plan (your step) are kept apart. A promise Sorted reads, or one
# you confirm, never closes, replaces or hides your plan; confirming asks "Keep my follow-up" or "I'll just wait for
# them"; while your step is open Home is never "All clear"; "I heard from them" ends a call that was only needed if
# they didn't get in touch; an unknown opening time is said and can be filled in; "Something's broken" presumes no
# appliance and has a car of its own; a corrected quote is the one every screen shows.
import os, sys, re, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *

PLAN = "Phone the garage in the morning if there's still no text, ask if it's ready and what the bill is. Not sure if they open at 8 or 9"
def garage(a, plan=PLAN):
    pg = a.pg; a.home(); a.tap('new-case')
    pg.locator('[data-cap82=fix]').first.evaluate('e=>e.click()'); wait(pg, 600)
    pg.locator('.gi147-car').click(); wait(pg, 700)
    pg.fill('#gi-who', 'Garage name not with me')
    pg.fill('#gi-what', 'said the car would be ready today after a brake job and they would text when it was done')
    pg.locator('form[data-f=gi] button[type=submit]').first.click(); wait(pg, 900)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg, 600)
    pg.fill('#f-baseline', plan); pg.locator('form[data-f=baseline] button[type=submit]').click(); wait(pg, 900)
    return a.cases()[-1]['id']

with sync_playwright() as p:
    a = App(p, email=False); pg = a.pg
    # ---- the repair door presumes nothing ----
    pg.locator('[data-cap82=fix]').first.evaluate('e=>e.click()'); wait(pg, 600)
    m = a.main()
    ok('What needs repairing?' in m, 'the repair door asks what needs repairing')
    ok(pg.locator('input[name=gi-item]:checked').count() == 0, 'no appliance is chosen for you')
    ok(pg.locator('.gi-chip.gi147-car[data-cap95=garage]').count() == 1 and pg.locator('.gi-chip.gi147-car').inner_text() == 'A car or van', 'a car or van is one of the choices')
    # ---- confirming their promise asks about your plan ----
    c1 = garage(a)
    t = a.case(c1); mv = t['moves'][0]
    ok(mv['src'] == 'plan' and mv['kind'] == 'contact' and mv.get('cond') == "if there's still no text" and mv.get('openUnk') is True, 'your plan is your step, with its condition and the unknown opening time: %s' % {k: mv.get(k) for k in ('cond', 'openUnk')})
    pg.click('[data-a=sug-yes]'); wait(pg, 900)
    m = a.main()
    ok(pg.locator('.plan148').count() == 1 and 'You also said you planned to' in m and pg.locator('[data-a=plan-keep148]').count() == 1 and pg.locator('[data-a=plan-wait148]').count() == 1, 'confirming their promise asks: Keep my follow-up, or I’ll just wait for them')
    t = a.case(c1)
    ok(t['moves'][0]['status'] == 'open' and t['board'] == 'yours' and t.get('planAsk148'), 'nothing about your plan changes before you answer')
    pg.reload(); wait(pg, 900)
    ok(pg.locator('.plan148').count() == 1, 'the question is still there after a reload')
    pg.click('[data-a=plan-keep148]'); wait(pg, 900)
    m = a.main()
    ok(pg.locator('.both148').count() == 1 and 'BOTH OF YOU HAVE A NEXT STEP' in m.upper(), 'kept: the case shows both of you have a next step')
    for x in ('What your garage said', 'Your plan', 'Only if there\'s still no text', 'Opening time', 'Not known yet', 'Check when they open, then contact them if there\'s still no text', 'Also waiting for'):
        ok(x in m, 'the card says “%s”' % x)
    ok(pg.locator('.both148 [data-a=heard148]').count() == 1 and pg.locator('.both148 [data-a=move-done]').count() == 1, 'with “I’ve called” and “I heard from them”')
    # opening time
    pg.click('[data-a=open148-ask]'); wait(pg, 400)
    pg.fill('#open148-time', '09:00'); pg.locator('form[data-f=open148] button[type=submit]').click(); wait(pg, 800)
    mv = a.case(c1)['moves'][0]
    ok(L(mv['dueAt']).hour == 9 and not mv.get('openUnk') and 'Not known yet' not in a.main(), 'telling Sorted they open at 9 moves your step to 9am: %s' % L(mv['dueAt']))
    # Home is never all clear while your step is open
    a.home(); m = a.main()
    ok('All clear' not in m and 'Nothing needs you' not in m, 'Home doesn’t say all clear')
    ok(pg.locator('[data-a=heard148][data-id="%s"]' % c1).count() == 1 and pg.locator('[data-a=home-move][data-id="%s"]' % c1).count() == 1, 'Home offers “I’ve called” and “I heard from them”')
    # I heard from them: the conditional call isn't needed, and Sorted asks what they said
    pg.locator('[data-a=heard148][data-id="%s"]' % c1).click(); wait(pg, 900)
    t = a.case(c1)
    ok(t['moves'][0]['status'] == 'dropped' and t['moves'][0].get('heard') and t['promises'][0]['status'] == 'open', 'I heard from them: your call isn’t needed; their promise is untouched until you say what they said')
    ok(pg.locator('#f-paste').count() == 1, 'and Sorted asks what they said')
    ok(any('so your follow-up isn’t needed now' in e for e in a.labels(c1)), 'the history says why')
    # ---- "I'll just wait for them" ----
    c2 = garage(a, 'Ring them tomorrow at 10 to check')
    pg.click('[data-a=sug-yes]'); wait(pg, 900)
    pg.click('[data-a=plan-wait148]'); wait(pg, 900)
    t = a.case(c2)
    ok(t['moves'][0]['status'] == 'dropped' and t['board'] == 'waiting' and pg.locator('.both148').count() == 0, 'waiting instead: your step is set aside, by you, and the case waits')
    ok(any('You chose to wait for' in e for e in a.labels(c2)), 'the history says it was your choice')
    # ---- no plan, no question ----
    c3 = garage(a, 'Not sure yet')
    pg.click('[data-a=sug-yes]'); wait(pg, 900)
    ok(pg.locator('.plan148').count() == 0 and not a.case(c3).get('moves'), 'with no plan, nothing is asked and no step is made')
    # ---- a plan given at the start, their promise later ----
    a.home(); a.tap('new-case'); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.fill('#f-case', 'Currys still owe me a refund for the kettle, order 556677'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 800)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    pg.fill('#f-baseline', 'Go into the shop on Saturday with the receipt'); pg.locator('form[data-f=baseline] button[type=submit]').click(); wait(pg, 900)
    c4 = a.cases()[-1]['id']
    pg.goto('https://sorted.test/?task=%s' % c4); wait(pg, 800)
    pg.click('.now137-add'); wait(pg, 300)
    fri = nextwd(4, 2)
    pg.fill('#f-paste', 'Currys: we will refund £20 to your card by %d %s.' % (fri.day, fri.strftime('%B'))); pg.locator('form[data-f=paste] button[type=submit]').first.click(); wait(pg, 900)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 900)
    ok(pg.locator('.plan148').count() == 1 and 'Go into the shop on Saturday with the receipt' in a.main(), 'their promise arriving later still asks about the plan you gave at the start')
    pg.click('[data-a=plan-keep148]'); wait(pg, 900)
    t = a.case(c4); mv = [x for x in t.get('moves', []) if x.get('src') == 'plan']
    ok(len(mv) == 1 and mv[0]['status'] == 'open' and mv[0]['what'].startswith('Go into the shop') and L(mv[0].get('dueAt')).weekday() == 5, 'Keep makes it your step, on Saturday: %s' % (mv and mv[0].get('dueAt')))
    # ---- a corrected quote is the one every screen shows ----
    a.home(); a.tap('new-case'); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.fill('#f-case', 'Evri said they would deliver the parcel by Friday %d %s' % (fri.day, fri.strftime('%B'))); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 800)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('[data-a=plan-skip]'); wait(pg, 800)
    c5 = a.cases()[-1]['id']
    pg.click('[data-a=sug-edit]'); wait(pg, 600)
    pg.fill('#f-said', 'Your parcel will be with you by Friday, the driver will leave it with a neighbour')
    pg.locator('form[data-f=promise] button[type=submit]').click(); wait(pg, 900)
    old = 'deliver the parcel by Friday'
    t = a.case(c5)
    ok(t['promises'][-1]['said'].startswith('Your parcel will be with you') and t['promises'][-1]['status'] == 'open', 'the edit is saved on the promise')
    m = a.main().split('What’s happened')[0]
    ok('leave it with a neighbour' in m and old not in m, 'the case page shows the corrected words (outside the history)')
    a.home(); m = a.main()
    ok(old not in m, 'Home never shows the old words')
    pk = a.pack(c5)
    ok('leave it with a neighbour' in pk, 'the record carries the corrected words')
    sv = a.share_view(c5)
    ok(old not in sv and 'neighbour' in sv, 'the helper’s link shows the corrected words')
    a.close()
finish()
