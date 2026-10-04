# v80: styling only. Text colours meet the contrast standard in light and dark mode, colours keep one meaning each,
# buttons don't loop an animation, and nothing scrolls sideways.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dates
from playwright.sync_api import sync_playwright
HERE = os.path.abspath('.'); errs = []; fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def wait(pg, ms=400): pg.wait_for_timeout(ms)
def db(pg): return pg.evaluate("JSON.parse(localStorage.getItem('__mockdb'))")
# contrast of an element's text against the nearest solid background behind it (gradients: their first colour stop)
CR = """(sel)=>{const el=document.querySelector(sel);if(!el)return null;
 const rgb=s=>{if(!s)return null;const m=s.match(/[\\d.]+/g);if(!m)return null;let v=m.map(Number);if(/^color\\(srgb/.test(s)){v=v.slice(0,4);v=[v[0]*255,v[1]*255,v[2]*255,v[3]===undefined?1:v[3]]}return v.slice(0,4)};
 const lum=c=>{const f=x=>{x/=255;return x<=0.03928?x/12.92:Math.pow((x+0.055)/1.055,2.4)};return 0.2126*f(c[0])+0.7152*f(c[1])+0.0722*f(c[2])};
 let fg=rgb(getComputedStyle(el).color),n=el,bg=null;
 while(n&&!bg){const cs=getComputedStyle(n),b=rgb(cs.backgroundColor);if(b&&(b[3]===undefined||b[3]>0.5))bg=b;else{const im=cs.backgroundImage.match(/rgba?\\([^)]*\\)/);if(im){const c=rgb(im[0]);if(c&&(c[3]===undefined||c[3]>0.5))bg=c}}n=n.parentElement}
 bg=bg||rgb(getComputedStyle(document.body).backgroundColor);const a=lum(fg),b=lum(bg);return (Math.max(a,b)+0.05)/(Math.min(a,b)+0.05)}"""
def start(pg, text):
    pg.goto('https://sorted.test/'); wait(pg)
    if pg.locator('[data-a=compose]').count(): pg.click('[data-a=compose]'); wait(pg)
    pg.fill('#f-case', text); pg.click('form[data-f=case] button[type=submit]'); wait(pg)
    if pg.locator('[data-a=match-new]').count(): pg.click('[data-a=match-new]'); wait(pg)
    pg.click('form[data-f=baseline] .chip >> nth=0'); pg.click('form[data-f=baseline] button[type=submit]'); wait(pg, 500)
    if pg.locator('[data-a=sug-yes]').count(): pg.click('[data-a=sug-yes]'); wait(pg)
    if pg.locator('text=Not now').count(): pg.click('text=Not now'); wait(pg, 150)
    return sorted([x['data'] for x in db(pg)['tasks']], key=lambda x: x.get('created') or '')[-1]['id']
with sync_playwright() as p:
    b = p.chromium.launch()
    for scheme in ['light', 'dark']:
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London', color_scheme=scheme)
        ctx.route('https://cdn.jsdelivr.net/**', lambda r: r.fulfill(path=HERE + '/tests/mock.js', content_type='application/javascript'))
        ctx.route(lambda u: u.startswith('https://sorted.test/'), lambda r: r.fulfill(path=HERE + '/tests/out/index.html', content_type='text/html') if '/art/' not in r.request.url else r.fulfill(body=''))
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('https://sorted.test/'); wait(pg, 600)
        ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), '%s: the landing page doesn’t scroll sideways' % scheme)
        ok(pg.locator('.ex126').count() == 1 and (pg.evaluate(CR, '.ex126 p') or 0) >= 4.5 and (pg.evaluate(CR, '.hero126 .hero-sub') or 0) >= 4.5, '%s: the landing example and the hero text are readable (v126)' % scheme)
        ok(pg.evaluate("(()=>{const r=document.querySelector('.hero .eyebrow');if(!r)return true;const h=parseFloat(getComputedStyle(r).lineHeight)||16;return r.getBoundingClientRect().height<h*2.6})()"), '%s: the line above the headline is balanced' % scheme)
        pg.goto('https://sorted.test/#start'); pg.evaluate("localStorage.clear();localStorage.setItem('__emailReady','1')"); pg.reload(); wait(pg, 200); pg.click('[data-a=anon-start]'); wait(pg)
        a = start(pg, "Currys promised a refund of £89 by Friday, order 445566")
        c = start(pg, "Argos promised a refund of £40 by Friday, order 778899")
        start(pg, "British Gas said the engineer will come on 20 December between 8 and 12")
        start(pg, "London Borough of Southwark PENALTY CHARGE NOTICE PCN Number: SK12345678 The penalty charge is £130.")
        pg.evaluate("()=>{var d=JSON.parse(localStorage.getItem('__mockdb'));d.tasks.forEach(y=>{if(/refund/i.test(y.data.title))y.data.promises.forEach(q=>{if(q.status==='open')q.dueAt=new Date(Date.now()-2*864e5).toISOString()})});localStorage.setItem('__mockdb',JSON.stringify(d));Object.keys(localStorage).filter(k=>k.startsWith('sorted.cache.')).forEach(k=>localStorage.removeItem(k))}")
        pg.goto('https://sorted.test/'); wait(pg, 700)
        ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), '%s: Home doesn’t scroll sideways' % scheme)
        for sel, name in [('.home44-section.needs .h2', 'Also open heading'), ('.home44-section.waiting .h2', 'Waiting heading'), ('.home44-row-title', 'row title'), ('.home44-row-meta', 'row details'), ('.case75-row-ref', 'row Ref'), ('button.link, a.link', 'link')]:
            v = pg.evaluate(CR, sel)
            ok(v is not None and v >= 4.5, '%s: %s contrast %.1f (at least 4.5)' % (scheme, name, v or 0))
        anim = pg.evaluate("getComputedStyle(document.querySelector('.btn.primary')||document.body).animationName")
        ok(anim in ('none', ''), '%s: the main button doesn’t loop an animation' % scheme)
        needs = pg.evaluate("getComputedStyle(document.querySelector('.home44-section.needs .h2')).color")
        wait_c = pg.evaluate("getComputedStyle(document.querySelector('.home44-section.waiting .h2')).color")
        btn = pg.evaluate("getComputedStyle(document.querySelector('.btn.primary')).backgroundImage")
        ok(needs != wait_c and 'rgb(109, 76, 255)' not in wait_c, '%s: Needs you and Waiting have their own colours, not the buttons’ violet' % scheme)
        pg.locator('[data-a=open][data-id="%s"]' % a).first.click(); wait(pg, 600)
        v = pg.evaluate(CR, '.case75-title-ref')
        ok(v is not None and v >= 4.5, '%s: the case Ref contrast %.1f (at least 4.5)' % (scheme, v or 0))
        pg.screenshot(path='tests/out/40_%s_case.png' % scheme, full_page=True)
        ctx.close()
    b.close()
print('ERRORS', errs); print('FAILS', fails)
