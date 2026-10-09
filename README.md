# Sequential Matching — Public Simulator Research Lab

An exploratory study of budgeted clarification and online matching using the organizers'
**public synthetic simulator**. This repository contains the policy prototypes, unchanged
simulator snapshot, reproducible analysis code, available episode-level results, charts,
the Round 1 research note, and the prior-phase experiment record.

> **Scope:** All reported episodes use public synthetic worlds. These results are not
> private-evaluation scores, Docker-validation results, real-user evidence, or evidence of
> real-world compatibility or product effectiveness.

## Round 1 research note (submitted thesis)

The Round 1 submission is **[`research/RESEARCH_NOTE_ROUND1.pdf`](research/RESEARCH_NOTE_ROUND1.pdf)** —
*The One Introduction Problem: a supply-constrained sequential matching policy.* Its thesis,
in brief:

- The score in this simulator is **supply-determined, not ranking-determined**. The
  reciprocal hard-constraint graph is thin (mean degree 2.53 in development; 33.9% of
  members have no feasible partner; 31.9% are permanently decline-blocked), giving
  per-family coverage ceilings (0.399 development, 0.341 cold start, 0.178 sparse).
- **Asking vs not-asking is the robust lever:** all sixteen asking-vs-no-ask contrasts
  exclude zero (+0.183 MSMI/100 for the unmodified starter baseline up to +0.425 for our
  best cell). **Targeted asking is not supported (H1):** unlock-value ranking gives
  −0.083 to +0.008 vs simpler ask rules, all CIs straddling zero, and reverses in cold
  start. An oracle with free perfect clarification plus maximum-cardinality allocation
  moves coverage by ~0.001 and MSMI not at all (analysis-only ladder).
- The single pre-specified defended comparison: **incumbent vs official greedy baseline
  +0.175 MSMI/100 (95% seed-block CI [+0.092, +0.258], p = 0.016, W/T/L 23/29/8)**. The
  best screened cell (potential asks + signed core-4 weights + global blossom matching,
  0.592) is a Round 2 candidate, not a confirmed result.
- Negative results reported on purpose: soft-residual asks null (+0.017, p = 0.961);
  online adaptation on dense directional responses falsified (decisions bit-identical in
  all 60 episodes); a calibrated fitted prior consistently loses to hand-coded weights,
  consistent with a weight-scale mechanism.

See [`research/ROUND1_NOTE.md`](research/ROUND1_NOTE.md) for the artifact-status map:
which scripts/results cited by the note are mirrored here and which are pending push from
the working machine (no Round 1 number is unsupported by an artifact the authors do not
possess). All results: public seeds only, in-process timings, unadjusted p-values, fully
synthetic data.

## Prior phase: the 2×2 clarification × matcher factorial

The current repo-level primary experiment from the earlier phase is a matched
**2 × 2 clarification-policy × matcher factorial**, with the three supplied controls:

- 6 policies × 6 public scenario families × 10 public seeds = **360 policy–world rows**
  across **60 matched worlds**.
- Potential-ask versus default clarification, crossed with greedy versus general-graph
  maximum-weight matching; no-clarification greedy and random-feasible controls included.
- Phase result: the potential-ask main effect was **+0.117 MSMI per 100 arrived members**
  (95% seed-block bootstrap CI [+0.025, +0.208], exact two-sided sign-flip p = 0.0449,
  unadjusted); the matcher main effect was +0.058 (95% CI [−0.013, +0.129], p = 0.195).

**Status:** these numbers reproduce exactly under the Round 1 harness (Round 1 note §6),
but their interpretation is **superseded** by the 17-configuration factorial and the
structural analysis in the Round 1 note: the ask advantage saturates (any asking rule
reaches 97–98% of the coverage ceiling) and reverses in cold start. Treat this phase as
the exploratory record that motivated the supply-side question.

A separate soft-question experiment is secondary. Its three-seed screen showed a small
pilot uplift for hard-plus-soft questions with max-weight matching; the seven-seed public
holdout estimate was only **+0.024 MSMI/100** (95% CI [−0.071, +0.131], p = 0.844). It does
**not** establish a reliable soft-question benefit. Around 83 additional ask units per
episode were used with virtually unchanged coverage. This too is consistent with the
Round 1 note's residual-soft-ask null (H5).

See [`research/SCALED_FACTORIAL_RESULTS.md`](research/SCALED_FACTORIAL_RESULTS.md) for
full tables, scenario results, contrasts, caveats, and soft-question summaries, and
[`research/SIMULATION_OVERVIEW_AND_REQUIREMENTS_AUDIT.md`](research/SIMULATION_OVERVIEW_AND_REQUIREMENTS_AUDIT.md)
for the simulator/spec audit and limitations. The earlier 198-episode pilot is retained in
[`experiment_log.md`](experiment_log.md) and its historical output files.

## Research note drafts and form support

- [`research/RESEARCH_NOTE_ROUND1.pdf`](research/RESEARCH_NOTE_ROUND1.pdf) — the submitted
  Round 1 note (22 pages).
- [`research/ROUND1_NOTE.md`](research/ROUND1_NOTE.md) — artifact-status map and §9
  checklist for the note.
- [`research/RESEARCH_NOTE_DRAFT.md`](research/RESEARCH_NOTE_DRAFT.md) /
  [`research/RESEARCH_NOTE_DRAFT.docx`](research/RESEARCH_NOTE_DRAFT.docx) — the
  prior-phase draft, **superseded** by the Round 1 PDF; retained as the 2×2 record.
- [`research/GFORM_DRAFT_ANSWERS.md`](research/GFORM_DRAFT_ANSWERS.md) — concise draft
  answers mapped to the form fields, aligned to the Round 1 thesis.

The soft-question aggregate graph and data file use the published aggregate values
recorded in the results note. The user-VM row-level JSON files for the 3-seed screen and
7-seed soft-question holdout were not present when this bundle was prepared, so they are
not included. The ten-seed factorial's full row-level JSON is included.

## Figures and data

- `results/scaled_factorial_heatmap.png` — prior-phase six-policy/six-family result chart.
- `results/factorial_effects_forest.png` — ask, matcher, and interaction main effects with
  seed-block bootstrap intervals (prior phase).
- `results/policy_workflow.png` — method overview diagram.
- `results/soft_ask_holdout_aggregate.png` — overall soft-question holdout estimate and
  descriptive scenario point estimates.
- `results/scaled_factorial_10seeds.json` — all 360 core factorial rows and analysis
  summaries.
- `results/scaled_factorial_summary.csv`, `results/scaled_factorial_contrasts.csv` —
  readable factorial exports.
- Historical pilot and phase-screen artifacts are retained in `results/` and clearly
  identified as exploratory in the accompanying reports.

## Methods in brief

The potential-ask policy ranks available members by the number of plausible candidate
edges whose hard feasibility might be blocked by unknown constraints. This is a
**heuristic**, not an exact expected-value-of-information calculation. All known hard
constraints remain non-negotiable gates. The max-weight policy matches the currently
feasible general graph using observed similarity across seven soft fields; it does not
inspect hidden simulator truth. The controlled comparisons hold one of the clarification
or matching components fixed. The Round 1 note extends this with unlock-value ask ranking,
signed core-4 weighting, a fitted pair-outcome prior, residual soft asks and an online
adaptation variant — all ablated against the same components.

The core factorial's primary score is the equal-weight mean of MSMI per 100 arrived
members across six scenario families. Confidence intervals resample public seed blocks;
exact sign-flip tests use the ten seed-block differences. The reported *p*-values are
unadjusted for multiple contrasts. Rare, discrete outcomes and scenario heterogeneity
limit inference.

## Reproduce checks and analysis

Use the existing Python environment or create a virtual environment. The unittest command
runs one small episode as a smoke test; the two figure commands only regenerate plots from
saved outputs and do not run experiments.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests
python make_scaled_factorial_heatmap.py
python make_research_figures.py
# Optional: rebuild the editable prior-phase DOCX
python -m pip install -r requirements-report.txt
python tools/build_research_note.py
```

The runners for the larger simulations are included, but executing them re-runs episodes.
Do not run them just to preview this repository. Main runner files (prior phase):

- `scaled_factorial.py` — additional public seeds for the core factorial.
- `soft_ask_screen.py` — targeted soft-field screen.
- `soft_ask_validation_7seeds.py` — soft-question holdout.
- `phase_screen.py`, `phase_hybrid_policy.py`, `checkpoint_diagnostics.py`,
  `corrected_learning_rerun.py` — exploratory phase/learning diagnostics.

The Round 1 harness (`scripts/`) and its artifacts are listed in
[`research/ROUND1_NOTE.md`](research/ROUND1_NOTE.md); see the ⏳ rows for items pending
push from the working machine.

## Provenance and reuse

The bundled `starter/kit.py` is copied unchanged from public starter release 1.0.0 at
upstream commit `a8e26b35118cfa8e886a02f93984923e43ab64f6`. See `starter/SOURCE.md`,
`starter/LICENSE`, and `starter/DATA_LICENSE.md` for provenance and the upstream
code/data terms. The experiment code has no separate top-level open-source license; no new
license is implied by this bundle.

The detailed public-simulator experiments were run in-process; recorded wall times are not
official per-invocation subprocess or Docker timings. No private evaluator, private seed
set, Docker assessment, or real-user evaluation has been performed. Analysis-only scripts
marked as such read simulator ground truth and are never imported by any policy at
inference time. `SHA256SUMS.txt` lists checksums for the packaged files (excluding the
checksum list itself).
