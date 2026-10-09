"""Run the core clarification × matcher factorial at 10 public seeds/variant.

Runs seven additional seeds, then combines them with the existing public-pilot
rows for seeds 101/202/303. All method comparisons use matched seed/variant
worlds. In-process public-simulator analysis only; not private or Docker eval.
"""
from __future__ import annotations
import csv, json, math, statistics, time
from pathlib import Path
import numpy as np
import experiment_lab as lab
import kit

ROOT=Path(__file__).resolve().parent
RESULTS=ROOT/"results"
EXTRA_JSON=RESULTS/"scaled_factorial_extra_7seeds.json"
FULL_JSON=RESULTS/"scaled_factorial_10seeds.json"
SUMMARY_CSV=RESULTS/"scaled_factorial_summary.csv"
CONTRASTS_CSV=RESULTS/"scaled_factorial_contrasts.csv"
METHODS=["greedy","no_ask","random_feasible","max_weight_similarity","potential_ask_greedy","potential_ask"]
EXISTING_SEEDS=[101,202,303]
NEW_SEEDS=[404,505,606,707,808,909,1010]
ALL_SEEDS=EXISTING_SEEDS+NEW_SEEDS
VARIANTS=["development","sparse","cold_start","delayed","shift","drift"]
N_BOOT=10000
BOOT_SEED=20261009


def save_extra(rows,complete=False):
    payload={"release":kit.VERSION,"runner":"in_process_public_simulator_scaled_factorial",
        "new_seeds":NEW_SEEDS,"variants":VARIANTS,"methods":METHODS,
        "target_new_episodes":len(NEW_SEEDS)*len(VARIANTS)*len(METHODS),
        "completed_new_episodes":len(rows),"complete":bool(complete),
        "note":"Public synthetic simulator only. Full 10-seed summaries merge these rows with checked-in pilot rows for seeds 101/202/303.",
        "rows":rows}
    EXTRA_JSON.write_text(json.dumps(payload,indent=2,allow_nan=False)+"\n")


def bootstrap_ci(values, rng, n_boot=N_BOOT):
    x=np.asarray(values,dtype=float)
    if not len(x): return [None,None]
    draws=rng.choice(x,size=(n_boot,len(x)),replace=True).mean(axis=1)
    lo,hi=np.percentile(draws,[2.5,97.5])
    return [float(lo),float(hi)]


def exact_sign_flip_p(block_diffs):
    d=np.asarray(block_diffs,dtype=float)
    n=len(d)
    if n==0: return None
    observed=abs(float(d.mean()))
    if observed==0: return 1.0
    extreme=0
    for mask in range(1<<n):
        signs=np.fromiter((1.0 if (mask>>i)&1 else -1.0 for i in range(n)),dtype=float,count=n)
        if abs(float((d*signs).mean())) >= observed-1e-12:
            extreme+=1
    return extreme/(1<<n)


def method_summary(rows, rng):
    out={}
    for method in METHODS:
        mr=[r for r in rows if r["method"]==method]
        seed_block={seed:statistics.mean(
            next(r["msmi_per_100_arrived_members"] for r in mr if r["seed"]==seed and r["variant"]==v)
            for v in VARIANTS) for seed in ALL_SEEDS}
        scenario={}
        for v in VARIANTS:
            vals=[r["msmi_per_100_arrived_members"] for r in mr if r["variant"]==v]
            scenario[v]={"n":len(vals),"mean":statistics.mean(vals),
                "sd":statistics.stdev(vals) if len(vals)>1 else 0.0,
                "bootstrap_ci95":bootstrap_ci(vals,rng)}
        primary=statistics.mean(seed_block.values())
        overall={}
        for field in ["assignments","mutual_acceptances","dates","mutual_second_meeting_intention","missing_feedback","coverage","mutual_acceptances_per_100","ask_cost","unserved_members","mean_first_intro_wait_days","policy_wall_seconds_in_process"]:
            vals=[r[field] for r in mr if r.get(field) is not None]
            overall[field+"_mean"]=statistics.mean(vals) if vals else None
        out[method]={"episodes":len(mr),"seeds_per_variant":len(ALL_SEEDS),
            "primary_equal_variant_msmi_per_100":primary,
            "primary_seed_block_ci95":bootstrap_ci(list(seed_block.values()),rng),
            "seed_block_scores":{str(k):v for k,v in seed_block.items()},
            "scenario_msmi_per_100":scenario,"overall_secondary_means":overall}
    return out


def contrast(rows,a,b,rng):
    ma={(r["seed"],r["variant"]):r for r in rows if r["method"]==a}
    mb={(r["seed"],r["variant"]):r for r in rows if r["method"]==b}
    keys=sorted(ma.keys() & mb.keys())
    diffs={k:ma[k]["msmi_per_100_arrived_members"]-mb[k]["msmi_per_100_arrived_members"] for k in keys}
    seed_block={s:statistics.mean(diffs[(s,v)] for v in VARIANTS) for s in ALL_SEEDS}
    per_variant={}
    for v in VARIANTS:
        vals=[diffs[(s,v)] for s in ALL_SEEDS]
        per_variant[v]={"mean_difference":statistics.mean(vals),
            "wins_ties_losses":[sum(x>0 for x in vals),sum(x==0 for x in vals),sum(x<0 for x in vals)],
            "bootstrap_ci95":bootstrap_ci(vals,rng)}
    return {"a_minus_b":f"{a} - {b}","paired_episodes":len(keys),
        "equal_variant_mean_difference":statistics.mean(seed_block.values()),
        "seed_block_bootstrap_ci95":bootstrap_ci(list(seed_block.values()),rng),
        "exact_two_sided_sign_flip_p_by_seed_block":exact_sign_flip_p(list(seed_block.values())),
        "wins_ties_losses_all_episodes":[sum(x>0 for x in diffs.values()),sum(x==0 for x in diffs.values()),sum(x<0 for x in diffs.values())],
        "per_variant":per_variant,
        "seed_block_differences":{str(k):v for k,v in seed_block.items()}}


def factorial_effect(rows,kind,rng):
    by={(r["method"],r["seed"],r["variant"]):r["msmi_per_100_arrived_members"] for r in rows}
    seed_blocks={}
    for seed in ALL_SEEDS:
        vals=[]
        for variant in VARIANTS:
            g=by[("greedy",seed,variant)]
            mg=by[("max_weight_similarity",seed,variant)]
            pg=by[("potential_ask_greedy",seed,variant)]
            pm=by[("potential_ask",seed,variant)]
            if kind=="ask_main": x=((pg-g)+(pm-mg))/2
            elif kind=="matcher_main": x=((mg-g)+(pm-pg))/2
            elif kind=="interaction": x=(pm-mg)-(pg-g)
            else: raise ValueError(kind)
            vals.append(x)
        seed_blocks[seed]=statistics.mean(vals)
    return {"effect":kind,"mean":statistics.mean(seed_blocks.values()),
        "seed_block_bootstrap_ci95":bootstrap_ci(list(seed_blocks.values()),rng),
        "exact_two_sided_sign_flip_p_by_seed_block":exact_sign_flip_p(list(seed_blocks.values())),
        "seed_block_values":{str(k):v for k,v in seed_blocks.items()}}


def main():
    RESULTS.mkdir(parents=True,exist_ok=True)
    rows=[]
    total=len(METHODS)*len(NEW_SEEDS)*len(VARIANTS)
    done=0
    for method in METHODS:
        for variant in VARIANTS:
            for seed in NEW_SEEDS:
                t=time.perf_counter()
                row=lab.run_episode(method,seed,variant)
                if not row.get("valid"):
                    raise RuntimeError(f"invalid simulator action: {method}/{variant}/{seed}: {row}")
                rows.append(row);done+=1
                save_extra(rows,complete=False)
                if done%6==0 or done==total:
                    print(json.dumps({"progress":f"{done}/{total}","method":method,
                        "variant":variant,"seed":seed,"msmi":row["mutual_second_meeting_intention"],
                        "episode_seconds":round(time.perf_counter()-t,2)}),flush=True)
    save_extra(rows,complete=True)
    old=json.loads((RESULTS/"public_pilot_results.json").read_text())["rows"]
    old=[r for r in old if r["method"] in METHODS and r["seed"] in EXISTING_SEEDS]
    for m in METHODS:
        assert sum(r["method"]==m for r in old)==18,(m,"old row count")
        assert sum(r["method"]==m for r in rows)==42,(m,"new row count")
    combined=old+rows
    for m in METHODS:
        for v in VARIANTS:
            assert sum(r["method"]==m and r["variant"]==v for r in combined)==10,(m,v,"expected 10 seeds")
    rng=np.random.default_rng(BOOT_SEED)
    summary=method_summary(combined,rng)
    contrasts={
        "potential_asks_vs_default_greedy":contrast(combined,"potential_ask_greedy","greedy",rng),
        "potential_asks_vs_default_maxweight":contrast(combined,"potential_ask","max_weight_similarity",rng),
        "maxweight_vs_greedy_default_asks":contrast(combined,"max_weight_similarity","greedy",rng),
        "maxweight_vs_greedy_potential_asks":contrast(combined,"potential_ask","potential_ask_greedy",rng),
    }
    factorial={k:factorial_effect(combined,k,rng) for k in ["ask_main","matcher_main","interaction"]}
    payload={"release":kit.VERSION,"runner":"in_process_public_simulator_scaled_factorial",
        "methods":METHODS,"seeds":ALL_SEEDS,"variants":VARIANTS,
        "episodes_per_method":60,"total_episodes":len(combined),
        "protocol":"Each public scenario family has 10 seeds. Primary summary equal-weights six family means. Bootstrap CIs resample seed blocks for primary/contrasts and episodes within family for scenario CIs. Exact sign-flip test uses 10 seed-block differences.",
        "bootstrap_analysis_seed":BOOT_SEED,"n_bootstrap":N_BOOT,
        "note":"Public synthetic simulator only; not private evaluation or Docker validation.",
        "rows":combined,"method_summary":summary,"paired_contrasts":contrasts,"factorial_effects":factorial}
    FULL_JSON.write_text(json.dumps(payload,indent=2,allow_nan=False)+"\n")
    # Summary table CSV.
    fieldnames=["method","primary_msmi_per_100","primary_ci95_low","primary_ci95_high","coverage_mean","assignments_mean","mutual_acceptances_mean","dates_mean","msmi_count_mean","missing_feedback_mean","ask_cost_units_mean","unserved_members_mean","first_intro_wait_days_mean"]
    with SUMMARY_CSV.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fieldnames);w.writeheader()
        for m in METHODS:
            s=summary[m];o=s["overall_secondary_means"];ci=s["primary_seed_block_ci95"]
            w.writerow({"method":m,"primary_msmi_per_100":s["primary_equal_variant_msmi_per_100"],
                "primary_ci95_low":ci[0],"primary_ci95_high":ci[1],
                "coverage_mean":o["coverage_mean"],"assignments_mean":o["assignments_mean"],
                "mutual_acceptances_mean":o["mutual_acceptances_mean"],"dates_mean":o["dates_mean"],
                "msmi_count_mean":o["mutual_second_meeting_intention_mean"],
                "missing_feedback_mean":o["missing_feedback_mean"],"ask_cost_units_mean":o["ask_cost_mean"],
                "unserved_members_mean":o["unserved_members_mean"],"first_intro_wait_days_mean":o["mean_first_intro_wait_days_mean"]})
    # Contrast CSV: all scenarios and the four pre-registered pairings.
    with CONTRASTS_CSV.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["contrast","scenario","mean_difference","ci95_low","ci95_high","wins","ties","losses"])
        w.writeheader()
        for name,c in contrasts.items():
            for v,x in c["per_variant"].items():
                w.writerow({"contrast":name,"scenario":v,"mean_difference":x["mean_difference"],
                    "ci95_low":x["bootstrap_ci95"][0],"ci95_high":x["bootstrap_ci95"][1],
                    "wins":x["wins_ties_losses"][0],"ties":x["wins_ties_losses"][1],"losses":x["wins_ties_losses"][2]})
    print("SUMMARY",json.dumps({"methods":{m:{"primary":s["primary_equal_variant_msmi_per_100"],"ci":s["primary_seed_block_ci95"]} for m,s in summary.items()},
        "factorial":factorial,"contrasts":{k:{"mean":v["equal_variant_mean_difference"],"ci":v["seed_block_bootstrap_ci95"],"p":v["exact_two_sided_sign_flip_p_by_seed_block"],"wtl":v["wins_ties_losses_all_episodes"]} for k,v in contrasts.items()}},indent=2,allow_nan=False),flush=True)
    print("WROTE",FULL_JSON,flush=True)
    print("WROTE",SUMMARY_CSV,flush=True)
    print("WROTE",CONTRASTS_CSV,flush=True)

if __name__=="__main__": main()
