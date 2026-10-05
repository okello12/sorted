# v133: reminders on the lock screen. "Get reminders on this phone" asks the phone, saves its push address with
# push_save, and from then on a case with a date gets its reminder rows even without an email; Settings says it is on
# and can turn it off (push_drop). On an iPhone outside the Home Screen it explains how to add Sorted there. Once a case
# has a date, Sorted offers the lock screen and (to a guest) an email, once. A reminder's Later and New date links open
# the case at those questions; a tap on a notification counts as a return. The service worker caches nothing, and
# the push encryption matches RFC 8291 (tests/webpush_check.mjs).
import os, sys, json, datetime, subprocess, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
today = datetime.date.today()
fri = today + datetime.timedelta(days=(4 - today.weekday()) % 7 or 7)
STUB = """
(()=>{
  var perm='default';
  try{Object.defineProperty(Notification,'permission',{get:()=>perm});Notification.requestPermission=function(){perm=localStorage.getItem('__permAnswer')||'granted';return Promise.resolve(perm)}}catch(e){}
  var sub=null,reg={scope:'/',pushManager:{getSubscription:()=>Promise.resolve(sub),subscribe:o=>{window.__subOpts={uvo:o.userVisibleOnly,keyLen:o.applicationServerKey.length};var k=localStorage.getItem('__subN')||'1';sub={endpoint:'https://fcm.googleapis.com/fcm/send/test-'+k,toJSON:()=>({endpoint:sub.endpoint,keys:{p256dh:'B'+'x'.repeat(86),auth:'a'.repeat(22)}}),unsubscribe:()=>{sub=null;return Promise.resolve(true)}};return Promise.resolve(sub)}}};
  var registered=false;
  try{Object.defineProperty(navigator,'serviceWorker',{get:()=>({register:(u,o)=>{window.__swUrl=u;registered=true;return Promise.resolve(reg)},ready:Promise.resolve(reg),getRegistration:()=>Promise.resolve(registered?reg:undefined)})})}catch(e){}
  if(!('PushManager' in window))window.PushManager=function(){};
})();
"""
IOS = "Object.defineProperty(navigator,'userAgent',{get:()=>'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1'});delete window.PushManager;"
with sync_playwright() as p:
    b = p.chromium.launch()
    def ctx_for(extra):
        c = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
        c.add_init_script(extra)
        c.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
        c.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
        return c
    ctx = ctx_for(STUB); pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    main = lambda: pg.inner_text('main')
    tap = lambda a: (pg.locator('.tab129 [data-a=%s]' % a).click(), wait(pg, 500))
    def start(text):
        tap('new-case')
        pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
        return cases()[-1]['id']
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1');localStorage.setItem('__pushReady','1')")
    pg.goto('https://sorted.test/#start'); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    # ---- once a case has a date: the offer, once ----
    c1 = start('Currys said they would refund £89 by %s, order 445566' % fri.strftime('%A'))
    pg.goto('https://sorted.test/?task=%s' % c1); wait(pg, 700)
    ng = pg.locator('.nudge133')
    ok(ng.count() == 1 and 'Want Sorted to tell you when it’s due?' in ng.inner_text() and ng.locator('[data-a=push-on]').count() == 1 and ng.locator('[data-a=go-claim]').count() == 1, 'a case with a date offers the lock screen and, to a guest, an email')
    ok(not [r for r in dbj().get('reminders', []) if r['task_id'] == c1], 'before that, a guest’s case has no reminder rows (no email, no phone)')
    # ---- switch it on ----
    ng.locator('[data-a=push-on]').click(); wait(pg, 800)
    subs = dbj().get('push_subs', [])
    ok(len(subs) == 1 and subs[0]['endpoint'].startswith('https://fcm.googleapis.com/') and pg.evaluate('window.__swUrl') == '/sw.js', 'Get reminders on this phone registers /sw.js and saves this phone’s push address')
    ok(pg.evaluate('window.__subOpts') == {'uvo': True, 'keyLen': 65}, 'it asks for visible notifications with Sorted’s public key')
    ok([r for r in dbj().get('reminders', []) if r['task_id'] == c1], 'the open case now has its reminder rows, with no email needed')
    ok(pg.locator('.nudge133 [data-a=push-on]').count() == 0 and pg.locator('.nudge133 [data-a=go-claim]').count() == 1, 'the lock-screen offer has gone; the email offer stays for a guest')
    c2 = start('Sky said an engineer would come on %s, ref SKY12345' % fri.strftime('%A'))
    ok([r for r in dbj().get('reminders', []) if r['task_id'] == c2], 'a new case with a date gets reminder rows straight away')
    tap('data'); pg.click('.acct112-nav [data-v=acct-settings]'); wait(pg, 400)
    pb = pg.locator('.push133')
    ok(pb.count() == 1 and pb.get_attribute('data-push') == 'on' and 'doesn’t say what the case is' in pb.inner_text(), 'Settings says reminders are on for this phone and that they don’t say what the case is')
    pb.locator('[data-a=push-off]').click(); wait(pg, 600)
    ok(not dbj().get('push_subs') and pg.locator('.push133').get_attribute('data-push') == 'off', 'Turn them off on this phone removes its push address')
    # ---- blocked, and the offer once only ----
    pg.evaluate("localStorage.setItem('__permAnswer','denied')"); pg.click('.push133 [data-a=push-on]'); wait(pg, 600)
    ok(pg.locator('.push133').get_attribute('data-push') == 'denied' and 'blocked' in pg.inner_text('.push133'), 'if the phone blocks notifications, Settings says how to allow them')
    c3 = start('Amazon said they would refund £20 by %s, ref AMZ12345' % fri.strftime('%A'))
    pg.goto('https://sorted.test/?task=%s' % c3); wait(pg, 700)
    if pg.locator('.nudge133').count(): pg.click('.nudge133 [data-a=nudge-skip]'); wait(pg, 300)
    pg.goto('https://sorted.test/?task=%s' % c1); wait(pg, 700)
    ok(pg.locator('.nudge133').count() == 0, 'Maybe later means the offer doesn’t come back')
    # ---- answers from a reminder: Later, New date, and a tap on the notification ----
    pg.goto('https://sorted.test/?task=%s&src=email&ans=later&p=x' % c1); wait(pg, 900)
    ok(pg.locator('.q130-later').count() == 1, 'Later in a reminder opens the case at “When should Sorted bring it back?”')
    pg.goto('https://sorted.test/?task=%s&src=email&ans=date&p=x' % c1); wait(pg, 900)
    ok(pg.locator('form[data-f=qdate]').count() == 1, 'New date in a reminder opens the case at “What’s the new date?”')
    pg.goto('https://sorted.test/?task=%s&src=push' % c2); wait(pg, 900)
    ev = [e for c in cases() if c['id'] == c2 for e in c['events']]
    ok(pg.locator('main.case56').count() == 1 and any(e.get('kind') == 'return' and e.get('src') == 'push' and 'notification' in e['label'] for e in ev), 'a tap on the notification opens the case and counts as coming back')
    ctx.close()
    # ---- an iPhone outside the Home Screen ----
    ctx = ctx_for(IOS); pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__pushReady','1')")
    pg.goto('https://sorted.test/#start'); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    pg.locator('.tab129 [data-a=data]').click(); wait(pg, 400); pg.click('.acct112-nav [data-v=acct-settings]'); wait(pg, 400)
    ok(pg.locator('.push133').count() == 1 and pg.locator('.push133').get_attribute('data-push') == 'needhome' and 'Add to Home Screen' in pg.inner_text('.push133'), 'on an iPhone in Safari, Settings explains Add to Home Screen first')
    ctx.close()
    # ---- the service worker and the encryption ----
    sw = open(HERE + '/public/sw.js').read()
    ok('showNotification' in sw and 'notificationclick' in sw and 'caches.' not in sw and 'addEventListener("fetch"' not in sw, 'the service worker shows notifications and opens the case, and caches nothing')
    r = subprocess.run(['node', '--experimental-strip-types', HERE + '/tests/webpush_check.mjs'], capture_output=True, text=True)
    ok('FAILS []' in r.stdout and r.stdout.count('PASS') == 3, 'the push encryption matches RFC 8291 and the VAPID header verifies')
    r = subprocess.run(['node', '--experimental-strip-types', HERE + '/tests/fn/send_reminders_check.mjs'], capture_output=True, text=True)
    ok('FAILS []' in r.stdout and r.stdout.count('PASS') == 10, 'send-reminders, run in Node: push to a guest, no case words in it, email with Later and New date, a forgotten phone removed (%d passes)' % r.stdout.count('PASS'))
    pg_src = open(HERE + '/public/index.html').read()
    ok(re.search(r'var VAPID_PUB="B[\w-]{86}"', pg_src) is not None and 'vapid_private' not in pg_src, 'the page carries only the public VAPID key')
    ok(not errs, 'no page errors: %s' % errs)
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
