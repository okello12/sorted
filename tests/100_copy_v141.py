# v141 (the copy and wording review). Wording that read wrongly, said untrue things or broke grammar:
#   - whose move with no name says "they"/"their", and a name typed at the start ("Aviva said …") is used;
#   - the summary's ask for a date that was never given asks for the date, never "on track for “within …”";
#   - whenText inside a sentence starts lower case ("Them, Within …", "It was By Friday" are gone);
#   - no "Them" shown as a name; "Latest:" and "about between" are gone; role words read "your landlord";
#   - the chase keeps "Aviva" as written and speaks to them; goals don't double-quote "said they would";
#   - a long sentence typed in the start box is "From what you wrote"; "they"/"not sure" is no name;
#   - the repair questions are "above"; Help, privacy, Terms and Settings tell the truth about kept documents,
#     reminders (lock screen, the Settings link in the email), retention and this browser;
#   - a reminder link or #case- link for a deleted case says so; #more-settings, #more-help and #privacy keep their place;
#   - focus goes to the panel heading, "Keep it" comes first, the Undo banner takes focus;
#   - page titles per route, an £89, "Waiting for", the told-date put-down line, the pack's plain sources.
import os, sys, datetime, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m):
    n[0] += 1; print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
today = datetime.date.today()
told = today - datetime.timedelta(days=((today.weekday() - 2) % 7) or 7)   # last Wednesday
DAY = lambda d: '%s %d %s' % (d.strftime('%A'), d.day, d.strftime('%B'))
CAPMID = re.compile(r'(?:, |\(|It was |They said |Due )(?:Within|Take|By|Sometime|No date) ')
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London', viewport={'width': 390, 'height': 844})
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url and '/fonts/' not in r.request.url else r.fulfill(body=''))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    dbj = lambda: pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))") or {}
    cases = lambda: sorted([x['data'] for x in dbj().get('tasks', []) if x['data'].get('kind') != 'moment'], key=lambda x: x.get('created') or '')
    case = lambda cid: [c for c in cases() if c['id'] == cid][0]
    tap = lambda a: (pg.locator('.tab129 [data-a=%s]' % a).click(), wait(pg, 500))
    main = lambda: pg.inner_text('main')
    def opencase(cid): pg.goto('https://sorted.test/?task=%s' % cid); wait(pg, 700)
    def start(text, keep=True):
        tap('new-case'); pg.locator('[data-cap82=other]').first.evaluate('e=>e.click()'); wait(pg, 300)
        pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg, 600)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        sug = pg.inner_text('.sug') if pg.locator('.sug').count() else ''
        if keep and pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
        if pg.locator('[data-a=nudge-skip]').count(): pg.click('[data-a=nudge-skip]'); wait(pg, 300)
        return cases()[-1]['id'], sug
    focus = lambda: pg.evaluate("(()=>{var e=document.activeElement;return e?(e.id||'')+'|'+(e.getAttribute('data-a')||'')+'|'+(e.className||'')+'|'+(e.textContent||'').trim().slice(0,60):''})()")
    # ---------- the public site ----------
    pg.goto('https://sorted.test/'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')")
    pg.goto('https://sorted.test/'); wait(pg, 700)
    land = pg.inner_text('body')
    ok('A £89' not in land and 'a £89' not in land, 'no “a £89” on the landing page')
    for h, tt in [('#privacy', 'Privacy · Sorted'), ('#terms', 'Terms · Sorted'), ('#help', 'Help · Sorted'), ('#about', 'About · Sorted')]:
        pg.goto('https://sorted.test/' + h); wait(pg, 500)
        ok(pg.title() == tt, 'the page title on %s is %r: %r' % (h, tt, pg.title()))
    pg.goto('https://sorted.test/'); wait(pg, 400); pg.evaluate("location.hash='#terms'"); wait(pg, 500)
    ok('h1' == pg.evaluate("document.activeElement.tagName.toLowerCase()"), 'moving to a public page puts focus on its heading')
    m = pg.inner_text('main') if pg.locator('main').count() else pg.inner_text('body')
    ok('“Report a problem” below' not in m and '“Report a problem” on the Contact page' in m, 'the Terms point at Report a problem on the Contact page')
    pg.goto('https://sorted.test/#privacy'); wait(pg, 500); m = pg.inner_text('body')
    ok('The file isn’t uploaded.' not in m and '“Keep a document with this case”' in m and 'unless something on them is still due' in m, 'privacy: kept documents and one retention sentence')
    ok('idle cases are deleted after 90 days' not in m.lower() and 'deleted automatically' not in m, 'no other retention wording on the privacy page')
    pg.goto('https://sorted.test/#help'); wait(pg, 500)
    for d in pg.locator('details').all():
        try: d.evaluate('e=>e.open=true')
        except Exception: pass
    m = pg.inner_text('body')
    ok('isn’t uploaded or kept, so keep your original' not in m and 'Keep a document with this case' in m, 'Help: a document can be kept with a case')
    ok('lock screen' in m or 'notification' in m, 'Help: reminders mention the phone as well as email')
    ok('goes idle for 90 days' not in m and ('link that stops them all' not in m or 'stops them all, after asking you once' in m), 'Help: no old retention wording; the stop link is described as it works (v142)')
    pg.goto('https://sorted.test/#how'); wait(pg, 500)
    ok('Done keeps it until you delete it' not in pg.inner_text('body'), 'How it works no longer says Done keeps it for ever')
    # ---------- a guest ----------
    pg.goto('https://sorted.test/#start'); wait(pg, 300); pg.click('[data-a=anon-start]'); wait(pg, 700)
    # 1. whose move with no name, and a name typed at the start
    c1, _ = start('They said they would call me back')
    m = main()
    ok('them asked' not in m and 'them’s move' not in m and 'Mine: they asked me for something' in m, 'no name: “Mine: they asked me for something”')
    c2, _ = start('Aviva said they would call me back')
    m = main()
    ok('Mine: Aviva asked me for something' in m and 'Theirs: I’m waiting for Aviva' in m, 'a name typed at the start is used in whose move')
    pg.click('[data-a=turn-theirs]'); wait(pg, 500); m = main()
    ok('waiting for Aviva' in m, 'the history and the case say you’re waiting for Aviva')
    # 11. the chase message keeps the name and speaks to them
    pg.goto('https://sorted.test/?task=%s' % c2); wait(pg, 700)
    if pg.locator('[data-a=panel][data-p=call]').count(): pg.locator('[data-a=panel][data-p=call]').first.evaluate('e=>e.click()'); wait(pg, 400)
    ask = pg.evaluate("(()=>{var e=document.querySelector('#f-ask');return e?e.value:''})()")
    ok('aviva said' not in ask and ('You said you would call me back' in ask or ask == ''), 'the chase keeps Aviva as written and speaks to them: %r' % ask[:120])
    # 14. "they" as the name is no name
    tap('new-case'); pg.locator('[data-cap82=chase]').first.evaluate('e=>e.click()'); wait(pg, 400)
    if pg.locator('#gi-who').count():
        pg.fill('#gi-who', 'they'); pg.fill('#gi-what', 'call me back with a decision'); pg.locator('form[data-f=gi] button[type=submit]').last.click(); wait(pg, 700)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
        t = cases()[-1]
        ok('from they' not in t['title'] and not t['title'].lower().startswith('they:') and 'from they' not in main(), '“they” is not taken as a name: %r' % t['title'])
    # 2, 8, 9, 10. an approximate date
    c3, sug = start('HMRC said they would reply within 15 working days')
    opencase(c3); m = main()
    ok(not CAPMID.search(m), 'no capital after a comma or bracket on the case: %s' % (CAPMID.search(m) and CAPMID.search(m).group(0)))
    ok('HMRC, within 15 working days' in m, 'the promise card: “HMRC, within 15 working days”')
    ev = ' '.join(e['label'] for e in case(c3)['events'])
    ok(', Within 15 working days' not in ev, 'the history line keeps “within” lower case')
    pg.locator('[data-a=panel][data-p=summary137]').first.evaluate('e=>e.click()'); wait(pg, 500)
    pre = pg.inner_text('#sum137-pre')
    ok('on track for “within' not in pre and 'You told me “within 15 working days”. Please confirm the date this will happen.' in pre, 'the summary asks for the date: %s' % pre.split('What I’m asking for now:')[-1][:120])
    ok('sumh' in focus(), '“Send this summary” puts focus on its heading: %s' % focus())
    c4, sug = start('Octopus Energy told me last Wednesday the £40 refund would take 3 to 5 working days')
    opencase(c4); m = main(); now = pg.inner_text('.now137') if pg.locator('.now137').count() else ''
    ok('promised it “take' not in now and ('Octopus Energy said “take 3 to 5 working days” on ' + DAY(told)) in now, 'what happened says when they said it: %s' % now[:200])
    ok('about between' not in m and 'Latest:' not in m, 'no “about between”, no “Latest:”')
    ok('You can put this down until' not in m, 'before choosing a day, no put-down line')
    pg.locator('[data-a=panel][data-p=summary137]').first.evaluate('e=>e.click()'); wait(pg, 500)
    pre = pg.inner_text('#sum137-pre')
    ok(('You told me it would “take 3 to 5 working days” on ' + DAY(told)) in pre, 'the summary gives the day they said it: %s' % pre.split('What I’m asking for now:')[-1][:160])
    # 12. a role word reads as a role
    c5, _ = start('landlord sed engineer tuesday ref AB12345')
    opencase(c5); m = main()
    ok('Landlord promised' not in m and 'Waiting for Landlord' not in m and 'from Landlord' not in m, 'Landlord is not used as a name in running text')
    ok('your landlord' in m.lower(), 'it reads “your landlord”')
    # 13. a long typed sentence is the person's own words
    c6, sug = start('The Royal Borough of Kensington and Chelsea Parking Services Department said they would reply within 15 working days', keep=False)
    ok('From their message' not in sug and 'FROM THEIR MESSAGE' not in sug, 'a long typed sentence is “From what you wrote”: %s' % sug[:80])
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg, 600)
    ok(not any('from their message' in e['label'] for e in case(c6)['events']), 'and the history says the words are yours')
    g = pg.evaluate("(()=>{var e=[...document.querySelectorAll('main *')].map(x=>x.textContent).join(' ');return /Make sure they do what they said: The Royal/.test(e)})()")
    ok(not g, 'the goal doesn’t quote a sentence that already says “said they would”')
    ok(pg.evaluate("document.activeElement&&document.activeElement.tagName!=='INPUT'"), 'after “Yes, keep track of it” focus is not in the email field')
    # 15. the repair questions are above
    c7, _ = start("My washing machine won't drain")
    m = main()
    ok('Answer the questions above.' in m and 'just below' not in m.split('Answer the questions')[-1][:30], 'the repair points at the questions above')
    ok("Won't" not in m and "Something's" not in m, 'no straight apostrophes in the washing machine choices')
    # 17. focus for kind, something changed, delete
    opencase(c1)
    pg.locator('[data-a=panel][data-p=kind]').first.evaluate('e=>e.click()'); wait(pg, 400)
    ok('kindh141' in focus(), '“Change the kind of case” puts focus on its heading: %s' % focus())
    pg.locator('[data-a=panel][data-p=""]').first.evaluate('e=>e.click()'); wait(pg, 300)
    opencase(c3)
    if pg.locator('[data-a=panel][data-p=changed]').count():
        pg.locator('[data-a=panel][data-p=changed]').first.evaluate('e=>e.click()'); wait(pg, 400)
        ok('sch' in focus(), '“Something changed” puts focus on its heading: %s' % focus())
    opencase(c7)
    pg.locator('[data-a=panel][data-p=delcase]').first.evaluate('e=>e.click()'); wait(pg, 400)
    ok('delh' in focus(), 'the delete question puts focus on its heading, not on Delete it: %s' % focus())
    ok(pg.evaluate("(()=>{var b=[...document.querySelectorAll('main .row.eq button')].map(x=>x.textContent);var i=b.indexOf('Keep it'),j=b.indexOf('Delete it');return i>=0&&j>i})()"), '“Keep it” comes before “Delete it”')
    pg.click('[data-a=case-del]'); wait(pg, 800)
    ok('del141' in focus(), 'after deleting, focus is on the Undo banner: %s' % focus())
    # 7. links to a deleted case
    pg.goto('https://sorted.test/?task=%s&src=email&ans=yes&p=x' % c7); wait(pg, 1200)
    body = pg.inner_text('body')
    ok('That case isn’t in Sorted any more, so nothing was recorded.' in body, 'a reminder answer for a deleted case says nothing was recorded')
    ok(pg.evaluate('location.hash') in ('#start', ''), 'and the address is Home, not #signin: %s' % pg.evaluate('location.hash'))
    pg.goto('https://sorted.test/#case-%s' % c7); wait(pg, 1200)
    ok('That case isn’t in Sorted any more.' in pg.inner_text('body'), 'a #case- link to a deleted case says so')
    # 5, 18. Account and Settings for a guest
    tap('data'); m = main()
    ok(', saved to Sorted.' in m and 'on this phone only' not in m and 'only this phone can open' not in m, 'Account: “N cases, saved to Sorted.”, this browser')
    ok('More · Sorted' != pg.title() and pg.title() == 'Account · Sorted', 'the page title says Account: %r' % pg.title())
    pg.click('.acct112-nav [data-v=acct-settings]'); wait(pg, 400); m = main()
    ok('lock screen' in m and 'can only remind you when you open it' not in m, 'Settings: a guest can be reminded on the lock screen')
    ok(pg.evaluate('location.hash') == '#more-settings', 'the Settings tab has its own address')
    pg.reload(); wait(pg, 1200)
    ok(pg.locator('#acct-settings-h').count() == 1, 'a refresh on Settings stays on Settings')
    pg.goto('https://sorted.test/#more-help'); wait(pg, 1200)
    ok(pg.locator('#help-h').count() == 1, '#more-help opens Help & About')
    pg.goto('https://sorted.test/#privacy'); wait(pg, 1200)
    ok(pg.locator('#help-h').count() == 1 and 'How your data is handled' in focus(), 'signed in, #privacy opens Help & About at the privacy notice: %s' % focus())
    # 6. the missed pill on Cases has the same warm colours as on Home, in dark mode too
    c8, _ = start('Evri said they would deliver my parcel last Tuesday but nothing came')
    PILL = "(()=>{var e=document.querySelector('.home111-hot .home44-pill');if(!e)return null;var s=getComputedStyle(e);return [s.color,s.backgroundColor]})()"
    def lum(c):
        v = [int(x) / 255 for x in re.findall(r'\d+', c)[:3]]
        v = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in v]
        return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]
    for scheme in ['light', 'dark']:
        pg.emulate_media(color_scheme=scheme); tap('cases'); cs = pg.evaluate(PILL)
        r = cs and (max(lum(cs[0]), lum(cs[1])) + 0.05) / (min(lum(cs[0]), lum(cs[1])) + 0.05)
        ok(cs and r >= 4.5, '%s: the missed pill on Cases reads at %.2f to 1: %s' % (scheme, r or 0, cs))
    pg.emulate_media(color_scheme='light')
    # 24. text inputs and selects are 44px tall
    opencase(c3); pg.locator('[data-a=panel][data-p=rename]').first.evaluate('e=>e.click()'); wait(pg, 400)
    hgt = pg.evaluate("(()=>{var e=document.querySelector('form[data-f=rename] input');return e?e.getBoundingClientRect().height:0})()")
    ok(hgt >= 44, 'the Rename box is at least 44px tall: %s' % hgt)
    pg.locator('[data-a=panel][data-p=refadd]').first.evaluate('e=>e.click()') if pg.locator('[data-a=panel][data-p=refadd]').count() else None; wait(pg, 400)
    hs = pg.evaluate("(()=>{var e=document.querySelector('form[data-f=refadd] select');return e?e.getBoundingClientRect().height:44})()")
    ok(hs >= 44, 'the reference type list is at least 44px tall: %s' % hs)
    print('ERRORS', errs); print('FAILS', fails)
    b.close()
