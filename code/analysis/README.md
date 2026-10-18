# Ad-hoc analysis scripts

These are the scripts that produced the tables in `REPORT.md` and `PAPER.md`
which are **not** covered by the clean-room pipeline in `../` (`waitlab.py`,
`analyse.py`, `ceilings.py`, `calibration.py`, `interaction.py`,
`wait_comparison.py`, `equivalence_check.py`).

They are included for provenance: every number in the write-ups is traceable to
a committed file, and in several cases the only route to that number is one of
these scripts. They are rougher than the pipeline modules and are preserved
essentially as-run.

## Caveat on paths

**Every script here has hardcoded absolute paths** (`/home/user/...`) pointing at
the machine the analysis was originally run on. They will not run as-is
elsewhere. Adjust the glob patterns and the `R =` / output paths at the top of
each file before use. This is left as a known defect rather than silently
rewritten, because changing the paths would make the committed copies
unfaithful to the runs that produced the reported numbers.

## Contents

| File | What it produced |
|---|---|
| `an120.py` | 120-seed pooled per-seed series, merging the 30-seed block with the 90-seed block |
| `an90.py` | 90-seed block (1131–1220) per-seed series from raw episode rows |
| `an_da.py` | Allocation-disparity decomposition, first version (three-leg: supply, ask allocation, realised access) |
| `an_da2.py` | Allocation-disparity decomposition, revised version with per-group power caveats |
| `mkresults.py` | Episode-level metrics assembled into the `results/` CSV and JSON tables |
| `pool.py` | Pool-level aggregation across families |
| `build_repo.py` | Assembles `repo_final/` from the working tree: licence, manifest, checksums, zip. Provenance for the packaged build. |
| `make_deck.py` | Builds the 15-slide presentation deck (PDF + PPTX) from the committed result files |

## The statistics module

`../restat.py` is **not** ad-hoc and has no hardcoded paths — it runs from the
repository root:

```bash
python3 code/restat.py     # writes results/restat_out.json
```

It is the single source of truth for every p-value, confidence interval and
W/T/L count in `REPORT.md` §5.13–5.15 and in `PAPER.md` §5. Its docstring
records why it exists: an earlier helper computed `order = sorted(...)` and then
never used it, so signed-rank values were assigned by position in an **unsorted**
array, making every p-value it produced meaningless. `restat.py` ranks by
magnitude correctly, averages ranks within tie groups, and applies the tie
correction to the variance.

It has been validated against `scipy.stats.wilcoxon` over 200 randomised cases
(differing n, tie density and effect size): **maximum absolute difference in
p = 0.0**.
