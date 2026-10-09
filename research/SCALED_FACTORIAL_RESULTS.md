# Scaled public-seed run: clarification × matcher factorial

**Run date:** 8 October 2026 (UTC)  
**Simulator:** organizer release 1.0.0, public synthetic worlds only  
**Status:** exploratory; not private evaluation, Docker assessment, or real-world evidence.

## Executive result

I ran the core 2×2 factorial at **10 seeds per scenario family**, plus the two remaining official controls: 6 methods × 6 public variants × 10 seeds = **360 policy–world episodes**. This includes 252 newly run episodes for seeds 404, 505, 606, 707, 808, 909, and 1010, combined with the existing 108 valid control episodes for seeds 101, 202, and 303. The same public seed/variant worlds were used across methods. All episodes completed with valid simulator actions.

The main pattern is still that **potential-ask clarification helps more than changing the matcher** in this public screen. Averaged over the two matchers, the estimated ask-policy effect is **+0.117 MSMI/100** (10-seed-block bootstrap 95% CI **[+0.025, +0.208]**; exact two-sided sign-flip *p* = **0.045**). The estimated matcher effect is smaller, **+0.058 MSMI/100** (95% CI **[-0.013, +0.129]**; *p* = **0.195**).

Treat this as **suggestive, not conclusive**: the p-values are unadjusted for the several contrasts, the screen uses public rather than private seeds, and one MSMI in a 200-arrival episode moves that episode score by 0.5. The potential-ask advantage also reverses in cold start, especially against max-weight matching.

## Methods and comparisons

The factorial holds one component fixed while varying the other:

| Ask policy | Matcher | Run name |
|---|---|---|
| Default clarification | Starter greedy matcher | `greedy` |
| No clarification | Starter greedy matcher | `no_ask` |
| Default clarification | General-graph max-weight matching on 7 soft-field similarities | `max_weight_similarity` |
| Potential-ask heuristic | Starter greedy matcher | `potential_ask_greedy` |
| Potential-ask heuristic | General-graph max-weight matching on 7 soft-field similarities | `potential_ask` |
| Default clarification | Random feasible matcher | `random_feasible` |

The two supplied non-factorial controls, **no-clarification greedy** and **random-feasible**, are included. “Potential ask” is the existing heuristic, not exact VOI: it prioritizes members whose unknown hard constraints may block plausible edges. The global matching is on a **general graph**, not a bipartite graph. Hard feasibility remains a gate in every method.

### Clarification budget use: soft questions were not tested

You are right to flag the unused headroom. **None of the six methods in this run asked a named soft field.** The supplied default (`kit.baseline_asks`) asks the three-unit `constraints` bundle; the potential-ask heuristic also asks only that bundle, but ranks members by potential hard-feasibility unlocks. So this factorial tests *which members to clarify for hard constraints*, not whether to spend spare units on soft preferences.

For methods that asked, mean episode spend was about **196.7 of 720 theoretical units**, leaving roughly **523 units of arithmetic headroom**. The simulator permits a named soft-field question for **1 unit** (versus 3 for the whole hard-constraint bundle). However, the 12-unit limit resets each day—unused units do not carry over—and only currently available members can be asked. A good policy should not re-ask fields already observed or declined; declined answers stay unknown. An earlier, separate 18-episode diagnostic found the daily cap bound on a mean 15.1 of 60 days, so the 523-unit difference is not a portable balance that can all necessarily be spent later.

The seven soft fields are `relationship_goal`, `relationship_pace`, `lifestyle`, `conversations`, `emotional_availability`, `space_for_relationship`, and `relocate`. In this synthetic simulator, the first four directly enter the acceptance-probability mechanism; the matcher also uses observed soft-field similarities. The targeted core-soft screen was implemented in `soft_ask_screen.py` and completed on the user's Ubuntu VM: **72/72 new episodes valid**, three seeds in each of six public families. These are actual 60-day simulator rollouts, not placeholders, but only a three-seed screen.

### Three-seed soft-ask screen (exploratory)

| Method | MSMI / 100 | MSMIs across 18 episodes | Mean ask units | Hard bundles / episode | Core soft questions / episode | Coverage |
|---|---:|---:|---:|---:|---:|---:|
| Soft-only + greedy | 0.111 | 4 | 0.0 | 0.00 | 0.0 | 0.123 |
| Soft-only + max-weight | 0.139 | 5 | 0.0 | 0.00 | 0.0 | 0.122 |
| Hard-only + greedy | 0.611 | 22 | 194.0 | 64.67* | 0.0 | 0.348 |
| Hard-only + max-weight | 0.639 | 23 | 194.0 | 64.67* | 0.0 | 0.348 |
| Hard + targeted soft + greedy | 0.583 | 21 | 279.7 | 64.67 | 85.72 | 0.349 |
| **Hard + targeted soft + max-weight** | **0.722** | **26** | **279.9** | **64.67** | **85.94** | **0.348** |

\*The original pilot control rows predate explicit ask-count fields, so their hard-bundle count is correctly derived as ask cost ÷ 3. The first summary export displayed zero for this metadata field; that did **not** affect outcome scores or paired contrasts.

Paired on the same 18 public seed/family episodes, hard-plus-soft with greedy was **−0.028 MSMI/100** vs hard-only greedy (21 vs 22 events; W/T/L 0/17/1). Hard-plus-soft with max-weight was **+0.083 MSMI/100** vs hard-only max-weight (26 vs 23 events; W/T/L 3/15/0). For max-weight, the family differences were concentrated in cold start (+0.333) and delayed (+0.167); development, sparse, shift, and drift were ties. The soft-only arm asked **zero** questions: without asking hard constraints, it found no currently hard-feasible pairs to target and had much lower coverage. This supports testing soft questions *after* hard clarification, not replacing hard questions with soft ones.

These comparisons use only three seed blocks and rare discrete outcomes. The +3-event max-weight result was a **pilot signal, not confirmation**; the matcher was selected for a follow-up after seeing these pilot results.

### Seven-seed public holdout for hard-plus-soft max-weight

The follow-up ran 42 new episodes for seeds 404, 505, 606, 707, 808, 909, and 1010, paired against the already-run hard-only max-weight results for the same worlds.

| Group | Hard + soft + max-weight | Hard-only max-weight | Difference | 95% seed-block CI | Exact sign-flip *p* | W/T/L | MSMI events |
|---|---:|---:|---:|---:|---:|---:|---:|
| Held-out 7 seeds (42 episodes) | 0.500 | 0.476 | +0.024 | [−0.071, +0.131] | 0.844 | 8 / 29 / 5 | 42 vs 40 |
| Combined 10 seeds (descriptive only) | 0.567 | 0.525 | +0.042 | [−0.033, +0.117] | Not reported | 11 / 44 / 5 | 68 vs 63 |

The held-out estimate is small, its interval spans zero, and the exact sign-flip test gives no evidence of a reliable average gain. Soft asks cost about **83 extra units/episode** (mean total 280.6 vs 197.9) for this max-weight policy, while coverage was virtually unchanged (0.3407 vs 0.3407). Scenario differences in the holdout were mixed: shift +0.286, drift +0.071, delayed 0, sparse 0, development −0.071, and cold start −0.143 MSMI/100. The combined 10-seed figure includes the three pilot seed blocks used to select this arm; treat it as descriptive, not selection-free confirmation. The soft-only arms asked zero questions and were not expanded. No soft-ask private evaluation has been performed.

**Conclusion for the note:** retain the ten-seed clarification × matcher factorial as the main result. The soft-ask experiment is a useful negative/uncertain secondary result: a small pilot uplift did not replicate convincingly in the held-out public seeds. Do not claim that using the leftover ask budget on soft questions improves overall MSMI.

## Primary results

The primary estimate is the equal-weight mean of the six scenario-family means. CIs resample the ten public seed blocks, where each block averages that seed's six scenario scores.

| Method | MSMI / 100 | 95% seed-block bootstrap CI | MSMI events across 60 episodes | Coverage | Mean ask cost (units/episode) |
|---|---:|---:|---:|---:|---:|
| No clarification + greedy | 0.167 | [0.050, 0.292] | 20 | 0.120 | 0.0 |
| Random feasible | 0.358 | [0.267, 0.458] | 43 | 0.342 | 196.8 |
| Greedy + default asks | 0.350 | [0.233, 0.467] | 42 | 0.343 | 196.8 |
| Max-weight + default asks | 0.408 | [0.317, 0.500] | 49 | 0.342 | 196.8 |
| Potential asks + greedy | 0.467 | [0.367, 0.558] | 56 | 0.342 | 196.7 |
| **Potential asks + max-weight** | **0.525** | **[0.408, 0.633]** | **63** | 0.343 | 196.7 |

The event totals are the actual sum of qualifying MSMIs across the 60 episodes for each method. They are not percentages.

## Scenario means (MSMI per 100 arrived members)

Each cell is the mean over ten public seeds for that family.

| Method | Development | Sparse | Cold start | Delayed | Shift | Drift |
|---|---:|---:|---:|---:|---:|---:|
| No clarification + greedy | 0.300 | 0.000 | 0.000 | 0.150 | 0.250 | 0.300 |
| Random feasible | 0.500 | 0.050 | 0.350 | 0.400 | 0.350 | 0.500 |
| Greedy + default asks | 0.350 | 0.050 | 0.550 | 0.400 | 0.400 | 0.350 |
| Max-weight + default asks | 0.450 | 0.000 | 0.600 | 0.600 | 0.400 | 0.400 |
| Potential asks + greedy | 0.650 | 0.100 | 0.400 | 0.550 | 0.500 | 0.600 |
| Potential asks + max-weight | 0.800 | 0.100 | 0.400 | 0.550 | 0.550 | 0.750 |

Potential asks improved the development and drift means in this run, but **lost in cold start**: −0.150 with greedy and −0.200 with max-weight. Sparse outcomes remained rare. This is an important failure pattern to report rather than hide.

## Paired factorial contrasts

All contrasts are method A minus method B, paired on the same seed/variant episodes. CIs for the overall contrasts resample ten seed blocks. Exact sign-flip tests use the ten seed-block differences. W/T/L counts are over 60 paired episodes; per-scenario counts are over ten.

| Contrast | Mean difference | 95% seed-block CI | Sign-flip *p* | W/T/L |
|---|---:|---:|---:|---:|
| Potential asks − default asks, greedy matcher | +0.117 | [+0.042, +0.208] | 0.039 | 20 / 32 / 8 |
| Potential asks − default asks, max-weight matcher | +0.117 | [−0.017, +0.242] | 0.160 | 22 / 28 / 10 |
| Max-weight − greedy, default asks | +0.058 | [−0.067, +0.175] | 0.445 | 14 / 40 / 6 |
| Max-weight − greedy, potential asks | +0.058 | [0.000, +0.117] | 0.172 | 8 / 50 / 2 |

The factorial main effects were:

| Effect | Mean | 95% seed-block CI | Sign-flip *p* |
|---|---:|---:|---:|
| Ask policy (potential vs default, averaged over matchers) | +0.117 | [+0.025, +0.208] | 0.045 |
| Matcher (max-weight vs greedy, averaged over asks) | +0.058 | [−0.013, +0.129] | 0.195 |
| Ask × matcher interaction | 0.000 | [−0.117, +0.125] | 1.000 |

The ask result against default greedy is the clearest contrast here; against default max-weight its CI includes zero. These are unadjusted exploratory tests, not a claim of a confirmed effect. There is no reliable evidence in this run that changing greedy to max-weight is the primary lever.

## Secondary metrics and reading the funnel

At essentially unchanged coverage and assignment counts, potential asks were associated with more intermediate successes:

| Method | Mean assignments | Mean mutual acceptances | Mean dates | Mean MSMIs | Mean missing feedback |
|---|---:|---:|---:|---:|---:|
| Greedy + default asks | 77.35 | 10.75 | 8.52 | 0.70 | 40.33 |
| Max-weight + default asks | 76.57 | 11.15 | 8.58 | 0.82 | 40.87 |
| Potential asks + greedy | 76.52 | 11.68 | 9.05 | 0.93 | 39.17 |
| Potential asks + max-weight | 76.40 | 12.12 | 9.33 | 1.05 | 39.43 |

This is consistent with a pair-quality/funnel hypothesis, not proof that clarification itself caused a real-world improvement. It also reinforces why mutual acceptance is not the primary outcome: an introduction, two Yes responses, and a date do not necessarily become MSMI.

## Methods and limitations

- Public simulator only: 10 public seeds per family. The official private ranking uses 20 private seeds per family; this is not a substitute for it.
- The analysis is in-process. All actions were simulator-valid, but this scaled batch was not a subprocess or Docker timing test.
- Primary-score bootstrap resamples ten seed blocks (10,000 draws; analysis seed 20261009). Scenario CIs in the JSON resample ten episodes within each family. Paired sign-flip tests are exact over the ten seed-block means.
- No multiplicity correction was applied across contrasts. Use “suggestive public-simulator evidence,” not “statistically proven.”
- Outcomes are discrete and scarce; all conclusions need scenario-level caveats, particularly cold start and sparse geography.
- The simulator and its outcomes are synthetic. Nothing here estimates relationship compatibility or product effectiveness for real people.

## Recommendation for the Round 1 note

Use the factorial as the main experimental design. State the narrow hypothesis as: **with hard constraints enforced, allocating clarification to members whose unknown constraints block promising edges may improve MSMI; changing the global matcher may have a smaller effect.** Report the 10-seed public result with the unadjusted uncertainty and the cold-start reversal. Keep the phase hybrids as a separate exploratory result; the earlier three-seed 4-phase advantage was only one extra event over its fixed control and is subject to winner's-curse selection.

Anything not completed—20-seed public runs, a full funnel/cold-start autopsy, true expected-value-of-information asks, or container testing—should be labelled **planned**, not implied to be done. The competition spec does not require a ten-page note; accuracy and the listed required elements matter more than length tonight.

## Reproduction artifacts

- `scaled_factorial.py` — reproducible runner; 7 added public seeds.
- `make_scaled_factorial_heatmap.py` — regenerates the heatmap from the combined JSON.
- `soft_ask_screen.py` — resumable 3-seed process-pool screen for targeted core-soft asks; 72 user-VM episodes completed valid.
- `soft_ask_validation_7seeds.py` — held-out seven-seed runner for hard-plus-soft max-weight only; the 42 held-out public episodes completed on the user's Ubuntu VM. The raw output JSON was not present in this shared bundle; its aggregate is reported above.
- `results/scaled_factorial_10seeds.json` — all 360 full episode rows, summaries, CIs, contrasts, and factorial effects.
- `results/scaled_factorial_summary.csv` — policy-level primary/secondary summary.
- `results/scaled_factorial_contrasts.csv` — paired scenario-level contrasts and W/T/L.
- `results/scaled_factorial_heatmap.png` — scenario and overall-score figure.
- Original pilot rows for seeds 101/202/303 remain in `results/public_pilot_results.json`.
