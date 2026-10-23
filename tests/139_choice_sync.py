# v174: opening a choice must survive a fresh copy of the same open case arriving.
import os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *

def remote_update(pg, cid, finished=False):
    pg.evaluate("""({id,finished})=>{
      var db=JSON.parse(localStorage.getItem('__mockdb'));
      var row=db.tasks.find(x=>x.data&&x.data.id===id),t=row.data;
      t.rev=(t.rev||0)+1;t.updatedAt=new Date().toISOString();
      t.events=(t.events||[]).concat([{at:t.updatedAt,label:'A second device updated this case.'}]);
      if(finished)t.board='done';
      localStorage.setItem('__mockdb',JSON.stringify(db));
      window.dispatchEvent(new Event('online'));
    }""", {'id': cid, 'finished': finished})
    wait(pg, 700)

with sync_playwright() as p:
    a=App(p); pg=a.pg
    cid=a.start('I need to fill in the application form')
    a.open(cid)
    pg.locator('.now137 [data-p=later]').click(); wait(pg, 100)
    ok(pg.locator('.q130-later').is_visible(), 'Can’t do this now opens the Later choices')
    chosen=(datetime.date.today()+datetime.timedelta(days=5)).isoformat()
    pg.locator('.q130-later input[type=date]').fill(chosen)
    remote_update(pg, cid)
    ok(pg.locator('.q130-later').is_visible() and pg.locator('.q130-later input[type=date]').input_value()==chosen, 'same-case sync keeps the choice and chosen day')
    pg.locator('.q130-later [data-a=q-close]').click(); wait(pg, 100)
    pg.locator('.now137 [data-p=changed]').click(); wait(pg, 100)
    remote_update(pg, cid)
    ok(pg.locator('.q130-changed').is_visible(), 'same-case sync keeps the Something changed choices')
    pg.locator('.q130-changed [data-a=sc-own]').click(); wait(pg, 100)
    field=pg.locator('#f-paste')
    field.fill('I have not filled in the form yet')
    before=field.input_value()
    field.evaluate('e=>e.blur()')
    remote_update(pg, cid)
    ok(pg.locator('#f-paste').input_value()==before and pg.get_by_text('What’s changed?').count()==1, 'same-case sync keeps the change form and typed words')
    pg.locator('form[data-f=paste] [data-p=""]').click(); wait(pg, 100)
    pg.locator('.now137 [data-p=later]').click(); wait(pg, 100)
    remote_update(pg, cid, True)
    ok(pg.locator('.q130-later').count()==0, 'a finished case still dismisses an obsolete choice')
    a.b.close()
print('ERRORS',errs);print('FAILS',fails)
