"""Regenerate the scaled ten-seed scenario heatmap and primary-score plot."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "results/scaled_factorial_10seeds.json").read_text())
OUT = ROOT / "results/scaled_factorial_heatmap.png"

methods = [
    ("no_ask", "No clarification"),
    ("random_feasible", "Random feasible"),
    ("greedy", "Greedy + default asks"),
    ("max_weight_similarity", "Max-weight + default asks"),
    ("potential_ask_greedy", "Potential asks + greedy"),
    ("potential_ask", "Potential asks + max-weight"),
]
variants = ["development", "sparse", "cold_start", "delayed", "shift", "drift"]
labels = [label for _, label in methods]
mat = np.array([
    [DATA["method_summary"][key]["scenario_msmi_per_100"][variant]["mean"]
     for variant in variants]
    for key, _ in methods
])
means = np.array([
    DATA["method_summary"][key]["primary_equal_variant_msmi_per_100"]
    for key, _ in methods
])
ci = np.array([
    DATA["method_summary"][key]["primary_seed_block_ci95"]
    for key, _ in methods
])

fig = plt.figure(figsize=(16, 7.7), dpi=120)
gs = fig.add_gridspec(1, 2, width_ratios=(2.15, 1.05), left=0.16, right=0.98,
                      top=0.77, bottom=0.22, wspace=0.32)
ax = fig.add_subplot(gs[0, 0])
bar_ax = fig.add_subplot(gs[0, 1])
fig.suptitle("Clarification × matcher factorial with baseline controls\n"
             "Public synthetic simulator; 10 seeds per scenario", fontsize=16, y=0.96)

im = ax.imshow(mat, cmap="YlGnBu", vmin=0, vmax=0.9, aspect="auto")
ax.set_xticks(range(len(variants)), [v.replace("_", " ").title() for v in variants],
              rotation=31, ha="right", rotation_mode="anchor")
ax.set_yticks(range(len(labels)), labels)
ax.tick_params(axis="both", labelsize=10)
ax.set_title("Scenario MSMI / 100\n10 public seeds per scenario", fontsize=12)
for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):
        value = mat[i, j]
        ax.text(j, i, f"{value:.2f}", ha="center", va="center", fontsize=8.5,
                color="white" if value >= 0.58 else "#1f2933")
cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.025)
cb.set_label("MSMIs / 100 arrivals", fontsize=9)

colors = ["#8a93a3"] * len(methods)
colors[-2] = "#4b83a2"
colors[-1] = "#df3b3d"
y = np.arange(len(methods))
bar_ax.barh(y, means, color=colors, alpha=0.95, height=0.78, zorder=2)
bar_ax.errorbar(means, y,
                xerr=np.vstack([means - ci[:, 0], ci[:, 1] - means]),
                fmt="none", ecolor="#222222", elinewidth=1.2,
                capsize=3, zorder=3)
bar_ax.set_yticks(y, [""] * len(y))
bar_ax.invert_yaxis()
bar_ax.set_xlim(0, 0.78)
bar_ax.set_xlabel("Equal-weight score (95% seed-block bootstrap CI)", fontsize=9)
bar_ax.set_title("Overall score", fontsize=12)
bar_ax.grid(axis="x", alpha=0.22, zorder=0)
bar_ax.tick_params(axis="x", labelsize=9)
for score, row in zip(means, y):
    bar_ax.text(score + 0.012, row, f"{score:.3f}", va="center", ha="left", fontsize=8)

fig.text(0.5, 0.075,
         "Exploratory public-seed results, not private evaluation. "
         "One MSMI in a 200-arrival episode changes the score by 0.5 per 100.",
         ha="center", fontsize=9)
fig.savefig(OUT, dpi=160, bbox_inches="tight")
print(OUT)
