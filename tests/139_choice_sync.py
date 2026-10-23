# v174: opening a choice must survive a fresh copy of the same open case arriving.
import os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *

with sync_playwright() as p:
    a=App(p); pg=a.pg
    cid=a.start('I need to fill in the application form')
    a.open(cid)
    pg.locator('.now137 [data-p=later]').click(); wait(pg, 100)
    ok(pg.locator('.q130-later').is_visible(), 'Can’t do this now opens the Later choices')
    chosen=(datetime.date.today()+datetime.timedelta(days=5)).isoformat()
    pg.locator('.q130-later input[type=date]').fill(chosen)
    pg.evaluate('draw143([{id:S.view.id,k:"adopt"}])'); wait(pg, 100)
    ok(pg.locator('.q130-later').is_visible() and pg.locator('.q130-later input[type=date]').input_value()==chosen and pg.evaluate('S.view.panel')=='later', 'same-case sync keeps the choice and chosen day')
    pg.locator('.q130-later [data-a=q-close]').click(); wait(pg, 100)
    pg.locator('.now137 [data-p=changed]').click(); wait(pg, 100)
    field=pg.locator('textarea').first
    field.fill('I have not filled in the form yet')
    before=field.input_value()
    field.evaluate('e=>e.blur()')
    pg.evaluate('draw143([{id:S.view.id,k:"adopt"}])'); wait(pg, 100)
    ok(pg.evaluate('S.view.panel')=='changed' and pg.locator('textarea').first.input_value()==before, 'same-case sync keeps the change form and typed words')
    pg.evaluate('S.view.panel=null;S.draft={};render()'); wait(pg, 100)
    pg.locator('.now137 [data-p=later]').click(); wait(pg, 100)
    pg.evaluate('task(S.view.id).board="done";draw143([{id:S.view.id,k:"adopt"}])'); wait(pg, 100)
    ok(pg.evaluate('S.view.panel') is None, 'a finished case still dismisses an obsolete choice')
    a.b.close()
print('ERRORS',errs);print('FAILS',fails)
