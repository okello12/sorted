# v102: semantic memory. Explicit facts the person gives must survive: refined or corrected, never silently lost.
# Part 1 runs generated wordings straight through the reader; part 2 checks the screens never ask again for what
# was already said ("must not ask").
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []; n = [0]
def ok(c, m, quiet=False):
    n[0] += 1
    if not c or not quiet: print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=450): pg.wait_for_timeout(ms)
ITEMS = ['screen', 'oven', 'intercom', 'TV', 'laptop', 'doorbell', 'boiler', 'router', 'garage door', 'radiator', 'printer', 'freezer', 'dishwasher', 'thermostat', 'extractor fan', 'kettle', 'flux capacitor', 'microwave', 'tumble dryer', 'fridge']
FORMS = ['The {I} is broken', 'My {I} broke', '{I} stopped working', 'The {I} isn’t working', '{I}’s gone', 'Problem with my {I}', '{I} broken', 'My {I} won’t turn on', 'the {I} has stopped working', 'my {I} keeps breaking', '{I} cracked', 'our {I} is not working']
def kept(r, item):
    i = item.lower(); th = (r['thing'] or '').lower(); it = (r['item'] or '').lower()
    fam = {'boiler': 'heating', 'radiator': 'heating', 'fridge': 'fridge', 'freezer': 'fridge', 'garage door': 'door', 'tumble dryer': 'dryer', 'laptop': 'laptop', 'dishwasher': 'dishwasher'}
    return (i in th) or (it and (i in it or fam.get(i, '#') in it))
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(timezone_id='Europe/London')
    ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    rd = ctx.new_page(); rd.route(lambda u: u.startswith('https://sorted.test/'), lambda q: q.fulfill(path=HERE + '/tests/out/reader.html', content_type='text/html'))
    rd.goto('https://sorted.test/'); wait(rd, 500)
    R = lambda t: rd.evaluate("(t)=>{var R=__read,f=R.caseFacts(t),s=R.readCase(t,f);return {item:f.item||'',party:f.party||'',ref:f.ref||'',amount:f.amount||'',kind:f.kind||'',resp:f.resp||'',thing:R.thingOf(t),unsafe:R.looksUnsafe(t),sug:s?{party:s.party||'',said:s.said,due:s.dueAt,end:s.dueEnd,past:!!s.past}:null}}", t)
    # 1 unknown nouns survive: 20 things x 12 wordings
    lost = []
    for it in ITEMS:
        for f in FORMS:
            t = f.replace('{I}', it); t = t[0].upper() + t[1:] if f.startswith('{I}') else t
            r = R(t)
            if not kept(r, it): lost.append('%s -> item=%r thing=%r' % (t, r['item'], r['thing']))
    ok(not lost, 'broken things: %d wordings keep the thing named (%d lost) %s' % (len(ITEMS) * len(FORMS), len(lost), lost[:6]))
    # 2 promises keep who, what, when and the reference
    P = [("Currys said my £89 refund would arrive Friday. Ref C991", dict(party='Currys', ref='C991', amount=89, kind='money')),
         ("Virgin said an engineer is coming Tuesday between 2 and 5", dict(sparty='Virgin', window=True)),
         ("British Gas said they’d send someone Tuesday", dict(sparty='British Gas')),
         ("Engineer will attend Tuesday between 2–4pm, ref A1842", dict(ref='A1842', window=True)),
         ("Amazon said my parcel would arrive tomorrow", dict(sparty='Amazon')),
         ("Aviva said they'd call me back within 48 hours, claim ref HC-77812", dict(ref='HC-77812', sparty='Aviva'))]
    for t, want in P:
        r = R(t); s = r['sug'] or {}
        good = bool(s) and all([(r['party'] == want['party']) if 'party' in want else True, (r['ref'] == want['ref']) if 'ref' in want else True, (r['amount'] == want['amount']) if 'amount' in want else True, (r['kind'] == want['kind']) if 'kind' in want else True, (s.get('party') == want['sparty']) if 'sparty' in want else True, bool(s.get('end')) if want.get('window') else True])
        ok(good, 'promise kept whole: %s -> %s' % (t, json.dumps({k: r[k] for k in ('party', 'ref', 'amount')} | {'sug': s}, ensure_ascii=False)[:180]))
    # 3 a demand on you is never their promise, and keeps who and how much
    r = R("HMRC says I owe £450 by 12 October"); ok(r['sug'] is None and r['party'] == 'HMRC' and r['amount'] == 450, 'HMRC demand: HMRC and £450 kept, not a promise')
    # 4 typos and shorthand
    for t, chk, label in [("washine machine wont drain", lambda r: r['item'] == 'Washing machine', 'washing machine'), ("bolier no hot water", lambda r: 'Heating' in r['item'], 'boiler'), ("currys refnd not here", lambda r: r['party'] == 'Currys' and r['kind'] == 'money', 'Currys refund'), ("landlord sed engineer tuesday", lambda r: r['resp'] == 'landlord' and r['sug'] is not None, 'landlord promise'), ("hmrc letta", lambda r: r['party'] == 'HMRC', 'HMRC')]:
        r = R(t); ok(chk(r), 'typo "%s" still reads as %s' % (t, label))
    # 5 negation
    r = R("It’s not the boiler. The thermostat is broken."); ok(r['item'] == '' and r['thing'] == 'Thermostat', 'not the boiler: the thermostat (%r, %r)' % (r['item'], r['thing']))
    r = R("The refund hasn’t arrived from Currys"); ok(r['kind'] == 'money' and r['sug'] is None, '"hasn’t arrived" is not a refund received, and not a promise')
    r = R("Currys promised to replace the TV Friday but they didn’t."); ok(r['sug'] and r['sug']['past'], 'said Friday but didn’t: the promise is in the past, so it is missed')
    r = R("The boiler is broken, I’ve contacted the landlord twice and he said an engineer would come yesterday but nobody came.")
    ok(r['sug'] and r['sug']['past'] and r['resp'] == 'landlord' and 'Heating' in r['item'], 'one long sentence: boiler, landlord, a missed visit, all kept')
    # 6 safety: danger is caught, its absence is not danger
    for t in ["My washing machine is smoking", "smoke coming out of the back", "burning smell from the dryer", "it smells burnt", "sparks from the socket", "the plug is sparking", "I can smell gas near the boiler", "water near the electrics", "the plug is hot"]:
        ok(R(t)['unsafe'], 'safety: "%s" stops for safety' % t)
    for t in ["There is no smoke or burning smell", "no sparks or smoke, it just won’t start", "nothing burning, it just won’t drain"]:
        ok(not R(t)['unsafe'], 'safety: "%s" is not treated as danger' % t)
    rd.close()
    # Part 2: the screens never ask again for what was said
    ctx2 = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London')
    ctx2.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
    ctx2.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
    pg = ctx2.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();sessionStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 300)
    if pg.locator('[data-a=anon-start]').count(): pg.click('[data-a=anon-start]'); wait(pg, 700)
    def start(text, door='other'):
        pg.goto('https://sorted.test/'); wait(pg, 600)
        d = pg.locator('#cap82-start [data-cap82=%s]' % door).first
        if d.count(): d.evaluate('e=>e.click()'); wait(pg)
        if door == 'other' or not pg.locator('.gi-form').count():
            if not pg.locator('#f-case').count() and pg.locator('[data-a=compose]').count(): pg.locator('[data-a=compose]').first.click(); wait(pg)
            pg.fill('#f-case', text); pg.locator('form[data-f=case] button[type=submit]').last.click(); wait(pg)
        elif door == 'fix':
            se = pg.locator('label.gi-chip:has-text("Something else")')
            if se.count(): se.first.click()
            pg.fill('#gi-what', text); pg.click('form[data-f=gi] button[type=submit]'); wait(pg, 600)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 550)
        return pg.inner_text('main')
    def empty(sel): return pg.locator(sel).count() and not pg.input_value(sel).strip()
    m = start('The screen is broken')
    ok(not empty('#f-item') and 'What is it, and what’s it doing?' not in m and 'What’s happening with the screen?' in m and 'Which one?' in m, 'screen: never "What is it?" with a blank box; asks which screen')
    pg.locator('button.chip[data-k=item]', has_text='Laptop screen').click(); wait(pg, 300)
    ok(pg.input_value('#f-item') == 'Laptop screen', 'picking Laptop screen refines it')
    m = start('My flux capacitor is broken'); ok(pg.input_value('#f-item') == 'Flux capacitor' if pg.locator('#f-item').count() else False, 'an unknown thing survives into the repair step')
    m = start('Currys said my £89 refund would arrive Friday. Ref C991')
    ok(pg.locator('[data-a=sug-yes]').count() == 1 and 'Currys' in m and 'C991' in m and 'Who owes you' not in m, 'Currys refund: proposed with who and the ref, no question about who')
    m = start('HMRC says I owe £450 by 12 October')
    ok((pg.input_value('#f-who') if pg.locator('#f-who').count() else '') == 'HMRC' and 'Who is the letter from' not in m and '20 Oct' not in m, 'HMRC demand: the message is already to HMRC')
    m = start('The landlord said he would come but didn’t.')
    ok('They said they would, and it hasn’t happened.' in m and 'They haven’t given you a date yet' not in m, 'said but didn’t: Sorted says it was missed')
    m = start('Currys promised to replace the TV Friday but they didn’t.', door='fix')
    ok(pg.locator('[data-a=sug-yes][data-v=missed]').count() == 1, 'chosen as broken, but a missed Currys promise is recognised as one (the doors are hints)')
    print('CHECKS', n[0])
    b.close()
print('ERRORS', errs); print('FAILS', fails)
