"""Does restricting the matcher to the four fields that actually matter help?

baseline_match scores an UNWEIGHTED count over all 7 SOFT fields, but the
generator's acceptance probability uses only 4, with unequal weights:

    relationship_goal .7 | relationship_pace .4 | lifestyle .25 | conversations .2

So three fields contribute pure noise to the ranking, and the four that matter
are treated as equally important when they are not (7:1 ratio at the extremes).

Three matchers compared, all with the SAME supplied ask rule (baseline_asks):

    greedy7     - supplied baseline: unweighted count over 7 fields
    core4       - unweighted count over the 4 that matter
    core4w      - weighted sum over the 4, using the generator's weights

The third is an oracle-ish upper bound on how much the weighting alone can buy,
because in `shift` the true weights change (.25/.8/-.25/.5) and we do not adapt.
"""

from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import statistics
from collections import defaultdict

import kit

# The four soft fields that enter the acceptance probability, with the
# development weights. `shift` uses different weights, which is exactly the
# "changing conditions" stress this will fail under if we do not adapt.
CORE = {"relationship_goal": .7, "relationship_pace": .4,
        "lifestyle": .25, "conversations": .2}
VARIANTS = ("development", "sparse", "cold_start", "delayed", "shift", "drift")


def score_core4(a: dict, b: dict) -> float:
    return sum(1 for k in CORE
               if a["fields"].get(k) is not None
               and a["fields"].get(k) == b["fields"].get(k))


def score_core4w(a: dict, b: dict) -> float:
    return sum(w for k, w in CORE.items()
               if a["fields"].get(k) is not None
               and a["fields"].get(k) == b["fields"].get(k))


def match_by(state, scorer):
    members = [m for m in state["members"] if m["available"]]
    past = {tuple(sorted((i["user_a"], i["user_b"])))
            for i in state["introductions"]}
    edges = []
    for a, b in itertools.combinations(members, 2):
        key = tuple(sorted((a["member_id"], b["member_id"])))
        if key in past or kit.eligibility(a, b)["status"] != "feasible":
            continue
        edges.append((-scorer(a, b), key))
    used, out = set(), []
    for _, pair in sorted(edges):
        if not used.intersection(pair):
            out.append(list(pair))
            used.update(pair)
    return out


def run(seed: int, variant: str) -> dict:
    res = {}
    for name, scorer in (("greedy7", None), ("core4", score_core4),
                         ("core4w", score_core4w)):
        sim = kit.Simulator(kit.generate(seed, 200, "evaluation", variant))
        for _ in range(60):
            st = sim.observe()
            sim.resolve_asks(kit.baseline_asks(st))
            pairs = (kit.baseline_match(sim.observe()) if scorer is None
                     else match_by(sim.observe(), scorer))
            sim.advance(pairs)
        for _ in range(40):
            sim.advance([])
        m = sim.metrics()
        arrived = sum(1 for x in sim.observe()["members"] if x["arrived_day"] <= 59)
        res[name] = 100 * m["mutual_second_meeting_intention"] / max(1, arrived)
    return {"seed": seed, "variant": variant, **res}


def job(a):
    try:
        return run(*a)
    except Exception as e:                                    # noqa: BLE001
        return {"error": repr(e)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--start", type=int, default=1101)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()

    seeds = list(range(a.start, a.start + a.seeds))
    jobs = [(s, v) for s in seeds for v in VARIANTS]
    print(f"  {len(seeds)} seeds x 6 families x 3 matchers = {len(jobs)} episodes")

    rows = []
    with mp.Pool(a.workers) as pool:
        for i, r in enumerate(pool.imap_unordered(job, jobs), 1):
            if "error" not in r:
                rows.append(r)
            if i % 30 == 0:
                print(f"    {i}/{len(jobs)}", flush=True)

    print(f"\n  {len(rows)} valid episodes\n")
    print(f"  {'matcher':10s} {'MSMI/100':>9s} {'vs greedy7':>12s}")
    base = defaultdict(list)
    for r in rows:
        for k in ("greedy7", "core4", "core4w"):
            base[k].append(r[k])
    prim = {k: statistics.fmean(v) for k, v in base.items()}
    for k in ("greedy7", "core4", "core4w"):
        d = prim[k] - prim["greedy7"]
        print(f"  {k:10s} {prim[k]:9.4f} {d:+12.4f}")

    # paired per-seed
    print("\n  paired by seed (seed = mean of six families):")
    per = {k: {} for k in ("greedy7", "core4", "core4w")}
    for k in per:
        by = defaultdict(dict)
        for r in rows:
            by[r["seed"]][r["variant"]] = r[k]
        per[k] = {s: statistics.fmean(f.values()) for s, f in by.items()
                  if len(f) == 6}
    sd = sorted(per["greedy7"])
    for k in ("core4", "core4w"):
        diffs = [per[k][s] - per["greedy7"][s] for s in sd]
        n = len(diffs)
        w = sum(1 for d in diffs if d > 1e-9)
        l = sum(1 for d in diffs if d < -1e-9)
        print(f"    {k:8s} mean {statistics.fmean(diffs):+.4f}  "
              f"sd {statistics.stdev(diffs):.3f}  "
              f"se {statistics.stdev(diffs)/n**.5:.4f}  W/T/L {w}/{n-w-l}/{l}")

    print("\n  by family (is the gain concentrated where weights are stable?):")
    print(f"    {'family':14s} {'greedy7':>9s} {'core4':>9s} {'core4w':>9s}")
    for v in VARIANTS:
        r = {k: statistics.fmean(x[k] for x in rows if x["variant"] == v)
             for k in ("greedy7", "core4", "core4w")}
        print(f"    {v:14s} {r['greedy7']:9.4f} {r['core4']:9.4f} {r['core4w']:9.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
