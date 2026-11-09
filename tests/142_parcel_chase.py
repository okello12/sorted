# v178: a parcel that hasn't come, and a chase you send yourself (agreed with Baldwin on 9 November 2026).
# "The courier says it was delivered yesterday, but I haven't received it." Sorted keeps their claim apart from the
# person's account, writes a message for the seller they choose, shows what goes in it before it opens in their own
# email app, records "I've sent it" only when they say so, turns a pasted reply into a proposal, and keeps the case
# open until they say how it ended. Usage records keep prepared, opened and said-sent apart, codes only.
from attlib143 import *

def submit_call(pg):
    pg.locator('form[data-f=call] button[type=submit]').click(); wait(pg, 600)
def ev(a): return [e for e in a.db().get('pilot_events', [])]

with sync_playwright() as p:
    a = App(p); pg = a.pg
    # 1 the claim and the person's account, apart
    a.start('Evri says my parcel was delivered yesterday but I haven’t received it')
    c = a.cases()[-1]; cid = c['id']; a.open(cid); m = a.main()
    ok(c['pb']['id'] == 'parcel' and c['pb']['stage'] == 'delivered', 'a parcel case at "marked delivered, not received": %s' % c.get('pb'))
    ok(c['pcl178']['claim'] == 'delivered' and c['pcl178']['recv'] == 'no', 'their claim and your account are kept apart on the case')
    ok(c['promises'] == [], 'their claim is not a promise')
    ok('They say it was delivered. You haven’t got it.' in m and 'Sorted keeps the two apart' in m, 'the card says both, apart')
    ok(pg.locator('.pb-card a[href*="citizensadvice.org.uk/consumer/somethings-gone-wrong-with-a-purchase/if-something-you-ordered-hasnt-been-delivered"]').count() == 1 and 'contact the seller rather than the courier' in m, 'one line of advice with the Citizens Advice page')
    ok('Next: ask the seller what they’ll do' in pg.inner_text('.now137'), 'Now names the next action, not their app')
    ok('Whose move is it now?' not in m, 'no whose-move question: the card already says it')
    ok('Ask the seller where it is' in m and 'Ask Evri for a date' not in m, 'the first response points at the seller')
    if pg.locator('[data-a=fr-ok]').count(): pg.click('[data-a=fr-ok]'); wait(pg, 500)
    pg.evaluate("document.querySelector('details.case117-u')&&document.querySelector('details.case117-u').setAttribute('open','')")
    u = pg.inner_text('details.case117-u') if pg.locator('details.case117-u').count() else ''
    ok('What they say' in u and 'Sorted hasn’t checked it' in u and 'What you’ve received' in u and 'Nothing yet (your words)' in u, 'What Sorted understood lists their claim and your account: %s' % u[:200].replace('\n', ' | '))
    # 2 the message: email by default, the seller suggested, an optional recipient checked before anything is saved
    pg.click('.pb-card [data-a=panel][data-p=call]'); wait(pg)
    m = a.main()
    ok(pg.locator('form[data-f=call] [data-k=via][data-v=email][aria-pressed=true]').count() == 1 and pg.locator('#f-to').count() == 1, 'email is chosen and there is a recipient field')
    ok('usually best to contact the seller rather than the courier' in m, 'the form says who to contact')
    ask = pg.input_value('#f-ask')
    ok(ask.startswith('Hi, my order is marked as delivered, but I haven’t received it.') and 'redeliver it, replace it or refund me' in ask, 'the message says what happened and asks by when: %s' % ask)
    pg.fill('#f-who', 'Currys'); pg.fill('#f-to', 'currys help'); submit_call(pg)
    ok('doesn’t look like an email address' in a.main() and a.case(cid).get('call') is None, 'a mistyped address is caught and nothing is saved')
    pg.fill('#f-to', 'help@currys.example'); submit_call(pg)
    c = a.case(cid)
    ok(c['call']['via'] == 'email' and c['call']['to'] == 'help@currys.example' and c['call']['who'] == 'Currys', 'the email is saved with its recipient (the channel shown, not phone)')
    # 3 before you send: what goes, and honesty about who sends it
    r = pg.inner_text('.rev178')
    ok('To' in r and 'help@currys.example' in r and 'Subject' in r and 'Only the message above. Nothing else from your case goes with it.' in r, 'Before you send: the recipient, subject and what it shares')
    ok('Sorted doesn’t send it for you and can’t see whether it was sent.' in r, 'and that the person sends it')
    href = pg.get_attribute('[data-a=mail-open]', 'href') or ''
    ok(href.startswith('mailto:help@currys.example?') and 'body=Hi%2C%20my%20order' in href, 'the email app opens addressed to them: %s' % href[:60])
    ok('Next: send the message, then say you’ve sent it' in pg.inner_text('.now137'), 'Now: send it, then say so')
    ok(pg.locator('.pb-card').count() == 0, 'the parcel card steps back while the message is ready')
    # 4 opened is not sent
    pg.evaluate("document.querySelector('[data-a=mail-open]').addEventListener('click',e=>e.preventDefault(),{once:true})"); pg.click('[data-a=mail-open]'); wait(pg)
    c = a.case(cid)
    ok(c['call'].get('openedAt') and not c['call'].get('sentAt'), 'opening the email app records an opening, not a send')
    ok('Have you sent it?' in pg.inner_text('.sent178') and pg.locator('[data-a=chase-notyet178]').count() == 1, 'and asks whether it was sent')
    pg.click('[data-a=chase-notyet178]'); wait(pg, 600)
    ok(not a.case(cid)['call'].get('openedAt') and not a.case(cid)['call'].get('sentAt') and pg.locator('[data-a=chase-sent178]').count() == 1, 'Not yet records nothing sent and keeps the way to say so')
    pg.click('[data-a=chase-sent178]'); wait(pg, 600)
    c = a.case(cid)
    ok(c['call'].get('sentAt') and 'You said you sent the email to Currys.' in a.labels(cid), 'I’ve sent it is recorded in the person’s terms')
    ok(pg.locator('#moveform, form[data-f=move]').count() >= 1 and 'Check for a reply from Currys' in (pg.input_value('#f-mwhat') if pg.locator('#f-mwhat').count() else a.main()), 'and offers a reminder in case they don’t reply')
    pg.locator('form[data-f=move] button[type=submit]').first.click(); wait(pg, 700)
    ok(any(mv.get('status') == 'open' for mv in a.case(cid).get('moves', [])), 'the reminder is the person’s own step')
    names = [e['name'] for e in ev(a)]
    ok(all(n in names for n in ['chase_prepared', 'chase_opened', 'chase_sent_said']) and names.index('chase_prepared') < names.index('chase_opened') < names.index('chase_sent_said'), 'usage records keep prepared, opened and said-sent apart: %s' % names)
    for e in ev(a):
        if e['name'].startswith('chase_'):
            ok(set(e['props']) <= {'via', 'pb', 'after_miss', 'mode', 'anon'} and all(not isinstance(v, str) or len(v) < 12 for v in e['props'].values()), 'codes only in %s: %s' % (e['name'], e['props']))
    # 5 the reply is a proposal; a confirmed date becomes the next tracked date
    a.open(cid)
    pg.locator('[data-a=panel][data-p=paste]').first.click(); wait(pg, 400)
    pg.fill('#f-paste', 'Thanks for contacting Currys. We will send you a replacement by %s.' % long(day(3))); pg.locator('form[data-f=paste] button[type=submit]').first.click(); wait(pg, 700)
    ma = [e for e in ev(a) if e['name'] == 'message_added']
    ok(ma and ma[-1]['props'].get('after_chase') is True and ma[-1]['props'].get('via') == 'paste', 'a reply added after a sent chase is counted as such')
    ok(not [q for q in a.case(cid)['promises'] if q['status'] == 'open'], 'nothing changes until the person confirms')
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 700)
    op = a.openp(cid)
    ok(len(op) == 1 and op[0].get('dueAt'), 'confirmed, their date is the next tracked date')
    a.open(cid)
    ok(pg.locator('.pb-card').count() == 0, 'the parcel card waits while their promise is open')
    # 6 the date passes and nothing came: the parcel card comes back, and the chase quotes their promise
    a.overdue(cid); a.open(cid)
    pg.locator('[data-a=missed]').first.click(); wait(pg, 700)
    if pg.locator('[data-a=out-yes]').count(): pg.click('[data-a=out-yes]'); wait(pg, 600)
    a.open(cid); c = a.case(cid)
    ok(c['pb']['stage'] == 'late' and 'It hasn’t arrived' in a.main(), 'a missed date brings the parcel back as not arrived: %s' % c['pb'])
    pg.click('.pb-card [data-a=panel][data-p=call]'); wait(pg)
    ok('didn’t happen' in pg.input_value('#f-ask'), 'the new message quotes what they promised')
    # 7 how it ended is the person's to say
    a.start('Royal Mail said my parcel would be delivered by %s' % long(day(4)))
    c2 = a.cases()[-1]['id']; ok(not a.case(c2).get('pb') and a.case(c2).get('pcl178') is None, 'a promise to deliver is not a claim it was delivered')
    if a.openp(c2):
        a.overdue(c2, 1); a.open(c2); pg.locator('[data-a=kept]').first.click(); wait(pg, 700)
        ok(a.case(c2)['pb']['stage'] == 'outcome' and 'How did it end?' in a.main(), 'when they say they kept it, Sorted asks how it ended')
        ok(a.case(c2)['board'] != 'done', 'and the case stays open')
        pg.click('.pb-card [data-a=pb-go][data-v=received]'); wait(pg, 600)
        ok(a.case(c2)['pcl178']['recv'] == 'yes' and pg.locator('form[data-f=done]').count() == 1, '“I’ve got the parcel” records it and opens the finish form')
        pg.locator('form[data-f=done] button[type=submit]').first.click(); wait(pg, 700)
        ok(a.case(c2)['board'] == 'done' and 'Received' in (a.case(c2).get('outcome') or ''), 'finished as received')
    else:
        ok(False, 'the Royal Mail promise was read')
    # 8 other wordings
    for words, want in [('My Argos parcel hasn’t arrived and the tracking hasn’t updated since Monday', 'stuck'),
                        ('My DPD parcel never arrived', 'late'),
                        ('The tracking says delivered but there is no sign of it', 'delivered')]:
        a.start(words, confirm=False); t = a.cases()[-1]
        ok((t.get('pb') or {}).get('stage') == want, '%s → %s (%s)' % (words, want, t.get('pb')))
    a.start('I want my money back for the parcel that never came', confirm=False); t = a.cases()[-1]
    ok((t.get('pb') or {}).get('id') != 'parcel', 'money back stays with the refund playbook')
    pg.set_viewport_size({'width': 320, 'height': 740}); a.open(cid)
    ok(pg.evaluate('document.documentElement.scrollWidth<=innerWidth'), 'nothing scrolls sideways at 320px')
    a.b.close()
print('ERRORS', errs); print('FAILS', fails)
