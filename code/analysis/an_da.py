import json, glob, gzip, math, random, statistics as st

VARIANTS = ("development", "sparse", "cold_start", "delayed", "shift", "drift")


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


rows = (load("/home/user/out_da/k*/episodes.jsonl.gz")
        + load("/home/user/out_90/c*/episodes.jsonl.gz")
        + load("/home/user/out_pag/episodes.jsonl.gz"))
g30 = json.load(open("/home/user/github_repo/bipartite-bard-round2/results/analysis_30seeds_900ep.json"))["summary"]

sf = {}
for r in rows:
    sf.setdefault((r["arm"], int(r["seed"])), {})[r["variant"]] = r["metrics"]["msmi_per_100_arrived_members"]

ARMS = ["greedy", "potential_ask", "potential_ask_greedy", "disagreement_aware"]


def per_seed(a):
    d = {}
    if a in g30 and "per_seed" in g30[a]:
        d = {int(k): v for k, v in g30[a]["per_seed"].items()}
    for (arm, s), fam in sf.items():
        if arm == a and len(fam) == 6:
            d[s] = sum(fam.values()) / 6
    return d


PS = {a: per_seed(a) for a in ARMS}
for a in ARMS:
    print(f"{a:22s} n_seeds={len(PS[a]):3d}  (1101-1130: {sum(1 for s in PS[a] if s<=1130)}, 1131-1220: {sum(1 for s in PS[a] if s>=1131)})")

SEEDS = sorted(PS["greedy"])
assert len(SEEDS) == 120
for a in ARMS:
    missing = [s for s in SEEDS if s not in PS[a]]
    if missing:
        print("!! MISSING", a, missing[:10], "count", len(missing))


def boot(v, B=50000, seed=7):
    rnd = random.Random(seed); n = len(v); o = []
    for _ in range(B):
        o.append(sum(v[rnd.randrange(n)] for _ in range(n)) / n)
    o.sort()
    return round(o[int(.025 * B)], 4), round(o[int(.975 * B)], 4)


def wilcoxon(d):
    d = [x for x in d if abs(x) > 1e-12]
    n = len(d)
    order = sorted(range(n), key=lambda i: abs(d[i]))
    rank = [0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(abs(d[j + 1]) - abs(d[i])) < 1e-12:
            j += 1
        for k in range(i, j + 1):
            rank[k] = (i + j) / 2 + 1
        i = j + 1
    W = min(sum(rank[i] for i in range(n) if d[i] > 0), sum(rank[i] for i in range(n) if d[i] < 0))
    mu = n * (n + 1) / 4; sd = math.sqrt(n * (n + 1) * (2 * n + 1) / 24)
    return round(math.erfc(abs((W - mu) / sd) / math.sqrt(2)), 4), sum(1 for x in d if x > 0), sum(1 for x in d if x < 0)


def contrast(a, b, seeds, B=50000, seed=7):
    d = [a[s] - b[s] for s in seeds]
    m = st.fmean(d); sd = st.stdev(d); se = sd / math.sqrt(len(d))
    lo, hi = boot(d, B, seed)
    p, w, l = wilcoxon(d)
    return dict(n=len(d), diff=round(m, 4), ci_lo=lo, ci_hi=hi, se=round(se, 4),
                sd=round(sd, 4), p=p, w=w, t=len(d) - w - l, l=l,
                rng=[round(min(d), 4), round(max(d), 4)])


print("\n=== 120-SEED PRIMARY (1101-1220) ===")
for a in ARMS:
    v = [PS[a][s] for s in SEEDS]
    lo, hi = boot(v, 50000, 12)
    print(f"{a:22s} {st.fmean(v):.4f}  [{lo:.3f}, {hi:.3f}]  SD={st.stdev(v):.3f}")

print("\n=== PAIRED CONTRASTS vs greedy, 120 seeds ===")
for a in ARMS[1:]:
    c = contrast(PS["greedy"], PS[a], SEEDS)
    ga = st.fmean([PS["greedy"][s] for s in SEEDS]); aa = st.fmean([PS[a][s] for s in SEEDS])
    print(f"greedy - {a:20s} {c['diff']:+.4f} [{c['ci_lo']:+.4f},{c['ci_hi']:+.4f}] se={c['se']:.4f} p={c['p']} W/T/L={c['w']}/{c['t']}/{c['l']}   ({ga:.3f} vs {aa:.3f})")

print("\n=== consistency across seed blocks ===")
for a in ARMS[1:]:
    for lab, (lo_, hi_) in (("1101-1130", (1101, 1130)), ("1131-1220", (1131, 1220))):
        ss = [s for s in SEEDS if lo_ <= s <= hi_]
        c = contrast(PS["greedy"], PS[a], ss, 20000, 5)
        print(f"  {a:20s} {lab}  n={c['n']:3d}  diff={c['diff']:+.4f} [{c['ci_lo']:+.4f},{c['ci_hi']:+.4f}]  p={c['p']}")

print("\n=== disagreement_aware vs greedy: per family (120 seeds) ===")
fam = {a: {} for a in ARMS}
for (arm, s), f in sf.items():
    for v in VARIANTS:
        if v in f:
            fam[arm].setdefault(v, []).append(f[v])
for v in VARIANTS:
    line = f"  {v:12s}"
    for a in ("greedy", "disagreement_aware"):
        line += f"  {a}={st.fmean(fam[a][v]):.4f} (n={len(fam[a][v])})"
    print(line)

print("\n=== headline stats, 1131-1220 block (90 seeds) ===")
for a in ARMS:
    sub = [r for r in rows if r["arm"] == a and int(r["seed"]) >= 1131]
    if not sub:
        continue
    print(f"  {a:22s} n_ep={len(sub):3d} events={sum(r['metrics']['mutual_second_meeting_intention'] for r in sub):4d} "
          f"cov={st.fmean([r['metrics']['coverage'] for r in sub]):.3f} "
          f"ask={st.fmean([r['metrics']['ask_cost'] for r in sub]):.1f} "
          f"unserved={st.fmean([r['metrics']['unserved_members'] for r in sub]):.1f}")

out = dict(generated="2026-10-15",
           arms={a: {str(k): round(v, 6) for k, v in sorted(PS[a].items())} for a in ARMS},
           contrasts_vs_greedy={a: contrast(PS["greedy"], PS[a], SEEDS) for a in ARMS[1:]})
json.dump(out, open("/home/user/out_da/analysis_120seeds.json", "w"), indent=1)
print("\nwrote /home/user/out_da/analysis_120seeds.json")
