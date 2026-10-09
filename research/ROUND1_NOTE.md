# Round 1 research note — status and artifact map

**Submitted note:** [`research/RESEARCH_NOTE_ROUND1.pdf`](RESEARCH_NOTE_ROUND1.pdf) —
*"The One Introduction Problem: A supply-constrained sequential matching policy:
clarification targeting, outcome-relevant weighting, and variance-aware evaluation."*
Round 1 research note, Vouchsafe Sequential Matching Hackathon, starter release 1.0.0,
prepared 9 October 2026. Editable source: `RESEARCH_NOTE_FINAL.md` (maintained on the
working machine; see §9 checklist below for items pending push).

**Superseded draft:** [`RESEARCH_NOTE_DRAFT.md`](RESEARCH_NOTE_DRAFT.md) is retained as the
record of the earlier 2×2 factorial phase. Its headline (potential-ask targeting as a
suggestive positive effect, +0.117 MSMI/100) is **superseded** by the Round 1 note, whose
17-configuration factorial and structural analysis conclude that targeted asking is not
supported (H1) and that the score is supply-determined (H6). The older numbers are not
wrong; they are the prior phase and are reproduced exactly by the Round 1 harness
(Round 1 note §6, replication table).

## Thesis of the submitted note (one paragraph)

Under reciprocal hard feasibility, MSMI in this simulator is determined first by whether a
policy makes the feasible graph usable at all (a step function any asking rule saturates:
coverage 0.120 → ~0.342, MSMI/100 0.167 → ~0.45), second by how much of the resulting edge
supply it consumes before members exit (68–87%; no tested rule moved it), and only third,
within a band narrower than 60 episodes can resolve, by how well it ranks pairs. The single
pre-specified defended comparison is incumbent vs official greedy baseline: **+0.175
MSMI/100, 95% seed-block CI [+0.092, +0.258], p = 0.016, W/T/L 23/29/8**. The best screened
cell (potential asks + signed core-4 + global matching, 0.592) is a Round 2 candidate, not
a confirmed result. All results: public seeds only, in-process, synthetic; not private
evaluation, Docker assessment, or real-world evidence.

## §9 artifact checklist (PDF claim → repository path → status)

Legend: ✅ present in this repository · ⏳ on the working machine, pending push · 🗂 prior-phase artifact, present

### Round 1 harness and analysis (new)

| PDF §9 item | Path | Status |
|---|---|---|
| §3.1/§3.2 structure diagnosis | `scripts/diagnose_structure.py` | ⏳ pending push |
| §3.1 coverage ceilings / edge supply | `scripts/diagnose_supply.py` | ⏳ pending push |
| §3.3 hard-constraint marginals | `scripts/estimate_priors.py` | ⏳ pending push |
| §4.3 randomised logging rollouts | `scripts/log_rollouts.py` | ⏳ pending push |
| §4.3 specification search / fitted prior | `scripts/fit_prior.py` | ⏳ pending push |
| Runner, labels, bootstrap, sign-flip test | `scripts/harness.py` | ⏳ pending push |
| All candidate policies | `scripts/policies.py` | ⏳ pending push |
| §6 head-to-head (sharded) | `scripts/compare.py` | ⏳ pending push |
| §6.6 oracle ladder (analysis-only) | `scripts/oracle.py` | ⏳ pending push |
| §6.8 ask-saturation probe | `scripts/ask_timing.py` | ⏳ pending push |
| §7.1 arithmetic bound | `scripts/attainable_ceiling.py` | ⏳ pending push |
| §6.9 baseline equivalence check | `scripts/test_baseline_equivalence.py` | ⏳ pending push |
| Every §6 table → JSON/CSV exports | `scripts/analyse.py` | ⏳ pending push |
| Note build script | `build_note.py` | ⏳ pending push |
| PDF render script | `make_pdf.py` | ⏳ pending push |
| Inference asset: hard priors | `assets/hard_priors.json` | ⏳ pending push |
| Inference asset: outcome prior | `assets/outcome_prior.json` | ⏳ pending push |
| Structure diagnosis output | `results/structure_diagnosis.json` | ⏳ pending push |
| Supply bounds / ceilings | `results/supply_bounds.json` | ⏳ pending push |
| Logging rollout shards | `results/logging_rollouts.json` (+ shards) | ⏳ pending push |
| Outcome model | `results/outcome_model.json` | ⏳ pending push |
| Per-variant models | `results/variant_models.json` | ⏳ pending push |
| Prior specification search | `results/prior_specification.json` | ⏳ pending push |
| Head-to-head shards (17 configs) | `results/main_shard*.json` | ⏳ pending push |
| Oracle ladder shards | `results/oracle_shard*.json` | ⏳ pending push |
| All §6 contrasts incl. 136 pairwise | `results/analysis.json` | ⏳ pending push |
| Per-method summary + waiting times (+ per-seed coverage/ceiling ratios) | `results/primary_summary.csv` | ⏳ pending push |
| §7.1 attainable-score bound | `results/attainable_ceiling.json` | ⏳ pending push |
| §6.8 ask-timing probe output | `results/ask_timing.json` | ⏳ pending push |
| CSV/Markdown exports | `results/*.csv` (new) | ⏳ pending push |

### Prior-phase artifacts (already published here)

| Item | Path | Status |
|---|---|---|
| 3-seed pilot (198 episodes, 11 methods) | `results/public_pilot_results.json`, `experiment_log.md` | 🗂 present |
| Phase screen (90 episodes) | `results/phase_screen_3seeds.json`, `phase_screen.py` | 🗂 present |
| 10-seed 2×2 factorial (360 rows) | `results/scaled_factorial_10seeds.json` (+ CSVs, heatmap) | 🗂 present |
| Soft-ask 3-seed screen / 7-seed holdout | `results/soft_ask_holdout_aggregate.csv` (+ PNG) | 🗂 present (aggregates; row-level JSON not bundled) |
| Label-cutoff corrected rerun | `results/corrected_learning_rerun_3seeds.json` | 🗂 present |
| Checkpoint/ask-budget diagnostics | `results/checkpoint_diagnostics.json` | 🗂 present |
| Spec audit | `research/SIMULATION_OVERVIEW_AND_REQUIREMENTS_AUDIT.md` | 🗂 present |

## What a reviewer can check today vs after the pending push

- **Today:** the submitted PDF; every prior-phase artifact above (recompute primary scores
  from `results/scaled_factorial_10seeds.json`); the spec audit; smoke tests and
  figure-regeneration commands in the README.
- **After the pending push:** every table in PDF §3–§7 traces to a JSON/CSV artifact, and
  every figure/script in §9 exists at the listed path. `SHA256SUMS.txt` is regenerated with
  each push. Until then, the ⏳ rows above are the authoritative list of what is not yet
  mirrored here; no Round 1 number in this repository is unsupported by an artifact that the
  authors do not possess.

## Independent re-verification (9 October 2026)

The three official baselines were re-run through the organisers' own reference evaluator
(`evaluate.py` + `policy.py`, trusted-local subprocess mode) for seeds 101/202/303 across
all six families: 54/54 episodes valid and identical, episode-by-episode, to the lab's
published rows in `results/scaled_factorial_10seeds.json`. See
[`VERIFICATION_2026_10_09.md`](VERIFICATION_2026_10_09.md) and
`results/reference_verification_3seeds.json`.

## Honesty labels (apply to everything in this repository)

Exploratory public-simulator evidence · public seeds only · unadjusted p-values ·
in-process timings (not official per-invocation or Docker timings) · fully synthetic data ·
not private evaluation, not real-user evidence, not evidence of product effectiveness.
