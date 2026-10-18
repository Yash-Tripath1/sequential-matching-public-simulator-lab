# Sequential Reciprocal Matching Under Uncertainty

### A two-phase study of policy evaluation under a rare outcome

**Anadi Tripathi**
Indian Institute of Technology Madras
ORCID [0009-0002-9827-698X](https://orcid.org/0009-0002-9827-698X) · tripathiyash382@gmail.com

---

## What this is

A study of whether a reported policy advantage in sequential matching survives
being measured properly.

The setting is a public synthetic simulator of a reciprocal matching service.
Each day, for sixty decision days, a policy observes a changing pool of roughly
200 members; it may spend a budget of twelve clarification units on unresolved
hard constraints and soft attributes, and it then proposes a set of
non-overlapping introductions among members whose reciprocal hard constraints
are all known and satisfied. The scored outcome is **MSMI/100**: completed
introductions in which both members subsequently record that they want to meet
again, per 100 members who arrived, averaged with equal weight over six
scenario families.

The outcome is rare — fewer than one qualifying event per episode — and that
turns out to govern everything else.

## The finding

Phase 1 of this work screened seventeen policy configurations on ten seeds
(1,020 episodes) and reported that one of them beat the supplied greedy baseline
by **+0.175 MSMI/100** (95% seed-block CI [+0.092, +0.258], p = 0.016).

Phase 2 re-tested that claim. We first recovered the winning configuration from
surviving code and confirmed it reproduces the published headline **exactly** —
0.525 and 63 events, matching on 60 of 60 episodes against the stored
per-episode record. We then ran it against the baseline on **120 fresh seeds
(720 episodes per arm)**.

The advantage did not replicate. The configuration scored **0.3694** against the
baseline's **0.4021**, a paired difference of **0.0326 in the baseline's favour**
(95% CI [−0.0250, +0.0903], p = 0.356). The two estimates are **7.09 standard
errors apart**, and their intervals do not overlap.

What did replicate is the structural finding: the outcome is supply-bound.
Coverage sits at **97.8% of its structural ceiling**, and **64% of the variance
in the acceptance outcome is unobservable by construction**. Removing
clarification costs **−0.304** (p < 0.001) and is the largest effect in the
study by an order of magnitude. The lesson is that **structure replicates and
ranking does not**.

The full account is in [`PAPER.md`](PAPER.md).

## Headline table, 120 fresh seeds

| policy | MSMI/100 | 95% CI | coverage/ceiling | ask units | unserved/200 |
|---|---:|---|---:|---:|---:|
| **`greedy`** (supplied, **adopted**) | **0.402** | [0.357, 0.448] | 0.978 | 197 | 133.3 |
| `oldest_first` | 0.364 | [0.319, 0.409] | 0.980 | 197 | 133.2 |
| `random_feasible` | 0.332 | [0.292, 0.374] | 0.982 | 197 | 133.0 |
| `no_ask` | 0.098 | [0.075, 0.122] | 0.344 | 0 | 176.0 |

Significant paired contrasts: `greedy` > `random_feasible` (**+0.070**,
p = 0.004) and `greedy` > `no_ask` (**+0.304**, p < 0.001). `greedy` against
`oldest_first` is +0.038 (p = 0.136), not significant.

Note the competing direction in the coverage column: `random_feasible` reaches
the *highest* fraction of the structural ceiling and scores the *lowest* of the
three clarifying policies. More introductions is not the objective.

**A power caveat that applies to every comparison here.** With per-seed SD 0.214
at n = 120, the smallest effect detectable at 80% power is **0.055**. Our one
positive signal, `disagreement_aware`, came in at **+0.013 [−0.025, +0.051],
p = 0.524** — 0.24× the detectable effect. We did not adopt it, and we say so
rather than dress a p = 0.52 result up as a win. Resolving it would take
roughly **2,055 seeds**.

## Documents

| | |
|---|---|
| [`PAPER.md`](PAPER.md) | The research write-up. Merges both phases into one continuous account. Start here. |
| `REPORT.md` | The original technical report, preserved as written. Where the two differ, `PAPER.md` is the later and corrected version. |
| `REPRODUCE.md` | Exact commands, versions, seed lists, expected values and checksums. |
| `docs/` | Problem statement, Phase 1 research note (PDF), and the Phase 2 working log and plan. |

## Running it

```bash
docker build -t sequential-matching .
python evaluate.py --seeds 101,102,103 --variants all --output results/final.json
python -m unittest -v          # 10 tests
python verify_data.py          # 25 checks on the committed data
```

`kit.py`, `policy.py` and `evaluate.py` sit at the repository root and are
mirrored in `code/`. The image is `python:3.12.7-slim`, and the adopted policy
needs **no third-party packages** — `requirements.txt` documents `networkx`,
which only the offline analysis scripts use.

Reproduce the headline number:

```bash
pip install networkx==3.7
cd code
python3 waitlab.py --seeds 1101,1102 --arms greedy --workers 4 --out /tmp/check
python3 analyse.py --out /tmp/check --arms greedy
```

Recompute every p-value, interval and win/tie/loss count in the paper:

```bash
python3 code/restat.py     # writes results/restat_out.json
```

## Layout

| path | what |
|---|---|
| `policy.py` | the adopted policy (JSON stdin/stdout protocol) |
| `kit.py`, `evaluate.py` | the simulator and evaluator, unmodified |
| `verify_data.py` | checks the committed results against the report's claims |
| `code/waitlab.py` | experiment harness, mirrors `evaluate.py::episode` in-process |
| `code/analyse.py` | primary score, paired contrasts, disparity decomposition |
| `code/restat.py` | statistics: Wilcoxon signed-rank, seed-block bootstrap, W/T/L |
| `code/ceilings.py` | per-seed structural coverage ceiling |
| `code/calibration.py`, `code/calibration_analysis.py` | directional calibration study |
| `code/interaction.py` | policy-by-scenario interaction tests |
| `code/wait_comparison.py` | paired waiting-time analysis |
| `code/fallback_audit.py` | counts silently swallowed errors over full episodes |
| `code/equivalence_check.py` | checks two implementations agree decision-for-decision |
| `code/analysis/` | ad-hoc scripts behind specific tables; see its README |
| root-level `*.py` | Phase 1 exploratory scripts (`scaled_factorial.py`, `phase_screen.py`, `soft_ask_screen.py` and others) — abandoned branches, kept for provenance |
| `results/` | machine-readable results plus gzipped raw episode logs |
| `tests/` | contract tests across all policy arms |
| `SHA256SUMS.txt` | checksums for every committed file |

## Reproducibility

Phase 1 reported seventeen configurations. **Its code is here and it runs**: we
re-executed the fourteen configurations it defines on its own ten screen seeds,
**840 episodes, zero errors**.

Six reproduce exactly, verified on all six scenario families each, including
all three supplied baselines. The other eleven do not, because the assembly
layer that composed them was never committed. Two attempts to rebuild them from
the surviving components produced the wrong policy: 0.458 against a published
0.592, and 0.150 against 0.492. Nothing here is reconstructed from a written
description alone, and nothing is cited that cannot be run.

Two independent executions of the 120-seed baseline agree to three decimals on
primary score, events, coverage and unserved count. `code/restat.py` has been
validated against `scipy.stats.wilcoxon` over 200 randomised cases with a
maximum absolute difference in p of 0.0.

Full accounting in `REPORT.md` §4 and `docs/`.

## Limitations

- All results describe a **synthetic simulator**. They are not evidence about
  real matching, real people, or any product.
- **We did not beat the supplied baseline.** That is a finding about our designs
  and this simulator, not proof that no better policy exists.
- The design detects 0.055 at 80% power. We cannot distinguish "no effect" from
  "an effect below that".
- `disagreement_aware` remains unresolved. It is the only arm above the baseline
  and we did not adopt it; we cannot say whether it is real.
- Within a seed, four of the six scenario families generate the same 200
  members. We resample seeds to account for this; resampling episodes would
  overstate precision by roughly a factor of two.
- Waiting times must be read together with the unserved count. Reported alone,
  they make the worst policy look the fairest.
- `waitfloor` was measured on 30 seeds and is not part of the 120-seed
  comparison.

## Provenance

The simulator, evaluator and supplied baselines are third-party, used under the
terms in `LICENSE.kit`; they are vendored in this repository (`kit.py`,
`starter/`) so that no external download is needed to reproduce anything here,
and `kit.py` is checksummed in `SHA256SUMS.txt`. Hypothesis design, harness,
policies, analysis and all reported findings are the author's, released under
`LICENSE` (MIT).

AI tooling (Arena.ai Agent Mode) was used for code and for drafting. All results
come from code in this repository and were validated against the supplied
evaluator on nine independent checks
(`results/validation_vs_official_evaluator.csv`). Verification, not generation,
is the step that matters; two fabricated figures were caught and removed during
the audit described in `PAPER.md` §9.
