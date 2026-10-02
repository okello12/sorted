"""Test-only compatibility for the v75 grouped case page.

Older walkthroughs predate the two collapsed top-level case groups. They still
exercise the same controls, so when those older scripts pause we open only the
new top-level groups for them. The dedicated v75/v76 walkthrough is excluded;
it verifies the real collapsed behaviour and opens groups like a user would.
"""
import os
import sys

if os.path.basename(sys.argv[0]) != "37_ui_consolidation.py":
    try:
        from playwright.sync_api import Page

        _original_wait_for_timeout = Page.wait_for_timeout

        def _wait_for_timeout_and_reveal_case_groups(self, timeout):
            result = _original_wait_for_timeout(self, timeout)
            try:
                self.locator("details.case75-group").evaluate_all(
                    "(groups) => groups.forEach((group) => { group.open = true; })"
                )
            except Exception:
                # Before navigation, or on pages without a case, there is nothing
                # to reveal. The walkthrough should continue exactly as before.
                pass
            return result

        Page.wait_for_timeout = _wait_for_timeout_and_reveal_case_groups
    except Exception:
        # Some non-browser helper invocations may start Python without Playwright.
        pass
