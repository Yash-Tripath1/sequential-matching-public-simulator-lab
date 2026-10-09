# Pre-submission checklist — Round 1 (deadline 9 October 2026, 23:59 IST)

Work top to bottom. Items marked **[you]** require the working machine or the Google Form;
everything else is already done in this bundle.

## Repository (this bundle)

- [x] Round 1 PDF mirrored: `research/RESEARCH_NOTE_ROUND1.pdf`.
- [x] Artifact-status map + §9 checklist: `research/ROUND1_NOTE.md`.
- [x] Corrected note source mirrored: `research/RESEARCH_NOTE_FINAL.md` (four corrections;
      see below).
- [x] `README.md` leads with the Round 1 thesis; prior phase relabelled, nothing deleted.
- [x] `research/RESEARCH_NOTE_DRAFT.md` carries a SUPERSEDED header.
- [x] `research/GFORM_DRAFT_ANSWERS.md` rewritten to the supply-side thesis; no
      placeholder tokens in form-facing text.
- [x] `research/PROVENANCE_AND_ARTIFACT_STATUS.md` updated.
- [x] `UPLOAD_GUIDE.md` updated for this layout.
- [x] Smoke tests pass; figure-regeneration commands run clean.
- [x] Official reference baselines re-verified through the organisers' evaluator
      (54/54 episodes identical; `research/VERIFICATION_2026_10_09.md`,
      `results/reference_verification_3seeds.json`). Trusted-local subprocess mode —
      Docker/container validation remains Round 2 work.
- [x] `SHA256SUMS.txt` regenerated over the packaged files.
- [ ] **[you]** Push the pending Round 1 harness from the working machine:
      `scripts/*.py` (13 files), `build_note.py`, `make_pdf.py`, `assets/hard_priors.json`,
      `assets/outcome_prior.json`, and the Round 1 `results/` artifacts
      (`structure_diagnosis.json`, `supply_bounds.json`, logging-rollout shards,
      `outcome_model.json`, `variant_models.json`, `prior_specification.json`,
      `main_shard*.json`, `oracle_shard*.json`, `analysis.json`, `primary_summary.csv`,
      `attainable_ceiling.json`, `ask_timing.json`, new CSV exports). Then flip the ⏳ rows
      in `research/ROUND1_NOTE.md` to ✅ and regenerate `SHA256SUMS.txt` again.

## Note corrections (in `research/RESEARCH_NOTE_FINAL.md`; rebuild PDF if time allows)

1. §3.3 — age-window row now carries a conditioning note (the ~0.13 prior and the §3.2
   0.39 all-pairs pass rate measure different things). **Verify the description against
   `scripts/estimate_priors.py` on the working machine before relying on it** — it states
   only what the note itself supports (marginal used by the unlock prior, training-pool
   estimate).
2. §5.4 — Bonferroni threshold reworded: attainable in principle (min p ≈ 0.001 at 2¹⁰
   arrangements) but demanding, not "below the resolution".
3. §6.2c — "the myopic single-day linear objective is itself misspecified" softened to
   "consistent with a weight-scale mechanism", with the separable discriminating test
   (spread/rank-transformed prior) named as Round 2 work.
4. §6.1 — caption clarifies `% of ceiling` is pooled across families and that
   `results/primary_summary.csv` carries the per-seed coverage-to-ceiling ratios.
   **[you]** Add that per-seed ratio column to `primary_summary.csv` on the working
   machine (analysis-only recomputation from `supply_bounds.json` + episode rows; NO new
   simulator episodes) before pushing, so the caption is true.
- [ ] **[you, optional]** Rebuild the PDF from the corrected source with your own
      `make_pdf.py`; if filed as a form revision before 23:59 IST it supersedes the
      first upload. If there is no time, the submitted PDF stands and the corrected source
      documents the deltas — none of the four changes a number.

## PDF itself

- [ ] **[you]** Confirm the PDF carries the team name/author line and the declaration
      before upload (the bundle's copy has none visible).

## Google Form

- [ ] Copy field texts from `research/GFORM_DRAFT_ANSWERS.md`; edit to fit field limits.
- [ ] Upload the PDF (check any size limit; the bundled copy is ~230 KB).
- [ ] Link field: repository URL; if pinning a commit, use the commit URL with the
      40-character SHA from your push (a revision before the deadline replaces the entry).
- [ ] Verify and sign the declaration (list every AI tool/contributor actually used).
- [ ] Keep the form receipt timestamp.

## Do NOT do tonight

- No new simulator episodes (the note is frozen; new runs would only create mismatches).
- No changes to `starter/` or to prior-phase result files.
- No private evaluation, Docker timing claims, or real-world language anywhere.
