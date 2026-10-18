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

# episode-level family score, split by block
val = {}   # (arm, block, variant) -> list
for r in rows:
    blk = "A" if int(r["seed"]) <= 1130 else "B"
    val.setdefault((r["arm"], blk, r["variant"]), []).append(r["metrics"]["msmi_per_100_arrived_members"])

# greedy block A per-family comes from g30 summary (30 seeds); DA block A from episodes
def fam_pooled(arm):
    out = {}
    for v in VARIANTS:
        a30 = g30[arm]["family"][v] if arm in g30 else None
        a90 = st.fmean(val[(arm, "B", v)])
        b30 = st.fmean(val[(arm, "A", v)]) if (arm, "A", v) in val else None
        if a30 is not None:
            out[v] = (30 * a30 + 90 * a90) / 120
        elif b30 is not None:
            out[v] = (30 * b30 + 90 * a90) / 120
        else:
            out[v] = a90
    return out


print("=== POOLED PER-FAMILY, 120 seeds (both arms n=120) ===")
g = fam_pooled("greedy")
d = fam_pooled("disagreement_aware")
p = fam_pooled("potential_ask_greedy")
print(f"{'family':13s} {'greedy':>8s} {'disagr_aware':>13s} {'delta':>8s} {'pag':>8s}")
wins = 0
for v in VARIANTS:
    delta = d[v] - g[v]
    wins += delta > 0
    print(f"{v:13s} {g[v]:8.4f} {d[v]:13.4f} {delta:+8.4f} {p[v]:8.4f}")
print(f"\ndisagreement_aware ahead on {wins}/6 families")
print(f"unweighted mean of family means: greedy={st.fmean([g[v] for v in VARIANTS]):.4f}  disagr={st.fmean([d[v] for v in VARIANTS]):.4f}")

# paired per-seed, per-family sign test (only block B has episode-level for both? no: DA has both blocks)
print("\n=== paired per-seed per-family sign test (120 seeds) ===")
psf = {}
for r in rows:
    psf[(r["arm"], int(r["seed"]), r["variant"])] = r["metrics"]["msmi_per_100_arrived_members"]
for v in VARIANTS:
    diffs = []
    for s in list(range(1101, 1131)) + list(range(1131, 1221)):
        key_g = ("greedy", s, v)
        key_d = ("disagreement_aware", s, v)
        if key_g in psf and key_d in psf:
            diffs.append(psf[key_d] - psf[key_g])
    w = sum(1 for x in diffs if x > 0); l = sum(1 for x in diffs if x < 0); t = len(diffs) - w - l
    print(f"  {v:13s} n={len(diffs):3d}  diff={st.fmean(diffs):+.4f}  DA ahead {w}/{t}/{l}")

# block-level stability of the DA effect
print("\n=== DA - greedy, block by block (15-seed chunks) ===")
for lo in range(1131, 1221, 15):
    ss = list(range(lo, min(lo + 15, 1221)))
    diffs = [psf[("disagreement_aware", s, v)] - psf[("greedy", s, v)]
             for s in ss for v in VARIANTS if ("disagreement_aware", s, v) in psf and ("greedy", s, v) in psf]
    print(f"  seeds {lo}-{min(lo+14,1220)}: {st.fmean(diffs):+.4f}")
ss = list(range(1101, 1131))
diffs = [psf[("disagreement_aware", s, v)] - psf[("greedy", s, v)]
         for s in ss for v in VARIANTS if ("disagreement_aware", s, v) in psf and ("greedy", s, v) in psf]
print(f"  seeds 1101-1130: {st.fmean(diffs):+.4f}")

# how big would the effect have to be, and what does the mechanism predict?
print("\n=== power: what could we have detected at 120 seeds? ===")
alldiff = [psf[("disagreement_aware", s, v)] - psf[("greedy", s, v)]
           for s in list(range(1101, 1131)) + list(range(1131, 1221)) for v in VARIANTS
           if ("disagreement_aware", s, v) in psf and ("greedy", s, v) in psf]
# per-seed primary-level diff
prim = {}
for arm in ("greedy", "disagreement_aware"):
    for s in list(range(1101, 1131)) + list(range(1131, 1221)):
        vals = [psf.get((arm, s, v)) for v in VARIANTS]
        if all(x is not None for x in vals):
            prim.setdefault(arm, {})[s] = st.fmean(vals)
dd = [prim["disagreement_aware"][s] - prim["greedy"][s] for s in sorted(prim["greedy"]) if s in prim["disagreement_aware"]]
sd = st.stdev(dd); n = len(dd); se = sd / math.sqrt(n)
print(f"  per-seed primary diff: mean={st.fmean(dd):+.4f}  SD={sd:.4f}  SE={se:.4f}  n={n}")
print(f"  95% CI = [{st.fmean(dd)-1.96*se:+.4f}, {st.fmean(dd)+1.96*se:+.4f}]")
print(f"  minimum detectable effect (80% power, 5%) ~ {2.8*se:.4f}")
