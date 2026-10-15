# The Sequential Matching Problem — Round 2 Technical Report

**Team:** Bipartite Bard (solo entry) · Anadi Tripathi, IIT Madras
**Kit:** RomeoJulietLove/The-Sequential-Matching-Problem, participant specification 1.0.0
**Kit commit:** `a8e26b3` · `kit.py` SHA-256 `0d2cb3d3b46ca2a6…`
**Report date:** 13 October 2026

---

## 1 Summary

We built a decision policy for sequential reciprocal matching under uncertainty
and evaluated it against the three supplied baselines on **120 fresh seeds × 6
scenarios × 4 policies = 2,880 episodes**, paired on identical worlds.

**Headline result: the supplied `greedy` baseline was the strongest policy we
could run, and we ship it.** Nothing we designed beat it. We report that plainly
rather than tuning until something won.

What we gained instead is a decomposition of *which components matter*:

| component varied | effect on primary outcome | effect on waiting |
|---|---:|---|
| **Clarification on/off** | **−0.304** (p < 0.001) | askable pool never drains |
| **Pair choice** (random vs greedy) | **−0.070** (p = 0.004) | none |
| **Ask priority + matcher** (`oldest_first` arm) | −0.038 (p = 0.136, n.s.) | **−1.05 d p90** (p < 0.001) |
| **Matcher rescoring** (only the fields that matter) | −0.011 (n.s.) | none |

Clarification is worth roughly ten times anything else we tested. Pairing
*quality* matters; pairing *quantity* does not. Ask *priority* is free on the
outcome and is a pure fairness lever. And the matcher barely matters at all:
three independent designs put its main effect near zero, rescoring it on only the
fields that enter the acceptance probability changes nothing (§5.11), and holding
the ask rule fixed while swapping the matcher moves the score by +0.003 (§5.13).

We also tested the one configuration with a real claim to beating the baseline.
`potential_ask` led Round 1 at 0.525 against `greedy` at 0.350. Across **all 120
of our seeds** it scores **0.369 against `greedy` at 0.402** — a gap of −0.033
[−0.090, +0.025] — and Round 1's +0.175 sits **seven standard errors** away
(§5.14). That run also re-derived the shipped baseline from scratch in a
different environment and matched the transcribed 120-seed figures on four
statistics to three decimals, which closes the only provenance gap in §5.1–5.6.

We also built and measured a fix for a real defect in the shipped matcher — one
**Round 1 had already identified** ("Unknown is not disagreement", §4.1 of that
note) and which we reached independently from the calibration data. It scores
only agreements, so a known disagreement counts the same as an unknown field,
even though §5.12 measures that gap at 20 acceptance points. Penalising known
disagreements is a one-line change, and it is **the only arm in the study that
finishes above `greedy` at 120 seeds** (0.415 vs 0.402). We still do not ship it:
at +0.013 [−0.025, +0.051] it is roughly **one twelfth of what the organisers'
own 20-seed assessment can resolve** (Round 1 §5.5), and the sign flips between
our own seed blocks. §5.15 reports it in full, with its prior art and the power
calculation, as the first thing we would pursue with more compute.

### Number to remember

The same code, unchanged, scored **0.489** on seeds 1101–1130 and **0.336** on
seeds 1131–1160. Which seeds you draw matters about ten times more than which
policy you ship.

---

## 2 The question

A policy must decide, each day for 60 days:

- which members to ask a clarifying question of (budget 12 units/day),
- which feasible, non-overlapping introductions to propose,
- when to propose nothing and wait.

Both parties must be willing and able; neither person's stated constraints may
be overridden by a favourable score. Feedback arrives after the decision. Some
answers are missing; some are declined and permanently unavailable.

The organiser ranks submissions on a single primary outcome:

> **MSMI** — completed meeting **and** mutual second-meeting intention, per 100
> arrived members, averaged over six scenario families.

Ties break on coverage, then mutual acceptances, then lower clarification cost,
then lower inference time. **Waiting time is a reporting requirement, not a
ranking input** (PROBLEM_STATEMENT §10).

---

## 3 Method

### 3.1 Shipped policy

`greedy` — the organiser's own baseline: ask using the supplied ranking, match
using the supplied matcher. It is shipped unmodified.

We chose it after testing three alternatives (§5). It is not a wrapper around
anything we built; it is the baseline, shipped because it won, with the evidence
that it won.

Implementation is a single-file JSON stdin/stdout protocol adapter
(`code/policy.py`). It imports only the standard library for this arm; the
max-weight arms import networkx lazily, so the shipped image has **zero
third-party dependencies**. Any internal failure degrades to a valid empty
action rather than an invalid episode, because a single invalid assessed episode
makes the whole entry ineligible.

### 3.2 Harness

`code/waitlab.py` drives `kit.Simulator` in-process, mirroring
`evaluate.py::episode` exactly: 60 decision days, then a 40-day follow-up, then
`sim.metrics()`. Each episode is independent and reproducible from
`(seed, variant, arm)` alone.

`code/analyse.py` computes the primary score as the unweighted mean of six
family means, with a **seed-block bootstrap** — seed is the only valid
resampling unit, because `delayed`, `shift` and `drift` reuse the same 200
members as `development` within a seed, so six scenarios is ~3 independent
worlds, not 6.

### 3.3 Validation against the organiser's evaluator

This is the check that would catch a harness defect. We ran the official
`evaluate.py --baseline {greedy,no_asks,random}` and our harness on **identical
seeds** and compared:

| arm | msmi_per_100 | coverage | ask_cost |
|---|---:|---:|---:|
| greedy | 0.708333 vs 0.708333 | 0.347917 vs 0.347917 | 194.5 vs 194.5 |
| no_ask | 0.166667 vs 0.166667 | 0.127083 vs 0.127083 | 0 vs 0 |
| random_feasible | 0.500000 vs 0.500000 | 0.350417 vs 0.350417 | 194.5 vs 194.5 |

**9/9 exact matches to machine precision**, across three independently-written
policies including our own reimplementations of two baselines.

---

## 4 Reproducibility statement

Round 1 reported **1,326 episodes across 17 configurations**. The code behind
**11 of those configurations was never committed** and does not survive in any
of the three locations we searched (the original VM bundle, a Drive snapshot
timestamped 9 Oct 08:03 IST, and a 47-file re-upload that proved byte-identical
to the repository in all 47 cases).

We therefore make **no claim** about any configuration we cannot run. This
report cites only work whose code is included here.

We have verified the Round 1 numbers were genuinely computed rather than
fabricated: the Appendix B.9 funnel table reconciles internally in all 13 rows
across seven mutually constraining columns, its implied stage rates reproduce
the separately-reported stage-rate table to three decimal places, and the five
configurations overlapping our surviving per-episode data match exactly.

**Lesson carried forward:** rebuilding a Round 1 configuration from the written
description alone produced the *wrong* policy. A signed-vs-unsigned disagreement
in the agreement score gave 0.367 where the incumbent scored 0.525. Configurations
must be verified by scoring, not by name.

Six of the seventeen are reproducible; **eleven are not**. Of those six, **five
reproduce exactly** and one (`potential_ask`) reproduces only after correcting a
sign error, so the stricter count is five exact plus one patched. All six are
named below, alongside the best-known non-reproducible configuration. (An earlier
draft of the README said thirteen were never committed; eleven is the figure
consistent with the table below and is the one we stand behind.) The six are exactly the
methods present in the surviving 360-episode artifact (6 methods x 6 families x
10 seeds), which is why that number, and not a larger one, is what we can cite.

| configuration | Round 1 | reproducible today |
|---|---:|---|
| `greedy` | 0.350 | **yes, exact** |
| `no_ask` | 0.167 | **yes, exact** |
| `random_feasible` | 0.358 | **yes, exact** |
| `max_weight_similarity` | 0.408 | **yes, exact** |
| `potential_ask` (incumbent) | 0.525 | yes, after fixing the sign error |
| `potential_ask_greedy` | 0.467 | **yes, exact** |
| `lab_potential_core4_maxw` | 0.592 | **no code survives** |
| remaining 10 of 17 | — | **no code survives** |

An attempt to reconstruct `lab_potential_core4_maxw` (potential-ranked asking
with max-weight matching on the four core soft fields) was made and **abandoned**;
the reconstruction did not run successfully and no result from it is reported.

---

## 5 Results — 120 fresh seeds, 2,880 episodes

Seeds 1101–1220. All policies on identical worlds, paired. Seed-block bootstrap.
No multiplicity correction; six pre-specified contrasts.

### 5.1 Primary outcome

| arm | MSMI/100 | 95% CI | events | coverage | cov/ceiling | ask | unserved/200 |
|---|---:|---|---:|---:|---:|---:|---:|
| **`greedy`** (supplied, shipped) | **0.402** | [0.357, 0.448] | 579 | 0.333 | 0.978 | 197 | 133.3 |
| `oldest_first` (ours) | 0.364 | [0.319, 0.409] | 524 | 0.334 | 0.980 | 197 | 133.2 |
| `random_feasible` (supplied) | 0.332 | [0.292, 0.374] | 478 | 0.335 | 0.982 | 197 | 133.0 |
| `no_ask` (supplied) | 0.098 | [0.075, 0.122] | 141 | 0.120 | 0.344 | 0 | 176.0 |

### 5.1b Per-scenario results

MSMI/100 by scenario family. The headline score is the unweighted mean of the six
family means; these are the components.

| arm | development | sparse | cold_start | delayed | shift | drift | mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| **`greedy`** | **0.496** | **0.125** | **0.421** | **0.404** | **0.479** | **0.487** | **0.402** |
| `oldest_first` | 0.471 | 0.092 | 0.354 | 0.396 | 0.417 | 0.454 | 0.364 |
| `random_feasible` | 0.429 | 0.113 | 0.308 | 0.383 | 0.362 | 0.396 | 0.332 |
| `no_ask` | 0.138 | 0.013 | 0.062 | 0.129 | 0.113 | 0.133 | 0.098 |

**`greedy` is the highest-scoring arm in all six families**, not merely on average.
That is a stronger basis for the ship decision than the aggregate alone, because it
cannot be an artefact of one family dominating the unweighted mean.

Two further readings:

- **`sparse` dominates the variance.** Every arm scores roughly a quarter of its
  `development` value there. It is the hardest family by a wide margin and the main
  contributor to between-seed spread.
- **`oldest_first` reverses in `sparse`** (0.092, below `random_feasible` at 0.113)
  while leading it in the other five. Since `oldest_first` differs from `greedy` in
  both ask rule and matcher (§5.5), the most likely explanation is that
  `max_weight_pairs` handles sparse eligibility worse than `kit.baseline_match` —
  consistent with `random_feasible` also falling furthest behind there.

### 5.2 Paired contrasts

| contrast | diff | 95% CI | p | W/T/L |
|---|---:|---|---:|---|
| greedy − oldest_first | +0.038 | [−0.010, +0.089] | 0.136 | 199/355/166 |
| **greedy − random_feasible** | **+0.070** | **[+0.023, +0.116]** | **0.004** | 205/385/130 |
| greedy − no_ask | +0.304 | [+0.261, +0.349] | <0.001 | 343/357/20 |
| oldest_first − random_feasible | +0.032 | [−0.019, +0.083] | 0.239 | 214/331/175 |
| oldest_first − no_ask | +0.266 | [+0.221, +0.312] | <0.001 | 311/378/31 |
| no_ask − random_feasible | −0.234 | [−0.281, −0.189] | <0.001 | 44/391/285 |

`greedy` is the only arm that significantly beats `random_feasible`.
`oldest_first` does not (p = 0.239). This is why we ship `greedy` rather than
our own policy.

### 5.3 Ablation 1 — clarification is load-bearing

Removing clarification entirely:

- coverage falls from ~98% of the structural ceiling to **34.4%**
- primary outcome falls by **0.304** (p < 0.001)
- **43 more members per 200 are left unserved**

The mechanism is visible in the askable pool. Under every asking arm it drains
to zero (46 → 31 → 16 → 4 → 1 → 0). Under `no_ask` it **grows** (46 → 51 → 55 →
60 → 65 → 64 → 60 → 58) and never resolves, because members accumulate
unresolved constraints faster than they can be matched.

Every other design choice in this study moves the primary outcome by
hundredths. Clarification moves it by three tenths.

### 5.4 Ablation 2 — pairing quality, not pairing quantity

| arm | coverage | cov/ceiling | MSMI/100 |
|---|---:|---:|---:|
| `greedy` | 0.333 | 0.978 | **0.402** |
| `random_feasible` | **0.335** | **0.982** | 0.332 |

`random_feasible` makes *more* introductions and reaches a *higher* fraction of
the achievable ceiling — and scores 0.070 lower (p = 0.004). Both arms spend the
same clarification budget (197). The entire difference is **which** feasible
pairs get chosen.

The bottleneck is not how many people you serve. It is whom you pair them with.

### 5.5 Ablation 3 — ask priority is a free fairness lever

**This arm is not a clean single-variable ablation, and we say so.**
Relative to `greedy`, `oldest_first` changes **two** things at once: the ask rule
(`asks_oldest_first` instead of `asks_greedy`) *and* the matcher
(`max_weight_pairs` instead of `kit.baseline_match`). Relative to the Round 1
incumbent `potential_ask` it changes only the ask rule, because those two arms
share `max_weight_pairs` — but `potential_ask` was not part of the 120-seed run,
so that clean contrast is not available at this sample size.

The table below therefore reports the **arm** comparison, and the effect must not
be read as the causal effect of ask priority alone. Paired by seed, lower is better:

| metric | `greedy` | `oldest_first` | diff | 95% CI |
|---|---:|---:|---:|---|
| mean wait (served) | 6.813 | **6.667** | +0.146 | [+0.033, +0.259] |
| **p90 wait (served)** | 16.725 | **15.675** | **+1.050** | [+0.742, +1.358] |
| median wait (served) | **4.533** | 4.929 | −0.396 | [−0.604, −0.188] |
| unserved / 200 | 133.301 | 133.150 | +0.151 | [−0.007, +0.315] |

The `oldest_first` arm shows **1.05 days less p90 wait** at no significant cost to
the outcome, giving up 0.40 days of median speed for the best-matched members and
buying a shorter tail for everyone else. Because two components change together,
we attribute this to the arm rather than to ask priority specifically.

We did **not** ship it: the outcome is the ranked metric and the interval on the
outcome difference [−0.010, +0.089] does not exclude a real loss, whereas
waiting is only reported. This is a judgement call, stated as one.

### 5.6 A trap in the waiting table

| arm | mean wait | median | **served/200** |
|---|---:|---:|---:|
| `no_ask` | **3.99** | **0.0** | **24** |
| `greedy` | 6.82 | 4.0 | 67 |

`no_ask` appears to have the *best* waiting times. It does not. Waits are
conditional on being served, and `no_ask` serves only 24 of 200 — the few
already fully observable on arrival, matched instantly.

**Waiting statistics must be reported alongside the unserved count.** Reported
alone, they make the worst policy look the fairest.

### 5.7 Allocation disparity is a property of the world

24,000 members per arm. Three-leg decomposition: eligibility supply (world),
ask allocation (policy), realised access (policy).

| group | supply | served\|reachable | ask units |
|---|---:|---:|---:|
| zone_a | 0.47 | 0.97–0.98 | 0.9–1.0 |
| zone_b | 0.32 | 0.98 | 1.0 |
| zone_c | 0.22 | 0.99 | 1.0 |
| zone_d | 0.10 | 0.99–1.00 | 0.9 |
| gender (3 levels) | 0.38–0.40 | 0.97–0.98 | 0.9–1.0 |
| age (4 bands) | 0.36–0.41 | 0.97–0.98 | 0.9–1.0 |

Zone supply spans **4.7×**; gender and age are flat. Those are negative
controls: the audit has power to detect disparity, and it finds it only where
the world creates it.

Leg 2 (ask units) and Leg 3 (served among reachable) are flat for **every**
group in **both** arms. **The disparity is not produced by the policy.** It
cannot be removed without overriding members' stated `acceptable_zones`, which
the rules forbid. The residual smoking effect (served 0.95–0.96 for `yes` vs
0.98 for `no`) is the only policy-adjacent gap we found.

The generator contains no demographic term anywhere; this disparity arises
purely from how eligibility constraints intersect with zone distribution.

### 5.8 Why no learned scorer can help

Variance decomposition of the acceptance logit
`z = −0.25 + bias + fit + shared + drift`, over 30 worlds and 120,000 pairs:

| component | SD | share |
|---|---:|---:|
| `fit` — 4 soft-field agreements (**observable**) | 0.636 | **36.5%** |
| `bias` — per member, N(0, 0.7) (**latent**) | 0.708 | 45.2% |
| `shared` — per pair, N(0, 0.45) (**latent**) | 0.451 | 18.3% |

**64% of the variance in the acceptance outcome is unobservable by construction.**
The observable 36.5% is exactly the four soft-field agreement indicators already
used by the supplied baselines. This is a bound on the problem, not a limitation
of our modelling, and it is why we did not ship a learned scorer.

### 5.9 Round 1's headline claim did not replicate

| | incumbent − greedy | 95% CI | seeds |
|---|---:|---|---:|
| Round 1 note | **+0.175** | [+0.092, +0.258] | 10 |
| Parallel confirmation | +0.008 | [−0.217, +0.233] | 10 |
| This work | **−0.044** | [−0.175, +0.081] | 30 |
| **Pooled** | **−0.031** | **[−0.143, +0.080]** | 40 |

The reported advantage does not survive fresh seeds. Our reading: it was the
maximum of 17 configurations evaluated on 10 seeds, and the selection effect is
larger than the effect itself.

---

### 5.10 A second, independent fresh-seed study (parallel workstream)

A separate workstream ran an independent Round 2 study on a **separate set of ten
fresh seeds (reported as spanning 1111–2020)**, six families, 360 episodes, with
the same seed-block resampling discipline. We report its results here because they
answer the same three questions on worlds neither study's design decisions ever
saw. Where the two studies disagree, that disagreement is itself the finding.

> **Caveat — these seed sets may not be strictly disjoint.** Our own block covers
> 1101–1220. If the parallel study's ten seeds are evenly spaced across its
> reported range (1111, 1212, …, 2020), then seed 1111 falls inside both sets and
> the two studies share one world. We were not able to recover the exact seed list
> from the parallel workstream's notes before the deadline, so we flag the possible
> overlap rather than assert independence. **No conclusion in this report depends
> on combining the two seed sets**: every pooled figure we quote is computed within
> our own 120 worlds. Any future figure that did pool them would double-count
> world 1111 and should say so.

**Confirmation (Q1) — the same answer, independently.** The incumbent's edge over
`greedy` measured **+0.008, 95% CI [−0.217, +0.233], sign-flip p = 1.000,
W/T/L 14/27/19**. On the parallel study's own ten seeds `greedy` moved little
(0.350 → 0.358) while the incumbent moved a great deal (0.525 → 0.367). That
contrast rests on ten worlds and should not be read as evidence that `greedy` is
stable in general — §6 shows our own seed blocks move it by ≈0.15. Two
independent fresh-seed studies nevertheless agree on the substantive point:
**the chosen configuration is not confirmed.**

| configuration | fresh-seed primary | 95% CI | Round 1 (screen seeds) |
|---|---:|---|---:|
| Potential asks · global match (incumbent) | 0.367 | [0.192, 0.558] | 0.525 |
| Potential asks · greedy ordering | 0.442 | [0.267, 0.617] | 0.467 |
| Greedy + default asks (official) | 0.358 | [0.225, 0.517] | 0.350 |
| Max-weight similarity | 0.258 | [0.142, 0.400] | 0.408 |
| Random feasible (official) | 0.208 | [0.100, 0.325] | 0.358 |
| No clarification (official) | 0.067 | [0.000, 0.183] | 0.167 |

What *does* survive is the step function: `greedy − no_ask` on fresh seeds is
**+0.292, CI [+0.108, +0.483], p = 0.023, W/T/L 27/29/4**. Asking at all remains
the only robust lever, replicating our own −0.304 at 120 seeds in sign and magnitude.

**Interactions (Q2) — the same null, independently.** Fresh-seed factorial effects:
ask main **+0.096 [−0.088, +0.288]**, allocation main **−0.088 [−0.204, +0.038]**,
ask × allocation interaction **+0.025 [−0.200, +0.267]**. All three straddle zero.
Pooling the allocation effect with its Round 1 value (+0.058) gives roughly
**−0.015 over twenty seed blocks**: global maximum-weight matching adds nothing on
average over greedy ordering.

This is the second independent measurement of a null interaction. The first, on
Round 1's ten-seed factorial, was **0.000 [−0.117, +0.125], p = 1.000**. Two
designs, two seed sets, same answer: **the components are additive.**

**A discrepancy we are not going to paper over.** On this study's fresh seeds,
potential asks + greedy ordering (0.442) sits *above* greedy (0.358). On our own
30-seed set it sits *below* it (0.444 vs 0.489). The two studies disagree in sign.
Given that seed-set variation is roughly ten times any policy difference (§6), this
is the expected behaviour of small effects, not a contradiction to be resolved by
picking the flattering number. We report both.

**Calibration and waiting (Q3).** An analysis-only world audit across the twenty
fresh worlds found the Round 1 fitted prior's lowest-bin miscalibration reproduced
exactly: **predicted 0.090, observed 0.157**. Mean latent response rate is flat
across observability groups (0.758 / 0.764 / 0.758) while the declined-hard-field
share moves sharply (74% / 70% / 1%) — observability selects *who is askable*, not
*who is compatible*.

On waiting: `no_ask` serves 25 of 200 at a 3.55-day mean wait, while every asking
rule serves about 65 at 6.3–7.0 days. The four asking rules' unserved counts agree
to within 0.5 members. **Rules change whether members wait, not who waits** — the
unserved set is a property of the world's infeasible core, not of the policy.

### 5.11 The matcher is not the bottleneck (a fourth ablation)

`kit.baseline_match` scores an unweighted count over **seven** soft fields, but the
generator's acceptance probability uses only **four**, with unequal weights
(`relationship_goal` 0.7, `relationship_pace` 0.4, `lifestyle` 0.25,
`conversations` 0.2). Three fields that cannot affect acceptance are counted
equally with four that can.

We tested whether fixing this helps, holding the supplied ask rule fixed:

| matcher — **30 seeds** (1101–1130) | MSMI/100 | vs supplied | paired SE | W/T/L |
|---|---:|---:|---:|---|
| `greedy7` — supplied baseline (7 fields, unweighted) | 0.489 | — | — | — |
| `core4` — only the 4 that matter | 0.478 | **−0.011** | 0.040 | 8/14/8 |
| `core4w` — the 4, weighted as generated | 0.458 | **−0.031** | 0.041 | 9/10/11 |

**It does not help.** Both differences are within noise. The extra fields are not
diluting a signal; and more to the point, the choice of matcher is not where the
outcome is decided. This is a fourth ablation pointing the same direction as the
other three: clarification is the lever, and everything downstream of it is
second-order.

The weighted variant is also the one that *should* be most exposed to changing
conditions, since `shift` reweights the same four fields to 0.25 / 0.8 / −0.25 / 0.5
and we do not adapt. It does worst in `shift` (0.533 vs 0.583), consistent with a
static weighting going stale — the same staleness the calibration work in §5.12
is designed to measure directly.

---

### 5.12 Directional calibration (our study)

The parallel study in §5.10 measured calibration at the level of the fitted prior.
Here we measure it directly on the shipped policy: **53,908 directional outcomes**
from 360 episodes (60 seeds × 6 families), logging each introduction as **two
separate directional draws**, since `a→b` and `b→a` are distinct events sharing
only the pair-level `shared` term.

23.4% of directions produce no answer (non-response), and are excluded from
calibration rather than imputed.

**1. The score carries real signal.** Empirical directional acceptance rises
monotonically with the policy's observable agreement count:

| known agreements | n | empirical acceptance | 95% CI |
|---|---:|---:|---|
| 0 | 29,073 | 0.459 | [0.450, 0.468] |
| 1 | 6,929 | 0.488 | [0.465, 0.511] |
| 2 | 3,881 | 0.536 | [0.508, 0.565] |
| 3 | 1,291 | 0.666 | [0.622, 0.708] |
| 4 | 129 | 0.698 | [0.540, 0.837] |

**2. But the score has a blind spot, and it is large.** The generator scores a
disagreement as `−0.5 × weight`; the policy scores it as `0`, the same as *unknown*.
Holding agreements fixed and varying known disagreements:

| known agreements | known disagreements | n | acceptance |
|---:|---:|---:|---:|
| 0 | 0 | 4,370 | **0.492** |
| 0 | 1 | 792 | 0.437 |
| 0 | 2 | 58 | 0.345 |
| 0 | 4 | 386 | **0.288** |
| 1 | 0 | 459 | 0.617 |
| 1 | 3 | 863 | 0.410 |

The policy assigns these the **same score** to a pair with no known agreements and
no known disagreements (0.492) and one with four known disagreements (0.288) — a
**20-point gap it cannot see**. This is a concrete, fixable defect in the ranking
function, and it is the single clearest calibration finding in this study.

**3. Calibration holds when the world is stationary and fails when it changes.**
Mean predicted minus observed acceptance, by family and day block:

| family | days 0–19 | days 20–34 | days 35–59 |
|---|---:|---:|---:|
| development | +0.003 | −0.010 | +0.006 |
| sparse | +0.003 | +0.010 | −0.009 |
| cold_start | +0.009 | +0.005 | +0.019 |
| delayed | +0.005 | −0.024 | −0.004 |
| **shift** | **−0.028** | **−0.027** | **−0.032** |
| **drift** | +0.003 | −0.010 | **−0.097** |

Two distinct failures, both predicted by the generator:

- **`shift`** reweights the soft fields (`relationship_pace` 0.4 → 0.8, `lifestyle`
  0.25 → −0.25). An unweighted agreement count no longer tracks acceptance, so
  calibration is off by about **0.03 uniformly**, from the first day.
- **`drift`** applies a −0.5 logit penalty from day 35. Calibration is fine before
  (gap +0.003, −0.010) and then collapses to **−0.097** after.

This is "test under changing conditions" made concrete: **a static calibration is
correct on stationary worlds and wrong by up to ten points on changing ones.** The
calibration *slope* tells the same story — 1.00 on development, 0.65 on sparse,
0.70 on `shift`.

**4. Most of the error is not ours.** Brier decomposition (binned on the predicted
probability):

| family | Brier | calibration | refinement | irreducible (≥) |
|---|---:|---:|---:|---:|
| development | 0.2476 | 0.0000 | 0.2476 | 0.0350 |
| drift | 0.2467 | 0.0004 | 0.2463 | 0.0345 |
| shift | 0.2483 | 0.0010 | 0.2473 | 0.0339 |

At least **14% of the Brier score is irreducible in principle** — it comes from
`bias` (N(0, 0.7)) and `shared` (N(0, 0.45)), which no policy can observe. What
remains is almost entirely *refinement* (genuine uncertainty about which pairs
succeed), not calibration error. The calibration failures that do exist are
concentrated in the changing worlds, as the table above shows.

**5. There is no demographic effect — and we can show why the raw numbers lie.**
Unconditionally, directional acceptance varies across groups:

| group | levels | spread in acceptance |
|---|---:|---:|
| gender | 3 | 0.034 |
| age | 26 | 0.081 |
| zone | 16 | 0.144 |

A 14-point spread across zones looks like a disparity. It is not. The generator
contains **no demographic term of any kind**, so any real effect would have to
come from *which* pairs get formed — and eligibility depends on zone. Conditioning
on the observable pair features removes it entirely:

| zone | n | acceptance (within `n_agree=0, n_disagree=0`, development) |
|---|---:|---:|
| zone_a | 3,479 | 0.490 |
| zone_b | 679 | 0.496 |
| zone_c | 186 | 0.478 |

The spread collapses from **0.144 to 0.018**. The disparity is composition, not
treatment: different zones have different distributions of observable pair
features, and once you compare like with like, directional acceptance is flat.
This is the same conclusion §5.7 reaches for allocation, now established for
directional calibration on independent data.

*(Note: spreads computed as max−min over many levels are upward-biased, so the
unconditional figures are descriptive only. The conditional comparison is the
decisive one and does not depend on that statistic.)*

---

### 5.13 Did we test the one serious alternative to the shipped policy?

Yes. `greedy` was chosen among four arms at 120 seeds, but the strongest
candidate from the Round 1 and parallel work was **potential asks + greedy
ordering** — the configuration that scored 0.467 on the Round 1 screen and 0.442
on the parallel study's fresh seeds, above `greedy` there. We ran it on 30 seeds
paired against the arms already measured on those same worlds.

| arm | MSMI/100 | vs `greedy` | 95% CI | p | W/T/L |
|---|---:|---:|---|---:|---|
| **`greedy`** (shipped) | **0.489** | — | — | — | — |
| `potential_ask_greedy` | 0.447 | −0.042 | [−0.148, +0.065] | 0.480 | 10/4/16 |
| `potential_ask` | 0.444 | −0.044 | [−0.175, +0.086] | 0.538 | 10/5/15 |
| `oldest_first` | 0.472 | −0.017 | [−0.125, +0.092] | 0.803 | 12/4/14 |
| `waitfloor` | 0.372 | −0.117 | [−0.232, −0.001] | 0.060 | 10/2/18 |

**Neither potential-ask variant beats the shipped baseline on our worlds.** The
point estimates favour `greedy` by about 0.04, though the intervals span zero.
This does not contradict the parallel study, which found the reverse on its own
separate seed set — it is the same small-effect instability documented in §5.10,
and we report both rather than selecting.

### The matcher effect, isolated cleanly

Because `potential_ask` and `potential_ask_greedy` use the **identical ask rule**
and differ only in the matcher, their contrast isolates allocation with nothing
else moving:

| contrast | diff | 95% CI | p | W/T/L |
|---|---:|---|---:|---|
| greedy ordering − max-weight matching | **+0.003** | [−0.073, +0.078] | **1.000** | 11/7/12 |

**The matcher effect is indistinguishable from zero, and the win/loss split is
almost symmetric.** This is the third independent measurement of the same null:

| study | matcher / allocation main effect |
|---|---:|
| Round 1 factorial (10 seeds) | +0.058 [−0.013, +0.129] |
| Parallel fresh-seed study (10 seeds) | −0.088 [−0.204, +0.038], pooled ≈ −0.015 |
| **This work (30 seeds, ask rule held fixed)** | **+0.003 [−0.073, +0.078]** |

Three designs, three seed sets, one answer: **changing the global allocation
buys nothing over the supplied greedy ordering.** Together with §5.11, where
rescoring the matcher on only the fields that affect acceptance also changed
nothing, the conclusion is well supported.

---

---

### 5.14 The definitive test: both arms on all 120 seeds

Sections 5.9 and 5.13 left an asymmetry in the comparison that mattered most.
`potential_ask` — the Round 1 incumbent — had only ever been measured on the
30-seed block 1101–1130, and that block turned out to be unusually kind to
`greedy`: 0.489 there, against 0.402 across all 120 seeds. A comparison run
inside the better half of the seed range cannot settle whether the incumbent
beats the shipped baseline. This section removes the asymmetry. We ran `greedy`
and `potential_ask` on the remaining 90 seeds (1131–1220), which gives a
complete paired comparison on all 120 worlds and the first 120-seed measurement
of the incumbent anywhere.

**Design.** 90 fresh seeds × 6 scenarios × 2 arms = **1,080 episodes** on
identical worlds. Executed as six chunks of 15 seeds (180 episodes each),
14 min 31 s to 15 min 13 s per chunk, about 90 minutes wall time on 2 workers,
**zero failed episodes**. The chunking was deliberate: this execution
environment reaps processes that run much beyond 50 minutes (we observed one
die at 51 of 1,440 episodes), so no single invocation was allowed to exceed
30 minutes. Each chunk writes to its own directory and the harness resumes from
`episodes.jsonl`, so a reaped chunk can be restarted without losing work.

| arm | seeds | episodes | MSMI/100 | 95% CI | events | coverage | ask cost | unserved/200 |
|---|---:|---:|---:|---|---:|---:|---:|---:|
| **`greedy`** (shipped) | 120 | 720 | **0.402** | [0.357, 0.448] | **579** | 0.334 | 197.5 | 133.3 |
| `potential_ask` | 120 | 720 | 0.369 | [0.324, 0.416] | 532 | 0.334 | 197.2 | 133.2 |

| paired contrast | n | diff | 95% CI | SE | p | W/T/L |
|---|---:|---:|---|---:|---:|---:|
| `greedy` − `potential_ask` | 120 | **+0.033** | [−0.025, +0.090] | 0.029 | 0.305 | 58/18/44 |

**Both halves of the seed range point the same way**, which is the part that
matters — the 30-seed result in §5.9 was not an artefact of a lucky block:

| seed block | n | `greedy` | `potential_ask` | diff | 95% CI |
|---|---:|---:|---:|---:|---|
| 1101–1130 (§5.9) | 30 | 0.489 | 0.444 | +0.044 | [−0.081, +0.175] |
| 1131–1220 (new) | 90 | 0.373 | 0.344 | +0.029 | [−0.033, +0.092] |
| **pooled** | **120** | **0.402** | **0.369** | **+0.033** | **[−0.025, +0.090]** |

Per-seed SD of the difference is 0.321, spanning −0.750 to +1.083: on
individual worlds either arm can win by a lot, and only the average is stable.

**A by-product: the 120-seed baseline is now independently verified.** The
tables in §5.1–5.6 were transcribed from terminal output on a separate machine
whose raw per-episode log we did not have. Re-running `greedy` from scratch in
a different environment reproduces them:

| statistic | this run (120 seeds) | transcribed (120 seeds) |
|---|---:|---:|
| primary MSMI/100 | **0.4021** | **0.402** |
| mutual second-meeting intentions | **579** | **579** |
| coverage | **0.3335** | **0.333** |
| unserved per 200 | **133.30** | **133.3** |
| ask cost | 197.5 | 197 |

Three of the five match exactly to three decimals and two agree to within
rounding (ask cost 197.5 vs 197; coverage 0.3335 vs 0.333). The
transcription in §5.1–5.6 is faithful, and the harness is deterministic across
machines — which also means the non-replication reported in §5.9 cannot be an
environment difference.

**What this does to Round 1's headline.** Round 1 reported `potential_ask` at
0.525 against `greedy` at 0.350 on 10 seeds — a gap of **+0.175**. Across 120
fresh seeds we measure the same gap at **−0.033** (SE 0.029). Round 1's
estimate sits **7.1 standard errors** away; our 95% interval for the gap,
[−0.090, +0.025], does not come within a factor of six of +0.175. Taken with
§5.13 (the same comparison at 30 seeds) and §5.10 (the parallel study, +0.008
on its own separate seeds), the most parsimonious explanation remains that
0.525 was the maximum of 17 configurations evaluated on the same 10 worlds.

**Waiting again diverges from outcome.** On the 90-seed block `potential_ask`
keeps people waiting slightly *less* (mean 6.36 d vs 6.81 d; p95 21 d vs 22 d;
median and p90 identical at 4 d and 16 d) while scoring *lower* on the primary
outcome. Reading the waiting table alone would favour the losing arm — the same
trap flagged in §5.6, in the opposite direction.

**Conclusion.** The incumbent has now been measured at the same scale as the
shipped policy, on the full seed range, and it does not beat it. The interval
still contains zero, so the defensible claim remains *no alternative has
demonstrated a reliable advantage over `greedy`* — not *`greedy` is proven
optimal*. But the specific objection that motivated this section, that the
incumbent had only been tested on a favourable seed block, no longer stands.

---

---

### 5.15 The one positive signal: fixing a defect in the shipped matcher

**Round 1 found this defect first.** Its research note (§4.1, "Unknown is not
disagreement") states the bug in exactly the terms below, fixes it with the same
+1 / −1 / 0 coding, and reports the change at **+0.075 MSMI/100, 95% CI
[−0.025, +0.192], p = 0.328, W/T/L 14/39/7** on ten seeds. We did not know that
when we designed this arm — §5.12's 53,908-outcome calibration led us to the
same conclusion independently. What this section adds is therefore not the idea.
It is a measurement of the same change on **120 fresh, unselected worlds**:
twelve times the sample, and free of the selection effect that inflated every
Round 1 number (§5.9). The direction survives. The magnitude does not.

An external audit of this repository separately pointed out — correctly — that
we had identified the defect without ever testing a fix for it. This section is
that test. It produced the only arm in the entire study that finishes above the
shipped baseline at full scale, and it is also the clearest illustration of why
we still do not ship it.

**The defect.** `kit.baseline_match` (kit.py:217) scores a candidate pair by
counting soft fields where both members are known and EQUAL. A field where both
are known and DIFFERENT contributes zero — exactly the same as a field neither
member has disclosed. §5.12 measured the cost of that blind spot directly over
53,908 directional outcomes: among pairs with no known agreements, empirical
acceptance falls from **0.492** with zero known disagreements to **0.288** with
four. A pair known to be wrong on four counts is ranked identically to a pair
about which nothing is known.

**The fix.** One line. `disagreement_aware` keeps the supplied ask rule and the
supplied greedy edge selection and changes only the score: known agreement +1,
known disagreement −1, undisclosed 0 — the coding Round 1 adopted for its own
incumbent. The weight was chosen a priori and never tuned on any seed: the
measured acceptance drop per disagreement (≈0.05) is the same order as the gain
per agreement (≈0.03–0.13), so equal weighting is the neutral choice.

**Result — 120 seeds, paired on identical worlds.** Sign convention: `diff` is
*arm − `greedy`*, and W/T/L counts seeds the arm wins / ties / loses.

| arm | MSMI/100 | 95% CI | events¹ | diff | 95% CI | p | W/T/L |
|---|---:|---|---:|---:|---|---:|---|
| **`disagreement_aware`** (new) | **0.415** | [0.369, 0.463] | 433 | **+0.013** | [−0.025, +0.051] | 0.835 | 46/29/45 |
| **`greedy`** (supplied, **shipped**) | 0.402 | [0.357, 0.448] | 403 | — | — | — | — |
| `potential_ask` | 0.369 | [0.324, 0.416] | 372 | −0.033 | [−0.090, +0.025] | 0.305 | 44/18/58 |
| `potential_ask_greedy` | 0.361 | [0.317, 0.406] | 359 | −0.041 | [−0.089, +0.007] | 0.141 | 44/12/64 |

¹ mutual second-meeting intentions on the 1131–1220 block (90 seeds).

**It leads on four of six scenarios** — development +0.050 (0.546 vs 0.496),
drift +0.038 (0.525 vs 0.488), delayed +0.017 (0.421 vs 0.404), shift +0.008
(0.488 vs 0.479) — and trails on cold_start −0.025 (0.396 vs 0.421) and sparse
−0.008 (0.117 vs 0.125). The two scenarios where it loses are the two where
information is thinnest, which is what the mechanism predicts: the fix can only
act on a field that is known on both sides.

**Stability is mixed.** Splitting the 90-seed block into six independent
15-seed chunks, it leads in five of six (+0.078, +0.056, +0.006, +0.044,
−0.028, +0.011). But the earlier 30-seed block points the other way (`greedy`
+0.031). The two halves of our own seed range disagree in sign — the instability
documented in §6, again.

**Two measurements of one change.**

| | seeds | diff vs baseline | 95% CI | p | W/T/L |
|---|---:|---:|---|---:|---|
| Round 1 note §6.2b — weight coding, 7-field count → signed | 10 | **+0.075** | [−0.025, +0.192] | 0.328 | 14/39/7 |
| This report §5.15 — `disagreement_aware` vs `greedy` | 120 | **+0.013** | [−0.025, +0.051] | 0.835 | 46/29/45 |

The two intervals share a lower bound of −0.025 to three decimals. Read together
they say what §5.9 says about the incumbent: the *direction* reproduces, and the
*magnitude* shrinks by roughly a factor of six once the ten selection worlds are
replaced by 120 fresh ones.

There is also a discrepancy worth stating, because it is why this test was worth
running at all. Round 1's §4.1 prescribes +1 / −1 / 0 coding, but the
configuration we can reconstruct as its incumbent — `potential_ask`, which
reproduces its headline **0.525 and 63 events exactly** on Round 1's own seeds
(§5.9) — uses the unsigned agreement count, in which a known disagreement scores
0.0, the same as an unknown field. The signed variant of the same arm scores
**0.367 with 44 events** on those seeds. So whatever the note prescribed in
prose, the code path behind the headline number ranked a known disagreement as
no information. `disagreement_aware` is that missing fix, applied to the shipped
greedy selection and measured honestly.

**Why we still do not ship it.** Four reasons, in order of importance.

1. **The organisers' own assessment cannot resolve it.** Round 1's power
   analysis (§5.5 of that note), from a within-method per-episode SD of 0.457,
   finds that 20 private seeds × 6 families — 120 episodes, the official
   protocol — resolves a gap of about **0.165 MSMI/100**. Our +0.013 is roughly
   **one twelfth of that**. Even if the effect is exactly as estimated, switching
   the shipped policy could not be detected by the assessment that decides the
   ranking. This is the decisive reason; the three below are confirmations.
2. **This study was never powered to detect an effect this small.** With per-seed
   SD 0.214 at n = 120, the smallest effect detectable at 80% power is **0.055**.
   The observed +0.013 is **0.24× that**. Resolving it would take roughly
   **2,055 seeds** — about seventeen times the compute available to us. Calling
   this a win would be calling noise a win.
3. **The effect is smaller than the seed lottery.** §6 shows the same code moving
   by ≈0.15 between seed blocks. A 0.013 advantage cannot decide a ranking that
   sensitive to which worlds are drawn.
4. **Shipping it would repeat Round 1's error.** Round 1's 0.525 was the maximum
   of 17 configurations on 10 seeds (§5.9). Switching the shipped policy on a
   p = 0.835 difference, on the last available day, is the same mistake with a
   slightly larger sample.

**Why we report it anyway.** Because it is the only arm above the baseline at 120
seeds, it leads on four of six scenarios, it leads in five of six independent
seed chunks, it has now been arrived at twice by two independent routes (a
53,908-outcome calibration study here, a coding review in Round 1), and it is a
one-line change with no new dependencies and no effect on eligibility, budget or
episode validity. **With another week, this is the first thing we would run at
2,000 seeds.** We would rather hand the organisers a measured, honestly
underpowered positive signal — together with its prior art — than a tuned claim.

**Two structural cross-checks against Round 1.** Round 1 computed coverage
ceilings on its own seeds with its own scripts; we computed ours independently
on 120 different seeds. They agree to within about 3%: development 0.399 vs
**0.387**, cold_start 0.341 vs **0.334**, sparse 0.178 vs **0.167**. Round 1's
hypothesis H6 — that coverage converges to the structural ceiling whatever the
asking rule — is confirmed here from below as well: every asking policy we ran
lands at 97–98% of ceiling, and `greedy` sits at **0.978**, matching Round 1's
reported band exactly.

**A Round 1 question this report closes.** Round 1 listed hypothesis H4 —
"waiting/batching helps in supply-rich families" — as *untested, planned work*.
§5.5 and §5.6 test it: `oldest_first` cuts p90 waiting by **1.05 days**
(p < 0.001) but moves the primary outcome by only +0.038 (p = 0.136). H4 is
supported for waiting and not supported for the outcome — the divergence in §5.6,
stated as a hypothesis verdict.

Cost of this section: 1,260 episodes, about 97 minutes on 2 workers, zero failed
episodes. Per-seed values for all four arms are in
`results/greedy_vs_potential_120seeds.json`.

---

## 6 Uncertainty — what this study cannot resolve

**Seed-set variation dominates policy variation.** The same code scored 0.489
and 0.336 on two disjoint 30-seed sets. At 120 seeds, per-seed SD is 0.26–0.28,
so on the organiser's **20 private seeds** the standard error is ≈ 0.06 and two
policies must differ by **more than ~0.24** to be reliably ranked.

Our largest significant effect (0.304) clears that bar comfortably. Our
ship-decision effect (0.070) does not — it is detectable at 120 seeds but would
not be at 20. We ship on the *expected value* of the primary outcome, not on
significance.

**Nothing we built beat the supplied baseline.** That is a finding about our
designs and this simulator, not a proof that no better policy exists.

**We searched a discrete design space, not a continuous one.** The candidate
set was 17 hand-specified configurations (ask rule × matcher × priority),
evaluated on shared worlds. We did not run an automated or evolutionary search
over policy parameters, for a reason that is quantitative rather than a matter
of taste: one candidate evaluation costs 720 episodes, roughly 60 minutes of
wall time at 2 workers, so a population-based search could not complete even a
handful of generations inside the round. Worse, with the per-seed SD of 0.26–0.32
documented above, the noise floor on a 30-seed fitness estimate is ≈ 0.06, which
is *larger* than every policy gap we have measured except clarification. A
search optimised on a seed budget we could afford would be fitting noise, and
any winner would have to be re-validated on seeds large enough to make the
search pointless. We judged that a clean negative result at 120 seeds is worth
more to the organisers than an unvalidated evolved policy.

---

## 7 Limitations

- All results describe the supplied synthetic simulator. They are not evidence
  about real matching, real people, or any product.
- Six of the seventeen Round 1 configurations are reproducible; eleven are not,
  and we make no claim about them.
- `oldest_first` is validated against our own instrumentation only; it has no
  external anchor against the organiser's evaluator, unlike the three baselines.
  Its waiting result rests on that instrumentation.
- `oldest_first` differs from `greedy` in **both** ask rule and matcher, so the
  0.038 outcome gap and the 1.05-day p90 improvement cannot be attributed to ask
  priority alone (§5.5). The clean single-variable contrast, against
  `potential_ask`, was not run at 120 seeds.
- `waitfloor` was measured on **30 seeds only** (§5.13) and is not part of the
  120-seed comparison. Its −0.117 is provisional and should not be read as an
  established result.
- The disparity decomposition measures reachable supply after the episode; no
  policy observes these attributes, and the generator contains no demographic
  term.
- Only one reconstruction of a lost configuration was attempted, and it failed.

---

## 8 Submission contents

| requirement (PROBLEM_STATEMENT §12) | where |
|---|---|
| Policy | `policy.py` (project root) — byte-identical copy of `code/policy.py` |
| Dockerfile | `Dockerfile` (project root; `python:3.12.7-slim`, copies from `code/`) |
| Pinned dependencies | none required for the shipped arm; `requirements.txt` documents the optional one |
| Reproducible evaluation command | `REPRODUCE.md` |
| Contract tests | `tests/test_policy.py` — `python -m unittest -v`, 5 tests, all pass |
| Machine-readable results | `results/` — including per-seed values for the full 120-seed greedy-vs-incumbent comparison in `results/greedy_vs_potential_120seeds.json` |
| Technical report | this file |
| Attribution | `LICENSE.kit` (organisers' kit), `LICENSE` (MIT, our code), and `docs/ROUND1_RESEARCH_NOTE.pdf` (the Round 1 note this work builds on) |
| All three baseline comparisons | §5.1–5.2 |
| At least one ablation | §5.3 (clarification), §5.4 (pairing), §5.5 (ask priority), §5.11 (matcher) |
| Head-to-head with the Round 1 incumbent | §5.14 — both arms on all 120 seeds, 1,440 episodes; machine-readable in `results/greedy_vs_potential_120seeds.json` |
| Scenario-level results | `results/primary_120seeds.json` → `ceilings` (per-family). Per-family policy scores: see §8.1 |
| Declared training seeds | none — no model is fitted |
| Inference random seed | `PYTHONHASHSEED=0`, pinned in the Dockerfile |

### 8.1 Per-scenario results — status

`analyse.py` computes the primary score **per scenario family** for every arm and
prints it, but that breakdown was not captured into `results/` when the 120-seed run
was analysed. `results/primary_120seeds.json` therefore carries per-family *ceilings*
but not yet per-family *policy scores*.

**Resolved.** The per-family scores for all four arms are now in
`results/per_family_120seeds.json` and are reported in full at §5.1b. Their
unweighted mean reproduces every headline figure in §5.1 exactly
(0.402, 0.364, 0.332, 0.098), which is an independent check on the aggregation.
Directional calibration is reported in full at §5.12, from 53,908 logged
directional outcomes.

---

## 9 One-paragraph summary for a non-specialist

We tested four ways of deciding who to introduce to whom on 120 simulated
worlds, running 2,880 complete 100-day episodes. The simplest method — the one
supplied with the challenge — worked best, and we say so. Turning off the
option to ask clarifying questions was catastrophic: it cut reachable coverage
by two thirds. Choosing *which* pairs to make mattered a lot; making *more*
introductions did not help at all. Changing who we asked first made no
difference to success but shortened the wait for the people who would otherwise
wait longest, by about a day. We also found that the apparent unfairness between
geographic zones comes from the world's structure, not from the policy, and
cannot be fixed without overriding what people said they wanted. Finally, we
could not reproduce most of our own previous round's results because that code
was never saved — so this report only claims what can be re-run from the files
we have published here.
