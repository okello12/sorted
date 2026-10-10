"""Runs the numbered test files, one after another or several at once.

    python3 tests/runner.py                 # serial, in name order (what run.sh did before v114)
    python3 tests/runner.py --jobs 4        # four files at a time
    python3 tests/runner.py --jobs 6 --shuffle 7   # random order, seed 7 (the isolation check)

Each file's whole output goes to tests/out/logs/<file>.log, so files running together never mix their output.
The summary is printed in name order whatever order the files ran in, with the same line per file as before:
"<file>: FAILS [] ERRORS []", every FINDING, and a list of findings at the end. Exit status 1 if any file did not end
with both FAILS [] and ERRORS [].

Run it through tests/run.sh, which builds the page and sets TZ and PYTHONPATH first.
"""
import argparse, concurrent.futures as cf, glob, os, random, subprocess, sys, time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GH = bool(os.environ.get('GITHUB_ACTIONS'))


def run_one(path, logdir, timeout):
    name = os.path.basename(path)
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, path], cwd=HERE, capture_output=True, text=True, timeout=timeout)
        out = p.stdout + p.stderr
    except subprocess.TimeoutExpired as e:
        out = ((e.stdout or b'').decode('utf8', 'replace') if isinstance(e.stdout, bytes) else (e.stdout or '')) + \
              '\nError: timed out after %ss\n' % timeout
    secs = time.time() - t0
    with open(os.path.join(logdir, name + '.log'), 'w', encoding='utf8') as f:
        f.write(out)
    return name, out, secs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=int(os.environ.get('SORTED_JOBS', '1')))
    ap.add_argument('--shuffle', type=int, default=None, help='random order with this seed')
    ap.add_argument('--timeout', type=int, default=450)  # v164: 106 and 107 run close to 300s with four at a time
    ap.add_argument('--logdir', default=os.path.join(HERE, 'tests', 'out', 'logs'))
    ap.add_argument('files', nargs='*')
    a = ap.parse_args()
    files = a.files or sorted(glob.glob(os.path.join(HERE, 'tests', '[0-9]*.py')))
    order = list(files)
    if a.shuffle is not None:
        random.Random(a.shuffle).shuffle(order)
    os.makedirs(a.logdir, exist_ok=True)
    t0 = time.time()
    res = {}
    with cf.ThreadPoolExecutor(max_workers=max(1, a.jobs)) as ex:
        for name, out, secs in ex.map(lambda f: run_one(f, a.logdir, a.timeout), order):
            res[name] = (out, secs)
    fail = 0
    findings = []
    for name in sorted(res):
        out, secs = res[name]
        lines = out.splitlines()
        r = ' '.join(l for l in lines if l.startswith('FAILS') or l.startswith('ERRORS') or 'Error' in l)
        print('%s: %s' % (name, r))
        f = ['  %s %s' % (name, l) for l in lines if l.startswith('FINDING ')]
        if f:
            print('\n'.join(f))
            findings += f
        if not ('FAILS []' in r and 'ERRORS []' in r):
            fail = 1
            if GH:
                why = [l for l in lines if l.startswith(('FAIL ', 'FAILS', 'ERRORS', 'Traceback')) or 'Error' in l][-8:]
                print('::error title=%s::%s' % (name, ' '.join(why)[:900]))
    if findings:
        print('\nFindings (not failures, but read them):\n' + '\n'.join(findings))
    slow = sorted(res.items(), key=lambda kv: -kv[1][1])[:5]
    print('\n%d files, %d at a time, %.0fs. Slowest: %s' % (len(res), a.jobs, time.time() - t0,
          ', '.join('%s %.0fs' % (n, v[1]) for n, v in slow)))
    sys.exit(fail)


if __name__ == '__main__':
    main()
