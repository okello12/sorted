# v171: document entry is separate from Home, review is before saving, and a sender alone never starts a call form.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *

with sync_playwright() as p:
    a = App(p); pg = a.pg
    old = a.start('Currys still has not refunded my kettle, order CK123456')
    count = len(a.cases())
    a.tap('new-case'); pg.locator('[data-cap82=document]').first.click(); wait(pg)
    ok(pg.locator('main.document171').count() == 1 and pg.locator('.home44-spot').count() == 0 and 'things need you' not in a.main(), 'document entry never mixes the form with the existing Home list')
    ok(pg.locator('.tab129 [aria-current=page]').get_attribute('data-a') == 'new-case', 'New is the selected tab during document entry')
    text = 'HMRC says I owe £300 tax by %s. Reference HM123456.' % long(day(14))
    pg.fill('#f-case', text); wait(pg, 150)
    pg.screenshot(path=HERE+'/tests/out/doc171-entry.png', full_page=True)
    pg.click('[data-a=doc171-home]'); wait(pg)
    ok(pg.locator('.home44-spot').count() > 0 and pg.locator('.draft119').count() == 1, 'Cancel returns to Home and keeps the typed letter as a draft')
    pg.click('[data-a=draft-go]'); wait(pg)
    ok(pg.locator('main.document171').count() == 1 and pg.input_value('#f-case') == text, 'Continue draft restores the focused document flow')
    pg.locator('form[data-f=case] button[type=submit]').click(); wait(pg)
    pg.locator('.doc171-review summary').click(); wait(pg, 100)
    pg.screenshot(path=HERE+'/tests/out/doc171-review.png', full_page=True)
    ok(pg.locator('.doc171-review').count() == 1 and 'HMRC' in pg.locator('.doc171-review').inner_text() and text in pg.locator('.doc171-words').inner_text(), 'the review shows the recognised sender and original words before saving')
    ok('No clear deadline found' not in pg.locator('.doc171-review').inner_text() and 'check this against the letter' in a.main(), 'an extracted deadline is explicitly for checking')
    ok(len(a.cases()) == count and pg.locator('form[data-f=baseline]').count() == 1, 'the optional pilot baseline remains before advice and no case exists yet')
    pg.click('[data-a=back-title]'); wait(pg)
    ok(pg.locator('main.document171').count() == 1 and pg.input_value('#f-case') == text, 'Back returns to the original letter text rather than a title-only form')
    pg.fill('#f-case', 'From HMRC'); pg.locator('form[data-f=case] button[type=submit]').click(); wait(pg)
    pg.locator('.ps-short button[type=submit]').click(); wait(pg)
    ok('Only the sender is known' in a.main(), 'a sender-only review makes the missing information explicit')
    pg.locator('[data-a=plan-skip]').click(); wait(pg, 700)
    pg.screenshot(path=HERE+'/tests/out/doc171-missing.png', full_page=True)
    ok(pg.locator('.doc171-missing').count() == 1 and pg.locator('form[data-f=call]').count() == 0, 'starting with only the sender offers adding the letter, not an assumed phone call')
    new = [t for t in a.cases() if t['id'] != old][0]
    ok(not new.get('promises') and not new.get('moves'), 'review and baseline skip invent no promise, deadline or plan')
    pg.locator('.doc171-missing [data-p=paste]').click(); wait(pg)
    ok(pg.locator('form[data-f=paste]').count() == 1 and pg.locator('input[type=file]').count() > 0, 'the primary action opens the existing photo or paste path')
    for width in [320,390,768]:
        pg.set_viewport_size({'width':width,'height':844}); wait(pg, 100)
        ok(pg.evaluate('document.documentElement.scrollWidth<=innerWidth'), 'document action has no sideways scrolling at %dpx' % width)
    a.close()
finish()
