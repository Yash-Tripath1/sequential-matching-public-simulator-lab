# Sequential Matching — Experiment Log

**Updated:** 8 October 2026  
**Starter release:** 1.0.0  
**Status:** exploratory public-simulator pilot; not a private-evaluation result

## What we tested

We ran the organisers' public simulator with the six published scenario variants: `development`, `sparse`, `cold_start`, `delayed`, `shift`, and `drift`. Each method was tested on the same three public seeds (101, 202, 303): **18 scored episodes per method**. The primary number below is the equal-weight average of MSMI per 100 arrived members across the six variants, matching the structure of the published score.

All **198 in-process episodes completed with legal simulator actions** (11 methods × 18 cases). The official starter tests and data verification had also passed earlier. The GA used a separate small training split: seeds 23 and 47 on development, sparse and drift (six train cases per candidate), with population 6 and 2 generations. Its selected weights were then tested on the 18 held-out cases.

## Results

| Method | Mean MSMI / 100 | Mean coverage | Mutual accepts / 100 | Mean ask cost |
|---|---:|---:|---:|---:|
| Potential asks + max-weight similarity (7 soft fields) | **0.639** | 0.348 | 6.42 | 194.0 |
| Potential asks + starter greedy matcher | **0.611** | 0.348 | 6.00 | 194.0 |
| Contextual Thompson pattern | 0.472 | 0.347 | 5.89 | 194.2 |
| Starter greedy | 0.389 | 0.349 | 6.08 | 194.2 |
| GP surrogate + UCB (`mean + 1σ`) | 0.389 | 0.345 | 6.36 | 194.2 |
| Max-weight similarity, default asks (7 soft fields) | 0.389 | 0.347 | 6.08 | 194.2 |
| Random feasible | 0.278 | 0.348 | 5.86 | 194.2 |
| GP surrogate, mean only | 0.222 | 0.336 | 4.97 | 194.2 |
| GA-tuned four-feature weights | 0.222 | 0.345 | 5.83 | 194.2 |
| Core-feature max-weight matching, equal weights, default asks | 0.194 | 0.345 | 5.61 | 194.2 |
| No clarification + starter greedy matcher | 0.111 | 0.123 | 1.81 | 0.0 |

### MSMI / 100 by scenario

| Method | Dev. | Sparse | Cold start | Delayed | Shift | Drift |
|---|---:|---:|---:|---:|---:|---:|
| Starter greedy | 0.33 | 0.00 | 0.83 | 0.50 | 0.33 | 0.33 |
| No clarification | 0.17 | 0.00 | 0.00 | 0.17 | 0.17 | 0.17 |
| Random feasible | 0.17 | 0.00 | 0.33 | 0.50 | 0.50 | 0.17 |
| Max-weight similarity, default asks | 0.33 | 0.00 | 0.50 | 0.67 | 0.50 | 0.33 |
| Thompson pattern | 0.50 | 0.00 | 0.83 | 0.50 | 0.50 | 0.50 |
| GP mean only | 0.17 | 0.00 | 0.33 | 0.50 | 0.17 | 0.17 |
| GP-UCB | 0.50 | 0.00 | 0.33 | 0.50 | 0.50 | 0.50 |
| GA-tuned | 0.17 | 0.00 | 0.33 | 0.50 | 0.17 | 0.17 |
| Core max-weight, equal weights + default asks | 0.17 | 0.00 | 0.33 | 0.33 | 0.17 | 0.17 |
| Potential asks + max-weight similarity | 1.17 | 0.00 | 0.17 | 0.50 | 0.83 | 1.17 |
| Potential asks + starter greedy | 1.00 | 0.00 | 0.33 | 0.50 | 0.83 | 1.00 |

## What we saw (carefully)

1. **Clarification mattered in this starter.** No-ask coverage averaged 12.2%, versus roughly 34–35% for the other methods; its primary score was also much lower. In this simulator, unknown hard constraints block otherwise possible pairs.
2. **The potential-ask heuristic was promising in two controlled comparisons.** It ranked people by how many plausible edges their hard-constraint clarification might unlock. With the same starter greedy matcher, it scored 0.611 vs 0.389 for default asks; on paired worlds it won 8, tied 8 and lost 2. With the same seven-soft-field maximum-weight matcher, it scored 0.639 vs 0.389 for default asks; again, 8 wins, 8 ties and 2 losses. Ask costs were effectively the same. These comparisons change the ask policy while holding the matching method fixed. They are a promising signal, **not proof**: only three seeds per scenario, and the heuristic is not exact expected value of information.
3. **The matcher change was small under potential asks.** Holding potential asks fixed, seven-soft-field maximum-weight matching scored 0.639 vs 0.611 with the starter greedy matcher (2 wins, 15 ties, 1 loss). This is too small/noisy to call a reliable win. Separately, default-ask max-weight similarity and starter greedy both averaged 0.389, but that comparison changes scoring details as well as the matching procedure, so it does not isolate the algorithm alone.
4. **Exploration had mixed results.** The coarse-pattern Thompson policy scored 0.472; GP-UCB scored 0.389, while GP mean-only scored 0.222. The UCB bonus helped over the same GP mean model in this pilot. This does not establish that either sophisticated policy is better than a tuned baseline.
5. **The tiny GA did not find a useful weight change.** It selected equal weights for relationship goal, pace, lifestyle and conversation style. Training performance tied with other candidates; held-out score was 0.222, close to the equal-weight core-matcher control at 0.194 (1 win, 17 ties, 0 losses across the paired cases). The run had only 10 distinct candidates and two generations, so this is mainly evidence that this **small, noisy search** was inconclusive.
6. **Sparse geography was the hard case.** All methods scored zero MSMIs on the three sparse episodes. Their coverage was also far lower. More seeds and a careful look at candidate scarcity are needed before drawing conclusions.

One MSMI in an episode with 200 arrivals changes that episode's score by 0.5. Most episode scores are therefore zero or a small multiple of 0.5; these small samples are noisy. Don’t treat the ranking as statistically settled.

## What each prototype actually was

- **Greedy / no-ask / random-feasible:** the supplied baselines. No-ask uses the starter greedy matcher but asks no clarifications; random-feasible uses the standard hard-constraint ask routine and samples valid pairs.
- **Max-weight similarity:** maximum-weight matching on the general graph of currently feasible pairs, using observed matches across all seven soft fields as weights.
- **Core max-weight control:** maximum-weight matching using equal weights on the four core fields, with the standard ask routine. This is also the comparison baseline for the GA-tuned core weights.
- **Thompson pattern:** Beta(1,1) posteriors over coarse observable pair-pattern groups; updates only when an MSMI outcome is mature and visible.
- **GP mean / GP-UCB:** a simple online Gaussian-process surrogate over observable pair-context features, trained on completed MSMI outcomes; UCB adds one posterior standard deviation. These are proof-of-concept implementations, not tuned production models.
- **Potential ask:** a heuristic that spends hard-constraint clarification units on available members with the most plausible currently blocked edges. It does not compute full mathematical VOI and does not ask soft-field questions. The seven-soft max-weight version differs from its default-ask control only in which members it asks; the greedy-matcher version provides a second ask-only control.
- **GA-tuned:** a small offline GA tunes four soft-match weights for a core-feature maximum-weight matching heuristic. GA is the tuner; it is not the per-day policy itself.

## Limitations / what this does *not* prove

- Only public synthetic simulator worlds were used. No private seeds, private evaluation, real people or real relationship outcomes were accessed.
- The public run uses 3 seeds per variant. For rare MSMI outcomes, that is nowhere near enough to declare a winner.
- The bulk runner is in-process to make experiments practical. Its wall times are not the official per-invocation 10-second subprocess or offline-Docker timings.
- The Thompson, GP, GA and potential-ask methods are deliberately small prototypes. They need better calibration, more training data and stronger validation before any competition submission.
- Do not interpret the simulator's synthetic outcomes as real-world compatibility or product effectiveness.

## Files

- `experiment_lab.py` — policy prototypes and public-simulator runner.
- `run_suite.py` — full pilot and GA search.
- `run_controls.py` — paired controls for ask policy vs matching method.
- `results/public_pilot_results.json` — per-episode metrics and summary.
- `results/summary.csv`, `results/by_variant.csv`, `results/episode_results.csv` — spreadsheet-friendly exports.
- overall comparison and scenario heatmap: superseded by `research/figures/fig1_msmi_forest.png` and `fig3_family_heatmap.png` (Round 1 figure set).
- `results/ga_search_history.json`, `results/ga_selected_weights.json` — GA record.
- `starter/kit.py` — unchanged public simulator snapshot; provenance and licenses are alongside it.

The upstream checkout was left unchanged. This experiment folder bundles the exact `kit.py` used so it can be reproduced independently.
