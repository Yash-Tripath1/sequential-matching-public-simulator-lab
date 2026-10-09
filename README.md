# Sequential Matching — Public Simulator Research Lab

An exploratory study of budgeted clarification and online matching using the organizers' **public synthetic simulator**. This repository contains the policy prototypes, unchanged simulator snapshot, reproducible analysis code, available episode-level results, charts, and a draft research note.

> **Scope:** All reported episodes use public synthetic worlds. These results are not private-evaluation scores, Docker-validation results, real-user evidence, or evidence of real-world compatibility or product effectiveness.

## Current research status

The current primary experiment is a matched **2 × 2 clarification-policy × matcher factorial**, with the three supplied controls:

- 6 policies × 6 public scenario families × 10 public seeds = **360 policy–world rows** across **60 matched worlds**.
- Potential-ask versus default clarification, crossed with greedy versus general-graph maximum-weight matching.
- No-clarification greedy and random-feasible controls are included.
- Primary result: the potential-ask main effect is **+0.117 MSMI per 100 arrived members** (95% seed-block bootstrap CI **[+0.025, +0.208]**, exact two-sided sign-flip *p* = **0.0449**, unadjusted). The matcher main effect is **+0.058** (95% CI **[−0.013, +0.129]**, *p* = **0.195**). Treat these as exploratory public-simulator evidence, not a confirmed effect; the ask advantage reverses in cold start.

A separate soft-question experiment is secondary. Its three-seed screen showed a small pilot uplift for hard-plus-soft questions with max-weight matching; the seven-seed public holdout estimate was only **+0.024 MSMI/100** (95% CI **[−0.071, +0.131]**, *p* = **0.844**). It does **not** establish a reliable soft-question benefit. Around 83 additional ask units per episode were used with virtually unchanged coverage.

See [`research/SCALED_FACTORIAL_RESULTS.md`](research/SCALED_FACTORIAL_RESULTS.md) for full tables, scenario results, contrasts, caveats, and soft-question summaries. See [`research/SIMULATION_OVERVIEW_AND_REQUIREMENTS_AUDIT.md`](research/SIMULATION_OVERVIEW_AND_REQUIREMENTS_AUDIT.md) for the simulator/spec audit and limitations. The earlier 198-episode pilot is retained separately in [`experiment_log.md`](experiment_log.md) and its historical output files.

## Research note and form support

- [`research/RESEARCH_NOTE_DRAFT.docx`](research/RESEARCH_NOTE_DRAFT.docx) — a roughly 10-page section/page-break draft for review (verify final pagination in Word/LibreOffice); author details and declarations must be checked before submission.
- [`research/RESEARCH_NOTE_DRAFT.md`](research/RESEARCH_NOTE_DRAFT.md) — editable source.
- [`research/GFORM_DRAFT_ANSWERS.md`](research/GFORM_DRAFT_ANSWERS.md) — concise draft answers mapped to the form fields.

The soft-question aggregate graph and data file use the published aggregate values recorded in the results note. The user-VM row-level JSON files for the 3-seed screen and 7-seed soft-question holdout were not present when this bundle was prepared, so they are not included. The ten-seed factorial's full row-level JSON is included.

## Figures and data

- `results/scaled_factorial_heatmap.png` — main six-policy/six-family result chart.
- `results/factorial_effects_forest.png` — ask, matcher, and interaction main effects with seed-block bootstrap intervals.
- `results/policy_workflow.png` — method overview diagram.
- `results/soft_ask_holdout_aggregate.png` — overall soft-question holdout estimate and descriptive scenario point estimates. Scenario-specific intervals are not shown because raw soft-holdout rows are not bundled.
- `results/scaled_factorial_10seeds.json` — all 360 core factorial rows and analysis summaries.
- `results/scaled_factorial_summary.csv`, `results/scaled_factorial_contrasts.csv` — readable factorial exports.
- Historical pilot and phase-screen artifacts are retained in `results/` and clearly identified as exploratory in the accompanying reports.

## Methods in brief

The potential-ask policy ranks available members by the number of plausible candidate edges whose hard feasibility might be blocked by unknown constraints. This is a **heuristic**, not an exact expected-value-of-information calculation. All known hard constraints remain non-negotiable gates. The max-weight policy matches the currently feasible general graph using observed similarity across seven soft fields; it does not inspect hidden simulator truth. The controlled comparisons hold one of the clarification or matching components fixed.

The core factorial's primary score is the equal-weight mean of MSMI per 100 arrived members across six scenario families. Confidence intervals resample public seed blocks; exact sign-flip tests use the ten seed-block differences. The reported *p*-values are unadjusted for multiple contrasts. Rare, discrete outcomes and scenario heterogeneity limit inference.

## Reproduce checks and analysis

Use the existing Python environment or create a virtual environment. The unittest command runs one small episode as a smoke test; the two figure commands only regenerate plots from saved outputs and do not run experiments.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests
python make_scaled_factorial_heatmap.py
python make_research_figures.py
# Optional: rebuild the editable research-note DOCX
python -m pip install -r requirements-report.txt
python tools/build_research_note.py
```

The runners for the larger simulations are included, but executing them re-runs episodes. Do not run them just to preview this repository. Main runner files:

- `scaled_factorial.py` — additional public seeds for the core factorial.
- `soft_ask_screen.py` — targeted soft-field screen.
- `soft_ask_validation_7seeds.py` — soft-question holdout.
- `phase_screen.py`, `phase_hybrid_policy.py`, `checkpoint_diagnostics.py`, `corrected_learning_rerun.py` — exploratory phase/learning diagnostics.

## Provenance and reuse

The bundled `starter/kit.py` is copied unchanged from public starter release 1.0.0 at upstream commit `a8e26b35118cfa8e886a02f93984923e43ab64f6`. See `starter/SOURCE.md`, `starter/LICENSE`, and `starter/DATA_LICENSE.md` for provenance and the upstream code/data terms. The experiment code has no separate top-level open-source license; no new license is implied by this bundle.

The detailed public-simulator experiment was run in-process; recorded wall times are not official per-invocation subprocess or Docker timings. No private evaluator, private seed set, Docker assessment, or real-user evaluation has been performed. `SHA256SUMS.txt` lists checksums for the packaged files (excluding the checksum list itself).
