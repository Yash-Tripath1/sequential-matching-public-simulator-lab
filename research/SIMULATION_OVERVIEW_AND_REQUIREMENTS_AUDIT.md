# Sequential Matching — simulation screen and spec audit

**Prepared:** 8 October 2026 (UTC)  
**Release checked:** organizer starter kit 1.0.0  
**Scope:** public synthetic simulator only; this is not a private-evaluation result or a real-world compatibility estimate.

## Executive summary

I checked the organizer's actual release against the proposed Gemini checklist, then ran both a three-seed phase screen and a scaled ten-seed clarification × matcher factorial on the public simulator. In the original phase screen, the four-phase schedule led by only one event; that hybrid was not retested in the scaled factorial. The stronger current research framing is the potential-ask hypothesis, with a small, exploratory positive ask effect and a cold-start reversal; the matcher effect remains uncertain. Full scaled tables are in `SCALED_FACTORIAL_RESULTS.md`.

The scaled follow-up completed **360 valid policy–world episodes**: six methods × six scenario families × ten public seeds. The average potential-vs-default ask effect was **+0.117 MSMI/100** (95% seed-block bootstrap CI **[+0.025, +0.208]**, exact two-sided sign-flip *p* = **0.045**, unadjusted). The average max-weight-vs-greedy effect was **+0.058** (95% CI **[−0.013, +0.129]**, *p* = **0.195**). These are suggestive public-simulator results only—not private evaluation or confirmatory evidence; potential asks lost in cold start.

A separate correctness issue surfaced in the existing exploratory code: its online outcome-label helper did not enforce the official 30-day first-date deadline. I fixed it in the workspace copy and reran the three learned baselines on the same public cases; their scores and per-episode outcomes were unchanged. The phase-screen learners use the corrected online label; static policies do not learn from labels, and all reported scores are calculated by the simulator's official metric.

## Quick environment and execution checks

- The official starter's 22 unit tests pass; `verify_data.py` confirms 2,000 members, 613 introductions, 1,270 feedback events, 1,129 conversation records, and 71 data files.
- Your experiment lab's 2 smoke tests pass.
- The official `kit.py` is byte-for-byte identical to the copy bundled in your experiment lab.
- The new in-process screen completed **90 valid episodes**: five new policy variants × six public variants × three seeds (101, 202, 303). The simulator rejected no actions.
- I also ran the four-phase policy through the official JSON subprocess evaluator for seed 101 across all six public variants. All six episodes were valid. Its equal-variant score was 0.583 MSMI/100, with 0.409 coverage, 7.08 mutual acceptances/100, and 205 clarification units. The same one-seed public run gave 0.500 for greedy, 0.333 for no-asks, and 0.250 for random-feasible. Treat all four as protocol smoke checks, not performance claims. This was local subprocess mode, not Docker-container validation.

## What was tested

The same potential-ask clarification heuristic was held fixed to isolate the matching schedule. Each method obeyed the public eligibility function; Thompson/GP scores only ranked feasible edges. Learning methods updated from assignment-time observed features and feedback visible by the current day. Hybrid phases share one learning history rather than discarding early observations when the matcher changes.

- **Potential asks + Thompson:** Thompson pattern sampling for all 60 decision days.
- **Potential asks + GP-UCB:** GP-UCB matching for all 60 days.
- **4-phase hybrid:** starter greedy on days 0–14; Thompson on 15–29; GP-UCB on 30–44; greedy on 45–59.
- **6-phase hybrid:** 10-day blocks: greedy → Thompson → GP-UCB → Thompson → GP-UCB → greedy.
- **Adaptive hybrid:** greedy on 0–14; between days 15–44 use Thompson until at least eight mature labels and both label classes are visible, then GP-UCB; return to greedy on 45–59.

The phase boundaries and adaptive threshold are exploratory choices, not optimized parameters. The Thompson and GP implementations are the small pilot prototypes from the experiment lab, not production-tuned models.

## Results: exploratory public screen (three-seed pilot)

This section records the earlier three-seed screen; the latest scaled factorial follows it below. Each row is an equal-weight average across six scenario variants, with **three seeds per variant**. Control rows are from your checked-in pilot on the same public seeds and variants; the new rows are from the 90-episode screen. Higher MSMI is better. Coverage and mutual acceptance are descriptive secondary metrics, not substitutes for MSMI.

| Policy | MSMI / 100 | MSMIs across 18 episodes | Coverage | Mutual accepts / 100 | Mean ask cost |
|---|---:|---:|---:|---:|---:|
| Greedy + default clarification (official baseline) | 0.389 | 14 | 0.349 | 6.08 | 194.2 |
| No clarification + greedy (official baseline) | 0.111 | 4 | 0.123 | 1.81 | 0.0 |
| Random feasible (official baseline) | 0.278 | 10 | 0.348 | 5.86 | 194.2 |
| Potential asks + starter greedy | 0.611 | 22 | 0.348 | 6.00 | 194.0 |
| Potential asks + 7-soft-field max-weight matching | 0.639 | 23 | 0.348 | 6.42 | 194.0 |
| Potential asks + Thompson | 0.139 | 5 | 0.350 | 6.44 | 194.0 |
| Potential asks + GP-UCB | 0.472 | 17 | 0.349 | 6.72 | 194.0 |
| **4-phase hybrid: G → TS → GP-UCB → G** | **0.667** | **24** | 0.349 | 6.28 | 194.0 |
| 6-phase hybrid: G/TS/GP/TS/GP/G | 0.500 | 18 | 0.347 | 6.42 | 194.0 |
| Adaptive hybrid | 0.611 | 22 | 0.349 | 6.17 | 194.0 |

### Scenario breakdown (MSMI per 100 arrived members)

| Policy | Development | Sparse | Cold start | Delayed | Shift | Drift |
|---|---:|---:|---:|---:|---:|---:|
| Potential asks + 7-soft max-weight | 1.167 | 0.000 | 0.167 | 0.500 | 0.833 | 1.167 |
| Potential asks + starter greedy | 1.000 | 0.000 | 0.333 | 0.500 | 0.833 | 1.000 |
| Potential asks + Thompson | 0.167 | 0.000 | 0.167 | 0.000 | 0.333 | 0.167 |
| Potential asks + GP-UCB | 0.833 | 0.000 | 0.167 | 0.500 | 0.500 | 0.833 |
| **4-phase hybrid** | **1.167** | **0.000** | 0.167 | **0.667** | 0.833 | **1.167** |
| 6-phase hybrid | 0.833 | 0.000 | 0.167 | 0.500 | 0.667 | 0.833 |
| Adaptive hybrid | 1.000 | 0.000 | 0.167 | 0.667 | 0.833 | 1.000 |

Because each episode has 200 arrivals, an 18-episode score converts to event count as `MSMI/100 × 36`: the four-phase policy has 24 events versus 23 for potential-ask + max-weight, a net **one event**. Its paired comparison against potential-ask + max-weight on the same 18 seed/variant cases was 3 wins, 13 ties, 2 losses; its mean difference was only +0.028 MSMI/100. Against potential-ask + greedy it was 3 wins, 14 ties, 1 loss (+0.056 MSMI/100). These are not persuasive evidence of a reliable improvement; a simple two-sided sign test on the 10 non-tied max-weight comparisons is about p=0.11. With 200 arrivals, a single MSMI changes an episode score by 0.5 per 100, so rare outcomes make a three-seed-per-variant screen very noisy. All tested methods scored zero in the three sparse episodes.

The four-phase result was one of several schedules screened, so the maximum is also subject to winner's-curse selection. The cleanest research framing is a 2×2: default vs potential asks, crossed with greedy vs general-graph max-weight matching. In the original pilot, potential asks beat default asks 8/8/2 (wins/ties/losses) with each matcher; a simple two-sided sign test is about p=0.11, so call this suggestive, not significant. Changing max-weight to greedy under potential asks was only 2/15/1 and about one event, consistent with matching being a secondary question. Potential asks also underperformed the default-ask controls in cold start: 0.167 vs 0.500 with max-weight matching and 0.333 vs 0.833 with the greedy matcher (only three episodes per variant); that failure mode should stay visible.

A follow-up label-availability diagnostic on the same 18 public cases found median mature labels of **17 by day 15, 46.5 by day 30, and 70.5 by day 45**, but median positive labels of **0, 1, and 1**, respectively. So "label starvation" needs qualification: the primary target has scarce positives, but the policy sees many mature negative MSMI labels early. The adaptive rule reached its threshold (at least eight mature labels and both classes) in 13/18 episodes, with median first GP-UCB day 25; it did not switch in 5/18. Sparse episodes had no positive labels in these three seeds. Report this as a small diagnostic, not a general rate.

Mean episode ask cost of about 194 is cumulative clarification units: the simulator's `ask_cost` is `asks_total`, and 12 × 60 gives a 720-unit episode ceiling. That's about 27% of total capacity, **but the daily cap did bind**: with the potential-ask rule, it used all 12 units on a mean 15.1 days per 60-day episode (all 18 diagnostic episodes hit the cap at least once), and asked on a mean 17.7 days. Thus aggregate budget was not exhausted, while per-day capacity constrained choices on many days.

**Interpretation:** the proposed 4-phase mixture is a reasonable hypothesis to carry forward, not a winner to claim. The 6-phase schedule did not help in this small screen. The static Thompson and GP variants did not beat the existing potential-ask controls. More complexity did not automatically help.

![Exploratory scenario heatmap and overall pilot scores](results/phase_screen_heatmap.png)

## Scaled follow-up: 10 public seeds per family

**Run date:** 8 October 2026 (UTC). The core clarification × matcher 2×2 was run at ten seeds in each of the six public families, alongside no-clarification and random-feasible controls. There are **60 matched public worlds and 360 method–world rows** (252 new rows plus the existing 108 rows for seeds 101, 202, and 303); every episode completed with valid simulator actions. This is still an in-process public-simulator run, not a private evaluation or Docker timing test.

| Method | MSMI / 100 | 95% seed-block bootstrap CI | MSMIs across 60 episodes |
|---|---:|---:|---:|
| No clarification + greedy | 0.167 | [0.050, 0.292] | 20 |
| Random feasible | 0.358 | [0.267, 0.458] | 43 |
| Greedy + default asks | 0.350 | [0.233, 0.467] | 42 |
| Max-weight + default asks | 0.408 | [0.317, 0.500] | 49 |
| Potential asks + greedy | 0.467 | [0.367, 0.558] | 56 |
| **Potential asks + max-weight** | **0.525** | **[0.408, 0.633]** | **63** |

The ask main effect (potential vs default, averaged across matchers) was **+0.117 MSMI/100**, CI **[+0.025, +0.208]**, exact two-sided seed-block sign-flip *p* = **0.0449**. The matcher main effect was **+0.058**, CI **[−0.013, +0.129]**, *p* = **0.1953**; the ask × matcher interaction was **0.000**, CI **[−0.117, +0.125]**, *p* = **1.0**. The potential-vs-default ask contrast was +0.117 with greedy matching (CI [+0.042, +0.208], *p* = 0.0391, W/T/L 20/32/8) and +0.117 with max-weight (CI [−0.017, +0.242], *p* = 0.1602, W/T/L 22/28/10). No multiplicity correction was applied; these are exploratory values, not a confirmed finding.

**Important scope gap: no method in the factorial asked a named soft field.** Default and potential policies asked only the three-unit hard `constraints` bundle. At about 196.7 units used out of 720 theoretical units, each asking method left approximately 523 units of arithmetic headroom. The cap is 12 per day and resets; unused daily units cannot be carried forward. Soft-field questions cost one unit and could affect matching scores, but their value was not tested. Earlier diagnostics found the daily cap bound on a mean 15.1 days; see `SCALED_FACTORIAL_RESULTS.md` for the proposed targeted soft-ask ablation.

Scenario heterogeneity is consequential. Potential asks were worse in cold start by **0.150** against default asks with greedy and **0.200** against default asks with max-weight. Gains were concentrated more in development and drift (also positive in shift); sparse outcomes remained rare. Do not omit the cold-start failure or generalize beyond the public synthetic simulator. The scaled factorial updates the original three-seed comparisons for the four static methods, but it did **not** retest phase hybrids or the learning methods; their pilot results remain three-seed exploratory results.

### Subsequent 3-seed soft-field screen (exploratory)

The user ran 72 additional valid public-simulator episodes (four ask/matcher methods × six families × seeds 101/202/303). These are real full rollouts on public synthetic worlds, but only three seed blocks per family.

| Method | MSMI / 100 | Events / 18 episodes | Ask units / episode | Soft questions / episode | Coverage |
|---|---:|---:|---:|---:|---:|
| Soft-only + greedy | 0.111 | 4 | 0.0 | 0.0 | 0.123 |
| Soft-only + max-weight | 0.139 | 5 | 0.0 | 0.0 | 0.122 |
| Hard-only + greedy | 0.611 | 22 | 194.0 | 0.0 | 0.348 |
| Hard-only + max-weight | 0.639 | 23 | 194.0 | 0.0 | 0.348 |
| Hard + targeted soft + greedy | 0.583 | 21 | 279.7 | 85.72 | 0.349 |
| **Hard + targeted soft + max-weight** | **0.722** | **26** | **279.9** | **85.94** | **0.348** |

Hard-plus-soft vs hard-only, paired over 18 worlds: greedy **−0.028** MSMI/100, 21 vs 22 events, W/T/L 0/17/1; max-weight **+0.083**, 26 vs 23 events, W/T/L 3/15/0. The max-weight advantage appeared in cold start (+0.333) and delayed (+0.167), with ties elsewhere. Soft-only asked no questions because no edges passed hard feasibility; it is not a useful substitute for hard clarification. These 3-seed results are a hypothesis-generating screen, not confirmation.

The first screen summary mistakenly showed zero hard-constraint bundles for old hard-only pilot controls because their rows lacked explicit ask-count fields; those rows spent 194 units/episode, equivalent to 64.67 three-unit bundles. That is a reporting-metadata issue only; score calculations and paired contrasts are unaffected. The corrected summarizer derives bundle counts from ask cost for those controls.

A held-out seven-seed follow-up for hard-plus-soft max-weight was run as 42 new episodes on seeds 404, 505, 606, 707, 808, 909, and 1010, paired against existing hard-only max-weight rows for those worlds. The held-out primary score was **0.500 vs 0.476 MSMI/100**, a +0.024 difference (95% seed-block bootstrap CI **[−0.071, +0.131]**, exact sign-flip *p* = **0.844**, W/T/L 8/29/5; 42 vs 40 MSMI events). This does **not** establish a reliable average benefit. The most favorable scenario was shift (+0.286); cold start moved negatively (−0.143); four families were zero or near zero. Hard-plus-soft used about 83 additional ask units per episode with virtually unchanged coverage. The combined ten-seed estimate (+0.042, CI [−0.033, +0.117]) includes the three pilot seed blocks used to select the policy and is descriptive only. Treat the held-out result as exploratory public evidence; it is not private evaluation.

For bootstrap intervals, the primary score and paired contrasts resample ten seed blocks (10,000 draws; analysis RNG seed 20261009); the exact sign-flip tests use the ten seed-block differences. Primary score equally weights the six family means. Full methods, all scenario means, paired contrasts, and limitations are in `SCALED_FACTORIAL_RESULTS.md`; machine-readable artifacts are `results/scaled_factorial_10seeds.json`, `results/scaled_factorial_summary.csv`, and `results/scaled_factorial_contrasts.csv`.

![Scaled ten-seed scenario heatmap and primary-score intervals](results/scaled_factorial_heatmap.png)

## Important code audit: MSMI training-label cutoff

The original `experiment_lab.py` helper `mature_primary_label` could label a date followed by two timely second-meeting Yes responses as positive **without checking that the date occurred within 30 days of assignment**. The official outcome requires that deadline. In the three public delayed seeds, this produced one label mismatch for the old Thompson-pattern run (seed 303: assigned day 31, date day 62, i.e. 31 days after assignment); no such mismatch appeared in the three GP-UCB/GP-mean checks. The audit sample is small.

I patched the helper in the workspace copy and reran Thompson, GP-mean, and GP-UCB on the same 18 seed/variant cases each. **Every per-episode outcome and aggregate score was identical** to the old run (paired W/T/L = 0/18/0 for each method). The one late-date label became observable only after the day-59 decision horizon, so it could not have changed those episodes' decisions. The stored pilot scores for these seeds are therefore confirmed, while the helper is now corrected for future runs. Final score calculation was always through the simulator metric, which already applies the 30-day deadline. Static potential-ask and greedy controls do not learn from these labels.

## Gemini checklist: what is right and what needs correction

| Gemini statement | Audit |
|---|---|
| 60 decision days plus 40 follow-up days; 200 members | **Correct.** No new asks or introductions during follow-up; feedback remains observable. The denominator includes members arrived by decision day 59, including those later unavailable or unserved. |
| Reciprocal hard checks | **Mostly correct.** Enforce both age ranges, explicit `who_to_meet`, relationship-structure agreement, smoking/children rules, reciprocal acceptable zones, and at least one schedule overlap. A known hard failure wins over missing data; unknown hard fields block the edge. |
| Geographic “zone adjacency” | **Wrong.** Zones are opaque fictional labels. Check whether each person's current zone appears in the other's `acceptable_zones`; there is no adjacency or distance rule. `relocate` is soft and does not override current zone constraints. |
| 12 daily clarification tokens; hard bundle 3, named soft field 1 | **Substantively correct; call them budget units.** The budget resets daily. The hard bundle is an artificial simulator abstraction. Clarification is immediate; disclosed answers are exact synthetic self-reports; declined answers remain unknown. |
| Delayed MSMI feedback / right-censoring | **Needs precision.** A qualifying first date must occur within 30 simulation days of assignment, and both people must say Yes to a second meeting within three days after that date. No response is missing, not evidence of dislike. Do not call immature recent outcomes failures. |
| One active introduction per person “per day” | **Wrong phrasing.** The rule is at most one **concurrent/outstanding** introduction per person, not one new introduction per person per day. No repeated pair within an episode; availability and the complete batch are validated. A person may be served again later if available and not paused. |
| Six variants × 20 seeds = 120 episodes per policy | **Correct for the private ranking protocol.** It is 20 private seeds per scenario family, equally weighted by family. Public variant IDs are `development`, `sparse`, `cold_start`, `delayed`, `shift`, `drift`. A small public screen is not a private score. |
| Potential asks + global bipartite matching / Hungarian | **Matching term is wrong.** There is no natural two-sided partition: this is a general undirected graph. Use a general-graph matching method (the pilot uses NetworkX `max_weight_matching`), or another optimizer that solves the same constraints. Hungarian assignment is not the direct model here. |
| Thompson + VOI | **Not what the current repo implements.** It contains a coarse-pattern Thompson matcher and a separate heuristic potential-ask policy. Potential asks are VOI-inspired, not an exact expected-value calculation; combining posterior outcome sampling with decision-relevant clarification would be new work. |
| MSMI, coverage, total introductions | **Partly right.** MSMI/100 is the primary ranking score; coverage is the first tie-break. Assignments, mutual acceptances, dates, missing feedback, clarification cost, first-introduction waits, and unserved count should also be reported. |
| Cumulative regret and required PNG performance curves | **Not required by the spec.** Regret is not defined, and unintroduced pairs have no observed outcome labels; the logging propensity is null. Do not claim oracle/counterfactual regret without a defensible reference and assumptions. A plot is optional, not a submission requirement. |

## Requirements checklist for the policy and report

### Actions and feasibility

- Read only the current observable state, ask results, visible feedback, policy-owned memory, and declared training assets. Never use hidden `truth`, private worlds, future members, or generator-seed/ID tricks.
- Run the two phases each decision day: ask, refresh observation, then match. Empty ask or match arrays are valid.
- Keep known hard constraints as gates; scores cannot override them. Distinguish observed, not-asked, and declined values; null is unknown, not zero or rejection.
- Check same pool, distinct available members, reciprocal constraints, no prior pair, no overlapping assignments in a batch, and no outstanding introduction per person. Validate the whole batch atomically.
- Daily budget: 12 units; `constraints` costs 3; one named soft field costs 1. Ask only currently available members. Preserve declined values as unknown.
- Never infer who someone wants to meet from age or gender. Geographic zones are allocation constraints, not real locations.

### Feedback, objective, and experiments

- Separate assignment, directional acceptance, mutual acceptance, first date, and each person's second-meeting intention.
- Primary outcome: date within 30 days of assignment **and** both Yes responses within three days of the date. Count one qualifying pair once.
- A no-response is missing; no date means no observed second-meeting preference; immature outcomes are right-censored. Train only on information observable at the action time.
- Primary score: per-episode `100 × MSMI / arrived_by_day_59`; average episode scores inside each scenario family, then equally average six family means. Do not pool all denominators or pick a best seed.
- Compare the three supplied baselines (greedy with clarification, no-clarification greedy, random-feasible) on identical seeds/scenarios and include a hypothesis-driven ablation. Report every scenario and multiple seeds with uncertainty/failure analysis.
- The static dataset has six training, two validation, and two development-test pools. Keep people/pairs from crossing splits; day-30 snapshots are not earlier-time observations. Propensities are null, so do not claim unbiased inverse-propensity estimates.

### Interface and final-build constraints

- One JSON request per process invocation; exactly one JSON response. Ask response keys: `asks`, `memory`; match response keys: `pairs`, `memory`. Stdout is protocol only; diagnostics go to stderr.
- Memory is explicit and carried between calls; it begins empty each independent episode. Handle an empty population/feasible graph. NaN/Infinity are invalid.
- Assessed inference: offline CPU, 2 cores, 1 GiB RAM, 64 processes, 10 seconds per call including startup; request/response/memory each ≤1 MiB; required assets ≤2 GiB. No network/GPU; Docker image and pinned dependencies/licences required for Round 2.
- All episodes must be valid. A malformed response, invalid ask/pair, timeout, or resource failure makes the assessed submission ineligible.
- Probability estimates are optional. If reported, specify directional A-accepts-B, B-accepts-A, and joint both-accept target/window, and show held-out calibration. Do not present GP-UCB scores as calibrated probabilities.

### Submission, provenance, and ownership

- Teams contain one to four participants. Round 1 is a PDF or Markdown research note; a website/dashboard is optional and does not replace the runnable policy in Round 2.
- The problem statement lists the Round 1 research note deadline as **9 October 2026, 23:59 IST** and says submission is through the Google Form; the link was still pending in the checked release. Keep the form receipt; if submitting a link, pin an unchanged version before the deadline. GitHub Issues are not the Round 1 route.
- Round 2 uses the public Final submission issue template and requires an immutable repository commit SHA or an immutable archive plus its SHA-256. Do not post personal data, passwords, or private participant data.
- All supplied people and outcomes are synthetic. Do not describe them as real users or as proof of real-world relationship prediction. External data must be lawfully available/licensed; declare external models, data, coding tools, dependencies, and licences.
- Students retain ownership of their work; participation does not itself grant a commercial licence to Vouchsafe/Romeo & Juliet.

The note should cover hypothesis, reciprocal feasibility, allocation, clarification, optional probabilities, baselines, planned experiments, and failure cases. The official release sets no 10-page minimum; Claude's ~10-page structure is a suggestion, not a submission rule. With the deadline tonight, prioritize completeness and accuracy over length. Docker packaging and the full final technical report belong to the later Round 2 build.

## Recommendation for the research note

1. Keep the central hypothesis narrow: **with hard feasibility enforced, targeting clarification at members whose missing constraints block promising potential edges may improve MSMI by unlocking useful options; global general-graph matching may reduce greedy allocation collisions.**
2. Use the ten-seed factorial as the strongest current public evidence: the ask main effect was +0.117 MSMI/100 (95% CI [+0.025, +0.208], unadjusted sign-flip *p* = 0.045), while the matcher effect was uncertain. State that the result is exploratory, public-only, and reverses in cold start. The complete report is `SCALED_FACTORIAL_RESULTS.md`.
3. Keep phase hybrids separate: the four-phase mixture led by only one event in the earlier three-seed pilot and has not been retested at ten seeds; do not present it as a winner.
4. Report the soft-question experiment as a secondary exploratory result: the 3-seed pilot showed a +3-event difference for hard-plus-soft max-weight, but the seven-seed public holdout estimated only +0.024 MSMI/100 (95% CI [−0.071, +0.131], sign-flip *p* = 0.844). This does not establish an average benefit. Soft-only asks used zero units because hard feasibility was still blocked; hard-plus-soft spent about 83 extra soft-question units/episode. Note the scenario heterogeneity (shift positive, cold-start negative), and don't elevate it above the ten-seed factorial.
5. Use the three official baselines and clean ask-only/matcher-only ablations. Do not promise calibrated probabilities or regret unless you define and validate them. Synthetic success is not evidence about real relationships.
6. Record the label-cutoff correction in the methods. The corrected three-seed rerun was identical to the stored learned-policy rows; keep the patched helper for future learning-policy work.

## Reproducibility files

- `SCALED_FACTORIAL_RESULTS.md` — report of the scaled ten-seed factorial and caveats.
- `scaled_factorial.py` — runner for seven additional seeds across six methods and six public variants.
- `soft_ask_screen.py` — resumable 3-seed, process-parallel screen for soft-field asks; user's 72 episodes completed valid, summary now available.
- `soft_ask_validation_7seeds.py` — held-out validation runner for hard-plus-soft max-weight; its 42 public-seed episodes completed on the user's VM.
- `make_scaled_factorial_heatmap.py` — regenerates the scaled scenario/primary-score figure from the combined JSON.
- `results/scaled_factorial_extra_7seeds.json` — 252 new rollouts.
- `results/scaled_factorial_10seeds.json` — combined 360 rows, summaries, paired contrasts, factorial effects, CIs, and tests.
- `results/scaled_factorial_summary.csv` and `results/scaled_factorial_contrasts.csv` — readable tables.
- `results/scaled_factorial_heatmap.png` — scaled scenario heatmap and primary-score intervals.
- `phase_screen.py` — new in-process screen; `python phase_screen.py` reproduces the 90 exploratory episodes.
- `phase_hybrid_policy.py` — four-phase version using the official JSON protocol; locally smoke-tested through `evaluate.py` for all six variants at seed 101.
- `checkpoint_diagnostics.py` — follow-up for mature label counts, adaptive switch timing, and daily ask-budget use.
- `corrected_learning_rerun.py` — reruns Thompson, GP-mean, and GP-UCB with the official label cutoff.
- `results/phase_screen_3seeds.json` — all 90 new episode rows and summary.
- `results/checkpoint_diagnostics.json` — 36 checkpoint/ask-budget diagnostic rows.
- `results/corrected_learning_rerun_3seeds.json` — 54 corrected-label learned-policy episodes and paired comparison.
- `results/phase_screen_summary.csv` — policy and scenario summary.
- `results/phase_screen_heatmap.png` — visual overview.
- `results/public_pilot_results.json` and `experiment_log.md` — prior pilot artifacts; learned-policy results need the date-cutoff audit above.

The in-process runtime column is not official per-invocation timing. The four-phase subprocess run passed the local evaluator's protocol and time checks, but Docker validation has not yet been done.
