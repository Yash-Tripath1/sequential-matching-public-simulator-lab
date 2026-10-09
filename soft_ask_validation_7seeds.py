"""Held-out public-seed follow-up for hard-plus-soft + max-weight.

Runs only seven new public seeds × six scenario families (42 episodes) for the
selected hard-plus-soft max-weight policy. It reuses the 3-seed soft-ask pilot
and the 10-seed hard-only max-weight controls. The 7-seed follow-up is the
least selection-biased comparison; the combined 10-seed result is descriptive.
"""
from __future__ import annotations
import argparse
import csv
import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from statistics import mean

for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import numpy as np  # noqa: E402
import experiment_lab as lab  # noqa: E402

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FACTORIAL_JSON = RESULTS / "scaled_factorial_10seeds.json"
PILOT_JSON = RESULTS / "soft_ask_screen_3seeds.json"
OUT_JSON = RESULTS / "soft_ask_validation_7seeds.json"
OUT_CSV = RESULTS / "soft_ask_validation_7seeds_summary.csv"
METHOD = "hard_plus_soft_maxweight"
CONTROL = "potential_ask"
SEEDS = [404, 505, 606, 707, 808, 909, 1010]
ALL_SEEDS = [101, 202, 303] + SEEDS
PILOT_SEEDS = [101, 202, 303]
VARIANTS = ["development", "sparse", "cold_start", "delayed", "shift", "drift"]
N_BOOT = 10000
BOOT_SEED = 20261010


def _key(row: dict) -> tuple[int, str]:
    return int(row["seed"]), row["variant"]


def _task_key(row: dict) -> tuple[str, int, str]:
    return row["method"], int(row["seed"]), row["variant"]


def _run_one(task: tuple[str, int, str]) -> dict:
    method, seed, variant = task
    row = lab.run_episode(method, seed, variant)
    if not row.get("valid"):
        raise RuntimeError(f"invalid episode: {method}/{seed}/{variant}: {row}")
    return row


def _atomic_json(path: Path, payload: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    tmp.replace(path)


def _load_new_rows() -> dict[tuple[str, int, str], dict]:
    if not OUT_JSON.exists():
        return {}
    try:
        payload = json.loads(OUT_JSON.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    if payload.get("runner") != "soft_ask_maxweight_holdout_v1":
        return {}
    rows = {}
    for row in payload.get("new_rows", []):
        if row.get("method") == METHOD and row.get("seed") in SEEDS and row.get("variant") in VARIANTS and row.get("valid"):
            rows[_task_key(row)] = row
    return rows


def _load_pilot_rows() -> list[dict]:
    if not PILOT_JSON.exists():
        raise FileNotFoundError(f"Need the completed 3-seed soft screen at {PILOT_JSON}")
    payload = json.loads(PILOT_JSON.read_text())
    rows = payload.get("new_rows", [])
    if not rows:
        rows = [r for r in payload.get("combined_rows", []) if r.get("method") == METHOD]
    pilot = [r for r in rows if r.get("method") == METHOD and r.get("seed") in PILOT_SEEDS]
    for seed in PILOT_SEEDS:
        for variant in VARIANTS:
            if sum(r["seed"] == seed and r["variant"] == variant for r in pilot) != 1:
                raise ValueError(f"Missing or duplicate 3-seed pilot row for {METHOD}/{seed}/{variant}")
    return pilot


def _load_controls() -> list[dict]:
    if not FACTORIAL_JSON.exists():
        raise FileNotFoundError(f"Need the completed 10-seed controls at {FACTORIAL_JSON}")
    rows = json.loads(FACTORIAL_JSON.read_text())["rows"]
    controls = [r for r in rows if r.get("method") == CONTROL and r.get("seed") in ALL_SEEDS]
    for seed in ALL_SEEDS:
        for variant in VARIANTS:
            if sum(r["seed"] == seed and r["variant"] == variant for r in controls) != 1:
                raise ValueError(f"Missing or duplicate hard-only control row for {CONTROL}/{seed}/{variant}")
    return controls


def _bootstrap_ci(values: list[float], rng: np.random.Generator) -> list[float]:
    x = np.asarray(values, dtype=float)
    draws = rng.choice(x, size=(N_BOOT, len(x)), replace=True).mean(axis=1)
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return [float(lo), float(hi)]


def _sign_flip_p(values: list[float]) -> float:
    x = np.asarray(values, dtype=float)
    observed = abs(float(x.mean()))
    if observed == 0:
        return 1.0
    extreme = 0
    for mask in range(1 << len(x)):
        signs = np.fromiter((1.0 if (mask >> i) & 1 else -1.0 for i in range(len(x))), dtype=float, count=len(x))
        if abs(float((x * signs).mean())) >= observed - 1e-12:
            extreme += 1
    return extreme / (1 << len(x))


def _method_summary(rows: list[dict], seeds: list[int], rng: np.random.Generator) -> dict:
    by_seed = {
        seed: mean(next(r["msmi_per_100_arrived_members"] for r in rows if r["seed"] == seed and r["variant"] == v)
                   for v in VARIANTS)
        for seed in seeds
    }
    by_variant = {
        v: mean(r["msmi_per_100_arrived_members"] for r in rows if r["variant"] == v)
        for v in VARIANTS
    }
    hard_bundles = []
    for r in rows:
        if "hard_constraint_bundles" in r:
            hard_bundles.append(r["hard_constraint_bundles"])
        elif r["method"] == CONTROL:
            # Existing 10-seed controls predate the explicit ask-count field;
            # they ask constraints only, each bundle costing exactly three units.
            hard_bundles.append(r["ask_cost"] / 3)
        else:
            hard_bundles.append(0)
    return {
        "episodes": len(rows),
        "seeds": seeds,
        "primary_equal_family_mean_msmi_per_100": mean(by_variant.values()),
        "primary_seed_block_ci95": _bootstrap_ci(list(by_seed.values()), rng),
        "seed_block_primary_scores": {str(k): v for k, v in by_seed.items()},
        "scenario_msmi_per_100": by_variant,
        "msmi_events": sum(int(r["mutual_second_meeting_intention"]) for r in rows),
        "ask_units_mean": mean(r["ask_cost"] for r in rows),
        "hard_constraint_bundles_mean": mean(hard_bundles),
        "soft_field_questions_mean": mean(r.get("soft_field_questions", 0) for r in rows),
        "coverage_mean": mean(r["coverage"] for r in rows),
        "assignments_mean": mean(r["assignments"] for r in rows),
    }


def _contrast(a_rows: list[dict], b_rows: list[dict], seeds: list[int], rng: np.random.Generator,
              include_sign_flip: bool) -> dict:
    a = {_key(r): r["msmi_per_100_arrived_members"] for r in a_rows}
    b = {_key(r): r["msmi_per_100_arrived_members"] for r in b_rows}
    diffs = {(s, v): a[(s, v)] - b[(s, v)] for s in seeds for v in VARIANTS}
    seed_blocks = {s: mean(diffs[(s, v)] for v in VARIANTS) for s in seeds}
    episode_diffs = list(diffs.values())
    per_variant = {}
    for v in VARIANTS:
        values = [diffs[(s, v)] for s in seeds]
        per_variant[v] = {
            "mean_difference": mean(values),
            "wins_ties_losses": [sum(x > 0 for x in values), sum(x == 0 for x in values), sum(x < 0 for x in values)],
        }
    result = {
        "n_seed_blocks": len(seeds),
        "n_paired_episodes": len(episode_diffs),
        "mean_equal_family_difference": mean(seed_blocks.values()),
        "seed_block_bootstrap_ci95": _bootstrap_ci(list(seed_blocks.values()), rng),
        "seed_block_differences": {str(k): v for k, v in seed_blocks.items()},
        "wins_ties_losses": [sum(x > 0 for x in episode_diffs), sum(x == 0 for x in episode_diffs), sum(x < 0 for x in episode_diffs)],
        "per_variant": per_variant,
    }
    if include_sign_flip:
        result["exact_two_sided_sign_flip_p"] = _sign_flip_p(list(seed_blocks.values()))
        result["note"] = "Exploratory 7-seed public holdout; unadjusted exact sign-flip test, not private evaluation."
    else:
        result["note"] = "Descriptive 10-seed aggregate includes the 3-seed pilot used to select this arm; do not treat its interval/test as selection-free."
    return result


def _write_csv(rows: list[dict]) -> None:
    fields = ["group", "method", "episodes", "primary_equal_family_mean_msmi_per_100",
              "ci95_low", "ci95_high", "msmi_events", "ask_units_mean",
              "hard_constraint_bundles_mean", "soft_field_questions_mean",
              "coverage_mean", "assignments_mean"]
    with OUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fields})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be at least 1")
    RESULTS.mkdir(parents=True, exist_ok=True)
    controls_all = _load_controls()
    pilot_soft = _load_pilot_rows()
    tasks = [(METHOD, seed, variant) for seed in SEEDS for variant in VARIANTS]
    done = _load_new_rows()
    pending = [task for task in tasks if task not in done]

    def checkpoint(complete: bool = False) -> None:
        new_rows = [done[t] for t in tasks if t in done]
        _atomic_json(OUT_JSON, {
            "runner": "soft_ask_maxweight_holdout_v1",
            "method": METHOD,
            "control_method": CONTROL,
            "pilot_seeds": PILOT_SEEDS,
            "heldout_seeds": SEEDS,
            "variants": VARIANTS,
            "target_new_episodes": len(tasks),
            "completed_new_episodes": len(new_rows),
            "complete": complete,
            "note": "Public synthetic only. The held-out 7 seeds were not used to select this arm; pilot and 10-seed aggregate are also reported separately.",
            "new_rows": new_rows,
        })

    print(f"Checkpoint status: {len(done)}/{len(tasks)} new episodes complete; {len(pending)} remain. Workers={args.workers}.", flush=True)
    if pending:
        if args.workers == 1:
            for task in pending:
                row = _run_one(task)
                done[task] = row
                checkpoint(False)
                print(f"{len(done)}/{len(tasks)} {task[0]}/{task[2]}/{task[1]} valid={row['valid']}", flush=True)
        else:
            with ProcessPoolExecutor(max_workers=args.workers) as executor:
                futures = {executor.submit(_run_one, task): task for task in pending}
                for future in as_completed(futures):
                    task = futures[future]
                    row = future.result()
                    done[task] = row
                    checkpoint(False)
                    print(f"{len(done)}/{len(tasks)} {task[0]}/{task[2]}/{task[1]} valid={row['valid']}", flush=True)

    checkpoint(True)
    heldout_soft = [done[t] for t in tasks]
    controls_heldout = [r for r in controls_all if r["seed"] in SEEDS]
    soft_all10 = pilot_soft + heldout_soft
    rng = np.random.default_rng(BOOT_SEED)

    holdout_contrast = _contrast(heldout_soft, controls_heldout, SEEDS, rng, include_sign_flip=True)
    all10_contrast = _contrast(soft_all10, controls_all, ALL_SEEDS, rng, include_sign_flip=False)
    summary_rows = []
    for group, method, rows, seeds in [
        ("holdout_7", METHOD, heldout_soft, SEEDS),
        ("holdout_7", CONTROL, controls_heldout, SEEDS),
        ("all_10_descriptive", METHOD, soft_all10, ALL_SEEDS),
        ("all_10_descriptive", CONTROL, controls_all, ALL_SEEDS),
    ]:
        sm = _method_summary(rows, seeds, rng)
        summary_rows.append({
            "group": group, "method": method, "episodes": sm["episodes"],
            "primary_equal_family_mean_msmi_per_100": sm["primary_equal_family_mean_msmi_per_100"],
            "ci95_low": sm["primary_seed_block_ci95"][0], "ci95_high": sm["primary_seed_block_ci95"][1],
            "msmi_events": sm["msmi_events"], "ask_units_mean": sm["ask_units_mean"],
            "hard_constraint_bundles_mean": sm["hard_constraint_bundles_mean"],
            "soft_field_questions_mean": sm["soft_field_questions_mean"],
            "coverage_mean": sm["coverage_mean"], "assignments_mean": sm["assignments_mean"],
            "details": sm,
        })

    payload = json.loads(OUT_JSON.read_text())
    payload["heldout_validation"] = {
        "soft_plus_hard_maxweight": _method_summary(heldout_soft, SEEDS, rng),
        "hard_only_maxweight_control": _method_summary(controls_heldout, SEEDS, rng),
        "paired_contrast": holdout_contrast,
    }
    payload["all_10_seed_descriptive"] = {
        "soft_plus_hard_maxweight": _method_summary(soft_all10, ALL_SEEDS, rng),
        "hard_only_maxweight_control": _method_summary(controls_all, ALL_SEEDS, rng),
        "paired_contrast": all10_contrast,
    }
    payload["analysis_seed"] = BOOT_SEED
    payload["n_bootstrap"] = N_BOOT
    payload["summary_rows"] = summary_rows
    _atomic_json(OUT_JSON, payload)
    _write_csv(summary_rows)
    print("Wrote", OUT_JSON)
    print("Wrote", OUT_CSV)
    print(json.dumps({"heldout_validation": payload["heldout_validation"],
                      "all_10_seed_descriptive": payload["all_10_seed_descriptive"]}, indent=2))


if __name__ == "__main__":
    main()
