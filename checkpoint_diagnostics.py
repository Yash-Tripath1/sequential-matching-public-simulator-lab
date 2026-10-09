"""Observable-feedback/ask-budget diagnostics for the hybrid screen.

No policy reads world truth. Output aggregates mature MSMI-label counts at the
planned switch days and clarification-unit usage. Simulator truth is used only
inside the official simulator's own generated world/actions.
"""
from __future__ import annotations
import json, statistics, time, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"starter"))
import kit
import phase_screen as ps

ROOT=Path(__file__).resolve().parent
SEEDS=[101,202,303]
VARIANTS=["development","sparse","cold_start","delayed","shift","drift"]
SCHEDULES=["four_phase","adaptive"]
CHECK_DAYS=[15,30,45]


def one_episode(seed,variant,schedule):
    world=kit.generate(seed=seed,n=200,pool_id="evaluation",variant=variant)
    sim=kit.Simulator(world)
    policy=ps.SharedHistoryPhasePolicy(seed=seed,schedule=schedule)
    checkpoints={}
    ask_costs=[]
    strategies=[]
    for _ in range(60):
        state=sim.observe()
        asks=policy.asks(state)
        cost=sum(3 if a["field"]=="constraints" else 1 for a in asks)
        ask_costs.append(cost)
        sim.resolve_asks(asks)
        state=sim.observe()
        pairs=policy.pairs(state)
        day=int(state["day"])
        strategy=policy._strategy_for_day(day)
        strategies.append(strategy)
        if day in CHECK_DAYS:
            checkpoints[str(day)]={
                "mature_labels":len(policy.gp_y),
                "positive_labels":sum(policy.gp_y),
                "strategy":strategy,
            }
        sim.advance(pairs)
    return {
        "seed":seed,"variant":variant,"schedule":schedule,
        "ask_cost":sim.metrics()["ask_cost"],
        "days_at_budget_limit":sum(c==12 for c in ask_costs),
        "days_with_any_ask":sum(c>0 for c in ask_costs),
        "max_daily_ask_cost":max(ask_costs,default=0),
        "checkpoints":checkpoints,
        "gp_days":sum(s=="gp_ucb" for s in strategies),
        "thompson_days":sum(s=="thompson" for s in strategies),
        "greedy_days":sum(s=="greedy" for s in strategies),
        "adaptive_gp_ever":any(s=="gp_ucb" for s in strategies),
        "adaptive_first_gp_day":next((i for i,s in enumerate(strategies) if s=="gp_ucb"),None),
    }


def main():
    rows=[]
    total=len(SCHEDULES)*len(SEEDS)*len(VARIANTS)
    for schedule in SCHEDULES:
        for variant in VARIANTS:
            for seed in SEEDS:
                t=time.perf_counter()
                r=one_episode(seed,variant,schedule)
                rows.append(r)
                print(json.dumps({"done":len(rows),"total":total,"schedule":schedule,
                    "variant":variant,"seed":seed,"ask_cost":r["ask_cost"],
                    "budget_days":r["days_at_budget_limit"],
                    "day15":r["checkpoints"].get("15"),
                    "day30":r["checkpoints"].get("30"),
                    "day45":r["checkpoints"].get("45"),
                    "gp_ever":r["adaptive_gp_ever"],
                    "seconds":round(time.perf_counter()-t,2)}),flush=True)
    summary={}
    for schedule in SCHEDULES:
        rs=[r for r in rows if r["schedule"]==schedule]
        entry={"episodes":len(rs),
            "mean_total_ask_units":statistics.mean(r["ask_cost"] for r in rs),
            "mean_days_at_12_unit_cap":statistics.mean(r["days_at_budget_limit"] for r in rs),
            "episodes_ever_hitting_12":sum(r["days_at_budget_limit"]>0 for r in rs),
            "mean_days_with_any_ask":statistics.mean(r["days_with_any_ask"] for r in rs)}
        for d in CHECK_DAYS:
            vals=[r["checkpoints"].get(str(d)) for r in rs]
            entry[f"day{d}_mature_labels_median"]=statistics.median(v["mature_labels"] for v in vals)
            entry[f"day{d}_positive_labels_median"]=statistics.median(v["positive_labels"] for v in vals)
            entry[f"day{d}_mature_labels_mean"]=statistics.mean(v["mature_labels"] for v in vals)
        if schedule=="adaptive":
            entry["adaptive_gp_episodes"]=sum(r["adaptive_gp_ever"] for r in rs)
            first=[r["adaptive_first_gp_day"] for r in rs if r["adaptive_first_gp_day"] is not None]
            entry["first_gp_day_median_if_switched"]=statistics.median(first) if first else None
        summary[schedule]=entry
    out={"runner":"in_process_public_simulator_diagnostics","seeds":SEEDS,
        "variants":VARIANTS,"rows":rows,"summary":summary,
        "note":"Observational diagnostics only; no private seeds or hidden policy inputs."}
    p=ROOT/"results"/"checkpoint_diagnostics.json"
    p.write_text(json.dumps(out,indent=2,allow_nan=False)+"\n")
    print("SUMMARY",json.dumps(summary,indent=2),flush=True)
    print("WROTE",p,flush=True)

if __name__=="__main__": main()
