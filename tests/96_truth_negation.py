# v139: a negated alternative must not erase the actual date. "Wednesday, not Tuesday" keeps Wednesday; a sentence
# with only "not Tuesday" has no positive date. This closes the edge found during review of the truth-integrity patch.
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]; n=[0]
def ok(c,m):
    n[0]+=1; print(('PASS ' if c else 'FAIL ')+m)
    if not c:fails.append(m)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    pg.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/reader.html',content_type='text/html'))
    pg.goto('https://sorted.test/')
    def read(text):
        return pg.evaluate("t=>{var f=__read.caseFacts(t),r=__read.readCase(t,f);return r?{due:r.dueAt||null,src:r.sourceWhen||'',prec:r.precision||'',tent:!!r.tentative,cand:r.candidateDueAt||null}:null}",text)
    r=read('Sky said the engineer is coming Wednesday, not Tuesday') or {}
    ok(r.get('due') and r.get('prec')=='exact_day' and 'Wednesday' in r.get('src',''),'Wednesday, not Tuesday keeps the positive Wednesday (%s)'%json.dumps(r))
    r=read('Virgin said the engineer would come, but not Tuesday') or {}
    ok(not r.get('due'),'not Tuesday on its own never becomes a positive appointment (%s)'%json.dumps(r))
    r=read('EE said the engineer would probably come Tuesday, not Wednesday') or {}
    ok(r.get('tent') and r.get('cand') and not r.get('due') and 'Tuesday' in r.get('src',''),'probably Tuesday, not Wednesday stays tentative Tuesday (%s)'%json.dumps(r))
    ok(not errs,'no page errors: %s'%errs)
    print('CHECKS',n[0]); b.close()
print('ERRORS',errs); print('FAILS',fails)
