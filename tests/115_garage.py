# v147: the garage test of 9 October. "A garage said the car would be ready today after a brake job and they would
# text when it was done. No text. The job-card number isn't with me." Plan: "Phone the garage in the morning to ask if
# it's ready and what the bill is. Not sure if they open at 8 or 9."
# Before v147: "Something's broken" offered only household repairs; "Garage name not with me" became the garage's name
# in the quote and the title; the quote read "said they would said the car would…"; confirming the promise dropped the
# plan, the case went to Waiting and Home said "All clear"; the calendar alarm was the evening before (already past) and
# the time "any time".
import os, sys, re, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *

PLAN = 'Phone the garage in the morning to ask if it is ready and what the bill is. Not sure if they open at 8 or 9'
with sync_playwright() as p:
    a = App(p, email=False); pg = a.pg
    # ---- "Something's broken" knows cars go to a garage ----
    m = a.main()
    ok('a car at the garage' in m, 'the repair door mentions a car at the garage')
    pg.locator('[data-cap82=fix]').first.evaluate('e=>e.click()'); wait(pg, 600)
    car = pg.locator('.gi147-car [data-cap95=garage]')
    ok(car.count() == 1, 'the repair questions offer the garage questions for a car or van')
    car.click(); wait(pg, 700)
    ok('Which garage?' in a.main() and pg.locator('#gi-who').count() == 1, 'and that opens the garage questions')
    # ---- the journey ----
    pg.fill('#gi-who', 'Garage name not with me')
    pg.fill('#gi-what', 'said the car would be ready today after a brake job and they would text when it was done')
    pg.locator('form[data-f=gi] button[type=submit]').first.click(); wait(pg, 900)
    ok(pg.locator('form[data-f=baseline]').count() == 1, 'the plan question is asked')
    pg.fill('#f-baseline', PLAN); pg.locator('form[data-f=baseline] button[type=submit]').click(); wait(pg, 900)
    t = a.cases()[-1]; m = a.main()
    ok((t.get('facts') or {}).get('party') == 'The garage' and 'not with me' not in json.dumps(t), 'a name placeholder is not a name: the garage, from the question (%s)' % (t.get('facts') or {}).get('party'))
    ok('said they would said' not in t['said'] and t['said'].startswith('The garage said the car would be ready'), 'no “said they would said”: %s' % t['said'])
    ok('not with me' not in t['title'].lower() and 'garage' in t['title'].lower(), 'the title names the garage, not the placeholder: %s' % t['title'])
    sp = t.get('sugP') or {}
    ok(sp.get('said', '').startswith('The car would be ready today') and sp.get('party') == 'The garage', 'the promise is the garage’s, in their words: %s' % sp.get('said'))
    mv = t.get('moves') or []
    ok(len(mv) == 1 and mv[0]['what'].startswith('Phone the garage in the morning') and mv[0].get('src') == 'plan' and mv[0].get('kind') == 'contact', 'the plan is kept as your step, in your words, next to their promise')
    due = L(mv[0].get('dueAt')) if mv else None
    nowl = datetime.datetime.now().astimezone()
    exp = nowl.date() + datetime.timedelta(days=0 if nowl.hour < 8 else 1)
    ok(due and due.hour == 8 and due.minute == 0 and due.date() == exp and not mv[0].get('allDay'), '“in the morning” is the next 8am: %s' % due)
    ok('no time given' in m and 'any time' not in m, 'their day says “no time given”, never “any time”')
    pg.click('[data-a=sug-yes]'); wait(pg, 900)
    t = a.cases()[-1]
    ok(t['board'] == 'yours' and [x['status'] for x in t['moves']] == ['open'] and t['promises'][0]['status'] == 'open', 'confirming their promise keeps your step open, and the case with you')
    m = a.main()
    ok('Next: phone the garage in the morning' in m, 'the case leads with your call')
    ok('evening before' not in m, 'no calendar alarm for an evening already gone')
    a.home(); m = a.main()
    ok('All clear' not in m and 'Nothing needs you' not in m, 'Home doesn’t say all clear while your call is to do')
    ok('Phone the garage in the morning' in m and '8am' in m and pg.locator('[data-a=home-move]').count() >= 1, 'Home names your call, its time, and a button for when it’s done')
    # ---- a promise due today with no step: the calendar alarm moves to 6pm, or isn't offered ----
    c2 = a.start('Currys said the washing machine part would arrive today')
    a.open(c2); m = a.main()
    if datetime.datetime.now().hour < 18:
        ok('It reminds you at 6pm that day.' in m and 'evening before' not in m, 'a promise due today: the calendar reminds you at 6pm, not the evening before')
    else:
        ok('evening before' not in m, 'after 6pm, no calendar alarm in the past')
    # ---- without a promise nothing changes ----
    c3 = a.start('BT broadband keeps dropping out', confirm=False)
    t3 = a.case(c3)
    ok(not [x for x in (t3.get('moves') or []) if x.get('kind') == 'contact'], 'with no promise, nothing is turned into a step of yours')
    a.close()
finish()
