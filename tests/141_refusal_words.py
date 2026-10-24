# v177, from Baldwin's walk of 24 October 2026: "They said I don’t qualify" pasted into a case was saved, then the paste
# screen said Sorted couldn't find a date and stayed open. Everyday refusals are now proposed as "they've said no" and
# nothing changes until the tap; hedged words are not; a message with nothing to propose closes the screen with a
# plain message.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *

def paste(a, cid, words):
    pg = a.pg; a.open(cid)
    pg.locator('[data-a=panel][data-p=paste]').first.click(); wait(pg, 400)
    pg.fill('#f-paste', words); pg.locator('form[data-f=paste] button[type=submit]').first.click(); wait(pg, 700)

with sync_playwright() as p:
    a = App(p); pg = a.pg
    # 1 a case with their promise: the refusal is proposed, the promise untouched until Yes
    c1 = a.start('DWP said they would decide on my PIP claim by 30 October')
    ok(len(a.openp(c1)) == 1, 'the case has DWP’s open promise')
    paste(a, c1, 'They said I don’t qualify')
    m = a.main()
    ok('Sounds like they’ve said no. Record that?' in m and 'They wrote: “They said I don’t qualify”' in m, '"They said I don’t qualify" is proposed as a refusal')
    ok('couldn’t find a date' not in m and pg.locator('#f-paste').count() == 0, 'no date message, the paste screen has closed')
    ok(len(a.openp(c1)) == 1 and any('They said I don’t qualify' in l for l in a.labels(c1)), 'nothing changed yet except the message being kept')
    pg.click('[data-a=out-yes]'); wait(pg, 700); t = a.case(c1)
    ok([q['status'] for q in t['promises']] == ['withdrawn'] and any(l.startswith('They said no: “They said I don’t qualify”') for l in a.labels(c1)), 'Yes closes the promise as withdrawn by them, with a history line')
    ok(pg.locator('#moveform').count() == 1 and 'They’ve said no. What will you do next?' in a.main(), 'and asks what you will do next')
    # 2 a case with no promise: proposed too; Not that changes nothing
    c2 = a.start('I applied for PIP and I am waiting to hear from DWP')
    paste(a, c2, 'DWP said I’m not eligible')
    ok('Sounds like they’ve said no. Record that?' in a.main(), '"not eligible" on its own is proposed on a case with no promise')
    before = len(a.labels(c2)); pg.click('[data-a=out-no]'); wait(pg, 600)
    ok(not a.case(c2).get('outP') and 'Sounds like they’ve said no' not in a.main() and a.case(c2)['board'] != 'done', 'Not that leaves the case as it was')
    # 3 more wordings through the page
    for words in ['They turned me down', 'Your application was unsuccessful', 'They told me I wasn’t entitled to it', 'They said no']:
        paste(a, c2, words)
        ok('Sounds like they’ve said no. Record that?' in a.main(), 'proposed: %s' % words)
        pg.click('[data-a=out-no]'); wait(pg, 400)
    # 4 hedged words and ordinary updates: kept, screen closed, a plain message, no proposal
    for words in ['I might not qualify, waiting to hear', 'Worried I don’t qualify but they haven’t decided', 'Thanks, we have received your form']:
        n = len(a.labels(c2)); paste(a, c2, words); m = a.main()
        ok('Sounds like they’ve said no' not in m and pg.locator('#f-paste').count() == 0, 'not a refusal, and the screen closes: %s' % words)
        ok(pg.locator('#toast').inner_text() == 'Added to the case. Sorted found nothing in it that changes a date or a promise.', 'with a plain message saying it was added')
        ok(len(a.labels(c2)) == n + 1, 'and the words are kept once')
    ok(pg.evaluate('document.documentElement.scrollWidth<=innerWidth'), 'nothing scrolls sideways')
    a.b.close()
print('ERRORS', errs); print('FAILS', fails)
