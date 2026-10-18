import json, glob, math, random, statistics as st
from collections import defaultdict

VARIANTS=("development","sparse","cold_start","delayed","shift","drift")
def load(pat):
    rows=[]
    for f in sorted(glob.glob(pat)):
        for line in open(f):
            line=line.strip()
            if not line: continue
            r=json.loads(line)
            if r.get("valid") is False or not r.get("metrics"): continue
            rows.append(r)
    return rows

rows = load("/home/user/out_90/c*/episodes.jsonl")
print("valid episodes:", len(rows))
bad = sum(1 for f in glob.glob("/home/user/out_90/c*/episodes.jsonl") for line in open(f) if line.strip() and (json.loads(line).get("valid") is False or not json.loads(line).get("metrics")))
print("invalid episodes:", bad)

seedfam=defaultdict(dict)   # (arm,seed) -> {variant: msmi}
agg=defaultdict(lambda: defaultdict(list))
for r in rows:
    arm=r["arm"]; s=int(r["seed"]); v=r["variant"]; m=r["metrics"]
    seedfam[(arm,s)][v]=m["msmi_per_100_arrived_members"]
    agg[arm]["events"].append(m["mutual_second_meeting_intention"])
    agg[arm]["cov"].append(m["coverage"])
    agg[arm]["ask"].append(m["ask_cost"])
    agg[arm]["unserved"].append(m["unserved_members"])
    agg[arm]["ma"].append(m["mutual_acceptances"])

arms=sorted({r["arm"] for r in rows})
seeds=sorted({int(r["seed"]) for r in rows})
print("arms:",arms,"seeds:",len(seeds),seeds[0],seeds[-1])
complete={a:[s for s in seeds if len(seedfam[(a,s)])==6] for a in arms}
for a in arms: print(a,"complete seeds:",len(complete[a]))

per_seed={a:{s: sum(seedfam[(a,s)].values())/6 for s in complete[a]} for a in arms}

def boot(diffs, B=20000, seed=7):
    rnd=random.Random(seed); n=len(diffs); out=[]
    for _ in range(B):
        out.append(sum(diffs[rnd.randrange(n)] for _ in range(n))/n)
    out.sort(); return out[int(.025*B)], out[int(.975*B)]

def wilcoxon(d):
    d=[x for x in d if abs(x)>1e-12]
    n=len(d)
    if n==0: return 1.0,0,0,0
    order=sorted(range(n), key=lambda i: abs(d[i]))
    rank=[0]*n
    i=0
    while i<n:
        j=i
        while j+1<n and abs(abs(d[j+1])-abs(d[i]))<1e-12: j+=1
        avg=(i+j)/2+1
        for k in range(i,j+1): rank[k]=avg
        i=j+1
    Wp=sum(rank[i] for i in range(n) if d[i]>0)
    Wm=sum(rank[i] for i in range(n) if d[i]<0)
    W=min(Wp,Wm)
    mu=n*(n+1)/4; sd=math.sqrt(n*(n+1)*(2*n+1)/24)
    z=(W-mu)/sd
    p=math.erfc(abs(z)/math.sqrt(2))
    return p, sum(1 for x in d if x>0), sum(1 for x in d if x<0), sum(1 for x in d if x==0)

print("\n=== 90-seed (1131-1220) arm summary ===")
for a in arms:
    v=list(per_seed[a].values())
    print(f"{a:16s} primary={st.fmean(v):.4f}  events={sum(agg[a]['events'])}  cov={st.fmean(agg[a]['cov']):.3f}  ask={st.fmean(agg[a]['ask']):.1f}  unserved={st.fmean(agg[a]['unserved']):.1f}")

print("\n=== paired contrast on 90 seeds: greedy - potential_ask ===")
base=per_seed["greedy"]
for a in arms:
    if a=="greedy": continue
    common=sorted(set(base)&set(per_seed[a]))
    d=[base[s]-per_seed[a][s] for s in common]
    lo,hi=boot(d); p,w,l,t=wilcoxon(d)
    m=st.fmean(d); sd=st.stdev(d); se=sd/math.sqrt(len(d))
    print(f"greedy-{a:16s} n={len(d)} diff={m:+.4f} [{lo:+.4f},{hi:+.4f}] se={se:.4f} p={p:.4f} W/T/L={w}/{t}/{l}  greedy={st.fmean([base[s] for s in common]):.4f} {a}={st.fmean([per_seed[a][s] for s in common]):.4f}")

print("\n=== per-family (90 seeds) ===")
for v in VARIANTS:
    line=f"{v:12s}"
    for a in arms:
        vals=[seedfam[(a,s)][v] for s in complete[a] if v in seedfam[(a,s)]]
        line+=f"  {a}={st.fmean(vals):.4f}"
    print(line)

json.dump({"per_seed":{a:{str(k):v for k,v in per_seed[a].items()} for a in arms},
           "n_episodes":len(rows),"seeds":seeds},
          open("/home/user/out_90/per_seed_90.json","w"), indent=1)
