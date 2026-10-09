# v149: a reminder that reaches a guest. On 9 October production had 16 people, 42 cases and no reminder ever sent.
# A case with a date now says plainly that nothing reaches the person outside Sorted yet, and offers one choice:
# their calendar first, this phone, an email, or no reminder. The choice is kept on the case and recorded as a code
# (reminder_path_chosen). The email panel no longer opens by itself after a promise is confirmed.
import os, sys, re, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *

with sync_playwright() as p:
    a = App(p, email=False); pg = a.pg
    fri = nextwd(4, 2)
    c1 = a.start('Currys said they would refund £40 by %d %s, order 556677' % (fri.day, fri.strftime('%B')))
    a.open(c1); m = a.main()
    card = pg.locator('.rem149')
    ok(card.count() == 1, 'a guest’s dated case asks how Sorted should remind them')
    ok('How should Sorted remind you on %s %d %s?' % (fri.strftime('%A'), fri.day, fri.strftime('%B')) in m and 'At the moment nothing will reach you outside Sorted' in m, 'it names the day and says honestly that nothing reaches them yet')
    ok(pg.locator('.rem149 [data-v=cal]').count() == 1 and 'primary' in (pg.locator('.rem149 [data-v=cal]').get_attribute('class') or ''), 'the calendar comes first')
    ok(pg.locator('.rem149 [data-v=email]').count() == 1 and pg.locator('.rem149 [data-v=none]').count() == 1, 'with email and “No reminder”')
    ok(pg.locator('#claim').count() == 0, 'the email panel doesn’t open by itself')
    ok(pg.locator('.rem149').count() == 1 and m.count('How should Sorted remind you') == 1, 'one question, not two')
    # calendar: the file is made, the choice kept and recorded as a code
    with pg.expect_download() as dl: pg.click('.rem149 [data-v=cal]')
    d = dl.value; ics = open(d.path(), encoding='utf-8').read()
    ok(d.suggested_filename.endswith('.ics') and 'BEGIN:VALARM' in ics, 'the calendar file has an alarm')
    wait(pg, 800)
    t = a.case(c1)
    ok((t.get('rem149') or {}).get('how') == 'cal' and t.get('calAt'), 'the choice is kept on the case')
    ok(pg.locator('.rem149').count() == 0 and 'Reminder: In your calendar' in a.main(), 'the question becomes one line saying how it will remind them')
    ev = [e for e in a.db().get('pilot_events', []) if e.get('name') == 'reminder_path_chosen']
    ok(ev and ev[-1]['props'].get('how') == 'calendar' and set(ev[-1]['props']) <= {'how', 'mode', 'anon'}, 'recorded as a code only: %s' % (ev and ev[-1]['props']))
    pg.reload(); wait(pg, 900)
    ok(pg.locator('.rem149').count() == 0 and 'Reminder: In your calendar' in a.main(), 'still answered after a reload')
    pg.click('[data-a=rem149-change]'); wait(pg, 600)
    ok(pg.locator('.rem149').count() == 1, '“Change” asks again')
    # no reminder
    pg.click('.rem149 [data-v=none]'); wait(pg, 600)
    ok('Reminder: No reminder' in a.main() and (a.case(c1).get('rem149') or {}).get('how') == 'none', '“No reminder” is a choice too, said plainly')
    # email opens the email panel
    c2 = a.start('Evri said they would deliver the parcel by %d %s, ref EV123456' % (fri.day, fri.strftime('%B')))
    a.open(c2); pg.click('.rem149 [data-v=email]'); wait(pg, 600)
    ok(pg.locator('#claim').count() == 1, '“Email me” opens the email form')
    # a case with no date asks nothing
    c3 = a.start('My neighbour’s tree is overhanging the fence', confirm=False)
    a.open(c3)
    ok(pg.locator('.rem149').count() == 0, 'no date, no reminder question')
    a.close()
    # an email account with reminders ready is not asked
    a = App(p, email=True); pg = a.pg
    c4 = a.start('Currys said they would refund £40 by %d %s, order 556678' % (fri.day, fri.strftime('%B')))
    a.open(c4)
    ok(pg.locator('.rem149').count() == 0, 'someone who already gets email reminders isn’t asked')
    a.close()
finish()
