# v149: docs/STATUS.md and the README say what is actually deployed. Fails when a release forgets to update them,
# so an engineer or an AI agent can trust the one page that says what is current.
import os, re, hashlib
HERE = os.path.abspath('.'); fails = []
def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
page = open(HERE + '/public/index.html', 'rb').read()
sha = hashlib.sha1(page).hexdigest()
ver = re.search(rb'SORTED_V="(v\d+)"', page).group(1).decode()
st = open(HERE + '/docs/STATUS.md', encoding='utf-8').read()
rd = open(HERE + '/README.md', encoding='utf-8').read()
ok(('**Release:** ' + ver + ' ') in st, 'STATUS.md names the release the page says it is (%s)' % ver)
ok(sha in st, 'STATUS.md carries the page fingerprint %s' % sha)
ok(('sha1 %s for %s' % (sha, ver)) in rd, 'the README carries the same fingerprint and release')
ok('release v69' not in rd, 'the README no longer claims an old release')
builds = re.findall(r"'(build\d*\.js)'", open(HERE + '/all.js').read())
ok(builds and builds[-1] == 'build%s.js' % ver[1:], 'the last layer in all.js is this release (%s)' % (builds and builds[-1]))
print('ERRORS', [])
print('FAILS', fails)
