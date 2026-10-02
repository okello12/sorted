"""Test-only compatibility for the v75 grouped case page.

Older walkthroughs predate the two collapsed top-level case groups. They still
exercise the same controls, so for those older scripts we reveal the new groups
before waits/clicks. The dedicated v75/v76 walkthrough is excluded; it verifies
the real collapsed behaviour and opens groups like a user would.
"""
import os
import sys

if os.path.basename(sys.argv[0]) != "37_ui_consolidation.py":
    try:
        from playwright.sync_api import Page, Locator

        _page_wait = Page.wait_for_timeout
        _page_click = Page.click
        _locator_click = Locator.click

        def _reveal(page):
            try:
                page.locator("details.case75-group").evaluate_all(
                    "(groups) => groups.forEach((group) => { group.open = true; })"
                )
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
