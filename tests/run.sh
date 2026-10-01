#!/bin/sh
# Run from the repository root:  sh tests/run.sh
# Needs Python 3 with Playwright (chromium) and Node. Builds the page, then runs every walkthrough against it.
set -e
node all.js >/dev/null
[ -d tests/node_modules ] || (cd tests && npm ci --omit=optional --ignore-scripts --silent)
mkdir -p tests/out
fail=0
for t in tests/[0-9]*.py; do
  r=$(timeout 300 python3 "$t" 2>&1 | grep -E '^FAILS|^ERRORS|Error' | tr '\n' ' ')
  echo "$(basename "$t"): $r"
  echo "$r" | grep -q "FAILS \[\]" && echo "$r" | grep -q "ERRORS \[\]" || fail=1
done
exit $fail
