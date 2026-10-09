"""Test-only compatibility for the v75 grouped case page.

Older walkthroughs predate the two collapsed top-level case groups. They still
exercise the same controls, so for those older scripts we reveal the new groups
before waits/clicks. The dedicated v75/v76 walkthrough is excluded; it verifies
the real collapsed behaviour and opens groups like a user would.

Since v113 a returning Home keeps "Sort something new" (the six routes, the
examples, life moments and the search fold) closed until the person taps
"+ New" or "+ Sort something new". Walkthroughs written before then use those
controls directly, so they see the section open. 68 and 70 check the real
closed behaviour and open it the way a person does.
"""
import os
import sys

if os.path.basename(sys.argv[0]) != "37_ui_consolidation.py":
    try:
        from playwright.sync_api import Page, Locator

        _page_wait = Page.wait_for_timeout
        _page_click = Page.click
        _locator_click = Locator.click

        _closed_ok = os.path.basename(sys.argv[0]) in ("68_visual_v111.py", "70_setup_and_help.py")

        def _reveal(page):
            try:
                page.locator("details.case75-group").evaluate_all(
                    "(groups) => groups.forEach((group) => { group.open = true; })"
                )
            except Exception:
                pass
            if not _closed_ok:
                try:
                    page.evaluate("() => { const s = document.querySelector('#home111-new'); if (s) s.classList.add('open'); }")
                except Exception:
                    pass

        def _wait(self, timeout):
            result = _page_wait(self, timeout)
            _reveal(self)
            return result

        def _click(self, selector, *args, **kwargs):
            _reveal(self)
            return _page_click(self, selector, *args, **kwargs)

        def _loc_click(self, *args, **kwargs):
            try:
                _reveal(self.page)
            except Exception:
                pass
            return _locator_click(self, *args, **kwargs)

        Page.wait_for_timeout = _wait
        Page.click = _click
        Locator.click = _loc_click
    except Exception:
        # Some helper invocations may start Python without Playwright installed.
        pass

# v145: SORTED_SHIFT_DAYS=N runs a walkthrough as if today were N days from now, in Python (datetime.date.today,
# datetime.datetime.now) and in every browser page (Date), so a test that only passes on one weekday can be found:
#   SORTED_SHIFT_DAYS=3 PYTHONPATH=$PWD/tests TZ=Europe/London python3 tests/94_dates.py
# N may be a fraction (0.5 is twelve hours later), to try a walkthrough at another time of day. Test-only. Unset (the
# normal run) it changes nothing.
_shift = os.environ.get("SORTED_SHIFT_DAYS")
if _shift:
    try:
        import datetime as _dt
        _off = _dt.timedelta(days=float(_shift))
        _RealDate, _RealDT = _dt.date, _dt.datetime

        class _ShiftDate(_RealDate):
            @classmethod
            def today(cls):
                d = _RealDate.today() + _off
                return cls(d.year, d.month, d.day)

        class _ShiftDT(_RealDT):
            @classmethod
            def now(cls, tz=None):
                d = _RealDT.now(tz) + _off
                return cls(d.year, d.month, d.day, d.hour, d.minute, d.second, d.microsecond, d.tzinfo)

            @classmethod
            def today(cls):
                return cls.now()

        _dt.date, _dt.datetime = _ShiftDate, _ShiftDT
        _ms = int(round(float(_shift) * 86400000))
        # A page whose test installs its own clock (pg.clock.install) already asks for the shifted time, so the shifted
        # Date is taken out again there (window.__shiftR, put back by an init script registered just before Playwright's
        # own clock script), and Date and Date.now both come from Playwright's clock.
        _JS = ("(()=>{if(window.__shift145)return;window.__shift145=%d;const R=Date,O=%d;window.__shiftR=R;"
               "function D(...a){if(!new.target)return new D().toString();return a.length?new R(...a):new R(R.now()+O)}"
               "D.prototype=R.prototype;D.now=()=>R.now()+O;D.UTC=R.UTC;D.parse=R.parse;"
               "Object.defineProperty(D.prototype,'constructor',{value:D,configurable:true,writable:true});window.Date=D})()") % (_ms, _ms)
        from playwright.sync_api import Browser, BrowserContext
        _new_context = Browser.new_context

        def _ctx(self, *a, **k):
            c = _new_context(self, *a, **k)
            c.add_init_script(_JS)
            return c

        Browser.new_context = _ctx
        _new_page = Browser.new_page

        def _page(self, *a, **k):
            pg = _new_page(self, *a, **k)
            pg.add_init_script(_JS)
            return pg

        Browser.new_page = _page
        from playwright.sync_api._generated import Clock as _Clock

        for _name in ("install", "set_fixed_time", "set_system_time", "pause_at"):
            def _mk(orig):
                def _w(self, *a, **k):
                    try:
                        self._sync(self._impl_obj._browser_context.add_init_script(script="if(window.__shiftR){window.Date=window.__shiftR}"))
                    except Exception as _e2:
                        print("SORTED_SHIFT_DAYS: clock not marked:", _e2)
                    return orig(self, *a, **k)
                return _w
            setattr(_Clock, _name, _mk(getattr(_Clock, _name)))
        print("SHIFTED %s days: now is %s" % (_shift, _ShiftDT.now().isoformat(timespec="minutes")))
    except Exception as _e:
        print("SORTED_SHIFT_DAYS not applied:", _e)
