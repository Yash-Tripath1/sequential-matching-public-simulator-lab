"""Corrected-label rerun of the existing learned baselines.

Uses the exact original policies and public worlds, but patches only the
MSMI-label helper to enforce the official 30-day date deadline. It writes a
separate artifact and leaves the checked-in historical pilot untouched.
"""
from __future__ import annotations
import json, statistics, time
from pathlib import Path
import experiment_lab as lab
import kit
from phase_screen import official_mature_primary_label

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"results"/"corrected_learning_rerun_3seeds.json"
METHODS=["thompson_pattern","gp_mean","gp_ucb"]
SEEDS=[101,202,303]
VARIANTS=["development","sparse","cold_start","delayed","shift","drift"]


def main():
    lab.mature_primary_label=official_mature_primary_label
    rows=[]
    total=len(METHODS)*len(SEEDS)*len(VARIANTS)
    for method in METHODS:
        for variant in VARIANTS:
            for seed in SEEDS:
                t=time.perf_counter()
                row=lab.run_episode(method,seed,variant)
                if not row.get("valid"):
                    raise RuntimeError(f"invalid episode {method}/{variant}/{seed}: {row}")
                rows.append(row)
                print(json.dumps({"done":len(rows),"total":total,"method":method,
                    "variant":variant,"seed":seed,"msmi":row["mutual_second_meeting_intention"],
                    "seconds":round(time.perf_counter()-t,2)}),flush=True)
    old=json.loads((ROOT/"results"/"public_pilot_results.json").read_text())["rows"]
    summary={}
    for method in METHODS:
        current=[r for r in rows if r["method"]==method]
        original=[r for r in old if r["method"]==method]
        by_variant={}
        for variant in VARIANTS:
            cr=[r for r in current if r["variant"]==variant]
            orows=[r for r in original if r["variant"]==variant]
            by_variant[variant]={
                "old_msmi_per_100":statistics.mean(r["msmi_per_100_arrived_members"] for r in orows),
                "corrected_msmi_per_100":statistics.mean(r["msmi_per_100_arrived_members"] for r in cr),
                "old_mature_msmi_count":sum(r["mutual_second_meeting_intention"] for r in orows),
                "corrected_mature_msmi_count":sum(r["mutual_second_meeting_intention"] for r in cr),
            }
        old_map={(r["variant"],r["seed"]):r for r in original}
        new_map={(r["variant"],r["seed"]):r for r in current}
        diffs=[new_map[k]["msmi_per_100_arrived_members"]-old_map[k]["msmi_per_100_arrived_members"] for k in sorted(old_map.keys()&new_map.keys())]
        summary[method]={
            "episodes":len(current),
            "old_equal_variant_msmi_per_100":statistics.mean(statistics.mean(r["msmi_per_100_arrived_members"] for r in original if r["variant"]==v) for v in VARIANTS),
            "corrected_equal_variant_msmi_per_100":statistics.mean(statistics.mean(r["msmi_per_100_arrived_members"] for r in current if r["variant"]==v) for v in VARIANTS),
            "paired_wins_ties_losses": [sum(x>0 for x in diffs),sum(x==0 for x in diffs),sum(x<0 for x in diffs)],
            "by_variant":by_variant,
        }
    payload={"release":kit.VERSION,"runner":"in_process_corrected_learning_label_rerun",
        "methods":METHODS,"seeds":SEEDS,"variants":VARIANTS,
        "note":"Public synthetic simulator only. Original artifacts preserved; rerun corrects only the mature-label date deadline.",
        "rows":rows,"summary":summary}
    OUT.write_text(json.dumps(payload,indent=2,allow_nan=False)+"\n")
    print("SUMMARY",json.dumps(summary,indent=2,allow_nan=False),flush=True)
    print("WROTE",OUT,flush=True)

if __name__=="__main__": main()
