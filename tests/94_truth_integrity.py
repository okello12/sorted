# v138: truth integrity. What was said, Sorted's interpretation, confirmed details, the person's own reminder/plan and
# an outbound draft stay separate. Vague/tentative dates never become firm appointments; checking an existing booking
# happens before a chase; guest save wording matches the real storage model; legacy vague dates are reviewed, not erased.
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE=os.path.abspath('.'); errs=[]; fails=[]; n=[0]
def ok(c,m):
    n[0]+=1; print(('PASS ' if c else 'FAIL ')+m)
    if not c:fails.append(m)
def wait(pg,ms=450): pg.wait_for_timeout(ms)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(timezone_id='Europe/London',viewport={'width':390,'height':844})
    ctx.grant_permissions(['clipboard-read','clipboard-write'],origin='https://sorted.test')
    ctx.route('https://cdn.jsdelivr.net/**',lambda r:r.fulfill(path=HERE+'/tests/mock.js',content_type='application/javascript'))
    ctx.route(lambda u:u.startswith('https://sorted.test/'),lambda r:r.fulfill(path=HERE+'/tests/out/index.html',content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))
    dbj=lambda:pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases=lambda:sorted([x['data'] for x in dbj().get('tasks',[]) if x['data'].get('kind')!='moment'],key=lambda x:x.get('created') or '')
    case=lambda cid:[x for x in cases() if x['id']==cid][0]
    main=lambda:pg.inner_text('main')
    def start(text,confirm=False):
        pg.goto('https://sorted.test/'); wait(pg,600)
        if pg.locator('.tab129 [data-a=new-case]').count(): pg.locator('.tab129 [data-a=new-case]').click(); wait(pg,350)
        if not pg.locator('#f-case').count() and pg.locator('[data-a=new-case]').count(): pg.locator('[data-a=new-case]').first.click(); wait(pg,350)
        if pg.locator('[data-cap82=other]').count(): pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg,250)
        pg.fill('#f-case',text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg,650)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg,450)
        if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg,450)
        if pg.locator('form[data-f=baseline]').count():
            pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg,500)
        cid=cases()[-1]['id']
        if confirm and pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg,650)
        if pg.locator('[data-a=nudge-skip]').count(): pg.click('[data-a=nudge-skip]'); wait(pg,250)
        return cid
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg,300); pg.click('[data-a=anon-start]'); wait(pg,750)
    uid=pg.evaluate("JSON.parse(localStorage.getItem('__mocksession')).user.id")

    # 1. The exact source phrase and the derived window are both kept. Checking an existing booking is the next action.
    src="They said an engineer would come sometime next week. I haven't checked whether the booking is in their app."
    c1=start(src,False); t=case(c1); sp=t.get('sugP') or {}
    ok(sp.get('win') and sp.get('precision')=='window' and sp.get('sourceWhen','').lower()=='sometime next week','sometime next week remains a window, with its source phrase (%s)'%json.dumps({k:sp.get(k) for k in ('win','precision','sourceWhen')}))
    ok(sp.get('sourceText')==src,'the original wording is kept separately')
    m=main()
    ok('What was actually said' in m and 'sometime next week' in m and 'There is no confirmed appointment day' in m,'the screen separates source wording from interpretation')
    ok('check the provider’s app and latest email for the booking' in m.lower() and 'get the call ready' not in m.lower(),'checking existing information comes before contacting the provider')
    ok(pg.locator('[data-a=truth-check-found]').count()==1 and pg.locator('[data-a=truth-check-none]').count()==1 and pg.locator('[data-a=truth-remind]').count()==1,'the three fast outcomes are available')
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg,650)
    t=case(c1); op=[q for q in t.get('promises',[]) if q.get('status')=='open'][0]; due0=op.get('dueAt'); end0=op.get('dueEnd')
    ok(op.get('win') and op.get('sourceWhen','').lower()=='sometime next week','confirmation keeps the promise as a window rather than a firm Friday')

    # 2. A user's reminder is an attention choice, not the provider's appointment.
    pg.goto('https://sorted.test/?task=%s'%c1); wait(pg,600); pg.click('[data-a=truth-remind]'); wait(pg,350)
    ok("Can’t do this now?" in main(),'Remind me to check opens the user-reminder picker')
    if pg.locator('[data-a=q-snooze]').count(): pg.locator('[data-a=q-snooze]').first.click(); wait(pg,600)
    t=case(c1); op=[q for q in t.get('promises',[]) if q.get('status')=='open'][0]
    ok(t.get('snooze') and op.get('dueAt')==due0 and op.get('dueEnd')==end0,'the reminder is separate; the provider timing is unchanged')
    pg.goto('https://sorted.test/?task=%s'%c1); wait(pg,550)
    ok('This is when you chose to check. It is not the provider’s appointment.' in main(),'the reminder is labelled as the user’s choice, not their appointment')

    # 3. If checking finds nothing, only then offer a previewed outbound draft. The draft is not evidence.
    pg.click('[data-a=truth-check-none]'); wait(pg,600); t=case(c1)
    ok(t.get('truthCheck',{}).get('status')=='none' and t.get('truthPlan',{}).get('st')=='done','checking the app/email is recorded as the completed user step')
    ok('Prepare a message' in main(),'after no booking is found, Sorted offers contact')
    before=json.dumps(t,sort_keys=True)
    pg.click('[data-a=truth-draft]'); wait(pg,300); m=main()
    ok('Draft — check before sending' in m and 'This is Sorted’s proposed message' in m,'a generated message is visibly a draft, not source evidence')
    draft=pg.input_value('#truth138-draft')
    ok('sometime next week' in draft.lower() and 'confirm the appointment day, time window and booking reference' in draft.lower(),'the draft quotes the uncertainty and asks for confirmation')
    ok('call' not in draft.lower(),'an app/email check does not silently become a call')
    after=json.dumps(case(c1),sort_keys=True)
    ok(before==after,'opening the outbound draft changes no case facts or history')

    # 4. A tentative day is not promoted to an appointment/deadline.
    c2=start('Sky said an engineer would probably come Tuesday.',False); t=case(c2); sp=t.get('sugP') or {}
    ok(sp.get('tentative') and sp.get('precision')=='tentative' and sp.get('candidateDueAt') and not sp.get('dueAt'),'probably Tuesday is a candidate day, not a confirmed appointment (%s)'%json.dumps({k:sp.get(k) for k in ('tentative','precision','candidateDueAt','dueAt')}))
    ok('not a confirmed appointment' in main().lower() and 'probably' in main().lower(),'the UI describes the day as tentative')
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg,600)
    t=case(c2); opens=[q for q in t.get('promises',[]) if q.get('status')=='open']
    if opens:
        q=opens[0]; ok(q.get('tentative') and not q.get('dueAt') and q.get('candidateDueAt'),'confirming what was said does not turn probably Tuesday into a firm Tuesday')
    else: ok(True,'the tentative statement stays unconfirmed rather than becoming a dated promise')

    # 5. A negated day can never become the current positive date.
    c3=start('Virgin said an engineer would come, but not Tuesday.',False); t=case(c3); cand=[]
    if t.get('sugP'): cand.append(t['sugP'])
    cand += [q for q in t.get('promises',[]) if q.get('status')=='open']
    ok(not any(q.get('dueAt') for q in cand),'not Tuesday never becomes a positive Tuesday deadline')

    # 6. Anonymous save language describes the real storage model and a failed write never displays Saved.
    pg.goto('https://sorted.test/?task=%s'%c1); wait(pg,900)
    sync=pg.locator('[data-sync="%s"]'%c1).inner_text() if pg.locator('[data-sync="%s"]'%c1).count() else ''
    ok('Saved. You can reopen it in this browser.' in sync and 'Saved to your account' not in sync,'guest success copy does not claim an account')
    pg.evaluate("localStorage.setItem('__failWrites','1')")
    c4=start("BT said an engineer would come sometime next week. I haven't checked the latest email.",True)
    pg.goto('https://sorted.test/?task=%s'%c4); wait(pg,450)
    if pg.locator('[data-a=truth-check-none]').count(): pg.click('[data-a=truth-check-none]'); wait(pg,800)
    sync=pg.locator('[data-sync="%s"]'%c4).inner_text() if pg.locator('[data-sync="%s"]'%c4).count() else ''
    ok('not yet sent' in sync.lower() and 'Saved. You can reopen' not in sync,'a refused server write never displays the success state (%s)'%sync)
    pg.evaluate("localStorage.removeItem('__failWrites')")

    # 7. A pre-v107 vague date stored as a firm day is flagged for review. Saying there was no firm date preserves the old row.
    oldday=(datetime.date.today()+datetime.timedelta(days=5)).isoformat()
    old={'id':'legacy-vague','title':'Virgin · engineer','mode':'call','board':'waiting','created':'2026-09-01T10:00:00.000Z','updatedAt':'2026-09-01T10:00:00.000Z','rev':2,
         'said':'Virgin said an engineer would come sometime next week','facts':{'party':'Virgin','kind':'service'},'moves':[],'events':[{'at':'2026-09-01T10:00:00.000Z','label':'Started.'}],
         'promises':[{'id':'legacy-p','said':'An engineer would come','party':'Virgin','ref':'','dueAt':oldday+'T00:00:00.000Z','dueEnd':None,'allDay':True,'by':True,'status':'open','loggedAt':'2026-09-01T10:00:00.000Z','src':'sentence'}]}
    pg.goto('https://sorted.test/'); wait(pg,500)
    pg.evaluate("([u,x])=>{var d=JSON.parse(localStorage.getItem('__mockdb'));d.tasks.push({id:x.id,user_id:u,data:x,updated_at:new Date().toISOString()});localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}",[uid,old])
    pg.goto('https://sorted.test/?task=legacy-vague'); wait(pg,900); t=case('legacy-vague')
    ok(t['promises'][0].get('legacyTimingReview') and 'Please check this date against the original message.' in main(),'a legacy vague phrase stored as a firm date is visibly flagged')
    pg.click('[data-a=truth-date-none]'); wait(pg,650); t=case('legacy-vague'); oldp=[q for q in t['promises'] if q['id']=='legacy-p'][0]; newp=[q for q in t['promises'] if q['status']=='open'][0]
    ok(oldp['status']=='replaced' and oldp.get('dueAt') and not newp.get('dueAt'),'review keeps the old dated promise in history and makes the current promise undated')
    ok(any('There was no confirmed date' in (e.get('label') or '') for e in t.get('events',[])),'the review is recorded as a user correction, not a provider reschedule')

    # 8. Finding the booking refines the vague promise without recording a provider-side reschedule.
    c5=start("EE said an engineer would come sometime next week. I haven't checked whether it is in the app.",True)
    t=case(c5); oldid=[q for q in t.get('promises',[]) if q.get('status')=='open'][0]['id']; before_res=len([e for e in dbj().get('pilot_events',[]) if e.get('name')=='outcome_rescheduled' and e.get('case_id')==c5])
    pg.goto('https://sorted.test/?task=%s'%c5); wait(pg,550); pg.click('[data-a=truth-check-found]'); wait(pg,250)
    found=(datetime.date.today()+datetime.timedelta(days=3)).isoformat(); pg.fill('.truth138-found input[name=tdate]',found); pg.fill('.truth138-found input[name=tref]','EE-7788'); pg.click('.truth138-found button[type=submit]'); wait(pg,700)
    t=case(c5); oldp=[q for q in t['promises'] if q['id']==oldid][0]; newp=[q for q in t['promises'] if q['status']=='open'][0]
    after_res=len([e for e in dbj().get('pilot_events',[]) if e.get('name')=='outcome_rescheduled' and e.get('case_id')==c5])
    ok(oldp['status']=='replaced' and newp.get('precision')=='exact_day' and newp.get('ref')=='EE-7788','a found booking becomes the current confirmed booking and preserves the earlier vague promise')
    ok(after_res==before_res and any('found the booking' in (e.get('label') or '').lower() for e in t.get('events',[])),'finding existing information is not misrecorded as the provider rescheduling')

    ok(not errs,'no page errors: %s'%errs)
    print('CHECKS',n[0]); b.close()
print('ERRORS',errs); print('FAILS',fails)
