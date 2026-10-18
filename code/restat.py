"""Recompute every p-value and W/T/L that this project generated itself.

The earlier helper had a defect: it computed `order = sorted(...)` and then
never used it, so signed-rank `rank` values were assigned by position in the
UNSORTED difference array. p-values were therefore meaningless. This module
implements the test correctly and is the single source of truth from here on.
"""
import glob, gzip, json, math, os, random, statistics as st
from collections import Counter

VARIANTS = ("development", "sparse", "cold_start", "delayed", "shift", "drift")
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Tie rule, stated once: per-seed primary scores are rationals with denominator
# 12 (mean of six per-100 scores, each a multiple of 0.5 on 200 members).
# Two arms TIE on a seed iff their scores are equal to within 1e-9, which is
# exact for these quantities and immune to float representation noise.
TIE = 1e-9


def wilcoxon_signed_rank(d):
    """Two-sided Wilcoxon signed-rank p (normal approx, tie-corrected)."""
    d = [x for x in d if abs(x) > TIE]
    n = len(d)
    if n == 0:
        return float("nan"), 0.0
    # rank |d| ascending; average ranks within tie groups
    idx = sorted(range(n), key=lambda i: abs(d[i]))
    rank = [0.0] * n
    i = 0
    tie_term = 0.0
    while i < n:
        j = i
        while j + 1 < n and abs(abs(d[idx[j + 1]]) - abs(d[idx[i]])) < TIE:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            rank[idx[k]] = avg
        t = j - i + 1
        tie_term += t ** 3 - t
        i = j + 1
    Wp = sum(rank[i] for i in range(n) if d[i] > 0)
    Wm = sum(rank[i] for i in range(n) if d[i] < 0)
    mu = n * (n + 1) / 4.0
    sd = math.sqrt((n * (n + 1) * (2 * n + 1) - tie_term / 2.0) / 24.0)
    if sd == 0:
        return 1.0, Wp
    z = (Wp - mu) / sd
    p = math.erfc(abs(z) / math.sqrt(2.0))
    return p, Wp, Wm, z


def wtl(d):
    w = sum(1 for x in d if x > TIE)
    l = sum(1 for x in d if x < -TIE)
    return w, len(d) - w - l, l


def boot_ci(d, B=50000, seed=7):
    rnd = random.Random(seed)
    n = len(d)
    o = []
    for _ in range(B):
        o.append(sum(d[rnd.randrange(n)] for _ in range(n)) / n)
    o.sort()
    return o[int(.025 * B)], o[int(.975 * B)]


def contrast(a, b, seeds, B=50000, seed=7):
    """a - b. W/T/L reported from a's perspective."""
    d = [a[s] - b[s] for s in seeds]
    m = st.fmean(d)
    sd = st.stdev(d)
    se = sd / math.sqrt(len(d))
    lo, hi = boot_ci(d, B, seed)
    p, *rest = wilcoxon_signed_rank(d)
    w, t, l = wtl(d)
    return dict(n=len(d), diff=round(m, 4), ci_lo=round(lo, 4), ci_hi=round(hi, 4),
                se=round(se, 4), sd=round(sd, 4), p=round(p, 4), w=w, t=t, l=l,
                rng=[round(min(d), 4), round(max(d), 4)])


# ---------------------------------------------------------------- load data
def load(pat):
    rows = []
    for f in sorted(glob.glob(pat)):
        op = gzip.open if f.endswith(".gz") else open
        with op(f, "rt") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                if r.get("valid") is False or not r.get("metrics"):
                    continue
                rows.append(r)
    return rows


raw = load(R + "/results/raw_episodes/*.jsonl.gz")
g30 = json.load(open(R + "/results/analysis_30seeds_900ep.json"))["summary"]

# per-seed primary from raw episodes (blocks A and B)
sf = {}
for r in raw:
    sf.setdefault((r["arm"], int(r["seed"])), {})[r["variant"]] = r["metrics"]["msmi_per_100_arrived_members"]
# greedy block A comes from the VM aggregate (no raw rows survive)
PS = {}
for a in ("greedy", "potential_ask", "potential_ask_greedy", "disagreement_aware"):
    d = {int(k): round(v, 10) for k, v in g30[a]["per_seed"].items()} if a in g30 else {}
    for (arm, s), fam in sf.items():
        if arm == a and len(fam) == 6:
            d[s] = round(sum(fam.values()) / 6, 12)
    PS[a] = d

SEEDS = sorted(PS["greedy"])
assert len(SEEDS) == 120

print("=" * 78)
print("SECTION 5.15 / 5.14 — 120 seeds, paired, diff = arm - greedy")
print("W/T/L counts seeds the ARM wins / ties / loses.  Tie rule: |diff| <= 1e-9.")
print("=" * 78)
print(f"{'arm':24s} {'score':>7s} {'diff':>8s} {'95% CI':>18s} {'p':>7s} {'W/T/L(arm)':>14s}")
res = {}
for a in ("disagreement_aware", "potential_ask", "potential_ask_greedy"):
    c = contrast(PS[a], PS["greedy"], SEEDS)
    res[a] = c
    g = st.fmean([PS["greedy"][s] for s in SEEDS])
    print(f"{a:24s} {st.fmean([PS[a][s] for s in SEEDS]):7.4f} {c['diff']:+8.4f} "
          f"[{c['ci_lo']:+.4f},{c['ci_hi']:+.4f}] {c['p']:7.4f} {c['w']}/{c['t']}/{c['l']}")
print(f"{'greedy':24s} {st.fmean([PS['greedy'][s] for s in SEEDS]):7.4f}")

print()
print("=" * 78)
print("SECTION 5.13 — 30 seeds (1101-1130), diff = arm - greedy")
print("=" * 78)
print(f"{'arm':24s} {'score':>7s} {'diff':>8s} {'95% CI':>18s} {'p':>7s} {'W/T/L(arm)':>14s}")
r13 = {}
gA = {int(k): round(v, 10) for k, v in g30["greedy"]["per_seed"].items()}
for a in ("potential_ask_greedy", "potential_ask", "oldest_first", "waitfloor"):
    if a not in g30:
        continue
    d = {int(k): round(v, 10) for k, v in g30[a]["per_seed"].items()}
    ss = sorted(set(d) & set(gA))
    c = contrast(d, gA, ss, 20000, 5)
    r13[a] = c
    print(f"{a:24s} {st.fmean([d[s] for s in ss]):7.4f} {c['diff']:+8.4f} "
          f"[{c['ci_lo']:+.4f},{c['ci_hi']:+.4f}] {c['p']:7.4f} {c['w']}/{c['t']}/{c['l']}")

d1 = {s: PS["potential_ask_greedy"][s] for s in PS["potential_ask_greedy"] if s <= 1130}
ss = sorted(set(d1) & set(gA))
c = contrast(d1, gA, ss, 20000, 5)
r13["potential_ask_greedy"] = c
print(f"{'potential_ask_greedy':24s} {st.fmean([d1[s] for s in ss]):7.4f} {c['diff']:+8.4f} "
      f"[{c['ci_lo']:+.4f},{c['ci_hi']:+.4f}] {c['p']:7.4f} {c['w']}/{c['t']}/{c['l']}")

print()
print("=" * 78)
print("matcher effect isolated (potential_ask_greedy - potential_ask), 30 seeds")
print("=" * 78)
d1 = {s: PS["potential_ask_greedy"][s] for s in PS["potential_ask_greedy"] if s <= 1130}
d2 = {s: round(v, 10) for s, v in
      ((int(k), v) for k, v in g30["potential_ask"]["per_seed"].items())}
c = contrast(d1, d2, sorted(set(d1) & set(d2)), 20000, 5)
print(f"  diff={c['diff']:+.4f} [{c['ci_lo']:+.4f},{c['ci_hi']:+.4f}] p={c['p']} W/T/L={c['w']}/{c['t']}/{c['l']}")

json.dump({"sections_5_14_5_15_120seeds": res, "section_5_13_30seeds": r13,
           "matcher_isolated_30seeds": c,
           "method": "two-sided Wilcoxon signed-rank, normal approximation with "
                     "tie correction on averaged |diff| ranks; seed-block bootstrap "
                     "50,000 resamples for CIs; tie rule |diff| <= 1e-9"},
          open(os.path.join(R, "results", "restat_out.json"), "w"), indent=2)
print("\nwrote", os.path.join(R, "results", "restat_out.json"))
