"""Directional calibration instrumentation for Round 2 question 3.

Logs ONE ROW PER DIRECTION for every introduction the shipped greedy policy makes.
Directional = we record a->b and b->a separately, because they are separate draws
sharing only the pair-level `shared` term.

The email asks for "directional calibration ... even when the synthetic outcome
generator has no demographic effect", and to "test under changing conditions".
So we log, per direction:

  OBSERVABLE (what any policy could compute from the interface)
    n_known   how many of the four soft fields are known on both sides
    n_agree   how many of those known fields agree   <- the policy's actual score
    n_disagree how many of those known fields disagree

  OUTCOME
    responded, accept (yes / no / None for missing)

  ANALYSIS ONLY (never visible to any policy; used to bound what is learnable)
    true_fit, actor_bias, shared, drift, true_p

This lets us measure:
  1. reliability by score bin, with calibration slope, intercept, log loss, Brier
  2. calibration drift by day block and family  (shift / drift vs development)
  3. the Brier decomposition into calibration + refinement + irreducible
  4. the "unknown is not disagreement" defect, directly

Usage:
    python3 calibration.py --seeds 1101-1160 --workers 4 --out ~/calib
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import os
from pathlib import Path

import kit

SOFT = ["relationship_goal", "relationship_pace", "lifestyle", "conversations"]
WEIGHTS_DEV = {"relationship_goal": .7, "relationship_pace": .4,
               "lifestyle": .25, "conversations": .2}
WEIGHTS_SHIFT = {"relationship_goal": .25, "relationship_pace": .8,
                 "lifestyle": -.25, "conversations": .5}
VARIANTS = ("development", "sparse", "cold_start", "delayed", "shift", "drift")


def _weights(variant: str) -> dict:
    return WEIGHTS_SHIFT if variant == "shift" else WEIGHTS_DEV


def observable_score(a: dict, b: dict) -> tuple[int, int, int]:
    """Exactly what kit.baseline_match scores on: known agreements only.

    Agreement contributes 1, disagreement 0, unknown 0. The generator instead
    uses +w for agreement and -0.5w for disagreement, so disagreement and
    unknown are NOT the same thing. That gap is the calibration finding.
    """
    known = agree = disagree = 0
    for k in SOFT:
        va, vb = a["fields"].get(k), b["fields"].get(k)
        if va is None or vb is None:
            continue
        known += 1
        if va == vb:
            agree += 1
        else:
            disagree += 1
    return known, agree, disagree


def run_episode(seed: int, variant: str) -> list[dict]:
    """One episode with the SHIPPED greedy policy, logging per-direction rows."""
    sim = kit.Simulator(kit.generate(seed, 200, "evaluation", variant))
    mem = sim.members                      # analysis-only handle on latent truth
    w = _weights(variant)
    rows: list[dict] = []
    seen = 0                               # introductions already accounted for

    for _ in range(60):
        st = sim.observe()
        sim.resolve_asks(kit.baseline_asks(st))
        pairs = kit.baseline_match(sim.observe())
        day = sim.day
        sim.advance(pairs)

        # Every introduction created on this day, with its two directions.
        for intro in sim.introductions[seen:]:
            a_id, b_id = intro["user_a"], intro["user_b"]
            ma, mb = mem[a_id], mem[b_id]
            known, agree, disagree = observable_score(ma, mb)

            # Recover the exact pair-level shared draw is impossible after the
            # fact, so recompute the deterministic parts and leave shared as the
            # residual we bound analytically instead of logging a fake value.
            fit_a = sum(wv * (1 if ma["truth"][k] == mb["truth"][k] else -.5)
                        for k, wv in w.items())
            fit_b = fit_a                  # fit is symmetric in the generator
            drift = -.5 if (variant == "drift" and intro["assigned_day"] >= 35) else 0.0

            # Pull the two directional outcomes out of the event stream.
            ev = [e for e in sim.events
                  if e.get("introduction_id") == intro["introduction_id"]
                  and e["event"] == "introduction_response"]
            by_member = {e["member_id"]: e for e in ev}

            for actor_id, other_id in ((a_id, b_id), (b_id, a_id)):
                e = by_member.get(actor_id)
                responded = bool(e and e["value"] is not None)
                accept = None
                if responded:
                    accept = 1 if e["value"] == "yes" else 0
                rows.append({
                    "seed": seed, "variant": variant, "day": intro["assigned_day"],
                    "actor": actor_id, "other": other_id,
                    "n_known": known, "n_agree": agree, "n_disagree": disagree,
                    "responded": responded, "accept": accept,
                    "actor_bias": mem[actor_id]["bias"],        # analysis only
                    "true_fit": fit_a,                          # analysis only
                    "drift": drift,                             # analysis only
                    # gender / age / zone are TOP-LEVEL member attributes, not
                    # entries in `truth`. The generator puts no demographic term
                    # in the acceptance probability, so these are negative
                    # controls: any spread here would be a finding.
                    "actor_gender": mem[actor_id].get("gender"),
                    "actor_age": mem[actor_id].get("age"),
                    "actor_zone": mem[actor_id].get("zone"),
                })
        seen = len(sim.introductions)

    for _ in range(40):
        sim.advance([])
    return rows


def _job(args) -> list[dict]:
    seed, variant = args
    try:
        return run_episode(seed, variant)
    except Exception as exc:                                   # noqa: BLE001
        print(f"  FAILED seed={seed} variant={variant}: {exc!r}", flush=True)
        return []


def parse_seeds(spec: str) -> list[int]:
    if "-" in spec:
        lo, hi = spec.split("-", 1)
        return list(range(int(lo), int(hi) + 1))
    return [int(s) for s in spec.split(",") if s.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="1101-1160")
    ap.add_argument("--variants", default=",".join(VARIANTS))
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="calib_out")
    a = ap.parse_args()

    seeds = parse_seeds(a.seeds)
    variants = [v for v in a.variants.split(",") if v.strip()]
    jobs = [(s, v) for s in seeds for v in variants]

    outdir = Path(a.out)
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / "directions.jsonl"

    print(f"  {len(seeds)} seeds x {len(variants)} variants = {len(jobs)} episodes")
    print(f"  workers: {a.workers}   -> {out}", flush=True)

    n = 0
    with out.open("w") as fh, mp.Pool(a.workers) as pool:
        for i, rows in enumerate(pool.imap_unordered(_job, jobs), 1):
            for r in rows:
                fh.write(json.dumps(r) + "\n")
            n += len(rows)
            if i % 20 == 0:
                print(f"    {i}/{len(jobs)} episodes, {n} direction rows", flush=True)

    print(f"  done: {n} direction rows -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
