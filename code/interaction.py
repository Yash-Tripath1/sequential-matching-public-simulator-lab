"""Ask x allocation interaction on fresh seeds. Answers Round 2 question 2.

Design (all four cells at 120 seeds, paired on identical worlds):

                     greedy matcher      random matcher
    default asks     greedy              random_feasible
    no asks          no_ask              no_ask_random

    main effect of asking    = mean[(greedy - no_ask) + (random - no_ask_random)] / 2
    main effect of matcher   = mean[(greedy - random) + (no_ask - no_ask_random)] / 2
    interaction              = (greedy - no_ask) - (random - no_ask_random)

Interaction near zero means the two components act additively: the value of
clarification does not depend on how you allocate, and vice versa. That is the
answer to "which interactions remain once each component is varied separately".

Usage:
    python3 interaction.py --out ~/out_2x2
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

VARIANTS = ("development", "sparse", "cold_start", "delayed", "shift", "drift")
CELLS = {"greedy": ("default", "greedy"),
         "random_feasible": ("default", "random"),
         "no_ask": ("none", "greedy"),
         "no_ask_random": ("none", "random")}


def load(out: Path) -> dict:
    """arm -> seed -> variant -> msmi_per_100 for that episode."""
    tab: dict[str, dict[int, dict[str, float]]] = defaultdict(
        lambda: defaultdict(dict))
    for line in (out / "episodes.jsonl").open():
        r = json.loads(line)
        if not r.get("valid") or not r.get("metrics"):
            continue
        m = r["metrics"]
        tab[r["arm"]][r["seed"]][r["variant"]] = (
            100 * m["mutual_second_meeting_intention"]
            / max(1, m["arrived_members"]))
    return tab


def per_seed(tab, arm):
    """Seed score = unweighted mean of the six family means."""
    out = {}
    for seed, fam in tab[arm].items():
        if len(fam) >= 6:
            out[seed] = statistics.fmean(fam[v] for v in VARIANTS)
    return out


def sign_flip_p(diffs: list[float], draws=20000, rng_seed=20261016) -> float:
    """Exact-ish two-sided sign-flip test on seed-block differences."""
    if not diffs:
        return float("nan")
    rng = random.Random(rng_seed)
    obs = abs(statistics.fmean(diffs))
    n = len(diffs)
    if n <= 20:                       # exact enumeration
        import itertools
        cnt = tot = 0
        for signs in itertools.product((-1, 1), repeat=n):
            tot += 1
            if abs(statistics.fmean(s * d for s, d in zip(signs, diffs))) >= obs - 1e-12:
                cnt += 1
        return cnt / tot
    hits = sum(1 for _ in range(draws)
               if abs(statistics.fmean(rng.choice((-1, 1)) * d for d in diffs)) >= obs)
    return hits / draws


def boot(diffs: list[float], draws=10000, rng_seed=20261016):
    rng = random.Random(rng_seed)
    vals = []
    for _ in range(draws):
        vals.append(statistics.fmean(rng.choice(diffs) for _ in diffs))
    vals.sort()
    return vals[int(.025 * len(vals))], vals[int(.975 * len(vals))]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out_2x2")
    ap.add_argument("--save", default=None)
    a = ap.parse_args()

    tab = load(Path(a.out))
    missing = [c for c in CELLS if c not in tab]
    if missing:
        print(f"  MISSING CELLS: {missing}. Run those arms first.")
        return 1

    ps = {c: per_seed(tab, c) for c in CELLS}
    seeds = sorted(set.intersection(*[set(ps[c]) for c in CELLS]))
    print(f"  {len(seeds)} seeds present in all four cells\n")

    d = {c: [ps[c][s] for s in seeds] for c in CELLS}

    # per-seed differences
    ask_eff_greedy = [g - n for g, n in zip(d["greedy"], d["no_ask"])]
    ask_eff_random = [r - n for r, n in zip(d["random_feasible"], d["no_ask_random"])]
    mat_eff_ask = [g - r for g, r in zip(d["greedy"], d["random_feasible"])]
    mat_eff_noask = [n - nr for n, nr in zip(d["no_ask"], d["no_ask_random"])]
    inter = [a_ - b_ for a_, b_ in zip(ask_eff_greedy, ask_eff_random)]

    print("=== cell means (MSMI/100) ===")
    for c in ("greedy", "random_feasible", "no_ask", "no_ask_random"):
        print(f"  {c:18s} {statistics.fmean(d[c]):.3f}   n={len(d[c])}")

    print("\n=== main effects and interaction ===")
    print(f"  {'effect':34s} {'mean':>8s} {'95% CI':>20s} {'p':>8s}")
    res = {}
    for label, diffs in (
        ("ask effect | greedy matcher", ask_eff_greedy),
        ("ask effect | random matcher", ask_eff_random),
        ("matcher effect | default asks", mat_eff_ask),
        ("matcher effect | no asks", mat_eff_noask),
        ("ASK main effect (averaged)", [(x + y) / 2 for x, y in
                                        zip(ask_eff_greedy, ask_eff_random)]),
        ("MATCHER main effect (averaged)", [(x + y) / 2 for x, y in
                                            zip(mat_eff_ask, mat_eff_noask)]),
        ("ASK x MATCHER interaction", inter),
    ):
        pt = statistics.fmean(diffs)
        lo, hi = boot(diffs)
        p = sign_flip_p(diffs)
        res[label] = {"mean": pt, "lo": lo, "hi": hi, "p": p}
        print(f"  {label:34s} {pt:+8.3f} {'['+f'{lo:+.3f}, {hi:+.3f}'+']':>20s} {p:8.3f}")

    print("\n  Interpretation: interaction CI spanning zero and p near 1 means the")
    print("  two components act additively - the value of clarification does not")
    print("  depend on the allocation rule, and vice versa.")

    if a.save:
        Path(a.save).write_text(json.dumps(
            {"n_seeds": len(seeds), "cells": {c: statistics.fmean(d[c]) for c in CELLS},
             "effects": res}, indent=2))
        print(f"\n  wrote {a.save}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
