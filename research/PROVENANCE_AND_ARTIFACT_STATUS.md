# Provenance and artifact status

**Updated 9 October 2026 for the Round 1 submission.**

- The Round 1 research note was first submitted as `research/RESEARCH_NOTE_ROUND1.pdf`
  (kept as the submission record). Corrected/compact rebuilds live alongside it:
  `RESEARCH_NOTE_ROUND1_rev2.pdf` (full corrected note) and
  `RESEARCH_NOTE_ROUND1_rev3.pdf` (compact figure-driven revision), built by
  `research/build_pdf_rev2.py` / `build_pdf_rev3.py` from
  `RESEARCH_NOTE_FINAL.md` / `RESEARCH_NOTE_REV3.md`.
  Its editable source `RESEARCH_NOTE_FINAL.md` is mirrored in `research/` with four small
  corrections applied after the PDF was rendered (age-window conditioning note in §3.3,
  Bonferroni wording in §5.4, softened mechanism claim in §6.2c, per-seed coverage/ceiling
  caption in §6.1). The submitted PDF predates those corrections; a rebuilt PDF, if filed
  as a form revision before the deadline, supersedes it. The authoritative artifact-status
  map and §9 checklist live in `research/ROUND1_NOTE.md`.
- The Round 1 harness scripts (`scripts/`), inference assets (`assets/`) and Round 1
  result artifacts (structure/supply diagnosis, logging rollouts, outcome model, main and
  oracle shards, `analysis.json`, `primary_summary.csv`, `attainable_ceiling.json`,
  `ask_timing.json`) exist on the working machine and are pending push; see the ⏳ rows in
  `research/ROUND1_NOTE.md`. They are not reconstructed here.
- The main ten-seed prior-phase factorial is represented by the full 360-row
  `results/scaled_factorial_10seeds.json`, plus readable CSVs and figures.
- The original pilot, phase screen, corrected-learning rerun, and checkpoint diagnostics
  are retained as exploratory artifacts; see the matching reports for their status and
  limitations.
- The hard-plus-soft three-seed screen and seven-seed holdout were run on the user's
  Ubuntu VM. Their aggregate results are documented in `SCALED_FACTORIAL_RESULTS.md` and
  `results/soft_ask_holdout_aggregate.csv`, but the raw soft-run JSON files were not
  present in the shared workspace when this archive was assembled. Per-family soft-holdout
  points are therefore shown without uncertainty intervals, and the figure script uses the
  documented aggregate CSV.
- On 9 October 2026 the three official baselines were re-run through the organisers'
  reference evaluator (trusted-local subprocess mode, seeds 101/202/303 × six families):
  54/54 episodes valid and identical to the published factorial rows. See
  `VERIFICATION_2026_10_09.md` and `results/reference_verification_3seeds.json`. This is
  not Docker/container-mode validation.
- No private-evaluation data, private seeds, Docker results, or real-user data are
  included. Analysis-only oracle scripts (Round 1) write disclosed answers directly into
  simulator records for diagnosis only; no policy does this and no oracle output is
  available at inference time.
- The bundled organizer simulator snapshot is unchanged and carries its own MIT notice;
  see `starter/SOURCE.md` and `starter/LICENSE`.
- No separate license is asserted for the experiment code. This bundle does not add a
  top-level code license.
