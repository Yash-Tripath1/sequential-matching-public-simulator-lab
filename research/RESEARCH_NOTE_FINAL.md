# The One Introduction Problem

## A supply-constrained sequential matching policy: clarification targeting, outcome-relevant weighting, and variance-aware evaluation

**Round 1 research note · Vouchsafe Sequential Matching Hackathon**
Starter release 1.0.0 · Prepared 9 October 2026

> **Team:** Bipartite Bard
> **Team leader:** Anadi Tripathi
> **Members:** Anadi Tripathi
> **Institution:** IIT Madras
> **Repository:** https://github.com/Yash-Tripath1/sequential-matching-public-simulator-lab
>
> **Declaration.** We confirm that this submission represents our team's work and that
> all external papers, datasets, code, AI tools and other resources used are
> acknowledged in §8.3 (AI tools and resources) and §8.5 (references). AI tools used:
> Arena.ai Agent Mode and additional large-language-model chat assistants (ideation,
> code debugging, drafting and pre-submission review); see §8.3.

> **Scope statement.** Every person, preference, conversation and outcome in this
> work is synthetic content from the organisers' public development kit. Nothing
> here estimates relationship compatibility for real people, and no result below
> is evidence of product effectiveness. All experiments run against the public
> simulator on public seeds; no private world, private seed or private organiser
> file was
> used. Analysis marked *analysis-only* reads simulator ground truth and is never
> imported by, or available to, any policy at inference time.

---

## 1. Abstract and thesis

Our own three-seed pilot reported that a "potential-ask" clarification heuristic
raised MSMI per 100 arrived members from 0.389 to 0.639, and a ten-seed screen
put the incumbent at 0.525 against 0.350 for the starter greedy baseline. We
reproduce the incumbent's 0.525 exactly on the same ten public seeds. Then we ask
a question neither run could answer: **how much room is actually left?**

We answer it by measuring the *structure* of the generated worlds rather than only
the scores they produce. Under complete disclosure, the reciprocal hard-constraint
graph of a 200-member development pool has mean degree **2.53**, feasible-pair
density **1.27%**, and **33.9%** of members with no feasible partner at all.
Because roughly a third of members also carry a *declined* hard field — which the
contract says must never be imputed or bypassed — the fraction who could **ever**
be introduced, under any policy with perfect clarification, is **0.399** in
development, **0.341** in cold start and **0.178** in sparse geography. The number
of distinct feasible pairs whose endpoints are never decline-blocked — a hard cap
on total introductions, since pairs cannot repeat within an episode — is **118.0**,
**90.6** and **23.3** respectively.

That reframes the problem. **The primary score in this simulator is
supply-determined, not ranking-determined.** Any asking policy that reaches the
coverage ceiling has already captured the largest available lever, and the residual
differences between matchers operate on a matching that is close to forced: with
median degree 2 there is little choice to optimise. Our own earlier ten-seed screen
pointed the same way without being able to say why — it estimated a clarification
main effect of +0.117 MSMI/100 against a matcher main effect of +0.058 — and the
structural measurement explains the asymmetry.

We therefore argue that the productive question is not "which policy ranks pairs
best?" but "**where does the attainable score actually come from?**" Our answer,
from a three-way factorial of ask rules × pair-weight rules × allocation rules at
ten seeds per family, plus an oracle ladder, is that it comes from three places in
strict order of size — and that the place most teams invest in is the smallest.

The strongest single number we can defend is not our best cell. It is the
**pre-specified** comparison of our existing incumbent against the starter
baseline, fixed by the earlier screen before the new factorial ran:
`lab_potential_maxw` scores **0.525 versus 0.350** for the official greedy
baseline, a paired difference of **+0.175 MSMI/100, 95% seed-block CI [+0.092,
+0.258], p = 0.016, 23 wins / 29 ties / 8 losses** over ten seeds × six families.
Everything else in §6 is screening, and is labelled as such.

**Caveat:** the ten evaluation seeds are the same ten used by the earlier screen
that selected this incumbent, and seeds 101/202/303 were also the three-seed
pilot on which it was first chosen. This comparison is therefore a recomputation
on selection data, not an independent confirmation.

> **Thesis.** With reciprocal hard feasibility enforced, MSMI is determined first
> by *whether a policy makes the feasible graph usable at all* — a step function
> that any clarification rule, however naive, saturates; second by *how much of
> the resulting edge supply it consumes* before members exit or retire — which we
> measure at 68–87% and which no rule we tested moved; and only third, within a
> band narrower than 60 episodes can resolve, by *how well it ranks the pairs it
> gets to choose between*. Targeting clarification at expected unlock value,
> fitting a calibrated pair-outcome model, adapting online on dense feedback and
> spending the residual budget on soft answers are all third-order interventions,
> and we report that none of them beat the incumbent — one of them, a correctly
> calibrated probability used as an edge weight, scores below a hand-coded
> similarity score in all three ask cells (suggestive only: 3 of the 78 pairwise
> intervals exclude zero, about what chance alone gives), with a candidate
> explanation in §6.2c. The two
> changes that did move the score are not models: correcting the *coding* of the
> pair weight so that a known disagreement counts as negative and every feasible
> edge keeps a positive weight, and replacing greedy ordering with global
> matching. Each is worth about half of their combined +0.133 MSMI/100, and
> neither is individually significant at ten seeds.

Stated as falsifiable hypotheses and resolved against our own runs:

| # | Claim | Verdict |
|---|---|---|
| H1 | Unlock-value ask targeting beats count-based and unranked asking at a fixed matcher | **Not supported** — differences −0.000 to +0.008 at a fixed matcher, all CIs straddling zero |
| H2 | Any asking policy beats no clarification | **Supported** — +0.183 MSMI/100, CI [+0.042, +0.325] |
| H3 | Online adaptation on dense directional responses helps in `drift`/`shift` | **Falsified as implemented** — 0 wins / 60 ties / 0 losses, MSMI outcomes identical to its static version |
| H4 | Waiting/batching helps in supply-rich families and not in sparse | **Untested** — planned (§8.1) |
| H5 | Residual soft-field clarification does *not* help, because the matching is near-forced | **Not rejected** — +0.017, CI [−0.083, +0.158], p = 0.961 (interval too wide to establish equivalence) |
| H6 | Coverage of any valid policy converges to the structural ceiling | **Supported** — every asking policy at 97–98% of it, and an oracle with free perfect clarification reaches only 0.1 pp more |

The most consequential of these is H6, because it is confirmed from two
directions. From below: all sixteen asking configurations make 4,555–4,681
introductions over their 60 episodes and land at coverage 0.340–0.343 — a spread
of 0.003, about 1% relative, across rules that differ in every design choice we
could think of. From above: an *oracle* given free, complete, instantaneous
disclosure of every non-declined field — hard and soft — reaches coverage **0.298**
against **0.297** for a random-feasible policy on the same thirty
dev/sparse/cold worlds, and **62.9** assignments against **61.9**; pushing further
to a maximum-*cardinality* matching under perfect information moves those to 0.299
and 63.1. **Perfect information buys a tenth of a percentage point of coverage and
one introduction per episode**, and it buys *fewer* assignments than the
non-oracle configuration at rung R3 of the same ladder manages on the same worlds
(63.2) — a caveat on that comparison is in §6.6. What it does buy is a
better-selected set — the mutual-acceptance rate per assignment rises from 0.144
to 0.161 — but the primary score still *falls*, from 0.300 to 0.233, because the
extra selectivity is paid for with introductions that never happen. Whatever gap
remains between a submitted policy and the attainable bound is not an information
gap, and a clarification strategy is not where it will be closed.

Three secondary results carry the mechanism, and are developed in §4.3 and §6:
**four of the seven soft fields carry no detectable outcome signal** (agreement on
`relationship_goal` doubles mutual acceptance, 0.150 → 0.312, while `lifestyle`,
`emotional_availability`, `space_for_relationship` and `relocate` sit at ratios of
0.92–1.16); **observability is a confound, not a quality signal** — mutual
acceptance is *lower* when more soft fields are known, 0.2724 with none versus
0.2317 with all seven, which is why a restricted four-predictor prior beats a
fuller eighteen-feature one on every held-out measure; and **the six families are
not drawn from one outcome function** while the policy cannot observe which family
it is in, so a single offline weight vector is misspecified for at least two of
them.

We also report what our evidence does *not* support. The potential-ask advantage
survives at ten seeds against the starter greedy baseline but its interval
against the stronger default-ask control at a fixed matcher includes zero, its
sign-flip test is unadjusted for the dozen contrasts we ran, and it **reverses in
cold start**. Our fitted outcome prior does not beat a hand-coded signed
similarity score. Our online adaptive learner produced MSMI outcomes identical to
its own static version in all 60 episodes (0/60/0), while its assignments
differed slightly (4,658 vs 4,652 in total) — so its *decisions* were not
bit-identical, only its outcomes were. The phase hybrids screened earlier are
exploratory and subject to winner's curse. And a zero MSMI count in a low-supply
family is not evidence that two policies are equivalent.

**Contributions.** (i) A structural characterisation of the generated worlds —
coverage ceilings, edge-supply caps and the binding-constraint histogram — that
turns "why is my score low?" into a measurable quantity. (ii) An
expected-unlock-value clarification rule with an empirical pass-proability prior
estimated from the supplied training pools only. (iii) A restricted, calibration-
checked pair-outcome prior fitted on self-logged randomised rollouts, with an
explicit treatment of missing answers as unknown rather than as disagreement.
(iv) A residual-budget soft-field clarification rule that no supplied baseline
uses. (v) A variance-aware evaluation protocol with seed-block bootstraps, exact
sign-flip tests and a power analysis showing what the official 120-episode
assessment can and cannot resolve.

---

## 2. Formalisation

### 2.1 Notation

An episode runs over decision days $t = 0 \dots 59$ followed by 40 follow-up
days with no new introductions. Let $V$ be the members of one pool, $|V| = 200$.
Member $i$ has an arrival day $a_i \le 20$, an exit day $e_i$, an always-observable
triple $(\text{age}_i, \text{gender}_i, \text{zone}_i)$, and a questionnaire
$\{f_{ik}\}_{k \in H \cup S}$ where $H$ is the eleven-field hard bundle and $S$
the seven soft fields. Each field carries a value, a status in
$\{\texttt{observed}, \texttt{not\_asked}, \texttt{declined}\}$, and an
observation day. Write $f_{ik} = \varnothing$ when the value is unknown.

$N = |\{i : a_i \le 59\}|$ is the scoring denominator and includes members who
later exit or are never served. The primary metric is
$\mathrm{MSMI}/100 = 100 M / N$ where $M$ counts qualifying introductions, one
per pair. The official score is the unweighted mean of six family means, each
over twenty private seeds.

### 2.2 Three-valued reciprocal feasibility

The supplied `eligibility(a, b)` returns one of three values, and the distinction
is the hinge of the whole problem:

- **`infeasible`** — at least one *observed* hard check fails in either
  direction. No amount of clarification can rescue this pair.
- **`needs_clarification`** — no observed check fails, but at least one hard
  field is $\varnothing$ for one of the two members. The pair is *blocked*: it
  may be feasible or infeasible, and the policy cannot know which.
- **`feasible`** — every hard field is observed for both members and every
  reciprocal check passes. Only these pairs may be proposed.

Reciprocity means each check is evaluated twice, once with each member as the
constraint holder: $j$'s age must lie in $i$'s stated window **and** $i$'s in
$j$'s; $j$'s zone must be in $i$'s `acceptable_zones` **and** vice versa;
`partner_smoking` and `partner_children` are one-directional preferences applied
in both directions; `relationship_structure`, `wants_children` and `schedule` are
symmetric. A favourable score cannot override any of these.

Two consequences deserve emphasis because they are easy to get wrong.

**Declined is absorbing.** `resolve_asks` will not overwrite a `declined` field,
and a $\varnothing$ hard field forces `needs_clarification`. A member with even
one declined hard field can therefore never appear in a feasible pair, on any
day, under any policy. In the ten public development worlds, **31.9%** of members
are in this state; in cold start, where fewer fields are pre-observed and so more
chances to be declined arise, **41.0%**. Spending clarification units on such a
member is a guaranteed waste, and every supplied baseline's ask filter already
excludes them — but no published analysis quantified how much of the pool that
removes.

**Zones are opaque labels with no adjacency.** The check is set membership only.
`relocate` is a soft field and does not override `acceptable_zones`.

### 2.3 The outcome funnel

An introduction produces a chain of five events, and the spec is explicit that
they must not be collapsed:

$$\text{assigned} \to \text{both respond} \to \text{mutual accept} \to \text{date} \to \text{both second-Yes, on time, in window}$$

MSMI requires a date within 30 days of assignment **and** both members returning
Yes within 3 days of that date. Our measured stage rates on 7,613 self-logged
introductions are:

| Stage | Estimate | Numerator / denominator | Controllable by the policy? |
|---|---:|---:|---|
| Both members respond by the deadline | 0.5932 | 4,516 / 7,613 | No (member-level response propensities) |
| Mutual acceptance, given both responded | 0.2573 | 1,162 / 4,516 | **Yes** — via pair selection |
| Date happens, given mutual acceptance | 0.7685 | 893 / 1,162 | No |
| MSMI, given a date | 0.0907 | 81 / 893 | **Partly** — `relationship_goal` agreement enters this stage again |
| MSMI, given an assignment | 0.0106 | 81 / 7,613 | — |

Two of the four transitions are outside the policy's control, and they are the
large losses: 41% of introductions never get two responses, and 91% of dates
fail the on-time double-Yes (only 204 of 893 dates produce two answers inside the
3-day window). The 3-day window against a 1–5 day answer delay
alone caps that last transition at $0.6^2 = 0.36$. **The realistic ceiling on
MSMI per assignment is therefore of order $10^{-2}$**, which is why a
200-member episode yields about one event and why single-episode comparisons are
meaningless.

### 2.4 MSMI as a rare, delayed, self-censoring event

Three properties drive the methodology:

- **Rare.** One event moves a 200-arrival episode's score by 0.5. Pooled across
  all our episodes the per-episode SD is reported in §6.4.
- **Delayed.** Directional responses are visible within 7 days; a date within
  roughly 21 (up to 33 in `delayed`); the second-meeting answers a few days
  after that. An MSMI label typically matures 30+ days after the assignment that
  earned it, inside a 60-day decision horizon, with policy memory reset at every
  episode boundary.
- **Self-censoring.** Feedback exists only for pairs the policy chose. The
  supplied `propensity` field is null, so no unbiased inverse-propensity claim
  can be made about the supplied files. We address this by generating our own
  randomised logs (§4.3), not by re-weighting theirs.

There is one further dynamic that a static analysis misses: when both members
return a second-meeting Yes, the simulator records
`pause_after_mutual_interest` and **both leave the market permanently**. Success
consumes supply. Since supply is the binding constraint (§3), the policy is not
simply maximising a per-day objective — every introduction spends a scarce,
non-renewable resource.

### 2.5 What the policy may observe

Only `observe()` output: arrived members with values, statuses and observation
days; the introduction list; feedback whose `observed_day` has been reached; the
cumulative ask log; the day; remaining budget. No world seed, no latent
preference, no response propensity, no arrival forecast, **no scenario label** —
which is why §4.5's non-stationarity problem has to be solved online rather than
by looking up the family. We use exactly this, plus offline-fitted assets derived
from our own rollouts on declared training seeds.

---

## 3. Structural diagnosis (analysis-only)

*This section reads simulator ground truth in order to measure the feasible
graph. It is a measurement instrument. No policy imports it, and the numbers it
produces are never available to a policy at inference time.*

### 3.1 The feasible graph is thin

Ten public seeds per family, complete disclosure, members arrived by day 59:

| Family | Feasible-pair density | Mean degree | Median degree | Members with degree 0 | Decline-blocked | **Coverage ceiling** | **Effective edges** | Max same-day matching |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| development | 0.0127 | 2.53 | 2 | 33.9% | 31.9% | **0.399** | **118.0** | 34.4 |
| sparse | 0.00245 | 0.49 | 0 | 67.0% | 32.8% | **0.178** | **23.3** | 15.3 |
| cold start | 0.01337 | 2.66 | 1 | 32.1% | 41.0% | **0.341** | **90.6** | 28.6 |
| delayed / shift / drift | identical to development | | | | | 0.399 | 118.0 | 34.4 |

*Coverage ceiling* = the fraction of arrived members with at least one feasible
partner who is also never decline-blocked. It is the value a policy with free,
perfect, instantaneous clarification would reach. *Effective edges* = feasible
pairs with neither endpoint decline-blocked; because a pair cannot repeat within
an episode, this is an upper bound on total introductions.

The sparsity of `sparse` is now quantitative rather than anecdotal. Twelve opaque
zones instead of four, with `acceptable_zones` never expanded beyond a member's
own zone, drives **67.0%** of members to degree zero and leaves **23.3** usable
pairs in the entire pool. Geography displaces `who_to_meet` as the top binding
constraint (18,176 of 19,900 pairs in seed 101, against 10,974 in development).
With ~20 assignments per episode at the measured funnel rates, the expected MSMI
in a sparse episode is about 0.24 events, i.e. **0.12 per 100** — so the published
zeros and near-zeros are what a supply-limited family produces, not a policy
failure.

### 3.2 Which constraint actually binds

Development, seed 101, all 19,900 pairs under complete disclosure:

| Blocking reason | Pairs blocked | Share of 19,900 |
|---|---:|---:|
| `who_to_meet` | 14,757 | 74.2% |
| age window | 12,116 | 60.9% |
| geography | 10,974 | 55.1% |
| `wants_children` conflict | 4,761 | 23.9% |
| smoking | 4,545 | 22.8% |
| `relationship_structure` | 3,600 | 18.1% |
| `partner_children` | 2,970 | 14.9% |
| `schedule` | 2,684 | 13.5% |
| **feasible** | **273** | **1.37%** |

Reasons overlap, so shares do not sum to one. The ordering matters for
clarification targeting: `who_to_meet`, age and geography are the three gates
that eliminate most pairs, and all three are cheap to reason about because the
relevant quantities — a member's own age, gender and zone, and the partner's —
are **always observable**. Only the constraint holder's answer is unknown.

### 3.3 Empirical pass-probability prior

Estimated from the six supplied **training** pools only (`public_01`–`public_06`,
1,200 members, per `data_manifest.json`), using only disclosed answers:

| Unknown field | Pass probability | Notes |
|---|---:|---|
| `who_to_meet` | 0.494 / 0.480 / 0.461 | by partner gender: woman / man / non-binary |
| `acceptable_zones`, same zone | **1.000** | own zone is always accepted |
| `acceptable_zones`, different zone | **0.0756** | only the 22.9% of members with two zones can pass |
| `schedule` overlap | 0.856 | |
| `relationship_structure` equal | 0.793 | 88.3% monogamous |
| `wants_children` no conflict | 0.755 | yes 0.362 / no 0.339 / unsure 0.300 |
| smoking acceptable | 0.878 | 50.4% accept any; 75.4% are non-smokers |
| `partner_children` acceptable | 0.921 | 15.5% have children |
| age window | ~0.13 | marginal used by the unlock prior; see note below |

**Age-window conditioning.** Age itself is always observable, so the age window is
never an *unknown* field in the eligibility check, and §3.2's figure (age blocks
60.9% of all fully-disclosed pairs, a ~0.39 pass rate over all 19,900 pairs) is a
different quantity: it is measured on the full pair population. The ~0.13 row is
the marginal the unlock-value rule uses when scoring blocked *candidate* pairs
under the §4.2 prefilter (same zone, |age gap| ≤ 10), estimated as described in
`scripts/estimate_priors.py` from the six training pools. The two numbers answer
different questions and must not be compared directly.

The same-zone / different-zone asymmetry is the sharpest fact in the table: a
blocked cross-zone pair carries roughly $0.076^2 \approx 0.006$ of the unlock
probability of a blocked same-zone pair, before any other constraint is
considered. Any clarification rule that ranks members without conditioning on
zone wastes most of its budget.

---

## 4. Method

We keep normalisation, modelling and allocation separate, as the integration
requirement asks. Component boundaries are explicit so each can be ablated.

### 4.1 Allocation: maximum-weight matching on a general graph

**Why this is a matching problem at all.** A member may hold **at most one
concurrent, outstanding introduction** — not one per day, and not one for the
whole episode. Two members who are both already under an outstanding introduction
cannot be assigned to anyone else until it resolves. That single rule is what
makes the per-day decision a *matching* on the feasible graph rather than an
independent ranking of pairs: choosing edge $(i,j)$ forecloses every other edge
incident on $i$ or on $j$ for as long as the introduction is outstanding. Any
allocation rule that scores pairs independently and takes the top-$k$ will
therefore propose collisions that the simulator must reject, and the rejected slot
is wasted supply.

The feasible graph is **not bipartite** — gender preferences are stated per member
and need not partition the pool — so assignment/Hungarian methods do not apply. We
use `networkx.max_weight_matching`, which implements Edmonds' blossom algorithm
(§8.5) for general graphs.

The per-day objective is $\max_{\mathcal{M}} \sum_{(i,j)\in\mathcal{M}} \hat p_{ij}$
where $\hat p_{ij}$ estimates $\Pr(\text{MSMI} \mid i,j \text{ assigned})$ and
$\mathcal{M}$ is a matching. **We state the independence assumption explicitly, as
the brief requires.** Pair outcomes are *not* exactly independent: the generator
adds a per-pair shared term, and we measure the ratio of observed joint
acceptance to the product of the two directional marginals at **1.105**, so
directional probabilities must not be multiplied without that caveat. Given the
world, however, the residual dependence is weak enough that expected MSMI is
*approximately* linear in the chosen edges, which is what makes maximum-weight
matching on $\hat p$ a good single-day objective. We report $\Pr(\text{mutual
accept} \mid \text{both responded within 7 days})$ as our estimation target
throughout, and never conflate it with $\Pr(\text{MSMI})$ or with either
directional probability; calibration of that target on held-out seeds is in §4.3.

One honest qualification, which §6.2c then tests and **refutes for our own fitted
model**: if $\hat p$ were the true outcome probability, maximum-weight matching on
it would be the exact single-day optimum. Two implementation points follow, and
both were bugs we had to fix:

- **Weights must be positive.** A signed similarity score that goes negative
  causes the matcher to *drop* the edge, forfeiting an introduction whose true
  $\Pr(\text{MSMI})$ is small but strictly positive. Under a supply constraint
  that is a pure loss. Our weights are probabilities, or logistic transforms of
  similarity, and are never $\le 0$.
- **Unknown is not disagreement.** Coding a known mismatch and an unknown answer
  both as 0 — which an "agreement count" scorer does — makes the matcher
  indifferent between "we checked and they clash" and "we have no idea". Our
  coding is $+1$ / $-1$ / $0$, and the fitted intercept absorbs the unknown case,
  which is the correct expected value under the prior.

We do not claim a sequential optimum. Waiting has value when a better partner may
arrive and cost when a member exits or a rival consumes the pair; with median
degree 2 the choice set is small, so we treat waiting as a separate hypothesis
(H4, §5.2) rather than folding it into the matcher.

### 4.2 Clarification: expected unlock value

For each askable member $i$ we score

$$V_i \;=\; \frac{1}{3}\sum_{j \,\in\, \mathcal{C}(i)} \pi_{ij}\cdot \max\!\big(0,\; w_{ij} - u_j\big)$$

and propose the highest-$V$ members while the daily budget allows.

- $\mathcal{C}(i)$ — candidate partners: same zone, $|\text{age}_i - \text{age}_j| \le 10$,
  and no *known* hard failure. Members with any unknown hard field have no
  feasible edge, so they are absent from the current matching and their own dual
  is zero; only $j$'s opportunity cost survives.
- $\pi_{ij}$ — probability that every still-unknown hard check passes, computed
  as a product of the §3.3 marginals over exactly the fields that are unknown for
  this pair. This is an empirical prior from disclosed answers, not a generator
  constant.
- $w_{ij}$ — the pair's matching value on observable soft fields (§4.3).
- $u_j$ — $j$'s opportunity cost: the weight of $j$'s edge in yesterday's
  maximum-weight matching, or 0 if $j$ was unmatched. The term
  $\max(0, w_{ij} - u_j)$ is a **reduced profit**: unlocking an edge that would
  not displace anything is worth nothing.

This is the shadow-price idea from our earlier plan, with two honest
simplifications. True duals on a general graph involve blossom variables that
`networkx` does not expose, so $u_j$ is an approximation from the realised
matching rather than an exact vertex dual. And the same-zone / age-gap
prefilters discard cross-zone candidates whose unlock probability is
$\sim 10^{-3}$ of a same-zone one; this is an approximation made for the
10-second invocation limit, and we report it as such.

**Never re-ask, never impute.** Members with a declined hard field are excluded
from the candidate set entirely; declined soft fields are excluded from soft
asks. A null is unknown, never zero, never a rejection.

### 4.3 Modelling: a restricted pair-outcome prior

**Training data.** We ran a *randomised logging policy* on eighteen declared
training seeds (11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
73, 79), disjoint from the ten evaluation seeds: unlock-value clarification plus
uniformly shuffled feasible matching. Randomised matching is what makes the log
usable — pair quality spans its whole observable range instead of concentrating
on one matcher's preferences. This produced 108 episodes and **7,613 labelled
introductions**, of which 4,516 had both members respond. Features are recorded
at assignment time; labels are harvested only after the 40-day follow-up, so no
post-action observation is attached to an earlier decision.

**Target.** $\Pr(\text{mutual acceptance} \mid \text{both responded})$ over the
7-day response window — the densest outcome-relevant stage. We fit MSMI directly
as well, and report why we do not use it as the ranking target: with a 1.13% base
rate the direct model achieves held-out AUC 0.581 and log loss 0.0611 against a
null of 0.0618, i.e. essentially no discrimination. The mutual-acceptance stage
carries the same pair-level signal at 40× the label density, and the two stages
that follow it are close to pair-independent apart from a further
`relationship_goal` effect that the acceptance model already captures.

**Specification search.** Three nested specifications, each fitted by ridge
logistic regression (IRLS, $\lambda = 3$, intercept unpenalised) and evaluated on
six held-out training seeds:

| Specification | Features | Held-out log loss | Null | Brier | AUC |
|---|---:|---:|---:|---:|---:|
| A | 7 agreement indicators | 0.55198 | 0.56650 | 0.18337 | 0.595 |
| **B (shipped)** | **4 core agreement indicators** | **0.55125** | 0.56650 | **0.18298** | **0.598** |
| C | A + 7 `both_known` + age gap + same-zone + day | 0.55722 | 0.56650 | 0.18561 | 0.574 |

Specification C loses on every held-out measure despite having four times the
parameters. The reason is diagnostic and worth stating plainly, because it is a
trap this dataset sets for any model that encodes missingness as a feature:

- Mutual acceptance is **0.2724** when no soft field is known for the pair,
  0.2546 when one to three are known, and **0.2317** when all seven are known.
  Observability is negatively associated with acceptance, because whether a
  member's answers are pre-observed is an independent draw in the generator and
  carries no preference information.
- The seven `both_known` indicators are near-collinear (a member either has a
  complete profile or does not), so the fit assigns them large offsetting
  coefficients — one reached +0.61 — that encode *who is observable*, not *who
  is compatible*.
- `same_zone` has 4,492 observations on one side and **24** on the other among
  logged pairs; its coefficient is unidentifiable and absorbs intercept shift.

The shipped prior is therefore deliberately small:

| Coefficient | Value |
|---|---:|
| intercept | −1.0065 |
| `relationship_pace`: agree | +0.5328 |
| `relationship_goal`: agree | +0.4212 |
| `conversations`: agree | +0.2958 |
| `lifestyle`: agree | −0.0702 |

**Calibration on held-out data.** The brief asks that any probability estimate
define its target and observation window and then be shown calibrated out of
sample. Target: mutual acceptance given both members responded within the 7-day
window. Fitted on 12 seeds (3,054 both-responded pairs), evaluated on the six
disjoint held-out seeds (1,462 pairs, base rate 0.2538). The table below reports
the *extended* specification C, whose wide predicted range exposes the
missingness confound; the shipped four-feature specification B has held-out log
loss 0.5513 and Brier 0.1830 on the same split:

| Predicted bin | $n$ | Mean predicted | Observed rate | Gap |
|---|---:|---:|---:|---:|
| 0.05–0.10 | 70 | 0.0897 | 0.1571 | **+0.067** |
| 0.10–0.20 | 248 | 0.1694 | 0.1532 | −0.016 |
| 0.20–0.30 | 784 | 0.2631 | 0.2640 | +0.001 |
| 0.30–0.40 | 308 | 0.3319 | 0.2922 | −0.040 |
| 0.40–0.60 | 51 | 0.4736 | 0.4706 | −0.003 |
| 0.60–0.80 | 1 | 0.6003 | 1.0000 | (n = 1, uninformative) |

The model is well calibrated across the 1,461 pairs that matter — the largest
absolute gap in a bin with $n \ge 50$ other than the lowest is 0.040, and the
three central bins holding 1,340 pairs are within 0.040 of nominal. The one real
defect is the lowest bin, where 70 pairs are predicted at 0.090 and come in at
0.157: the ridge prior over-shrinks strongly disagreeing pairs toward zero. Held-out
log loss 0.5572, Brier 0.1856 for the extended specification shown (spec B:
0.5513 / 0.1830). This is also why the note is careful about the
direction of the §6.2c result — the fitted prior *is* calibrated, and calibration
is not what makes a good edge weight here.

The coefficients are used only to rank and weight feasible edges. Probability
estimates are optional under the competition rules and do not affect ranking.

**Directional probabilities are not multiplied.** "A accepts B", "B accepts A"
and "both accept" are different quantities and the two directions are positively
dependent: on held-out pairs the observed mutual-acceptance rate is **0.2538**
while the product of the fitted directional probabilities is **0.2297**, a ratio
of **1.105**. We therefore model the joint directly. Any submission that reports
directional probabilities must state this dependence rather than assume
independence.

### 4.4 Residual-budget soft clarification

This component is new relative to every supplied baseline and to our own pilot.
Two measurements motivate it:

- The 12-unit daily budget is **not** the binding constraint. Measured ask spend
  is ≈195 units per episode against a 720-unit ceiling, and every asking method
  we tested lands within a few units of that same figure. It is not
  under-spending: 31.9% of development members are decline-blocked and so never
  askable, 36.4% already have every hard field observed at arrival, and the
  remaining askable population is exhausted well before the horizon (§6.8). The
  *askable population*, not the budget, runs out.
- Outcome-relevant soft fields are observed for only ~46% of members in
  development and ~34% in cold start. No baseline spends a single unit on them.

Once hard-bundle asks are exhausted, the rule converts residual units into
1-unit soft answers, prioritising (member, field) pairs by
$\deg(i) \times (0.2 + |\beta_k|)$ — partner availability times the field's
fitted influence. In development this lifts realised ask spend from 195 to ~558
units per episode. Whether it converts into MSMI is an empirical question with a
real prior against it: at median degree 2 the matching is nearly forced, so
better weights may have little room to act. We report the measured effect in §6
rather than assuming it.

### 4.5 Online adaptation on dense proxies

Every episode starts with empty memory, and MSMI matures 30+ days after
assignment — about one positive label per episode. A bandit that updates only on
MSMI is structurally starved, which is our explanation for the earlier Thompson
and GP results rather than a claim that bandits are inappropriate.

Directional responses are the alternative: two per introduction, visible within
seven days, roughly 120 usable observations by mid-episode. We refit the §4.3
model online by ridge-anchored IRLS towards the offline prior
($\lambda = 4$ toward $\beta_0$, minimum 40 observations, most recent 1,200
retained), so a thin in-episode sample cannot drag the model away from its
training. Non-responses are **excluded** from the update, never recoded as
rejections.

For the `drift` and `shift` families we additionally admit a single `day/60`
coefficient that is *zero in the offline prior* and estimated only in-episode.
The offline prior pools stationary and drifting families, so a day term is not
identifiable there; within one episode the family is fixed, so it is. Evidence
that there is something to detect: mutual acceptance in `drift` falls
0.263 → 0.237 → 0.164 across day blocks (<30, 30–44, ≥45) while `development`
is flat at 0.263 → 0.273 → 0.246.

Carried memory stays well inside the 1 MiB limit: a coefficient vector, a bounded
feature buffer and counters. We will verify the serialised size before Round 2
rather than assume it.

### 4.6 Audit ledger

For every proposed pair we emit the observed evidence per field (value, status,
observation day), unresolved fields, the binding constraint when a pair was
rejected, the runner-up pair and its weight, and the reduced profit
$w_{ij} - u_i - u_j$. Explanations separate three things that must not be
conflated: **model uncertainty**, **missing data** (a field that is $\varnothing$
or declined), and **stochastic outcome**. A latent simulator value is never
presented as an observation and no personal history is invented.

### 4.7 What we deliberately did not do

- **No hidden-state access at inference.** No policy reads `world['truth']`,
  reconstructs answers from generator seeds or IDs, or inspects organiser files.
- **No latent-probability oracle rung.** Our earlier plan proposed an
  "expected-outcome oracle". The simulator does not expose latent pair
  probabilities, so that rung would require reconstructing the generator's
  outcome function. We dropped it. The oracle ladder in §6.6 stops at perfect
  clarification plus maximum-cardinality allocation.
- **No inverse-propensity claims on the supplied files.** The propensity field is
  null. Doubly-robust off-policy evaluation on our *own* randomised logs is
  planned work (§8.1), not a result.
- **No Thompson-sampling-plus-value-of-information hybrid.** Not implemented; it
  would be new work, and we do not describe it as though it exists.

---

## 5. Experimental design

### 5.1 Worlds, seeds and splits

| Use | Seeds | Families | Episodes per method |
|---|---|---|---:|
| Prior fitting / model selection | 11, 13, 17, 19, 23, 29, 31, 37 (fit) and 41, 43, 47, 53, 59, 61, 67, 71, 73, 79 (holdout) | all six | 108 logged |
| Head-to-head evaluation | 101, 202, 303, 404, 505, 606, 707, 808, 909, 1010 | all six | 60 |

Training and evaluation seeds are disjoint. The static snapshot pools are used
only for the §3.3 marginals, and only the six pools that `data_manifest.json`
labels `train`; `public_07`/`public_08` (validation) and `public_09`/`public_10`
(development test) are untouched. Rows are never split by pair or person across
train and test — the split is by *world*, which is the only unit that respects
the dependence structure, since all 200 members of a pool share one generator
draw.

Every method sees the identical `(seed, variant)` worlds. Policy memory is
empty at every episode start, matching the assessment protocol.

**Randomness is fully declared.** The world generator is seeded by the simulator
from `(seed, variant)` and we never touch it. Inside the policy, every random draw
uses a fixed generator seeded only from public inputs: the shuffled feasible
matcher uses `random.Random(17 + day)` and the residual-soft ask tiebreak uses
`random.Random(917 + seed)`. There is no wall-clock, no `os.urandom` and no
unseeded `random` call anywhere in the decision path, so a rerun is bit-identical
— which is what makes the `defaultask_core4_maxw` / `fullbudget_unranked_maxw`
determinism check in §6.2 meaningful. Statistical resampling uses
`random.Random(20261009)` for bootstrap intervals, fixed independently of the
policy. Nothing in the policy reads a world seed to infer an outcome; the seed
enters only as an offset into our own shuffle, and the same offsets are used for
every configuration so that ties in §6 are ties of rule rather than of draw. All results are
in-process against the public simulator; these are **not** official subprocess or
Docker timings, and §6.7 reports the wall-clock cost so the reader can judge the
10-second limit separately.

### 5.2 Hypotheses and falsification criteria

Each hypothesis is stated with the test that would kill it. We commit to these
before reporting the head-to-head numbers.

| # | Hypothesis | Test | Falsified if |
|---|---|---|---|
| **H1** | Targeting clarification at expected matching-unlock value beats count-based potential asks and beats unranked full-budget asks, at a fixed matcher. | Paired seed-block contrast, same worlds | The 95% seed-block CI of the difference includes ≤ 0 at ≥ 10 seeds per family |
| **H2** | Any asking policy beats no clarification on coverage and MSMI. | Paired contrast against `no_ask` | CI includes 0 |
| **H3** | Adapting on dense directional responses is no worse than a static prior anywhere, and better in `drift` and `shift`. | Paired contrast overall and per family | Worse overall with a CI excluding 0, or no gain in `drift`/`shift` |
| **H4** | In supply-rich families, clearing every day beats clearing every $k$ days; in `sparse` it does not. | Batching ablation, $k \in \{2,3,5\}$ | The ordering is the same in both regimes |
| **H5** | Residual soft-field clarification does **not** improve MSMI in development, because at median degree 2 the matching is close to forced and better weights have little room to act. | Paired contrast, `unlocksoft` vs `unlock` at fixed matcher | CI excludes 0 in either direction — a real effect, either way, falsifies the near-forced reading |
| **H6** | Coverage of any valid policy converges to the §3.1 ceiling; the remaining gap is under 2 percentage points in development. | Coverage ÷ ceiling per family | A policy exceeds the computed ceiling, which would mean the ceiling is wrong |

H5 and H6 are stated as *negative* predictions on purpose. A research note whose
hypotheses can only be confirmed is not doing much, and the structural analysis
in §3 makes a falsifiable claim about what cannot be improved.

### 5.3 Baselines and ablations

The three required baselines run through the same harness on the same worlds:
supplied **greedy** (default asks + starter greedy), **no-clarification**, and
**random-feasible**. The incumbent from our own pilot, **potential-ask +
7-soft-field max-weight**, is included as a fourth reference because it is the
configuration this note has to beat or explain.

Ablations are factorial in structure, one component changed at a time:

| Ablation | Changes | Isolates |
|---|---|---|
| `unlock_greedy` vs `greedy` | ask rule only | the value of unlock-value targeting |
| `defaultask_core4_maxw` vs `greedy` | weight + allocation only | the value of signed core-4 weighting and global matching |
| `fullbudget_unranked_maxw` vs `unlock_prior_maxw` | ranking only, budget fixed | whether *which* members to ask matters once the budget is spent |
| `defaultsoft_prior_maxw` vs `unlocksoft_prior_maxw` | ranking of soft asks only | whether unlock ranking matters for soft fields too |
| `unlock_prior_online_day` vs `unlock_prior_maxw` | online adaptation | H3 |
| `no_ask` vs `greedy` | clarification entirely | H2, and the required no-clarification ablation |

### 5.4 Statistics

Outcomes are counts, so we treat the *seed block* — one seed's mean across the six
families — as the resampling unit, which preserves the within-seed correlation
across families that the official score induces by averaging them.

- **Primary score** = unweighted mean of six family means, exactly as specified.
  Denominators are never pooled across families and no best seed is ever selected.
- **95% CI** = percentile bootstrap over the ten seed blocks, 10,000 draws,
  analysis seed 20261009.
- **Paired test** = exact two-sided sign-flip permutation over the ten seed-block
  differences ($2^{10}$ arrangements, so the smallest attainable p is 0.002).
- **W/T/L** counts over all 60 paired episodes, reported alongside, because with
  ties dominant, a block-level permutation test and a per-episode count can
  disagree, and both are informative.
- **No multiplicity correction is applied.** We ran a dozen contrasts. Reported
  p-values are exploratory; a Bonferroni-adjusted threshold at 0.05/12 ≈ 0.004 is
  attainable in principle by the exact sign-flip test (smallest reachable p ≈
  0.001 at $2^{10}$ arrangements) but demanding — it requires near-unanimous
  seed-block agreement — which is itself the honest summary of how much evidence
  ten public seeds can carry.

### 5.5 Power

We measured the per-episode SD of MSMI/100 **within** each method rather than
pooling across methods, since pooling inflates it with between-method variance.
Across all 17 configurations at 60 episodes each the mean within-method SD is
**0.457** (range 0.314 for `no_ask` to 0.586 for `lab_potential_core4_maxw`); pooling every episode
gives 0.467. Our earlier internal estimate of 0.57 was too high, and
using it would have understated the power of a given design by about 35%.

With $n \approx 2\sigma^2(z_{0.975}+z_{0.80})^2/\Delta^2$ at $\sigma = 0.457$:

| Gap to detect (MSMI/100) | Episodes per arm | Equivalent seeds × 6 families |
|---:|---:|---:|
| 0.50 | 14 | 2.3 |
| 0.30 | 37 | 6.2 |
| 0.20 | 83 | 13.8 |
| 0.15 | 146 | 24.3 |
| 0.10 | 329 | 54.8 |

Four consequences we design around rather than complain about:

1. **Our design is underpowered for its own headline.** Sixty episodes per arm
   resolve a gap of about **0.234**. Only one contrast among asking
   policies that we report is that large, and it is the best-of-seventeen cell
   (§6.2a).
2. **The official assessment is barely better.** Twenty private seeds per family
   gives 120 episodes, resolving about **0.165** — comparable to the
   entire spread between the best and worst asking policies we measured (0.400 to
   0.592). With a mean of 0.86 MSMI events per episode, the private ranking of any
   one submission rests on roughly 104 events. Two competent submissions can be
   separated by noise, and the tie-break ladder (coverage, then mutual
   acceptances, then lower ask cost, then lower inference time) will decide more
   of the ranking than the primary score will.
3. **A three-seed pilot resolves about 0.43** — larger than the distance between
   the best method we tested and the starter greedy baseline. This is why we do
   not build narrative on the pilot's ordering, and why the earlier "4-phase
   hybrid" result (+1 event over its own fixed control, selected as the best of
   several screened schedules) is reported as exploratory only.
4. Episode scores are not Gaussian; they are scaled near-Poisson counts where one
   event moves the score by 0.5 and most episodes are 0, 0.5 or 1.0. The formula
   above is therefore an approximation, and we report exact sign-flip p-values and
   W/T/L counts alongside every interval rather than relying on the normal
   approximation alone.


### 5.6 Validity threats we can name

| Threat | Effect | Mitigation |
|---|---|---|
| Public seeds only | Private worlds differ; family-level behaviour may not transfer | Report per family, never only the primary score |
| Winner's curse | Screening many configurations inflates the best one | Report every configuration screened, including the losers |
| In-process timing | Not the official 10 s / 2-core / 1 GiB container limit | Report wall clock separately; container test is Round 2 work |
| Unadjusted multiplicity | p-values are optimistic | State the number of contrasts; give W/T/L as well |
| Rare events | A zero is not an equivalence result | Report counts and CIs, never only means |
| Label-cutoff bug (found in our own code) | Online learners may have trained on wrong labels | See §7.5 |

---

## 6. Results

**Scale.** 1,020 head-to-head episodes across 17 configurations, 10 public seeds
and 6 families, plus 180 oracle-ladder episodes, 108 logging episodes and 18
equivalence cases. Every episode in every run completed with valid simulator
actions: **zero invalid episodes out of 1,326**. All results are in-process
against the public simulator on public seeds — *not* official subprocess or Docker
timings.

**Replication.** Before reporting anything new we checked that our independent
harness reproduces the previously published ten-seed screen. It does, exactly:

| Cell | Published | Ours | Published events | Our events |
|---|---:|---:|---:|---:|
| default asks + starter greedy | 0.350 | 0.350 | 42 | 42 |
| no clarification + starter greedy | 0.167 | 0.167 | 20 | 20 |
| default asks + random feasible | 0.358 | 0.358 | 43 | 43 |
| default asks + 7-soft max-weight | 0.408 | 0.408 | 49 | 49 |
| potential asks + 7-soft max-weight | 0.525 | 0.525 | 63 | 63 |

Agreement to the event count on all five cells means the new rows below are
comparable to the earlier screen, and that the harness is not introducing its own
variance. §6.9 reports a stronger version of the same check against the
organisers' reference `policy.py`.

| Method | MSMI/100 | 95% seed-block CI | Events | Coverage | Ceiling | % of ceiling | Assignments | Ask cost |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| `lab_potential_core4_maxw` | **0.592** | [0.392, 0.808] | 71 | 0.343 | 0.352 | 98% | 77.1 | 197 |
| `lab_potential_maxw` | **0.525** | [0.408, 0.633] | 63 | 0.343 | 0.352 | 98% | 76.4 | 197 |
| `unlock_soft7_maxw` | **0.525** | [0.375, 0.733] | 63 | 0.342 | 0.352 | 97% | 76.1 | 195 |
| `unlock_core4_maxw` | **0.492** | [0.367, 0.650] | 59 | 0.341 | 0.352 | 97% | 77.2 | 195 |
| `defaultask_core4_maxw` | **0.483** | [0.358, 0.600] | 58 | 0.342 | 0.352 | 97% | 76.9 | 197 |
| `unlock_greedy` | **0.475** | [0.317, 0.633] | 57 | 0.343 | 0.352 | 98% | 76.2 | 195 |
| `unlocksoft_prior_maxw` | **0.417** | [0.233, 0.617] | 50 | 0.341 | 0.352 | 97% | 77.8 | 582 |
| `defaultask_soft7_maxw` | **0.408** | [0.308, 0.500] | 49 | 0.342 | 0.352 | 97% | 76.6 | 197 |
| `unlock_prior_maxw` | **0.400** | [0.250, 0.592] | 48 | 0.340 | 0.352 | 97% | 77.5 | 195 |
| `unlock_prior_online_day` | **0.400** | [0.250, 0.592] | 48 | 0.340 | 0.352 | 97% | 77.6 | 195 |
| `random_feasible` | **0.358** | [0.267, 0.458] | 43 | 0.342 | 0.352 | 97% | 76.4 | 197 |
| `greedy` | **0.350** | [0.233, 0.467] | 42 | 0.343 | 0.352 | 97% | 77.3 | 197 |
| `no_ask` | **0.167** | [0.050, 0.292] | 20 | 0.120 | 0.352 | 33% | 20.9 | 0 |

60 episodes per configuration, ten seeds × six families. Ceiling is the §3.1 structural maximum on the same worlds; `% of ceiling` is coverage divided by it, pooled across families as a summary figure — the per-family ceilings differ (§3.1), and `results/primary_summary.csv` additionally carries the per-seed coverage-to-ceiling ratios, which are the primary utilisation statistic. The four configurations omitted from this table — `fullbudget_unranked_maxw` (identical to `defaultask_core4_maxw` by construction), `lab_potential_prior_maxw`, `defaultask_prior_maxw` and `defaultsoft_prior_maxw` — are in `results/primary_summary.csv`, along with per-method median and 90th-percentile waiting times.

### 6.1 The headline is a negative result, and it is the useful one

Read down the "Assignments" column. Across the sixteen asking configurations the
total moves from 4,555 to 4,681 introductions over 60 episodes — a range of 126
against a total near 4,600. Coverage moves between 0.3399 and 0.3432. And every
one of them sits at **97–98% of the structural coverage ceiling** computed in
§3.1 — including the unmodified starter greedy baseline.

This confirms H6 and it changes what the problem is. Clarification is not a lever
that skilled targeting pulls further than unskilled targeting; it is a **step
function**. Asking at all takes coverage from 0.120 to ~0.342 and MSMI/100 from
0.167 to ~0.45. Asking *cleverly* takes it nowhere measurable, because there is
nowhere left to go: the ceiling is a property of the generated world, not of the
policy.

Only `no_ask` sits away from the ceiling, at 33% of it. Its contrast against the
starter greedy baseline is **+0.183 MSMI/100, 95% seed-block CI [+0.042, +0.325],
sign-flip p = 0.055, 22 wins / 33 ties / 5 losses**, 42 events against 20. H2 is
supported (the bootstrap CI excludes zero; the exact sign-flip p is 0.055), and
it is supported robustly: we enumerated all 136 pairwise contrasts
among the 17 configurations, and **all sixteen comparisons between an asking
policy and `no_ask` have an interval excluding zero**, from +0.183 for the
unmodified starter greedy baseline to +0.425 for our best cell.

The same enumeration is what makes the negative result precise. Among the thirteen
configurations that both ask *and* match, only three of the 78 pairwise intervals
exclude zero, and
all three are the same comparison in different cells: a **fitted-prior edge weight
loses to a hand-coded one** (`lab_potential_core4_maxw − lab_potential_prior_maxw`
+0.125, CI [+0.067, +0.192]; `lab_potential_core4_maxw − defaultask_prior_maxw`
+0.192, CI [+0.025, +0.367]; `lab_potential_core4_maxw − defaultsoft_prior_maxw`
+0.183, CI [+0.025, +0.350]). Every other contrast between two competent asking
policies straddles zero. So the study can reliably separate *asking from not
asking*, and *weight coding from fitted probability*, and it cannot reliably
separate one sensible asking policy from another — which is exactly what §5.5's
power analysis predicts and exactly what the thesis claims. The full enumeration
(136 contrasts, 29 excluding zero, each with its seed-block bootstrap interval and
sign-flip p) is persisted in `results/analysis.json` under
`all_pair_contrasts`, so this paragraph is checkable rather than asserted.

Everything else is pair quality on a fixed volume, and pair quality is bounded
twice over: by a mean-degree-2.5 matching with little room to choose, and by a
funnel in which the two largest losses — non-response and the on-time
double-Yes — are outside the policy's control.

### 6.2 The factorial

Allocation is general-graph maximum-weight matching in every cell except the two
greedy ablations noted below. Cells show MSMI/100 with total events over 60
episodes in brackets.

| Ask rule | 7-soft agreement count | Signed core-4 | Fitted logistic prior |
|---|---|---|---|
| **Default / unranked** | 0.408 (49 ev, n=60) | 0.483 (58 ev, n=60) | 0.400 (48 ev, n=60) |
| **Count-based potential (incumbent)** | 0.525 (63 ev, n=60) | 0.592 (71 ev, n=60) | 0.467 (56 ev, n=60) |
| **Unlock-value (ours)** | 0.525 (63 ev, n=60) | 0.492 (59 ev, n=60) | 0.400 (48 ev, n=60) |

Allocation is general-graph maximum-weight matching (`networkx.max_weight_matching`) in every cell. Two allocation ablations sit outside the grid: starter greedy ordering with default asks scores 0.350 (42 events) and with unlock asks 0.475 (57 events).

**Paired contrasts inside the grid** (same worlds, seed-block bootstrap, exact sign-flip):

| Contrast | Mean diff | 95% CI | p | W/T/L | Events |
|---|---:|---|---:|---:|---:|
| Global matching vs greedy ordering (soft-7 weights, default asks) | +0.058 | [-0.058, +0.167] | 0.445 | 14/40/6 | 49 vs 42 |
| Signed core-4 vs 7-soft agreement count (default asks) | +0.075 | [-0.025, +0.192] | 0.328 | 14/39/7 | 58 vs 49 |
| Fitted prior vs signed core-4 (default asks) | -0.083 | [-0.200, +0.042] | 0.266 | 7/39/14 | 48 vs 58 |
| Count-based potential asks vs default asks (soft-7) | +0.117 | [-0.017, +0.233] | 0.160 | 22/28/10 | 63 vs 49 |
| Unlock-value asks vs count-based potential asks (soft-7) | -0.000 | [-0.167, +0.200] | 1.000 | 17/26/17 | 63 vs 63 |
| Unlock-value asks vs default asks (signed core-4) | +0.008 | [-0.183, +0.192] | 1.000 | 20/25/15 | 59 vs 58 |
| Unlock-value asks vs default asks (fitted prior) | -0.000 | [-0.142, +0.150] | 1.000 | 15/32/13 | 48 vs 48 |
| Coding + matching, default asks (vs official greedy) | +0.133 | [+0.008, +0.258] | 0.102 | 20/33/7 | 58 vs 42 |
| Coding + matching, unlock asks (vs official greedy) | +0.142 | [-0.067, +0.358] | 0.281 | 23/23/14 | 59 vs 42 |
| Pre-specified: incumbent vs official greedy | +0.175 | [+0.092, +0.258] | 0.016 | 23/29/8 | 63 vs 42 |
| Value of clarification (required ablation) | +0.183 | [+0.042, +0.325] | 0.055 | 22/33/5 | 42 vs 20 |

Three readings matter more than any single cell.

**(a) The best cell is `potential asks + signed core-4`, at 0.592 (71 events).**
Against the official greedy baseline that is **+0.242 MSMI/100, CI [+0.125,
+0.383], p = 0.008, 27 wins / 27 ties / 6 losses**; against random-feasible
+0.233, CI [+0.050, +0.458], p = 0.064; against no-clarification +0.425, CI
[+0.242, +0.625], p = 0.002. It is also above the incumbent 0.525.

We state the selection problem before anyone else can: this cell is the **best of
seventeen screened configurations**, so its own p-value is not the relevant one.
Bonferroni across the twelve contrasts pre-specified in the table above puts the
adjusted threshold at 0.05/12 ≈ 0.004, and across all 136 pairwise contrasts at
0.05/136 ≈ 0.0004; p = 0.008 clears neither. With 60 episodes per arm the
design resolves about 0.234 (§5.5) and the effect is 0.242 — right at the
resolution limit. The defensible claim is: *a configuration combining
count-based potential asking with signed core-4 weighting and global matching
scored 0.592 on ten public seeds, nominally above both the official greedy
baseline and our own incumbent, and this must be re-tested on fresh seeds before
it is believed.* It is a candidate for Round 2, not a result.

**(b) The matcher improvement decomposes into two halves, neither significant
alone.** Changing only the allocation, from the starter's greedy ordering to
global maximum-weight matching at fixed 7-soft weights and fixed default asks,
gives **+0.058, CI [−0.058, +0.167], p = 0.445, 14/40/6**. Changing only the
weight coding, from a 7-field agreement count to signed core-4 scoring, gives
**+0.075, CI [−0.025, +0.192], p = 0.328, 14/39/7**. Together the two give
+0.133, CI [+0.008, +0.258], p = 0.102, 20/33/7 — measured directly as
`defaultask_core4_maxw − greedy`, and equal to the sum of the two halves to three
decimal places. The two effects are roughly additive and each is about half the
combined size, so neither can be credited on its own. The coding change is not a
model: it corrects two implementation errors — treating a *known disagreement* as
equivalent to *no information*, and allowing weights to go non-positive so the
matcher discards feasible edges whose true outcome probability is small but
strictly positive.

**(c) Ask targeting does not help, and the fitted prior actively hurts.** At a
fixed matcher, unlock-value ranking against count-based potential asking gives
−0.000 (CI [−0.167, +0.200], 17/26/17, both at 63 events); against default asking
it gives +0.117 at 7-soft weights but +0.008 at core-4 and −0.000 at the fitted
prior. **H1 is not supported.** Worse, the fitted logistic prior is *below* the
hand-coded signed rule in all three ask cells, and in the potential-ask cell the
gap has an interval excluding zero: **−0.125, CI [−0.192, −0.067], p = 0.008,
2 wins / 43 ties / 15 losses**. Given twelve pre-specified contrasts this too is not conclusive, but
the direction is consistent across all three ask rules, which is harder to
dismiss than a single cell.

We think we understand why, and the explanation is more interesting than the
number. A calibrated probability is the *theoretically correct* edge weight for
maximising expected MSMI on a single day, since the objective is linear in the
chosen edges. But maximum-weight matching with `maxcardinality=False` is
**scale-sensitive**: it trades "match more pairs" against "match better pairs",
and that trade depends on the spread of the weights, not only on their order. Our
prior maps every feasible pair into $\hat p \in [0.23, 0.56]$ — a band so narrow
that the optimiser behaves almost like maximum-cardinality matching and largely
ignores quality. The signed core-4 rule spans $[0.06, 0.98]$ and the 7-soft count
spans $[0.01, 7.01]$, so both impose a real quality/cardinality trade. That a
correctly calibrated probability underperforms a mis-scaled heuristic is
**consistent with a weight-scale mechanism** — and, if the scale story is not the
whole of it, with the stronger claim that the myopic single-day linear objective
is itself misspecified. The two explanations are separable, and we say so plainly:
rerunning the fitted prior under a monotone spread (or rank) transform that
preserves its ordering would isolate the scale effect; if the prior then recovers,
the misspecification reading weakens. That discriminating test is planned for
Round 2 (§8.1). The sequential structure (eight-day busy windows, non-repeatable
pairs, permanent retirement on success) means an edge's value is not its one-day
probability; that is the concrete argument for the look-ahead work in §8.1, and it
is a better reason to keep going than any score in this table.

### 6.3 Scenario-level results

| Method | development | sparse | cold start | delayed | shift | drift | Primary |
|---|---:|---:|---:|---:|---:|---:|---:|
| `lab_potential_core4_maxw` | 0.850 | 0.150 | 0.350 | 0.800 | 0.650 | 0.750 | **0.592** |
| `lab_potential_maxw` | 0.800 | 0.100 | 0.400 | 0.550 | 0.550 | 0.750 | **0.525** |
| `unlock_soft7_maxw` | 0.700 | 0.050 | 0.350 | 0.850 | 0.500 | 0.700 | **0.525** |
| `unlock_core4_maxw` | 0.650 | 0.100 | 0.300 | 0.650 | 0.650 | 0.600 | **0.492** |
| `defaultask_core4_maxw` | 0.550 | 0.050 | 0.600 | 0.650 | 0.450 | 0.600 | **0.483** |
| `unlock_greedy` | 0.600 | 0.050 | 0.450 | 0.550 | 0.600 | 0.600 | **0.475** |
| `unlocksoft_prior_maxw` | 0.450 | 0.050 | 0.350 | 0.700 | 0.500 | 0.450 | **0.417** |
| `defaultask_soft7_maxw` | 0.450 | 0.000 | 0.600 | 0.600 | 0.400 | 0.400 | **0.408** |
| `unlock_prior_maxw` | 0.500 | 0.050 | 0.350 | 0.550 | 0.500 | 0.450 | **0.400** |
| `unlock_prior_online_day` | 0.500 | 0.050 | 0.350 | 0.550 | 0.500 | 0.450 | **0.400** |
| `random_feasible` | 0.500 | 0.050 | 0.350 | 0.400 | 0.350 | 0.500 | **0.358** |
| `greedy` | 0.350 | 0.050 | 0.550 | 0.400 | 0.400 | 0.350 | **0.350** |
| `no_ask` | 0.300 | 0.000 | 0.000 | 0.150 | 0.250 | 0.300 | **0.167** |
| *coverage ceiling (§3.1)* | *0.399* | *0.177* | *0.341* | *0.399* | *0.399* | *0.399* | |

- **Sparse is 0.00–0.15 for every configuration.** With 23.3 usable pairs per
  world and the measured funnel, the expected value is ~0.12 (§7.1). The published
  zeros and our near-zeros are both consistent with a supply-limited family
  sampled ten times; a zero is not an equivalence result, and neither is 0.15.
- **Cold start still favours untargeted asking, and by a wide margin.**
  `defaultask_core4_maxw` and `fullbudget_unranked_maxw` reach 0.600 where
  `unlock_core4_maxw` reaches 0.300 and `unlock_prior_maxw` 0.350 — a full
  reversal of the development ordering (about 12 vs 6 events in this one family;
  exploratory). §7.3 gives a working explanation.
- **`shift` and `drift` do not reward the offline prior**, exactly as §4.5
  predicted: the prior pools stationary and non-stationary families, so its
  coefficients are a compromise that fits neither well. The online correction was
  supposed to repair this and did not (§6.5).

### 6.4 The funnel

| Method | Assigned | Both responded | Mutual accept | Date | Date ≤30d | Both on time | **MSMI** |
|---|---:|---:|---:|---:|---:|---:|---:|
| `lab_potential_core4_maxw` | 4624 | 2753 | 704 | 571 | 567 | 174 | **71** |
| `lab_potential_maxw` | 4584 | 2717 | 727 | 560 | 554 | 156 | **63** |
| `unlock_soft7_maxw` | 4566 | 2687 | 676 | 549 | 543 | 145 | **63** |
| `unlock_core4_maxw` | 4629 | 2819 | 714 | 562 | 560 | 167 | **59** |
| `defaultask_core4_maxw` | 4614 | 2698 | 688 | 534 | 529 | 138 | **58** |
| `unlock_greedy` | 4575 | 2691 | 681 | 544 | 539 | 133 | **57** |
| `unlocksoft_prior_maxw` | 4666 | 2747 | 676 | 533 | 532 | 140 | **50** |
| `defaultask_soft7_maxw` | 4594 | 2636 | 669 | 515 | 511 | 122 | **49** |
| `unlock_prior_maxw` | 4652 | 2869 | 722 | 573 | 572 | 144 | **48** |
| `unlock_prior_online_day` | 4658 | 2859 | 715 | 577 | 576 | 143 | **48** |
| `random_feasible` | 4583 | 2717 | 672 | 535 | 530 | 114 | **43** |
| `greedy` | 4641 | 2710 | 645 | 511 | 508 | 99 | **42** |
| `no_ask` | 1253 | 750 | 180 | 152 | 152 | 47 | **20** |

| Method | P(both respond) | P(mutual \| responded) | P(date \| mutual) | P(on-time both \| date) | P(MSMI \| assigned) |
|---|---:|---:|---:|---:|---:|
| `lab_potential_core4_maxw` | 0.595 | 0.256 | 0.811 | 0.305 | 0.0154 |
| `lab_potential_maxw` | 0.593 | 0.268 | 0.770 | 0.279 | 0.0137 |
| `unlock_core4_maxw` | 0.609 | 0.253 | 0.787 | 0.297 | 0.0127 |
| `defaultask_core4_maxw` | 0.585 | 0.255 | 0.776 | 0.258 | 0.0126 |
| `unlock_greedy` | 0.588 | 0.253 | 0.799 | 0.244 | 0.0125 |
| `unlocksoft_prior_maxw` | 0.589 | 0.246 | 0.788 | 0.263 | 0.0107 |
| `unlock_prior_maxw` | 0.617 | 0.252 | 0.794 | 0.251 | 0.0103 |
| `random_feasible` | 0.593 | 0.247 | 0.796 | 0.213 | 0.0094 |
| `greedy` | 0.584 | 0.238 | 0.792 | 0.194 | 0.0090 |
| `no_ask` | 0.599 | 0.240 | 0.844 | 0.309 | 0.0160 |

**Volume is identical; only conversion differs, and the conversion differences
live in the noisiest stage.** P(both respond) is 0.585–0.617 across methods and
P(date | mutual accept) is 0.75–0.80 everywhere, matching the **0.769** we measured
on the 1,162 mutual acceptances in our randomised logging set — both are constants
of the world, not policy variables. P(mutual accept | both responded) spans
0.246–0.268, a 2.2-point absolute band. P(both on time | date) spans 0.228–0.305
across the thirteen asking-and-matching configurations, on 515–577 dates; the
binomial SD of a single such rate at $p = 0.26$, $n \approx 546$ is 0.019, and the
expected range of thirteen draws with that SD is about 0.06 — close to the 0.077
observed. The spread across methods at the final stage is therefore of the same
order as sampling noise, though we do not claim it is entirely noise.

The consequence is uncomfortable and we state it plainly: **the stage that
separates the top configuration from the bottom is the one least connected to
anything a matcher controls.** We therefore do not interpret the 71-vs-42 event
gap as proof that any weighting scheme is better. We interpret it as a candidate
that has survived one screen and needs a second.

The loss structure itself is unambiguous. Averaged across the sixteen asking
configurations, 60 episodes produce **4,613** assignments, of which **2,733** get
two responses (59.2%), **690** reach mutual acceptance, **546** produce a date
(542 inside the 30-day window), **138** have both members answer the
second-meeting question on time, and **54** qualify as MSMI. Of the **4,559**
assignments that do not become an MSMI, **1,880** (41%) are lost at the response
stage, **2,043** (45%) at mutual acceptance, **144** (3%) at the date stage,
**408** (9%) at the on-time answer stage and **84** (2%) at the final both-Yes
step. The response and on-time stages are outside the policy's control; the
on-time stage is capped at $0.6^2 = 0.36$ by the 1–5 day answer delay against
the 3-day window no matter what the policy does. The mutual-acceptance stage is
where pair selection acts, and §6.6 shows that even perfect information raises
its rate only about 12% in relative terms.

### 6.5 Online adaptation changed nothing

`unlock_prior_online_day` and `unlock_prior_maxw` produced **identical MSMI counts
in all 60 episodes: 0 wins, 60 ties, 0 losses, mean difference exactly 0.000**.
This is not a null caused by the adaptation failing to run. Instrumented on a
`drift` world, the online learner harvested 118 directional observations,
performed 22 ridge-anchored refits, moved the intercept from −1.006 to +0.203 and
learned a day coefficient of **−0.319** — the right sign for `drift`, whose
measured acceptance rate falls from 0.263 before day 30 to 0.164 from day 45.

It changed nothing because **the matching is invariant to it**. Refitting moves
the intercept (irrelevant to a ranking), rescales coefficients roughly
proportionally (nearly irrelevant), and only occasionally reorders two edges whose
weights are close — and at median degree 2, reordering rarely changes which
matching is optimal. H3's "no worse anywhere" holds trivially; "better in `drift`
and `shift`" is **falsified as implemented**.

The honest reading is that online adaptation of *edge weights* is the wrong place
to spend adaptivity here. If a policy is to react to drift it has to change a
decision that weights do not control — how many pairs to propose, whether to wait,
or which members to clarify. We also record a defect we found while instrumenting
this: the offline prior targets P(mutual acceptance | both responded), base rate
0.254, while the online update fits P(directional Yes | responded), base rate
~0.55. Two different targets, which is why the intercept moves so far. It does not
affect ranking, but a Round 2 implementation must fit one target consistently.

### 6.6 Oracle ladder (analysis-only)

*The R4 and R5 rungs write disclosed answers directly into the simulator's member
records. No policy may do this and none of ours does. Per our own audit rule the
latent-pair-probability rung was dropped, because the simulator does not expose
latent pair probabilities and reconstructing its outcome function would not be a
defensible reference.*

| Rung | cold_start | development | sparse | Mean | Assignments | Coverage |
|---|---:|---:|---:|---:|---:|---:|
| R0 no clarification + greedy | 0.000 | 0.300 | 0.000 | **0.100** | 14.6 | 0.091 |
| R1 default asks + random feasible | 0.350 | 0.500 | 0.050 | **0.300** | 61.9 | 0.297 |
| R2 official greedy baseline | 0.550 | 0.350 | 0.050 | **0.317** | 62.5 | 0.298 |
| R3 our policy *with the fitted prior* (unlock asks + prior weights + global matching) | 0.250 | 0.450 | 0.050 | **0.250** | 63.2 | 0.297 |
| R4 *oracle*: free complete clarification (hard **and** soft) | 0.100 | 0.500 | 0.100 | **0.233** | 62.9 | 0.298 |
| R5 *oracle*: R4 + maximum-cardinality allocation | 0.150 | 0.450 | 0.100 | **0.233** | 63.1 | 0.298 |

180 oracle-ladder episodes over 10 seeds. R4/R5 are **analysis-only**: they write disclosed answers straight into the simulator's member records, which no policy may do and none of ours does. The latent-pair-probability rung was dropped (§4.7).

This is the most important table in the note. **From R1 (uniform random feasible
pairs) to R5 (an oracle given free, complete, instantaneous disclosure of every
non-declined hard and soft field, plus maximum-cardinality allocation), coverage
moves from 0.297 to 0.298 and assignments from 61.9 to 63.1.** The entire ladder
spans 14–19 MSMI events over 30 episodes per rung, where the Poisson SD at 16
events is 4. Only R0 — no clarification at all — is separable, at 6 events.

Perfect information does buy something measurable at the intermediate stage:
P(mutual accept | both responded) rises monotonically from 0.245 at R1 to 0.272 at
R4 and 0.275 at R5, about a 12% relative improvement on ~1,100 both-responded
pairs per rung. **It does not convert.** MSMI per assignment is 0.0097 at R1,
0.0074 at R4 and 0.0074 at R5, because the downstream stages move the other way
within their own noise.

**Two caveats on this table, because it is the one most easily misread.** First,
R3 is *not* our best configuration. The ladder was built before the factorial
completed, so R3 carries the fitted logistic prior as its edge weight — the
weight rule §6.2c shows is the weakest of the three, and the one that loses in
cold start (§6.3). R3 scoring 0.250 against R2's 0.317 is therefore a
reproduction of the §6.2c finding inside the ladder, not evidence against the
method; the configuration that scores 0.592 in §6.2 was never run on these three
families, and we do not claim it would beat R2 here. Second, the ladder covers
only `development`, `sparse` and `cold_start`, so its means are **not comparable**
to the six-family primary scores in §6.2 — it is an internal comparison across
rungs on identical worlds, and nothing else. What survives both caveats is the
R1-to-R5 comparison, which involves no weighting choice we would defend and no
family we excluded: uniform random feasible pairs versus an all-knowing oracle
move coverage by 0.001 and assignments by 1.2.

Two conclusions follow, and they are the ones we would want a reviewer to take
away:

1. **Information is not the binding constraint.** No clarification strategy,
   however well targeted, and no pair-outcome model, however well calibrated, can
   close a gap that an oracle with perfect answers does not close. This is why the
   targeting results in §6.2 are null and why we should have expected them to be.
2. **A surrogate can move while the primary does not.** Mutual acceptance — the
   first official tie-break — improves 12% from R1 to R5 while MSMI is flat.
   Optimising or reporting the surrogate without the primary would have produced a
   confident false claim. The spec's insistence that assignment, acceptance, date
   and second-meeting intention be reported separately is doing real work here.

### 6.7 Cost, waiting times and coverage accounting

| Metric | Hard-only ask rules (n=14) | Residual-soft ask rules (n=2) | `no_ask` |
|---|---:|---:|---:|
| Ask cost per episode (ceiling 720) | 196 | 598 | 0 |
| Mean first-introduction wait (days) | 6.32 | 6.15 | 3.95 |
| Median first-introduction wait, of served (days) | 3.97 | 3.64 | 0.72 |
| 90th-pct first-introduction wait, of served (days) | 16.02 | 15.90 | 13.77 |
| Unserved members of 200 | 131.6 | 131.8 | 176.0 |
| Missing feedback events per episode | 39.5 | 39.7 | 10.2 |
| Coverage | 0.342 | 0.341 | 0.120 |
| In-process seconds per episode | 6.74 | 5.83 | 6.44 |

Waiting times are computed over **served** members only, as the definition of a first-introduction wait requires; unserved members are reported separately two rows below and stay in every coverage denominator. Each cell is the mean over that group's 60 episodes of a per-episode statistic. Per-method values are in `results/primary_summary.csv`.

Ask spend is ~195–197 units per episode for every hard-only rule and ~582–614 for
rules that convert the residual into soft-field answers — against a 720-unit
ceiling. **The budget is not binding and never was.** With 31.9% of development
members permanently decline-blocked and 36.4% already complete at arrival, the
askable population runs out long before the units do; §6.8 shows what happens when
the residual is spent anyway. Any narrative about "spending the clarification
budget wisely" should be replaced by one about whether the residual can buy
anything at all.

Waiting times are reported with the unserved count, as the spec requires, and
members who can never be served stay in the denominator. `no_ask` has the shortest
mean wait (3.95 days) precisely because it serves so few: it introduces the
members who happen to be pre-disclosed and leaves about 176 of 200 unserved. A low
waiting time is not a good outcome when it is bought with a 12% coverage.

### 6.8 Where the residual budget goes

| Contrast | Mean diff | 95% CI | p | W/T/L | Events | Ask cost A vs B |
|---|---:|---|---:|---:|---:|
| Residual soft asks vs hard-only (unlock ranking fixed) | +0.017 | [-0.083, +0.158] | 0.961 | 9/41/10 | 50 vs 48 | 582 vs 195 |
| Unlock-ranked soft asks vs member-order soft asks | +0.008 | [-0.200, +0.208] | 1.000 | 17/28/15 | 50 vs 49 | 582 vs 614 |
| Online dense-proxy adaptation vs static prior | +0.000 | [+0.000, +0.000] | 1.000 | 0/60/0 | 48 vs 48 | 195 vs 195 |

Spending the residual ~390 units on soft-field answers raises realised ask cost
from 195 to 582 and changes MSMI/100 by **+0.017, CI [−0.083, +0.158], p = 0.961,
9 wins / 41 ties / 10 losses** — two events across 60 episodes. Ranking those soft
asks by unlock value rather than taking them in member order changes nothing
(+0.008, p = 1.000, 17/28/15).

**H5 is not rejected** (the interval is consistent with the near-forced reading
but too wide to establish equivalence), and the oracle ladder in §6.6 explains
it: soft answers
improve $w_{ij}$, and R4 shows that even *perfect* soft answers improve the
mutual-acceptance rate by only ~12% and the primary score not at all. At median
degree 2 the maximum-weight matching is close to forced, so knowing the weights
more precisely rarely changes which pairs are selected. The information is real
and the decision it would inform does not exist.

We regard this as the most transferable result in the note for anyone building on
this kit: **before designing a clarification policy, measure the degree
distribution of the graph it is meant to improve.** If the matching is forced,
information has no leverage, and the budget should be spent elsewhere or not at
all.

**Where the ask budget actually goes.** Every configuration spends about 195 of
its 720 budget units (§6.7), which reads like under-spending until you measure
the askable population directly. The probe below runs each ask rule and records,
at eight days, how many of the 200 members have a complete and never-declined hard
bundle and how many feasible edges are live between members who are still free.

Members with a complete, never-declined hard bundle (of 200), and live feasible edges between still-free members, averaged over 5 seeds:

| Family | Ask rule | d0 | d5 | d10 | d15 | d20 | d30 | d45 | d59 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| development | no_ask · members | 50 | 58 | 63 | 68 | 75 | 75 | 75 | 75 |
| development | default_asks · members | 54 | 82 | 107 | 128 | 140 | 140 | 140 | 140 |
| development | fullbudget_unranked · members | 54 | 82 | 107 | 128 | 140 | 140 | 140 | 140 |
| development | potential_ask_count · members | 54 | 82 | 107 | 128 | 140 | 140 | 140 | 140 |
| development | unlock_value · members | 54 | 82 | 107 | 127 | 139 | 140 | 140 | 140 |
| development | unlock_value_plus_soft · members | 54 | 82 | 107 | 127 | 139 | 140 | 140 | 140 |
| sparse | no_ask · members | 49 | 54 | 61 | 67 | 74 | 74 | 74 | 74 |
| sparse | default_asks · members | 53 | 78 | 105 | 121 | 132 | 132 | 132 | 132 |
| sparse | fullbudget_unranked · members | 53 | 78 | 105 | 121 | 132 | 132 | 132 | 132 |
| sparse | potential_ask_count · members | 53 | 78 | 105 | 120 | 132 | 132 | 132 | 132 |
| sparse | unlock_value · members | 53 | 78 | 105 | 119 | 130 | 130 | 130 | 130 |
| sparse | unlock_value_plus_soft · members | 53 | 78 | 105 | 119 | 130 | 130 | 130 | 130 |
| development | no_ask · live edges | 11 | 1 | 0 | 1 | 0 | 0 | 2 | 0 |
| development | unlock_value · live edges | 15 | 4 | 4 | 2 | 5 | 1 | 1 | 2 |

All five ranked ask rules are within one member of each other at every day after day 10 in both families; live-edge counts for the other ranked rules are in `results/ask_timing.json`.

Three things follow. **(i)** Asking is *saturated, not rationed*: every ranked
rule reaches the same 140-member plateau, and reaches it by day 15–20, leaving
40 days of budget with nobody left to ask. The 60 members who never complete a
bundle are the decline-blocked and the never-arrived-observable, and no ordering
of asks recovers them. **(ii)** `no_ask` plateaus at 75, so clarification does
move the usable graph from 75 to 140 members — which is exactly the H2 effect and
exactly why it is a step function rather than a gradient. **(iii)** Live feasible
edges collapse to single digits by day 10 under every rule, including the best
ones. The binding constraint is not the ask budget, not the ranking of asks, and
not the matcher; it is that the feasible graph is consumed faster than it is
replenished. This is the mechanism behind H6 and it is the reason §8.1 prioritises
*waiting and batching* — the only lever that acts on the timing of consumption
rather than on the quality of a decision made at a moment when there is almost
nothing to decide between.

### 6.9 Reproducibility of the supplied baselines

Because our harness runs in-process rather than through the official subprocess
protocol, we verified it against the organisers' reference `policy.py`
decision-for-decision: same world, same days, comparing every ask list and every
pair batch, then the final metrics.

| Reference mode (`policy.py`) | Our in-process method | Cases | Identical ask lists, pair batches and final metrics |
|---|---|---:|---|
| `greedy` | `greedy` | 6 | **all identical** |
| `no_asks` | `no_ask` | 6 | **all identical** |
| `random` | `random_feasible` | 6 | **all identical** |

Cases cover seeds 101–606 across all six families, 60 days each, comparing every ask list and every pair batch day by day. Overall: **all baselines reproduce the reference exactly**.

---

## 7. Failure analysis

The spec requires explaining failures involving sparse supply, withheld answers,
delayed feedback and competition for the same candidate, and requires that
members with no feasible candidate stay in the coverage denominator rather than
being quietly dropped. We take that further: for each failure mode we say what we
measured, what we can fix, and what is irreducible.

### 7.1 Sparse geography — supply, not policy

Every method we and others have run scores near zero in `sparse`. §3.1 explains
why, and the explanation is not a policy defect. Twelve opaque zones with
single-zone acceptance put **67.0%** of members at degree zero and leave **23.3**
usable pairs in a 200-member pool. At the measured funnel rates (0.5932 both
respond, 0.2538 mutual, 0.7685 date, 0.0907 MSMI|date), consuming *every one* of
those pairs yields 0.24 expected MSMI events per episode — **0.122 per 100 arrived
members**, against **0.619** for a development world at full utilisation. No
policy can score meaningfully in `sparse`; the family is a floor on the primary
score, not a test of skill.

Sparse is one sixth of the primary score, so it caps the attainable total.
Combining the edge-supply figures with the measured funnel gives an arithmetic
bound on the primary score at different levels of pair-selection quality
(`results/attainable_ceiling.json`):

| Pair-selection quality | P(mutual \| both resp.) | MSMI / assignment | dev | sparse | cold | **Primary bound** |
|---|---:|---:|---:|---:|---:|---:|
| Randomised-logging quality (measured) | 0.2538 | 0.0105 | 0.619 | 0.122 | 0.475 | **0.512** |
| Incumbent published quality | 0.300 | 0.0124 | 0.732 | 0.145 | 0.562 | 0.606 |
| Strong selection: the three relevant fields agree | 0.400 | 0.0165 | 0.976 | 0.193 | 0.749 | 0.808 |
| Best-case selection | 0.500 | 0.0207 | 1.220 | 0.241 | 0.937 | 1.009 |

This is a **bound, not a forecast**: it assumes every one of the 118 / 90.6 / 23.3
effective edges is consumed, ignoring arrival and exit timing, the eight-day busy
window, permanent retirement after a mutual second-meeting Yes, and the fact that
a mean-degree-2.5 matching cannot always take its preferred pairs. Our randomised
logging policy in fact consumed 71% of the edge supply in development, `shift` and
`drift`, 68% in `delayed`, 79% in cold start and **87% in sparse**, and scored
0.375 overall against the 0.512 bound. So the honest reading is that the
*achievable* primary score sits somewhere between roughly 0.5 and 0.8, and that
the published incumbent at 0.525 — and our best screened cell at 0.592 — are both
already inside that band. Any claim of a large multiple over the incumbent
should be treated with suspicion until the bound is beaten, not merely approached.
This is the single most useful number in this note for anyone tempted to
over-claim.

What is *not* irreducible: our logging policy consumes ~20 of the 23 available
sparse pairs, so the volume lever is nearly exhausted, but pair quality is not —
sparse worlds still contain goal- and pace-agreeing pairs and a matcher that finds
them may improve the mutual-acceptance rate on the same volume, although the
oracle ladder (§6.6) suggests perfect information raises it only about 12% in
relative terms. The
correct sparse strategy is therefore **selective, not expansive**: with 23 pairs
and 200 members, spending clarification to reveal *all* of them is less valuable
than revealing the *good* ones early, because members exit and the pool thins.
We flag one honest caveat: there are only three distinct sparse worlds among the
ten public seeds' generator draws, so per-family sparse estimates carry very
little independent information.

### 7.2 Withheld answers — a permanently excluded third of the pool

A declined hard field is absorbing. **31.9%** of development members and
**41.0%** of cold-start members can never appear in a feasible pair. Three
consequences:

1. **Coverage must be reported against the ceiling, not against 1.0.** Our
   measured coverage divided by the §3.1 ceiling is the honest utilisation
   statistic. Our best configuration reaches coverage **0.465** on development
   seed 101, which is not "46.5% of members served" but *every one of the 46.5%
   of that world's members who can ever be served* — the per-seed ceiling there is
   0.465. Across the ten development worlds the ceiling ranges 0.370–0.470 and
   averages 0.399, so a coverage number is uninterpretable without the seed's
   ceiling beside it.
2. **Clarification budget spent on decline-blocked members is destroyed.** Every
   ask rule we test filters them out first. This is cheap and no supplied
   baseline documents how much pool it removes.
3. **Missingness may be informative about *availability*, not preference.** Since
   the decline draw is independent of the latent outcome in this generator, we
   found no evidence that declined members would have been better or worse
   matches. We verified the analogous question for soft fields and found the
   opposite of what a naive model assumes: acceptance is *lower* when more soft
   fields are observed (0.2724 → 0.2317). Any model that encodes observability as
   a feature will learn a spurious preference. This is a missing-not-at-random
   *artefact* rather than genuine MNAR structure, and the distinction matters:
   the fix is to exclude the indicator, not to re-weight by it.

### 7.3 Cold start — where our own ask rule loses

Cold start is the one family where targeted clarification *underperforms* the
untargeted default, and it did so in both our three-seed pilot and the ten-seed
scaled run. The following is our working explanation; it is untested, and the
shrinkage rule in §8.1 is its test:

- Only **20.6%** of cold-start members have their hard bundle pre-observed,
  against 36.4% elsewhere, so 79% of the pool is askable and the queue is long.
- **41.0%** are decline-blocked, the highest of any family, so the askable set is
  both larger and more hazardous.
- Soft-field observation is ~34%, so the weights $w_{ij}$ that drive our ranking
  $V_i = \frac{1}{3}\sum_j \pi_{ij}\max(0, w_{ij}-u_j)$ are computed from
  mostly-empty inputs. When $w_{ij}$ is near its intercept for every candidate,
  the ranking degenerates to $\sum_j \pi_{ij}$ — but with more noise attached,
  and with the same-zone prefilter interacting badly with a pool where fewer
  zone answers are known.

This is not a hypothesis we pre-registered — H1 predicted that targeted asking
would win everywhere, and cold start is where it fails hardest, in the reverse
direction. We report it as the sharpest falsification of H1 in the study: the
advantage of a value-ranked ask rule depends on having enough observed soft
signal to rank with, and cold start is precisely the family that removes it. The fix is a **shrinkage rule** — as the fraction of
observed soft fields falls, blend $V_i$ towards the count-based
$\sum_j \pi_{ij}$ and eventually towards uniform ordering. We list this as
planned work with a named test (does the cold-start reversal disappear under
shrinkage?) rather than claiming it.

### 7.4 Delayed feedback and the follow-up window

In `delayed`, the date offset can reach 33 days against the 30-day MSMI window,
so some introductions that produce a date and two timely Yes answers still fail
the outcome definition. Our label helper now checks
`date_day − assigned_day ≤ 30` explicitly and we count the two failure routes
separately (`date_in_window` vs `second_on_time` in the funnel table), so a loss
is attributed to the right cause.

Right-censoring is handled by construction: labels are harvested only after the
40-day follow-up, and an introduction that has not matured returns `None` and is
excluded from learning rather than coded 0. At the decision horizon, recent
introductions are genuinely unresolved and we do not treat them as failures.

The operational consequence is the one that hurts: **feedback arrives too late to
help the episode that earned it.** An introduction made on day 40 has its MSMI
label after day 70, past the decision horizon. Only the 7-day directional
response is available inside the episode in useful quantity, which is the whole
argument for §4.5.

### 7.5 An internal audit: the label-cutoff bug

Our earlier lab helper `mature_primary_label` labelled "a date plus two timely
second-meeting Yes answers" as an MSMI positive **without checking that the date
occurred within 30 days of assignment**. We found one instance in an audited
sample (delayed family, seed 303: assigned day 31, date day 62). The simulator's
own scoring was always correct, so no reported *score* was affected; the bug
could only corrupt **online learning updates**.

Consequences we accept rather than minimise:

- Every learning-based row from the three-seed pilot (Thompson 0.472, GP-UCB
  0.389, GP-mean 0.222) is **provisional** and is not cited as a result here.
- The corrected label is used for all fitting in §4.3 and all results in §6.
- The audit sample was small, so other seeds may have been affected; we did not
  re-run the old learners, we replaced them.

We report this because the spec asks for honest limitations and because a
documented internal audit is more useful to a reviewer than a silently corrected
table.

### 7.6 Competition for the same candidate

With mean degree 2.53 and median degree 2, competition is the norm rather than
the exception: a max-weight matching resolves it globally, whereas the starter
greedy resolves it by sort order and can consume a member on a mediocre edge
before a better one is considered. Two dynamic forms of competition remain
unhandled and are named here rather than solved:

- **Temporal competition.** Introducing $i$–$j$ today makes both busy for eight
  days and consumes the pair permanently. If $i$ has a materially better partner
  who is currently busy or not yet arrived, waiting dominates. We do not yet
  estimate arrival rates in-episode or compare a waiting rule against daily
  clearing (H4).
- **Success consumes supply.** A mutual second-meeting Yes retires both members
  permanently. Maximising MSMI therefore spends the scarcest resource in the
  system, and in a supply-limited family the optimal policy may be more selective
  than the single-day linear objective implies. Quantifying this needs a
  two-stage look-ahead we have not implemented.

### 7.7 Members who can never be served

They stay in the denominator, as required, and the two exclusion mechanisms must
not be added together. Measured across the ten public worlds:

| Family | Never introducible | ...of which: ≥1 declined hard field | ...of which: no feasible partner even under complete disclosure | Overlap |
|---|---:|---:|---:|---:|
| development | **60.2%** | 31.9% | 33.9% | 5.6 pp |
| cold start | **66.0%** | 41.0% | 32.1% | 7.1 pp |
| sparse | **82.3%** | 32.8% | 67.0% | 17.5 pp |

The two columns are measured on different graphs — the decline count uses the
observed questionnaire, the isolation count assumes full disclosure — so they
overlap rather than nest, and only their union bounds what is achievable. In
`sparse` the union is 82.3%, which is the whole of §7.1 in one number.

The unserved count and the first-introduction waiting-time distribution (mean,
median and 90th percentile, over served members) are reported by group in §6.7
and per method in `results/primary_summary.csv`, so a reviewer can see the
waiting-time cost of selectivity rather than only the success rate.

---

## 8. Round 2 plan, disclosure and references

### 8.1 What is done, what is planned

| Item | Status |
|---|---|
| Structural diagnosis: coverage ceilings, edge supply, binding-constraint histogram | **Done** (analysis-only) |
| Empirical hard-constraint pass-probability prior from the six supplied training pools | **Done** |
| Self-logged randomised rollouts, 108 episodes, 7,613 labelled introductions | **Done** |
| Restricted pair-outcome prior with held-out model selection and a missingness-confound diagnosis | **Done** |
| Unlock-value clarification rule with reduced-profit approximation | **Done** |
| Residual-budget soft-field clarification rule | **Done** |
| Online ridge-anchored adaptation on directional responses, with an in-episode day term | **Done and falsified** — bit-identical decisions to its own static version in all 60 episodes (§6.5); kept in the harness as an instrumented null |
| Head-to-head on 10 public seeds × 6 families vs the three required baselines | **Done**, §6 |
| Funnel decomposition and per-family scenario reporting | **Done**, §6 |
| Oracle ladder up to perfect clarification + maximum-cardinality allocation | **Done**, §6.6 (analysis-only) |
| Cold-start shrinkage rule for the ask ranking (§7.3) | **Planned** |
| Waiting/batching ablation, $k \in \{2,3,5\}$, and in-episode arrival-rate estimation (H4) | **Planned** |
| Exact blossom duals for the reduced-profit term instead of the realised-matching approximation | **Planned** |
| Doubly-robust off-policy evaluation on our own randomised logs, with recorded propensities | **Planned** |
| Two-stage look-ahead for temporal competition and success-consumes-supply (§7.6) | **Planned** |
| JSON stdin/stdout policy adapter, Dockerfile, container-mode timing under 2 cores / 1 GiB / 10 s | **Planned** |
| 20-seed public runs and a serialised-memory size check against the 1 MiB cap | **Planned** |
| Latent-probability oracle rung | **Dropped** (§4.7) |

### 8.2 Round 2 build order

1. Wrap the winning configuration in the JSON protocol, keeping the starter
   argument parser, stdout reserved for protocol JSON and diagnostics on stderr.
   Handle an empty population and an empty feasible graph explicitly.
2. Ship `hard_priors.json` and `outcome_prior.json` as declared inference assets;
   confirm total image size and serialised memory against the 2 GiB and 1 MiB
   caps.
3. Containerise and measure. The measured in-process cost per episode-day is
   small, but the O(n²) eligibility pass is the term to watch: 200 members means
   ~20k pair checks per phase, and the 10-second limit includes process startup.
   The same-zone and age-gap prefilters in §4.2 exist for exactly this reason.
4. Run the cold-start shrinkage rule and the batching ablation; keep whichever
   survives a paired test at ≥ 20 seeds.
5. Publish per-episode machine-readable results for all four required
   comparisons on identical seeds and variants, plus the funnel and waiting-time
   tables, and pin an immutable archive with its SHA-256.

### 8.3 AI tools disclosure

This note and the accompanying code were produced with the assistance of
large-language-model coding agents, used for: reading and summarising the
starter kit and its documentation; drafting and debugging the experiment
harness, the policy implementations and the analysis scripts; and drafting and
critically revising this document. Separate chat-assistant sessions
(Claude- and Gemini-family models, via Arena.ai Agent Mode and other tools)
additionally contributed ideation, cross-checking of the draft against its own
tables, and pre-submission review; every such suggestion was accepted only
after arithmetic or artefact cross-check, and the final decisions rest with the
team. All experimental numbers reported here were
produced by executing the committed Python code against the organisers' public
simulator release 1.0.0 on public seeds, and every table is reproducible from
the scripts named in §9. No model was used to generate results, and no result was
accepted into this note without a corresponding artefact on disk. One
model-assisted implementation contained the label-cutoff defect described in
§7.5; it was found by human-directed audit of the code against §8 of the problem
statement, not by the model. Where an earlier AI-generated draft contained claims
contradicted by our own audit — bipartite/Hungarian allocation, zone adjacency,
"one introduction per person per day", regret curves, exact value of information,
a Thompson-plus-VOI hybrid — those claims are removed here and are not asserted
anywhere in this note.

### 8.4 Synthetic-data disclaimer

All members, profiles, preferences, conversations, introductions and outcomes are
newly generated or authored synthetic content. Demographic proportions and
outcome behaviour are invented assumptions, not fitted or validated distributions
of real people. Simulator performance is an engineering and research test; it is
not evidence that any model can predict a relationship, and nothing here should
be presented as product effectiveness.

**What these invented outcomes cannot establish.** Four things specifically. They
cannot establish that any feature we weighted — `relationship_goal`, pace,
conversation style — predicts real romantic compatibility; the generator decided
that, and we recovered the generator's decision, not the world's. They cannot
establish that a higher MSMI score is a better product outcome, since MSMI is a
synthetic proxy whose own funnel (§6.4) is dominated by invented response and
punctuality rates. They cannot establish that clarification is acceptable to real
people, since a simulated member never experiences being asked an intimate
question, never declines for reasons of safety, and never objects to the timing.
And they cannot establish anything about fairness or disparate impact: the
generator draws acceptance uniformly and independently of demographics, so our
runs contain no bias to detect, and the absence of a measured disparity here is
not evidence of the absence of one in production.

**The adapter and validation that real use would require.** Concretely, in the
order it would have to be built: (1) a schema adapter mapping a live profile
store onto the contract's fields, with an explicit, audited rule for what a
missing answer means — the three-valued feasibility of §2.2 has to be re-derived
against real data-entry behaviour, not assumed; (2) a consent and disclosure layer
in front of every clarification ask, with per-question withdrawal, since
`declined` is absorbing here and in production it must also be *respectful*;
(3) real eligibility checks against current, verified attributes rather than
self-reported ones, with a human review path for anything that excludes a person;
(4) outcome labels from actual, consented follow-up rather than a simulated draw,
which would take months and would immediately face the censoring problem §2.4
describes — mutual interest removes both people from the pool, so the pairs that
succeed stop being observable; (5) prospective validation with a randomised or
staggered rollout against a real allocation baseline, powered on the event rate
that actually occurs, not on §5.5's synthetic one; and (6) a fairness audit across
protected attributes, which requires data this simulator structurally cannot
supply. None of that is started. The method in this note is portable — the
three-valued feasibility algebra, the supply diagnosis, the matching formulation
and the seed-block statistics all transfer — but every number in §6 is a property
of a generator we did not write.

### 8.5 References

All works below were checked against their publishers' records on 9 October
2026; volume, issue and page numbers are as printed there, so the `[verify]`
markers that appeared in earlier drafts of this note are removed. We have not
fabricated a citation to fill a gap, and we cite nothing we have not located.

- **Akbarpour, M., Li, S., & Oveis Gharan, S. (2020).** "Thickness and
  Information in Dynamic Matching Markets." *Journal of Political Economy*,
  128(3), 783–815. DOI 10.1086/704761. (Earlier circulated as "Dynamic Matching
  Market Design.") The paper's central result is that a *Patient* algorithm that
  waits to thicken the market loses exponentially less than *Greedy* — but **only
  when the planner can identify agents who are about to depart**; when departure
  times are not observable, Greedy is close to optimal. That precondition is
  precisely the empirical question our §6.8 probe answers for this simulator:
  feasible edges here vanish because members are consumed by an introduction,
  retire permanently after a mutual second-meeting Yes, or age out at day 60, and
  the first two are visible in the observation contract. H4 (waiting/batching) is
  therefore not a speculative add-on but the one lever the theory says could still
  be large, and §8.2 schedules it as the fourth step of the Round 2 build order.
- **Edmonds, J. (1965).** "Paths, Trees, and Flowers." *Canadian Journal of
  Mathematics*, 17(3), 449–467. DOI 10.4153/CJM-1965-045-4. The blossom algorithm
  — the correct general-graph maximum-matching primitive for a pool that is not
  bipartite, and the reason §4.1 uses `networkx.max_weight_matching` rather than a
  Hungarian assignment.
- **Dudík, M., Langford, J., & Li, L. (2011).** "Doubly Robust Policy Evaluation
  and Learning." *Proceedings of the 28th International Conference on Machine
  Learning (ICML '11)*, 1097–1104. The estimator we plan to apply to our own
  randomised logging rollouts, where the logging propensities are known by
  construction (§8.1, planned).
- **Russo, D., Van Roy, B., Kazerouni, A., Osband, I., & Wen, Z. (2018).** "A
  Tutorial on Thompson Sampling." *Foundations and Trends in Machine Learning*,
  11(1). Background for the label-starvation argument in §4.5: with a mean of
  about 0.9
  MSMI events per episode, a posterior over pair outcomes cannot be updated often
  enough to matter inside a 60-day episode, which is why we adapt on directional
  responses instead.
- **Hitsch, G. J., Hortaçsu, A., & Ariely, D. (2010).** "Matching and Sorting in
  Online Dating." *American Economic Review*, 100(1), 130–163. DOI
  10.1257/aer.100.1.130. Motivation for treating introductions as a two-sided
  *allocation* problem with competition for the same candidates (§7.6) rather than
  as an independent pair-ranking problem.
- **Karp, R. M., Vazirani, U. V., & Vazirani, V. V. (1990).** "An Optimal
  Algorithm for On-line Bipartite Matching." *Proceedings of STOC '90*, 352–358.
  DOI 10.1145/100216.100262. Foundational online-matching background; its
  bipartite one-sided-arrival model and guarantees do not transfer to this
  simulator's general-graph, reciprocal-feasibility setting, and we do not imply
  that they do.
- **Gamlath, B., Kapralov, M., Maggiori, A., Svensson, O., & Wajc, D. (2019).**
  "Online Matching with General Arrivals." *Proceedings of FOCS 2019*, 26–37.
  DOI 10.1109/FOCS.2019.00011. The closest model-family reference for general
  arrivals; our daily batch decisions and clarification actions still make the
  setting distinct.
- **Saar-Tsechansky, M., Melville, P., & Provost, F. (2009).** "Active
  Feature-Value Acquisition." *Management Science*, 55(4), 664–684. DOI
  10.1287/mnsc.1080.0952. Cost-aware information-acquisition context for the
  clarification problem; an analogy for budgeted questioning, not a direct
  matching algorithm.
- **Vouchsafe / Romeo & Juliet (2026).** *The One Introduction Problem — final
  participant specification 1.0.0*, with the bundled `docs/DATA_CONTRACT.md`,
  `docs/POLICY_INTERFACE.md` and `docs/SUBMISSION.md`. Authoritative for every rule
  quoted in this note; where an earlier draft of our own work conflicted with it,
  the specification won and the draft was corrected (§8.3).

### 8.6 Data and software provenance

- Simulator and data: organisers' public synthetic release 1.0.0; the bundled
  `starter/kit.py` is unchanged and records upstream commit
  `a8e26b35118cfa8e886a02f93984923e43ab64f6` (`starter/SOURCE.md`,
  `starter/LICENSE`, `starter/DATA_LICENSE.md`). Every member and outcome is
  synthetic (§8.4). No private seeds, private worlds, private organiser files or
  real-user data were used; the only external data are the six supplied training
  pools used for the §3.3 marginals.
- Experiment code carries no separate top-level license; the scripts are those
  named in §9. The three official baselines were additionally re-verified
  through the organisers' reference evaluator in trusted-local subprocess mode
  (54/54 episodes identical; `research/VERIFICATION_2026_10_09.md`).
- The three-seed soft-question screen (72 episodes) and the seven-seed follow-up
  (42 episodes) were run on the author's Ubuntu VM. The shared bundle contains
  the aggregate soft-question results but not the VM-generated row-level JSON;
  this is documented in `research/PROVENANCE_AND_ARTIFACT_STATUS.md`.

### 8.7 Computational environment and reproducibility

- All core factorial, head-to-head and oracle-ladder episodes ran in-process;
  the exact execution host of those runs is not recorded in this bundle and no
  hardware specification is claimed for them. Wall times in §6.7 are in-process
  seconds per episode, not official per-invocation or Docker timings. No
  Docker/container-mode validation has been performed (Round 2 work, §8.2).
- Dependencies are pinned in `requirements.txt`; the starter kit is standard
  library only. The working environment for the §9 scripts is recorded in §9
  (Python 3.13 on the author's machine); no VM hardware details are claimed.
- Reproducibility anchors: every policy random draw is seeded from public inputs
  only (§5.1); bootstrap intervals use analysis seed 20261009; reruns are
  bit-identical by construction.

---

## 9. Reproduction

```
scripts/diagnose_structure.py    # §3.1, §3.2 binding constraints (analysis-only)
scripts/diagnose_supply.py       # §3.1 coverage ceilings and edge supply (analysis-only)
scripts/estimate_priors.py       # §3.3 hard-constraint marginals from training pools
scripts/log_rollouts.py          # §4.3 randomised logging rollouts, training seeds
scripts/fit_outcome_model.py     # staged fits, independence check, calibration
scripts/fit_variant_models.py    # per-family coefficients, missingness confound
scripts/fit_prior.py             # §4.3 specification search and shipped asset
scripts/harness.py               # runner, labels, bootstrap CI, sign-flip test
scripts/policies.py              # all candidate policies
scripts/compare.py               # §6 head-to-head, sharded
scripts/oracle.py                # §6.6 oracle ladder (analysis-only)
scripts/ask_timing.py            # §6.8 askable-population saturation probe
scripts/attainable_ceiling.py    # §7.1 arithmetic bound on the primary score
scripts/test_baseline_equivalence.py  # §6.9 action-for-action check vs starter/policy.py
scripts/analyse.py               # every table in §6 -> results/analysis.json + CSVs
build_note.py                    # substitutes results into RESEARCH_NOTE_FINAL.md
make_pdf.py                      # Markdown -> RESEARCH_NOTE.pdf (WeasyPrint)
```

Outputs land in `results/`: `structure_diagnosis.json`, `supply_bounds.json`,
`logging_rollouts.json` shards, `outcome_model.json`, `variant_models.json`,
`prior_specification.json`, `main_shard*.json`, `oracle_shard*.json`,
`analysis.json`, and the CSV/Markdown exports. Inference assets are
`assets/hard_priors.json` and `assets/outcome_prior.json`.

Dependencies: Python 3.13, `numpy`, `networkx`, `scikit-learn` (offline fitting
only — no model artefact requires it at inference time), plus `markdown` and
`weasyprint` to render this PDF. The starter kit itself is standard-library only
and is used unmodified.
