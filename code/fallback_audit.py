#!/usr/bin/env python3
"""fallback_audit.py — count silent fallbacks and measure per-call latency.

Why this exists
---------------
`policy.py` deliberately falls back to an empty, valid action if any arm
raises. That is the correct safety choice: the rules say an invalid assessed
episode makes the whole entry ineligible.

Falling back *silently* is not correct. The supplied `evaluate.py` only reads
stderr when the child exits non-zero, so a fallback would otherwise be scored
as a perfectly valid episode with zero introductions and no visible trace.

`policy.py` therefore counts fallbacks in `memory`, which the protocol carries
across calls and back to the harness. This script runs complete episodes
through the same `decide()` entry point the evaluator uses — in process, so it
is fast enough to run over hundreds of episodes — and reports:

  * fallbacks per arm, and the first few reasons if any occurred
  * the largest single-invocation time, against the 10 s per-call rule limit

Usage (from the project root)
-----------------------------
    python3 code/fallback_audit.py --seeds 1101-1110
    python3 code/fallback_audit.py --seeds 101,102 --arms greedy --selftest
"""
from __future__ import annotations

import argparse
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "code"))

import kit  # noqa: E402
from kit import Simulator, generate, VERSION  # noqa: E402

import policy  # noqa: E402

VARIANTS = ("development", "sparse", "cold_start", "delayed", "shift", "drift")
RULE_LIMIT_S = 10.0


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


def episode(world, arm: str) -> dict:
    """Mirror evaluate.py::episode, but call decide() in process."""
    sim = Simulator(world)
    memory = None
    calls = 0
    total = 0.0
    worst = 0.0
    for _ in range(60):
        for phase in ("ask", "match"):
            request = {"schema_version": VERSION, "phase": phase,
                       "state": sim.observe(), "memory": memory}
            t0 = time.perf_counter()
            response = policy.decide(request, arm)
            dt = time.perf_counter() - t0
            calls += 1
            total += dt
            worst = max(worst, dt)
            memory = response.get("memory")
            action = response.get("asks" if phase == "ask" else "pairs")
            if phase == "ask":
                sim.resolve_asks(action)
            else:
                sim.advance(action)
    for _ in range(40):
        sim.advance([])
    m = sim.metrics()
    mem = memory or {}
    return {"msmi": m["mutual_second_meeting_intention"], "calls": calls,
            "total_s": round(total, 3), "max_call_s": round(worst, 4),
            "fallbacks": int(mem.get("fallbacks", 0)),
            "reasons": mem.get("fallback_reasons") or []}


def selftest() -> int:
    """Prove the counter works by provoking a fallback."""
    bad = {"phase": "match",
           "state": {"day": 0, "members": [{"member_id": "x"}],  # no 'available'
                     "introductions": []},
           "memory": {}}
    out = policy.decide(bad, "greedy")
    n = int((out.get("memory") or {}).get("fallbacks", 0))
    print(f"selftest: deliberately malformed state -> fallbacks counter = {n}")
    ok = n >= 1
    print("selftest:", "PASS (counter is wired)" if ok else "FAIL (counter not incremented)")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="1101-1110")
    ap.add_argument("--arms", default="greedy,disagreement_aware")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    seeds = parse_seeds(args.seeds)
    arms = [a for a in args.arms.split(",") if a.strip()]

    print(f"fallback audit — {len(seeds)} seeds x {len(VARIANTS)} variants "
          f"x {len(arms)} arms = {len(seeds) * len(VARIANTS) * len(arms)} episodes")
    print(f"rule limit: {RULE_LIMIT_S:.0f} s per invocation\n")

    worst_overall = 0.0
    total_fallbacks = 0
    for arm in arms:
        rows = []
        for seed in seeds:
            for variant in VARIANTS:
                rows.append(episode(generate(seed, 200, "evaluation", variant), arm))
        fb = sum(r["fallbacks"] for r in rows)
        worst = max(r["max_call_s"] for r in rows)
        worst_overall = max(worst_overall, worst)
        total_fallbacks += fb
        reasons = [x for r in rows for x in r["reasons"]][:5]
        print(f"  {arm:22s} episodes={len(rows):4d}  fallbacks={fb}  "
              f"max single call={worst:.4f}s  mean episode={statistics.fmean(r['total_s'] for r in rows):.2f}s")
        for x in reasons:
            print(f"        reason: {x}")

    print()
    print(f"TOTAL fallbacks across all audited episodes: {total_fallbacks}")
    print(f"Largest single invocation anywhere: {worst_overall:.4f} s "
          f"(limit {RULE_LIMIT_S:.0f} s) -> "
          f"{'WITHIN LIMIT' if worst_overall < RULE_LIMIT_S else 'EXCEEDS LIMIT'}")
    return 0 if total_fallbacks == 0 and worst_overall < RULE_LIMIT_S else 1


if __name__ == "__main__":
    raise SystemExit(main())
