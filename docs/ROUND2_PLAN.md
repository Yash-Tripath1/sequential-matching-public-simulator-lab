# Round 2 plan: The One Introduction Problem
**Team Bipartite Bard · drafted 10 Oct 2026 · no simulations run**

This is a working document: what I read, what I think the feedback is really asking,
what I'd build, and the order I'd build it in. Nothing below has been executed
except two generator-structure probes, which are flagged as such in §3.1 and §5.2.

---

## 0. What I read

| Source | What it is |
|---|---|
| `IITM_RJ_Research.pdf` | the 30-page Round 1 note (rev3 lineage) |
| `SCALED_FACTORIAL_RESULTS (1).md` | the 10-seed clarification × matcher screen writeup |
| GitHub repo | 7 commits; `experiment_lab.py`, `scaled_factorial.py`, `results/`, `research/` |
| `starter/kit.py` | the organiser simulator, read line by line |
| Round 2 email | the three questions + the deliverables list |

**Headline numbers I'm working from** (PDF Appendix B.6, 60 episodes per arm, 10 public seeds):

```
lab_potential_core4_maxw   0.592  [0.392, 0.808]   71 events   <-- selected winner
lab_potential_maxw         0.525  [0.408, 0.633]   63 events   <-- incumbent
unlock_soft7_maxw          0.525  [0.375, 0.733]   63
defaultask_core4_maxw      0.483  [0.358, 0.600]   58
greedy (official)          0.350  [0.233, 0.467]   42
no_ask (official)          0.167  [0.050, 0.292]   20
```

---

## 1. Priority zero: the reproducibility gap

This is not a Round 2 task, it is a precondition for having a Round 2 at all.
The email praises "your attention to the measurement process" and then asks for
"a working implementation with source code and a reproducible environment".
Right now the repository cannot reproduce the note.

**What's missing.** `CHECKLIST.md` and `research/PROVENANCE_AND_ARTIFACT_STATUS.md`
both say, in as many words, that these are *pending push from the working machine*:

- `scripts/*.py`, 13 files (structure/supply diagnosis, rollout logging, prior
  fitting, oracle ladder, ask timing, attainable ceiling)
- `assets/hard_priors.json`, `assets/outcome_prior.json`
- `results/analysis.json`, `primary_summary.csv`, `ask_timing.json`,
  `attainable_ceiling.json`, `structure_diagnosis.json`, `supply_bounds.json`,
  `outcome_model.json`, `main_shard*.json`, `oracle_shard*.json`

I checked: **none of them are in the repo.** There is no `scripts/` directory and
no `assets/` directory. The PDF cites `results/analysis.json`,
`results/primary_summary.csv` and `results/ask_timing.json` three separate times;
all three are absent.

**How the two artifacts diverge.** The PDF reports 1,326 episodes across 17
configurations (1,020 head-to-head). The repo's largest artifact,
`results/scaled_factorial_10seeds.json`, holds 360 episodes across 6 methods.
Cross-checking the six:

| Repo method | MSMI/100 | PDF row it matches |
|---|---:|---|
| `greedy` | 0.350 | `greedy` 0.350 ✓ |
| `no_ask` | 0.167 | `no_ask` 0.167 ✓ |
| `random_feasible` | 0.358 | `random_feasible` 0.358 ✓ |
| `max_weight_similarity` | 0.408 | `defaultask_soft7_maxw` 0.408 ✓ |
| `potential_ask` | 0.525 | `lab_potential_maxw` 0.525 ✓ |
| `potential_ask_greedy` | 0.467 | **no row anywhere in the PDF** |

And the reverse: **the PDF's winning configuration has no code in the repo.**
`lab_potential_core4_maxw` (0.592) needs three things: the unlock-value ask rule,
the signed core-4 weight coding, and the fitted logistic prior. I grepped the whole
repo: no `unlock_value`, no `core4`, no `signed`, no prior asset. The only
occurrence of the string `lab_potential_core4_maxw` in the entire repository is a
LaTeX comment inside `research/build_pdf_rev2.py`.

There is also a naming collision waiting to bite: the repo's
`potential_ask_greedy` (0.467) and the PDF's `unlock_greedy` (0.475) are different
methods with confusingly similar roles, and only one of them exists in each artifact.

**Two ways out.**

- **(A) Recover.** If the working machine still exists, push the 13 scripts, the two
  assets and the result artifacts, then do a *clean-clone reproduction* and commit the
  log. This is the only route where Round 1 stands as written.
- **(B) Re-scope, honestly.** If it's gone, say so first, in the Round 2 report, before
  any new number. Rebuild the missing configurations against the repo, re-run, and
  publish a **Round 1 reproduction status table**: every headline number, whether it
  currently reproduces, and the reason if not. Route (B) is survivable *because* the
  note's whole brand is disclosure, but it is only survivable if you volunteer it.
  Being caught is the version that ends the submission.

Do this first. Everything else in this document assumes it is resolved.

---

## 2. What I think the feedback is actually saying

Three questions, but read them together they are one request.

> *"Does the chosen configuration survive confirmation on genuinely new worlds…"*

The 0.592 is the best of 17 screened cells. The note already knows this: it says so
in §6.2(a), and the fresh-seed split in §6.1 gives +0.143 with a CI that straddles
zero. They are telling you the 0.592 is not yet a result.

> *"Which interactions between learning, asking and allocation remain once each
> component is varied separately?"*

You never ran learning × asking × allocation as a factorial. You ran asking ×
weight-coding at a fixed matcher, plus two greedy ablations. "Varied separately" is
a request for a real design.

> *"Can you check both directional calibration and allocation disparities, even when
> the synthetic outcome generator has no demographic effect?"*

The "even when" is the interesting half. They know the generator draws acceptance
blind to demographics. They want to see whether you understand that this does **not**
imply zero measured disparity, and whether you can tell the two apart.

And then the sentence I'd tape to the monitor:

> *"If a simpler method works as well, explain what the comparison taught you."*

That is a strong hint. Read with your own §6.2, ask targeting null, fitted prior
actively *harmful*, online adaptation a literal 0/60/0, residual soft asks null, 
the organisers are inviting you to ship something simple and spend the saved
complexity budget on evidence instead. I think that is the right call, and §7 makes
the case.

---

## 3. Question 1: confirmation on genuinely new worlds

### 3.1 A structural fact you have not yet used, and it changes the statistics

I probed `generate()` directly (no policy, no rollout, just two `generate()` calls
and a member-ID comparison). For a fixed seed:

| Variant | Shares member pool with `development`? |
|---|---|
| `delayed` | **yes, identical 200 members, identical IDs, ages, genders, biases, response rates, arrival and exit days** |
| `shift` | **yes, identical** |
| `drift` | **yes, identical** |
| `cold_start` | no, diverges after ~15 members |
| `sparse` | no, diverges after ~2 members |

The mechanism is in `kit.py`: the draw sequence is `random.Random(seed)` and the
variant only branches on the `sparse` zone rule and the `complete = r.random() < p`
threshold. Non-sparse variants with the same `p` never desync. And crucially
`rand_for(world_seed, a, b, day)` means **the pair-level outcome draws are shared
across those four variants too.**

So your ten "seeds × six families" is really ten seeds × **three** independent
worlds. `development`, `delayed`, `shift` and `drift` are the same 200 people
re-run under four different dynamics. Your own Appendix B.1 says as much
("delayed / shift / drift, identical to development") but the inference was never
carried into the statistics.

**The specific defect.** §5.3 gets the primary CI right (it bootstraps seed blocks,
which keeps the shared world together). But the note also says *"Scenario CIs in the
JSON resample ten episodes within each family."* That resamples across seeds within
a family: it smears one world's four correlated scenarios across ten independent
worlds. Any per-family interval computed that way is too narrow, and it is exactly
what "scenarios sharing a world kept together in the uncertainty calculation" is
pointing at.

**Fix, three things:**

1. One resampling unit everywhere: the **seed block**. No exceptions, no per-family
   episode bootstrap. Per-family intervals become "this family's contribution to the
   seed-block bootstrap", reported as descriptive, with the dependence stated.
2. Report the **effective sample size**. State plainly: 40 seeds × 6 families = 240
   episodes but ≈120 independent worlds, because four of six scenarios share a pool.
   Then quote the design effect and the corrected power. This is a credibility move, 
   it shows you know the number is smaller than it looks.
3. A **cluster sensitivity check**: bootstrap at the (seed, scenario) level versus the
   seed level and show how much the interval moves. If it barely moves, say so and
   move on; if it moves a lot, every Round 1 per-family claim needs revisiting.

### 3.2 Confirmation itself

The good news: `generate(seed=…)` accepts any integer. There is **no fixed public
seed set**: 101…1010 was your choice. Genuinely new worlds are free.

Protocol I'd run:

1. **Freeze and pre-register.** Commit, before a single fresh episode: the frozen
   configuration, the frozen hyperparameters, the fresh seed list, the primary
   contrast, and the decision rule. Hash it (`SHA256SUMS.txt` already exists, reuse
   it) and push. The hash is the whole point; it's what makes the confirmation a
   confirmation.
2. **Generate the seed list mechanically** (e.g. `random.Random(20261010).sample(range(10_000, 99_000), 40)`),
   commit the generator call, and never hand-pick. Hand-picked "fresh" seeds are not
   fresh.
3. **Run the frozen config and the official greedy on identical worlds**, 40 seeds × 6
   families = 240 episodes per arm.
4. **Pre-register the claim rule**, e.g.: *we will call this confirmed if the 95%
   seed-block CI lower bound on (config − greedy) exceeds 0 and the point estimate is
   ≥ 0.10.*
5. **Report the regression.** You are testing a best-of-17 selection. Say in advance
   that you expect shrinkage, and report it either way. If 0.592 comes back at 0.51,
   the honest paper is *"the selected configuration regressed by 0.08 on fresh worlds;
   here is the screen-to-confirmation gap, and here is what we now believe."* That is
   a better submission than a fragile 0.592.

### 3.3 Power: this is the real fix

Your Appendix B.5 is the most under-used table in the note:

| Gap to detect | Episodes per arm |
|---|---:|
| 0.30 | 37 |
| 0.20 | 83 |
| 0.15 | 146 |
| 0.10 | 329 |

Sixty episodes resolve ≈0.234. Your entire spread of interesting configurations is
0.40 → 0.59. **You have been running an experiment that cannot answer the question
you are asking.** Round 1 was not wrong, it was underpowered, and the note says so
in six different places without changing the design.

The fix is not a cleverer estimator. It is more worlds, and fewer arms.

At ~6.7 s/episode in-process:

| Design | Episodes | Core-hours | Wall time, 16 workers |
|---|---:|---:|---:|
| 2 arms × 40 seeds × 6 | 480 | 0.9 | ~4 min |
| 12 cells × 40 seeds × 6 | 2,880 | 5.4 | ~21 min |
| 12 cells × 60 seeds × 6 | 4,320 | 8.0 | ~32 min |

All of it is affordable. **Restructure from "17 configurations × 10 seeds" to
"4–6 configurations × 40–60 fresh seeds."** Same compute, roughly double the
resolution, and it answers all three questions at once.

Run it with a resumable process pool writing row-level JSONL (you already built one
for the soft-ask screen, reuse it).

---

## 4. Question 2: learning × asking × allocation

### 4.1 The design

A full factorial with each component varied on its own. Keep it small enough to
power:

| Component | Levels |
|---|---|
| **Learning** | static offline prior · online ridge-anchored refit |
| **Asking** | default (supplied `baseline_asks`) · count-based potential |
| **Allocation** | greedy ordering · global max-weight matching |

2 × 2 × 2 = 8 cells, 40 seeds, 6 families = 1,920 episodes. Add the two official
baselines on the same worlds for the required comparison.

Estimate the three main effects, three two-way interactions and one three-way
interaction **directly as contrasts on paired worlds**, each with a seed-block CI and
a W/T/L count.

### 4.2 My predictions, and why I'd commit to them in advance

Writing these down before running is the single cheapest integrity upgrade available.

- **Learning main effect ≈ 0, and the interactions with it ≈ 0.** Your §6 already
  found the online adapter produced *identical MSMI outcomes in all 60 episodes*.
  The mechanism is structural: ~0.9 MSMI events per episode, and a day-40
  introduction matures after day 70, past the horizon. There is nothing to learn
  online inside one episode at this event rate. Expect a clean null.
- **Asking main effect > 0, but strictly the step function.** Any asking beats none
  (+0.183). Which asking rule does not measurably matter.
- **Allocation main effect small and positive**, consistent with your +0.058.
- **All interactions ≈ 0, and indistinguishable from zero at even 40 seeds.** The
  interaction terms are smaller than the main effects, and the main effects are
  already at the resolution limit.

If I'm right, the honest Round 2 result on Q2 is: *"we ran the three-way factorial
at a resolution capable of detecting 0.15; the learning component and every
interaction involving it are null; the only surviving effect is the asking step
function, which we already knew."* That is a real finding: it says the system is
supply-determined, not policy-determined, which is the note's thesis.

### 4.3 The one component worth adding: batching (H4)

H4 is untested and it is the only lever that acts on *timing* rather than *ranking*, 
your §7.6 identifies exactly that, and §6.6 shows live feasible edges collapsing to
single digits by day 10 under every rule.

But I'd go in expecting to falsify it, and here is the reason: **Akbarpour, Li and
Oveis Gharan's Patient algorithm only beats Greedy when the planner can identify
agents about to depart.** I checked `observe()`: it returns `member_id`, `pool_id`,
`synthetic`, `age`, `gender`, `zone`, `arrived_day`, `fields`, `field_status`,
`field_observed_day`, `source`, and a computed `available` boolean. **`exit_day` is
not in the observation contract.** Departure times are unobservable, the
precondition fails, and the theory's own fallback says Greedy is close to optimal.

That is a clean, theory-grounded, pre-registered prediction: **batching does not
help.** It costs 2 extra cells (batch window k ∈ {1, 3, 7}) × 6 families × 20 seeds
= 360 episodes. Worth it precisely because it closes the last open hypothesis in
the note and does so with a citation-backed prediction rather than a fishing trip.

---

## 5. Question 3: directional calibration and allocation disparities

This is where I think you can actually win Round 2. It is the most interesting
question, it is the one nobody will have done well, and I already have the shape of
the answer.

### 5.1 Directional calibration

The generator's directional acceptance is:

```
z = -0.25 + a.bias + fit + shared + drift        bias ~ N(0, 0.7)
p = sigmoid(z)                                   shared ~ N(0, 0.45)
```

and the second-meeting probability is:

```
p2 = sigmoid(0.15 + a.second_bias + shared + 0.4·[goal agrees])   second_bias ~ N(0, 0.5)
```

**Neither contains a demographic term. Neither contains an age, gender or zone term.**
The only systematic signal is soft-field agreement, weighted per variant.

What to measure:

1. **Per-direction reliability diagrams** for P(a accepts b), stratified by actor
   gender, age band, zone, scenario family, and day block. Report calibration slope,
   intercept, log loss and Brier **with CIs**: not eyeballed plots.
2. **Calibration under change.** This is the sharp one. `shift` reweights the soft
   fields (`relationship_pace` 0.4 → 0.8, `lifestyle` 0.25 → −0.25,
   `conversations` 0.2 → 0.5) and `drift` applies −0.5 from day 35. Your offline prior
   is fitted on stationary data and *must* go stale. Measure the drift in calibration
   error by day block and by family. This is "test under changing conditions" made
   concrete, and it is the honest explanation for why §6.5's online correction did
   nothing: it was refitting toward a prior that was already the problem.
3. **The Brier decomposition.** Split Brier into calibration + refinement +
   irreducible. Because `bias ~ N(0, 0.7)` is per-member and unobservable, a
   substantial share of directional variation is *unforecastable in principle*. An
   analysis-only estimate of that irreducible floor (you already do analysis-only
   oracle work in §3 and §6.5) tells you how much calibration error is yours and how
   much is the world's. That reframes "the model is only AUC 0.598" from an
   embarrassment into a bound.
4. **Don't multiply directions.** You already measured the joint at 0.2538 against a
   product of fitted directionals of 0.2297 (ratio 1.105). Report the induced joint
   bias from naive multiplication as a small calibration table. It's a two-line
   result that shows you know why you modelled the joint.

### 5.2 Allocation disparities: the finding is already visible

I ran a structural probe (no policy, no rollout): for each member under complete
disclosure, does at least one feasible partner exist? 10 seeds × 200 members,
grouped by observable attribute. **Fraction of members with ≥1 feasible partner:**

| Group | development | cold start | sparse |
|---|---:|---:|---:|
| **gender** man | 0.66 | 0.66 | 0.33 |
| **gender** woman | 0.67 | 0.70 | 0.33 |
| **gender** non-binary | 0.61 | 0.67 | 0.29 |
| **age** 21–27 | 0.64 | 0.63 | 0.29 |
| **age** 28–34 | 0.70 | 0.72 | 0.35 |
| **age** 35–40 | 0.66 | 0.72 | 0.38 |
| **age** 41–46 | 0.64 | 0.65 | 0.30 |
| **zone_a** | **0.78** | 0.79 | n/a |
| **zone_b** | 0.59 | 0.64 | n/a |
| **zone_c** | 0.38 | 0.36 | n/a |
| **zone_d** | **0.25** | 0.30 | n/a |
| **has_children** no / yes | 0.68 / **0.52** | 0.69 / 0.58 | 0.34 / 0.27 |
| **smoking** no / occasionally / yes | 0.71 / **0.52** / **0.52** | 0.71 / 0.58 / 0.57 | 0.38 / **0.19** / **0.16** |

Three things fall out immediately.

**(a) Gender and age are flat.** 0.61–0.70 across gender, 0.63–0.72 across age bands.
That is your **negative control**: it demonstrates the audit has power and isn't
just manufacturing disparities. Lead with it.

**(b) Zone, smoking and children show large gaps with no demographic term anywhere.**
zone_a 0.78 vs zone_d 0.25: a 3.1× gap in who is introducible at all. Smokers
0.52 vs non-smokers 0.71. Parents 0.52 vs 0.68. And the mechanism is entirely
*legitimate*: it is members' own stated preferences meeting other members' stated
preferences. `partner_smoking='no_smoking'` is a coin flip, so smokers lose half the
pool; same for `partner_children`. Zone is worse because zones are drawn 60/23/12/05,
so zone_d has 5% of the pool and cross-zone acceptance only exists for the 30% who
listed a second zone.

**(c) Therefore the disparity is mostly not the policy's fault, and you must not
"fix" it.** Fixing zone_d's 0.25 would mean overriding `acceptable_zones`, i.e.
violating stated preferences and hard eligibility. The email says explicitly:
*"preserve stated preferences and hard eligibility constraints."* A team that reports
"we found a 3× geographic disparity and declined to correct it, because the
correction would require introducing people to partners they stated they don't
accept" is a team that understood the assignment.

### 5.3 The deliverable: a four-way decomposition

Report, for each group, and separately for each scenario family:

1. **Eligibility supply**: P(member has ≥1 feasible partner). A property of the
   world. Not the policy's.
2. **Clarification allocation**: ask units per *askable* member, by group. This one
   **is** the policy's, and it's where I expect a real finding (below).
3. **Realised access**: served/introducible ratio, plus mean, median and 90th-percentile
   first-introduction wait, computed **among members who actually have a feasible
   partner**. Reporting wait times over the whole pool would just re-measure supply.
4. **Outcome parity**: P(MSMI | introduced) by group. Predicted flat. This is the
   falsification test: if it's flat, the policy isn't inducing outcome disparity; if
   it isn't, something in the ranking is.

### 5.4 The part that *is* fixable, and it's a genuine contribution

Here is the one place I think your policy is actively making the disparity worse,
and it's a direct consequence of your own best idea.

Your unlock-value ask rule ranks members by expected unlock:

- `P(pass)` for `acceptable_zones` is **1.000 same-zone and 0.0756 cross-zone**
  (your own Appendix B.3, "a blocked cross-zone pair carries roughly 1/13 of the
  unlock probability of a blocked same-zone pair").
- So a zone_d member is ranked near the bottom of the ask queue, essentially always.

Meanwhile your §6.6 shows the askable population saturates by day 15–20 in
development: the budget stops binding long before the horizon. **So the ranking
isn't buying you throughput; it's only choosing the order.** A member who is
already disadvantaged by the constraint graph gets asked last, and gets asked last
*for a reason that is downstream of the same disadvantage*. That is a compounding
allocation disparity that is entirely policy-controllable and, at current coverage,
should cost you nothing in MSMI.

**Two cheap candidate remedies, to be tested as paired ablations:**

- **Round-robin / fairness floor**: reserve a fixed share of the daily 12 units for
  the least-recently-asked eligible members.
- **Saturation-aware relaxation**: once the askable population is exhausted (the
  day-15–20 plateau you already detect), spend residual budget by longest-wait-first
  instead of by unlock value. Costs nothing, because the budget is already slack.

Both are testable against the frozen config on identical worlds. Prediction: **MSMI
unchanged, tail waiting time for zone_c/zone_d and smokers reduced.** If that holds
you have a result that is simultaneously a fairness contribution, a
"who gets left waiting" deliverable, and *free* on the primary metric. That is the
best available Round 2 finding, and it costs 2 arms.

### 5.5 Instrumentation warning

None of §5.3 can be recovered retroactively. **Modify the harness now** to log, per
member per episode: group attributes, ask units received, day of first ask, day of
first introduction, served flag, and feasible-degree at day 0. Every episode you run
before that change is a wasted episode for the disparity audit.

---

## 6. Engineering: the parts that can sink you regardless of the science

From the email: *"a working implementation with source code and a reproducible
environment."* Your §8.2 already lists these; I'd reorder by risk.

1. **The reproducibility push (§1).** Blocks everything.
2. **JSON protocol adapter.** Round 1 ran in-process. Round 2 will not. Wrap the
   frozen policy behind the organisers' protocol and handle the explicit failure
   modes you already flagged: empty population, empty feasible graph, zero remaining
   budget, all members busy. Budget real time here: this is where submissions die.
3. **Container.** Measure against the real limits: 10 s, 2 cores, 2 GiB image, **1 MiB
   carried memory**. Your §4.5 says "we will verify the serialised size before Round
   2", do it early, because the carried state (coefficient vector + feature buffer +
   counters) is the thing most likely to blow the cap. Publish the measured numbers,
   and label them as container-mode timings, not in-process.
4. **Slim the runtime.** `requirements.txt` currently pulls networkx + numpy +
   scikit-learn + matplotlib. At inference you need **stdlib + networkx only**:
   ship the fitted prior as static coefficients in JSON (no sklearn), and keep
   matplotlib dev-only. networkx is pure Python and small; the rest is dead weight in
   a 2 GiB image and a cold-start budget.
5. **The O(n²) pass.** 19,900 `eligibility()` calls per phase is fine (~0.1 s/day
   measured). The real cost is `observe()` deep-copying every member every call.
   Worth one profiling pass, but I don't expect it to be binding.
6. **Row-level machine-readable output** for all four required comparisons, on
   identical seeds, pinned with SHA-256, you already promised this in §8.2.

---

## 7. The narrative: ship the simple thing

The email says: *"If a simpler method works as well, explain what the comparison
taught you."*

Look at what your own §6 killed: unlock-value targeting (null), the fitted prior
(actively harmful, −0.125), online adaptation (0/60/0), residual soft asks (+0.017,
p = 0.961), and per §4.1 the two things that *did* move the score were fixing a
sign-coding bug and switching to a general-graph matcher.

So the simplest configuration that survives your own evidence is:

> **supplied `baseline_asks` + signed core-4 weights + global max-weight matching**
> = `defaultask_core4_maxw`, **0.483**

versus the elaborate winner at **0.592 (unconfirmed, best-of-17)**.

My prediction for the fresh-seed confirmation: **0.592 regresses to roughly 0.50–0.55**,
at which point it is statistically indistinguishable from the simple config, and the
defensible submission is the simple one.

That is a much stronger story than defending 0.592:

- It is what the evidence supports.
- It is falsifiable and pre-registrable.
- It converts four null results from "things that didn't work" into "the reason we
  shipped something simple", which is exactly what "explain what the comparison
  taught you" is asking for.
- It reallocates the entire complexity budget to the three things the organisers
  actually asked about: confirmation, interactions, and calibration/disparity.

The risk is real: if 0.592 holds up at 40+ fresh seeds, you ship it and say so. Commit
to the decision rule in advance and let the data decide.

---

## 8. Suggested sequencing

| # | Task | Depends on | Notes |
|---|---|---|---|
| 0 | Resolve the reproducibility gap (§1) | n/a | **Blocking.** Push or re-scope. |
| 1 | Read the official protocol spec; confirm per-day vs per-episode invocation | problem statement | Determines the 10 s budget meaning |
| 2 | Instrument harness for the disparity audit (§5.5) | 1 | Do before any new episode |
| 3 | Fix the resampling unit; recompute all CIs over seed blocks (§3.1) | 0 | May revise Round 1 per-family claims |
| 4 | Commit the pre-registration: frozen config, seed generator, decision rule | 0, 3 | Hash and push **before** running |
| 5 | Fresh-seed confirmation, 2 arms × 40 seeds (§3.2) | 4 | ~4 min at 16 workers |
| 6 | 2×2×2 factorial, 40 seeds (§4.1) | 4 | ~21 min at 16 workers |
| 7 | Batching ablation H4 (§4.3) | 4 | ~10 min |
| 8 | Fairness-floor / saturation-aware ask ablations (§5.4) | 6 | 2 arms |
| 9 | Directional calibration suite (§5.1) | 6 | Reuses logged data |
| 10 | Container + protocol adapter + timing (§6) | 1 | Start early, run in parallel |
| 11 | Short technical report + machine-readable bundle | all | |

Tasks 5–9 total roughly **5,000–6,000 episodes ≈ 10 core-hours**: under an hour on
16 workers. The binding constraints are human: task 0 and task 10.

---

## 9. Open questions for you

1. **Does the working machine still exist** with `scripts/` (13 files), the two
   `assets/*.json`, and the Round 1 result artifacts? This decides route (A) vs (B)
   in §1 and it blocks everything else.
2. **What compute do you have for Round 2**: cores, and can it run overnight? This
   sets whether 40 or 60 fresh seeds is the right number.
3. **Problem statement / submission protocol**: still to come. I specifically need
   the invocation contract (one call per day vs one per episode) and the exact
   container limits.
4. **Round 2 deadline**: the email says it comes separately. Once it lands we can
   back-solve the schedule in §8.

---

### Appendix: the two probes I actually ran

Everything else in this document is read off the note, the repo or `kit.py`.

1. **World sharing (§3.1).** Called `generate(seed=101, n=200, variant=v)` for all six
   variants and compared member IDs and attributes. No policy, no rollout, no episode.
   Result in the §3.1 table.
2. **Group eligibility supply (§5.2).** For seeds 101–1010 × {development, cold_start,
   sparse}: wrote each member's `truth` into `fields` (analysis-only, the same
   operation your §3 performs), enumerated all 19,900 pairs per world, and counted
   members with degree ≥ 1. Result in the §5.2 table.

Neither consumed a seed that should be reserved for the fresh-seed confirmation, and
neither ran a decision policy.
