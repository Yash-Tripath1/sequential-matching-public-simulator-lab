"""Run paired ablations for ask policy vs matching policy on the same cases."""
import json
import time
from pathlib import Path
from experiment_lab import run_episode, save_results

OUT = Path(__file__).resolve().parent / "results/public_pilot_results.json"
VARIANTS = ["development", "sparse", "cold_start", "delayed", "shift", "drift"]
SEEDS = [101, 202, 303]
METHODS = ["core_max_matching", "potential_ask_greedy"]

payload = json.loads(OUT.read_text())
rows = payload["rows"]
for method in METHODS:
    for variant in VARIANTS:
        for seed in SEEDS:
            if any(r["method"] == method and r["variant"] == variant and r["seed"] == seed for r in rows):
                continue
            started = time.time()
            row = run_episode(method, seed, variant)
            rows.append(row)
            save_results(rows, OUT)
            print(json.dumps({"method": method, "variant": variant, "seed": seed,
                              "msmi_per_100": row["msmi_per_100_arrived_members"],
                              "coverage": row["coverage"],
                              "seconds": round(time.time() - started, 2)}), flush=True)
print(json.dumps(json.loads(OUT.read_text())["summary"], indent=2))
