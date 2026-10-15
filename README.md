# The Sequential Matching Problem, Round 2

**Team Bipartite Bard**, a solo entry by **Anadi Tripathi**, IIT Madras
Vouchsafe / RomeoJulietLove hackathon · final build, October 2026

**The findings are in [`REPORT.md`](REPORT.md).** This file is the map.

---

## What this submission is

A policy for a sequential matching simulator, together with the study that
chose it. On each of 100 days the policy sees a pool of 200 members, may ask up
to 12 clarifying questions, and proposes mutually acceptable introductions. The
primary outcome is **MSMI/100**: completed meetings **and** mutual
second-meeting intention, per 100 members.

We tested four policies on **120 fresh seeds (2,880 complete episodes)** and
shipped the simplest one, because it had the highest score. Everything is
reported, including the parts that did not work.

---

## The result in four lines

1. **We ship the supplied `greedy` baseline.** Three alternatives were tested on
   120 fresh seeds and none beat it on the primary outcome. Two of the three
   gaps clear the noise floor at 120 seeds; none clears what the organiser's
   20-seed assessment can resolve. We report that rather than tuning until
   something won.
2. **Clarification is load-bearing.** Removing it drops reachable coverage from
   98% of the structural ceiling to 34%, and costs −0.304 on the primary
   outcome (p < 0.001). Nothing else we tested moves the score by more than
   hundredths.
3. **Pairing quality beats pairing quantity.** `random_feasible` makes *more*
   introductions and reaches a *higher* fraction of the ceiling, and scores
   0.070 lower (p = 0.004). The bottleneck is whom you pair, not how many.
4. **The same code scored 0.489 and 0.336** on two disjoint 30-seed sets. Which
   seeds you draw matters roughly ten times more than which policy you ship.

### Headline table, 120 seeds, 2,880 episodes

| arm | MSMI/100 | 95% CI | cov/ceiling | asks | unserved/200 |
|---|---:|---|---:|---:|---:|
| **`greedy`** (supplied, **shipped**) | **0.402** | [0.357, 0.448] | 0.978 | 197 | 133.3 |
| `oldest_first` (ours) | 0.364 | [0.319, 0.409] | 0.980 | 197 | 133.2 |
| `random_feasible` (supplied) | 0.332 | [0.292, 0.374] | 0.982 | 197 | 133.0 |
| `no_ask` (supplied) | 0.098 | [0.075, 0.122] | 0.344 | 0 | 176.0 |

Significant contrasts: `greedy` > `random_feasible` (+0.070, p = 0.004) and
`greedy` > `no_ask` (+0.304, p < 0.001). `greedy` vs `oldest_first` is +0.038,
p = 0.136: not significant, but we ship the point estimate.

---

## Run it

The assessed build is the repository root, so the organiser's commands work
with no setup step:

```bash
docker build -t bipartite-bard .
python evaluate.py --seeds 101,102,103 --variants all --output results/final.json
python -m unittest -v          # 8 tests
python verify_data.py          # 25 checks on the committed data
```

`kit.py`, `policy.py` and `evaluate.py` sit at the root and are mirrored in
`code/`. The image is `python:3.12.7-slim` and the shipped arm needs **no
third-party packages**; `requirements.txt` documents `networkx`, which is only
used by the offline analysis scripts.

### Reproduce the headline number

```bash
pip install networkx==3.7
cd code
python3 waitlab.py --seeds 1101,1102 --arms greedy --workers 4 --out /tmp/check
python3 analyse.py --out /tmp/check --arms greedy
```

Exact commands, versions, seed lists, expected values and checksums are in
[`REPRODUCE.md`](REPRODUCE.md).

---

## What is in here

| path | what |
|---|---|
| `REPORT.md` | the technical report, the submission document |
| `REPRODUCE.md` | exact commands, versions, seeds, checksums |
| `Dockerfile` | the submission image |
| `policy.py` | the shipped policy (JSON stdin/stdout protocol) |
| `kit.py`, `evaluate.py` | organiser kit, unmodified |
| `verify_data.py` | checks the committed results against the report's claims |
| `code/` | everything else: harness, ablation arms, analysis |
| `code/waitlab.py` | experiment harness, mirrors `evaluate.py::episode` in-process |
| `code/analyse.py` | primary score, paired contrasts, disparity decomposition |
| `code/ceilings.py` | per-seed structural coverage ceiling |
| `code/wait_comparison.py` | paired waiting-time analysis |
| `code/fallback_audit.py` | runs full episodes and counts silently swallowed errors |
| `code/equivalence_check.py` | proves the two candidate implementations agree |
| `results/` | machine-readable results, CSV and JSON, plus gzipped raw episode logs |
| `tests/` | contract tests, including empty-input coverage for all seven arms |
| `SHA256SUMS.txt` | checksums for every committed file |
| `docs/ROUND1_RESEARCH_NOTE.pdf` | the Round 1 note this work builds on |
| `docs/ROUND2_FINDINGS.md` | full working notes, including the negative results |
| `docs/ROUND2_PLAN.md` | the plan, written before the runs |

---

## Reproducibility, stated up front

Round 1 reported 17 configurations. **The code for 11 of them was never
committed and does not survive anywhere.** We cite nothing we cannot run.

Six configurations do reproduce exactly, including all three supplied
baselines. Rebuilding a configuration from its written description gave the
*wrong* policy once already, where a sign error produced 0.367 where the
incumbent scored 0.525, so nothing here is reconstructed by description alone.

Full accounting in `REPORT.md` §4 and `docs/ROUND2_FINDINGS.md` §10.

---

## Honest limitations

- All results describe the supplied **synthetic simulator**. They are not
  evidence about real matching, real people, or any product.
- **We did not beat the supplied baseline.** That is a finding about our designs
  and this simulator, not proof that no better policy exists.
- On the organiser's 20 private seeds, two policies must differ by about **0.24**
  to be reliably ranked. Our ship-decision effect (0.070) would not be
  detectable at that size. We ship on expected value, not significance.
- Waiting times must be read together with the unserved count. Reported alone,
  they make the worst policy look the fairest (`REPORT.md` §5.6).
- An attempted reconstruction of Round 1's 0.592 configuration did not run and
  is not reported.
- `waitfloor` was measured on 30 seeds only and is not part of the 120-seed
  comparison.

---

## Attribution

The simulator, evaluator and baselines are the organiser's, used under the
kit's stated permissions (`LICENSE.kit`). Hypothesis design, harness, analysis
and all reported findings are ours, released under `LICENSE` (MIT).

AI tooling (Arena.ai Agent Mode) was used for code and drafting. All results
come from code in this repository and were validated against the organiser's
own evaluator on 9 independent checks
(`results/validation_vs_official_evaluator.csv`).
