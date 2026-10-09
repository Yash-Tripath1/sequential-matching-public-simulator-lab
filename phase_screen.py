"""Quick paired screening of time-phased matching policies.

Uses the unchanged public v1.0 simulator and observable-state-only policy code.
New runs use the same three public seeds and six variants as the checked-in pilot.
This is an exploratory screen, not private evaluation.
"""
from __future__ import annotations

import json
import random
import statistics
import time
from pathlib import Path

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, RBF

import experiment_lab as lab
import kit

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "phase_screen_3seeds.json"
SEEDS = [101, 202, 303]
VARIANTS = ["development", "sparse", "cold_start", "delayed", "shift", "drift"]
METHODS = [
    "potential_ask_thompson",
    "potential_ask_gp_ucb",
    "hybrid_4phase",
    "hybrid_6phase",
    "hybrid_adaptive",
]


def official_mature_primary_label(intro, feedback, day):
    """Label the official MSMI target only when visible and mature.

    Unlike the original exploratory helper, this also enforces the official
    30-day first-date deadline before returning a positive label.
    """
    iid = intro["introduction_id"]
    events = [e for e in feedback if e.get("introduction_id") == iid]
    responses = [e for e in events if e.get("event") == "introduction_response"]
    if len(responses) < 2:
        return 0 if day >= int(intro["response_deadline_day"]) else None
    if not all(e.get("value") == "yes" for e in responses):
        return 0
    dates = [e for e in events if e.get("event") == "date_happened"]
    if not dates:
        return 0 if day >= int(intro["assigned_day"]) + 30 else None
    date = dates[0]
    if date.get("value") is not True:
        return 0
    date_day = int(date["occurred_day"])
    if date_day - int(intro["assigned_day"]) > 30:
        return 0
    second = [e for e in events if e.get("event") == "second_meeting_intention"]
    if len(second) < 2:
        return None
    success = all(
        e.get("value") == "yes"
        and e.get("occurred_day") is not None
        and int(e["occurred_day"]) - date_day <= 3
        for e in second
    )
    return int(success)


class SharedHistoryPhasePolicy(lab.Policy):
    """Potential-ask policy with a shared mature-outcome history across matchers.

    Sharing history matters: a switch from greedy to Thompson/GP must not discard
    observations generated during the earlier phase. Matching always runs on
    currently feasible edges only; hard eligibility is never softened by a score.
    """

    name = "shared_history_phase_policy"

    def __init__(self, seed=0, weights=None, schedule="thompson"):
        super().__init__(seed=seed, weights=weights)
        self.schedule = schedule
        self.asker = lab.PotentialAskPolicy(seed=seed)
        self.soft_weights = {f: 1.0 for f in lab.SOFT}
        self.core_weights = {f: 1.0 for f in lab.CORE}
        self.kappa = 1.0

    def asks(self, state):
        # Keep clarification fixed across matcher comparisons to isolate the
        # effect of the matching schedule.
        return self.asker.asks(state)

    def _strategy_for_day(self, day):
        if self.schedule == "thompson":
            return "thompson"
        if self.schedule == "gp_ucb":
            return "gp_ucb"
        if self.schedule == "four_phase":
            # The proposed sequence: 15 days each of greedy, TS, GP-UCB, greedy.
            return ("greedy" if day < 15 else
                    "thompson" if day < 30 else
                    "gp_ucb" if day < 45 else "greedy")
        if self.schedule == "six_phase":
            # Equal 10-day blocks: G -> TS -> GP -> TS -> GP -> G.
            return ("greedy", "thompson", "gp_ucb", "thompson", "gp_ucb", "greedy")[day // 10]
        if self.schedule == "adaptive":
            # Warm-start; use TS until at least 8 mature labels contain both
            # classes, then GP-UCB; revert to greedy in the final 15 days.
            if day < 15 or day >= 45:
                return "greedy"
            if len(self.gp_y) >= 8 and len(set(self.gp_y)) > 1:
                return "gp_ucb"
            return "thompson"
        raise ValueError(f"Unknown schedule: {self.schedule}")

    def _bind_and_update(self, state):
        # Assignment-time features are bound to visible intro IDs; only feedback
        # released by the simulator is used, and late dates cannot count as MSMI.
        for intro in state.get("introductions", []):
            key = lab.assignment_key(
                intro["user_a"], intro["user_b"], int(intro["assigned_day"])
            )
            if key in self.pending_features:
                self.intro_features[intro["introduction_id"]] = self.pending_features[key]
                self.intro_arms[intro["introduction_id"]] = self.pending_arms[key]
        feedback = state.get("feedback", [])
        for intro in state.get("introductions", []):
            iid = intro["introduction_id"]
            if iid in self.seen_outcomes or iid not in self.intro_features:
                continue
            label = official_mature_primary_label(intro, feedback, int(state["day"]))
            if label is not None:
                self.gp_x.append(self.intro_features[iid])
                self.gp_y.append(int(label))
                arm = self.intro_arms[iid]
                if label:
                    self.arm_counts[arm][0] += 1
                else:
                    self.arm_counts[arm][1] += 1
                self.seen_outcomes.add(iid)

    def _gp_scores(self, rows, day):
        x_candidates = [lab.pair_context(a, b, day) for a, b in rows]
        if len(self.gp_y) >= 4 and len(set(self.gp_y)) > 1:
            X = np.asarray(self.gp_x, dtype=float)
            y = np.asarray(self.gp_y, dtype=float)
            kernel = ConstantKernel(0.12, constant_value_bounds="fixed") * RBF(
                length_scale=1.5, length_scale_bounds="fixed"
            )
            model = GaussianProcessRegressor(
                kernel=kernel, alpha=0.08, optimizer=None,
                normalize_y=False, random_state=self.seed,
            )
            model.fit(X, y)
            mu, sigma = model.predict(np.asarray(x_candidates, dtype=float), return_std=True)
            return mu + self.kappa * sigma
        prior = np.asarray([
            lab.greedy_soft_score(a, b, self.core_weights) for a, b in rows
        ], dtype=float)
        prior = prior / max(float(prior.max()), 1.0)
        return 0.02 * prior + self.kappa * 0.05

    def _thompson_scores(self, rows, day):
        rng = random.Random(self.seed * 100003 + day * 97)
        samples = {
            arm: rng.betavariate(alpha, beta)
            for arm, (alpha, beta) in self.arm_counts.items()
        }
        scores = []
        for a, b in rows:
            arm = lab.pattern_arm(a, b)
            alpha, beta = self.arm_counts[arm]
            value = samples.get(arm)
            if value is None:
                value = rng.betavariate(alpha, beta)
            value += 1e-5 * lab.greedy_soft_score(a, b, self.core_weights)
            scores.append(value)
        return scores

    def pairs(self, state):
        day = int(state["day"])
        self._bind_and_update(state)
        strategy = self._strategy_for_day(day)
        rows = list(lab.feasible_edges(state))
        if not rows:
            return []
        row_by_key = {
            lab.pair_key(a["member_id"], b["member_id"]): (a, b)
            for a, b in rows
        }

        if strategy == "greedy":
            result = kit.baseline_match(state)
        elif strategy == "similarity":
            edges = [
                (a, b, lab.greedy_soft_score(a, b, self.soft_weights))
                for a, b in rows
            ]
            result = lab.weighted_matching(edges)
        elif strategy == "thompson":
            scores = self._thompson_scores(rows, day)
            result = lab.weighted_matching([
                (a, b, float(score)) for (a, b), score in zip(rows, scores)
            ])
        elif strategy == "gp_ucb":
            scores = self._gp_scores(rows, day)
            result = lab.weighted_matching([
                (a, b, max(0.0, float(score)))
                for (a, b), score in zip(rows, scores)
            ])
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        # Store assignment-time observable features for every selected edge,
        # including greedy-phase edges, so later learners can use mature outcomes.
        for pair in result:
            key = lab.assignment_key(pair[0], pair[1], day)
            a, b = row_by_key[lab.pair_key(pair[0], pair[1])]
            self.pending_features[key] = lab.pair_context(a, b, day)
            self.pending_arms[key] = lab.pattern_arm(a, b)
        return result


def register_factories():
    lab.POLICY_FACTORIES.update({
        "potential_ask_thompson": lambda **kw: SharedHistoryPhasePolicy(schedule="thompson", **kw),
        "potential_ask_gp_ucb": lambda **kw: SharedHistoryPhasePolicy(schedule="gp_ucb", **kw),
        "hybrid_4phase": lambda **kw: SharedHistoryPhasePolicy(schedule="four_phase", **kw),
        "hybrid_6phase": lambda **kw: SharedHistoryPhasePolicy(schedule="six_phase", **kw),
        "hybrid_adaptive": lambda **kw: SharedHistoryPhasePolicy(schedule="adaptive", **kw),
    })


def summarize(rows):
    summary = lab.summarize(rows)
    old_path = HERE / "results" / "public_pilot_results.json"
    old = json.loads(old_path.read_text())["rows"]
    for method in METHODS:
        new_map = {(r["variant"], r["seed"]): r for r in rows if r["method"] == method}
        comparisons = {}
        for control in ("potential_ask", "potential_ask_greedy"):
            old_map = {(r["variant"], r["seed"]): r for r in old if r["method"] == control}
            diffs = [
                new_map[k]["msmi_per_100_arrived_members"] - old_map[k]["msmi_per_100_arrived_members"]
                for k in sorted(new_map.keys() & old_map.keys())
            ]
            comparisons[control] = {
                "paired_cases": len(diffs),
                "mean_difference_msmi_per_100": statistics.mean(diffs) if diffs else None,
                "wins_ties_losses": [sum(d > 0 for d in diffs), sum(d == 0 for d in diffs), sum(d < 0 for d in diffs)],
            }
        summary[method]["paired_vs_existing_controls"] = comparisons
    return summary


def main():
    register_factories()
    rows = []
    total = len(METHODS) * len(VARIANTS) * len(SEEDS)
    done = 0
    for method in METHODS:
        for variant in VARIANTS:
            for seed in SEEDS:
                started = time.perf_counter()
                row = lab.run_episode(method, seed, variant)
                if not row.get("valid"):
                    raise RuntimeError(f"Invalid simulator action: {method}/{variant}/{seed}: {row}")
                rows.append(row)
                done += 1
                print(json.dumps({
                    "progress": f"{done}/{total}", "method": method,
                    "variant": variant, "seed": seed,
                    "msmi": row["mutual_second_meeting_intention"],
                    "seconds": round(time.perf_counter() - started, 2),
                }), flush=True)
    payload = {
        "release": kit.VERSION,
        "runner": "in_process_public_simulator_screen",
        "seeds": SEEDS,
        "variants": VARIANTS,
        "methods": METHODS,
        "episodes_per_method": len(SEEDS) * len(VARIANTS),
        "note": "Exploratory public synthetic-simulator screen; not official private evaluation or container validation.",
        "rows": rows,
        "summary": summarize(rows),
    }
    OUT.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    print(f"Wrote {OUT}", flush=True)
    print(json.dumps(payload["summary"], indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
