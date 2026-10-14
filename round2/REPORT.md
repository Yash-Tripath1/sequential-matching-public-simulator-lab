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
| **Ask priority** (longest-wait first) | −0.038 (p = 0.136, n.s.) | **−1.05 d p90** (p < 0.001) |

Clarification is worth roughly ten times anything else we tested. Pairing
*quality* matters; pairing *quantity* does not. Ask *priority* is free on the
outcome and is a pure fairness lever.

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

Six of the seventeen are reproducible; **eleven are not**. Five of the six are named
below, alongside the best-known non-reproducible configuration.

| configuration | Round 1 | reproducible today |
|---|---:|---|
| `greedy` | 0.350 | **yes, exact** |
| `no_ask` | 0.167 | **yes, exact** |
| `random_feasible` | 0.358 | **yes, exact** |
| `max_weight_similarity` | 0.408 | **yes, exact** |
| `potential_ask` (incumbent) | 0.525 | yes, after fixing the sign error |
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

`oldest_first` holds the matcher identical to the incumbent and changes one
thing: every clarification slot goes to the longest-waiting askable member,
instead of the most promising one. Paired by seed, lower is better:

| metric | `greedy` | `oldest_first` | diff | 95% CI |
|---|---:|---:|---:|---|
| mean wait (served) | 6.813 | **6.667** | +0.146 | [+0.033, +0.259] |
| **p90 wait (served)** | 16.725 | **15.675** | **+1.050** | [+0.742, +1.358] |
| median wait (served) | **4.533** | 4.929 | −0.396 | [−0.604, −0.188] |
| unserved / 200 | 133.301 | 133.150 | +0.151 | [−0.007, +0.315] |

Asking strategy removes **1.05 days from the p90 wait** at no significant cost
to the outcome. It gives up 0.40 days of median speed for the best-matched
members and buys a shorter tail for everyone else.

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

---

## 7 Limitations

- All results describe the supplied synthetic simulator. They are not evidence
  about real matching, real people, or any product.
- Six of the seventeen Round 1 configurations are reproducible; eleven are not,
  and we make no claim about them.
- `oldest_first` is validated against our own instrumentation only; it has no
  external anchor against the organiser's evaluator, unlike the three baselines.
  Its waiting result rests on that instrumentation.
- The `waitfloor` arm ran under a signed-ranking defect and is **not reported**.
- The disparity decomposition measures reachable supply after the episode; no
  policy observes these attributes, and the generator contains no demographic
  term.
- Only one reconstruction of a lost configuration was attempted, and it failed.

---

## 8 Submission contents

| requirement (PROBLEM_STATEMENT §12) | where |
|---|---|
| Policy | `code/policy.py` |
| Dockerfile | `Dockerfile` |
| Pinned dependencies | none required for the shipped arm; `requirements.txt` documents the optional one |
| Reproducible evaluation command | `REPRODUCE.md` |
| Machine-readable results | `results/` |
| Technical report | this file |
| Attribution | `LICENSE.kit` |
| All three baseline comparisons | §5.1–5.2 |
| At least one ablation | §5.3 (clarification), §5.4 (pairing), §5.5 (ask priority) |
| Scenario-level results | `results/primary_120seeds.json` → `ceilings` (per-family). Per-family policy scores: see §8.1 |
| Declared training seeds | none — no model is fitted |
| Inference random seed | `PYTHONHASHSEED=0`, pinned in the Dockerfile |

### 8.1 Per-scenario results — status

`analyse.py` computes the primary score **per scenario family** for every arm and
prints it, but that breakdown was not captured into `results/` when the 120-seed run
was analysed. `results/primary_120seeds.json` therefore carries per-family *ceilings*
but not yet per-family *policy scores*.

This is a known gap in the archived artifacts, not a gap in the experiment — the
numbers exist and are regenerated with the command in `REPRODUCE.md` §3. We flag it
rather than point to a file that does not contain what we claim.

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
