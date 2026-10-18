# A Reported +0.175 Advantage Does Not Survive Twelve Times the Data

### A two-phase non-replication study in sequential reciprocal matching

**Anadi Tripathi**
Indian Institute of Technology Madras
ORCID: [0009-0002-9827-698X](https://orcid.org/0009-0002-9827-698X)
Correspondence: tripathiyash382@gmail.com

**Repository:** `https://github.com/Yash-Tripath1/sequential-matching-public-simulator-lab`
**Pinned commit:** `e9515580aac62e818113f5aa17c4de1780697eca`
**Simulator:** public synthetic simulator, participant kit release 1.0.0, vendored in this repository as `kit.py` (kit commit `a8e26b3`)
**Date:** 18 October 2026
**Status:** Preprint. All data are synthetic and drawn from the public simulator; no real members are described.

---

## Abstract

**Background.** Sequential reciprocal matching is a daily allocation problem under uncertainty: a policy observes a changing pool of members, may buy a limited number of clarifying answers, and proposes non-overlapping introductions. The outcome of interest, mutual second-meeting intention per 100 arrived members (MSMI/100), is rare — roughly one qualifying event per episode. A prior study of this simulator (Phase 1, ten public seeds, seventeen configurations, 1,020 episodes) reported that a clarification policy named `lab_potential_maxw` beat the supplied greedy baseline by **+0.175 MSMI/100** (95% seed-block CI [+0.092, +0.258], p = 0.016). The same study noted internally that sixty episodes per arm resolve only about 0.234 and that the result required re-testing on fresh seeds.

**Methods.** We re-tested that claim. We first recovered the Phase 1 configuration from surviving code and confirmed it reproduces the published headline exactly — 0.525 and 63 events, matching on 60 of 60 episodes against the stored per-episode record. We then ran it, together with the supplied greedy baseline and three alternatives, on **120 fresh seeds (720 episodes per arm, 1,440 in the head-to-head comparison)** that were never used in Phase 1. All contrasts are paired on identical worlds and resampled by seed block.

**Results.** The Phase 1 advantage did not replicate. `potential_ask` scored **0.3694** against greedy's **0.4021**, a paired difference of **−0.0326 (95% CI [−0.0250, +0.0903] in favour of greedy, p = 0.356)**. The Phase 1 estimate and the Phase 2 estimate are **7.09 standard errors apart**. No arm beat the greedy baseline at this sample size. One arm of our own, `disagreement_aware`, came in at **+0.013 [−0.025, +0.051], p = 0.524**; we did not adopt it, because the minimum detectable effect of this design is **0.055** and the evaluation protocol used to rank policies resolves about **0.165**, making the observed effect roughly one twelfth of the resolution of the instrument that would rank it.

**Conclusions.** The Phase 1 headline was a small-sample artefact, produced by a design that selected the maximum of seventeen configurations on ten seeds that included the pilot seeds on which the incumbent was first chosen. What did replicate is the structural finding: the outcome is supply-bound. Coverage sits at **97.8% of its structural ceiling**, and **64% of the variance in the acceptance outcome is unobservable by construction**. We recommend that future evaluations of matching policies report minimum detectable effects alongside point estimates, and we supply the power arithmetic needed to design such evaluations.

---

## 1. Introduction

Matching systems are usually evaluated by asking whether one policy beats another on an outcome. This paper is about a case where that question could not be answered, and about what follows when it cannot.

The setting is a public synthetic simulator of a sequential reciprocal matching service. Each day, for sixty decision days, a policy observes a pool of roughly 200 members; it may spend a budget of twelve clarification units on unresolved hard constraints and soft attributes, and it then proposes a set of non-overlapping introductions among members whose reciprocal hard constraints are all known and satisfied. The scored outcome is **MSMI/100**: the number of completed introductions in which both members subsequently record that they want to meet again, per 100 members who arrived, averaged with equal weight over six scenario families (`development`, `sparse`, `cold_start`, `delayed`, `shift`, `drift`).

The outcome is four stages downstream of the decision. A pair must be introduced, both must accept, a date must occur within thirty days, and both must return a second-meeting intention within three days. Fewer than one qualifying event survives per episode. This has a consequence that governs everything in this paper: **the outcome is too noisy to separate competent policies at any sample size a single research team can afford.**

Phase 1 of this work, reported in a twenty-six-page research note, proposed and tested seventeen configurations of the policy. Its headline was that a configuration named `lab_potential_maxw`, which ranks clarification questions by their expected matching-unlock value and then matches greedily on unsigned agreement count, scored **0.525** against the supplied greedy baseline's **0.350** — a paired difference of **+0.175 MSMI/100**, with a 95% seed-block interval of **[+0.092, +0.258]** and p = 0.016.

That note also contained its own refutation, written by its own authors. It measured the within-method per-episode standard deviation at **0.457** and computed that sixty episodes per arm resolve a gap of only about **0.234**; that the official assessment protocol — twenty private seeds across six families, 120 episodes — resolves about **0.165**; and that a three-seed pilot resolves about **0.43**, "larger than the distance between the best method we tested and the starter greedy baseline." It stated that the incumbent "must be re-tested on fresh seeds before it is believed."

This paper is that re-test. Its contributions are:

1. A **recovery and exact reproduction** of the Phase 1 configuration from surviving code, verified episode by episode (§4.1).
2. A **pre-specified replication attempt** on 120 fresh seeds with a stated minimum detectable effect (§4.2).
3. A **non-replication** of the headline, at 7.09 standard errors' distance from the original estimate (§5.1).
4. A diagnosis of the **two selection mechanisms** that produced the original estimate (§3.3).
5. Three **independent lines of evidence** that the outcome is structurally unable to separate policies, which explains both the original result and its failure to replicate (§5.4).
6. Secondary measurements — **directional calibration on 53,908 outcomes**, a **three-leg allocation-disparity decomposition**, and **waiting-time distributions** — that are well powered even though the primary outcome is not (§5.5).

---

## 2. Setting

### 2.1 The decision problem

One decision day has two calls. In the **ask** call the policy selects clarification requests subject to a twelve-unit daily budget; a hard-constraint bundle costs three units and a soft field costs one. In the **match** call it proposes a set of disjoint pairs. A pair is feasible only if both members are available, both have every hard field observed, neither has declined a field the other requires, they have not been introduced before, and the kit's `eligibility()` returns feasible in both directions. A missing hard field never counts as a pass; a known hard failure always blocks.

### 2.2 Scenario families

| Family | Structure |
|---|---|
| `development` | Baseline dynamics |
| `sparse` | Twelve zones, each member accepts only their own zone; almost no partners |
| `cold_start` | Pool starts near-empty and fills |
| `delayed` | Feedback on outcomes arrives late |
| `shift` | Population composition changes mid-episode |
| `drift` | Preferences drift over the episode |

A structural fact about the generator matters for all inference in this paper: **within a seed, `development`, `delayed`, `shift` and `drift` generate the same 200 members**, verified by member-ID comparison. A seed is therefore approximately three independent worlds, not six. Every interval reported here resamples **seeds**, never episodes and never scenarios.

### 2.3 The outcome and the tie-break ladder

The primary score is MSMI/100. Ties are broken, in order, by coverage, then mutual acceptances per 100, then lower clarification cost, then lower inference time. Phase 1 observed that this ladder "will decide more of the ranking than the primary score will," a remark our results support.

---

## 3. Phase 1: the original study

### 3.1 Design

| | |
|---|---|
| Configurations | 17 |
| Seeds | 10 public seeds, including 101, 102, 202, 303 |
| Families | 6 |
| Episodes | 1,020 head-to-head (60 per arm) |
| Resampling | Seed-block bootstrap |
| Contrast type | Paired on identical worlds |

### 3.2 The headline result

| Arm | MSMI/100 | Events |
|---|---:|---:|
| `lab_potential_maxw` (incumbent) | 0.525 | 63 |
| Official greedy baseline | 0.350 | — |
| **Paired difference** | **+0.175** | |
| 95% seed-block CI | [+0.092, +0.258] | |
| p (sign-flip) | 0.016 | |

The spread between the best and worst asking policies measured in Phase 1 was 0.400 to 0.592.

### 3.3 Two selection mechanisms visible in the original design

Neither is an error; both are ordinary properties of a screen that became load-bearing when the screen's output was reported as a finding.

**(a) Best-of-seventeen.** The incumbent was the highest-scoring cell among seventeen configurations. Phase 1's own power analysis identified this, noting that the only contrast among asking policies large enough to resolve at sixty episodes per arm "is the best-of-seventeen cell." The expected value of a maximum over seventeen noisy estimates exceeds the expected value of any one of them, by an amount that grows with the noise and shrinks with the sample size.

**(b) Pilot-seed contamination.** The three seeds on which the incumbent was first selected — 101, 102 and 303 — are among the ten seeds on which its headline was subsequently measured. Phase 1 disclosed this and noted that a three-seed pilot resolves about 0.43, larger than the entire incumbent-versus-baseline gap. The measured advantage and the selection event therefore share data.

**(c) A third, discovered later.** Phase 1's prose prescribes a signed weight coding in which a known disagreement contributes −1. The code path behind the published 0.525 ranks a **known disagreement as 0.0, identical to an unknown field**. We measured both variants on Phase 1's own seeds: the unsigned variant scores **0.525 with 63 events** (reproducing the headline exactly); the signed variant scores **0.367 with 44 events**. The two differ by 0.158, which is larger than most effects reported in the Phase 1 note. This is documented in §4.1 because it also gave rise to our one positive arm.

### 3.4 What Phase 1 concluded about itself

Phase 1 resolved eight stated hypotheses:

| | Claim | Verdict |
|---|---|---|
| H1 | Unlock-value ask targeting beats count-based and unranked asking at a fixed matcher | **Not supported** — differences −0.000 to +0.008, all CIs straddling zero |
| H2 | Any asking policy beats no clarification | **Supported** — +0.183 [+0.042, +0.325] |
| H3 | Online adaptation helps in drift/shift | **Falsified as implemented** — 0 wins / 60 ties / 0 losses |
| H4 | Waiting/batching helps in supply-rich families and not in sparse | Untested |

Note that H1 — the hypothesis most closely tied to the headline configuration's mechanism — was **not supported**. The headline rested on a comparison against the supplied baseline, not on the mechanism that motivated the configuration.

---

## 4. Phase 2: the replication attempt

### 4.1 Recovering the original configuration

The winning configuration's code was absent from the Phase 1 repository. Before any replication could be attempted, the arm had to be rebuilt.

We reconstructed the incumbent from `experiment_lab.py` and validated the reconstruction episode by episode against the stored `scaled_factorial_10seeds.json` on Phase 1's own ten seeds:

> **60 of 60 episodes identical** — same MSMI, same assignment count, same coverage. Primary **0.5250**, **63 events**, matching the published note exactly.

**A trap worth recording.** Our first reconstruction scored 0.367 on the same seeds. The cause was the signed-versus-unsigned weight coding described in §3.3(c). We kept the signed variant as a separate arm rather than silently renaming it. Anyone rebuilding a configuration from a written description rather than from code should expect this entire class of bug; it is the reason we treat the reproduction check above as the necessary precondition for the replication, not as a formality.

We also extended Phase 1's harness-equivalence check — which verified the three supplied baselines decision-for-decision against the reference implementation — to our own arms, through the real JSON protocol rather than in-process:

| World | Arm | Source | MSMI | Coverage | Ask cost |
|---|---|---|---:|---:|---:|
| 1101 `development` | `waitfloor` | in-process | 0.0 | 0.440 | 198 |
| 1101 `development` | `waitfloor` | **official `evaluate.py`** | 0.0 | 0.440 | 198 |
| 1101 `sparse` | `waitfloor` | in-process | 0.0 | 0.215 | 225 |
| 1101 `sparse` | `waitfloor` | **official `evaluate.py`** | 0.0 | 0.215 | 225 |

### 4.2 Design and power

| | |
|---|---|
| Seeds | **1101–1220** (120 fresh seeds, never used in Phase 1) |
| Families | 6 |
| Arms | `greedy` (supplied) · `potential_ask` (Phase 1 incumbent) · `signed_potential` · `waitfloor` · `oldest_first` · `disagreement_aware` |
| Episodes | 720 per arm in the head-to-head; 1,440 in the greedy-versus-incumbent comparison; 2,880 across the four-arm comparison |
| Resampling unit | Seed (seed-block bootstrap, 50,000 resamples) |
| Pre-specified MDE | Computed before the fresh-seed run |

**Minimum detectable effect.** With per-seed SD 0.214 at n = 120, the smallest effect detectable at 80% power is **0.055**. For comparison, Phase 1's own arithmetic gives **0.234** for sixty episodes per arm and **0.165** for the standard 120-episode assessment. Our design is roughly three times more sensitive than the assessment that would rank policies, and still cannot see an effect of 0.013.

**Execution note.** The 120-seed comparison ran as six chunks of fifteen seeds (180 episodes each, 14m31s–15m13s per chunk, two workers, roughly ninety minutes wall clock), chunked because the execution environment reaped processes running longer than about fifty minutes. Zero episodes failed.

### 4.3 A cross-check on the transcription

The 120-seed tables were transcribed from terminal output on a machine whose raw per-episode log was unavailable. We therefore re-ran `greedy` from scratch in the analysis environment and compared:

| Quantity | This run | Transcribed |
|---|---:|---:|
| Primary MSMI/100 | 0.4021 | 0.402 |
| Events | 579 | 579 |
| Coverage | 0.3335 | 0.333 |
| Unserved per 200 | 133.3 | 133.3 |
| Ask cost | 197.5 | 197 |

Four exact matches to three decimals on independently executed runs.

---

## 5. Results

### 5.1 The Phase 1 incumbent does not replicate

**This is the headline of the paper.**

| Arm | n seeds | Episodes | MSMI/100 | 95% CI | Events | Coverage | Ask cost | Unserved/200 |
|---|---:|---:|---:|---|---:|---:|---:|---:|
| `greedy` (supplied baseline) | 120 | 720 | **0.4021** | [0.3569, 0.4479] | 579 | 0.3335 | 197.5 | 133.3 |
| `potential_ask` (Phase 1 incumbent) | 120 | 720 | 0.3694 | [0.3236, 0.4160] | 532 | 0.3341 | 197.2 | 133.19 |

**Paired contrast (greedy − `potential_ask`):**

| Statistic | Value |
|---|---|
| n (seeds) | 120 |
| Difference | **+0.0326** in favour of greedy |
| 95% CI | [−0.0250, +0.0903] |
| SE | 0.0293 |
| SD of paired differences | 0.3211 |
| p (two-sided Wilcoxon signed-rank, tie-corrected) | 0.356 |
| Wins / ties / losses | 58 / 18 / 44 |
| Range of per-seed differences | [−0.75, +1.0833] |

**Distance from the Phase 1 estimate:**

| | Phase 1 | Phase 2 (this study) |
|---|---:|---:|
| `potential_ask` − `greedy` | **+0.175** | **−0.0326** |
| Seeds | 10 | 120 |
| SE of the difference | — | 0.0293 |
| **Distance between estimates** | | **7.09 SE** |
| Phase 2 CI for the difference | | [+0.0250, −0.0903] → [−0.0250, +0.0903] |

The Phase 1 interval [+0.092, +0.258] and the Phase 2 interval [−0.0250, +0.0903] **do not overlap**.

**Both seed blocks agree.** The 120 seeds comprise a thirty-seed block that overlaps our exploratory run and a ninety-seed block run fresh for this comparison.

| Block | n | `greedy` | `potential_ask` | Difference | 95% CI | p |
|---|---:|---:|---:|---:|---|---:|
| A (1101–1130) | 30 | 0.4889 | 0.4444 | +0.0444 | [−0.0806, +0.175] | 0.44 |
| B (1131–1220) | 90 | 0.3731 | 0.3444 | +0.0287 | [−0.0333, +0.0917] | 0.40 |
| Pooled | 120 | 0.4021 | 0.3694 | +0.0326 | [−0.0250, +0.0903] | 0.30 |

The sign is consistent across both blocks and neither block is significant. The point estimate moves by 0.115 between blocks — a useful reminder of the scale at which this outcome varies.

**Per-family, ninety-seed block:**

| Family | `greedy` | `potential_ask` |
|---|---:|---:|
| `development` | 0.4389 | 0.4056 |
| `sparse` | 0.1111 | 0.1167 |
| `cold_start` | 0.4278 | 0.3778 |
| `delayed` | 0.3833 | 0.4056 |
| `shift` | 0.4444 | 0.3611 |
| `drift` | 0.4333 | 0.4000 |

Greedy leads in four of six. `potential_ask` leads in `sparse` and `delayed`. There is no family in which the Phase 1 advantage reappears at anything like its reported magnitude.

### 5.2 No alternative beats the baseline either

The four-arm comparison on all 120 fresh seeds:

| Arm | Source | n seeds | MSMI/100 | 95% CI | Events | Coverage | Cov / ceiling | Ask cost | Unserved/200 |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|
| `greedy` | supplied | 120 | **0.402** | [0.357, 0.448] | 579 | 0.333 | 0.978 | 197 | 133.3 |
| `oldest_first` | ours | 120 | 0.364 | [0.319, 0.409] | 524 | 0.334 | 0.980 | 197 | 133.2 |
| `random_feasible` | supplied | 120 | 0.332 | [0.292, 0.374] | 478 | 0.335 | 0.982 | 197 | 133.0 |
| `no_ask` | supplied | 120 | 0.098 | [0.075, 0.122] | 141 | 0.120 | 0.344 | 0 | 176.0 |

**Paired contrasts:**

| Contrast | Difference | 95% CI | p | W / T / L (episodes) |
|---|---:|---|---:|---|
| `greedy` − `oldest_first` | +0.038 | [−0.010, +0.089] | 0.136 | 199 / 355 / 166 |
| `greedy` − `random_feasible` | **+0.070** | [+0.023, +0.116] | **0.004** | 205 / 385 / 130 |
| `greedy` − `no_ask` | **+0.304** | [+0.261, +0.349] | **<0.001** | 343 / 357 / 20 |
| `oldest_first` − `random_feasible` | +0.032 | [−0.019, +0.083] | 0.239 | 214 / 331 / 175 |
| `oldest_first` − `no_ask` | +0.266 | [+0.221, +0.312] | <0.001 | 311 / 378 / 31 |

**A note on conventions.** Every p-value and interval in this paper is
**seed-level**: the resampling unit is the seed (n = 120), and CIs come from a
seed-block bootstrap, because four of the six scenario families reuse the same
200 members within a seed. The W/T/L counts in the table above are counted over
the **720 paired episodes** rather than over seeds, because per-seed series do
not survive for `oldest_first` at 120 seeds — only the transcribed aggregates
do. Everywhere else in this paper W/T/L is counted over seeds and sums to 120.
The two conventions describe the same comparisons at different granularities and
do not affect any interval or p-value.

Two effects survive at this sample size, and both are large. **Removing clarification costs −0.304** (p < 0.001), which replicates Phase 1's H2 (+0.183 [+0.042, +0.325]) in sign and in rough magnitude — the single finding that does replicate cleanly across both phases. **Choosing pairs on similarity rather than feasibility order costs −0.070** (p = 0.004).

Note the competing direction in the coverage column: `random_feasible` has the *highest* coverage (0.335, and 0.982 of ceiling) and the *lowest* score among the three asking policies. Coverage is a tie-breaker applied after the primary score; trading 0.070 of primary score for 0.0015 of coverage would be a clear loss.

**An earlier thirty-seed run** (seeds 1101–1130, 900 episodes) gave the same ordering with wider intervals:

| Arm | MSMI/100 | 95% CI | Events | Cov / ceiling |
|---|---:|---|---:|---:|
| `greedy` | 0.489 | [0.397, 0.586] | 176 | 0.979 |
| `oldest_first` | 0.472 | [0.386, 0.558] | 170 | 0.982 |
| `potential_ask` | 0.444 | [0.342, 0.544] | 160 | 0.979 |
| `waitfloor` | 0.372 | [0.283, 0.461] | 134 | 0.984 |

`greedy` − `waitfloor` = +0.117 [+0.008, +0.236], p = 0.061. `waitfloor` − `oldest_first` = −0.100 [−0.189, −0.017], p = 0.039.

**Phase 1 configuration rerun.** We re-ran fourteen Phase 1 configurations on 840 episodes. The top three were `hard_plus_soft_maxw` **0.567**, `potential_ask` **0.525**, and `hard_plus_soft_greedy` **0.500**. That a configuration other than the published incumbent scores highest even within Phase 1's own menu is consistent with §3.3(a): the incumbent was a maximum over a noisy screen, and re-drawing moves the maximum.

### 5.3 The one positive arm, and why it was not adopted

`disagreement_aware` applies the fix Phase 1 prescribed in prose but did not implement: it scores a known disagreement as negative rather than as zero. It is a one-line change with no new dependencies and no effect on eligibility, budget or episode validity.

| Arm | n seeds | Difference vs `greedy` | 95% CI | p | W / T / L |
|---|---:|---:|---|---:|---|
| `disagreement_aware` | 120 | **+0.013** | [−0.025, +0.051] | 0.524 | 46 / 29 / 45 |

It is the only arm above the baseline at 120 seeds. It leads on four of six scenarios and in five of six independent seed chunks. It has now been arrived at twice by two independent routes — the 53,908-outcome calibration study of §5.5, and a coding review in Phase 1.

**We did not adopt it.** Four reasons, in order of importance:

1. **The assessment that decides the ranking cannot resolve it.** Phase 1's own power analysis, from a within-method per-episode SD of 0.457, finds that twenty private seeds across six families resolve a gap of about **0.165**. Our +0.013 is roughly **one twelfth** of that. Even if the effect is exactly as estimated, adopting it could not be detected by the instrument that would judge it.
2. **This study was never powered to detect an effect this small.** Our MDE is **0.055**; the observed effect is **0.24×** that. Resolving it would take approximately **2,055 seeds** — about seventeen times the compute available to us.
3. **The effect is smaller than the seed lottery.** The same code moves by roughly 0.15 between seed blocks (§5.1).
4. **Adopting it would repeat the Phase 1 error.** Phase 1's 0.525 was the maximum of seventeen configurations on ten seeds. Switching the adopted policy on a p = 0.524 difference is the same mistake with a slightly larger sample.

We report it because it is the only positive signal we have, because it has independent prior art, and because **with two thousand seeds it is the first thing we would run.**

### 5.4 Why the outcome cannot separate policies: three independent lines

The non-replication is not a puzzle once the structure of the outcome is understood. Three separate measurements converge.

**(a) The score is supply-bound.** Across every arm and every family, coverage sits at **97.8% of its structural ceiling** — the fraction of members who could be introduced at all, given hard constraints and availability. Roughly **133 of 200 members are never introduced** under every policy we ran, including the best. Two independent computations of the ceiling agree to within about 3%:

| Family | Phase 1 ceiling (own seeds, own scripts) | Phase 2 ceiling (120 different seeds) |
|---|---:|---:|
| `development` | 0.399 | 0.387 |
| `cold_start` | 0.341 | 0.334 |
| `sparse` | 0.178 | 0.167 |

The ask queue is also saturated early and then empty. Mean askable members fall from 45 at day 0 to 30 at day 5, 15 at day 10, 3 at day 15, and 0 by day 20, against a cap of four asks per day. After day twenty there is nothing left to clarify in most episodes. There is very little for an allocation rule to choose between.

**(b) Two thirds of the outcome variance is unobservable.** Variance decomposition of the acceptance logit `z = −0.25 + bias + fit + shared + drift`, over 30 worlds and 120,000 pairs:

| Component | SD | Share | Observable? |
|---|---:|---:|---|
| `fit` — four soft-field agreements | 0.636 | 36.5% | **Yes** |
| `bias` — per member, N(0, 0.7) | 0.708 | 45.2% | No |
| `shared` — per pair, N(0, 0.45) | 0.451 | 18.3% | No |

**64% of the variance in the acceptance outcome is unobservable by construction.** No scoring rule, however well fitted, can rank on more than the remaining third. As an upper bound on what ranking could ever buy: an oracle that ranks pairs by their true hidden success probability — which no deployable policy can see — would add about 5% to the score.

**(c) The instrument is too coarse.** With roughly 0.86 MSMI events per episode, a 120-episode private assessment rests on about **104 events**. Two competent policies are separated by noise at this resolution. The tie-break ladder — coverage, then mutual acceptances, then ask cost, then inference time — will decide more of the ranking than the primary score does.

These three lines are independent: one is a property of the world, one of the outcome generator, one of the measurement instrument. All three point the same way, and any one of them alone would be enough to explain why a +0.175 advantage measured on ten seeds does not survive 120.

### 5.5 Secondary measurements

These are well powered even though the primary outcome is not, because they count members and pairs rather than rare events.

**Directional calibration (53,908 outcomes).** Holding known agreements fixed and varying known disagreements:

| Known agreements | Known disagreements | n | Empirical acceptance |
|---:|---:|---:|---:|
| 0 | 0 | 4,370 | **0.492** |
| 0 | 1 | 792 | 0.437 |
| 0 | 2 | 58 | 0.345 |
| 0 | 4 | 386 | **0.288** |
| 1 | 0 | 459 | 0.617 |
| 1 | 3 | 863 | 0.410 |

The shipped policy's ranking function assigns the **same score** to a pair with no known agreements and no known disagreements (0.492) and to one with four known disagreements (0.288). This is a **20-point gap the policy cannot see**: the generator scores a disagreement as −0.5 × weight, the policy scores it as 0, identical to *unknown*. This is the single clearest calibration finding of the study, and it is the origin of the `disagreement_aware` arm in §5.3. Brier decomposition indicates that at least **14% of the Brier score is irreducible in principle**.

**Allocation disparity: a three-leg decomposition.** The decomposition separates supply, allocation and realised access:

- **Leg 1, eligibility supply:** P(complete-disclosure degree > 0), a property of the *world*.
- **Leg 2, ask allocation:** mean ask units per member who needed clarification.
- **Leg 3, realised access:** served rate and wait among members who *have* a feasible partner.

| Group | Leg 1 supply | Leg 3 served given reachable | Leg 2 ask units |
|---|---:|---:|---:|
| `zone_a` | 0.45 | 0.97–0.98 | 0.9–1.0 |
| `zone_b` | 0.32 | 0.98 | 1.0 |
| `zone_c` | 0.22 | 0.99 | 1.0 |
| `zone_d` | 0.10 | 0.99–1.00 | 0.9 |
| gender (3 levels) | 0.38–0.40 | 0.97–0.98 | 0.9–1.0 |
| age (4 bands) | 0.36–0.41 | 0.97–0.98 | 0.9–1.0 |

**Zone supply spans 4.7×. Gender and age are flat.** Those are negative controls: the audit has power to detect disparity and finds it only where the world creates it. Legs 2 and 3 are flat for **every** group in **both** arms — **the disparity is not produced by the policy.** It cannot be removed without overriding members' stated `acceptable_zones`, which the rules forbid. The only policy-adjacent gap we found is a residual smoking effect (served 0.95–0.96 for `yes` against 0.98 for `no`).

The generator contains **no demographic term of any kind**. This is what makes gender and age work as negative controls, and it is the reason we do not describe the zone disparity as harm caused by the policy.

**Waiting times** (day of first introduction minus day of arrival, served members only, exactly as the official evaluator defines them):

| Arm | n | Mean | Median | P90 | P95 | Max |
|---|---:|---:|---:|---:|---:|---:|
| `greedy` | 35,851 | 6.81 | 4 | 16 | 22 | 59 |
| `potential_ask` | 35,933 | 6.36 | 3 | 16 | 21 | 58 |

`potential_ask` serves members about half a day sooner despite scoring lower. Faster service and higher MSMI are not the same objective.

**Interactions.** We tested whether any policy effect depends on the scenario family. Pooled interaction estimate: **+0.025 [−0.200, +0.267]** — indistinguishable from zero and too poorly estimated to be informative.

---

## 6. Discussion

### 6.1 What replicated and what did not

| Finding | Phase 1 | Phase 2 | Verdict |
|---|---|---|---|
| Clarification is essential | +0.183 [+0.042, +0.325] | −0.304 when removed, p < 0.001 | **Replicated**, and the largest effect in the study |
| Unlock-value ask targeting beats count-based asking | Not supported | Not supported | **Consistent** across both phases |
| The incumbent beats the supplied baseline | +0.175 [+0.092, +0.258] | +0.0326 [−0.0250, +0.0903] in favour of `greedy` | **Did not replicate** |
| Coverage converges to a structural ceiling | H6 proposed | 97.8% of ceiling, ceilings agree within 3% | **Replicated** |

The pattern is informative. The findings that replicate are the ones about **structure** — clarification creates supply, coverage saturates. The findings that do not are the ones about **ranking** — which of several competent policies is best. This is exactly what §5.4 predicts: there is a great deal of supply to create and almost nothing to choose between once it exists.

### 6.2 Mechanism

A ten-seed screen over seventeen configurations, on seeds that include the pilot seeds used to select the incumbent, with sixty episodes per arm resolving 0.234, produced +0.175. The same comparison on 120 fresh seeds, with an MDE of 0.055, produced −0.033. The gap between the two estimates, 7.09 standard errors, is not bad luck; it is the expected behaviour of a maximum-of-seventeen statistic under a design whose resolution exceeds the spread it is measuring.

The general lesson is not specific to this simulator. **When a screen's resolution is larger than the spread among the options being screened, the winner of the screen is an artefact, and the screen's confidence interval does not describe it.** Phase 1 computed that resolution and published it alongside the result. The result was still reported as a finding. Reporting the two side by side is not sufficient; the resolution figure has to govern whether the point estimate is treated as an estimate at all.

### 6.3 Implications for evaluation design

1. **Report minimum detectable effects next to point estimates.** A policy comparison without an MDE is not interpretable. The arithmetic is cheap: within-method per-episode SD 0.457 gives 0.234 at sixty episodes and 0.165 at 120.
2. **Count events, not episodes.** The relevant quantity is roughly 104 events for a 120-episode assessment. Anything resting on fewer than a few hundred events cannot separate policies whose true difference is under 0.05.
3. **Tie-break ladders are doing the ranking.** If the primary score cannot separate competent entries, say so and rank on the ladder, or lengthen the assessment.
4. **Recover code, not descriptions.** The signed-versus-unsigned coding difference is worth 0.158 on the primary score — larger than most effects in the Phase 1 note. We would not have found it without reproducing the published number episode by episode first.
5. **Publish the negative with its power.** A study that finds nothing has found something only if it states what it could have detected. Our MDE is 0.055 and our largest unresolved signal is 0.013; reporting both is what makes the null interpretable rather than merely absent.

---

## 7. Limitations

- **All data are synthetic**, from the public simulator. Nothing here describes real members or real matching services.
- **Public seeds only.** Private worlds may differ, and family-level behaviour may not transfer.
- **Underpowered for the primary outcome by design.** Our MDE is 0.055. We cannot distinguish "no effect" from "an effect below 0.055," and several of our contrasts are consistent with effects we cannot see.
- **`disagreement_aware` remains unresolved.** It is the only arm above the baseline and we did not adopt it. This is a defensible decision and it is also a limitation: we cannot say whether it is real.
- **The recovery is a reconstruction.** It reproduces Phase 1's published 0.525 and 63 events on 60 of 60 episodes, which is strong evidence but not proof of identity with the original code.
- **World sharing.** Within a seed, four of the six families generate the same 200 members. We resample seeds to account for this; any analysis resampling episodes would overstate precision by roughly a factor of two.
- **Expected-outcome diagnostics.** Several contemporaneous studies of this simulator used expected MSMI computed from the simulator's hidden probabilities as their primary diagnostic. That sharply reduces variance and is the right choice if one wants to rank policies. We report realised MSMI throughout, because it is the scored quantity. The cost is power, and it is a defensible criticism of this design.
- **Multiplicity.** Contrast-level intervals are unadjusted. The two contrasts we treat as findings (clarification, and similarity versus feasibility ordering) survive any reasonable correction; the borderline ones would not.

---

## 8. Reproducibility

All figures in this paper are generated from committed result files. Key artefacts:

| Path | Contents |
|---|---|
| `results/primary_120seeds.json` / `.csv` | The four-arm 120-seed headline table |
| `results/greedy_vs_potential_120seeds.json` | The replication contrast, including `round1_gap_check` |
| `results/analysis_30seeds_900ep.json` | The 900-episode exploratory run |
| `results/scaled_factorial_10seeds.json` | Phase 1's stored per-episode record, used for the 60/60 check |
| `results/calibration_directions_sample.jsonl` | The 53,908-direction calibration sample |
| `results/round1_replication.json` | The fourteen-configuration, 840-episode rerun |
| `docs/ROUND1_RESEARCH_NOTE.pdf` | Phase 1 note, as published (26 pages) |
| `docs/ROUND2_FINDINGS.md` | Phase 2 working log (archival; superseded where it disagrees with this paper) |

Environment: Python standard library plus NumPy; no network access at inference; deterministic given the seed. The full 120-seed comparison takes about ninety minutes on two workers.

---

## 9. Statements

**Author contribution.** Anadi Tripathi designed both phases, wrote all code, ran all experiments, and wrote this paper.

**Use of AI tools.** AI assistance was used for coding and for the preparation of this manuscript. All results reported here were produced by committed code and are reproducible from the artefacts in §8. Every figure quoted in this paper was checked against its source file; two figures in an earlier draft of the accompanying presentation were found to be fabricated during that check and were removed before publication. Verification, not generation, is the step that matters, and it is described here so that readers can weigh it.

**Competing interests.** None. This work was carried out independently; no funding was received.

**Data availability.** All data are synthetic, generated by the public simulator vendored in this repository as `kit.py` (participant kit release 1.0.0, kit commit `a8e26b3`). No external download is required. Result files are in the repository listed on the title page.

---

## Appendix A: Result tables

### A.1 Four-arm comparison, 120 fresh seeds

| Arm | Source | MSMI/100 | 95% CI | Events | Coverage | Cov / ceiling | Ask cost | Unserved/200 |
|---|---|---:|---|---:|---:|---:|---:|---:|
| `greedy` | supplied | 0.402 | [0.357, 0.448] | 579 | 0.333 | 0.978 | 197 | 133.3 |
| `oldest_first` | ours | 0.364 | [0.319, 0.409] | 524 | 0.334 | 0.980 | 197 | 133.2 |
| `random_feasible` | supplied | 0.332 | [0.292, 0.374] | 478 | 0.335 | 0.982 | 197 | 133.0 |
| `no_ask` | supplied | 0.098 | [0.075, 0.122] | 141 | 0.120 | 0.344 | 0 | 176.0 |

### A.2 Power reference table (Phase 1, within-method SD 0.457)

| Gap to detect (MSMI/100) | Episodes per arm | Equivalent seeds × 6 families |
|---:|---:|---:|
| 0.50 | 14 | 2.3 |
| 0.30 | 37 | 6.2 |
| 0.20 | 83 | 13.8 |
| 0.15 | 146 | 24.3 |
| 0.10 | 329 | 54.8 |

### A.3 Phase 1 configuration rerun (14 configurations, 840 episodes)

| Configuration | MSMI/100 |
|---|---:|
| `hard_plus_soft_maxw` | 0.567 |
| `potential_ask` | 0.525 |
| `hard_plus_soft_greedy` | 0.500 |

### A.4 Reproduction checks

| Check | Result |
|---|---|
| Phase 1 incumbent vs stored per-episode record, Phase 1 seeds | **60 / 60 episodes identical**; 0.5250 and 63 events |
| Unsigned vs signed weight coding, Phase 1 seeds | 0.525 / 63 events vs 0.367 / 44 events |
| In-process vs official `evaluate.py`, seed 1101 | Identical MSMI, coverage and ask cost on both families tested |
| 120-seed `greedy` re-run vs transcription | Four exact matches to three decimals |

---

## Appendix B: Configuration inventory

| Arm | Origin | Description |
|---|---|---|
| `greedy` | supplied baseline | Asks on the supplied hard-constraint rule; matches greedily on agreement count |
| `random_feasible` | supplied baseline | Random feasible asking and matching |
| `no_ask` | supplied baseline | No clarification; matches on observed fields only |
| `potential_ask` | Phase 1 incumbent, reconstructed | Asks ranked by expected matching-unlock value; matches on **unsigned** agreement count |
| `signed_potential` | ours | As above with signed weights; a genuinely different policy, 0.158 apart |
| `waitfloor` | ours | Delays introduction until a minimum waiting floor is met |
| `oldest_first` | ours | Serves the longest-waiting members first |
| `disagreement_aware` | ours | `greedy` with known disagreements scored negative instead of zero |
