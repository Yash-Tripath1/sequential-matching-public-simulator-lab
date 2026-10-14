# Bipartite Bard — The Sequential Matching Problem, Round 2

Team Bipartite Bard — a solo entry by Anadi Tripathi, IIT Madras
Vouchsafe / RomeoJulietLove hackathon · Final build, October 2026

**Read [`REPORT.md`](REPORT.md) for the findings.** This file is the map.

---

## The result in four lines

1. **We ship the supplied `greedy` baseline.** Three alternatives were tested on
   120 fresh seeds and none beat it. We report that rather than tuning until
   something won.
2. **Clarification is the whole game.** Removing it drops reachable coverage from
   98% of the structural ceiling to 34%, and costs −0.304 on the primary outcome
   (p < 0.001). Nothing else we tested moves the score by more than hundredths.
3. **Pairing quality beats pairing quantity.** `random_feasible` makes *more*
   introductions and reaches a *higher* fraction of the ceiling — and scores
   0.070 lower (p = 0.004). The bottleneck is whom you pair, not how many.
4. **The same code scored 0.489 and 0.336** on two disjoint 30-seed sets. Which
   seeds you draw matters ~10× more than which policy you ship.

---

## Headline table — 120 seeds, 2,880 episodes

| arm | MSMI/100 | 95% CI | cov/ceiling | ask | unserved/200 |
|---|---:|---|---:|---:|---:|
| **`greedy`** (supplied, **shipped**) | **0.402** | [0.357, 0.448] | 0.978 | 197 | 133.3 |
| `oldest_first` (ours) | 0.364 | [0.319, 0.409] | 0.980 | 197 | 133.2 |
| `random_feasible` (supplied) | 0.332 | [0.292, 0.374] | 0.982 | 197 | 133.0 |
| `no_ask` (supplied) | 0.098 | [0.075, 0.122] | 0.344 | 0 | 176.0 |

Significant contrasts: `greedy` > `random_feasible` (+0.070, p = 0.004);
`greedy` > `no_ask` (+0.304, p < 0.001). `greedy` vs `oldest_first` is
+0.038, p = 0.136 — not significant, but we ship the point estimate.

---

## What is in here

| path | what |
|---|---|
| `REPORT.md` | **the technical report** — the submission document |
| `REPRODUCE.md` | exact commands, versions, seeds, checksums |
| `Dockerfile` | the submission image; **zero third-party dependencies** |
| `code/policy.py` | the shipped policy (JSON stdin/stdout protocol) |
| `code/kit.py`, `code/evaluate.py`, `code/baseline_policy.py` | organiser kit, unmodified |
| `code/waitlab.py` | experiment harness (in-process, mirrors `evaluate.py::episode`) |
| `code/analyse.py` | primary score, paired contrasts, disparity decomposition |
| `code/ceilings.py` | per-seed structural coverage ceiling |
| `code/wait_comparison.py` | paired waiting-time analysis |
| `results/` | machine-readable results, CSV + JSON |
| `docs/ROUND2_FINDINGS.md` | full working notes, 19 sections, with the negative results |
| `docs/ROUND2_PLAN.md` | the plan, written before the runs |

---

## Reproduce in three commands

```bash
pip install networkx==3.7
cd code
python3 waitlab.py --seeds 1101,1102 --arms greedy --workers 4 --out /tmp/check
python3 analyse.py --out /tmp/check --arms greedy
```

Full procedure, verification steps and expected values: [`REPRODUCE.md`](REPRODUCE.md).

---

## Reproducibility, stated up front

Round 1 reported 17 configurations. **The code for 13 of them was never
committed and does not survive anywhere.** We cite nothing we cannot run.

Six configurations do reproduce exactly, including all three supplied baselines.
Rebuilding a configuration from its written description gave the *wrong* policy
once already — a sign error produced 0.367 where the incumbent scored 0.525 — so
nothing here is reconstructed by description alone.

Full accounting in `REPORT.md` §4 and `docs/ROUND2_FINDINGS.md` §10.

---

## Honest limitations

- All results describe the supplied **synthetic simulator**. They are not
  evidence about real matching or any product.
- **We did not beat the supplied baseline.** That is a finding about our designs
  and this simulator, not proof that no better policy exists.
- On the organiser's 20 private seeds, two policies must differ by **~0.24** to
  be reliably ranked. Our ship-decision effect (0.070) would not be detectable
  at that size; we ship on expected value, not significance.
- Waiting times must be read with the unserved count. Reported alone, they make
  the worst policy look the fairest (`REPORT.md` §5.6).
- An attempted reconstruction of Round 1's 0.592 configuration did not run and
  is not reported.

---

## Attribution

The simulator, evaluator and baselines are the organiser's, used under the kit's
stated permissions (`LICENSE.kit`). Hypothesis design, harness, analysis and all
reported findings are ours.

AI tooling (Arena.ai Agent Mode) was used for code and drafting. All results come
from code in this repository and were validated against the organiser's own
evaluator on 9 independent checks (`results/validation_vs_official_evaluator.csv`).
