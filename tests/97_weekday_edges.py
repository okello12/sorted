# v140: weekday edge cases are stable on every day of the week.
# A no-show on the named weekday is a missed visit, not a future appointment; a bare weekday correction is resolved
# beside the appointment being corrected, not beside today's date.
import os
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]; n=[0]
def ok(c,m):
    n[0]+=1; print(('PASS ' if c else 'FAIL ')+m)
    if not c:fails.append(m)
def wait(pg,ms=250): pg.wait_for_timeout(ms)
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(timezone_id='Europe/London')
    rd=ctx.new_page()
    rd.route(lambda u:u.startswith('https://sorted.test/'),lambda q:q.fulfill(path=HERE+'/tests/out/reader.html',content_type='text/html'))
    rd.on('pageerror',lambda e:errs.append(str(e)))
    rd.goto('https://sorted.test/'); wait(rd,400)

    no_show=rd.evaluate("""()=>{
      var names=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'],wd=names[new Date().getDay()];
      var text='Landlord said an engineer would come on '+wd+' to fix the boiler but nobody turned up';
      var f=__read.caseFacts(text),r=__read.readCase(text,f);
      return r?{due:r.dueAt,past:!!r.past,text:text}:null;
    }""")
    ok(no_show and no_show['past'] and rd.evaluate("(x)=>new Date(x)<new Date()",no_show['due']),
       'a same-weekday explicit no-show is already missed (%s)'%no_show)

    rel=rd.evaluate("""()=>{
      var days=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'],now=new Date(),base=new Date(now);
      var want=2,add=(want-base.getDay()+7)%7;if(!add)add=7;base.setDate(base.getDate()+add);base.setHours(8,0,0,0);
      var end=new Date(base);end.setHours(12,0,0,0);
      var cur={party:'Sky',ref:'AB123',dueAt:base.toISOString(),dueEnd:end.toISOString(),allDay:false,by:false};
      var a=__read.corrRead(cur,'Sorry, I meant Wednesday');
      var wed=a&&new Date(a.dueAt||a.to),cur2=Object.assign({},cur,{dueAt:a&&(a.dueAt||a.to),dueEnd:a&&a.dueEnd});
      var b=__read.corrRead(cur2,'They moved it to Thursday'),thu=b&&new Date(b.dueAt||b.to);
      return {base:base.toISOString(),wed:wed&&wed.toISOString(),wedEnd:a&&a.dueEnd,thu:thu&&thu.toISOString(),
              d1:wed&&Math.round((wed-base)/86400000),d2:thu&&wed&&Math.round((thu-wed)/86400000),
              wh:wed&&wed.getHours(),we:a&&a.dueEnd&&new Date(a.dueEnd).getHours(),moved:!!(b&&b.moved)};
    }""")
    ok(rel and rel['d1']==1 and rel['wh']==8 and rel['we']==12,
       'bare Wednesday correction stays beside the future Tuesday and preserves its slot (%s)'%rel)
    ok(rel and rel['d2']==1 and rel['moved'],
       'provider move to Thursday stays beside the corrected Wednesday and remains a reschedule (%s)'%rel)

    ok(not errs,'no page errors: %s'%errs)
    print('CHECKS',n[0])
    b.close()
print('ERRORS',errs);print('FAILS',fails)
