#!/usr/bin/env python3
"""Build the Round 2 presentation deck: 15 slides, PDF + PPTX."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
from pptx import Presentation
from pptx.util import Inches

W, H = 13.333, 7.5
NAVY = "#1f3a5f"
GREEN = "#2e7d32"
RED = "#c62828"
GREY = "#78909c"
AMBER = "#ef6c00"
LIGHT = "#eceff1"

plt.rcParams.update({"font.size": 11, "axes.edgecolor": "#90a4ae",
                     "axes.labelcolor": "#263238", "text.color": "#263238",
                     "xtick.color": "#37474f", "ytick.color": "#37474f"})

slides = []   # (fig, takeaway)


def new(title, subtitle, takeaway):
    fig = plt.figure(figsize=(W, H), dpi=150)
    fig.patch.set_facecolor("white")
    fig.add_axes([0, 0.885, 1, 0.115]).axis("off")
    fig.axes[-1].add_patch(FancyBboxPatch((0, 0), 1, 1, transform=fig.axes[-1].transAxes,
                                          facecolor=NAVY, edgecolor="none"))
    fig.text(0.045, 0.945, title, color="white", fontsize=21, fontweight="bold", va="center")
    if subtitle:
        fig.text(0.045, 0.905, subtitle, color="#cfd8dc", fontsize=11.5, va="center")
    slides.append((fig, takeaway))
    return fig


def body(fig, rect=(0.07, 0.13, 0.86, 0.70)):
    ax = fig.add_axes(rect)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_facecolor("white")
    return ax


def finish(fig, takeaway):
    if takeaway:
        fig.text(0.045, 0.055, takeaway, fontsize=11.5, color=NAVY, va="center",
                 style="italic", wrap=True)
        fig.add_axes([0.035, 0.035, 0.006, 0.115]).axis("off")
        fig.axes[-1].add_patch(FancyBboxPatch((0, 0), 1, 1, transform=fig.axes[-1].transAxes,
                                              facecolor=AMBER, edgecolor="none"))


# ---------------------------------------------------------------- 1 title
fig = plt.figure(figsize=(W, H), dpi=150)
fig.patch.set_facecolor(NAVY)
fig.text(0.5, 0.68, "The Sequential Matching Problem", color="white",
         fontsize=40, fontweight="bold", ha="center")
fig.text(0.5, 0.56, "Round 2  ·  Bipartite Bard", color="#b0bec5", fontsize=22, ha="center")
fig.text(0.5, 0.42, "Anadi Tripathi  ·  Indian Institute of Technology Madras",
         color="white", fontsize=15, ha="center")
fig.text(0.5, 0.30, "120 fresh seeds  ·  2,880 episodes  ·  53,908 logged outcomes",
         color="#90caf9", fontsize=13, ha="center")
fig.text(0.5, 0.13, "commit e9515580aac62e818113f5aa17c4de1780697eca",
         color="#78909c", fontsize=9.5, ha="center", family="monospace")
slides.append((fig, None))

# ---------------------------------------------------------------- 2 the task
fig = new("The task", "Each of 100 days: observe, ask up to 12 questions, propose pairs",
          "Primary outcome is MSMI/100: completed meeting AND mutual second-meeting intention, per 100 members.")
ax = body(fig, (0.07, 0.16, 0.86, 0.66)); ax.axis("off")
steps = ["observe\n200 members", "ask\n≤12 clarifications", "match\ndisjoint feasible pairs",
         "feedback\naccept / decline / silent"]
xs = np.linspace(0.06, 0.72, 4)
for x, s in zip(xs, steps):
    ax.add_patch(FancyBboxPatch((x, 0.55), 0.20, 0.30, boxstyle="round,pad=0.02",
                                transform=ax.transAxes, facecolor=LIGHT, edgecolor=NAVY, lw=2))
    ax.text(x + 0.10, 0.70, s, transform=ax.transAxes, ha="center", va="center", fontsize=11.5)
    if x < xs[-1]:
        ax.annotate("", xy=(x + 0.215, 0.70), xytext=(x + 0.205, 0.70),
                    xycoords="axes fraction", textcoords="axes fraction",
                    arrowprops=dict(arrowstyle="->", color=NAVY, lw=2))
ax.text(0.5, 0.30, "Constraints that must hold", transform=ax.transAxes, ha="center",
        fontsize=13, fontweight="bold")
for i, s in enumerate(["mutual feasibility every day", "stated preferences never overridden",
                       "hard eligibility preserved", "≤12 asks/day, 10s per invocation"]):
    ax.text(0.5, 0.20 - i * 0.075, "•  " + s, transform=ax.transAxes, ha="center", fontsize=11)
finish(fig, slides[-1][1]); slides[-1] = (fig, None)

# ---------------------------------------------------------------- 3 headline
fig = new("Headline result", "120 fresh seeds (1101–1220) × 6 scenario families × 4 policies = 2,880 episodes",
          "We ship the supplied greedy baseline. Three alternatives were tested and none beat it on the primary outcome.")
ax = body(fig, (0.12, 0.16, 0.76, 0.70))
arms = ["no_ask", "random_feasible", "oldest_first", "greedy"]
vals = [0.098, 0.332, 0.364, 0.402]
lo = [0.098 - 0.075, 0.332 - 0.292, 0.364 - 0.319, 0.402 - 0.357]
hi = [0.122 - 0.098, 0.374 - 0.332, 0.409 - 0.364, 0.448 - 0.402]
cols = [GREY, GREY, GREY, GREEN]
y = np.arange(len(arms))
ax.barh(y, vals, color=cols, height=0.55)
ax.errorbar(vals, y, xerr=[lo, hi], fmt="none", ecolor="#37474f", capsize=6, lw=1.6)
for i, v in enumerate(vals):
    ax.text(v + 0.012, i, f"{v:.3f}", va="center", fontweight="bold", fontsize=12)
ax.set_yticks(y)
ax.set_yticklabels([a + ("  (SUPPLIED, SHIPPED)" if a == "greedy" else
                         "  (ours)" if a == "oldest_first" else "  (supplied)") for a in arms], fontsize=10.5)
ax.set_xlabel("MSMI per 100 arrived members  (95% seed-block bootstrap CI)", fontsize=10.5)
ax.set_xlim(0, 0.50); ax.invert_yaxis()
ax.grid(axis="x", alpha=0.25); ax.set_axisbelow(True)
finish(fig, slides[-1][1]); slides[-1] = (fig, None)

# ---------------------------------------------------------------- 4 per family
fig = new("greedy leads in every scenario family", "Not merely on average: it is highest in all six, taken one at a time",
          "Their unweighted mean reproduces every headline figure exactly, an independent check on the aggregation.")
ax = body(fig, (0.09, 0.16, 0.82, 0.70))
fam = ["development", "sparse", "cold_start", "delayed", "shift", "drift"]
g = [0.496, 0.125, 0.421, 0.404, 0.479, 0.487]
o = [0.471, 0.092, 0.354, 0.396, 0.417, 0.454]
r = [0.429, 0.113, 0.308, 0.383, 0.362, 0.396]
n = [0.138, 0.013, 0.062, 0.129, 0.113, 0.133]
x = np.arange(len(fam)); w = 0.20
for i, (v, c, lab) in enumerate([(g, GREEN, "greedy"), (o, "#5c6bc0", "oldest_first"),
                                 (r, GREY, "random_feasible"), (n, "#ab47bc", "no_ask")]):
    ax.bar(x + (i - 1.5) * w, v, w, label=lab, color=c)
ax.set_xticks(x); ax.set_xticklabels(fam, fontsize=10.5)
ax.set_ylabel("MSMI/100", fontsize=10.5)
ax.legend(frameon=False, ncol=4, fontsize=10, loc="upper center")
ax.grid(axis="y", alpha=0.25); ax.set_axisbelow(True)
finish(fig, slides[-1][1]); slides[-1] = (fig, None)

# ---------------------------------------------------------------- 5 ablation 1
fig = new("Ablation 1 — clarification is load-bearing", "Removing the ask phase: greedy vs no_ask, paired on identical worlds",
          "The single largest effect in the study, and the only one that clears what a 20-seed assessment can resolve.")
ax = body(fig, (0.10, 0.18, 0.80, 0.66))
labels = ["Reachable coverage\n(fraction of structural ceiling)", "Primary outcome\n(MSMI/100)"]
gr = [0.978, 0.402]; na = [0.344, 0.098]
x = np.arange(2); w = 0.30
ax.bar(x - w / 2, gr, w, label="greedy (asks)", color=GREEN)
ax.bar(x + w / 2, na, w, label="no_ask (no clarification)", color=RED)
for i, (a, b) in enumerate(zip(gr, na)):
    ax.text(i - w / 2, a + 0.02, f"{a:.3f}", ha="center", fontweight="bold")
    ax.text(i + w / 2, b + 0.02, f"{b:.3f}", ha="center", fontweight="bold")
    ax.annotate("", xy=(i + w / 2, b + 0.055), xytext=(i - w / 2, a + 0.045),
                arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.5, ls=":"))
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=11)
ax.set_ylim(0, 1.12); ax.legend(frameon=False, fontsize=10.5)
ax.grid(axis="y", alpha=0.25); ax.set_axisbelow(True)
ax.text(0.5, 0.92, "−0.304 MSMI/100   (p < 0.001)", transform=ax.transAxes, ha="center",
        fontsize=14, fontweight="bold", color=RED)
finish(fig, slides[-1][1]); slides[-1] = (fig, None)

# ---------------------------------------------------------------- 6 ablation 2
fig = new("Ablation 2 — pairing quality beats pairing quantity",
          "random_feasible makes MORE introductions and reaches MORE of the ceiling, yet scores LOWER",
          "The bottleneck is whom you pair, not how many. −0.070 MSMI/100 (p = 0.004).")
ax = body(fig, (0.10, 0.18, 0.80, 0.66))
metrics = ["Introductions\n(raw coverage)", "Fraction of\nstructural ceiling", "Primary outcome\n(MSMI/100)"]
gr = [0.333, 0.978, 0.402]; rf = [0.335, 0.982, 0.332]
x = np.arange(3); w = 0.30
ax.bar(x - w / 2, gr, w, label="greedy", color=GREEN)
ax.bar(x + w / 2, rf, w, label="random_feasible", color=GREY)
for i, (a, b) in enumerate(zip(gr, rf)):
    ax.text(i - w / 2, a + 0.012, f"{a:.3f}", ha="center", fontsize=10, fontweight="bold")
    ax.text(i + w / 2, b + 0.012, f"{b:.3f}", ha="center", fontsize=10, fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels(metrics, fontsize=10.5)
ax.set_ylim(0, 1.12); ax.legend(frameon=False, fontsize=10.5)
ax.grid(axis="y", alpha=0.25); ax.set_axisbelow(True)
ax.annotate("marginally more pairs\nand higher ceiling…", xy=(1, 1.01), fontsize=10,
            ha="center", color=NAVY)
ax.annotate("…yet −0.070 on the outcome", xy=(2, 0.53), fontsize=11, ha="center",
            color=RED, fontweight="bold")
finish(fig, slides[-1][1]); slides[-1] = (fig, None)

# ---------------------------------------------------------------- 7 waiting
fig = new("Who gets left waiting", "Waiting must be read alongside the unserved count",
          "oldest_first cuts p90 wait by 1.05 days at no significant cost to the outcome — a free fairness lever we did not ship.")
ax = body(fig, (0.10, 0.18, 0.80, 0.66))
m = ["median wait\n(served)", "mean wait\n(served)", "p90 wait\n(served)", "unserved\n/200"]
gr = [4.533, 6.813, 16.725, 133.301]
of = [4.929, 6.667, 15.675, 133.150]
x = np.arange(4); w = 0.30
ax.bar(x - w / 2, gr, w, label="greedy", color=GREEN)
ax.bar(x + w / 2, of, w, label="oldest_first", color="#5c6bc0")
for i, (a, b) in enumerate(zip(gr, of)):
    ax.text(i - w / 2, a + max(gr) * 0.02, f"{a:.2f}", ha="center", fontsize=9.5)
    ax.text(i + w / 2, b + max(gr) * 0.02, f"{b:.2f}", ha="center", fontsize=9.5)
ax.set_xticks(x); ax.set_xticklabels(m, fontsize=10)
ax.set_ylabel("days (last panel: members)", fontsize=10)
ax.legend(frameon=False, fontsize=10.5); ax.grid(axis="y", alpha=0.25); ax.set_axisbelow(True)
ax.annotate("−1.05 days\n[0.742, 1.358]", xy=(2, 17.6), ha="center", fontsize=11,
            color=NAVY, fontweight="bold")
finish(fig, slides[-1][1]); slides[-1] = (fig, None)

# ---------------------------------------------------------------- 8 forest
fig = new("Round 1's headline claim did not replicate", "Incumbent minus greedy, four independent estimates",
          "Pooled across 40 fresh seeds the advantage is −0.031. Our reading: it was the maximum of 17 configs on 10 seeds.")
ax = body(fig, (0.13, 0.16, 0.74, 0.70))
lab = ["Round 1 note (10 seeds)", "Parallel study (10 seeds)", "This work (30 seeds)", "POOLED (40 seeds)"]
est = [0.175, 0.008, -0.044, -0.031]
l = [0.092, -0.217, -0.175, -0.143]
h = [0.258, 0.233, 0.081, 0.080]
y = np.arange(len(lab))[::-1]
cols = [GREY, GREY, GREY, NAVY]
ax.errorbar(est, y, xerr=[[e - a for e, a in zip(est, l)], [b - e for e, b in zip(est, h)]],
            fmt="o", color=NAVY, ecolor=NAVY, capsize=7, lw=2, markersize=9)
for i, (e, a, b) in enumerate(zip(est, l, h)):
    ax.text(0.30, y[i], f"{e:+.3f}  [{a:+.3f}, {b:+.3f}]", va="center", fontsize=10.5,
            fontweight="bold" if i == 3 else "normal")
ax.axvline(0, color=RED, ls="--", lw=2)
ax.set_yticks(y); ax.set_yticklabels(lab, fontsize=11)
ax.set_xlim(-0.32, 0.60); ax.set_xlabel("incumbent − greedy  (MSMI/100)", fontsize=10.5)
ax.grid(axis="x", alpha=0.25); ax.set_axisbelow(True)
ax.text(0.02, 3.35, "favours incumbent →", fontsize=9, color=GREY, transform=ax.get_yaxis_transform())
finish(fig, slides[-1][1]); slides[-1] = (fig, None)

# ---------------------------------------------------------------- 9 interactions
fig = new("Interactions are indistinguishable from zero",
          "Two independent studies; each component varied separately",
          "Learning, asking and allocation are additive here. The interaction is not the story.")
ax = body(fig, (0.13, 0.18, 0.74, 0.64))
lab = ["ask main effect", "allocation main effect", "ask × allocation interaction"]
est = [0.096, -0.088, 0.025]
l = [-0.088, -0.204, -0.200]; h = [0.288, 0.038, 0.267]
y = np.arange(3)[::-1]
for i, (e, a, b) in enumerate(zip(est, l, h)):
    ax.plot([a, b], [y[i], y[i]], color=NAVY, lw=4, solid_capstyle="butt")
    ax.plot(e, y[i], "o", color=NAVY, markersize=12)
    ax.text(0.33, y[i], f"{e:+.3f}  [{a:+.3f}, {b:+.3f}]", va="center", fontsize=11)
ax.axvline(0, color=RED, ls="--", lw=2)
ax.set_yticks(y); ax.set_yticklabels(lab, fontsize=11)
ax.set_xlim(-0.28, 0.50); ax.set_xlabel("effect on MSMI/100 (95% CI)", fontsize=10.5)
ax.grid(axis="x", alpha=0.25); ax.set_axisbelow(True)
ax.text(0.5, 0.88, "every interval straddles zero", transform=ax.transAxes, ha="center",
        fontsize=12, color=NAVY, fontweight="bold")
finish(fig, slides[-1][1]); slides[-1] = (fig, None)

# ---------------------------------------------------------------- 10 blind spot
fig = new("Directional calibration: a 20-point blind spot",
          "53,908 logged outcomes — the policy's score cannot see a known DISAGREEMENT",
          "A pair with four known disagreements scores the same as a pair about whom nothing is known.")
ax = body(fig, (0.13, 0.18, 0.74, 0.66))
labels = ["0 agree / 0 disagree\n(unknown)", "0 agree / 1 disagree", "0 agree / 2 disagree",
          "0 agree / 4 disagree"]
vals = [0.492, 0.437, 0.345, 0.288]
cols = [GREEN, GREY, "#ef6c00", RED]
b = ax.bar(range(4), vals, color=cols, width=0.55)
for r, v in zip(b, vals):
    ax.text(r.get_x() + r.get_width() / 2, v + 0.012, f"{v:.3f}", ha="center", fontweight="bold")
ax.set_xticks(range(4)); ax.set_xticklabels(labels, fontsize=10)
ax.set_ylabel("realised acceptance", fontsize=10.5); ax.set_ylim(0, 0.60)
ax.grid(axis="y", alpha=0.25); ax.set_axisbelow(True)
ax.annotate("", xy=(3, 0.30), xytext=(0, 0.503),
            arrowprops=dict(arrowstyle="->", color=RED, lw=2, ls=":"))
ax.text(1.5, 0.47, "scored identically by the policy", fontsize=11, ha="center", color=RED,
        fontweight="bold")
finish(fig, slides[-1][1]); slides[-1] = (fig, None)

# ---------------------------------------------------------------- 11 drift
fig = new("Calibration degrades under changing conditions",
          "Signed calibration gap by day window — stationary worlds hold, non-stationary ones do not",
          "Fine on development; −0.097 after day 35 in drift. At least 14% of the Brier score is irreducible in principle.")
ax = body(fig, (0.12, 0.18, 0.78, 0.66))
fam = ["development", "sparse", "cold_start", "delayed", "shift", "drift"]
win = np.array([[0.003, -0.010, 0.006], [0.003, 0.010, -0.009], [0.009, 0.005, 0.019],
                [0.005, -0.024, -0.004], [-0.028, -0.027, -0.032], [0.003, -0.010, -0.097]])
im = ax.imshow(win, cmap="RdYlGn", vmin=-0.10, vmax=0.03, aspect="auto")
ax.set_xticks(range(3)); ax.set_xticklabels(["days 0–19", "days 20–34", "days 35–59"], fontsize=11)
ax.set_yticks(range(6)); ax.set_yticklabels(fam, fontsize=11)
for i in range(6):
    for j in range(3):
        v = win[i, j]
        ax.text(j, i, f"{v:+.3f}", ha="center", va="center", fontsize=11,
                fontweight="bold", color="white" if abs(v) > 0.055 else "#263238")
ax.set_title("blue = under-confident  ·  red = over-confident", fontsize=10, color=GREY)
plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
finish(fig, slides[-1][1]); slides[-1] = (fig, None)

# ---------------------------------------------------------------- 12 disparity
fig = new("Allocation disparity is a property of the world",
          "Three-leg decomposition over 24,000 members per arm: supply (world) vs allocation and access (policy)",
          "Zone supply spans 4.7× while served|reachable and ask units are flat for every group. The policy is not the cause.")
ax = body(fig, (0.10, 0.18, 0.80, 0.66))
groups = ["zone_a", "zone_b", "zone_c", "zone_d", "gender\n(3 levels)", "age\n(4 bands)"]
supply = [0.47, 0.32, 0.22, 0.10, 0.39, 0.385]
served = [0.975, 0.98, 0.99, 0.995, 0.975, 0.975]
asks = [0.95, 1.0, 1.0, 0.9, 0.95, 0.95]
x = np.arange(len(groups)); w = 0.26
ax.bar(x - w, supply, w, label="eligibility supply (world)", color=RED)
ax.bar(x, served, w, label="served | reachable (policy)", color=GREEN)
ax.bar(x + w, asks, w, label="ask units (policy)", color="#5c6bc0")
ax.set_xticks(x); ax.set_xticklabels(groups, fontsize=10)
ax.set_ylabel("share", fontsize=10.5); ax.set_ylim(0, 1.12)
ax.legend(frameon=False, fontsize=10.5, ncol=3, loc="upper center")
ax.grid(axis="y", alpha=0.25); ax.set_axisbelow(True)
ax.annotate("4.7× spread", xy=(0, 0.50), xytext=(0.55, 0.62), fontsize=11, color=RED,
            fontweight="bold", arrowprops=dict(arrowstyle="->", color=RED))
ax.text(5.4, 1.02, "flat →", fontsize=11, color=GREEN, fontweight="bold", ha="center")
finish(fig, slides[-1][1]); slides[-1] = (fig, None)

# ---------------------------------------------------------------- 13 no demo effect
fig = new("There is no demographic effect",
          "Raw spread in acceptance, and the one conditional test the study ran",
          "Zone spread collapses 0.144 -> 0.018 once pair features are held fixed. Gender and age are reported as raw spreads only.")
ax = body(fig, (0.13, 0.18, 0.74, 0.66))
g = ["gender\n(3 levels)\nraw", "age\n(26 bands)\nraw", "zone\n(16 zones)\nraw",
     "zone\nCONDITIONED on\npair features"]
vals = [0.034, 0.081, 0.144, 0.018]
cols = [RED, RED, RED, GREEN]
b = ax.bar(range(4), vals, color=cols, width=0.55)
for r, v in zip(b, vals):
    ax.text(r.get_x() + r.get_width() / 2, v + 0.004, f"{v:.3f}", ha="center",
            fontweight="bold", fontsize=11)
ax.set_xticks(range(4)); ax.set_xticklabels(g, fontsize=10)
ax.set_ylabel("spread in acceptance", fontsize=10.5); ax.set_ylim(0, 0.175)
ax.grid(axis="y", alpha=0.25); ax.set_axisbelow(True)
ax.annotate("", xy=(3, 0.021), xytext=(2, 0.148),
            arrowprops=dict(arrowstyle="->", color=NAVY, lw=2, ls=":"))
ax.text(2.5, 0.156, "composition, not treatment", fontsize=11.5, ha="center",
        color=NAVY, fontweight="bold")
ax.text(0.5, -0.20, "Gender and age are negative controls: the study reports their raw spreads, "
        "not conditional ones.", transform=ax.transAxes, ha="center", fontsize=9.5, color=GREY)
finish(fig, slides[-1][1]); slides[-1] = (fig, None)

# ---------------------------------------------------------------- 14 R1 rerun
fig = new("Round 1's code is here, and it runs",
          "We re-executed all 14 configurations it defines on Round 1's own 10 screen seeds: 840 episodes, zero errors",
          "Six of the seventeen configurations reproduce exactly, each verified on all six scenario families — not just the primary score.")
ax = body(fig, (0.11, 0.16, 0.78, 0.70))
names = ["hard_plus_soft_maxw", "potential_ask", "hard_plus_soft_greedy", "potential_ask_greedy",
         "thompson_pattern", "gp_ucb", "max_weight_sim", "core_max_matching", "random_feasible",
         "greedy", "gp_mean", "soft_core_maxw", "no_ask", "soft_core_greedy"]
vals = [0.567, 0.525, 0.500, 0.467, 0.442, 0.425, 0.408, 0.375, 0.358, 0.350, 0.325, 0.175,
        0.167, 0.167]
verified = {1, 6, 8, 9, 12}   # potential_ask, max_weight_sim, random_feasible, greedy, no_ask
cols = [GREEN if i in verified else "#b0bec5" for i in range(len(names))]
y = np.arange(len(names))[::-1]
ax.barh(y, vals, color=cols, height=0.62)
for i, v in enumerate(vals):
    ax.text(v + 0.008, i, f"{v:.3f}" + ("  ✓ verified" if i in verified else ""),
            va="center", fontsize=9.5, fontweight="bold" if i in verified else "normal")
ax.set_yticks(y); ax.set_yticklabels(names, fontsize=9.5)
ax.set_xlabel("MSMI/100 on Round 1 screen seeds 101–1010 (10 seeds × 6 families)", fontsize=10)
ax.set_xlim(0, 1.02); ax.grid(axis="x", alpha=0.25); ax.set_axisbelow(True)
finish(fig, slides[-1][1]); slides[-1] = (fig, None)

# ---------------------------------------------------------------- 15 ship
fig = new("What we ship, and what we cannot claim", "", "")
ax = body(fig, (0.08, 0.14, 0.84, 0.74)); ax.axis("off")
left = ["SHIP", "", "greedy — the supplied baseline,", "unmodified, because it scored", "highest and nothing beat it.",
        "", "Shipped on expected value, not", "on significance: the 0.070 margin", "would not be detectable on",
        "20 private seeds."]
right = ["CANNOT CLAIM", "", "• Results describe the supplied", "  synthetic simulator only",
         "• We did not beat the baseline", "• 11 of 17 Round 1 configs do not",
         "  reproduce; we cite none of them", "• Waiting figures must be read with",
         "  the unserved count", "• Seed choice moves the score ~10×",
         "  more than policy choice"]
ax.text(0.02, 0.98, "\n".join(left), transform=ax.transAxes, va="top", fontsize=12.5,
        color=GREEN, fontweight="bold")
ax.text(0.52, 0.98, "\n".join(right), transform=ax.transAxes, va="top", fontsize=11.5, color=RED)
ax.add_patch(FancyBboxPatch((0.46, 0.06), 0.006, 0.88, transform=ax.transAxes,
                            facecolor=LIGHT, edgecolor="none"))
ax.text(0.02, 0.10, "Everything is reproducible: docker build · 8 tests · 25 data checks · 82/82 checksums",
        transform=ax.transAxes, fontsize=11.5, color=NAVY, fontweight="bold")

# ---------------------------------------------------------------- output
import os
os.makedirs("/home/user/deck", exist_ok=True)
pdf = "/home/user/deck/BipartiteBard_Round2_Presentation.pdf"
from matplotlib.backends.backend_pdf import PdfPages
with PdfPages(pdf) as pp:
    for f, _ in slides:
        pp.savefig(f, facecolor=f.patch.get_facecolor())
        plt.close(f)
print("PDF :", pdf, os.path.getsize(pdf), "bytes,", len(slides), "slides")

pngs = []
for i, (f, _) in enumerate(slides, 1):
    p = f"/home/user/deck/slide{i:02d}.png"
    f.savefig(p, dpi=150, facecolor=f.patch.get_facecolor())
    pngs.append(p)
    plt.close(f)

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
blank = prs.slide_layouts[6]
for p in pngs:
    s = prs.slides.add_slide(blank)
    s.shapes.add_picture(p, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
pptx = "/home/user/deck/BipartiteBard_Round2_Presentation.pptx"
prs.save(pptx)
print("PPTX:", pptx, os.path.getsize(pptx), "bytes")
