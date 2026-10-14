"""Directional calibration analysis. Consumes calibration.py output.

Answers Round 2 question 3 ("directional calibration and allocation disparities,
even when the synthetic outcome generator has no demographic effect") and the
"test under changing conditions" requirement.

    python3 calibration_analysis.py --input ~/calib/directions.jsonl

Produces calibration_report.json plus a printed summary.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

VARIANTS = ("development", "sparse", "cold_start", "delayed", "shift", "drift")
DAY_BLOCKS = ((0, 19, "d00-19"), (20, 34, "d20-34"), (35, 59, "d35-59"))


# ---------------------------------------------------------------- utilities
def sigmoid(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-z))


def logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def seed_block_bootstrap(rows, stat_fn, draws=2000, rng_seed=20261015):
    """Seed is the resampling unit: scenarios within a seed share one world."""
    import random
    rng = random.Random(rng_seed)
    by_seed = defaultdict(list)
    for r in rows:
        by_seed[r["seed"]].append(r)
    seeds = sorted(by_seed)
    flat = {s: by_seed[s] for s in seeds}
    point = stat_fn(rows)
    vals = []
    for _ in range(draws):
        pick = [flat[s] for s in (rng.choice(seeds) for _ in seeds)]
        sample = [r for grp in pick for r in grp]
        try:
            vals.append(stat_fn(sample))
        except Exception:                                    # noqa: BLE001
            pass
    vals.sort()
    lo = vals[int(.025 * len(vals))] if vals else point
    hi = vals[int(.975 * len(vals))] if vals else point
    return point, lo, hi


def brier(rows, key="p_hat"):
    if not rows:
        return float("nan")
    return statistics.fmean((r[key] - r["accept"]) ** 2 for r in rows)


def logloss(rows, key="p_hat"):
    if not rows:
        return float("nan")
    out = []
    for r in rows:
        p = min(max(r[key], 1e-6), 1 - 1e-6)
        out.append(-(r["accept"] * math.log(p) + (1 - r["accept"]) * math.log(1 - p)))
    return statistics.fmean(out)


def fit_calibration_slope(rows, key="p_hat"):
    """Logistic regression of outcome on logit(p_hat).

    slope 1 = perfectly calibrated. slope < 1 = predictions too extreme.
    Intercept != 0 = systematic bias in the base rate.
    """
    if len(rows) < 30:
        return float("nan"), float("nan"), 0
    # Newton-free: one-parameter grid search on slope, closed form for intercept.
    xs = [logit(r[key]) for r in rows]
    ys = [r["accept"] for r in rows]
    best = (float("nan"), float("nan"), float("inf"))
    for slope in [i / 100 for i in range(0, 301, 5)]:
        for inter in [i / 20 for i in range(-40, 41, 2)]:
            ll = 0.0
            for x, y in zip(xs, ys):
                z = inter + slope * x
                p = sigmoid(z)
                p = min(max(p, 1e-9), 1 - 1e-9)
                ll -= y * math.log(p) + (1 - y) * math.log(1 - p)
            if ll < best[2]:
                best = (slope, inter, ll)
    return best[0], best[1], len(rows)


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="directions.jsonl")
    ap.add_argument("--out", default="calibration_report.json")
    a = ap.parse_args()

    rows = [json.loads(l) for l in open(a.input)]
    # Calibration is measured on directions that produced an answer.
    resp = [r for r in rows if r["responded"] and r["accept"] is not None]
    miss = len(rows) - len(resp)
    print(f"  {len(rows)} direction rows; {len(resp)} answered; "
          f"{miss} missing ({miss/max(1,len(rows)):.1%})")

    report: dict = {"n_directions": len(rows), "n_answered": len(resp),
                    "n_missing": miss,
                    "missing_rate": miss / max(1, len(rows))}

    # ---- 1. the policy's implicit probability -----------------------------
    # Map the observable score to a probability by fitting on development only,
    # then apply that SAME mapping everywhere. Staleness under shift/drift is
    # precisely the point.
    dev = [r for r in resp if r["variant"] == "development"]
    base = statistics.fmean(r["accept"] for r in dev)
    by_score = defaultdict(list)
    for r in dev:
        by_score[r["n_agree"]].append(r["accept"])
    score_p = {k: statistics.fmean(v) for k, v in by_score.items()}
    default_p = base
    print(f"\n  reference mapping fitted on development (base rate {base:.4f}):")
    for k in sorted(score_p):
        print(f"     n_agree={k}: p={score_p[k]:.3f}  (n={len(by_score[k])})")

    for r in resp:
        r["p_hat"] = score_p.get(r["n_agree"], default_p)

    # ---- 2. overall calibration -------------------------------------------
    print("\n=== 1. OVERALL CALIBRATION (reference mapping applied everywhere) ===")
    print(f"  {'variant':14s} {'n':>6s} {'empirical':>10s} {'mean p_hat':>11s} "
          f"{'Brier':>8s} {'logloss':>8s} {'slope':>6s} {'intercept':>10s}")
    overall = {}
    for v in VARIANTS:
        g = [r for r in resp if r["variant"] == v]
        if len(g) < 50:
            continue
        emp = statistics.fmean(r["accept"] for r in g)
        mph = statistics.fmean(r["p_hat"] for r in g)
        br = brier(g)
        ll = logloss(g)
        sl, ic, n = fit_calibration_slope(g)
        overall[v] = {"n": len(g), "empirical": emp, "mean_p_hat": mph, "brier": br,
                      "logloss": ll, "slope": sl, "intercept": ic}
        print(f"  {v:14s} {len(g):6d} {emp:10.4f} {mph:11.4f} {br:8.4f} "
              f"{ll:8.4f} {sl:6.2f} {ic:10.2f}")
    report["overall_by_variant"] = overall

    # ---- 3. calibration under changing conditions -------------------------
    print("\n=== 2. CALIBRATION UNDER CHANGE (day blocks; drift applies -0.5 at day 35) ===")
    print(f"  {'variant':14s} {'block':8s} {'n':>6s} {'empirical':>10s} {'mean p_hat':>11s} {'gap':>8s}")
    blocks = {}
    for v in VARIANTS:
        for lo, hi, lab in DAY_BLOCKS:
            g = [r for r in resp if r["variant"] == v and lo <= r["day"] <= hi]
            if len(g) < 30:
                continue
            emp = statistics.fmean(r["accept"] for r in g)
            mph = statistics.fmean(r["p_hat"] for r in g)
            blocks[f"{v}|{lab}"] = {"n": len(g), "empirical": emp,
                                    "mean_p_hat": mph, "gap": emp - mph}
            print(f"  {v:14s} {lab:8s} {len(g):6d} {emp:10.4f} {mph:11.4f} {emp-mph:+8.4f}")
    report["day_blocks"] = blocks

    # ---- 4. reliability table ---------------------------------------------
    print("\n=== 3. RELIABILITY BY SCORE BIN (all variants pooled) ===")
    print(f"  {'n_agree':>8s} {'n':>6s} {'empirical':>10s} {'95% CI':>22s}")
    rel = {}
    for k in sorted(set(r["n_agree"] for r in resp)):
        g = [r for r in resp if r["n_agree"] == k]
        if len(g) < 30:
            continue
        pt, lo, hi = seed_block_bootstrap(g, lambda s: statistics.fmean(r["accept"] for r in s))
        rel[k] = {"n": len(g), "empirical": pt, "lo": lo, "hi": hi}
        print(f"  {k:8d} {len(g):6d} {pt:10.4f} {'['+f'{lo:.3f}, {hi:.3f}'+']':>22s}")
    report["reliability_by_score"] = rel

    # ---- 5. "unknown is not disagreement" ---------------------------------
    print("\n=== 4. UNKNOWN vs DISAGREEMENT (generator uses -0.5w for disagreement) ===")
    print("  Holding n_agree fixed, vary n_disagree. Flat => policy score is fine.")
    print(f"  {'variant':14s} {'agree':>6s} {'disag':>6s} {'n':>6s} {'empirical':>10s}")
    unk = {}
    for v in ("development", "shift"):
        for agree in sorted(set(r["n_agree"] for r in resp if r["variant"] == v)):
            for dis in sorted(set(r["n_disagree"] for r in resp
                                   if r["variant"] == v and r["n_agree"] == agree)):
                g = [r for r in resp if r["variant"] == v
                     and r["n_agree"] == agree and r["n_disagree"] == dis]
                if len(g) < 30:
                    continue
                emp = statistics.fmean(r["accept"] for r in g)
                unk[f"{v}|a{agree}|d{dis}"] = {"n": len(g), "empirical": emp}
                print(f"  {v:14s} {agree:6d} {dis:6d} {len(g):6d} {emp:10.4f}")
    report["unknown_vs_disagreement"] = unk

    # ---- 6. Brier decomposition -------------------------------------------
    print("\n=== 5. BRIER DECOMPOSITION (calibration + refinement + irreducible) ===")
    print("  Irreducible uses the ANALYSIS-ONLY latent terms: a lower bound on")
    print("  any model's error, since bias and shared are unobservable.")
    decomp = {}
    for v in VARIANTS:
        g = [r for r in resp if r["variant"] == v]
        if len(g) < 50:
            continue
        # calibration + refinement, binned on p_hat
        bins = defaultdict(list)
        for r in g:
            bins[round(r["p_hat"], 3)].append(r)
        cal = ref = 0.0
        n = len(g)
        for _, grp in bins.items():
            f = statistics.fmean(r["p_hat"] for r in grp)
            o = statistics.fmean(r["accept"] for r in grp)
            cal += len(grp) * (f - o) ** 2
            ref += len(grp) * o * (1 - o)
        cal /= n
        ref /= n
        total = brier(g)
        # Irreducible floor: how wrong a prediction is FORCED to be when it
        # knows fit and drift exactly but cannot see bias ~ N(0,0.7) or
        # shared ~ N(0,0.45). Monte Carlo over both latent terms.
        # Analysis-only by construction: no policy observes these.
        import random
        _rng = random.Random(20261015)
        _N = 64
        _b = [_rng.gauss(0, .7) for _ in range(_N)]
        _s = [_rng.gauss(0, .45) for _ in range(_N)]
        acc = []
        for r in g:
            base = -.25 + r["true_fit"] + r["drift"]
            phat = sigmoid(base)                       # best possible prediction
            acc.append(statistics.fmean(
                (sigmoid(base + bi + si) - phat) ** 2 for bi in _b for si in _s))
        irred = statistics.fmean(acc)
        decomp[v] = {"brier": total, "calibration": cal, "refinement": ref,
                     "irreducible_lower_bound": irred}
        print(f"  {v:14s} Brier {total:.4f} = cal {cal:.4f} + ref {ref:.4f} "
              f"| irreducible >= {irred:.4f}")
    report["brier_decomposition"] = decomp

    # ---- 7. no demographic effect -----------------------------------------
    print("\n=== 6. DIRECTIONAL CALIBRATION BY GROUP (generator has no demographic term) ===")
    print("  Flat across groups is the expected, and reassuring, result.")
    groups = {}
    for attr in ("actor_gender", "actor_age", "actor_zone"):
        vals = sorted({r[attr] for r in resp if r.get(attr) is not None}, key=str)
        per = {}
        for val in vals:
            g = [r for r in resp if r.get(attr) == val]
            if len(g) < 50:
                continue
            per[str(val)] = {"n": len(g),
                             "empirical": statistics.fmean(r["accept"] for r in g)}
        if per:
            groups[attr] = per
            rs = [v["empirical"] for v in per.values()]
            print(f"  {attr:14s} n_levels={len(per)}  range "
                  f"{min(rs):.3f}-{max(rs):.3f}  spread {max(rs)-min(rs):.3f}")
    report["by_group"] = groups

    Path(a.out).write_text(json.dumps(report, indent=2))
    print(f"\n  wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
