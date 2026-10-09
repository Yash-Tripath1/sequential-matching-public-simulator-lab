#!/usr/bin/env python3
"""Export CSV summaries and a README-ready MSMI chart from saved pilot results."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
INPUT = RESULTS / "public_pilot_results.json"
VARIANTS = ["development", "sparse", "cold_start", "delayed", "shift", "drift"]
VARIANT_LABELS = ["Development", "Sparse", "Cold start", "Delayed", "Shift", "Drift"]
LABELS = {
    "potential_ask": "Potential asks + max-weight (7 soft)",
    "potential_ask_greedy": "Potential asks + starter greedy",
    "thompson_pattern": "Thompson pattern",
    "greedy": "Starter greedy",
    "gp_ucb": "GP-UCB",
    "max_weight_similarity": "Max-weight similarity (default asks)",
    "random_feasible": "Random feasible",
    "gp_mean": "GP mean only",
    "ga_tuned": "GA-tuned core weights",
    "core_max_matching": "Core max-weight, equal weights",
    "no_ask": "No clarification",
}


def write_exports(data: dict) -> None:
    summary = data["summary"]
    with (RESULTS / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "method", "episodes", "equal_variant_weight_msmi_per_100",
            "mean_coverage", "mean_mutual_acceptances_per_100", "mean_ask_cost",
            "mean_in_process_policy_seconds",
        ])
        ordered = sorted(
            summary.items(),
            key=lambda item: item[1]["overall"]["equal_variant_weight_msmi_per_100"],
            reverse=True,
        )
        for method, entry in ordered:
            overall = entry["overall"]
            writer.writerow([
                method, overall["episodes"], overall["equal_variant_weight_msmi_per_100"],
                overall["mean_coverage"], overall["mean_mutual_acceptances_per_100"],
                overall["mean_ask_cost"], overall["mean_in_process_policy_seconds"],
            ])

    with (RESULTS / "by_variant.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "method", "variant", "episodes", "mean_msmi_per_100", "sd_msmi_per_100",
            "mean_coverage", "mean_mutual_acceptances_per_100", "mean_ask_cost",
        ])
        for method, entry in sorted(summary.items()):
            for variant, values in entry["by_variant"].items():
                writer.writerow([
                    method, variant, values["episodes"], values["msmi_per_100_mean"],
                    values["msmi_per_100_sd"], values["coverage_mean"],
                    values["mutual_acceptances_per_100_mean"], values["ask_cost_mean"],
                ])

    fields = [
        "method", "seed", "variant", "valid", "msmi_per_100_arrived_members",
        "coverage", "mutual_acceptances_per_100", "ask_cost", "served_members",
        "unserved_members", "mean_first_intro_wait_days", "policy_wall_seconds_in_process",
    ]
    with (RESULTS / "episode_results.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data["rows"])


def write_chart(data: dict) -> None:
    summary = data["summary"]
    methods = sorted(
        summary,
        key=lambda method: summary[method]["overall"]["equal_variant_weight_msmi_per_100"],
        reverse=True,
    )
    means = [summary[m]["overall"]["equal_variant_weight_msmi_per_100"] for m in methods]
    labels = [LABELS.get(m, m) for m in methods]
    matrix = np.asarray([
        [summary[m]["by_variant"][v]["msmi_per_100_mean"] for v in VARIANTS]
        for m in methods
    ])

    teal = "#0f766e"
    blue = "#2563eb"
    gray = "#94a3b8"
    colors = [
        teal if method.startswith("potential_ask")
        else blue if method in {"thompson_pattern", "gp_ucb", "gp_mean", "ga_tuned"}
        else gray
        for method in methods
    ]

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 12,
        "axes.labelsize": 9,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    })
    fig = plt.figure(figsize=(16.5, 9.3))
    # Reserve clear bands for the title/subtitle at top and source/caveat note at bottom.
    grid = fig.add_gridspec(
        1, 2, left=0.20, right=0.94, bottom=0.21, top=0.84,
        width_ratios=[1.12, 1.0], wspace=0.12,
    )
    ax_bar = fig.add_subplot(grid[0, 0])
    ax_heat = fig.add_subplot(grid[0, 1])
    y = np.arange(len(methods))

    ax_bar.barh(y, means, color=colors, height=0.68, edgecolor="white", linewidth=0.7)
    ax_bar.set_yticks(y, labels)
    ax_bar.invert_yaxis()
    ax_bar.set_xlim(0, 0.76)
    ax_bar.set_xlabel("Equal-weight mean MSMI per 100 arrivals  (higher is better)")
    ax_bar.set_title("A  Overall comparison", loc="left", fontweight="bold", pad=11)
    ax_bar.xaxis.grid(True, color="#e2e8f0", linewidth=0.8)
    ax_bar.set_axisbelow(True)
    ax_bar.spines[["top", "right", "left"]].set_visible(False)
    ax_bar.spines["bottom"].set_color("#cbd5e1")
    ax_bar.tick_params(axis="y", length=0, pad=8)
    for idx, value in enumerate(means):
        ax_bar.text(value + 0.012, idx, f"{value:.3f}", va="center", ha="left",
                    fontsize=8.5, color="#0f172a", fontweight="bold" if idx < 2 else "normal")

    image = ax_heat.imshow(matrix, aspect="auto", cmap="YlGnBu", vmin=0, vmax=1.2,
                           interpolation="nearest")
    ax_heat.set_xticks(np.arange(len(VARIANTS)), VARIANT_LABELS, rotation=32,
                       ha="right", rotation_mode="anchor")
    ax_heat.set_yticks(y, [])
    ax_heat.tick_params(axis="y", left=False)
    ax_heat.set_title("B  Scenario variation", loc="left", fontweight="bold", pad=11)
    ax_heat.set_xticks(np.arange(-0.5, len(VARIANTS), 1), minor=True)
    ax_heat.set_yticks(np.arange(-0.5, len(methods), 1), minor=True)
    ax_heat.grid(which="minor", color="white", linewidth=1.5)
    ax_heat.tick_params(which="minor", bottom=False, left=False)
    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            val = matrix[row, col]
            color = "white" if val >= 0.68 else "#0f172a"
            ax_heat.text(col, row, f"{val:.2f}", ha="center", va="center",
                         fontsize=8, color=color, fontweight="medium")
    colorbar = fig.colorbar(image, ax=ax_heat, fraction=0.046, pad=0.035)
    colorbar.set_label("Mean MSMI per 100", rotation=90, labelpad=10)
    colorbar.outline.set_visible(False)

    fig.suptitle(
        "Sequential Matching — public synthetic simulator pilot",
        x=0.02, y=0.985, ha="left", fontsize=17, fontweight="bold", color="#0f172a",
    )
    fig.text(
        0.02, 0.935,
        "11 policies · 6 public variants · 3 seeds per variant · 18 episodes per policy · all simulator-valid",
        ha="left", va="top", fontsize=10, color="#475569",
    )
    fig.text(
        0.02, 0.025,
        "Teal = potential-ask variants · blue = learned/optimized prototypes · gray = reference methods. "
        "Exploratory only: rare outcomes and three seeds per scenario; not a private-evaluation result.",
        ha="left", va="bottom", fontsize=8.5, color="#475569",
    )
    fig.savefig(RESULTS / "msmi_findings.png", dpi=190, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    if not INPUT.exists():
        raise SystemExit(f"Missing {INPUT}; run the experiment suite first.")
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    if not data.get("rows") or not data.get("summary"):
        raise SystemExit("The result JSON is empty or missing its summary.")
    write_exports(data)
    write_chart(data)
    print("Wrote results/summary.csv, results/by_variant.csv, results/episode_results.csv, "
          "and results/msmi_findings.png")


if __name__ == "__main__":
    main()
