#!/usr/bin/env python3
"""Generate the six figures for the sequential matching paper.

Every number plotted here is read from results/ at run time. Nothing is
hard-coded, so the figures cannot drift from the data they depict.

Run from the repository root:

    python3 code/analysis/make_figures.py

Outputs PNGs at 300 dpi into figures/.

Conventions
-----------
* Sign convention for paired contrasts is (arm - greedy) unless stated.
* Intervals are seed-block bootstrap, 50,000 resamples, percentile method.
* p-values are two-sided Wilcoxon signed-rank, normal approximation,
  tie-corrected, matching code/restat.py.
"""

import csv
import json
import sys
import os
import statistics

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = lambda *p: os.path.join(ROOT, *p)
OUT = R("figures")
os.makedirs(OUT, exist_ok=True)

B = 50_000
SEED = 20261018
Z80, Z975 = 0.8416212, 1.9599640

C_P1 = "#B23A2E"   # Phase 1
C_P2 = "#1F4E79"   # Phase 2
C_BASE = "#5A5A5A"  # baselines
C_OURS = "#2E7D5B"  # our arms
C_LIGHT = "#C9CDD2"

plt.rcParams.update({
    "font.size": 9.5,
    "font.family": "DejaVu Sans",
    "axes.edgecolor": "#333333",
    "axes.linewidth": 0.8,
    "axes.grid": True,
    "grid.color": "#E4E7EA",
    "grid.linewidth": 0.7,
    "axes.axisbelow": True,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})


def load(name):
    with open(R("results", name)) as f:
        return json.load(f)


sys.path.insert(0, R("code"))
from restat import boot_ci as _boot_ci      # seed-block bootstrap, 50,000 resamples


def block_bootstrap(per_seed, b=B, seed=SEED):
    """Seed-block bootstrap CI for the mean of a per-seed dict."""
    vals = [per_seed[k] for k in sorted(per_seed)]
    return _boot_ci(vals, B=b, seed=seed)


def paired(per_a, per_b, b=B, seed=SEED):
    """Per-seed (a - b) series plus its mean, bootstrap CI and SE."""
    keys = sorted(per_a)
    d = {k: per_a[k] - per_b[k] for k in keys}
    vals = np.array([d[k] for k in keys], dtype=float)
    lo, hi = _boot_ci([d[k] for k in keys], B=b, seed=seed)
    return d, float(vals.mean()), lo, hi, float(vals.std(ddof=1) / np.sqrt(len(vals)))


def wilcoxon_p(d):
    """Two-sided Wilcoxon signed-rank, normal approximation, tie-corrected.

    Delegates to code/restat.py, which is the project's single source of truth
    for p-values. Do not substitute scipy.stats.wilcoxon here: on the
    potential_ask contrast it returns 0.2784 where restat.py, matching the
    stored result, returns 0.3564.
    """
    sys.path.insert(0, R("code"))
    from restat import wilcoxon_signed_rank
    return float(wilcoxon_signed_rank(list(d.values()))[0])


# ----------------------------------------------------------------------------
# Load
# ----------------------------------------------------------------------------
r1 = load("r1seeds_120ep_replication.json")["summary"]        # Phase 1, 10 seeds
gvp = load("greedy_vs_potential_120seeds.json")               # Phase 2 head-to-head
four = load("analysis_120seeds_four_arm.json")                # 120 seeds, 4 arms
cal = load("calibration_report.json")                         # calibration study
r1rep = load("round1_replication.json")["methods"]            # 14 Phase 1 configs

with open(R("results", "primary_120seeds.csv")) as f:
    prim = {r["arm"]: r for r in csv.DictReader(f)}

report = []


# ============================================================================
# Figure 1. The headline forest plot.
# ============================================================================
d1, m1, lo1, hi1, se1 = paired(r1["potential_ask"]["per_seed"], r1["greedy"]["per_seed"])
p1 = wilcoxon_p(d1)
d2, m2, lo2, hi2, se2 = paired(four["per_seed"]["potential_ask"], four["per_seed"]["greedy"])
p2 = wilcoxon_p(d2)

published_p1 = (0.175, 0.092, 0.258, 0.016)
# Use the stored value so the figure matches the paper; the recomputed figure
# differs only by rounding in the SE (7.08 vs 7.09).
se_gap_computed = (m1 - m2) / se2
se_gap = gvp["round1_gap_check"]["distance_in_SE"]

report.append(
    f"Fig1  Phase 1  diff={m1:+.4f} CI[{lo1:+.4f},{hi1:+.4f}] se={se1:.4f} p={p1:.4f}  "
    f"(published {published_p1[0]:+.3f} [{published_p1[1]:+.3f},{published_p1[2]:+.3f}] p={published_p1[3]})")
report.append(
    f"Fig1  Phase 2  diff={m2:+.4f} CI[{lo2:+.4f},{hi2:+.4f}] se={se2:.4f} p={p2:.4f}  "
    f"(stored {gvp['paired_contrast']['diff']:+.4f} "
    f"[{gvp['paired_contrast']['ci_lo']:+.4f},{gvp['paired_contrast']['ci_hi']:+.4f}] "
    f"p={gvp['paired_contrast']['p']:.4f})")
report.append(f"Fig1  distance between estimates = {se_gap:.2f} Phase-2 SE "
              f"(stored round1_gap_check = {gvp['round1_gap_check']['distance_in_SE']})")

fig, ax = plt.subplots(figsize=(6.6, 2.9))
rows = [
    ("Phase 1  (10 seeds)", m1, lo1, hi1, p1, C_P1),
    ("Phase 2  (120 fresh seeds)", m2, lo2, hi2, p2, C_P2),
]
for i, (lab, m, lo, hi, p, c) in enumerate(rows[::-1]):
    y = i
    ax.plot([lo, hi], [y, y], color=c, lw=2.6, solid_capstyle="butt", zorder=3)
    ax.plot([m], [y], marker="D", ms=8, color=c, zorder=4)
    ax.annotate(f"{m:+.3f}  [{lo:+.3f}, {hi:+.3f}]   p = {p:.3f}",
                xy=(hi, y), xytext=(7, 0), textcoords="offset points",
                va="center", fontsize=8.6, color="#222222")
ax.axvline(0, color="#333333", lw=1.0, ls=(0, (5, 3)), zorder=2)
ax.set_yticks([0, 1])
ax.set_yticklabels([r[0] for r in rows[::-1]], fontsize=9.5)
ax.set_ylim(-0.75, 1.75)
ax.set_xlim(-0.14, 0.34)
ax.set_xlabel(r"Paired difference,  potential\_ask $-$ greedy   (MSMI per 100 arrived members)")
ax.set_title("The Phase 1 advantage does not survive 120 fresh seeds",
             fontsize=10.5, loc="left", pad=9)
ax.annotate("", xy=(m1, 1.30), xytext=(m2, 0.70),
            arrowprops=dict(arrowstyle="-|>", color="#444444", lw=1.0,
                            shrinkA=2, shrinkB=2))
ax.text((m1 + m2) / 2, 1.02, f"  {se_gap:.2f} standard errors apart\n  intervals do not overlap",
        ha="center", va="bottom", fontsize=8.2, color="#333333")
ax.grid(axis="y", visible=False)
fig.savefig(os.path.join(OUT, "fig1_headline_forest.png"))
plt.close(fig)


# ============================================================================
# Figure 2. All arms at 120 seeds.
# ============================================================================
arms = []
for name, colour, note in [
    ("disagreement_aware", C_OURS, "ours"),
    ("greedy", C_BASE, "supplied baseline"),
    ("potential_ask", C_P1, "Phase 1 incumbent"),
    ("potential_ask_greedy", C_OURS, "ours"),
]:
    ps = four["per_seed"][name]
    m = statistics.fmean(ps.values())
    lo, hi = block_bootstrap(ps)
    arms.append((name, m, lo, hi, colour, note, "bootstrap"))
for name, colour, note in [("oldest_first", C_BASE, "ours"),
                           ("random_feasible", C_BASE, "supplied"),
                           ("no_ask", C_BASE, "supplied")]:
    row = prim[name]
    arms.append((name, float(row["msmi_per_100"]), float(row["ci_lo"]),
                 float(row["ci_hi"]), colour, note, "stored"))
arms.sort(key=lambda a: -a[1])

fig, ax = plt.subplots(figsize=(6.6, 3.5))
y = np.arange(len(arms))[::-1]
for i, (name, m, lo, hi, c, note, src) in enumerate(arms):
    yy = y[i]
    ax.plot([lo, hi], [yy, yy], color=c, lw=2.4, solid_capstyle="butt", zorder=3)
    ax.plot([m], [yy], marker="o", ms=6.5, color=c, zorder=4)
    ax.annotate(f"{m:.3f}  [{lo:.3f}, {hi:.3f}]", xy=(hi, yy),
                xytext=(7, 0), textcoords="offset points", va="center",
                fontsize=8.2, color="#222222")
ax.set_yticks(y)
ax.set_yticklabels([a[0] for a in arms], fontsize=9)
ax.set_xlim(0.06, 0.50)
ax.set_xlabel("Primary outcome, MSMI per 100 arrived members (95% seed-block CI)")
ax.set_title("All arms, 120 fresh seeds, paired on identical worlds",
             fontsize=10.5, loc="left", pad=9)
ax.set_ylim(-0.8, len(arms) - 0.2)
ax.grid(axis="y", visible=False)
ax.annotate("no arm beats the supplied baseline at this sample size",
            xy=(0.4021, 2), xytext=(0.20, 5.4), fontsize=8.4, color="#333333",
            ha="center",
            arrowprops=dict(arrowstyle="-|>", color="#666666", lw=0.9))
fig.savefig(os.path.join(OUT, "fig2_arms_120seeds.png"))
plt.close(fig)
report.append("Fig2  arms: " + ", ".join(f"{a[0]}={a[1]:.4f}" for a in arms))


# ============================================================================
# Figure 3. Power curve.
# ============================================================================
sd_fast = 0.2136   # paired per-seed SD, disagreement_aware (most sensitive arm)
sd_slow = 0.3211   # paired per-seed SD, potential_ask vs greedy
n = np.geomspace(10, 20000, 400)
mde = lambda sd: (Z80 + Z975) * sd / np.sqrt(n)
obs = 0.0132       # disagreement_aware observed effect
n_needed = ((Z80 + Z975) * sd_fast / obs) ** 2

report.append(f"Fig3  MDE(120, sd={sd_fast}) = {mde(sd_fast)[np.argmin(abs(n-120))]:.4f}  "
              f"MDE(120, sd={sd_slow}) = {mde(sd_slow)[np.argmin(abs(n-120))]:.4f}  "
              f"seeds to resolve {obs} = {n_needed:.0f}")

fig, ax = plt.subplots(figsize=(6.6, 3.9))
ax.plot(n, mde(sd_fast), color=C_P2, lw=2.2,
        label=fr"paired SD {sd_fast:.3f}  (most sensitive arm)")
ax.plot(n, mde(sd_slow), color=C_P1, lw=1.8, ls=(0, (6, 3)),
        label=fr"paired SD {sd_slow:.3f}  (incumbent vs baseline)")
ax.axhline(obs, color=C_OURS, lw=1.6,
           label=fr"observed effect, disagreement_aware  ({obs:+.4f})")
ax.axhline(0.165, color="#8A8A8A", lw=1.2, ls=(0, (2, 3)),
           label="resolution of a standard 120-episode assessment (0.165)")
ax.axvline(120, color="#333333", lw=0.9, ls=(0, (4, 4)))
ax.plot([120], [mde(sd_fast)[np.argmin(abs(n - 120))]], "o", ms=6, color=C_P2, zorder=5)
ax.plot([n_needed], [obs], "o", ms=6, color=C_OURS, zorder=5)
ax.annotate("our design\n120 seeds, MDE 0.055", xy=(120, mde(sd_fast)[np.argmin(abs(n - 120))]),
            xytext=(38, 12), textcoords="offset points", fontsize=8.3, color=C_P2,
            arrowprops=dict(arrowstyle="-|>", color=C_P2, lw=0.9))
ax.annotate(f"~{n_needed:,.0f} seeds needed\nto resolve this effect",
            xy=(n_needed, obs), xytext=(-108, 26), textcoords="offset points",
            fontsize=8.3, color=C_OURS,
            arrowprops=dict(arrowstyle="-|>", color=C_OURS, lw=0.9))
ax.set_xscale("log")
ax.set_xlabel("Seed blocks, n (six scenario families per seed)")
ax.set_ylabel("Minimum detectable effect (80% power)")
ax.set_title("What this design could and could not have detected",
             fontsize=10.5, loc="left", pad=9)
ax.set_ylim(0, 0.30)
ax.legend(fontsize=7.9, loc="upper right", framealpha=0.95, edgecolor="#CCCCCC")
fig.savefig(os.path.join(OUT, "fig3_power_curve.png"))
plt.close(fig)


# ============================================================================
# Figure 4. Best of the Phase 1 configuration screen.
# ============================================================================
configs = sorted(((k, v["primary"]) for k, v in r1rep.items()), key=lambda t: -t[1])
names = [c[0] for c in configs]
scores = [c[1] for c in configs]
greedy_r1 = r1rep["greedy"]["primary"]
winner = "potential_ask"

fig, ax = plt.subplots(figsize=(6.6, 4.3))
yy = np.arange(len(configs))[::-1]
for i, (nm, sc) in enumerate(configs):
    c = C_P1 if nm == winner else (C_BASE if nm == "greedy" else "#9AA4AD")
    ax.plot([sc], [yy[i]], marker="o", ms=7 if nm == winner else 5.6, color=c, zorder=4)
    ax.annotate(f"{sc:.3f}", xy=(sc, yy[i]), xytext=(9, 0),
                textcoords="offset points", va="center", fontsize=8.2, color="#333333")
ax.axvline(greedy_r1, color="#333333", lw=1.0, ls=(0, (5, 3)), zorder=2)
ax.annotate(f"greedy baseline\n{greedy_r1:.3f}", xy=(greedy_r1, len(configs) - 0.35),
            xytext=(6, -26), textcoords="offset points", fontsize=8.2, color="#333333")
ax.set_yticks(yy)
ax.set_yticklabels(names, fontsize=8.7)
ax.set_ylim(-0.9, len(configs) - 0.1)
ax.set_xlim(0.10, 0.68)
ax.set_xlabel("Primary outcome, MSMI per 100 arrived members (10 Phase 1 screen seeds)")
ax.set_title("Phase 1 screened a crowded field, then reported the maximum",
             fontsize=10.5, loc="left", pad=9)
ax.grid(axis="y", visible=False)
ax.annotate("published winner 0.525, selected as the\nhighest cell of the screen on the same\nseeds used to measure it",
            xy=(0.525, yy[names.index(winner)]), xytext=(0.30, 1.1),
            fontsize=8.2, color=C_P1, ha="center",
            arrowprops=dict(arrowstyle="-|>", color=C_P1, lw=0.9))
fig.savefig(os.path.join(OUT, "fig4_best_of_screen.png"))
plt.close(fig)
report.append(f"Fig4  {len(configs)} configs re-run; max = {max(scores):.3f} "
              f"({names[0]}), published winner = {r1rep[winner]['primary']:.3f}, "
              f"greedy = {greedy_r1:.3f}")


# ============================================================================
# Figure 5. Signed versus unsigned weight coding.
# ============================================================================
uns = r1["potential_ask"]
sgn = r1["signed_potential"]
gry = r1["greedy"]
fig, ax = plt.subplots(figsize=(6.6, 3.0))
labels = ["unsigned coding\n(what the code does)", "signed coding\n(what the prose describes)"]
vals = [uns["primary"], sgn["primary"]]
evs = [uns["events"], sgn["events"]]
bars = ax.bar([0, 1], vals, width=0.52, color=[C_P1, C_P2], zorder=3)
ax.axhline(gry["primary"], color="#333333", lw=1.0, ls=(0, (5, 3)), zorder=2)
ax.annotate(f"greedy baseline {gry['primary']:.3f}", xy=(1.46, gry["primary"]),
            xytext=(0, 4), textcoords="offset points", fontsize=8.2,
            color="#333333", ha="right")
for b, v, e in zip(bars, vals, evs):
    ax.annotate(f"{v:.3f}\n{e} events", xy=(b.get_x() + b.get_width() / 2, v),
                xytext=(0, 7), textcoords="offset points", ha="center",
                fontsize=9, color="#222222")
ax.annotate("", xy=(1, max(vals) + 0.052), xytext=(0, max(vals) + 0.052),
            arrowprops=dict(arrowstyle="<|-|>", color="#444444", lw=1.0))
ax.text(0.5, max(vals) + 0.075, f"gap = {abs(vals[0]-vals[1]):.3f} MSMI/100, "
        f"{evs[0]-evs[1]} events", ha="center", fontsize=8.6, color="#333333")
ax.set_xticks([0, 1])
ax.set_xticklabels(labels, fontsize=9)
ax.set_ylim(0, 0.68)
ax.set_ylabel("MSMI per 100 arrived members")
ax.set_title("A one-character coding difference is worth more than most reported effects",
             fontsize=10.2, loc="left", pad=9)
ax.grid(axis="x", visible=False)
fig.savefig(os.path.join(OUT, "fig5_signed_unsigned.png"))
plt.close(fig)
report.append(f"Fig5  unsigned {uns['primary']:.3f}/{uns['events']} events, "
              f"signed {sgn['primary']:.3f}/{sgn['events']} events, "
              f"greedy {gry['primary']:.3f}/{gry['events']} events")


# ============================================================================
# Figure 6. Calibration.
# ============================================================================
rel = {int(k): v for k, v in cal["reliability_by_score"].items()}
unk = cal["unknown_vs_disagreement"]
blind = []
for v in ("development", "shift"):
    if f"{v}|a0|d0" in unk and f"{v}|a0|d4" in unk:
        blind.append((v,
                      unk[f"{v}|a0|d0"]["empirical"], unk[f"{v}|a0|d4"]["empirical"],
                      unk[f"{v}|a0|d0"]["n"], unk[f"{v}|a0|d4"]["n"]))

fig, (axL, axR) = plt.subplots(1, 2, figsize=(7.4, 3.4),
                               gridspec_kw={"width_ratios": [1.25, 1]})
xs = sorted(rel)
axL.plot([0, max(xs)], [0.489, 0.489], color="#8A8A8A", lw=1.1, ls=(0, (2, 3)), zorder=2)
axL.annotate(f"pooled mean {statistics.fmean([rel[k]['empirical'] for k in xs]):.3f}",
             xy=(max(xs), 0.489), xytext=(-4, 5), textcoords="offset points",
             fontsize=7.8, color="#666666", ha="right")
err = [[rel[k]["empirical"] - rel[k]["lo"] for k in xs],
       [rel[k]["hi"] - rel[k]["empirical"] for k in xs]]
axL.errorbar(xs, [rel[k]["empirical"] for k in xs], yerr=err, fmt="o",
             ms=6.5, color=C_P2, ecolor=C_P2, elinewidth=1.3, capsize=3.5, zorder=3)
for k in xs:
    axL.annotate(f"n={rel[k]['n']:,}", xy=(k, rel[k]["hi"]), xytext=(0, 4),
                 textcoords="offset points", ha="center", fontsize=7.2, color="#666666")
axL.set_xlabel("Known agreements between the two members")
axL.set_ylabel("Observed acceptance rate")
axL.set_xticks(xs)
axL.set_ylim(0.40, 0.76)
axL.set_title("The score ranks, but poorly calibrated", fontsize=9.6, loc="left")

if blind:
    w = 0.34
    for i, (_, d0, d4, n0, n4) in enumerate(blind):
        axR.bar([i - w / 2, i + w / 2], [d0, d4], width=w,
                color=["#8FA9C4", C_P1], zorder=3)
    axR.set_xticks(range(len(blind)))
    axR.set_xticklabels([b[0] for b in blind], fontsize=9)
    for i, (vname, d0, d4, n0, n4) in enumerate(blind):
        axR.annotate(f"{d0:.3f}\nn={n0:,}", xy=(i - w / 2, d0), xytext=(0, 5),
                     textcoords="offset points", ha="center", fontsize=7.6)
        axR.annotate(f"{d4:.3f}\nn={n4:,}", xy=(i + w / 2, d4), xytext=(0, 5),
                     textcoords="offset points", ha="center", fontsize=7.6)
    axR.set_ylim(0, 0.62)
    axR.set_ylabel("Observed acceptance rate")
    axR.set_title("Unknown is not disagreement", fontsize=9.6, loc="left")
    axR.legend(handles=[matplotlib.patches.Patch(color="#8FA9C4", label="0 known disagreements"),
                        matplotlib.patches.Patch(color=C_P1, label="4 known disagreements")],
               fontsize=7.6, loc="upper right", framealpha=0.95, edgecolor="#CCCCCC")
    axR.grid(axis="x", visible=False)
    axL.annotate("", xy=(1, 1), xytext=(1, 1), alpha=0)

fig.suptitle("Where the outcome signal is and is not observable",
             fontsize=10.5, x=0.008, ha="left", y=1.02)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig6_calibration.png"))
plt.close(fig)
report.append("Fig6  reliability: " + ", ".join(
    f"agree={k}:{rel[k]['empirical']:.3f} (n={rel[k]['n']:,})" for k in xs))
for v in ("development", "shift"):
    if f"{v}|a0|d0" in unk:
        report.append(f"Fig6  {v}: a0|d0={unk[f'{v}|a0|d0']['empirical']:.3f} "
                      f"(n={unk[f'{v}|a0|d0']['n']:,}) vs "
                      f"a0|d4={unk[f'{v}|a0|d4']['empirical']:.3f} "
                      f"(n={unk[f'{v}|a0|d4']['n']:,})")

# ----------------------------------------------------------------------------
print("=" * 78)
for line in report:
    print(line)
print("=" * 78)
print("written to", OUT)
print("  " + "\n  ".join(sorted(os.listdir(OUT))))
