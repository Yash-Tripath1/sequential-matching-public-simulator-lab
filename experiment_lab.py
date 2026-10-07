"""Small, auditable policy experiments for the Sequential Matching Problem.

This is a research sandbox, separate from the organisers' starter repo. Policies
receive only Simulator.observe() states and their own memory; they never inspect
world['truth']. Bulk runs are in-process for speed, so they do not test the
official subprocess/Docker limits. See experiment_log.md for protocol/results.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import random
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
# Prefer the byte-for-byte bundled public simulator so the zip is self-contained.
# The sibling path remains as a convenient fallback for the original workspace.
STARTER_CANDIDATES = [PROJECT_DIR / "starter", PROJECT_DIR.parent / "sequential-matching-problem"]
STARTER = next((p for p in STARTER_CANDIDATES if (p / "kit.py").is_file()), STARTER_CANDIDATES[0])
sys.path.insert(0, str(STARTER))

import kit  # noqa: E402
import networkx as nx  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.gaussian_process import GaussianProcessRegressor  # noqa: E402
from sklearn.gaussian_process.kernels import ConstantKernel, RBF  # noqa: E402

CORE = ["relationship_goal", "relationship_pace", "lifestyle", "conversations"]
SOFT = list(kit.SOFT)


def pair_key(a: str, b: str) -> str:
    x, y = sorted((a, b))
    return x + "|" + y


def assignment_key(a: str, b: str, day: int) -> str:
    return f"{day}|{pair_key(a, b)}"


def relation(a: dict, b: dict, field: str) -> int:
    va = a.get("fields", {}).get(field)
    vb = b.get("fields", {}).get(field)
    if va is None or vb is None:
        return 0
    return 1 if va == vb else -1


def known_equal(a: dict, b: dict, field: str) -> float:
    va = a.get("fields", {}).get(field)
    vb = b.get("fields", {}).get(field)
    return 1.0 if va is not None and vb is not None and va == vb else 0.0


def pair_context(a: dict, b: dict, day: int) -> list[float]:
    """Features from the *observable* state at the time this pair is considered."""
    x = []
    for field in SOFT:
        va = a.get("fields", {}).get(field)
        vb = b.get("fields", {}).get(field)
        both = va is not None and vb is not None
        x.append(1.0 if both and va == vb else (-1.0 if both else 0.0))
        x.append(1.0 if both else 0.0)
    x.extend([
        abs(int(a["age"]) - int(b["age"])) / 25.0,
        1.0 if a.get("zone") == b.get("zone") else 0.0,
        min(max(day, 0), 60) / 60.0,
    ])
    return x


def pattern_arm(a: dict, b: dict) -> str:
    """A coarse contextual arm: goal relation plus other core matches/knownness."""
    g = relation(a, b, "relationship_goal")
    g_code = "?" if g == 0 else ("=" if g == 1 else "!")
    other = [relation(a, b, f) for f in CORE[1:]]
    k = sum(v != 0 for v in other)
    m = sum(v == 1 for v in other)
    return f"{g_code}:{m}:{k}"


def feasible_edges(state: dict):
    members = [m for m in state["members"] if m.get("available")]
    past = {
        pair_key(i["user_a"], i["user_b"])
        for i in state.get("introductions", [])
    }
    for a, b in itertools.combinations(members, 2):
        key = pair_key(a["member_id"], b["member_id"])
        if key in past:
            continue
        if kit.eligibility(a, b)["status"] == "feasible":
            yield a, b


def weighted_matching(edges):
    graph = nx.Graph()
    for a, b, weight in edges:
        w = float(weight)
        if not math.isfinite(w) or w <= 0:
            continue
        graph.add_edge(a["member_id"], b["member_id"], weight=w)
    if not graph.number_of_edges():
        return []
    pairs = nx.max_weight_matching(graph, maxcardinality=False, weight="weight")
    normalized = sorted(tuple(sorted(p)) for p in pairs)
    return [list(pair) for pair in normalized]


def greedy_soft_score(a: dict, b: dict, weights: dict[str, float] | None = None) -> float:
    weights = weights or {f: 1.0 for f in SOFT}
    score = 0.01
    for field, weight in weights.items():
        score += float(weight) * known_equal(a, b, field)
    return score


def random_feasible(state: dict, seed: int = 17) -> list[list[str]]:
    candidates = [m for m in state["members"] if m.get("available")]
    past = {pair_key(i["user_a"], i["user_b"]) for i in state.get("introductions", [])}
    edges = []
    for a, b in itertools.combinations(candidates, 2):
        key = pair_key(a["member_id"], b["member_id"])
        if key not in past and kit.eligibility(a, b)["status"] == "feasible":
            edges.append((a, b))
    random.Random(seed + int(state["day"])).shuffle(edges)
    used, result = set(), []
    for a, b in edges:
        ids = {a["member_id"], b["member_id"]}
        if not used.intersection(ids):
            result.append(sorted(ids))
            used.update(ids)
    return result


def mature_primary_label(intro: dict, feedback: list[dict], day: int) -> int | None:
    """Return the official MSMI outcome only after it is observable/mature."""
    iid = intro["introduction_id"]
    events = [e for e in feedback if e.get("introduction_id") == iid]
    responses = [e for e in events if e.get("event") == "introduction_response"]
    if len(responses) < 2:
        if day >= int(intro["response_deadline_day"]):
            return 0
        return None
    if not all(e.get("value") == "yes" for e in responses):
        return 0

    dates = [e for e in events if e.get("event") == "date_happened"]
    if not dates:
        return 0 if day >= int(intro["assigned_day"]) + 30 else None
    date = dates[0]
    if date.get("value") is not True:
        return 0
    second = [e for e in events if e.get("event") == "second_meeting_intention"]
    if len(second) < 2:
        return None
    date_day = int(date["occurred_day"])
    success = all(
        e.get("value") == "yes"
        and e.get("occurred_day") is not None
        and int(e["occurred_day"]) - date_day <= 3
        for e in second
    )
    return 1 if success else 0


class Policy:
    name = "base"

    def __init__(self, seed: int = 0, weights: dict[str, float] | None = None, kappa: float = 0.5):
        self.seed = seed
        self.weights = weights or {f: 1.0 for f in SOFT}
        self.kappa = kappa
        self.pending_features: dict[str, list[float]] = {}
        self.pending_arms: dict[str, str] = {}
        self.intro_features: dict[str, list[float]] = {}
        self.intro_arms: dict[str, str] = {}
        self.seen_outcomes: set[str] = set()
        self.gp_x: list[list[float]] = []
        self.gp_y: list[int] = []
        self.arm_counts: dict[str, list[int]] = defaultdict(lambda: [1, 1])  # alpha, beta

    def asks(self, state: dict) -> list[dict]:
        return kit.baseline_asks(state)

    def _bind_and_update(self, state: dict) -> None:
        by_key = {}
        for intro in state.get("introductions", []):
            key = assignment_key(intro["user_a"], intro["user_b"], int(intro["assigned_day"]))
            if key in self.pending_features:
                self.intro_features[intro["introduction_id"]] = self.pending_features[key]
                self.intro_arms[intro["introduction_id"]] = self.pending_arms[key]
        feedback = state.get("feedback", [])
        for intro in state.get("introductions", []):
            iid = intro["introduction_id"]
            if iid in self.seen_outcomes or iid not in self.intro_features:
                continue
            label = mature_primary_label(intro, feedback, int(state["day"]))
            if label is not None:
                self.gp_x.append(self.intro_features[iid])
                self.gp_y.append(int(label))
                arm = self.intro_arms[iid]
                if label:
                    self.arm_counts[arm][0] += 1
                else:
                    self.arm_counts[arm][1] += 1
                self.seen_outcomes.add(iid)

    def pairs(self, state: dict) -> list[list[str]]:
        return kit.baseline_match(state)


class GreedyPolicy(Policy):
    name = "greedy"


class NoAskPolicy(GreedyPolicy):
    name = "no_ask"

    def asks(self, state: dict) -> list[dict]:
        return []


class RandomPolicy(Policy):
    name = "random_feasible"

    def pairs(self, state: dict) -> list[list[str]]:
        return random_feasible(state)


class MaxWeightPolicy(Policy):
    name = "max_weight_similarity"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.weights = self.weights or {f: 1.0 for f in SOFT}

    def pairs(self, state: dict) -> list[list[str]]:
        edges = []
        for a, b in feasible_edges(state):
            edges.append((a, b, greedy_soft_score(a, b, self.weights)))
        return weighted_matching(edges)


class ThompsonPatternPolicy(Policy):
    name = "thompson_pattern"

    def pairs(self, state: dict) -> list[list[str]]:
        self._bind_and_update(state)
        rng = random.Random(self.seed * 100003 + int(state["day"]) * 97)
        samples = {
            arm: rng.betavariate(alpha, beta)
            for arm, (alpha, beta) in self.arm_counts.items()
        }
        edge_rows = list(feasible_edges(state))
        edge_by_key = {pair_key(a["member_id"], b["member_id"]): (a, b) for a, b in edge_rows}
        edges = []
        for a, b in edge_rows:
            arm = pattern_arm(a, b)
            alpha, beta = self.arm_counts[arm]
            value = samples.get(arm)
            if value is None:
                value = rng.betavariate(alpha, beta)
            # Tiny deterministic preference breaks ties among pairs in one pattern.
            value += 1e-5 * greedy_soft_score(a, b, {f: 1.0 for f in CORE})
            edges.append((a, b, value))
        result = weighted_matching(edges)
        for pair in result:
            key = assignment_key(pair[0], pair[1], int(state["day"]))
            a, b = edge_by_key[pair_key(pair[0], pair[1])]
            self.pending_arms[key] = pattern_arm(a, b)
            self.pending_features[key] = pair_context(a, b, int(state["day"]))
        return result


class GpUcbPolicy(Policy):
    """Online GP surrogate over pair contexts, scoring MSMI outcomes with UCB."""
    def pairs(self, state: dict) -> list[list[str]]:
        self._bind_and_update(state)
        edges_raw = list(feasible_edges(state))
        if not edges_raw:
            return []
        edge_by_key = {pair_key(a["member_id"], b["member_id"]): (a, b) for a, b in edges_raw}
        x_candidates = [pair_context(a, b, int(state["day"])) for a, b in edges_raw]
        if len(self.gp_y) >= 4 and len(set(self.gp_y)) > 1:
            X = np.asarray(self.gp_x, dtype=float)
            y = np.asarray(self.gp_y, dtype=float)
            kernel = ConstantKernel(0.12, constant_value_bounds="fixed") * RBF(
                length_scale=1.5, length_scale_bounds="fixed"
            )
            model = GaussianProcessRegressor(kernel=kernel, alpha=0.08, optimizer=None, normalize_y=False)
            model.fit(X, y)
            mu, sigma = model.predict(np.asarray(x_candidates, dtype=float), return_std=True)
            scores = mu + self.kappa * sigma
        else:
            # Cold-start fallback: weak similarity prior plus explicit uncertainty bonus.
            prior = np.asarray([greedy_soft_score(a, b, {f: 1.0 for f in CORE}) for a, b in edges_raw])
            prior = prior / max(float(prior.max()), 1.0)
            scores = 0.02 * prior + self.kappa * 0.05
        edges = [(a, b, max(0.0, float(s))) for (a, b), s in zip(edges_raw, scores)]
        result = weighted_matching(edges)
        for pair in result:
            key = assignment_key(pair[0], pair[1], int(state["day"]))
            a, b = edge_by_key[pair_key(pair[0], pair[1])]
            self.pending_features[key] = pair_context(a, b, int(state["day"]))
            self.pending_arms[key] = pattern_arm(a, b)
        return result


class WeightedMaxPolicy(Policy):
    name = "weighted_max_matching"

    def pairs(self, state: dict) -> list[list[str]]:
        edges = []
        for a, b in feasible_edges(state):
            # GA tunes these four soft-field weights. Missing fields earn no match credit.
            score = 0.001 + sum(
                float(self.weights.get(f, 0.0)) * known_equal(a, b, f)
                for f in CORE
            )
            edges.append((a, b, score))
        return weighted_matching(edges)


class PotentialAskPolicy(MaxWeightPolicy):
    """Simple VOI-inspired heuristic: clarify constraints for high-potential members."""
    name = "potential_ask"

    def asks(self, state: dict) -> list[dict]:
        available = [m for m in state["members"] if m.get("available")]
        budget = int(state.get("ask_budget_remaining", 12))
        ranked = []
        for m in available:
            status = m.get("field_status", {})
            fields = m.get("fields", {})
            has_missing_hard = any(fields.get(f) is None for f in kit.HARD)
            declined_hard = any(status.get(f) == "declined" for f in kit.HARD)
            if not has_missing_hard or declined_hard or budget < 3:
                continue
            potential = 0.0
            for other in available:
                if other["member_id"] == m["member_id"]:
                    continue
                check = kit.eligibility(m, other)["status"]
                if check == "infeasible":
                    continue
                known_fit = sum(known_equal(m, other, f) for f in CORE)
                potential += 0.2 + known_fit
            ranked.append((potential, m["member_id"]))
        ranked.sort(key=lambda x: (-x[0], x[1]))
        asks, spent = [], 0
        for potential, member_id in ranked:
            if spent + 3 > budget or potential <= 0:
                break
            asks.append({"member_id": member_id, "field": "constraints"})
            spent += 3
        return asks


class PotentialAskGreedyPolicy(PotentialAskPolicy):
    """Ablation: keep potential-based asks, restore the organisers' greedy matcher."""
    name = "potential_ask_greedy"

    def pairs(self, state: dict) -> list[list[str]]:
        return kit.baseline_match(state)


POLICY_FACTORIES = {
    "greedy": lambda **kw: GreedyPolicy(**kw),
    "no_ask": lambda **kw: NoAskPolicy(**kw),
    "random_feasible": lambda **kw: RandomPolicy(**kw),
    "max_weight_similarity": lambda **kw: MaxWeightPolicy(**kw),
    "core_max_matching": lambda **kw: WeightedMaxPolicy(**kw),
    "thompson_pattern": lambda **kw: ThompsonPatternPolicy(**kw),
    "gp_mean": lambda **kw: GpUcbPolicy(kappa=0.0, **kw),
    "gp_ucb": lambda **kw: GpUcbPolicy(kappa=1.0, **kw),
    "potential_ask": lambda **kw: PotentialAskPolicy(**kw),
    "potential_ask_greedy": lambda **kw: PotentialAskGreedyPolicy(**kw),
}


def run_episode(method: str, seed: int, variant: str, weights: dict[str, float] | None = None,
                timeout_seconds: float = 30.0) -> dict:
    """In-process public-simulator rollout; same observations/actions/score as evaluator."""
    world = kit.generate(seed=seed, n=200, pool_id="evaluation", variant=variant)
    sim = kit.Simulator(world)
    factory = POLICY_FACTORIES.get(method)
    if method == "ga_tuned":
        policy = WeightedMaxPolicy(seed=seed, weights=weights or {})
    elif factory:
        policy = factory(seed=seed, weights=weights or {})
    else:
        raise KeyError(method)

    started = time.perf_counter()
    for _ in range(60):
        state = sim.observe()
        asks = policy.asks(state)
        sim.resolve_asks(asks)
        state = sim.observe()
        pairs = policy.pairs(state)
        sim.advance(pairs)
    policy_seconds = time.perf_counter() - started

    arrived = {m["member_id"]: m["arrived_day"] for m in world["members"] if m["arrived_day"] <= 59}
    for _ in range(40):
        sim.advance([])
    result = sim.metrics()
    first = {}
    for intro in sim.introductions:
        for member in (intro["user_a"], intro["user_b"]):
            first.setdefault(member, intro["assigned_day"])
    waits = [first[i] - arrived[i] for i in first]
    denom = len(arrived)
    result.update({
        "method": method,
        "seed": seed,
        "variant": variant,
        "valid": True,
        "arrived_members": denom,
        "msmi_per_100_arrived_members": 100 * result["mutual_second_meeting_intention"] / max(1, denom),
        "served_members": len(first),
        "unserved_members": denom - len(first),
        "coverage": len(first) / max(1, denom),
        "mutual_acceptances_per_100": 100 * result["mutual_acceptances"] / max(1, denom),
        "mean_first_intro_wait_days": statistics.mean(waits) if waits else None,
        "policy_wall_seconds_in_process": policy_seconds,
        "ask_cost": result["ask_cost"],
    })
    return result


def summarize(rows: list[dict]) -> dict:
    out = {}
    methods = sorted({r["method"] for r in rows})
    for method in methods:
        mr = [r for r in rows if r["method"] == method]
        by_variant = {}
        for variant in sorted({r["variant"] for r in mr}):
            vr = [r for r in mr if r["variant"] == variant]
            by_variant[variant] = {
                "episodes": len(vr),
                "msmi_per_100_mean": statistics.mean(r["msmi_per_100_arrived_members"] for r in vr),
                "msmi_per_100_sd": statistics.stdev(r["msmi_per_100_arrived_members"] for r in vr) if len(vr) > 1 else 0.0,
                "coverage_mean": statistics.mean(r["coverage"] for r in vr),
                "mutual_acceptances_per_100_mean": statistics.mean(r["mutual_acceptances_per_100"] for r in vr),
                "ask_cost_mean": statistics.mean(r["ask_cost"] for r in vr),
                "wait_days_mean": statistics.mean([r["mean_first_intro_wait_days"] or 0 for r in vr]),
            }
        overall = {
            "episodes": len(mr),
            "equal_variant_weight_msmi_per_100": statistics.mean(v["msmi_per_100_mean"] for v in by_variant.values()),
            "mean_coverage": statistics.mean(r["coverage"] for r in mr),
            "mean_mutual_acceptances_per_100": statistics.mean(r["mutual_acceptances_per_100"] for r in mr),
            "mean_ask_cost": statistics.mean(r["ask_cost"] for r in mr),
            "mean_in_process_policy_seconds": statistics.mean(r["policy_wall_seconds_in_process"] for r in mr),
        }
        out[method] = {"overall": overall, "by_variant": by_variant}
    return out


def save_results(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"release": kit.VERSION, "runner": "in_process_public_simulator_pilot",
               "rows": rows, "summary": summarize(rows)}
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--methods", default="greedy,no_ask,random_feasible,max_weight_similarity,thompson_pattern,gp_mean,gp_ucb,potential_ask")
    p.add_argument("--seeds", default="101,202")
    p.add_argument("--variants", default="all")
    p.add_argument("--output", default=str(PROJECT_DIR / "results/pilot.json"))
    args = p.parse_args()
    methods = args.methods.split(",")
    seeds = [int(s) for s in args.seeds.split(",")]
    variants = list(kit.generate.__defaults__[-1:] or [])  # unused; keep CLI explicit below
    variants = ["development", "sparse", "cold_start", "delayed", "shift", "drift"] if args.variants == "all" else args.variants.split(",")
    rows = []
    output = Path(args.output)
    for method in methods:
        for variant in variants:
            for seed in seeds:
                t0 = time.time()
                try:
                    row = run_episode(method, seed, variant)
                except Exception as exc:
                    row = {"method": method, "seed": seed, "variant": variant, "valid": False, "error": repr(exc)}
                rows.append(row)
                # Save after each episode so an interrupted exploratory run still leaves a record.
                save_results(rows, output)
                print(json.dumps({"method": method, "seed": seed, "variant": variant,
                                  "valid": row.get("valid"), "msmi": row.get("msmi_per_100_arrived_members"),
                                  "seconds": round(time.time()-t0, 2)}), flush=True)
    print(json.dumps(summarize(rows), indent=2))


if __name__ == "__main__":
    main()
