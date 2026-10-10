# v161: the product modules (src/product, docs/PRODUCT_PHASE1.md) tested on their own in Node, the same bytes the
# page runs: label and receipt reading, the record's statuses and history, masking, the safety rules and their
# version, the registry's official-domain rule, and the routes.
import subprocess, sys, os
HERE = os.path.abspath('.')
p = subprocess.run(['node', HERE + '/tests/product/units.mjs'], capture_output=True, text=True)
sys.stdout.write(p.stdout); sys.stdout.write(p.stderr)
if p.returncode and 'FAILS [' not in p.stdout:
    print('ERRORS', [p.stderr[-300:]]); print('FAILS', ['units did not run'])
