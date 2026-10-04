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
