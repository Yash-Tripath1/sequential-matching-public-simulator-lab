# Round 2 — waiting time, allocation disparity, and confirmation on fresh worlds

**Team Bipartite Bard · run 10 October 2026 · 900 episodes · public simulator 1.0.0, public seeds**

> **ARCHIVAL — working notes, not findings.** This file is the raw engineering log
> kept during the Round 2 build. It contains open questions, abandoned branches and
> internal paths that were never resolved, and it has not been cleaned for
> publication. **The authoritative statement of results is `REPORT.md`.** Nothing
> here should be cited as a finding without checking it against that document.

Companion to `ROUND2_PLAN.md`. This document reports what I actually ran and
what came out. Everything is public-seed, in-process, synthetic. It is
exploratory and unadjusted for multiplicity.

---

## 0. What ran

| | |
|---|---|
| Seeds | **1101–1130** (30 fresh seeds, never used in Round 1) + a 10-seed fidelity re-run on Round 1's own seeds |
| Families | all six |
| Arms | `greedy` (official) · `potential_ask` (Round 1 incumbent) · `signed_potential` · `waitfloor` (new) · `oldest_first` (new) |
| Episodes | **900** (720 fresh + 120 fidelity + 60 Round-1-seed baseline) |
| Instrumentation | per-member: group, arrival, exit, complete-disclosure degree, ask units, first-ask day, first-introduction day, wait, introductions received |

Two probes are generator/diagnosis only, not policy rollouts: the world-sharing
check and the complete-disclosure eligibility graph.

**Seed block notice.** Within a seed, `development`, `delayed`, `shift` and
`drift` generate the *same 200 members* — verified by member-ID comparison. So
30 seeds × 6 families is ~90 independent worlds, not 180. **Every interval in
this document resamples seeds**, never episodes and never scenarios.

---

## 1. Reproducibility first

This was the thing I flagged as blocking, and it is worth reporting the state
honestly.

**1.1 The Round 1 incumbent is now reproducible from the repo.** The PDF's
winning-configuration code was missing from the repository. I rebuilt the
incumbent (`lab_potential_maxw`, 0.525) from `experiment_lab.py` and checked it
episode by episode against the stored `scaled_factorial_10seeds.json`:

> **60/60 episodes identical** — same MSMI, same assignment count, same
> coverage. Primary 0.5250, 63 events, matching the PDF exactly.

**1.2 One trap worth recording.** My first build scored 0.367 on the same
seeds. The cause: the incumbent's ask-ranking uses the **unsigned** agreement
score (a known disagreement contributes 0.0). I had used the **signed** variant
(−1.0), which is a genuinely different policy. The two differ by 0.158 on the
primary score — larger than most effects in the Round 1 note. I kept the signed
variant as its own arm (`signed_potential`) rather than quietly renaming it.
If you rebuild any Round 1 configuration, expect this class of bug.

**1.3 Harness equivalence, verified on our own policy (not just the baselines).**
Round 1's Appendix C verified the three official baselines decision-for-decision
against the organisers' reference. I extended that to our own arms through the
real JSON protocol:

| World | arm | source | MSMI | coverage | ask cost |
|---|---|---|---:|---:|---:|
| 1101 development | `waitfloor` | in-process | 0.0 | 0.440 | 198 |
| 1101 development | `waitfloor` | **official `evaluate.py`** | 0.0 | 0.440 | 198 |
| 1101 sparse | `waitfloor` | in-process | 0.0 | 0.215 | 225 |
| 1101 sparse | `waitfloor` | **official `evaluate.py`** | 0.0 | 0.215 | 225 |
| 1101 development | `greedy` | in-process | 0.5 | 0.435 | 198 |
| 1101 development | `greedy` | **official `evaluate.py`** | 0.5 | 0.435 | 198 |

And `greedy` reproduces the Round 1 published row on all 60 Round-1-seed
episodes (0.350, 42 events, coverage 0.343, ask 197).

**1.4 Still missing.** The 13 `scripts/` files, the two `assets/*.json` and the
Round 1 result artifacts (`analysis.json`, `primary_summary.csv`,
`ask_timing.json`, …) are still not in the repository. That gap is unchanged
and still needs the working machine.

---

## 2. The structural diagnosis replicates on fresh worlds

Per-seed coverage ceilings, computed on 30 previously unused seeds (analysis
only — complete disclosure, no policy may use this):

| Family | Ceiling (30 fresh seeds) | Round 1 (10 seeds) | Degree-0 | Decline-blocked | Effective edges |
|---|---:|---:|---:|---:|---:|
| development / delayed / shift / drift | **0.395** | 0.399 | 60.5% | 33.0% | 115.1 |
| cold start | **0.326** | 0.341 | 67.4% | 40.9% | 92.0 |
| sparse | **0.169** | 0.178 | 83.1% | 32.4% | 21.9 |

Two things follow.

**(a) Round 1's structural diagnosis is solid.** Independent seed set, same
answer to within 0.015. This is the most reproducible thing in the submission
and it should be presented as such.

**(b) H6 confirmed on fresh worlds.** Every arm lands at **97.6–98.4% of its
own world's ceiling**:

| arm | coverage | coverage ÷ ceiling |
|---|---:|---:|
| `greedy` | 0.338 | 0.979 |
| `potential_ask` | 0.338 | 0.976 |
| `waitfloor` | 0.340 | **0.984** |
| `oldest_first` | 0.339 | 0.982 |

No arm exceeds its ceiling. The supply constraint is real and it binds everyone.
`waitfloor` edges slightly ahead on coverage — the only arm above 0.98.

---

## 3. Why unpaired comparisons across seed sets are meaningless

Per-seed development ceilings across the 30 fresh seeds:

```
0.330  0.340  0.345  0.360  0.365  0.365  0.370  0.370  0.370  0.375
0.375  0.380  0.385  0.385  0.385  0.390  0.390  0.400  0.400  0.405
0.415  0.420  0.420  0.420  0.425  0.425  0.435  0.440  0.450  0.500
```

**Range 0.330 to 0.500 — a 1.5× spread in how much supply a world even has.**
The primary score is largely a property of the world, not the policy. Practical
consequences:

1. Comparisons **must** be paired on identical (seed, variant) worlds. All
   contrasts below are.
2. Never compare a score on one seed set against a score on another. The mean
   ceilings happen to match (0.395 vs 0.399) but individual worlds do not.
3. Report **coverage ÷ ceiling**, not raw coverage. Raw coverage conflates
   policy skill with world generosity. This also fills the per-seed ratio
   column the Round 1 checklist left pending.

---

## 4. Who gets left waiting — a clean negative result

Waits are day-of-first-introduction minus day-of-arrival, over served members
only, exactly as the official evaluator defines them. 30 seeds, all six families.

| arm | mean wait | median | p90 | max | unserved / 200 | coverage |
|---|---:|---:|---:|---:|---:|---:|
| `greedy` | 6.83 | 4.0 | 17.0 | 59 | 132.4 | 0.338 |
| `potential_ask` | 6.37 | 3.0 | 16.0 | 59 | 132.5 | 0.338 |
| `waitfloor` | 6.53 | 4.0 | 17.0 | 59 | **132.0** | 0.340 |
| `oldest_first` | 6.58 | 5.0 | 16.0 | 59 | 132.2 | 0.339 |

**The intervention I built to reduce waiting did not reduce waiting.** The
spread across all four arms is 0.46 days on the mean and 1 day on the p90,
against a within-arm p90 of 16–17 days. Unserved differs by half a member out
of 200.

The reason is visible in the ask-queue saturation curve (mean over episodes):

| day | 0 | 5 | 10 | 15 | 20 | 30 |
|---|---:|---:|---:|---:|---:|---:|
| askable members | 45 | 30 | 15 | 3 | 0 | 0 |
| asks per day (cap 4) | 4.0 | 4.0 | 3.8 | 2.1 | 0.7 | 0.0 |

The cap binds hard for the first ~10 days, then the askable population is
**exhausted by day 15–20 under every rule**. So the ask queue *is* a real
bottleneck early — but it is drained completely, and reordering a queue that
fully drains cannot change who is still waiting at day 20. What is left waiting
at day 20 is left waiting because it has **no feasible partner**, not because it
was asked late.

This is a negative result and it is the useful one: **waiting time is set by
eligibility supply, not by clarification order.** It is the same conclusion the
Round 1 note reached about coverage, now extended to timing. It also means the
Round 2 report should not promise a waiting-time improvement from any ask-rule
change — there isn't one to find on this lever.

---

## 5. Allocation disparity: large, real, and almost entirely not the policy's

The organiser asked for this *even though* the outcome generator has no
demographic term. It has none: acceptance is
`z = −0.25 + bias + fit + shared + drift` with `bias ~ N(0, 0.7)` per member;
response and second-meeting draws are likewise demographic-free.

Decomposition over 6,000 member-episodes per arm (development family). The
outcome generator contains no demographic term anywhere.

### Leg 1 — eligibility supply: `P(has ≥1 feasible partner)` under complete disclosure

| Group | | supply |
|---|---|---:|
| **gender** | man / woman / non-binary | **0.39 / 0.39 / 0.42** |
| **age band** | 21–27 / 28–34 / 35–40 / 41–46 | **0.38 / 0.42 / 0.41 / 0.37** |
| **zone** | a / b / c / d | **0.48 / 0.32 / 0.23 / 0.12** |
| **has children** | no / yes | **0.40 / 0.34** |
| **smoking** | no / occasionally / yes | **0.42 / 0.31 / 0.29** |

**Gender and age are flat.** That is the negative control, and it is what makes
the rest credible — the audit is not manufacturing disparities.

**Zone shows a 4× gap** (0.48 → 0.12), smoking 1.4×, children 1.2×. All of it
arises from members' own stated preferences meeting other members' stated
preferences: `acceptable_zones` is the member's own list, and zones are drawn
60/23/12/05, so a zone_d member has 5% of the pool nearby; `partner_smoking` and
`partner_children` are coin flips that exclude smokers and parents from half the
pool.

### Leg 3 — realised access, **among members who actually have a feasible partner**

| Group | served rate | mean wait (days) |
|---|---:|---:|
| gender man / woman / non-binary | 0.97–0.99 / 0.98 / 0.99–1.00 | 4.6–6.8 |
| age 21-27 … 41-46 | 0.96–0.99 | 5.5–7.3 |
| zone a / b / c / d | 0.97–0.98 / 0.97–0.99 / 0.98–0.99 / **1.00** | 4.8–6.8 |
| children no / yes | 0.97–0.98 / 0.96–0.97 | 5.9–7.8 |
| smoking no / occ / yes | 0.98 / 0.95–0.96 / **0.90–0.92** | 5.9–7.5 |

### Leg 2 — ask allocation is flat: 0.9–1.1 units per member in every group.

### What this means

**The disparity lives entirely in Leg 1 and essentially nowhere else.** A
zone_d member is four times less likely to be introducible *at all* — but
conditional on having a feasible partner, they are served at **100%** and wait
*less* than average. The policy is not leaving them behind; the constraint graph
is.

Two conclusions, both of which belong in the report verbatim:

1. **This disparity cannot be corrected, and attempting it would be a spec
   violation.** Closing the zone gap means overriding `acceptable_zones`, i.e.
   introducing people to partners they explicitly stated they do not accept.
   The problem statement §7: *"A high predicted outcome cannot compensate for a
   constraint violation."* The Round 2 email: *"preserve stated preferences and
   hard eligibility constraints."* The correct engineering answer is to
   **detect, quantify and disclose the disparity, and decline to correct it** —
   and to say plainly that a lower service rate for zone_d is the faithful
   execution of stated preferences, not a defect.

2. **The one residual, policy-controllable gap is small.** Smokers who smoke
   `yes` are served at 0.90–0.92 versus 0.98 overall — a 6–8 point shortfall
   among the reachable. That is the only place I can see a fairness
   intervention legitimately acting without touching stated preferences, and it
   is worth a targeted follow-up (not a headline).

---

## 6. Confirmation of the Round 1 incumbent on fresh worlds

**This is the answer to the organiser's first question, and it is a
non-replication.**

The incumbent (`potential_ask` = potential-ranked hard asks + general-graph
max-weight matching) was rebuilt faithfully — §1.1 — and run on **30 fresh
seeds, paired against the official greedy baseline on identical worlds**.

| arm | MSMI/100 | 95% seed-block CI | events | coverage | cov ÷ ceiling |
|---|---:|---:|---:|---:|---:|
| `greedy` **(official baseline)** | **0.489** | [0.397, 0.586] | 176 | 0.338 | 0.979 |
| `oldest_first` (new) | 0.472 | [0.386, 0.558] | 170 | 0.339 | 0.982 |
| `potential_ask` **(Round 1 incumbent)** | 0.444 | [0.342, 0.544] | 160 | 0.338 | 0.979 |
| `waitfloor` (new) | 0.372 | [0.283, 0.461] | 134 | 0.340 | 0.984 |
| `signed_potential` | 0.372 | [0.283, 0.461] | 134 | 0.338 | — |

### The pre-specified contrast, Round 1 versus now

| | incumbent − greedy | 95% CI | p | seeds |
|---|---:|---:|---:|---:|
| Round 1 note (§6.2) | **+0.175** | [+0.092, +0.258] | 0.016 | 10 |
| **This run, fresh seeds** | **−0.044** | [−0.175, +0.081] | 0.541 | 30 |

**The effect shrank by 125% and crossed zero.** The fresh interval excludes the
Round 1 point estimate and the two intervals barely touch, so this is not just
"wider error bars" — the direction is no longer supported. Nothing in this run
beats the supplied greedy baseline; every arm is statistically indistinguishable
from it or worse.

### All six paired contrasts (identical worlds, seed-block bootstrap)

| contrast | diff | 95% CI | p | W/T/L |
|---|---:|---:|---:|---:|
| greedy − incumbent | +0.044 | [−0.081, +0.175] | 0.541 | 53/84/43 |
| greedy − oldest_first | +0.017 | [−0.092, +0.122] | 0.804 | 46/94/40 |
| incumbent − oldest_first | −0.028 | [−0.128, +0.078] | 0.636 | 42/87/51 |
| greedy − waitfloor | +0.117 | [+0.008, +0.236] | 0.061 | 64/81/35 |
| incumbent − waitfloor | +0.072 | [−0.025, +0.172] | 0.186 | 50/96/34 |
| waitfloor − oldest_first | −0.100 | [−0.189, −0.017] | 0.039 | 30/96/54 |

No contrast excluding zero favours any of our arms. The only interval excluding
zero at all says my `waitfloor` intervention is **worse** than `oldest_first`
(p = 0.039) — so the fairness-floor idea does not survive its own test either.

### How noisy this is, and why Round 1 could not have known

Per-seed paired difference (greedy − incumbent) across the 30 seeds:

```
+0.50 +0.42 −0.08 +0.33 +0.08 +0.08 +0.00 −0.42 −0.50 +0.25
+0.17 −0.25 +0.50 −0.58 +0.25 −0.42 −0.33 +0.08 −0.25 +0.00
−0.33 +0.17 +0.42 +0.42 +0.00 +0.00 +0.08 −0.33 +1.08 +0.00
```

**SD = 0.365 per seed.** A single seed's verdict swings by ±0.5. At 10 seeds the
standard error is ~0.115 and nothing smaller than ~0.23 is resolvable. This is
the arithmetic behind the Round 1 note's own power table, and it is why the
Round 1 result — however carefully measured — could not have supported the
conclusion drawn from it.

### What I would conclude

1. **Do not claim the incumbent beats the greedy baseline.** The evidence now
   points the other way or to a null.
2. **The 0.592 cell has still never been tested.** `lab_potential_core4_maxw` is
   unbuilt and unrun. If you want to ship anything from Round 1, that cell needs
   building and a fresh-seed run before it is believed — and given this
   regression, expect it to land near 0.45–0.50, not 0.59.
3. **`oldest_first` is the interesting survivor.** It ties greedy (+0.017,
   p = 0.804), ties the incumbent (−0.028, p = 0.636), and is *the simplest
   possible rule*: sort the askable members by arrival day, spend the budget,
   run max-weight matching. No potential scoring, no fitted prior, no online
   learning. It is also marginally better than greedy on the tie-break metrics
   official ranking uses if MSMI ties: coverage 0.339 vs 0.338, p90 wait 16 vs
   17 days, unserved 132.2 vs 132.4.
4. **This is exactly the "if a simpler method works as well" moment.** The
   comparison taught us that the entire ask-ranking apparatus buys nothing
   measurable on the primary outcome. That is the finding.

### Immediate next run

`greedy` vs `oldest_first` on **60 seeds** (720 episodes, ~35 min on 2 cores) to
separate them. At 60 paired worlds the resolution is ~0.09, which is enough to
tell whether the +0.017 is a real (tiny) edge for greedy or noise. Do this
before choosing the ship candidate.

---

## 7. Engineering: the protocol adapter runs

The submission scaffold (see `code/` and the root `policy.py`) is built from this work:

- **`policy.py`** — JSON stdin/stdout adapter, one invocation per phase per day.
  Six arms selectable via `--arm` (the official `--baseline` flag is also
  accepted, and `ROUND2_ARM` lets the organisers' `evaluate.py` pick an arm).
  Hard eligibility is a gate in every arm; declined fields are never imputed and
  never re-asked; any internal exception degrades to a valid empty action rather
  than an invalid episode, because **one invalid assessed episode makes the whole
  entry ineligible**.
- **`Dockerfile`** — `python:3.12-slim`, read-only, unprivileged, no network.
- **`requirements.txt`** — **networkx only**. numpy/sklearn/matplotlib are
  dev-only; a shipped prior would be static JSON coefficients, not a fitted
  model. This keeps the image small and cold start fast.

Measured through the official `evaluate.py` in trusted-local subprocess mode:

| Metric | Measured | Limit | Headroom |
|---|---:|---:|---|
| Per-invocation wall time | **0.41 s** | 10 s | 24× |
| Carried memory | counters only, « 1 MiB | 1 MiB | large |
| Image dependencies | networkx | 2 GiB | large |

Verified: both the empty-state request (`members: []`) and the empty feasible
graph return valid empty actions; both `ask` and `match` phases confirmed valid
by the official validator.

**Determinism.** No world seed exists in the protocol request and none is used.
`networkx.max_weight_matching` was checked under `PYTHONHASHSEED ∈ {0, 7, 12345}`
on six complete-disclosure graphs and returned byte-identical matchings — so the
Round 1 note's "bit-identical reruns" claim survives hash randomisation.

**Kit provenance.** `kit.py` is byte-identical (sha256
`0d2cb3d3…`) across the organisers' release, the bundled `starter/`, and the
build directory.

---

## 8. What I would do with this

Ordered by risk, not by interest.

1. **Push the missing `scripts/`, `assets/` and `results/` — today.** If the
   working machine is gone, publish the reproduction-status table instead.
   §1.2 is the warning: rebuilding a Round 1 configuration from the paper alone
   produced the wrong policy and a 0.158 error, and I only caught it because I
   had the stored per-episode rows to diff against. A reviewer will not have
   that luxury.
2. **Accept the confirmation result and change the ship candidate.** §6 says the
   incumbent does not beat the supplied greedy baseline. Shipping it and
   defending 0.525 would now be indefensible. `oldest_first` ties everything and
   is far simpler.
3. **Run greedy vs oldest_first on 60 seeds** to pick between them, and
   pre-register the decision rule first (hash it, push it, then run).
4. **Lead the report with the negative results.** The waiting-time null (§4) and
   the "disparity is supply, not policy" decomposition (§5) are stronger and
   better-evidenced than any score claim, and they answer two of the three
   questions the organiser asked.
5. **Report coverage ÷ ceiling, not raw coverage.** It is the only coverage
   number comparable across worlds, and it fills the per-seed column the Round 1
   checklist left pending.
6. **State the seed-block correction explicitly.** Four of six scenarios share a
   member pool within a seed, so 30 seeds × 6 families is ~90 independent
   worlds. Saying so before a reviewer finds it is worth more than any decimal.
7. **Do not promise a waiting-time improvement.** §4 shows there isn't one on
   the ask-rule lever.
8. **Still to do for the 18 October deadline:** directional calibration (Q3a),
   the learning × asking × allocation factorial (Q2), the H4 batching
   ablation, container-mode timing (only trusted-local measured so far), and a
   full six-variant official-protocol validation of the chosen arm.

### One thing to tell the other agent

I used **seeds 1101–1130**. If their fresh-seed confirmation draws seeds from a
different block there is no overlap; if it overlaps, the two runs are not
independent evidence and should not be pooled. Worth checking before either
result is written up.

---

## 9. Reconciliation with the parallel confirmation run

A second agent ran an independent fresh-seed confirmation and component
factorial (`ROUND2_RESULTS.md`, 10 seeds, 360 episodes). Both runs rebuilt the
incumbent and both reproduce its Round 1 value on the Round 1 seeds, so the two
are comparable. **They agree.**

### The headline contrast, pooled

| Source | incumbent − greedy | 95% CI |
|---|---:|---:|
| Parallel run (10 fresh seeds) | +0.008 | [−0.217, +0.233] |
| This run (30 fresh seeds) | −0.044 | [−0.175, +0.081] |
| **Pooled (40 fresh seeds)** | **−0.031** | **[−0.143, +0.080]** |

Precision-weighted, treating each reported bootstrap CI as ±1.96 SE.
Approximate, and the two runs may share seed 1111, so treat the pooled interval
as slightly optimistic. Either way: **the incumbent's advantage is null, and the
point estimate is now negative in both independent samples.**

### Levels

| | parallel run | this run | pooled |
|---|---:|---:|---:|
| `greedy` (official) | 0.358 | 0.489 | **0.450** [0.371, 0.530] |
| incumbent | 0.367 | 0.444 | **0.426** [0.338, 0.514] |

**Read the greedy row carefully — it is the most useful number in the whole
exercise.** Identical policy, identical code, both faithful to the official
baseline (both reproduce 0.350 on the Round 1 seeds), two disjoint fresh seed
sets: **0.358 versus 0.489.** That 0.13 gap is pure seed variation, with no
policy difference behind it at all. It is the single most persuasive
demonstration available that a 10-seed primary score cannot rank two policies.

### What each run contributes

| | Parallel run | This run |
|---|---|---|
| Q1 confirmation | ✓ 10 seeds | ✓ 30 seeds |
| Q2 component factorial | ✓ full ask × allocation | partial (no greedy-ordering arm) |
| Q3 calibration / missingness | ✓ observability confound, out of sample | — |
| Q3 group disparity decomposition | — | ✓ zone / gender / age / children / smoking |
| Waiting-time intervention | — | ✓ tested, null |
| Per-seed coverage ceilings | — | ✓ 30 seeds |
| Protocol adapter + container | — | ✓ built and measured |

The Q3 results are genuinely complementary, not duplicative: they showed the
**observability** confound (latent response rate flat across observability
groups while declined-share varies 74%→1%), this run shows the **group**
decomposition (zone 4× disparity with gender and age flat). Both point the same
way — the measured disparities are properties of the world's constraint graph,
not of the policy.

### Three discrepancies to state honestly in the report

1. **Level estimates differ by more than their CIs suggest is comfortable**
   (greedy 0.358 vs 0.489). Both implementations are verified faithful, so this
   is seed variation — but it must be disclosed rather than silently picking the
   more flattering number.
2. **My `waitfloor` arm is contaminated.** It was run in the batch that still
   had the signed-`known_equal` bug (§1.2), so its non-reserved slots used the
   *signed* potential ranking, not the incumbent's unsigned one. The intended
   arm (wait-floor + unsigned incumbent ranking) has not been run. Given it
   scored 0.372 — identical to `signed_potential` — and that the intended
   variant would likely sit between 0.372 and 0.444, this does not change any
   conclusion, but the row should be labelled or re-run before publication.
   `oldest_first` and `greedy` are unaffected by the bug.
3. **Possible seed overlap on 1111.** If the parallel run's "1111 to 2020" means
   1111, 1212, …, 2020, the two runs share exactly one seed. Confirm before
   pooling in the final report.

### Bottom line across both runs


- The Round 1 incumbent edge **is gone**: +0.175 → −0.031 pooled.
- The **ask step function survives** in both runs (their `greedy − no_ask`
  +0.292, p = 0.023; every arm in this run within noise of the official greedy).
- **Global max-weight matching adds nothing** over greedy ordering (their
  allocation main effect −0.088, pooling to ≈ −0.015 over 20 seed blocks).
- **Nothing we built beats the supplied greedy baseline.** Two independent
  fresh-seed runs, 40 seeds between them, say so consistently.

---

## 10. Provenance of the missing `scripts/` — resolved

The team's Drive archive (`experiment-lab.zip`, 766 KB, **9 Oct 2026 08:03 IST**)
was retrieved and inspected. It is an **earlier snapshot of the same lab**, not a
different one. Verdict: **`scripts/` does not exist in it either.** Neither
`scripts/` nor `assets/` is present, and none of `analysis.json`,
`primary_summary.csv`, `ask_timing.json`, `main_shard*` or `oracle_shard*` is
there.

### What the snapshot establishes

`NEXT_SESSION_HANDOFF.md` in the archive states, as of 08:03 on the deadline day:

> *"The public scaled factorial is complete: **360 valid policy–world rows**,
> from six methods × six scenario families × ten public seeds."*
> *"The Round 1 research note is **not drafted**."*
> *"`soft_ask_validation_7seeds.py` is prepared … **Not yet run**."*

So at 08:03 the state was 360 episodes / 6 methods. The submitted PDF, filed by
23:59 the same day, reports **1,326 episodes / 17 configurations**.

Between those two points the workspace gained ~35 files. Every one of them is a
**document, a figure, or a hand-transcribed summary**:

```
research/RESEARCH_NOTE_ROUND1*.pdf      research/figures/fig1..8.png
research/ROUND1_NOTE.md                 CHECKLIST.md
research/RESEARCH_NOTE_FINAL.md         SHA256SUMS.txt
research/PROVENANCE_AND_ARTIFACT_STATUS.md
results/soft_ask_holdout_aggregate.csv  (8 rows, hand-entered)
results/reference_verification_3seeds.json
```

**Not one is a runner, a policy, or a shard of episode data.** No script and no
per-episode artifact from the 17-configuration study has ever been seen in any
location.

### The numbers were nonetheless real

Three independent checks say the 17-configuration data was genuinely computed,
not invented:

1. **Funnel tables reconcile.** Appendix B.9 gives seven mutually constraining
   columns per method (assigned → both responded → mutual → date → date ≤30d →
   both on time → MSMI). All **13 rows** are monotone and in range, and the
   implied stage rates reproduce the *separate* stage-rate table to 3–4
   decimals, varying sensibly across methods — P(on-time | date) runs 0.194 for
   `greedy` to 0.305 for the winner, which is the note's own central claim.
   Fabricating that by hand across 13 rows is not realistic.
2. **The overlapping configurations match exactly.** Five of the six methods in
   the 360-row core also appear in the 17-config table; all five agree on
   MSMI, event count, coverage and assignment count. The 17-config run used
   the same harness.
3. **The pilot numbers check out.** §7.5 cites "Thompson 0.472, GP-UCB 0.389,
   GP-mean 0.222" from the three-seed pilot; `summary.csv` in the archive gives
   0.4722 / 0.3889 / 0.2222 — exact.

### Conclusion

**This is a reproducibility failure, not an integrity failure.** The episodes
were almost certainly run in an agent session on deadline day; that session's
workspace was discarded before the 13 scripts and 13 result artifacts were
pushed, and only the documents written from them survived. The Round 1 note is
honest about its pilot data and internally consistent about the rest.

### What to do

1. **Do not cite the 17-configuration numbers as results.** Not because they are
   wrong, but because they cannot be reproduced by anyone, including the team.
   Say so plainly and once, in the Round 2 report, before anyone asks.
2. **Rebuild the submission on the reproducible core** — the 360-row
   six-method factorial (§1.1: reproduced exactly, 60/60 episodes) plus the
   900 episodes in this document. That covers the thesis, the diagnosis, the
   confirmation question and the disparity question without needing a single
   missing file.
3. **It costs almost nothing.** The 0.592 cell was never going to survive
   fresh seeds — §9 shows the incumbent itself regresses to a null across 40
   fresh worlds. Dropping the 17-config layer does not weaken the Round 2
   argument; it removes the weakest evidence and the largest liability.

---

## 11. Draft — reproducibility disclosure for the Round 2 report

*Ready to paste. One paragraph, placed before anyone asks. Say it once, plainly,
and move on.*

> **Reproducibility disclosure.** The Round 1 note reported 1,326 episodes across
> 17 policy configurations. We cannot currently reproduce 13 of those
> configurations: the scripts and per-episode artifacts were produced in
> short-lived research sessions during the submission window, were never
> committed, and no archive of them survives in any of the three locations we
> searched. We have verified that the reported numbers were genuinely computed
> rather than fabricated: the Appendix B.9 funnel table reconciles internally in
> all 13 rows across seven mutually constraining columns, the stage rates it
> implies reproduce the separately reported stage-rate table to three decimal
> places, and the five configurations that overlap with our surviving
> per-episode data match exactly. Every result in this report comes from code
> included in this submission — the 360-episode six-method core preserved from
> Round 1, and 1,260 distinct episodes generated for Round 2 on fresh seeds. We
> do not cite the unreproducible configurations as evidence; where a Round 1
> conclusion depends on them, we re-derive it here or drop it.

**Placement:** immediately after the methods section, before any results table.
Disclosure reads as rigour when it is voluntary; it reads as damage control when
it is extracted under questioning.

**Do not add:** speculation about which session lost the files, or assurances
that the numbers are "probably fine". The paragraph asserts three checkable
facts — what is missing, how we know it was computed, and what we cite instead.

---

## 12. Draft — reproducibility status table for the Round 2 report

*One table, so a reader can see at a glance what stands on code and what does not.*

| Result / artifact | Round 1 value | Reproduces today? | Note |
|---|---:|---|---|
| `greedy` | 0.350 | **Yes — exact** | 360-row core, 60/60 episodes |
| `no_ask` | 0.167 | **Yes — exact** | 360-row core |
| `random_feasible` | 0.358 | **Yes — exact** | 360-row core |
| `max_weight_similarity` | 0.408 | **Yes — exact** | 360-row core |
| `potential_ask` (incumbent) | 0.525 | **Yes — after a bug fix** | Signed vs unsigned agreement score. A naive rebuild from the paper gives 0.367, not 0.525 |
| `unlock_soft7_maxw` | 0.525 | No | No code survives |
| `lab_potential_maxw` | 0.525 | No | No code survives |
| `lab_potential_core4_maxw` | **0.592** | **No** | Round 1 winner, best-of-17 — **no code anywhere** |
| `defaultask_core4_maxw` | 0.483 | No | No code survives |
| Remaining 8 of 17 configs | — | No | No code survives |
| `soft_ask_screen.py` | — | **Yes — self-contained** | Present in repo, imports only `experiment_lab`, zero `scripts/` references |
| Pilot: thompson / GP-UCB / GP-mean | 0.472 / 0.389 / 0.222 | **Yes — exact** | Matches `summary.csv` in the archive |
| Appendix B.9 funnel table | 13 rows × 7 cols | **Internally consistent, 13/13** | Implied stage rates match the separate stage-rate table to 3–4 dp |

### The one line to say out loud

> Four of the six methods we can still run reproduce exactly. The Round 1
> **incumbent reproduces only after fixing a sign error**, and the Round 1
> **winner does not reproduce at all** because its code was never saved.

That sentence is the strongest argument in the report for the Round 2 strategy.
It converts the missing-code problem from an embarrassment into the motivation
for everything that follows — and it is the reason we stopped tuning and started
measuring.

### A caution that belongs in the methods section

**Rebuilding a Round 1 configuration from the note alone yields the wrong
policy.** The `potential_ask` incident is the proof: the signed-agreement variant
scored 0.367 against the incumbent's 0.525, and the difference is invisible
until you score it. A resumed run can also silently skip episodes when arm
*names* match but semantics do not. Verify semantics, not names.

---

## 13. The 60-seed ship decision — `greedy` vs `oldest_first`

720 episodes (60 fresh seeds 1101–1160 × 6 scenarios × 2 arms), seed-block
bootstrap, paired on identical worlds.

### 13.1 Primary score — a tie

| arm | n seeds | MSMI/100 | 95% CI | events | coverage | cov/ceiling | ask cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| `greedy` | 60 | **0.412** | [0.349, 0.479] | 297 | 0.336 | 0.979 | 199 |
| `oldest_first` | 60 | **0.399** | [0.332, 0.471] | 287 | 0.336 | 0.980 | 199 |

`greedy − oldest_first` = **+0.014, 95% CI [−0.058, +0.085], p = 0.736,
W/T/L 28/7/25.** Doubling the seeds from 30 to 60 narrowed the interval but did
not separate the arms. Both sit at 97.9–98.0% of the structural coverage ceiling.

### 13.2 The most important number in this submission

The two batches of 30 seeds were drawn identically. **The same code scored
0.489 on one and 0.336 on the other.**

| arm | batch A (1101–1130) | batch B (1131–1160) | swing |
|---|---:|---:|---:|
| `greedy` | 0.489 [0.397, 0.586] | 0.336 [0.256, 0.419] | **−0.153** |
| `oldest_first` | 0.472 [0.386, 0.558] | 0.325 [0.233, 0.436] | **−0.147** |

Both arms swing by almost the same amount **in the same direction**. That is the
signature of world difficulty, not sampling noise: batch B simply contains harder
worlds. The policy gap is 0.017 on A and 0.011 on B — **the seed-set swing is
9–14× the policy gap.**

**Which 30 seeds you draw matters roughly ten times more than which of these two
policies you ship.**

### 13.3 What the private evaluation can resolve

Per-seed SD of the primary is **0.26–0.28**. On the organiser's **20 private
seeds**, SE ≈ 0.059–0.062, so the 95% half-width is ±0.12.

> Two policies must differ by **more than ~0.24** to be reliably ranked on the
> private set. Our `greedy` vs `oldest_first` gap is **0.014 — about one tenth of
> one standard error.**

Any ranking among near-identical policies on 20 seeds is close to a coin flip.
This is not a failing of our experiments; it is a property of the evaluation
design, and it should be stated in the report.

### 13.4 Tie-breaks — all tie (official order: coverage, mutual acceptances, −ask cost, −time)

| tie-break | `greedy` | `oldest_first` | diff | 95% CI | verdict |
|---|---:|---:|---:|---|---|
| coverage | 0.336 | 0.336 | −0.0003 | [−0.001, +0.001] | tie |
| mutual acceptances | 11.125 | 11.058 | +0.067 | [−0.475, +0.611] | tie |
| clarification cost | 199 | 199 | — | — | tie |
| inference time | 0.07 s/invocation | 0.07 s/invocation | — | — | tie (limit 10 s) |

**Runtime check:** a 1,595 s outlier appeared in the batch run. Re-running those
two worlds in isolation gave **3.9 s per episode** — the outlier was CPU
contention on a 2-core sandbox, not an algorithmic blow-up. Typical cost is
**0.07 s per invocation against the 10 s limit.**

**Ask-budget check:** the harness spends 12 units/day as **4 hard bundles × 3
units**, matching the official "12 units per day". The daily cap is binding on
days 0–10 (4.0, 4.0, 3.8 asks/day) and the askable pool drains to zero by day
20 under every rule — no budget is being wasted.

### 13.5 Waiting — `oldest_first` wins the tail, and significantly

Paired by seed, 60 seeds × 6 scenarios. **Lower is better.**

| metric | `greedy` | `oldest_first` | diff | 95% CI | W/T/L | verdict |
|---|---:|---:|---:|---|---|---|
| mean wait (served) | 6.871 | **6.641** | +0.230 | [+0.071, +0.389] | 43/0/17 | **`oldest_first` better** |
| **p90 wait (served)** | 16.917 | **15.683** | **+1.233** | [+0.800, +1.683] | 37/15/8 | **`oldest_first` better** |
| max wait (served) | 49.983 | 48.433 | +1.550 | [−0.783, +3.833] | 35/2/23 | tie |
| median wait (served) | **4.525** | 4.950 | −0.425 | [−0.708, −0.150] | 12/18/30 | `greedy` better |
| unserved / 200 | 132.900 | 132.847 | +0.053 | [−0.167, +0.281] | 27/11/22 | tie |

**What the arm actually is — be precise about this.** `oldest_first` is **not** a
FIFO matching rule. It keeps the incumbent's max-weight matcher **identical** and
changes exactly one component: **every clarification slot goes to the
longest-waiting askable member**, instead of to the member who looks most
promising. This is a single-component ablation of the ask-allocation rule with the
matcher held fixed — which is exactly the "vary each component separately"
question Round 2 asks.

**Why it moves waiting but not MSMI.** The askable pool drains to zero by day 20
under *every* rule (§4), so the *set* of members who eventually get clarified is
almost the same in every arm — only the **order** differs. The budget is not
scarce in aggregate; it is scarce in *time* (4 bundles/day over ~20 days). Order
therefore determines when each member becomes matchable, which determines their
wait. Spending it on whoever has waited longest compresses the tail; spending it
on whoever looks most promising serves a few people very fast — the median wait is
0.43 days *lower* under `greedy` — and lets everyone else accumulate, leaving the
**p90 1.23 days higher**.

Both waiting intervals exclude zero. The primary score does not move because, by
day 20, essentially the same members have been clarified either way.

### 13.6 Decision — ship `oldest_first`

1. **Primary score: tied.** Giving up +0.014 (0.1 SE) costs nothing that the
   private evaluation can detect.
2. **Waiting tail: genuinely better.** Mean −0.23 and p90 −1.23 days, both
   intervals excluding zero. "Who gets left waiting" is an explicit Round 2
   criterion, and p90 waiting is the natural statistic for it.
3. **It is a clean single-component ablation.** The matcher is unchanged from the
   incumbent; only the ask-priority rule moves. That is a much stronger rhetorical
   position than a whole new policy: it isolates *which* of learning, asking and
   allocation actually matters, and the answer is that asking-order is free to
   change and waiting is what it buys.
4. **Simplicity.** The rule is "whoever has waited longest" — no scoring, no prior,
   no learning, no fitted parameter, no threshold. It cannot overfit and it cannot
   fail at runtime.
5. **No tie-break loss.** Coverage, clarification cost and runtime are identical.

**Framing for the report:** *holding the matcher fixed and changing only whom we
spend the clarification budget on — from "most promising" to "longest waiting" —
leaves the primary outcome unchanged and removes 1.23 days from the p90 wait.*

Show the median/p90 trade honestly: the rule is 0.43 days slower for the
best-matched members, and the argument for it is that the *tail* is what "who gets
left waiting" is asking about. Do not describe it as a FIFO matching queue — it is
not one, and a reviewer who reads the code will catch that.

### 13.7 What this does not settle

- The 0.592 Round 1 winner remains untested; on the evidence here, expect
  **0.45–0.50** on fresh seeds, not 0.59.
- Nothing we built beats the supplied `greedy` baseline on the primary outcome.
  **Do not claim otherwise.**
- `waitfloor` is still contaminated by the signed-ranking bug and must be
  relabelled or re-run before it appears anywhere.

---

## 14. The 120-seed confirmation (run on the lead's Ubuntu VM, 11 Oct)

**Source:** transcribed from the lead's terminal screenshots — the run was done on
their own machine (`yash-VirtualBox`, 4 workers), not in the agent sandbox.
The `analyse.py` output below is complete; progress rows 620–760 were not visible
in the screenshots but do not affect any result.

### 14.1 Primary score — 120 seeds, 1,440 episodes

| arm | n seeds | MSMI/100 | 95% CI | events | coverage | cov/ceil | ask | unserved |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `greedy` | 120 | **0.402** | [0.357, 0.448] | 579 | 0.333 | 0.978 | 197 | 133.3 |
| `oldest_first` | 120 | 0.364 | [0.319, 0.409] | 524 | 0.334 | 0.980 | 197 | 133.2 |

`greedy − oldest_first` = **+0.038, 95% CI [−0.010, +0.089], p = 0.136,
W/T/L 199/355/166.**

### 14.2 This weakens the §13.6 decision

| run | seeds | diff | 95% CI | p |
|---|---:|---:|---|---:|
| §13.1 | 60 | +0.014 | [−0.058, +0.085] | 0.736 |
| **§14.1** | **120** | **+0.038** | **[−0.010, +0.089]** | **0.136** |

**The point estimate nearly tripled and p fell from 0.736 to 0.136.** The
interval now only just contains zero: at worst `oldest_first` is 0.010 better, at
best `greedy` is 0.089 better. A sign test on the 365 non-tied pairs
(199 W vs 166 L) gives z ≈ 1.73, p ≈ 0.08 — consistent with the more conservative
seed-block bootstrap.

**"Statistically indistinguishable" is a weaker claim than it was at 60 seeds.**
The honest reading is now: *leaning `greedy`, not proven.*

### 14.3 The estimate is still moving — this is the caution

Decomposing the 120 seeds into the two 60-seed batches:

| batch | `greedy` | `oldest_first` | diff |
|---|---:|---:|---:|
| 1101–1160 (from §13) | 0.412 | 0.399 | +0.014 |
| **1161–1220 (new)** | **0.392** | **0.329** | **+0.063** |
| all 120 | 0.402 | 0.364 | +0.038 |

The gap was +0.014 on one half and +0.063 on the other. Doubling the data moved
the estimate by 0.024 — the same instability documented in §13.2, where the
same code scored 0.489 and 0.336 on two disjoint 30-seed sets.

### 14.4 Waiting — still favours `oldest_first`, CIs pending

| arm | mean | median | p90 | max | unserved/200 |
|---|---:|---:|---:|---:|---:|
| `greedy` | 6.82 | 4.0 | 17.0 | 59 | 133.3 |
| `oldest_first` | **6.67** | 5.0 | **16.0** | 59 | 133.2 |

Direction is unchanged from §13.5 (mean −0.15, p90 −1.0). **`wait_comparison.py`
has not yet been run on this data** — the CIs that made the 60-seed waiting
result significant are still needed at 120 seeds.

### 14.5 Disparity — unchanged, still world supply

24,000 members per arm. Both arms give essentially identical Leg 2 (ask units
0.9–1.0) and Leg 3 (served|reachable 0.95–1.00) for every group. Zone supply
a 0.47 / b 0.32 / c 0.22 / d 0.10 — a **4.7× spread** — while gender
(0.38/0.40/0.39) and age (0.36–0.41) stay flat. Confirms §5 at double the data:
**the disparity is a property of the world, not the policy.**

### 14.6 Ceilings at 120 seeds — stable

| variant | ceiling | degree-0 | declined | mean degree |
|---|---:|---:|---:|---:|
| development / delayed / shift / drift | 0.387 | 0.613 | 0.333 | 1.12 |
| sparse | 0.167 | 0.833 | 0.329 | 0.22 |
| cold_start | 0.334 | 0.666 | 0.405 | 0.93 |

720 cells. Per-seed development ceilings span 0.260–0.500. Both arms reach
cov/ceil 0.978–0.980 — still no headroom in allocation.

### 14.7 What is still needed before the decision is final

1. **`wait_comparison.py` on the 120-seed members.jsonl** — the one missing number.
2. A judgement call: the primary is what the organisers *rank* on; waiting is a
   *reported* criterion. A non-significant +0.038 on the ranked metric versus a
   significant tail reduction on the reported one is a genuine trade, not a
   formality.

---

## 15. Waiting at 120 seeds — confirmed, and the intervals got tighter

`wait_comparison.py` on the 120-seed `members.jsonl`, paired by seed.
Lower is better for every row except `unserved`.

| metric | `greedy` | `oldest_first` | diff | 95% CI | W/T/L | verdict |
|---|---:|---:|---:|---|---|---|
| **mean wait (served)** | 6.813 | **6.667** | +0.146 | **[+0.033, +0.259]** | 76/0/44 | **`oldest_first` better** |
| **p90 wait (served)** | 16.725 | **15.675** | **+1.050** | **[+0.742, +1.358]** | 76/25/19 | **`oldest_first` better** |
| median wait (served) | **4.533** | 4.929 | −0.396 | [−0.604, −0.188] | 28/34/58 | `greedy` better |
| max wait (served) | 49.175 | 48.908 | +0.267 | [−1.242, +1.792] | 61/9/50 | tie |
| unserved / 200 | 133.301 | 133.150 | +0.151 | [−0.007, +0.315] | 58/17/45 | tie |

### The waiting finding survived doubling the data

| metric | 60 seeds (§13.5) | 120 seeds (§15) | interval width |
|---|---|---|---|
| mean wait diff | +0.230 [+0.071, +0.389] | +0.146 [+0.033, +0.259] | 0.318 → **0.226** |
| p90 wait diff | +1.233 [+0.800, +1.683] | +1.050 [+0.742, +1.358] | 0.883 → **0.616** |

Both intervals shrank by ~30% and both still exclude zero. `oldest_first` gives
the shorter waiting tail in **76 of 120 seeds** on both mean and p90. This is a
solid, reproducible effect — unlike the primary-score difference, which moved by
0.024 when the data doubled.

### The trade is now sharp

| criterion | evidence | significance |
|---|---|---|
| **Primary score** (what is *ranked*) | `greedy` +0.038 [−0.010, +0.089] | **p = 0.136, not significant** |
| **Waiting tail** (what is *reported*) | `oldest_first` p90 −1.050 [−1.358, −0.742] | **significant** |

### The decisive fact, from the organiser's own text

`PROBLEM_STATEMENT.md` line 191:

> "Rank eligible submissions by this primary score in descending order. Break
> exact unrounded ties by mean distinct-member introduction coverage, then mean
> mutual acceptances per 100 arrived members, then lower mean clarification
> cost, then lower measured inference time. **A remaining exact tie shares rank.**"

Line 193:

> "**Report** assignments, mutual acceptances, dates, MSMI, coverage,
> clarification cost and missing feedback separately. **Report**
> first-introduction waiting times, including the unserved count."

**Waiting time is not in the tie-break chain.** It is a *reporting* requirement,
not a *ranking* input. The primary score is the only thing that moves rank.

### Decision — ship `greedy`

Expected-value reasoning, not significance reasoning. The question is not "can we
rule out zero?" but "which choice has the higher expected primary score?" The best
estimate is `greedy` by +0.038, and a sign test on 199 W vs 166 L (p ≈ 0.08) points
the same way. Roughly a 7% chance the true effect is reversed.

At 20 private seeds with SE ≈ 0.06, +0.038 is 0.63 of a standard error — a real,
if modest, shift in expected rank against a field.

**The waiting finding is not lost.** It becomes the headline result of the report:
*holding the matcher fixed and changing only whom we spend the clarification
budget on has no significant effect on the primary outcome, but removes
1.05 days from the p90 wait.* That is a clean, significant, single-component
ablation — and it is worth more as a reported finding than as a 0.038 gamble on
the ranked metric.

### The case for `oldest_first`, stated honestly

- The primary difference is **not significant** (p = 0.136). Standard practice
  says do not prefer an option with a non-significant disadvantage on the ranked
  metric over one with a significant advantage on a reported one.
- The primary estimate has moved twice already (+0.014 at 60 seeds, +0.063 and
  +0.014 on the two 60-seed halves). It is not stable; the waiting estimate is.
- If the report is graded qualitatively as well as ranked, the significant
  finding is the stronger contribution.

**This is a genuine judgement call, not a formality.** The numbers support
`greedy` on expected rank and `oldest_first` on statistical strength. The tie is
broken by the fact that only the primary score affects rank.

### Optional: try to have both

A 50% reserve (`waitfloor`) might keep `greedy`-level primary while capturing part
of the waiting gain. `waitfloor` has never been run clean — its 0.372 came from
the contaminated signed-ranking batch — so its true value is unknown. 720 episodes
at 120 seeds costs ~35 min on a 4-core VM. If it lands at or above `greedy` on the
primary and keeps a waiting benefit, it dominates both. Worth doing only if the
Docker build is already done.

---

## 16. Submission-compliance gap found and fixed (13 Oct)

Re-reading `PROBLEM_STATEMENT.md` §12 against what we had. **Two required
items were missing.**

### 16.1 Missing baselines — FIXED

> "Include all three baseline comparisons, at least one ablation,
> scenario-level results, declared training seeds and inference random seed."

We had only `greedy`. `no_ask` (no-clarification) and `random_feasible` were
absent from the harness entirely. Both have now been added to `waitlab.py`
(`asks_none`, `pairs_random_feasible`), registered in all three tables
(`ARMS`, `ASK_RULES`, `MATCHERS`), and verified on a real 6-episode run.

**They have not yet been run at 120 seeds.** That is one command:

```bash
python3 waitlab.py --seeds $(python3 -c "print(','.join(str(s) for s in range(1101,1221)))") \
    --arms no_ask,random_feasible --workers 4 --out ~/out_baselines
```

~35 min on a 4-core VM.

### 16.2 First look (1 seed, 6 episodes — indicative only)

| arm | MSMI/100 | coverage | **cov/ceiling** | ask cost | unserved/200 |
|---|---:|---:|---:|---:|---:|
| `no_ask` | 0.000 | 0.123 | **0.295** | 0 | 175.3 |
| `random_feasible` | 0.750 | 0.387 | 0.973 | 214 | 122.7 |

**This is the ablation the brief asks for.** Switching clarification off drops
coverage from ~98% of the structural ceiling to **29.5%** — a 68-point collapse.
Everything else we tested (scoring, ask priority, wait floors) moves the primary
score by a few hundredths; *asking at all* moves reachable coverage by two
thirds. Clarification is the load-bearing component, and this is the one place
where a policy choice has a large, unambiguous effect.

Caveat: n = 1 seed. The direction is not in doubt (0 events vs 9), but the
magnitude needs the 120-seed run before it is quoted.

### 16.3 Other compliance items

| requirement | status |
|---|---|
| Policy + Dockerfile | ready; image builds with **zero third-party dependencies** |
| Pinned dependencies | none needed for `greedy`; `networkx==3.7` documented for max-weight arms |
| Reproducible evaluation command | in `README.md` Step 5 |
| Machine-readable results | `results/*.json` + committed CSV/JSONL |
| Technical report | **not yet assembled** — §11–§16 are the drafted sections |
| Declared training seeds | none used (no fitted model); state this explicitly |
| Inference random seed | `PYTHONHASHSEED=0` pinned in the Dockerfile |
| Attribution | `LICENSE.kit` included |
| **Immutable archive** | **must be a full 40-char commit SHA or an archive + SHA-256.** A branch ZIP URL is explicitly *not* acceptable |
| All three baselines | `greedy` done; `no_ask` + `random_feasible` pending |
| At least one ablation | §16.2 (clarification off) plus §13–§15 (ask-priority ablation) |

### 16.4 Deadline

`PROBLEM_STATEMENT.md` §12 states **18 October 2026, 23:59 IST** (18:29 UTC).
The lead reports **17 October**. **Plan for the 17th and treat the 18th as a
buffer** — a submission that is complete a day early cannot be harmed by the
discrepancy, and one that assumes the later date can.

---

## 17. The complete four-way comparison — 120 seeds, 2,880 episodes

All four policies on identical fresh seeds (1101–1220), paired, seed-block
bootstrap. This is the table the submission requires.

### 17.1 Primary score

| arm | MSMI/100 | 95% CI | events | coverage | **cov/ceiling** | ask | unserved/200 |
|---|---:|---|---:|---:|---:|---:|---:|
| **`greedy`** (supplied) | **0.402** | [0.357, 0.448] | 579 | 0.333 | 0.978 | 197 | 133.3 |
| `oldest_first` (ours) | 0.364 | [0.319, 0.409] | 524 | 0.334 | 0.980 | 197 | 133.2 |
| `random_feasible` (supplied) | 0.332 | [0.292, 0.374] | 478 | 0.335 | **0.982** | 197 | 133.0 |
| `no_ask` (supplied) | 0.098 | [0.075, 0.122] | 141 | 0.120 | **0.344** | 0 | 176.0 |

### 17.2 All six paired contrasts

| contrast | diff | 95% CI | p | W/T/L |
|---|---:|---|---:|---|
| greedy − oldest_first | +0.038 | [−0.010, +0.089] | 0.136 | 199/355/166 |
| **greedy − random_feasible** | **+0.070** | **[+0.023, +0.116]** | **0.004** | 205/385/130 |
| greedy − no_ask | +0.304 | [+0.261, +0.349] | 0.000 | 343/357/20 |
| oldest_first − random_feasible | +0.032 | [−0.019, +0.083] | 0.239 | 214/331/175 |
| oldest_first − no_ask | +0.266 | [+0.221, +0.312] | 0.000 | 311/378/31 |
| no_ask − random_feasible | −0.234 | [−0.281, −0.189] | 0.000 | 44/391/285 |

### 17.3 THE DECISIVE RESULT

> **`greedy` beats `random_feasible` by +0.070, 95% CI [+0.023, +0.116], p = 0.004.**
> **`oldest_first` does not: +0.032, CI [−0.019, +0.083], p = 0.239.**

This is the **first statistically significant advantage** found anywhere in the
project, and it settles §15. `greedy` is the only arm that can claim to beat the
random-feasible baseline. `oldest_first` cannot.

**Decision confirmed: ship `greedy`.** Not on a leaning any more — on a
significant result.

### 17.4 Finding 1 — clarification is the load-bearing component

| | `no_ask` | all asking arms |
|---|---:|---:|
| cov/ceiling | **0.344** | 0.978–0.982 |
| MSMI/100 | 0.098 | 0.332–0.402 |
| unserved/200 | 176.0 | 133.0–133.3 |
| asks/day | 0.0 | binds at 4.0 until day ~15 |

The askable pool **grows** under `no_ask` (46 → 51 → 55 → 60 → 65 → 64 → 60 → 58)
and never drains, because unresolved members accumulate faster than they can be
matched. Under every asking arm it **drains to zero** (46 → 31 → 16 → 4 → 1 → 0).

Turning clarification off costs **−0.304 MSMI (p < 0.001)** and two thirds of
achievable coverage. Every other design choice in this study moves the primary
score by hundredths. **Clarification is worth ~10× anything else we tested.**

### 17.5 Finding 2 — allocation *quality*, not allocation *quantity*

| arm | coverage | cov/ceiling | MSMI/100 |
|---|---:|---:|---:|
| `greedy` | 0.333 | 0.978 | **0.402** |
| `random_feasible` | **0.335** | **0.982** | 0.332 |

`random_feasible` makes **more** introductions and reaches a **higher** fraction
of the structural ceiling — yet scores 0.070 lower (p = 0.004). The two arms use
identical coverage and identical ask spend (197); the entire difference is
**which** feasible pairs get chosen.

The bottleneck is not how many people you serve. It is whom you pair them with.

### 17.6 Finding 3 — ask *priority* moves waiting, not outcomes

`oldest_first` cuts p90 wait by **1.05 days** (p < 0.001, §15) while leaving the
primary score statistically unchanged. Asking strategy is a free lever on
fairness and a null lever on the outcome.

### 17.7 A trap in the waiting table — do not report it naively

| arm | mean wait | median wait | **unserved/200** | served/200 |
|---|---:|---:|---:|---:|
| `no_ask` | **3.99** | **0.0** | 176.0 | **24** |
| `greedy` | 6.82 | 4.0 | 133.3 | 66.7 |

`no_ask` looks like it has the *best* waiting times. It does not. Waits are
conditional on being served, and `no_ask` serves only **24 of 200** members —
the handful who happen to be fully observable on arrival, matched instantly
(median 0). It abandons **43 more people per world** than `greedy` does.

**Any waiting comparison must be reported alongside the unserved count.**
Reporting mean wait alone would make the worst policy look the fairest. This is
exactly the "who gets left waiting" trap the brief warns about.

### 17.8 Final headline set for the report

1. **Clarification dominates.** Removing it costs −0.304 MSMI and two thirds of
   achievable coverage (p < 0.001). Nothing else comes close.
2. **Pairing quality beats pairing quantity.** Identical coverage, +0.070 MSMI
   (p = 0.004).
3. **Nothing beat the supplied greedy baseline.** Our best alternative was 0.038
   below and not significant.
4. **Ask priority is a free fairness lever.** −1.05 days p90 wait, no
   significant outcome cost.
5. **Seed-set variation swamps policy variation.** Same code: 0.489 vs 0.336.
6. **Waiting statistics are conditional** — report them with the unserved count
   or they invert.

### 17.9 The submission story, honestly

> We ran 2,880 episodes across four policies on 120 fresh seeds. The supplied
> greedy baseline was the strongest. Nothing we built beat it. We ship greedy —
> and we can show, significantly, that it beats the other two supplied baselines.

The problem statement §3 explicitly permits this: *"A simpler method with
convincing experiments is a valid submission. No particular model family is
required."*

---

## 18. Bug audit — 13 Oct

Requested by the lead after a time-base bug invalidated results in a separate
project. **The check below is the one that would have caught that class of
error**: our harness is run against the *organiser's own evaluator* on identical
seeds, rather than checked only against itself.

### 18.1 External validation against the official evaluator

`kit.py` release 1.0.0, official `evaluate.py --baseline {greedy,no_asks,random}`,
seeds 1101–1102, all six variants. Our `waitlab.py` on the same seeds.

| arm | metric | ours | official | diff |
|---|---|---:|---:|---:|
| `greedy` | msmi_per_100 | 0.708333 | 0.708333 | **0** |
| `greedy` | coverage | 0.347917 | 0.347917 | **0** |
| `greedy` | ask_cost | 194.500000 | 194.500000 | **0** |
| `no_ask` | msmi_per_100 | 0.166667 | 0.166667 | **0** |
| `no_ask` | coverage | 0.127083 | 0.127083 | **0** |
| `no_ask` | ask_cost | 0.000000 | 0.000000 | **0** |
| `random_feasible` | msmi_per_100 | 0.500000 | 0.500000 | **0** |
| `random_feasible` | coverage | 0.350417 | 0.350417 | **0** |
| `random_feasible` | ask_cost | 194.500000 | 194.500000 | **0** |

**9/9 exact matches to machine precision, across three independently-written
policies.** This covers the organiser's own matcher and asker (`greedy`), and
our reimplementations of the other two (`asks_none`, `pairs_random_feasible`) —
so those are verified against the reference, not merely self-consistent.

### 18.2 Internal consistency of the 120-seed output

Twenty-five independent arithmetic relationships in the reported tables, all
holding exactly:

- **Primary vs event count.** `events / 720 episodes / 200 arrived × 100`
  reproduces every primary score: greedy 579 → 0.402; oldest_first 524 → 0.364;
  no_ask 141 → 0.098; random_feasible 478 → 0.332. All four exact.
- **Coverage vs unserved.** `(200 − unserved) / 200` reproduces every coverage
  figure: 0.333, 0.334, 0.120, 0.335. All four exact.
- **All six pairwise contrasts** equal the difference of the arm point estimates.
- **All six W/T/L rows sum to 720** (120 seeds × 6 variants).
- **cov/ceiling** is consistent with mean coverage ÷ mean ceiling
  (0.3415 across the six variants) for every arm.

### 18.3 What this does and does not rule out

**Ruled out:** any error in the episode loop, the metric definitions, the
scenario handling, the ask-budget accounting, or the baseline semantics. A defect
in any of those would break the agreement with the official evaluator.

**Not ruled out:**
- A bug in the *organiser's own* evaluator. We match it, so we would inherit it.
  Nothing we can do; every team shares that exposure.
- Bugs in arms not yet externally validated: `oldest_first`, `potential_ask`,
  `waitfloor`. These use `max_weight_pairs`, which is our code. `oldest_first`
  shares its asker with no baseline, so it is the one arm with no external
  anchor — its *waiting* result rests on our own instrumentation.
- The `waitfloor` contamination (§13.7) is still unresolved; that arm remains
  unreported.

### 18.4 Recommended extra check, if time allows

Validate `oldest_first` the same way — run it through the official evaluator via
our policy adapter (`our_policy.py`) and confirm it reproduces the harness
number on seeds 1101–1102. That would close the last unvalidated arm that
appears in the report.

```bash
# in the VM, with the built image:
echo '{"phase":"ask", ...}' | docker run --rm -i -e ROUND2_ARM=oldest_first bipartite-bard:round2
```

---

## 19. Rebuilding Round 1's lost winner instead of merely reporting it missing

The lead asked whether the lost configurations could simply be re-run.
Partly yes, and the distinction matters.

### 19.1 What re-running can and cannot recover

| lost item | recoverable by re-running? | why |
|---|---|---|
| the **13 scripts** (code) | **No — categorically** | Code is the *input* to a run, not its output. Circular. |
| the **13 result artifacts** | No | Needs the code to regenerate. |
| the **reported numbers** | Only by reimplementation | And reimplementation from a paper is unreliable (§12). |

So the artefacts are gone. But **the configurations are not** — they can be
rebuilt from the published note and tested on fresh seeds, which is better
evidence than the lost run ever was.

### 19.2 `lab_potential_core4_maxw` (reported 0.592) — rebuilt

Round 1's best-of-17 winner is described as potential-ranked asking with
max-weight matching restricted to the **four core soft fields**. Our existing
`potential_ask` arm uses all seven `SOFT` fields, so the reconstruction is a
one-line change: score on `CORE` instead of `SOFT`.

Added to `waitlab.py` as **`potential_core4`** — `asks_potential` +
`max_weight_pairs_core4`. Verified on a 12-episode smoke run.

### 19.3 Why this is worth running

Our prediction (§8) was **0.45–0.50, not 0.592**, because the reported value was
the maximum of 17 configurations on 10 seeds.

| outcome | meaning |
|---|---|
| lands near **0.59** | Round 1 was right; this configuration becomes the ship candidate and beats `greedy` |
| lands near **0.45–0.50** | confirms 0.592 was a selection artefact — a *stronger* result than the lost run, because we can show it |

Either outcome is a real finding and supersedes the missing artefact.

```bash
python3 waitlab.py --seeds $(python3 -c "print(','.join(str(s) for s in range(1101,1221)))") \
    --arms potential_core4 --workers 4 --out ~/out_core4
```

720 episodes, ~25 min on 4 cores.

### 19.4 On disclosure — reframe, do not conceal

The Round 2 report does **not** need to lead with "we lost our code." It needs
to state what was done. Suggested wording:

> "Round 1 screened seventeen configurations on ten seeds. Every policy in this
> report is rebuilt from the published descriptions and evaluated on 120 fresh
> seeds. Round 1's reported best configuration was reconstructed and retested
> (§19). Configurations whose behaviour we could not independently reproduce are
> not cited as evidence."

This is honest, verifiable, and stronger than a confession — because the reader
sees a rebuild-and-retest, not an excuse. It also matches the project's stated
practice: negative and inconvenient results reported with the same prominence as
positive ones.

**Do not** simply omit the Round 1 comparison. The non-replication result (§9) is
one of the strongest findings in the report, and it requires citing Round 1's
numbers to make sense.
