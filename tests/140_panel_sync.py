# v175: a fresh revision must not throw away work on other case and Home screens.
import os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *

def remote_update(pg, cid, finished=False):
    pg.evaluate("""({id,finished})=>{
      var db=JSON.parse(localStorage.getItem('__mockdb'));
      var t=db.tasks.find(x=>x.data&&x.data.id===id).data;
      t.rev=(t.rev||0)+1;t.updatedAt=new Date().toISOString();
      t.events=(t.events||[]).concat([{at:t.updatedAt,label:'A second device added a note.'}]);
      if(finished)t.board='done';
      localStorage.setItem('__mockdb',JSON.stringify(db));window.dispatchEvent(new Event('online'));
    }""", {'id':cid,'finished':finished})
    wait(pg, 700)

def panel(pg, name):
    pg.evaluate("""(name)=>{var el=document.querySelector('[data-a="panel"][data-p="'+name+'"]');
      if(!el)throw Error('missing panel control '+name);el.click()}""", name)
    wait(pg, 150)

with sync_playwright() as p:
    a=App(p);pg=a.pg
    cid=a.start('I need to contact HMRC about my tax account')
    for name, field, words in [('rename','#f-rename','My tax question'),('done','#f-outcome','I asked for a written answer'),('move','#f-mwhat','Call HMRC on Monday')]:
        a.open(cid);panel(pg,name)
        pg.locator(field).fill(words);pg.locator(field).evaluate('e=>e.blur()')
        remote_update(pg,cid)
        ok(pg.locator(field).count()==1 and pg.locator(field).input_value()==words, name+' form and its words survive an account refresh')
    a.open(cid);panel(pg,'delcase');remote_update(pg,cid)
    ok(pg.get_by_role('heading',name='Delete this case?').count()==1,'delete confirmation does not vanish before a choice')

    # A Home quick-answer sheet is also an open choice, with its own selected day.
    a.task_js(cid,"t.mode='call';t.board='waiting';t.promises=[{id:'p-sync',party:'HMRC',said:'We will reply',status:'open',dueAt:new Date(Date.now()-2*864e5).toISOString(),dueEnd:null,allDay:true,by:true,loggedAt:new Date(Date.now()-3*864e5).toISOString()}];t.moves=[]")
    a.home()
    q=pg.locator('[data-a=q-later][data-qid="%s"]'%cid)
    ok(q.count()==1,'overdue promise has a quick Later choice on Home')
    if q.count():
        q.click();wait(pg,150)
        chosen=(datetime.date.today()+datetime.timedelta(days=5)).isoformat()
        pg.locator('.q130-later input[type=date]').fill(chosen)
        remote_update(pg,cid)
        ok(pg.locator('.q130-later').count()==1 and pg.locator('.q130-later input[type=date]').input_value()==chosen,'Home quick choice and its date survive an account refresh')
    a.b.close()
print('ERRORS',errs);print('FAILS',fails)
