#!/usr/bin/env python3
"""equivalence_check.py: confirm the two implementations of the candidate agree.

`disagreement_aware` deliberately exists in two places:

  * `policy.py:pairs_greedy_signed`: a selectable arm, so that anyone can
    reproduce the result with `ROUND2_ARM=disagreement_aware` through the
    organisers' own `evaluate.py`.
  * `waitlab.py:pairs_disagreement_aware`: the arm that actually produced the
    120-seed numbers in REPORT.md section 5.15, inside the instrumented harness
    that records per-member and waiting-time data.

Two copies of one idea are a liability unless they are *shown* to agree. This
script runs both over the same states, drawn from real episodes, and reports
whether they ever return a different matching.

Run from the project root:

    python3 code/equivalence_check.py --seeds 1101-1103
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "code"))

from kit import Simulator, generate  # noqa: E402

import policy  # noqa: E402
import waitlab  # noqa: E402

VARIANTS = ("development", "sparse", "cold_start", "delayed", "shift", "drift")


def parse_seeds(spec: str) -> list[int]:
    out: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part.lstrip("-"):
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return sorted(set(out))


def norm(pairs) -> set:
    return {frozenset(p) for p in pairs}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="1101-1103")
    ap.add_argument("--days", type=int, default=60)
    args = ap.parse_args()

    seeds = parse_seeds(args.seeds)
    comparisons = 0
    mismatches = []
    empty_days = 0

    for seed in seeds:
        for variant in VARIANTS:
            sim = Simulator(generate(seed, 200, "evaluation", variant))
            for day in range(args.days):
                sim.resolve_asks(policy.baseline_asks(sim.observe()))
                state = sim.observe()
                a = norm(policy.pairs_greedy_signed(state))
                b = norm(waitlab.pairs_disagreement_aware(state))
                comparisons += 1
                if not a:
                    empty_days += 1
                if a != b:
                    mismatches.append({"seed": seed, "variant": variant, "day": day,
                                       "policy_only": sorted(map(sorted, a - b))[:3],
                                       "waitlab_only": sorted(map(sorted, b - a))[:3]})
                sim.advance([list(p) for p in a])

    print(f"equivalence check: policy.pairs_greedy_signed vs waitlab.pairs_disagreement_aware")
    print(f"  seeds          : {seeds[0]}–{seeds[-1]} ({len(seeds)})")
    print(f"  decision days  : {comparisons}  ({len(seeds)} seeds x {len(VARIANTS)} variants x {args.days} days)")
    print(f"  days with no feasible pair: {empty_days}")
    print(f"  mismatches     : {len(mismatches)}")
    for m in mismatches[:5]:
        print(f"      {m}")
    ok = not mismatches
    print()
    print("RESULT:", "IDENTICAL on every state compared" if ok else "DIVERGENT: do not ship the candidate")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
