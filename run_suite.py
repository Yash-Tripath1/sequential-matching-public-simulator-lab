"""Run a small public-data comparison plus a tiny GA hyperparameter search."""
from __future__ import annotations

import json
import random
import statistics
import time
from pathlib import Path

from experiment_lab import (
    CORE, POLICY_FACTORIES, run_episode, save_results, summarize,
)

OUT = Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
VARIANTS = ["development", "sparse", "cold_start", "delayed", "shift", "drift"]
TEST_SEEDS = [101, 202, 303]
TRAIN_CASES = [(23, "development"), (47, "development"),
               (23, "sparse"), (47, "sparse"),
               (23, "drift"), (47, "drift")]
METHODS = ["greedy", "no_ask", "random_feasible", "max_weight_similarity",
           "thompson_pattern", "gp_mean", "gp_ucb", "potential_ask"]


def save_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")


def normalize(weights):
    values = [max(0.02, float(x)) for x in weights]
    total = sum(values)
    return {field: value / total for field, value in zip(CORE, values)}


def ga_search():
    rng = random.Random(8675309)
    cache: dict[tuple[float, ...], tuple[float, list[dict]]] = {}
    history = []

    def fitness(weight_map):
        key = tuple(round(weight_map[f], 4) for f in CORE)
        if key not in cache:
            rows = []
            for seed, variant in TRAIN_CASES:
                row = run_episode("ga_tuned", seed, variant, weights=weight_map)
                row["ga_weights"] = weight_map
                rows.append(row)
            score = statistics.mean(r["msmi_per_100_arrived_members"] for r in rows)
            cache[key] = (score, rows)
            save_json(OUT / "ga_training_cache.json", [
                {"weights": list(k), "score": v[0]} for k, v in cache.items()
            ])
        return cache[key][0]

    population = [normalize([1, 1, 1, 1])]
    population.extend(normalize([rng.uniform(0.05, 1.0) for _ in CORE]) for _ in range(5))
    best_ever = None
    for generation in range(2):
        scored = [(fitness(w), w) for w in population]
        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_weights = scored[0]
        if best_ever is None or best_score > best_ever[0]:
            best_ever = (best_score, best_weights)
        history.append({"generation": generation, "best_train_mean": best_score,
                        "mean_train_mean": statistics.mean(s for s, _ in scored),
                        "best_weights": best_weights})
        save_json(OUT / "ga_search_history.json", history)
        print(json.dumps({"stage": "ga_train", "generation": generation,
                          "best_train_mean": best_score, "weights": best_weights}), flush=True)
        if generation == 1:
            break

        # Elitism + tournament selection + arithmetic crossover + mutation.
        next_population = [scored[0][1], scored[1][1]]
        while len(next_population) < len(population):
            pool = rng.sample(scored, k=min(3, len(scored)))
            p1 = max(pool, key=lambda x: x[0])[1]
            pool = rng.sample(scored, k=min(3, len(scored)))
            p2 = max(pool, key=lambda x: x[0])[1]
            child = []
            for f in CORE:
                val = p1[f] if rng.random() < 0.5 else p2[f]
                if rng.random() < 0.4:
                    val += rng.gauss(0, 0.2)
                child.append(max(0.02, val))
            next_population.append(normalize(child))
        population = next_population

    return best_ever[1], history


def main():
    all_rows = []
    result_path = OUT / "public_pilot_results.json"
    total = len(METHODS) * len(TEST_SEEDS) * len(VARIANTS)
    current = 0
    for method in METHODS:
        for variant in VARIANTS:
            for seed in TEST_SEEDS:
                current += 1
                t0 = time.time()
                row = run_episode(method, seed, variant)
                all_rows.append(row)
                save_results(all_rows, result_path)
                print(json.dumps({"stage": "public_eval", "progress": f"{current}/{total}",
                                  "method": method, "seed": seed, "variant": variant,
                                  "valid": row["valid"],
                                  "msmi_per_100": row["msmi_per_100_arrived_members"],
                                  "coverage": round(row["coverage"], 3),
                                  "seconds": round(time.time() - t0, 2)}), flush=True)

    tuned_weights, history = ga_search()
    ga_rows = []
    ga_total = len(TEST_SEEDS) * len(VARIANTS)
    ga_current = 0
    for variant in VARIANTS:
        for seed in TEST_SEEDS:
            ga_current += 1
            t0 = time.time()
            row = run_episode("ga_tuned", seed, variant, weights=tuned_weights)
            row["ga_weights"] = tuned_weights
            ga_rows.append(row)
            all_rows.append(row)
            save_results(all_rows, result_path)
            print(json.dumps({"stage": "ga_holdout", "progress": f"{ga_current}/{ga_total}",
                              "seed": seed, "variant": variant,
                              "msmi_per_100": row["msmi_per_100_arrived_members"],
                              "coverage": round(row["coverage"], 3),
                              "seconds": round(time.time() - t0, 2)}), flush=True)

    save_json(OUT / "ga_selected_weights.json", {"weights": tuned_weights,
        "training_cases": TRAIN_CASES, "ga_history": history,
        "holdout_mean_msmi_per_100": statistics.mean(r["msmi_per_100_arrived_members"] for r in ga_rows)})
    print(json.dumps(summarize(all_rows), indent=2), flush=True)


if __name__ == "__main__":
    main()
