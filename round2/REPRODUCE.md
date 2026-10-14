# Reproducing every number in the report

Everything below was run on Ubuntu 22.04/24.04 with Python 3.12. All commands are
single-line; run them from the repository root unless stated.

---

## 1 Environment

```bash
python3 -m pip install networkx==3.7
```

`networkx` is needed **only** by the max-weight matcher arms (`oldest_first`,
`potential_ask`). The shipped `greedy` arm uses the standard library alone, and
the Docker image installs nothing.

| component | value |
|---|---|
| Python | 3.12 (3.10+ sufficient) |
| kit commit | `a8e26b3` |
| `kit.py` SHA-256 | `0d2cb3d3b46ca2a6…` (full digest in `SHA256SUMS.txt`) |
| networkx | 3.7 |
| inference random seed | `PYTHONHASHSEED=0` (pinned in `Dockerfile`) |
| training seeds | none — no model is fitted |

Verify the kit before doing anything else:

```bash
python3 -c "import hashlib; print(hashlib.sha256(open('code/kit.py','rb').read()).hexdigest())"
```

Must begin `0d2cb3d3`. If it does not, stop — you have the wrong simulator.

---

## 2 Seeds and scale

| run | seeds | arms | episodes |
|---|---|---|---|
| 30-seed sweep | 1101–1130 | 5 | 900 |
| 60-seed ship comparison | 1101–1160 | 2 | 720 |
| **120-seed full comparison** | **1101–1220** | **4** | **2,880** |
| Round-1-seed replication | 101–1010 | 2 | 120 |
| Official-evaluator validation | 1101–1102 | 3 | 36 |

---

## 3 The main run (2,880 episodes)

```bash
cd code
CEIL=$(python3 -c "print(','.join(str(s) for s in range(1101,1221)))")
python3 waitlab.py --seeds $CEIL --arms greedy,oldest_first --workers 4 --out ~/out_ship
python3 waitlab.py --seeds $CEIL --arms no_ask,random_feasible --workers 4 --out ~/out_baselines
python3 ceilings.py $CEIL development,sparse,cold_start,delayed,shift,drift ~/out_ship/ceilings.json
```

Runtime: ~42 min per 1,440 episodes on 4 cores (≈7 s/episode, 4 workers). The
progress counter advances by 20 per line, so a line appears every ~35 s — this is
normal, not a stall.

Then analyse:

```bash
cp ~/out_ship/ceilings.json ~/out_baselines/
python3 analyse.py --out ~/out_baselines --arms no_ask,random_feasible --skip-disparity
mkdir -p ~/out_all && cat ~/out_ship/episodes.jsonl ~/out_baselines/episodes.jsonl > ~/out_all/episodes.jsonl && cp ~/out_ship/ceilings.json ~/out_all/
python3 analyse.py --out ~/out_all --arms greedy,oldest_first,no_ask,random_feasible --skip-disparity
```

Expected (this is `results/primary_120seeds.csv`):

```
greedy           0.402 [0.357, 0.448]  579 events  cov 0.333  cov/ceil 0.978
oldest_first     0.364 [0.319, 0.409]  524 events  cov 0.334  cov/ceil 0.980
random_feasible  0.332 [0.292, 0.374]  478 events  cov 0.335  cov/ceil 0.982
no_ask           0.098 [0.075, 0.122]  141 events  cov 0.120  cov/ceil 0.344
```

---

### 3.1 Per-scenario results (required — do not skip)

`analyse.py` writes `analysis.json` into the output directory next to
`episodes.jsonl`. It contains `summary[arm]["family"]` — the primary score broken
out by **each of the six scenario families** for every arm. That is the
scenario-level evidence the submission requires, and it is **not** in
`results/` yet.

Copy it across and it lands in `results/`:

```bash
cp ~/out_all/analysis.json /path/to/round2/results/per_family_120seeds.json
```

Verify it has all six families for all four arms:

```bash
python3 -c "
import json
d=json.load(open('results/per_family_120seeds.json'))
for arm,s in d['summary'].items():
    f=s.get('family',{})
    print(arm, len(f), {k:round(v,3) for k,v in f.items()})
"
```

Expect four arms, each with six families (`development`, `sparse`, `cold_start`,
`delayed`, `shift`, `drift`).

---

## 4 Waiting-time analysis

```bash
cat ~/out_ship/members.jsonl ~/out_baselines/members.jsonl > ~/out_all/members.jsonl
python3 wait_comparison.py ~/out_all/members.jsonl greedy oldest_first
```

Expected (`results/waiting_paired_120seeds.csv`): mean wait +0.146 [+0.033, +0.259]
and p90 wait +1.050 [+0.742, +1.358], both excluding zero in `oldest_first`'s favour.

---

## 5 Validation against the organiser's evaluator

The check that would catch a harness defect. Run the official evaluator and our
harness on identical seeds and compare all nine metrics:

```bash
cd code
for B in greedy no_asks random; do python3 evaluate.py --baseline $B --seeds 1101,1102 --variants all --output /tmp/off_$B.json; done
python3 waitlab.py --seeds 1101,1102 --arms greedy,no_ask,random_feasible --workers 4 --out /tmp/ours
```

Expected: **9/9 exact matches** (`results/validation_vs_official_evaluator.csv`):

| arm | msmi_per_100 | coverage | ask_cost |
|---|---:|---:|---:|
| greedy | 0.708333 | 0.347917 | 194.5 |
| no_ask | 0.166667 | 0.127083 | 0.0 |
| random_feasible | 0.500000 | 0.350417 | 194.5 |

Note the official baseline flags are `no_asks` and `random`; our arm names are
`no_ask` and `random_feasible`.

**If any of the nine differs, do not trust any result in the report.**

---

## 6 Determinism

```bash
for HS in 0 42; do PYTHONHASHSEED=$HS python3 waitlab.py --seeds 1101 --arms greedy --workers 1 --out /tmp/hs$HS; done
```

Both runs must produce identical `msmi_per_100_arrived_members` per episode.
If they differ, the sweep is not reproducible — report it rather than proceeding.

---

## 7 Docker

```bash
cp code/policy.py policy.py && cp code/kit.py . && docker build -t bipartite-bard:round2 .
echo '{"phase":"ask","state":{"day":0,"members":[],"introductions":[],"ask_budget_remaining":12},"memory":{}}' | docker run --rm -i bipartite-bard:round2
echo '{"phase":"match","state":{"day":0,"members":[],"introductions":[]},"memory":{}}' | docker run --rm -i bipartite-bard:round2
```

Both must print valid JSON and exit 0. The image installs **nothing** — the
shipped `greedy` arm is standard-library only, and `networkx` is imported lazily
so it is never needed at container start.

To run a different arm without rebuilding:

```bash
docker run --rm -i -e ROUND2_ARM=oldest_first bipartite-bard:round2
```

---

## 8 A note on the results files

`results/primary_120seeds.*` was **transcribed from terminal output** of the
analysis scripts; the raw per-episode JSONL (3,600 episodes, tens of MB) stays on
the team's machine rather than in git. The transcribed tables are the complete
aggregates and were checked for internal consistency:

- `events ÷ 720 ÷ 200 × 100` reproduces every primary score exactly
- `(200 − unserved) ÷ 200` reproduces every coverage figure exactly
- all six contrasts equal the difference of the arm point estimates
- all six W/T/L rows sum to 720

To regenerate the raw data, re-run §3 — about 85 minutes on 4 cores.
