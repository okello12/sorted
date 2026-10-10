# v167: from Baldwin's iPhone. A "Heating or hot water" case showed "What is it, and what’s it doing?" with "What is
# it?" empty, because tapping "Something else" (already the choice shown) wiped the name. "Something else" now keeps
# the case's own name, Washing machine and back restores it, and a repair saved with no name is named from its words.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *
with sync_playwright() as p:
    a = App(p, email=False); pg = a.pg
    a.home()
    cid = a.start('My heating isn’t working', False)
    def val(): return pg.input_value('#f-item') if pg.locator('#f-item').count() else None
    a.open(cid); m = a.main()
    ok(val() == 'Heating or hot water' and 'What is it, and' not in m and 'Can you smell gas' in m, 'the case opens with its name and the gas question')
    pg.locator('form[data-f=what] .chip[data-k=item]', has_text='Something else').click(); wait(pg, 300); m = a.main()
    ok(val() == 'Heating or hot water' and 'What is it, and' not in m and 'Can you smell gas' in m, 'tapping “Something else” keeps the name')
    pg.locator('form[data-f=what] .chip[data-k=item]', has_text='Washing machine').click(); wait(pg, 300)
    pg.locator('form[data-f=what] .chip[data-k=item]', has_text='Something else').click(); wait(pg, 300)
    ok(val() == 'Heating or hot water', 'Washing machine and back brings the name back')
    pg.locator('form[data-f=what] button[type=submit]').click(); wait(pg, 600)
    ok(a.case(cid)['fix']['item'] == 'Heating or hot water' and a.case(cid)['fix']['step'] == 'who', 'carrying on keeps it')
    # a repair saved with no name is named from its words
    cid2 = a.start('The boiler keeps losing pressure', False)
    a.task_js(cid2, "t.fix.item='';")
    a.open(cid2); m = a.main()
    ok(val() == 'Heating or hot water' and 'What is it, and' not in m, 'a case with no name is named from its words')
    pg.locator('form[data-f=what] button[type=submit]').click(); wait(pg, 600)
    ok(a.case(cid2)['fix']['item'] == 'Heating or hot water', 'and carrying on saves the name')
    # typing a different name still works
    cid3 = a.start('My heating isn’t working', False)
    a.open(cid3); pg.fill('#f-item', 'Immersion heater'); pg.locator('form[data-f=what] button[type=submit]').click(); wait(pg, 600)
    ok(a.case(cid3)['fix']['item'] == 'Immersion heater', 'a name typed by the person wins')
    a.close()
finish()
