# v161: the product safety gate through the page (docs/PRODUCT_PHASE1.md, Safety boundaries). For each dangerous
# description (sparking, burning smell, smoke, gas, swollen battery, exposed cable, water near electrics, overheating,
# a brake problem, a boiler problem) a product case stores a decision with the rules that matched and the rule version,
# a STOP_USE case is a safety case (t.safety, "Safety first", the page's safety screen when its own words caught it),
# a professional-only case says only a qualified person should work on it, and no case offers Sorted's own checks.
# A safe description stores SAFE_EXTERNAL_CHECKS and offers no checks either (Phase 1 offers none).
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *
CASES = [
    ('sparking', 'washing_machine', 'It is sparking at the back when it spins', 'STOP_USE'),
    ('burning smell', 'tumble_dryer', 'There is a burning smell when it runs', 'STOP_USE'),
    ('smoke', 'dishwasher', 'Smoke came out of the bottom', 'STOP_USE'),
    ('gas', 'oven', 'I can smell gas near it', 'STOP_USE'),
    ('swollen battery', 'vacuum', 'The battery has swollen and the case is bulging', 'STOP_USE'),
    ('exposed cable', 'coffee', 'The cable is frayed and the wires are exposed', 'STOP_USE'),
    ('water near electrics', 'washing_machine', 'Water is pooling around the plug socket behind it', 'STOP_USE'),
    ('overheating', 'printer', 'It keeps overheating and the casing gets very hot', 'STOP_USE'),
    ('brake problem', 'other', 'The brakes are grinding and the pedal feels soft', 'PROFESSIONAL_ONLY'),
    ('boiler problem', 'boiler', 'No hot water and the pressure keeps dropping', 'PROFESSIONAL_ONLY'),
    ('safe', 'washing_machine', 'It won’t drain and the water stays in the drum', 'SAFE_EXTERNAL_CHECKS'),
]
with sync_playwright() as p:
    a = App(p, email=False); pg = a.pg
    for name, cat, words, want in CASES:
        before = set(c['id'] for c in a.cases())
        a.home(); a.tap('new-case'); pg.locator('[data-cap82=fix]').first.evaluate('e=>e.click()'); wait(pg, 400)
        pg.click('[data-a=prod161-type]'); wait(pg, 200)
        pg.fill('#prod-brand', 'Bosch'); pg.fill('#prod-model', 'TEST123X'); pg.locator('input[name=prod-cat][value=%s]' % cat).evaluate('e=>e.click()')
        pg.click('form[data-f=prod161] button[type=submit]'); wait(pg, 300)
        pg.fill('#gi-what', words); pg.locator('form[data-f=gi] button[type=submit]').first.click(); wait(pg, 800)
        screen = 'Stop. Don’t use it.' in a.main()
        if pg.locator('[data-a=safe-continue]').count(): pg.click('[data-a=safe-continue]'); wait(pg, 500)
        if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg, 400)
        if pg.locator('[data-a=vague-go]').count(): pg.click('[data-a=vague-go]'); wait(pg, 400)
        if pg.locator('form[data-f=baseline]').count(): pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 700)
        new = until(pg, lambda: [c for c in a.cases() if c['id'] not in before], 8000)
        if not new: ok(False, '%s: a case was made' % name); continue
        c = new[0]; d = (c.get('prod') or {}).get('safety') or {}
        ok(d.get('result') == want and d.get('rule_version') == 'ps-1' and isinstance(d.get('matched_rules'), list), '%s: %s stored with its rules and version (got %s %s)' % (name, want, d.get('result'), d.get('matched_rules')))
        a.open(c['id']); m = a.main()
        ok('Try these safe checks' not in m, '%s: no checks of Sorted’s own' % name)
        if want == 'STOP_USE':
            ok(c.get('safety') is True and 'Safety first' in m and 'could be dangerous' in m, '%s: a safety case, said on the case%s' % (name, ' (the safety screen first)' if screen else ''))
        elif want == 'PROFESSIONAL_ONLY':
            ok('Only a qualified person should work on this.' in m, '%s: only a qualified person' % name)
        else:
            ok(not c.get('safety') and 'Nothing you’ve said sounds dangerous.' in m, 'a safe description: no stop, said plainly')
    a.close()
finish()
