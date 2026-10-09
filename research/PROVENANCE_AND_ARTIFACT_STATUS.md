# Provenance and artifact status

- The main ten-seed factorial is represented by the full 360-row `results/scaled_factorial_10seeds.json`, plus readable CSVs and figures.
- The original pilot, phase screen, corrected-learning rerun, and checkpoint diagnostics are retained as exploratory artifacts; see the matching reports for their status and limitations.
- The hard-plus-soft three-seed screen and seven-seed holdout were run on the user's Ubuntu VM. Their aggregate results are documented in `SCALED_FACTORIAL_RESULTS.md` and `results/soft_ask_holdout_aggregate.csv`, but the raw soft-run JSON files were not present in the shared workspace when this archive was assembled. Per-family soft-holdout points are therefore shown without uncertainty intervals, and the figure script uses the documented aggregate CSV.
- No private-evaluation data, private seeds, Docker results, or real-user data are included.
- The bundled organizer simulator snapshot is unchanged and carries its own MIT notice; see `starter/SOURCE.md` and `starter/LICENSE`.
- No separate license is asserted for the experiment code. This bundle does not add a top-level code license.
