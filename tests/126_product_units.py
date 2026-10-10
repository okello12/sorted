# v161: the product modules (src/product, docs/PRODUCT_PHASE1.md) tested on their own in Node, the same bytes the
# page runs: label and receipt reading, the record's statuses and history, masking, the safety rules and their
# version, the registry's official-domain rule, and the routes.
import subprocess, sys, os
HERE = os.path.abspath('.')
# since v164 (the Phase 1.5 audit) also the safety corpus: everyday dangerous, professional-only and safe descriptions
errs, fails = [], []
for f in ('units.mjs', 'safety_corpus.mjs'):
    p = subprocess.run(['node', HERE + '/tests/product/' + f], capture_output=True, text=True)
    out = p.stdout
    sys.stdout.write('\n'.join(l for l in out.splitlines() if not l.startswith(('ERRORS', 'FAILS'))) + '\n')
    if 'FAILS []' not in out: fails.append(f + ': ' + (out.split('FAILS', 1)[-1].strip()[:300] or p.stderr[-300:]))
print('ERRORS', errs); print('FAILS', fails)
