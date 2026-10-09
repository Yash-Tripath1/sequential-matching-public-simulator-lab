"""Resumable, process-parallel 3-seed screen for targeted core-soft asks.

Reuses existing 3-seed hard-only controls and runs only four new ask/matcher
cells (soft-only and hard-plus-soft × greedy and max-weight). This is a public,
exploratory screen, not private/Docker evaluation. No hidden truth is read.
"""
from __future__ import annotations
import argparse
import csv
import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from statistics import mean

# Avoid BLAS/OpenMP oversubscription when multiple rollout processes are used.
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import experiment_lab as lab  # noqa: E402

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
PILOT_JSON = RESULTS / "public_pilot_results.json"
OUT_JSON = RESULTS / "soft_ask_screen_3seeds.json"
OUT_CSV = RESULTS / "soft_ask_screen_3seeds_summary.csv"
SEEDS = [101, 202, 303]
VARIANTS = ["development", "sparse", "cold_start", "delayed", "shift", "drift"]
NEW_METHODS = [
    "soft_core_greedy",
    "soft_core_maxweight",
    "hard_plus_soft_greedy",
    "hard_plus_soft_maxweight",
]
HARD_CONTROLS = ["potential_ask_greedy", "potential_ask"]
CONTROL_FOR = {
    "soft_core_greedy": "potential_ask_greedy",
    "hard_plus_soft_greedy": "potential_ask_greedy",
    "soft_core_maxweight": "potential_ask",
    "hard_plus_soft_maxweight": "potential_ask",
}
ALL_ASK_FIELDS = ["constraints"] + list(lab.SOFT)


def task_key(row: dict) -> tuple[str, int, str]:
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
    if payload.get("runner") != "targeted_core_soft_ask_screen_v1":
        return {}
    valid_methods = set(NEW_METHODS)
    valid_seeds = set(SEEDS)
    valid_variants = set(VARIANTS)
    rows = {}
    for row in payload.get("new_rows", []):
        if (row.get("method") in valid_methods and row.get("seed") in valid_seeds
                and row.get("variant") in valid_variants and row.get("valid")):
            rows[task_key(row)] = row
    return rows


def _get_controls() -> list[dict]:
    if not PILOT_JSON.exists():
        raise FileNotFoundError(f"Expected existing pilot controls at {PILOT_JSON}")
    rows = json.loads(PILOT_JSON.read_text())["rows"]
    controls = [r for r in rows if r.get("method") in HARD_CONTROLS and r.get("seed") in SEEDS]
    for method in HARD_CONTROLS:
        for variant in VARIANTS:
            count = sum(r["method"] == method and r["variant"] == variant for r in controls)
            if count != len(SEEDS):
                raise ValueError(f"Expected {len(SEEDS)} hard-only rows for {method}/{variant}; got {count}")
    return controls


def _method_summary(rows: list[dict]) -> dict:
    out = {}
    for method in sorted({r["method"] for r in rows}):
        mr = [r for r in rows if r["method"] == method]
        by_variant = {
            v: mean(r["msmi_per_100_arrived_members"] for r in mr if r["variant"] == v)
            for v in VARIANTS
        }
        out[method] = {
            "episodes": len(mr),
            "primary_equal_family_mean_msmi_per_100": mean(by_variant.values()),
            "scenario_msmi_per_100": by_variant,
            "msmi_events": sum(int(r["mutual_second_meeting_intention"]) for r in mr),
            "ask_units_mean": mean(r["ask_cost"] for r in mr),
            "hard_constraint_bundles_mean": mean(
                r.get("hard_constraint_bundles", r["ask_cost"] / 3 if r["method"] in HARD_CONTROLS else 0)
                for r in mr
            ),
            "soft_field_questions_mean": mean(r.get("soft_field_questions", 0) for r in mr),
            "coverage_mean": mean(r["coverage"] for r in mr),
            "assignments_mean": mean(r["assignments"] for r in mr),
        }
    return out


def _paired_contrasts(rows: list[dict]) -> dict:
    by_method = {
        method: {(r["seed"], r["variant"]): r for r in rows if r["method"] == method}
        for method in {r["method"] for r in rows}
    }
    out = {}
    for method, control in CONTROL_FOR.items():
        diffs = {
            (seed, variant): by_method[method][(seed, variant)]["msmi_per_100_arrived_members"]
            - by_method[control][(seed, variant)]["msmi_per_100_arrived_members"]
            for seed in SEEDS for variant in VARIANTS
        }
        seed_blocks = {seed: mean(diffs[(seed, variant)] for variant in VARIANTS) for seed in SEEDS}
        per_variant = {}
        for variant in VARIANTS:
            values = [diffs[(seed, variant)] for seed in SEEDS]
            per_variant[variant] = {
                "mean_difference": mean(values),
                "wins_ties_losses": [sum(x > 0 for x in values), sum(x == 0 for x in values), sum(x < 0 for x in values)],
            }
        values = list(diffs.values())
        out[f"{method}_minus_{control}"] = {
            "mean_equal_family_difference": mean(seed_blocks.values()),
            "seed_block_differences": {str(k): v for k, v in seed_blocks.items()},
            "wins_ties_losses_18_pairs": [sum(x > 0 for x in values), sum(x == 0 for x in values), sum(x < 0 for x in values)],
            "per_variant": per_variant,
            "note": "Three-seed screening contrast only; no p-value or confirmatory inference.",
        }
    return out


def _write_csv(summary: dict) -> None:
    fields = [
        "method", "episodes", "primary_equal_family_mean_msmi_per_100", "msmi_events",
        "ask_units_mean", "hard_constraint_bundles_mean", "soft_field_questions_mean",
        "coverage_mean", "assignments_mean",
    ]
    with OUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for method, row in summary.items():
            writer.writerow({"method": method, **{key: row[key] for key in fields if key != "method"}})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=3, help="independent rollout processes (start with 2 or 3)")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be at least 1")
    RESULTS.mkdir(parents=True, exist_ok=True)

    controls = _get_controls()
    tasks = [(m, s, v) for m in NEW_METHODS for v in VARIANTS for s in SEEDS]
    done = _load_new_rows()
    unexpected = set(done) - set(tasks)
    if unexpected:
        done = {k: v for k, v in done.items() if k in set(tasks)}
    pending = [task for task in tasks if task not in done]

    def checkpoint(complete: bool = False) -> None:
        rows = [done[t] for t in tasks if t in done]
        _atomic_json(OUT_JSON, {
            "runner": "targeted_core_soft_ask_screen_v1",
            "seeds": SEEDS,
            "variants": VARIANTS,
            "new_methods": NEW_METHODS,
            "target_new_episodes": len(tasks),
            "completed_new_episodes": len(rows),
            "complete": complete,
            "note": "Public synthetic 3-seed screen. Existing hard-only controls are reused; no private evaluation or Docker timing test.",
            "new_rows": rows,
        })

    print(f"Checkpoint status: {len(done)}/{len(tasks)} new episodes already complete; {len(pending)} remain. Workers={args.workers}.", flush=True)
    if pending:
        print(f"Starting {len(pending)} missing episodes.", flush=True)
        if args.workers == 1:
            for index, task in enumerate(pending, 1):
                row = _run_one(task)
                done[task] = row
                checkpoint(False)
                print(f"{len(done)}/{len(tasks)} {task[0]}/{task[2]}/{task[1]} valid={row['valid']}", flush=True)
        else:
            with ProcessPoolExecutor(max_workers=args.workers) as executor:
                future_to_task = {executor.submit(_run_one, task): task for task in pending}
                for future in as_completed(future_to_task):
                    task = future_to_task[future]
                    row = future.result()
                    done[task] = row
                    checkpoint(False)
                    print(f"{len(done)}/{len(tasks)} {task[0]}/{task[2]}/{task[1]} valid={row['valid']}", flush=True)

    checkpoint(True)
    new_rows = [done[t] for t in tasks]
    combined = controls + new_rows
    summary = _method_summary(combined)
    contrasts = _paired_contrasts(combined)
    payload = json.loads(OUT_JSON.read_text())
    payload["control_methods"] = HARD_CONTROLS
    payload["summary"] = summary
    payload["paired_contrasts_vs_hard_only"] = contrasts
    payload["combined_rows"] = combined
    _atomic_json(OUT_JSON, payload)
    _write_csv(summary)
    print("Wrote", OUT_JSON)
    print("Wrote", OUT_CSV)
    print(json.dumps({"summary": summary, "paired_contrasts_vs_hard_only": contrasts}, indent=2))


if __name__ == "__main__":
    main()
