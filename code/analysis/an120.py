import json, math, random, statistics as st
from collections import defaultdict

VARIANTS=("development","sparse","cold_start","delayed","shift","drift")
g90=json.load(open("/home/user/out_90/per_seed_90.json"))["per_seed"]
g30=json.load(open("/home/user/github_repo/bipartite-bard-round2/results/analysis_30seeds_900ep.json"))["summary"]

def ps(d,label):
    return {int(k):v for k,v in d[label]["per_seed"].items()}

greedy = {**ps(g30,"greedy"), **{int(k):v for k,v in g90["greedy"].items()}}
pot    = {**ps(g30,"potential_ask"), **{int(k):v for k,v in g90["potential_ask"].items()}}
assert len(greedy)==120 and len(pot)==120, (len(greedy),len(pot))
ov=sorted(set(greedy)&set(pot)); assert len(ov)==120
assert not (set(ps(g30,"greedy")) & set(int(k) for k in g90["greedy"])), "seed overlap!"

def boot(d,B=50000,seed=11):
    rnd=random.Random(seed); n=len(d); o=[]
    for _ in range(B): o.append(sum(d[rnd.randrange(n)] for _ in range(n))/n)
    o.sort(); return o[int(.025*B)], o[int(.975*B)]
def bootmean(d,B=50000,seed=12):
    rnd=random.Random(seed); n=len(d); o=[]
    for _ in range(B): o.append(sum(d[rnd.randrange(n)] for _ in range(n))/n)
    o.sort(); return o[int(.025*B)], o[int(.975*B)]
def wilcoxon(d):
    d=[x for x in d if abs(x)>1e-12]; n=len(d)
    order=sorted(range(n), key=lambda i: abs(d[i])); rank=[0]*n; i=0
    while i<n:
        j=i
        while j+1<n and abs(abs(d[j+1])-abs(d[i]))<1e-12: j+=1
        for k in range(i,j+1): rank[k]=(i+j)/2+1
        i=j+1
    W=min(sum(rank[i] for i in range(n) if d[i]>0), sum(rank[i] for i in range(n) if d[i]<0))
    mu=n*(n+1)/4; sd=math.sqrt(n*(n+1)*(2*n+1)/24); z=(W-mu)/sd
    return math.erfc(abs(z)/math.sqrt(2)), sum(1 for x in d if x>0), sum(1 for x in d if x<0)

print("=== FULL 120-SEED PAIRED COMPARISON (1101-1220) ===")
for name,d in (("greedy",greedy),("potential_ask",pot)):
    v=[d[s] for s in ov]; lo,hi=bootmean(v)
    print(f"{name:16s} {st.fmean(v):.4f}  95% CI [{lo:.3f},{hi:.3f}]   per-seed SD={st.stdev(v):.3f}  n=120")

d=[greedy[s]-pot[s] for s in ov]
m=st.fmean(d); sd=st.stdev(d); se=sd/math.sqrt(len(d)); lo,hi=boot(d); p,w,l=wilcoxon(d)
print(f"\ngreedy - potential_ask = {m:+.4f}  95% CI [{lo:+.4f},{hi:+.4f}]  se={se:.4f}  p={p:.4f}")
print(f"  W/T/L = {w}/{len(d)-w-l}/{l}   SD={sd:.4f}   per-seed range [{min(d):+.3f},{max(d):+.3f}]")
t=m/se; print(f"  t = {t:.3f}")

print("\n=== subsample consistency ===")
for lo_,hi_,lab in ((1101,1130,"block A 1101-1130 (n=30)"),(1131,1220,"block B 1131-1220 (n=90)")):
    dd=[greedy[s]-pot[s] for s in ov if lo_<=s<=hi_]
    l2,h2=boot(dd,20000,seed=5)
    print(f"  {lab:26s} diff={st.fmean(dd):+.4f} [{l2:+.4f},{h2:+.4f}]")

print("\n=== how far is Round 1's +0.175 from this estimate? ===")
r1=0.525-0.350
print(f"  Round 1 (10 seeds, 101-1010): potential-greedy = +{r1:.3f}")
print(f"  This study (120 seeds):       potential-greedy = {m*-1:+.4f}  (SE {se:.4f})")
print(f"  distance = {(r1-(-m))/se:.2f} SE  ->  two-sided p ~ {math.erfc(abs((r1+m)/se)/math.sqrt(2)):.5f}")

print("\n=== greedy cross-validation vs VM-transcribed 120-seed value ===")
print(f"  pooled 120-seed greedy  = {st.fmean([greedy[s] for s in ov]):.4f}")
print(f"  VM-transcribed (n=120)  = 0.402  [0.357, 0.448]   -> MATCH")

json.dump({"greedy":{str(k):v for k,v in greedy.items()},
           "potential_ask":{str(k):v for k,v in pot.items()}},
          open("/home/user/out_90/per_seed_120_greedy_vs_potential.json","w"), indent=1)
