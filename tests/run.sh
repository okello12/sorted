#!/bin/sh
# Run from the repository root:  sh tests/run.sh
# Needs Python 3 with Playwright (chromium) and Node. Builds the page, then runs every walkthrough against it.
set -e
export TZ=Europe/London   # the app's users are in the UK; see tests/dates.py
# Makes tests/sitecustomize.py available. It lets pre-v75 walkthroughs open the
# new top-level case groups before touching controls that used to be always visible.
export PYTHONPATH="$PWD/tests${PYTHONPATH:+:$PYTHONPATH}"
node all.js >/dev/null
[ -d tests/node_modules ] || (cd tests && npm ci --omit=optional --ignore-scripts --silent)
mkdir -p tests/out
# Tests swap in tests/mock.js for the database library, so drop that one script's fingerprint in the test copy.
# 12_audit_fixes.py checks the fingerprint in the real page against the npm package.
sed 's#\(supabase-js@[0-9.]*/dist/umd/supabase.js"\) integrity="[^"]*"#\1#' public/index.html > tests/out/index.html
node tests/make_reader.js
# a control character in the page means an escaping mistake in a generator (a "\\b" that became a backspace, say)
if LC_ALL=C grep -qP '[\x00-\x08\x0B\x0C\x0E-\x1F]' public/index.html; then echo "control character in public/index.html: an escaping mistake in a build layer"; exit 1; fi
fail=0
findings=""
for t in tests/[0-9]*.py; do
  out=$(timeout 300 python3 "$t" 2>&1) || true
  r=$(echo "$out" | grep -E '^FAILS|^ERRORS|Error' | tr '\n' ' ')
  echo "$(basename "$t"): $r"
  # a FINDING is something a test noticed but doesn't fail on; show it so a green run can't hide it
  f=$(echo "$out" | grep -E '^FINDING ' | sed "s#^#  $(basename "$t") #")
  [ -n "$f" ] && echo "$f" && findings="$findings
$f"
  echo "$r" | grep -q "FAILS \[\]" && echo "$r" | grep -q "ERRORS \[\]" || fail=1
done
[ -n "$findings" ] && printf '\nFindings (not failures, but read them):%s\n' "$findings"
exit $fail
