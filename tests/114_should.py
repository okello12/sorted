# v146: "should" is their estimate, the same whether typed or pasted.
# Before v146 "DWP said my payment should arrive by Friday" (typed) was a maybe and created nothing, while
# "Your parcel should arrive by Friday 16 October." (pasted) was a firm promise that could count as broken.
# Now: "should" with a day, from them, is proposed as their estimate (est146), with a line saying so; once confirmed the
# card says "They expect"; on the day Sorted asks, and "Not yet" records no miss and no company total; a booked or
# "will" date stays firm; might, maybe, hopefully, "try their best" and the person's own "I should" stay non-commitments.
import os, sys, re, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *
import corpus

def paste(a, cid, text):
    pg = a.pg; a.open(cid); pg.click('.now137-add'); wait(pg, 300)
    pg.fill('#f-paste', text); pg.locator('form[data-f=paste] button[type=submit]').first.click(); wait(pg, 800)

READ = """(xs)=>xs.map(function(t){var r=window.__read,p=r.readCase(t,r.caseFacts(t));return p?{said:p.said,est:!!p.est146,dueAt:p.dueAt}:null})"""
with sync_playwright() as p:
    a = App(p); pg = a.pg
    # ================= the reader: one rule for typed and pasted =================
    a.ctx.route(lambda u: u.startswith('https://sorted.test/reader'), lambda r: r.fulfill(path=HERE + '/tests/out/reader.html', content_type='text/html'))
    rp = a.ctx.new_page(); rp.goto('https://sorted.test/reader'); wait(rp, 500)
    r = rp.evaluate(READ, corpus.SHOULD_EST)
    bad = [s for s, x in zip(corpus.SHOULD_EST, r) if not x or not x['est'] or not x['dueAt']]
    ok(not bad, '“should” with a day, typed or pasted, is read as their estimate: %d/%d %s' % (len(r) - len(bad), len(r), bad))
    r = rp.evaluate(READ, corpus.SHOULD_FIRM)
    ok(all(x and not x['est'] for x in r), 'a booked or “will” date stays firm: %s' % [x and x['said'] for x in r])
    r = rp.evaluate(READ, corpus.SHOULD_NOT)
    ok(not any(r), 'maybes, “try their best” and your own “I should” are not commitments: %s' % [(s, x['said']) for s, x in zip(corpus.SHOULD_NOT, r) if x])
    rp.close()
    # ================= typed: proposed as their estimate =================
    fri = nextwd(4, 2)
    a.home(); a.tap('new-case')
    pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
    pg.fill('#f-case', 'DWP said my payment should arrive by %d %s' % (fri.day, fri.strftime('%B')))
    pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 700)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 600)
    m = a.main()
    ok(pg.locator('[data-a=sug-yes]').count() == 1, 'the typed sentence is proposed for you to confirm, not dropped')
    ok(pg.locator('.sug .est146').count() == 1 and 'That’s their estimate, not a firm promise' in m, 'the proposal says it is their estimate')
    pg.click('[data-a=sug-yes]'); wait(pg, 800)
    if pg.locator('[data-a=nudge-skip]').count(): pg.click('[data-a=nudge-skip]'); wait(pg, 300)
    c1 = a.cases()[-1]['id']
    p1 = a.openp(c1)
    ok(len(p1) == 1 and p1[0].get('est146') is True and p1[0].get('party') == 'DWP', 'confirmed, the promise keeps the estimate mark: %s' % (p1 and {k: p1[0].get(k) for k in ('party', 'est146', 'prec')}))
    a.open(c1); m = a.main()
    ok("THEY EXPECT" in m.upper() and "THEY PROMISED" not in m.upper() and "DWP expects it by" in m and "said it should happen, and the date is on the case" in m and pg.locator('.promise .est146').count() == 1, 'the card says “They expect”, what happened says “expects it” and whose move says “should”, with the estimate line')
    ok(pg.locator('.promise [data-p=chk138]').count() == 1, 'with “Choose when to check”')
    # ================= on the day: "Not yet" is no broken promise =================
    a.overdue(c1, 1); n0 = len(a.outcomes())
    a.open(c1); m = a.main()
    ok('The day they expected has passed' in m or 'Did it' in m or 'Has' in m, 'once the day passes Sorted asks about it')
    btn = pg.locator('[data-a=missed]').first
    ok(btn.count() == 1, 'with the “not yet” answer on the card')
    if btn.count(): btn.click(); wait(pg, 900)
    t1 = a.case(c1)
    ok(t1['promises'][-1]['status'] == 'open' and len(a.outcomes()) == n0, 'Not yet records no miss and no company total')
    ok(any('should happen by then, not that it would' in e for e in a.labels(c1)), 'the history says why: %s' % a.labels(c1)[-1:])
    # ================= pasted: the same rule =================
    c2 = a.start('Evri lost my parcel, ref EV556677', confirm=False)
    sat = nextwd(5, 2)
    paste(a, c2, 'Evri: Your parcel should arrive by %s %d %s.' % (sat.strftime('%A'), sat.day, sat.strftime('%B')))
    m = a.main()
    ok(pg.locator('[data-a=sug-yes]').count() == 1 and pg.locator('.sug .est146').count() == 1, 'a pasted “should” is proposed as their estimate too')
    pg.click('[data-a=sug-yes]'); wait(pg, 800)
    p2 = a.openp(c2)
    ok(p2 and p2[-1].get('est146') is True, 'and kept as one once confirmed')
    # a firm date pasted the same way is unchanged
    c3 = a.start('Currys owe me a refund, order 123456', confirm=False)
    paste(a, c3, 'Currys: we will refund £40 by %d %s.' % (fri.day, fri.strftime('%B')))
    ok(pg.locator('[data-a=sug-yes]').count() == 1 and pg.locator('.sug .est146').count() == 0, 'a “will” date is proposed as a firm promise, with no estimate line')
    # ================= a firm promise still counts =================
    c4 = a.start('Argos said they will refund £20 by %d %s, order 9911' % (fri.day, fri.strftime('%B')))
    a.overdue(c4, 1); n0 = len(a.outcomes())
    a.open(c4); pg.locator('[data-a=missed]').first.click(); wait(pg, 900)
    ok(a.case(c4)['promises'][-1]['status'] == 'missed' and len(a.outcomes()) == n0 + 1, 'a firm date they gave can still be missed and counted')
    a.close()
finish()
