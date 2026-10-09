# Independent baseline re-verification — 9 October 2026

**What was run.** The three official baselines (`greedy`, `no_asks`, `random`) were
executed through the organisers' own reference evaluator (`evaluate.py` invoking
`policy.py`, starter release 1.0.0) in trusted-local subprocess mode, for public seeds
101, 202, 303 across all six public scenario families: **54 assessed episodes**.

**Why.** Round 1 note §6.9 claims the lab harness reproduces the reference policy
decision-for-decision. The lab publishes row-level rows for exactly these three seeds in
`results/scaled_factorial_10seeds.json`, so the claim is checkable externally.

**Result.**

- All 54 episodes completed **valid** (no rejected actions, no protocol errors).
- **54/54 episodes are identical** to the lab's published rows, episode-by-episode, on
  assignments, mutual acceptances, dates, MSMI, and coverage.
- Three-seed-subset primary scores (equal-weight family means):

| Baseline | Reference evaluator | Lab factorial rows |
|---|---:|---:|
| `greedy` | 0.389 (14 events) | 0.389 (14 events) |
| `no_ask` | 0.111 (4 events) | 0.111 (4 events) |
| `random_feasible` | 0.278 (10 events) | 0.278 (10 events) |

These match the pilot table in `experiment_log.md` for the same three seeds.

**Scope and caveats.** This is a subprocess-protocol verification of the supplied
baselines on public seeds — it is **not** Docker/container-mode validation and it does not
re-run the Round 1 harness's 17-configuration factorial (whose scripts are pending push;
see `ROUND1_NOTE.md`). Raw output: `results/reference_verification_3seeds.json`.
