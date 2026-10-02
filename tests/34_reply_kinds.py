# v72: when a reply comes into a case, the server reads what kind it is with the page's own patterns
# (supabase/functions/inbound-email/readers.mjs, made by tools/make_server_reader.js) and emails the owner without details.
import os, sys, json, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=350): pg.wait_for_timeout(ms)
RD = 'supabase/functions/inbound-email/readers.mjs'
# 1 the server's patterns are the page's patterns
tmp = os.path.join(tempfile.mkdtemp(), 'r.mjs')
subprocess.run(['node', 'tools/make_server_reader.js', tmp], check=True)
ok(open(tmp).read() == open(RD).read(), 'readers.mjs is up to date with the page (run node tools/make_server_reader.js)')
# 2 what kind of reply
CASES = [
    ("Your challenge has been rejected. The penalty charge remains payable.", "rejected"),
    ("We are unable to accept your representations.", "rejected"),
    ("The PCN will not be cancelled.", "rejected"),
    ("We have cancelled the PCN. No further action will be taken.", "cancelled"),
    ("Your appeal has been accepted.", "cancelled"),
    ("We have received your challenge.", "ack"),
    ("Thank you, we acknowledge receipt of your email.", "ack"),
    ("Sorry for the delay. Your refund will be processed within 5 working days.", "date"),
    ("The engineer will come on Friday between 8 and 12.", "date"),
    ("We expect the replacement to arrive by 14 October.", "date"),
    ("Thanks for your email. Please call us on the number below.", "other"),
    ("Our office is closed on Friday.", "other"),
]
js = "import {replyKind} from './%s'; const c=JSON.parse(process.argv[1]); console.log(JSON.stringify(c.map(x=>replyKind(x))))" % RD
got = json.loads(subprocess.run(['node', '--input-type=module', '-e', js, json.dumps([c[0] for c in CASES])], capture_output=True, text=True, check=True).stdout)
for (t, want), g in zip(CASES, got): ok(g == want, '%s: %s' % (want, t))
# 3 the email never carries the case, the sender or the reply
src = open('supabase/functions/inbound-email/index.ts').read()
nb = src[src.index('async function notify('):src.index('// v4 (Sorted v70)')]
ok('replyKind(' in src and 'import { replyKind } from "./readers.mjs"' in src, 'inbound-email uses the shared reader')
ok(not any(w in nb for w in ['d.subject', 'd.from', 'fromDomain', 'bodyText', 'text || ']) and 'subject: "A reply came into one of your Sorted cases"' in nb, 'the notification is built only from the kind: no subject, sender or words from the reply')
ok('kind === "ack"' in nb and 'email_optouts' in nb and '6 * 3600000' in src, 'no email for an acknowledgement, after opting out, or more than once in 6 hours per case')
# 4 the page: opening from that email counts as a return, and the notice says what is sent
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 200); pg.click('[data-a=anon-start]'); wait(pg)
    pg.fill('#f-case', "Currys refund hasn't arrived, order 445566"); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    cid = pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks[0].data.id")
    pg.goto('https://sorted.test/?task=%s&src=reply' % cid); wait(pg, 700)
    ev = pg.evaluate("JSON.parse(localStorage.getItem('__mockdb')).tasks[0].data.events")
    ok(any(e.get('kind') == 'return' and e.get('src') == 'reply' and e['label'].startswith('Opened from the reply link') for e in ev), 'opening the case from the reply email counts as a return')
    pg.goto('https://sorted.test/'); wait(pg, 400); pg.click('text=Your data'); wait(pg)
    ok('That email never says which case, who sent it or what it says.' in pg.inner_text('main'), 'the privacy notice says what the reply email contains')
    b.close()
print('ERRORS', errs); print('FAILS', fails)
