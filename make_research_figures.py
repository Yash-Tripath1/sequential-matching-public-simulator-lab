#!/usr/bin/env python3
"""Build publication-style figures from saved public aggregates (no simulations)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def workflow_figure() -> None:
    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4.2)
    ax.axis("off")

    boxes = [
        (0.25, 2.25, 1.55, 1.0, "Observe current\nstate"),
        (2.05, 2.25, 1.75, 1.0, "Rank options blocked\nby unknown hard fields"),
        (4.05, 2.25, 1.45, 1.0, "Ask within the\ndaily budget"),
        (5.75, 2.25, 1.55, 1.0, "Apply reciprocal\nhard-feasibility gate"),
        (7.55, 2.25, 1.55, 1.0, "Match feasible\ngeneral graph"),
        (9.35, 2.25, 1.4, 1.0, "Observe feedback\nwhen available"),
    ]
    colors = ["#EAF2F8", "#E8F5E9", "#E8F5E9", "#FFF3E0", "#EAF2F8", "#F3E5F5"]
    for (x, y, w, h, text), color in zip(boxes, colors):
        patch = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.08,rounding_size=0.08",
            linewidth=1.2, edgecolor="#24445C", facecolor=color,
        )
        ax.add_patch(patch)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9.2, color="#162A3A")
    for i in range(len(boxes) - 1):
        x1 = boxes[i][0] + boxes[i][2] + 0.04
        x2 = boxes[i + 1][0] - 0.05
        ax.add_patch(FancyArrowPatch((x1, 2.75), (x2, 2.75), arrowstyle="-|>", mutation_scale=12, linewidth=1.2, color="#476273"))

    ax.text(5.5, 3.72, "Clarification and matching workflow", ha="center", va="center", fontsize=15, weight="bold", color="#142B3B")
    ax.text(5.5, 1.45, "Hard constraints stay non-negotiable gates. The potential-ask score is heuristic, not exact VOI.",
            ha="center", va="center", fontsize=10, color="#344B5A")
    ax.text(5.5, 0.98, "Among feasible pairs: compare starter greedy with maximum-weight matching; soft-question asks are a secondary ablation.",
            ha="center", va="center", fontsize=9.5, color="#344B5A")
    fig.tight_layout()
    fig.savefig(RESULTS / "policy_workflow.png", dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def factorial_forest() -> None:
    data = json.loads((RESULTS / "scaled_factorial_10seeds.json").read_text())
    keys = ["ask_main", "matcher_main", "interaction"]
    labels = [
        "Ask policy: potential vs default",
        "Matcher: max-weight vs greedy",
        "Ask × matcher interaction",
    ]
    effects = data["factorial_effects"]
    estimates = [effects[k]["mean"] for k in keys]
    lows = [effects[k]["seed_block_bootstrap_ci95"][0] for k in keys]
    highs = [effects[k]["seed_block_bootstrap_ci95"][1] for k in keys]
    ps = [effects[k]["exact_two_sided_sign_flip_p_by_seed_block"] for k in keys]

    fig, ax = plt.subplots(figsize=(9.4, 4.3))
    ys = [2, 1, 0]
    ax.axvline(0, color="#555555", linewidth=1, linestyle="--", zorder=1)
    for y, label, est, lo, hi, p in zip(ys, labels, estimates, lows, highs, ps):
        color = "#2C7A7B" if est >= 0 else "#B84A4A"
        ax.errorbar(est, y, xerr=[[est - lo], [hi - est]], fmt="o", capsize=4,
                    markersize=6, color=color, ecolor=color, linewidth=2, zorder=3)
        ax.text(hi + 0.012, y, f"{est:+.3f}  [{lo:+.3f}, {hi:+.3f}]   p={p:.3f}",
                va="center", fontsize=8.8, color="#263746")
    ax.set_yticks(ys, labels)
    ax.set_xlim(-0.16, 0.35)
    ax.set_ylim(-0.6, 2.7)
    ax.set_xlabel("Difference in MSMI per 100 arrived members", fontsize=10)
    ax.set_title("Ten-seed public factorial: main effects and interaction", fontsize=13, weight="bold", pad=13)
    ax.grid(axis="x", color="#DCE3E8", linewidth=0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=9)
    ax.text(0.01, -0.24, "Points and bars: estimate and 95% seed-block bootstrap CI. Exact sign-flip p-values are unadjusted; n = 10 seed blocks.",
            transform=ax.transAxes, fontsize=8.2, color="#485B68")
    fig.subplots_adjust(left=0.31, right=0.98, top=0.84, bottom=0.25)
    fig.savefig(RESULTS / "factorial_effects_forest.png", dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def soft_holdout_plot() -> None:
    with (RESULTS / "soft_ask_holdout_aggregate.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    overall = next(r for r in rows if r["scenario"] == "Overall")
    families = [r for r in rows if r["scenario"] != "Overall"]
    labels = ["Overall (7-seed holdout)"] + [r["scenario"] for r in families]
    vals = [float(overall["paired_difference_msmi_per_100"])] + [float(r["paired_difference_msmi_per_100"]) for r in families]
    y = list(range(len(labels) - 1, -1, -1))

    fig, ax = plt.subplots(figsize=(8.8, 4.9))
    ax.axvline(0, color="#555555", linewidth=1, linestyle="--", zorder=1)
    for i, (lab, val, ypos) in enumerate(zip(labels, vals, y)):
        if lab.startswith("Overall"):
            lo = float(overall["ci95_low"])
            hi = float(overall["ci95_high"])
            ax.errorbar(val, ypos, xerr=[[val - lo], [hi - val]], fmt="D", capsize=4,
                        markersize=6, color="#245A81", ecolor="#245A81", linewidth=2, zorder=3)
        else:
            color = "#B84A4A" if val < 0 else "#2C7A7B"
            ax.plot(val, ypos, "o", markersize=6, color=color, zorder=3)
    ax.set_yticks(y, labels)
    ax.set_xlim(-0.24, 0.38)
    ax.set_ylim(-0.8, len(labels) - 0.2)
    ax.set_xlabel("Hard + soft asks minus hard-only asks (MSMI per 100)", fontsize=9.5)
    ax.set_title("Soft-question max-weight holdout: small, uncertain pooled difference", fontsize=12.5, weight="bold", pad=12)
    ax.grid(axis="x", color="#DCE3E8", linewidth=0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=9)
    ax.text(0.01, -0.24,
            "Overall: +0.024 [−0.071, +0.131], p = 0.844. Scenario points are descriptive only; no per-family intervals are available in the bundled aggregate.",
            transform=ax.transAxes, fontsize=8.1, color="#485B68", wrap=True)
    fig.subplots_adjust(left=0.31, right=0.98, top=0.84, bottom=0.28)
    fig.savefig(RESULTS / "soft_ask_holdout_aggregate.png", dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    workflow_figure()
    factorial_forest()
    soft_holdout_plot()
    print("Wrote results/policy_workflow.png")
    print("Wrote results/factorial_effects_forest.png")
    print("Wrote results/soft_ask_holdout_aggregate.png")


if __name__ == "__main__":
    main()
