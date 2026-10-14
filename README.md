# The One Introduction Problem · Bipartite Bard

Team **Bipartite Bard** — a solo entry by Anadi Tripathi, IIT Madras
Vouchsafe Sequential Matching Hackathon · built on the organisers' public
synthetic simulator (participant specification 1.0.0, kit commit `a8e26b3`).

---

## This repository has two rounds

| | what | status |
|---|---|---|
| **[`round2/`](round2/)** | **the final build — this is the submission** | current |
| root files, `research/`, `results/`, `starter/`, `tools/`, `tests/` | Round 1 research lab | **frozen**, kept for provenance |

**Assessors: everything required for the final build is in [`round2/`](round2/).**
Start at [`round2/REPORT.md`](round2/REPORT.md).

---

## Round 2 — the final build

**We ship the supplied `greedy` baseline.** Three alternatives were tested on 120
fresh seeds and none beat it. We report that rather than tuning until something
won.

Headline table — 120 seeds × 6 scenarios × 4 policies = **2,880 episodes**, paired
on identical worlds:

| arm | MSMI/100 | 95% CI | cov/ceiling | unserved/200 |
|---|---:|---|---:|---:|
| **`greedy`** (supplied, **shipped**) | **0.402** | [0.357, 0.448] | 0.978 | 133.3 |
| `oldest_first` (ours) | 0.364 | [0.319, 0.409] | 0.980 | 133.2 |
| `random_feasible` (supplied) | 0.332 | [0.292, 0.374] | 0.982 | 133.0 |
| `no_ask` (supplied) | 0.098 | [0.075, 0.122] | 0.344 | 176.0 |

**What the ablations showed:**

- **Clarification is load-bearing.** Removing it drops reachable coverage from
  98% of the structural ceiling to 34% and costs −0.304 on the primary outcome
  (p < 0.001). Nothing else we tested moves the score by more than hundredths.
- **Pairing quality beats pairing quantity.** `random_feasible` makes *more*
  introductions and reaches a *higher* share of the ceiling — and scores 0.070
  lower (p = 0.004). The bottleneck is *whom* you pair, not how many.
- **Ask priority is a free fairness lever.** Directing every clarification slot
  to the longest-waiting member removes **1.05 days from the p90 wait**
  (p < 0.001) with no significant outcome cost.
- **Seed-set variation dominates.** The same code scored 0.489 and 0.336 on two
  disjoint 30-seed sets — roughly ten times the size of any policy difference.

Full report: [`round2/REPORT.md`](round2/REPORT.md) ·
reproduction: [`round2/REPRODUCE.md`](round2/REPRODUCE.md)

---

## Round 1 — frozen

The Round 1 research note is at
[`research/RESEARCH_NOTE_ROUND1_rev3.pdf`](research/RESEARCH_NOTE_ROUND1_rev3.pdf).

**Important:** Round 1 reported 17 configurations. The code for 13 of them was
never committed and does not survive in any location we searched. We therefore
cite nothing we cannot run. The non-replication of Round 1's headline claim is
one of the findings of Round 2 — see `round2/REPORT.md` §5.9.

Six configurations do reproduce exactly, including all three supplied baselines:
`greedy` 0.350, `no_ask` 0.167, `random_feasible` 0.358.

---

## Reproducibility

All Round 2 results come from code in [`round2/code/`](round2/code/) and were
validated against the organiser's own evaluator on **9 independent metrics with
9 exact matches** — see
[`round2/results/validation_vs_official_evaluator.csv`](round2/results/validation_vs_official_evaluator.csv).

Kit integrity: `kit.py` SHA-256 begins `0d2cb3d3b46ca2a6`. Verify before trusting
anything:

```bash
python3 -c "import hashlib; print(hashlib.sha256(open('round2/code/kit.py','rb').read()).hexdigest())"
```

---

## Attribution and scope

The simulator, evaluator and baselines are the organiser's, used under the kit's
stated permissions (`round2/LICENSE.kit`). Hypothesis design, harness, analysis
and all reported findings are ours.

Every result describes the supplied synthetic simulator. Nothing here is evidence
about real matching, real people, or any product.

AI tooling (Arena.ai Agent Mode) was used for code and drafting. All results come
from code in this repository.
