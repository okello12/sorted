# v169: context cards reuse the saved date wording and never infer a missed outcome.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attlib143 import *
with sync_playwright() as p:
    a = App(p, email=True); pg = a.pg
    late = a.start('Currys said the refund would arrive by %s' % long(day(6)))
    early = a.start('BT said an engineer would come on %s between 8 and 12' % long(day(3)))
    a.home()
    box = pg.locator('.context169-next')
    ok(box.count() == 1 and 'BT' in box.inner_text(), 'Home surfaces the nearest saved promise rather than insertion order')
    box.locator('button').click(); wait(pg)
    ok('BT' in pg.inner_text('main') and 'Currys' not in pg.locator('.case56-title').inner_text(), 'Review opens the matching case')
    a.task_js(early, "t.title='<img src=x onerror=alert(1)>';t.promises.forEach(function(p){p.prec='approx';p.phrase='sometime next week';p.party='<img src=x onerror=alert(1)>'})")
    a.home()
    ok('sometime next week' in pg.locator('.context169-next').inner_text().lower(), 'an approximate promise keeps its original uncertain wording')
    ok(pg.locator('.context169-next [onerror]').count() == 0, 'saved text cannot create an event handler in the date card')
    a.task_js(early, "t.title='BT engineer visit';t.promises.forEach(function(p){p.prec='day';delete p.phrase;p.party='BT'})")
    a.overdue(early, 2); a.home()
    why = pg.locator('.context169-why')
    ok(why.count() == 1 and not why.locator('p').first.is_visible(), 'the leading case has a folded explanation')
    why.locator('summary').focus(); pg.keyboard.press('Enter')
    ok(why.locator('p').first.is_visible() and 'does not tell Sorted whether it happened' in why.inner_text(), 'keyboard opens the explanation without assuming a missed outcome')
    ok(a.openp(early)[0]['status'] == 'open', 'viewing the reason never marks their promise missed')
    for width in (320, 390, 768):
        pg.set_viewport_size({'width': width, 'height': 844})
        ok(pg.evaluate('document.documentElement.scrollWidth<=document.documentElement.clientWidth+1'), 'context cards fit at %dpx' % width)
    pg.set_viewport_size({'width': 390, 'height': 844})
    pg.screenshot(path=HERE + '/tests/out/context169-mobile.png', full_page=True)
    a.task_js(late, "t.promises.forEach(function(p){p.dueAt=null;p.dueEnd=null})")
    a.home()
    ok(pg.locator('.context169-next').count() == 0, 'no tracked date card appears when there is no dated waiting promise')
    a.close()
finish()
