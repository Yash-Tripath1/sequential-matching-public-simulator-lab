#!/usr/bin/env python3
"""Analysis for the Round 2 waiting-time / disparity experiment.

Statistical conventions (deliberately stricter than the Round 1 note):
  * The resampling unit is the SEED, never the episode and never the
    scenario. Within a seed, development/delayed/shift/drift are the SAME
    200 members, so a per-family bootstrap across seeds is invalid.
  * Paired contrasts are computed on identical (seed, variant) worlds.
  * Exact sign-flip permutation when n_seeds <= 20, otherwise a
    200,000-draw Monte Carlo sign-flip, always reported alongside W/T/L.
  * No multiplicity correction; the number of contrasts is stated.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import random
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANALYSIS_SEED = 20261010
VARIANTS = ("development", "sparse", "cold_start", "delayed", "shift", "drift")


# ------------------------------------------------------------------ bootstrap
def seed_block_bootstrap(family_by_seed: dict[int, dict[str, float]], draws=10000, rng=None):
    """Resample seeds; each seed contributes the mean of its six family scores."""
    rng = rng or random.Random(ANALYSIS_SEED)
    seeds = sorted(family_by_seed)
    blocks = [statistics.mean(family_by_seed[s][v] for v in family_by_seed[s]) for s in seeds]
    n = len(blocks)
    out = []
    for _ in range(draws):
        out.append(statistics.fmean(blocks[rng.randrange(n)] for _ in range(n)))
    out.sort()
    return out[int(0.025 * draws)], out[int(0.975 * draws)]


def sign_flip_p(diffs: list[float], draws=200000, rng=None):
    """Two-sided sign-flip test on the per-seed differences."""
    rng = rng or random.Random(ANALYSIS_SEED)
    n = len(diffs)
    obs = abs(statistics.fmean(diffs))
    if obs == 0:
        return 1.0
    if n <= 20:
        count = 0
        total = 0
        for mask in range(1 << n):
            s = 0.0
            for i in range(n):
                s += diffs[i] if (mask >> i) & 1 else -diffs[i]
            total += 1
            if abs(s / n) >= obs - 1e-12:
                count += 1
        return count / total
    hits = 0
    for _ in range(draws):
        s = sum(d if rng.random() < 0.5 else -d for d in diffs)
        if abs(s / n) >= obs - 1e-12:
            hits += 1
    return (hits + 1) / (draws + 1)


# ---------------------------------------------------------------------- load
def load(outdir: Path):
    eps = [json.loads(l) for l in (outdir / "episodes.jsonl").read_text().splitlines() if l.strip()]
    eps = [e for e in eps if e.get("metrics") is not None]
    mems = []
    mp = outdir / "members.jsonl"
    if mp.exists():
        mems = [json.loads(l) for l in mp.read_text().splitlines() if l.strip()]
    return eps, mems


def primary_table(eps):
    """arm -> seed -> variant -> score"""
    tab = collections.defaultdict(lambda: collections.defaultdict(dict))
    for e in eps:
        tab[e["arm"]][e["seed"]][e["variant"]] = e["metrics"]["msmi_per_100_arrived_members"]
    return tab


# ------------------------------------------------------------------- section 1
CEILINGS: dict = {}


def load_ceilings(outdir):
    cp = outdir / "ceilings.json"
    if cp.exists():
        for c in json.loads(cp.read_text()):
            CEILINGS[(c["seed"], c["variant"])] = c["ceiling"]


def complete_seeds(tab, arm, min_variants=6):
    """Only seeds where every scenario ran: the primary score needs all six."""
    return sorted(s for s, fam in tab[arm].items() if len(fam) >= min_variants)


def section_primary(eps, arms, outdir=None, show_per_seed=False):
    tab = primary_table(eps)
    print("=" * 88)
    print("1. PRIMARY SCORE  (unweighted mean of six family means; seed-block bootstrap)")
    print("   world-sharing: dev/delayed/shift/drift are the SAME 200 members per seed,")
    print("   so a seed is ~3 independent worlds, not 6. Seed is the only resampling unit.")
    print("=" * 88)
    ceil = CEILINGS
    print(f"{'arm':16s} {'n_seeds':>7s} {'MSMI/100':>9s} {'95% CI':>20s} {'events':>8s} {'cov':>7s} "
          f"{'cov/ceil':>9s} {'ask':>6s} {'unserved':>9s}")
    summary = {}
    for arm in arms:
        if arm not in tab:
            continue
        fam = tab[arm]
        seeds = complete_seeds(tab, arm)
        if not seeds:
            continue
        fam = {s: fam[s] for s in seeds}
        per_seed = {s: statistics.mean(fam[s][v] for v in fam[s]) for s in seeds}
        point = statistics.fmean(per_seed.values())
        lo, hi = seed_block_bootstrap(fam)
        ev = sum(e["metrics"]["mutual_second_meeting_intention"]
                 for e in eps if e["arm"] == arm and e["seed"] in set(seeds))
        cov = statistics.fmean(e["metrics"]["coverage"] for e in eps if e["arm"] == arm and e["seed"] in set(seeds))
        ask = statistics.fmean(e["metrics"]["ask_cost"] for e in eps if e["arm"] == arm and e["seed"] in set(seeds))
        uns = statistics.fmean(e["metrics"]["unserved_members"] for e in eps if e["arm"] == arm and e["seed"] in set(seeds))
        ratio = statistics.fmean([e["metrics"]["coverage"] / ceil[(e["seed"], e["variant"])]
                                 for e in eps if e["arm"] == arm and e["seed"] in set(seeds)
                                 and (e["seed"], e["variant"]) in ceil]) if ceil else float("nan")
        print(f"{arm:16s} {len(seeds):7d} {point:9.3f} {'[' + f'{lo:.3f}, {hi:.3f}' + ']':>20s} {ev:8d} {cov:7.3f} "
              f"{ratio:9.3f} {ask:6.0f} {uns:9.1f}")
        summary[arm] = {"primary": point, "lo": lo, "hi": hi, "events": ev, "coverage": cov,
                        "ask_cost": ask, "unserved": uns, "n_seeds": len(seeds), "cov_over_ceiling": ratio,
                        "per_seed": per_seed,
                        "family": {v: statistics.fmean(fam[s][v] for s in seeds) for v in VARIANTS
                                   if all(v in fam[s] for s in seeds)}}
        if show_per_seed:
            print(f"{'':16s}   per-seed: " + " ".join(f"{s}:{per_seed[s]:.2f}" for s in seeds))
            print(f"{'':16s}   family:   " + " ".join(
                f"{v[:4]}:{summary[arm]['family'][v]:.2f}" for v in summary[arm]["family"]))
    return tab, summary


# ------------------------------------------------------------------- section 2
def section_contrasts(eps, tab, arms, pairs):
    print()
    print("=" * 88)
    print("2. PAIRED CONTRASTS  (identical seed/variant worlds; seed-block bootstrap)")
    print(f"   {len(pairs)} contrasts reported; no multiplicity correction")
    print("=" * 88)
    print(f"{'contrast':34s} {'diff':>7s} {'95% CI':>20s} {'p':>7s} {'W/T/L':>14s}")
    out = []
    for a, b in pairs:
        if a not in tab or b not in tab:
            continue
        seeds = sorted(set(complete_seeds(tab, a)) & set(complete_seeds(tab, b)))
        if not seeds:
            continue
        per_seed = {}
        wtl = [0, 0, 0]
        for s in seeds:
            ds = [tab[a][s][v] - tab[b][s][v] for v in sorted(set(tab[a][s]) & set(tab[b][s]))]
            per_seed[s] = statistics.fmean(ds)
        for v in VARIANTS:
            for s in seeds:
                if v in tab[a][s] and v in tab[b][s]:
                    d = tab[a][s][v] - tab[b][s][v]
                    wtl[0 if d > 0 else (1 if d == 0 else 2)] += 1
        diffs = [per_seed[s] for s in seeds]
        point = statistics.fmean(diffs)
        lo, hi = seed_block_bootstrap({s: {0: per_seed[s]} for s in seeds})
        p = sign_flip_p(diffs)
        print(f"{a + ' - ' + b:34s} {point:+7.3f} {'[' + f'{lo:+.3f}, {hi:+.3f}' + ']':>20s} {p:7.3f} "
              f"{str(wtl[0]) + '/' + str(wtl[1]) + '/' + str(wtl[2]):>14s}")
        out.append({"a": a, "b": b, "diff": point, "lo": lo, "hi": hi, "p": p, "wtl": wtl})
    return out


# ------------------------------------------------------------------- section 3
def pct(xs, q):
    if not xs:
        return float("nan")
    xs = sorted(xs)
    i = min(len(xs) - 1, int(math.ceil(q * len(xs))) - 1)
    return float(xs[max(0, i)])


def section_waiting(eps, arms):
    print()
    print("=" * 88)
    print("3. WHO GETS LEFT WAITING  (waits are day-of-first-intro minus day-of-arrival,")
    print("   served members only, exactly as the official evaluator defines them)")
    print("=" * 88)
    print(f"{'arm':16s} {'mean':>7s} {'median':>7s} {'p90':>7s} {'max':>6s} {'unserved/200':>13s} {'never-asked':>12s} {'asked&unserved':>15s}")
    out = {}
    for arm in arms:
        sub = [e for e in eps if e["arm"] == arm]
        if not sub:
            continue
        waits = [w for e in sub for w in e["waits"]]
        unserved = statistics.fmean(e["metrics"]["unserved_members"] for e in sub)
        out[arm] = {
            "mean": statistics.fmean(waits), "median": pct(waits, 0.5), "p90": pct(waits, 0.9),
            "max": max(waits), "unserved": unserved, "n_waits": len(waits),
        }
        print(f"{arm:16s} {statistics.fmean(waits):7.2f} {pct(waits, .5):7.1f} {pct(waits, .9):7.1f} "
              f"{max(waits):6.0f} {unserved:13.1f} {'-':>12s} {'-':>15s}")
    return out


# ------------------------------------------------------------------- section 4
GROUPS = [("gender", "gender"), ("age band", "band"), ("zone", "zone"),
          ("has_children", "kids"), ("smoking", "smoke")]


def section_disparity(mems, arms, focus_variant=None):
    print()
    print("=" * 88)
    print("4. ALLOCATION DISPARITY DECOMPOSITION")
    print("   Leg 1 eligibility supply : P(complete-disclosure degree > 0) - a property of the WORLD")
    print("   Leg 2 ask allocation     : mean ask units per member who needed clarification")
    print("   Leg 3 realised access    : served rate + wait, among members WITH a feasible partner")
    print("   The outcome generator contains no demographic term; gender/age are negative controls.")
    print("=" * 88)
    rows = mems if focus_variant is None else [m for m in mems if m["variant"] == focus_variant]
    for arm in arms:
        sub = [m for m in rows if m["arm"] == arm]
        if not sub:
            continue
        print(f"\n--- arm: {arm}  (members: {len(sub)}) ---")
        for label, key in GROUPS:
            buckets = collections.defaultdict(list)
            for m in sub:
                buckets[m[key]].append(m)
            parts = []
            for g, ms in sorted(buckets.items(), key=lambda kv: str(kv[0])):
                if len(ms) < 150:
                    continue
                supply = sum(1 for m in ms if m["deg"] > 0) / len(ms)
                reachable = [m for m in ms if m["deg"] > 0]
                served = sum(1 for m in reachable if m["fid"] is not None) / max(1, len(reachable))
                waits = [m["wait"] for m in reachable if m["wait"] is not None]
                w = statistics.fmean(waits) if waits else float("nan")
                need = [m for m in ms if m["fad"] is not None or m["asks"] > 0]
                asku = statistics.fmean([m["asks"] for m in ms])
                parts.append(f"{g}: supply={supply:.2f} served|reach={served:.2f} wait={w:4.1f} ask={asku:4.1f} (n={len(ms)})")
            if parts:
                print(f"  {label:13s}")
                for p in parts:
                    print(f"      {p}")


# ------------------------------------------------------------------- section 5
def section_saturation(eps, arms):
    print()
    print("=" * 88)
    print("5. ASK-QUEUE SATURATION  (mean over episodes; is the daily cap binding?)")
    print("=" * 88)
    print(f"{'arm':16s} " + " ".join(f"d{d:<4d}" for d in (0, 5, 10, 15, 20, 30, 45, 59)))
    for arm in arms:
        sub = [e for e in eps if e["arm"] == arm]
        if not sub:
            continue
        ab = [statistics.fmean(e["askable_by_day"][d] for e in sub) for d in range(60)]
        ak = [statistics.fmean(e["asks_by_day"][d] for e in sub) for d in range(60)]
        print(f"{arm:16s} " + " ".join(f"{int(ab[d]):<5d}" for d in (0, 5, 10, 15, 20, 30, 45, 59)) + "   <- askable")
        print(f"{'':16s} " + " ".join(f"{ak[d]:<5.1f}" for d in (0, 5, 10, 15, 20, 30, 45, 59)) + "   <- asks/day (cap 4)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "out"))
    ap.add_argument("--arms", default="greedy,potential_ask,waitfloor,oldest_first")
    ap.add_argument("--skip-disparity", action="store_true")
    args = ap.parse_args()
    arms = [a for a in args.arms.split(",") if a.strip()]
    outdir = Path(args.out)
    eps, mems = load(outdir)
    print(f"loaded {len(eps)} episodes, {len(mems)} member rows\n")
    load_ceilings(outdir)
    tab, summary = section_primary(eps, arms, outdir)
    pairs = [(a, b) for i, a in enumerate(arms) for b in arms[i + 1:]]
    contrasts = section_contrasts(eps, tab, arms, pairs)
    waits = section_waiting(eps, arms)
    section_saturation(eps, arms)
    if not args.skip_disparity and mems:
        section_disparity(mems, arms, focus_variant="development")
    (outdir / "analysis.json").write_text(json.dumps({
        "summary": summary, "contrasts": contrasts, "waiting": waits,
    }, indent=2))


if __name__ == "__main__":
    main()
