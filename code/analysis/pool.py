import json, glob, math, statistics as st
from collections import defaultdict
rows=[]
for f in sorted(glob.glob("/home/user/out_90/c*/episodes.jsonl")):
    for line in open(f):
        line=line.strip()
        if not line: continue
        r=json.loads(line)
        if r.get("valid") is False or not r.get("metrics"): continue
        rows.append(r)
g30=json.load(open("/home/user/github_repo/bipartite-bard-round2/results/analysis_30seeds_900ep.json"))["summary"]
def s30(a,k): return g30[a][k]
print("=== pooled 120-seed headline stats (90 fresh + 30 from analysis_30seeds_900ep) ===")
for a,lab in (("greedy","greedy"),("potential_ask","potential_ask")):
    sub=[r for r in rows if r["arm"]==a]
    n90=len(sub); n30=s30(a,"n_seeds")*6
    ev90=sum(r["metrics"]["mutual_second_meeting_intention"] for r in sub); ev30=s30(a,"events")
    cov90=st.fmean([r["metrics"]["coverage"] for r in sub]); cov30=s30(a,"coverage")
    ask90=st.fmean([r["metrics"]["ask_cost"] for r in sub]); ask30=s30(a,"ask_cost")
    uns90=st.fmean([r["metrics"]["unserved_members"] for r in sub]); uns30=s30(a,"unserved")
    cov=(cov30*30+cov90*90)/120; ask=(ask30*30+ask90*90)/120; uns=(uns30*30+uns90*90)/120
    print(f"{a:14s} events={ev30+ev30*0+ev90+ (ev30):d}? -> 30blk={ev30} 90blk={ev90} TOTAL={ev30+ev90}")
    print(f"{'':14s} coverage={cov:.4f}  ask_cost={ask:.1f}  unserved/200={uns:.2f}  episodes={n30+n90}")
print("\nVM transcribed greedy 120-seed: primary 0.402 [0.357,0.448] events 579 coverage 0.333 ask_cost 197 unserved 133.3")

print("\n=== waiting time, 90-seed block (1131-1220) ===")
for a in ("greedy","potential_ask"):
    w=[]
    for r in rows:
        if r["arm"]==a: w+=r["waits"]
    w.sort()
    print(f"{a:14s} n={len(w)} mean={st.fmean(w):.2f} median={st.median(w):.0f} p90={w[int(.9*len(w))]:.0f} max={w[-1]}")
