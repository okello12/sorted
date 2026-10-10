# v161: a product's serial number is a protected identifier (docs/PRODUCT_PHASE1.md, Privacy). The full value is kept
# once, in the case's product record, and shown only after Show or copied after Copy. Everywhere else it is masked
# (••••5432) or absent: Home, Cases, the case page, the ledger, the history, the helper's link, the adviser pack, the
# summary, what the assistant is sent, an error report, usage records, reminder rows and the address bar. Even when the
# person also typed it in their own words, Home, the helper's link, the assistant and error reports mask it.
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *
SER = 'SN98765432'; MASK = '••••5432'
def has(x): return SER in (x if isinstance(x, str) else json.dumps(x, ensure_ascii=False))
with sync_playwright() as p:
    a = App(p, email=True); pg = a.pg
    a.home(); a.tap('new-case'); pg.locator('[data-cap82=fix]').first.evaluate('e=>e.click()'); wait(pg, 400)
    pg.click('[data-a=prod161-type]'); wait(pg, 200)
    pg.fill('#prod-brand', 'Bosch'); pg.fill('#prod-model', 'WGG244ZCGB'); pg.fill('#prod-serial', SER.lower()); pg.locator('input[name=prod-cat][value=washing_machine]').evaluate('e=>e.click()')
    pg.click('form[data-f=prod161] button[type=submit]'); wait(pg, 300)
    ok(MASK in a.main() and not has(a.main()), 'the start shows the serial masked')
    pg.fill('#gi-what', 'It won’t spin. Serial %s on the label.' % SER)
    pg.locator('form[data-f=gi] button[type=submit]').first.click(); wait(pg, 800)
    for sel in ('[data-a=match-new]', '[data-a=vague-go]'):
        if pg.locator(sel).count(): pg.click(sel); wait(pg, 400)
    if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 800)
    c = until(pg, lambda: [x for x in a.cases() if x.get('prod')], 8000)[0]; cid = c['id']
    ok(c['prod']['f']['serial']['v'] == SER, 'the full serial is kept once, in the product record')
    # the case itself
    a.open(cid); m = a.main()
    import os as _o
    if _o.environ.get('DBG'):
        print(c['title'], c.get('facts'));print([l for l in m.split('\n') if SER in l]); print([r for r in c.get('ledger',[]) if SER in json.dumps(r)]); a.home(); print([l for l in a.main().split('\n') if SER in l]); a.open(cid)
    ok(MASK in m and m.count(SER) == m.count('Serial ' + SER + ' on the label'), 'the case page masks the product serial (the person’s own words are theirs)')
    ok(not any(has(r['v']) for r in c.get('ledger', [])) and any(r['v'] == MASK for r in c.get('ledger', [])), 'the ledger has the serial only masked')
    ok(not any(has(e['label']) for e in c['events'] if not e['label'].startswith('You said') and 'on the label' not in e['label']), 'Sorted’s own history lines never hold the full serial')
    # Home and Cases
    a.home(); ok(not has(a.main()), 'Home never shows the full serial (even from the person’s words)')
    a.tap('cases'); ok(not has(a.main()), 'Cases never shows it')
    ok(not has(pg.url), 'the address bar never holds it')
    # the helper's link
    tx = a.share_view(cid); ok(not has(tx), 'the helper’s link never shows it')
    sh = [r for r in a.db().get('shares', []) if r.get('task_id') == cid]
    ok(sh and not has(sh[0].get('card')), 'the shared card stored for the helper never holds it')
    # the adviser pack and the summary
    pk = a.pack(cid); ok(not has(pk.replace('Serial ' + SER + ' on the label', '')), 'the adviser pack shows the product serial masked at most')
    a.open(cid); pg.evaluate("(()=>{var b=document.createElement('button');b.setAttribute('data-a','panel');b.setAttribute('data-p','summary137');document.querySelector('main').appendChild(b);b.click()})()"); wait(pg, 400)
    pre = pg.inner_text('#sum137-pre') if pg.locator('#sum137-pre').count() else ''
    ok(pre and not has(pre.replace('Serial ' + SER + ' on the label', '')), 'the summary shows the product serial masked at most')
    # the assistant
    a.open(cid); pg.evaluate("(()=>{var b=document.createElement('button');b.setAttribute('data-a','ai-explain');b.setAttribute('data-at','said');document.querySelector('main').appendChild(b);b.click()})()"); wait(pg, 400)
    if pg.locator('[data-a=ai-ok]').count(): pg.click('[data-a=ai-ok]'); wait(pg, 300)
    if pg.locator('[data-a=ai-explain-go]').count(): pg.click('[data-a=ai-explain-go]'); wait(pg, 600)
    calls = pg.evaluate('window.__ai||[]')
    ok(calls and not has(calls) and MASK in json.dumps(calls, ensure_ascii=False), 'what the assistant is sent has the serial masked (%d call)' % len(calls))
    # an error report
    pg.evaluate("setTimeout(function(){throw new Error('boom %s')},0)" % SER); wait(pg, 600)
    errs_sent = pg.evaluate("JSON.parse(localStorage.getItem('__errs')||'[]')")
    ok(errs_sent and not has(errs_sent), 'an error report never holds the serial: %s' % json.dumps(errs_sent[-1:], ensure_ascii=False)[:120])
    errs[:] = [e for e in errs if 'boom' not in e]
    # usage records and reminder rows
    db = a.db()
    ok(not has(db.get('pilot_events', [])), 'usage records never hold it')
    ok(not has(db.get('reminders', [])), 'reminder rows never hold it')
    a.close()
finish()
