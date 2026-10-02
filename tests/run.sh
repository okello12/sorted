#!/bin/sh
# Run from the repository root:  sh tests/run.sh
# Needs Python 3 with Playwright (chromium) and Node. Builds the page, then runs every walkthrough against it.
set -e
export TZ=Europe/London   # the app's users are in the UK; see tests/dates.py
node all.js >/dev/null
[ -d tests/node_modules ] || (cd tests && npm ci --omit=optional --ignore-scripts --silent)
mkdir -p tests/out
# Tests swap in tests/mock.js for the database library, so drop that one script's fingerprint in the test copy.
# 12_audit_fixes.py checks the fingerprint in the real page against the npm package.
sed 's#\(supabase-js@[0-9.]*/dist/umd/supabase.js"\) integrity="[^"]*"#\1#' public/index.html > tests/out/index.html
node tests/make_reader.js
fail=0
for t in tests/[0-9]*.py; do
  r=$(timeout 300 python3 "$t" 2>&1 | grep -E '^FAILS|^ERRORS|Error' | tr '\n' ' ')
  echo "$(basename "$t"): $r"
  echo "$r" | grep -q "FAILS \[\]" && echo "$r" | grep -q "ERRORS \[\]" || fail=1
done
exit $fail
