# v145 (audit pass 3, area C): documents and parking, and the server's contract with the page.
# Real images and PDFs are read by Tesseract and pdf.js (served from tests/node_modules), as in tests 77, 85 and 105.
# C1: bank and card details read from a photo or PDF (sort code, account number, IBAN, card number, NI number) are hidden
#     before they reach the box, the case, its history, references or the adviser pack; the status says so; an energy
#     bill's account number and other references are left alone.
# C2: a file is what its bytes say: a PDF named .jpg and a photo named .pdf are read; a kept document is stored with its
#     real type; an empty file and a text file named .pdf are refused with a reason.
# C3: their reply to a challenge through the parking door says it isn't the notice itself, and creates nothing on its own.
# C4: a notice date written month first gets a hint instead of only "not found".
# C5: when the reader can't start (no connection), the paste panel says so as an alert, with the ways forward.
# C6: a reference printed in spaced groups ("Reference: 4402 7788 1123") is kept whole.
# C7: a corrected reduced amount is saved as typed and marked as yours (it was replaced by the read one when the read
#     one started with the same digits).
# Also: TfL, private (POFA) and Notice to Owner notices; rotated, dark, cropped and glare photos; a two-page PDF, a PDF
# with no text layer and a 20 MB photo; every failure reaches a screen with routes and creates nothing; ten realistic
# reads of receipts, tickets and letters pass the quality check; the CSP covers every outside address the page loads.
# Server: tests/fn/server145_check.mjs (send-reminders v15, inbound-email v8, email-stop, resend-events v2,
# originals-cleanup v3, sw.js) and supabase/parked/25_live_attention_v145.sql run on a throwaway local Postgres when one
# is installed (an attention item or a Later keeps a case alive; migration 23 alone did not).
import os, sys, json, re, datetime, subprocess, tempfile, shutil, glob, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); O = HERE + '/tests/node_modules/'; OUT = HERE + '/tests/out'; errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m, flush=True)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)

# ---- 0 the server functions in Node ----
r = subprocess.run(['node', '--experimental-strip-types', HERE + '/tests/fn/server145_check.mjs'], capture_output=True, text=True)
lines = [l for l in r.stdout.split('\n') if l.startswith('PASS ') or l.startswith('FAIL ')]
ok(r.returncode == 0 and 'FAILS []' in r.stdout and len(lines) >= 26 and not any(l.startswith('FAIL') for l in lines), 'server functions in Node (%d checks): %s' % (len(lines), [l for l in lines if l.startswith('FAIL')] or (r.stderr[-300:] if r.returncode else 'all pass')))

# ---- 1 retention: migration 25 on a throwaway Postgres ----
def pg_check():
    bins = sorted(glob.glob('/usr/lib/postgresql/*/bin/initdb'))
    if not bins: print('NOTE no local Postgres: the retention function was not run here'); return
    B = os.path.dirname(bins[-1]); tmp = tempfile.mkdtemp(prefix='pg145-'); os.chmod(tmp, 0o777)
    pre = ['runuser', '-u', 'nobody', '--'] if os.geteuid() == 0 else []
    port = str(54000 + os.getpid() % 900); user = 'nobody' if os.geteuid() == 0 else None
    try:
        subprocess.run(pre + [B + '/initdb', '-D', tmp + '/d', '-A', 'trust'], check=True, capture_output=True)
        subprocess.run(pre + [B + '/pg_ctl', '-D', tmp + '/d', '-o', "-k %s -p %s -c listen_addresses=''" % (tmp, port), '-l', tmp + '/log', '-w', 'start'], check=True, capture_output=True)
        def sql(q):
            a = [B + '/psql', '-h', tmp, '-p', port, '-d', 'postgres', '-v', 'ON_ERROR_STOP=1', '-At', '-c', q]
            if user: a[1:1] = ['-U', user]
            p = subprocess.run(a, capture_output=True, text=True)
            if p.returncode: raise RuntimeError(p.stderr[-400:])
            return p.stdout.strip()
        sql("create role anon; create role authenticated; create or replace function public.try_ts(t text) returns timestamptz language plpgsql stable set search_path to '' as $$ begin return t::timestamptz; exception when others then return null; end $$;")
        m23 = open(HERE + '/supabase/parked/23_audit_v141.sql').read()
        f23 = re.search(r'create or replace function public\.sorted_case_live\(d jsonb\).*?\n\$\$;', m23, re.S).group(0)
        now = datetime.datetime.now(datetime.timezone.utc)
        iso = lambda d: (now + datetime.timedelta(days=d)).isoformat()
        cases = {
            'check day in 120 days': ({'board': 'waiting', 'promises': [], 'att': [{'id': 'att-1', 'kind': 'check', 'at': iso(120), 'pid': 'p1'}]}, True),
            'Later in 100 days': ({'board': 'yours', 'snooze': {'until': iso(100), 'att': 'att-2'}, 'att': [{'id': 'att-2', 'kind': 'snooze', 'at': iso(100)}]}, True),
            'parking reminder next month': ({'board': 'yours', 'att': [{'id': 'att-pk-payby-x', 'kind': 'remind', 'at': (now + datetime.timedelta(days=30)).date().isoformat()}]}, True),
            'cancelled check day': ({'board': 'waiting', 'att': [{'id': 'att-3', 'kind': 'check', 'at': iso(120), 'cancelled': iso(-1)}]}, False),
            'done check day': ({'board': 'waiting', 'att': [{'id': 'att-4', 'kind': 'check', 'at': iso(120), 'done': iso(-1)}]}, False),
            'finished case': ({'board': 'done', 'att': [{'id': 'att-5', 'kind': 'check', 'at': iso(120)}], 'snooze': {'until': iso(100)}}, False),
            'check day 40 days ago': ({'board': 'waiting', 'att': [{'id': 'att-6', 'kind': 'check', 'at': iso(-40)}]}, False),
            'nothing dated': ({'board': 'yours', 'moves': [{'id': 'm1', 'status': 'open', 'src': 'plan', 'what': 'Check TSB’s website'}]}, False),
            'open promise next week': ({'promises': [{'id': 'p', 'status': 'open', 'dueAt': iso(7)}]}, True),
            'deadline on you': ({'deadline': {'iso': (now + datetime.timedelta(days=20)).date().isoformat()}}, True),
            'garbage att': ({'att': 'nonsense', 'snooze': [1, 2]}, False),
        }
        def run(fn):
            sql(fn); res = {}
            for k, (d, _) in cases.items(): res[k] = sql("select public.sorted_case_live($j$%s$j$::jsonb)" % json.dumps(d)) == 't'
            return res
        before = run(f23); after = run(open(HERE + '/supabase/parked/25_live_attention_v145.sql').read())
        bad = [k for k, (_, want) in cases.items() if after[k] != want]
        ok(not bad, 'migration 25: a live check day, a Later and a parking reminder keep a case; cancelled, done, finished and long-past ones don’t; promises, deadlines and the rest as before: %s' % (bad or 'all as expected'))
        ok(not before['check day in 120 days'] and not before['Later in 100 days'], 'reproduced: before migration 25 a case whose only date was a check day or a Later was removed by the idle clean-up')
        ok(sql("select has_function_privilege('authenticated','public.sorted_case_live(jsonb)','execute')") == 'f', 'the app roles still can’t call it')
    finally:
        subprocess.run(pre + [B + '/pg_ctl', '-D', tmp + '/d', '-m', 'immediate', 'stop'], capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)
pg_check()

# ---- 2 static: CSP and the manifest ----
vj = json.load(open(HERE + '/vercel.json'))
csp = [h['value'] for x in vj['headers'] for h in x['headers'] if h['key'] == 'Content-Security-Policy'][0]
dirs = {d.split()[0]: d.split()[1:] for d in [s.strip() for s in csp.split(';')] if d}
page = open(HERE + '/public/index.html').read()
ocrv = re.search(r'OCRV="([^"]+)"', page).group(1); pdfv = re.search(r'PDFV="([^"]+)"', page).group(1)
need_script = ['https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.117.2/dist/umd/supabase.js', 'https://cdn.jsdelivr.net/npm/tesseract.js@%s/dist/tesseract.min.js' % ocrv,
               'https://cdn.jsdelivr.net/npm/tesseract.js@%s/dist/worker.min.js' % ocrv, 'https://cdn.jsdelivr.net/npm/pdfjs-dist@%s/build/pdf.min.js' % pdfv, 'https://cdn.jsdelivr.net/npm/pdfjs-dist@%s/build/pdf.worker.min.js' % pdfv]
need_connect = ['https://boxrwcuhxmimayaxzywu.supabase.co/rest/v1/tasks', 'wss://boxrwcuhxmimayaxzywu.supabase.co/realtime/v1', 'https://cdn.jsdelivr.net/npm/tesseract.js-core@%s/tesseract-core-simd-lstm.wasm.js' % ocrv,
                'https://cdn.jsdelivr.net/npm/@tesseract.js-data/eng@1.0.0/4.0.0_best_int/eng.traineddata.gz', 'https://cdn.jsdelivr.net/npm/pdfjs-dist@%s/build/pdf.worker.min.js' % pdfv]
covers = lambda srcs, u: any(u.startswith(s) if s.endswith('/') else (u == s or u.startswith(s + '/')) for s in srcs if s.startswith('http') or s.startswith('wss'))
ok(all(covers(dirs['script-src'], u) for u in need_script) and all(covers(dirs['connect-src'], u) for u in need_connect), 'the CSP names every outside script and connection the page uses, by pinned path')
ok("'none'" in dirs.get('object-src', []) and "'none'" in dirs.get('frame-ancestors', []) and dirs.get('worker-src') == ["'self'", 'blob:'], 'objects and framing are refused; workers only from the site or blob:')
mf = json.load(open(HERE + '/public/manifest.webmanifest')); meta = re.search(r'<meta name="description" content="([^"]+)"', page).group(1)
ok(mf['description'].split('. ')[0] == meta.split('. ')[0] == 'Keep everyday admin moving' and 'Keep the details together' in mf['description'], 'the installed app describes Sorted as the site does: %r' % mf['description'])
sw = open(HERE + '/public/sw.js').read()
ok('caches.' not in sw and 'openWindow(url); }); ' not in sw and 'function () { return self.clients.openWindow(url); }' in sw, 'the service worker still caches nothing, and falls back to a new window')

# ---- fixtures ----
H = {'Access-Control-Allow-Origin': '*'}
FAILOCR = [False]; seen = []
def cdn(r):
    u = r.request.url; seen.append(u)
    if FAILOCR[0] and ('tesseract' in u): return r.abort()
    if '/npm/tesseract.js@5.1.1/dist/' in u: return r.fulfill(path=O + 'tesseract.js/dist/' + u.split('/dist/')[1], content_type='application/javascript', headers=H)
    if '/npm/tesseract.js-core@5.1.1/' in u: f = u.split('@5.1.1/')[1]; return r.fulfill(path=O + 'tesseract.js-core/' + f, content_type='application/wasm' if f.endswith('.wasm') else 'application/javascript', headers=H)
    if '/npm/@tesseract.js-data/eng@1.0.0/' in u: return r.fulfill(path=O + '@tesseract.js-data/eng/4.0.0_best_int/eng.traineddata.gz', content_type='application/gzip', headers=H)
    if '/npm/pdfjs-dist@' in u: f = u.split('/npm/pdfjs-dist@3.11.174/')[1]; return r.fulfill(path=O + 'pdfjs-dist/' + f, content_type='application/javascript', headers=H)
    return r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript')
T = datetime.date.today()
def D(k): return T + datetime.timedelta(days=k)
def dmy(d): return d.strftime('%d/%m/%Y')
def lab(d): return '%d %s %d' % (d.day, ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][d.month - 1], d.year)
CONT, NOTICE = D(-4), D(-2)
B = '<body style="margin:0;background:#fff;font-family:Arial;font-size:20px;line-height:1.5;padding:24px;color:#111">'
FX = {
 'tfl': B + '<b>TRANSPORT FOR LONDON</b><br><b>PENALTY CHARGE NOTICE</b><br>PCN number: LN12345678<br>Vehicle registration: AB12 CDE<br>Date of contravention: %s<br>Location: Brixton Road SW9<br>Penalty charge: £160<br>Reduced to £605 if paid within 14 days.<br>Date of notice: %s</body>' % (dmy(CONT), dmy(NOTICE)),
 'pofa': B + '<b>PARKING CHARGE NOTICE</b><br>Notice to Keeper<br>Issued under Schedule 4 of the Protection of Freedoms Act 2012<br>Excel Parking Services Ltd<br>Parking Charge Number: 9876543210<br>Vehicle Registration: AB12 CDE<br>Date of event: %s<br>Parking charge: £100<br>Reduced to £60 if paid within 14 days.<br>Date issued: %s</body>' % (dmy(CONT), dmy(NOTICE)),
 'nto': B + '<b>LONDON BOROUGH OF CAMDEN</b><br><b>NOTICE TO OWNER</b><br>PCN number: CU12345678<br>Vehicle registration: AB12 CDE<br>Date of contravention: %s<br>Penalty charge: £130<br>Date of notice: %s</body>' % (dmy(D(-40)), dmy(NOTICE)),
 'rej': B + 'London Borough of Lambeth<br>PCN LJ12345678<br>Thank you for your challenge. We have considered it carefully but we have decided to reject it. The penalty charge of £130 is now payable. However we will accept £65 if paid within 14 days of the date of this letter.</body>',
 'dvla': B + '<b>DVLA</b><br>Vehicle registration: AB12 CDE<br>Our records show that the vehicle tax for this vehicle is due on %s. You must tax it or make a SORN by that date.<br>Reference: 4402 7788 1123</body>' % dmy(D(20)),
 'energy': B + '<b>Octopus Energy</b><br>Your bill<br>Account number: A-1234ABCD<br>Bill date: %s<br>Amount due: £142.37<br>We will collect this by Direct Debit on %s.</body>' % (dmy(D(-3)), dmy(D(10))),
 'bank': B + '<b>Barclays Bank UK PLC</b><br>Statement<br>Sort code 20-45-77 Account number 43218765<br>IBAN GB29 NWBK 6016 1331 9268 19<br>03 Oct CARD PAYMENT TO TESCO STORES £23.40<br>04 Oct DIRECT DEBIT OCTOPUS ENERGY £142.37<br>Card number 4929 1234 5678 9012</body>',
 'us': B + '<b>LAMBETH COUNCIL</b><br><b>PENALTY CHARGE NOTICE</b><br>PCN Number: LJ12345678<br>Vehicle registration: AB12 CDE<br>Date of contravention: 10/23/2026<br>Penalty charge: £130</body>',
 'crop': B + 'Date of event: %s<br>Parking charge: £100<br>Reduced to £60 if paid within 14 days.<br>Payment can be made online or by phone.</body>' % dmy(CONT),
 'noise': '<body style="margin:0;background:#fff;font-family:Courier;font-size:15px;padding:10px;color:#333">' + ('#@ ~~ ;; || ^^ %% ** ' * 6) + '<br>' + (' ~^ |l 0O ;: ,. ' * 10) + '</body>',
}
BANK_BITS = ['20-45-77', '43218765', 'GB29', 'NWBK', '6016 1331', '4929 1234', '4929123456789012']
R10 = {  # realistic reads that must pass the quality check
 'sainsburys': ('<body style="margin:0;background:#fff;font-family:Courier;font-size:17px;line-height:1.35;padding:18px;color:#222;width:340px">SAINSBURY\'S<br>Supermarkets Ltd<br>VAT Number: 660 4548 36<br><br>SEMI SKIMMED MILK 4PT &nbsp; £1.55<br>BREAD WHITE 800G &nbsp; £1.85<br>BANANAS LOOSE &nbsp; £0.98<br>BALANCE DUE &nbsp; £4.38<br>VISA &nbsp; £4.38<br>CARD NUMBER ************4921<br>AUTH CODE 123456<br>09/10/26 14:22 S0221 R05<br>Thank you for shopping at Sainsbury\'s</body>', 400, 470),
 'royalmail': (B + 'Royal Mail<br>We missed you!<br>Something for you: Large letter<br>We tried to deliver on: Thu 08 Oct<br>Collect from: Fri 09 Oct after 12:00<br>Your reference: AB 1234 5678 9GB<br>Redeliver online at royalmail.com/redelivery</body>', 560, 360),
 'gwr': ('<body style="margin:0;background:#f6f1e3;font-family:Arial;font-size:18px;line-height:1.4;padding:18px;color:#a32">Great Western Railway<br>OFF-PEAK RETURN &nbsp; STD<br>From: READING<br>To: LONDON TERMINALS<br>Valid until: 09.OCT.26<br>Route: ANY PERMITTED<br>Price: £29.80 &nbsp; Adult<br>Number: 12345 678901 23</body>', 460, 320),
 'thames': (B + 'Thames Water<br>Your bill<br>Account number 9001 234 567<br>Bill date 1 October 2026<br>Amount due £87.40<br>We\'ll collect your Direct Debit on or around 15 October 2026.<br>Questions? thameswater.co.uk/myaccount</body>', 600, 360),
 'hmrc': (B + 'HM Revenue &amp; Customs<br>Unique Taxpayer Reference (UTR): 12345 67890<br>Date: 2 October 2026<br>Dear Mr Smith<br>Self Assessment: you need to send a tax return.<br>You must send your return by 31 January 2027.<br>If you do not, you may have to pay a penalty of £100.</body>', 620, 380),
 'currys': (B + 'Currys<br>Order confirmation<br>Order number: 1234-5678-9012<br>Hotpoint washing machine x1 &nbsp; £299.00<br>Delivery: Tuesday 13 October, 7am - 7pm<br>Total paid: £299.00<br>Need help? currys.co.uk/help</body>', 560, 340),
 'ncp': ('<body style="margin:0;background:#fff;font-family:Courier;font-size:18px;line-height:1.4;padding:16px;color:#111;width:300px">TICKET 0042<br>NCP Car Park<br>Leeds Woodhouse Lane<br>ENTRY 08:41 09/10/26<br>TARIFF 3<br>KEEP THIS TICKET<br>Pay at machine before returning to vehicle</body>', 340, 300),
 'aviva': (B + 'Dear Baldwin,<br>Thank you for contacting Aviva. Your claim number is CL-778899.<br>We have appointed an assessor who will contact you within 5 working days to arrange a visit.<br>Kind regards,<br>Aviva Claims Team</body>', 600, 330),
 'argos': ('<body style="margin:0;background:#fff;font-family:Courier;font-size:16px;line-height:1.4;padding:16px;color:#111;width:380px">ARGOS<br>Receipt<br>123/4567 Kettle Russell Hobbs &nbsp; £34.99<br>Total &nbsp; £34.99<br>Paid by card: Contactless<br>Order no. 1122334455<br>Refunds within 30 days with receipt<br>Store 0789 Till 03 09/10/2026 11:05</body>', 420, 320),
 'evri': ('<body style="margin:0;background:#fff;font-family:Arial"><div style="margin:20px;padding:14px 16px;background:#e9e9eb;border-radius:18px;font-size:17px;line-height:1.35;color:#111;max-width:320px">Evri: Your parcel H01ABC1234567890 is on its way. Expected Friday 9 October between 10:00 - 14:00. From ASOS. Track at evri.com</div></body>', 390, 220),
}
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', cdn)
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    ctx.on('request', lambda rq: seen.append(rq.url))
    os.makedirs(OUT, exist_ok=True)
    def shot(name, html, w=560, h=440, css='', kind='png'):
        sp = b.new_page(viewport={'width': w, 'height': h}); sp.set_content(html.replace('</body>', css + '</body>') if css else html)
        path = OUT + '/d112_%s.%s' % (name, 'jpg' if kind == 'jpeg' else 'png'); sp.screenshot(path=path, type=kind, **({'quality': 85} if kind == 'jpeg' else {})); sp.close(); return path
    P = {k: shot(k, v, h=300 if k == 'crop' else (200 if k == 'noise' else 440), w=400 if k == 'noise' else 560) for k, v in FX.items()}
    P['rot'] = shot('rot', FX['pofa'].replace('padding:24px;', 'padding:40px;transform:rotate(-6deg);transform-origin:center;'), h=520)
    P['dark'] = shot('dark', FX['pofa'].replace('background:#fff', 'background:#2b2b2e').replace('color:#111', 'color:#e8e8e8'))
    P['glare'] = shot('glare', FX['pofa'], css='<div style="position:absolute;left:150px;top:60px;width:380px;height:260px;border-radius:50%;background:radial-gradient(closest-side,rgba(255,255,255,1),rgba(255,255,255,.95) 60%,rgba(255,255,255,0))"></div>')
    # a PDF with no text layer (one JPEG page), a two-page PDF with text, a 20 MB photo, an empty file, and misnamed files
    J = shot('pofa_j', FX['pofa'], kind='jpeg'); jb = open(J, 'rb').read()
    objs = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>', b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 560 440] /Resources << /XObject << /Im0 4 0 R >> >> /Contents 5 0 R >>',
            ('<< /Type /XObject /Subtype /Image /Width 560 /Height 440 /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length %d >>\nstream\n' % len(jb)).encode() + jb + b'\nendstream',
            b'<< /Length 30 >>\nstream\nq 560 0 0 440 0 0 cm /Im0 Do Q\nendstream']
    pdf = b'%PDF-1.4\n'; offs = []
    for i, o in enumerate(objs): offs.append(len(pdf)); pdf += ('%d 0 obj\n' % (i + 1)).encode() + o + b'\nendobj\n'
    xr = len(pdf); pdf += ('xref\n0 %d\n0000000000 65535 f \n' % (len(objs) + 1)).encode() + b''.join(('%010d 00000 n \n' % o).encode() for o in offs) + ('trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (len(objs) + 1, xr)).encode()
    open(OUT + '/d112_scan.pdf', 'wb').write(pdf)
    tp = b.new_page(); tp.set_content(FX['tfl'].replace('£605', '£80').replace('</body>', '<div style="page-break-before:always"></div><p>Page 2. How to pay: online at tfl.gov.uk/pcn. You may challenge this notice within 28 days.</p></body>')); tp.pdf(path=OUT + '/d112_two.pdf'); tp.close()
    big = open(P['tfl'], 'rb').read(); open(OUT + '/d112_big.png', 'wb').write(big + b'\0' * (20 * 1048576 - len(big)))
    open(OUT + '/d112_empty.png', 'wb').write(b'')
    open(OUT + '/d112_pdf_as.jpg', 'wb').write(open(OUT + '/d112_two.pdf', 'rb').read())
    open(OUT + '/d112_jpg_as.pdf', 'wb').write(jb)
    R10P = {k: shot('r10_' + k, v[0], w=v[1], h=v[2]) for k, v in R10.items()}

    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    case = lambda cid: [x for x in cases() if x['id'] == cid][0]
    main = lambda: pg.inner_text('main')
    def status():
        return ((pg.inner_text('#ocr-status') if pg.locator('#ocr-status').count() else '') + ' ' + (pg.inner_text('#doc-status') if pg.locator('#doc-status').count() else '')).strip()
    def read_wait():
        st = ''
        for _ in range(400):
            st = status()
            if re.search(r'Photo read|couldn’t|doesn’t look|Done\.|can’t read|isn’t a picture', st): wait(pg, 700); return st
            wait(pg, 500)
        return 'TIMEOUT ' + st
    def home():
        pg.goto('https://sorted.test/'); wait(pg, 600)
        if pg.locator('.tab129 [data-a=new-case]').count(): pg.locator('.tab129 [data-a=new-case]').first.evaluate('e=>e.click()'); wait(pg, 300)
    def parking():
        home(); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', 'PCN'); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 500)
    def doc_door(): home(); pg.locator('[data-cap82=document]').first.evaluate('e=>e.click()'); wait(pg, 300)
    def photo(path, sel='input[data-ocr=f-case]'): pg.set_input_files(sel, path); return read_wait()
    def review(): return {k: (pg.input_value('#doc-' + k) if pg.locator('#doc-' + k).count() else None) for k in ('issuer', 'ref', 'vrm', 'when', 'issued', 'amount', 'discount', 'payby')}
    def after_start():
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 700)
    def confirm():
        n0 = len(cases()); pg.click('form[data-f=doc] button[type=submit]'); wait(pg, 800); after_start()
        return cases()[-1] if len(cases()) > n0 else None
    def start_box():
        n0 = len(cases()); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 800); after_start()
        for s in ('[data-a=sug-no]', '[data-a=nudge-skip]'):
            if pg.locator(s).count(): pg.locator(s).first.click(); wait(pg, 300)
        return cases()[-1] if len(cases()) > n0 else None
    def opencase(cid):
        pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 900)
        pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); wait(pg, 200)
    def failed_screen(n0):
        return pg.locator('.doc121-fail [role=alert]').count() == 1 and pg.locator('.doc121-fail input[capture]').count() == 1 and 'Choose another file' in main() and pg.locator('.doc121-fail [data-a=doc-manual]').count() == 1 and len(cases()) == n0
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)

    # ---- 3 readers directly ----
    rp = ctx.new_page(); rp.route(lambda u: u.startswith('https://sorted.test/'), lambda q: q.fulfill(path=HERE + '/tests/out/reader.html', content_type='text/html'))
    rp.goto('https://sorted.test/')
    for _ in range(240):
        if rp.evaluate('!!(window.__read&&window.__read.ocrClean)'): break
        rp.wait_for_timeout(250)
    rd = rp.evaluate("""()=>{var R=window.__read,o={};
      o.bank=R.ocrClean("Barclays Bank UK PLC\\nStatement\\nSort code 20-45-77 Account number 43218765\\nIBAN GB29 NWBK 6016 1331 9268 19\\nCard number 4929 1234 5678 9012\\nNational Insurance number QQ 12 34 56 C\\nPassport number 123456789");
      o.keep=["Octopus Energy\\nAccount number: A-1234ABCD\\nAccount number 12345678 Amount due £142.37","Amazon order 205-1234567-1234567 arrives Friday. Tracking 4929123456789012","PCN LJ12345678 Vehicle AB12 CDE. DPD parcel 15501234567890","Visa ending 4921. Paid £20 on 03/10/2026"].map(function(x){return R.ocrClean(x)===x});
      o.grouped=R.ocrClean("Refund to 4111 1111 1111 1111 done");
      o.refs=[R.caseFacts("DVLA letter. Reference: 4402 7788 1123. Tax due soon.").ref,R.refsRead("Order number 1234 5678 9012 arriving Friday").map(function(x){return x.v}),R.caseFacts("Aviva claim ref 77812 2026 is open").ref,R.caseFacts("BT ref AB123 9am Tuesday").ref,R.caseFacts("Currys order 445566 arriving Friday").ref];
      o.r10=%s.map(function(x){return R.docAssess(x,70,"document").status});
      return o}""" % json.dumps(['TESCO STORES 2241\n1 x MILK £1.20\nTOTAL £5.60\nVAT No 220 4302 31\nThank you for shopping with us']))
    ok(all(x not in rd['bank'] for x in BANK_BITS + ['QQ 12 34 56', '123456789']) and rd['bank'].count('••••') == 6 and 'Sort code ••••' in rd['bank'] and 'Barclays Bank UK PLC' in rd['bank'], 'C1: sort code, account number, IBAN, card, NI and passport numbers are hidden in what Sorted reads: %r' % rd['bank'])
    ok(all(rd['keep']), 'C1: an energy account number, an Amazon order, a tracking number, a PCN, a DPD parcel and a card’s last four digits are left alone: %s' % rd['keep'])
    ok(rd['grouped'] == 'Refund to •••• done', 'C1: a card number printed in four groups is hidden even without a label: %r' % rd['grouped'])
    ok(rd['refs'] == ['4402 7788 1123', ['1234 5678 9012'], '77812', 'AB123', '445566'], 'C6: spaced references are kept whole; a year, a time or a single number are not joined on: %s' % rd['refs'])
    rp.close()

    # ---- 4 C7 and a TfL notice: a corrected reduced amount is saved as typed ----
    parking(); st = photo(P['tfl']); r = review()
    ok('Photo read' in st and r['issuer'] == 'Transport for London' and r['ref'] == 'LN12345678' and r['amount'] == '£160' and (r['discount'] or '').startswith('£605') and r['when'] == lab(CONT) and r['issued'] == lab(NOTICE), 'a TfL notice is read for review: %s' % r)
    ok(pg.locator('input[name=doc-kind][value=tfl]:checked').count() == 1, 'TfL is chosen as the sender')
    pg.fill('#doc-discount', '£60'); pg.fill('#doc-vrm', 'AB12 CDF'); c = confirm(); f = (c or {}).get('cf', {}).get('f', {})
    ok(f.get('discount', {}).get('v') == '£60' and f['discount'].get('how') == 'you', 'C7: the reduced amount corrected to £60 is saved as £60 and marked as yours (it was kept as the misread £605): %s' % f.get('discount'))
    ok(f.get('vrm', {}).get('v') == 'AB12 CDF' and f['vrm'].get('how') == 'you' and f.get('ref', {}).get('how') == 'read' and f.get('amount', {}).get('how') == 'read', 'edits are marked as yours, untouched details as read')
    ok('£605' not in json.dumps(c, ensure_ascii=False) and '£605' not in main(), 'the misread amount appears nowhere in the case or on its page')

    # ---- 5 a private notice (POFA) and a Notice to Owner ----
    parking(); st = photo(P['pofa']); r = review()
    ok(r['ref'] == '9876543210' and r['issuer'].startswith('Excel Parking') and r['amount'] == '£100' and pg.locator('input[name=doc-kind][value=private]:checked').count() == 1 and 'parking charge' in main().lower(), 'a private parking charge with POFA wording is read as a private company’s notice: %s' % r)
    c = confirm()
    ok(c and c['cf']['kind'] == 'private' and 'Notice to Keeper' in c['cf']['f']['type']['v'], 'the case is a Notice to Keeper from a private company: %s' % (c and c['cf']['f']['type']))
    parking(); st = photo(P['nto']); r = review(); c = confirm()
    ok(c and c['cf']['f']['type']['v'].startswith('Notice to Owner') and c['cf']['f']['issuer']['v'] == 'Camden Council' and r['when'] == lab(D(-40)), 'a Notice to Owner is read as one, from Camden: %s' % (c and c['cf']['f']['type']))

    # ---- 6 C3: their reply to a challenge through the parking door ----
    parking(); n0 = len(cases()); st = photo(P['rej'])
    ok(pg.locator('.doc145c-reply').count() == 1 and 'reply to a challenge, not the notice itself' in main() and len(cases()) == n0, 'C3: a rejection letter says it reads like their reply, not the notice, and creates nothing on its own')
    parking(); photo(P['tfl'])
    ok(pg.locator('.doc145c-reply').count() == 0, 'a real notice has no such note')

    # ---- 7 C4: a date written month first ----
    parking(); st = photo(P['us']); w = pg.inner_text('.doc121-review') if pg.locator('.doc121-review').count() else ''
    ok(review()['when'] == '' and 'Sorted saw “10/23/2026”, which is written month first' in w and '23/10/2026' in w, 'C4: a month-first date isn’t read as a UK date, and the review says what it saw: %r' % [l for l in w.split('\n') if 'month' in l])

    # ---- 8 variants: rotated, dark, cropped, glare; never invented, never the box, never a case ----
    for key in ('rot', 'dark', 'glare'):
        parking(); n0 = len(cases()); st = photo(P[key]); r = review() if pg.locator('.doc121-review').count() else None
        good = r is not None and r['ref'] in ('9876543210', '') and r['vrm'] in ('AB12 CDE', '') and r['amount'] in ('£100', '')
        ok((good or failed_screen(n0)) and pg.input_value('#f-case') == 'PCN' and len(cases()) == n0, '%s photo: a review with nothing invented, or a failure with routes; never the box, no case (%s, %s)' % (key, st[:40], r))
    parking(); n0 = len(cases()); st = photo(P['crop']); r = review() if pg.locator('.doc121-review').count() else None
    ok((r is None and failed_screen(n0)) or (r is not None and not r['ref'] and not r['issuer']), 'a cropped notice with no number or sender: a failure with routes, or a review that invents neither: %s %s' % (st[:60], r))

    # ---- 9 files: no text layer, two pages, 20 MB, empty, misnamed ----
    for key, path, want in (('a PDF with no text layer', OUT + '/d112_scan.pdf', '9876543210'), ('a two-page PDF', OUT + '/d112_two.pdf', 'LN12345678'), ('a 20 MB photo', OUT + '/d112_big.png', 'LN12345678'),
                            ('C2: a PDF saved with a .jpg name', OUT + '/d112_pdf_as.jpg', 'LN12345678'), ('C2: a photo saved with a .pdf name', OUT + '/d112_jpg_as.pdf', '9876543210')):
        parking(); n0 = len(cases()); st = photo(path); r = review() if pg.locator('.doc121-review').count() else {}
        ok('Photo read' in st and r.get('ref') == want and len(cases()) == n0, '%s is read for review: %s %s' % (key, st[:50], r.get('ref')))
    parking(); n0 = len(cases()); st = photo(OUT + '/d112_empty.png')
    ok('couldn’t open this file' in st and failed_screen(n0), 'an empty file says it couldn’t be opened, with routes, and creates nothing: %r' % st[:70])
    parking(); n0 = len(cases()); st = photo(P['energy'])
    ok('doesn’t look like a parking notice' in st and failed_screen(n0), 'an energy bill in the parking door: not a notice, with routes, nothing created')
    parking(); n0 = len(cases()); st = photo(P['noise'])
    ok('couldn’t read this photo clearly' in st and failed_screen(n0), 'an unreadable photo: a failure with routes, nothing created')

    # ---- 10 C6 and C1 through the document door: DVLA, an energy bill, a bank statement ----
    doc_door(); st = photo(P['dvla']); c = start_box()
    ok(c and c['facts'].get('ref') == '4402 7788 1123' and '4402 7788 1123' in main(), 'C6: the DVLA letter’s reference is kept whole: %s' % (c and c['facts'].get('ref')))
    doc_door(); st = photo(P['energy']); box = pg.input_value('#f-case')
    ok('A-1234ABCD' in box and 'hid' not in st, 'C1: an energy bill’s account number stays, and nothing is said to be hidden')
    doc_door(); st = photo(P['bank']); box = pg.input_value('#f-case')
    ok(all(x not in box for x in BANK_BITS) and box.count('••••') >= 4 and 'Sorted hid 4 bank or card numbers it read' in st, 'C1: the statement’s numbers are hidden in the box, and the status says so: %r' % st[:80])
    c = start_box(); cid = c['id']; blob = json.dumps(c, ensure_ascii=False)
    ok(all(x not in blob for x in BANK_BITS) and not c.get('refs'), 'C1: the case, its title, its words, its history and its references hold none of them')
    opencase(cid); pg.locator('[data-a=panel][data-p=paste]').first.evaluate('e=>e.click()'); wait(pg, 400)
    st = photo(P['bank'], 'input[data-ocr=f-paste]'); pv = pg.input_value('#f-paste')
    ok(all(x not in pv for x in BANK_BITS) and 'hid' in st, 'C1: the paste panel hides them too: %r' % st[:60])
    pg.click('form[data-f=paste] button[type=submit]'); wait(pg, 700)
    for s in ('[data-a=sug-no]', '[data-a=refs-no]', '[data-a=out-no]'):
        if pg.locator(s).count(): pg.locator(s).first.click(); wait(pg, 300)
    opencase(cid); pg.locator('[data-a=panel][data-p=pack]').first.evaluate('e=>e.click()') if pg.locator('[data-a=panel][data-p=pack]').count() else None; wait(pg, 500)
    pk = main()
    ok(all(x not in pk for x in BANK_BITS) and all(x not in json.dumps(case(cid), ensure_ascii=False) for x in BANK_BITS), 'C1: the adviser pack and the saved case hold none of them')
    ok(not re.search(r'43218765|4929', pg.evaluate("Object.keys(localStorage).map(k=>localStorage.getItem(k)).join(' ')+Object.keys(sessionStorage).map(k=>sessionStorage.getItem(k)).join(' ')")), 'C1: nor does anything kept on the phone')

    # ---- 11 C2: kept documents are what their bytes say ----
    opencase(cid)
    def keep(spec):
        opencase(cid); pg.set_input_files('input[data-keepdoc="%s"]' % cid, spec); wait(pg, 1200)
        return json.loads(pg.evaluate("localStorage.getItem('__storage')") or '[]')
    s0 = keep({'name': 'empty.pdf', 'mimeType': 'application/pdf', 'buffer': b''})
    ok(not s0 and 'That file is empty' in main(), 'C2: an empty file isn’t kept, and says why')
    s1 = keep({'name': 'letter.jpg', 'mimeType': 'image/jpeg', 'buffer': open(OUT + '/d112_two.pdf', 'rb').read()})
    ok(len(s1) == 1 and s1[0]['name'].endswith('.pdf') and s1[0]['type'] == 'application/pdf', 'C2: a PDF named .jpg is kept as a PDF: %s' % [(x['name'][-12:], x['type']) for x in s1])
    s2 = keep({'name': 'notes.pdf', 'mimeType': 'application/pdf', 'buffer': b'these are my notes, not a pdf'})
    ok(len(s2) == 1 and 'isn’t a photo or PDF' in main(), 'C2: a text file named .pdf is refused, whatever its name says')
    s3 = keep({'name': 'scan.pdf', 'mimeType': 'application/pdf', 'buffer': jb})
    ok(len(s3) == 2 and s3[1]['name'].endswith('.jpg') and s3[1]['type'] == 'image/jpeg', 'C2: a photo named .pdf is kept as a photo')
    kept = [e['label'] for e in case(cid)['events'] if e['label'].startswith('Kept a document')]
    ok(len(kept) == 2 and all(re.match(r'^Kept a document with this case: (?:Photo|PDF), \d{1,2} [A-Z][a-z]{2}\.$', x) for x in kept) and ': PDF,' in kept[0] and ': Photo,' in kept[1], 'the history names only the kind (by its real type) and the day: %s' % kept)

    # ---- 12 ten realistic reads pass the quality check through the document door ----
    bad = []
    for k, path in R10P.items():
        doc_door(); n0 = len(cases()); st = photo(path)
        if not st.startswith('Done') or not pg.input_value('#f-case').strip() or len(cases()) != n0: bad.append((k, st[:60]))
    ok(not bad and rd['r10'] == ['ok'], 'ten real reads of receipts, tickets and letters pass the quality check and fill the box (nothing created yet): %s' % (bad or 'all pass'))

    # ---- 13 C5: the reader can't start ----
    opencase(cid); pg.locator('[data-a=panel][data-p=paste]').first.evaluate('e=>e.click()'); wait(pg, 400)
    FAILOCR[0] = True; pg.reload(); wait(pg, 900)
    if not pg.locator('#f-paste').count(): pg.locator('[data-a=panel][data-p=paste]').first.evaluate('e=>e.click()'); wait(pg, 400)
    ev0 = len(case(cid)['events']); pg.set_input_files('input[data-ocr=f-paste]', R10P['aviva']); st = read_wait()
    ok('couldn’t read that picture' in st and 'Nothing was added' in st and pg.locator('#ocr-status[role=alert]').count() == 1 and pg.locator('.ocr143-routes input[capture]').count() == 1 and pg.locator('[data-a=ocr-type]').count() == 1 and len(case(cid)['events']) == ev0, 'C5: with no connection to the reader, the paste panel says so as an alert, with retake, another file or type it: %r' % st[:80])
    FAILOCR[0] = False

    # ---- 14 everything outside the site that was loaded is allowed by the CSP ----
    outside = sorted(set(u.split('?')[0] for u in seen if not u.startswith('https://sorted.test/') and not u.startswith('data:') and not u.startswith('blob:')))
    allow = dirs['script-src'] + dirs['connect-src']
    ok(outside and all(covers(allow, u) for u in outside), 'every outside address the page loaded during this walk is in the CSP: %s' % [u for u in outside if not covers(allow, u)])
    ok(not errs, 'no page errors: %s' % errs[:2])
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
