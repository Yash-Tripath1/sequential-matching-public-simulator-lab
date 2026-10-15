#!/usr/bin/env python3
"""Paired waiting-time comparison between two arms.

This is the script that produced the ship decision in section 13 of
ROUND2_FINDINGS.md: greedy and oldest_first tie on the primary outcome
(p = 0.736), so the decision was made on the waiting-time distribution
instead, where oldest_first wins the tail.

Usage:
    python3 wait_comparison.py out/members.jsonl greedy oldest_first

Reads the per-member JSONL written by waitlab.py. Lower wait is better.
"""
import json
import random
import statistics
import sys
from collections import defaultdict

VAR = ('development', 'sparse', 'cold_start', 'delayed', 'shift', 'drift')


def load(path, arms):
    waits = defaultdict(list)   # (arm, seed) -> [wait of each served member]
    unserv = defaultdict(int)   # (arm, seed, variant) -> never introduced
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        a = r['arm']
        if a not in arms:
            continue
        if r.get('fid') is None:
            unserv[(a, r['seed'], r['variant'])] += 1
        else:
            waits[(a, r['seed'])].append(r['wait'])
    return waits, unserv


def pct(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(p * len(v)))]


def boot(d, n=20000, seed=13):
    r = random.Random(seed)
    x = list(d.values())
    k = len(x)
    draws = sorted(statistics.fmean(r.choices(x, k=k)) for _ in range(n))
    return statistics.fmean(x), draws[int(.025 * n)], draws[int(.975 * n)]


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'out/members.jsonl'
    a1 = sys.argv[2] if len(sys.argv) > 2 else 'greedy'
    a2 = sys.argv[3] if len(sys.argv) > 3 else 'oldest_first'
    arms = {a1, a2}

    waits, unserv = load(path, arms)
    seeds = sorted({s for _, s in waits})
    if not seeds:
        sys.exit(f'no rows for arms {sorted(arms)} in {path}')

    metrics = [
        ('mean wait (served)',  lambda a, s: statistics.fmean(waits[(a, s)])),
        ('median wait (served)',lambda a, s: statistics.median(waits[(a, s)])),
        ('p90 wait (served)',   lambda a, s: pct(waits[(a, s)], .90)),
        ('max wait (served)',   lambda a, s: max(waits[(a, s)])),
        ('unserved / 200',      lambda a, s: statistics.fmean(
                                    unserv[(a, s, v)] for v in VAR)),
    ]

    print('=' * 94)
    print(f'WAITING TIME  --  {a1} vs {a2}   ({len(seeds)} seeds, paired)')
    print('lower is better for every row except unserved')
    print('=' * 94)
    print(f"{'metric':22s} {a1[:8]:>9s} {a2[:8]:>9s} {'diff':>8s} "
          f"{'95% CI':>18s} {'W/T/L':>13s}  verdict")
    print('-' * 94)
    for name, fn in metrics:
        d = {s: fn(a1, s) - fn(a2, s) for s in seeds}
        m, lo, hi = boot(d)
        g = statistics.fmean(fn(a1, s) for s in seeds)
        o = statistics.fmean(fn(a2, s) for s in seeds)
        w = sum(1 for v in d.values() if v > 1e-9)
        l = sum(1 for v in d.values() if v < -1e-9)
        verdict = (f'{a1} higher' if lo > 0 else
                   f'{a2} higher' if hi < 0 else 'tie')
        print(f'{name:22s} {g:9.3f} {o:9.3f} {m:+8.3f} '
              f'[{lo:+.3f},{hi:+.3f}] {w:4d}/{len(d)-w-l:3d}/{l:4d}  {verdict}')
    print('-' * 94)


if __name__ == '__main__':
    main()
