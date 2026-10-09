"""JSON-protocol version of the four-phase hybrid for the official evaluator.

Schedule: greedy (days 0-14), contextual Thompson (15-29), GP-UCB (30-44),
greedy (45-59). Potential-ask clarification is held fixed in every phase.
All learned data are assignment-time observable features and mature visible feedback.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "starter"))
import kit  # noqa: E402
import networkx as nx  # noqa: E402

CORE = ["relationship_goal", "relationship_pace", "lifestyle", "conversations"]
SOFT = list(kit.SOFT)
INFERENCE_SEED = 17


def pair_key(a, b):
    x, y = sorted((a, b))
    return x + "|" + y


def assignment_key(a, b, day):
    return f"{day}|{pair_key(a, b)}"


def relation(a, b, field):
    va = a.get("fields", {}).get(field)
    vb = b.get("fields", {}).get(field)
    if va is None or vb is None:
        return 0
    return 1 if va == vb else -1


def known_equal(a, b, field):
    va = a.get("fields", {}).get(field)
    vb = b.get("fields", {}).get(field)
    return 1.0 if va is not None and vb is not None and va == vb else 0.0


def soft_score(a, b, fields=None):
    fields = fields or SOFT
    return 0.01 + sum(known_equal(a, b, f) for f in fields)


def pattern_arm(a, b):
    g = relation(a, b, "relationship_goal")
    g_code = "?" if g == 0 else ("=" if g == 1 else "!")
    other = [relation(a, b, f) for f in CORE[1:]]
    known = sum(v != 0 for v in other)
    matches = sum(v == 1 for v in other)
    return f"{g_code}:{matches}:{known}"


def pair_context(a, b, day):
    x = []
    for field in SOFT:
        va = a.get("fields", {}).get(field)
        vb = b.get("fields", {}).get(field)
        both = va is not None and vb is not None
        x.extend([1.0 if both and va == vb else (-1.0 if both else 0.0), 1.0 if both else 0.0])
    x.extend([
        abs(int(a["age"]) - int(b["age"])) / 25.0,
        1.0 if a.get("zone") == b.get("zone") else 0.0,
        min(max(day, 0), 60) / 60.0,
    ])
    return x


def potential_asks(state):
    available = [m for m in state.get("members", []) if m.get("available")]
    budget = int(state.get("ask_budget_remaining", 12))
    ranked = []
    for m in available:
        fields = m.get("fields", {})
        status = m.get("field_status", {})
        if not any(fields.get(f) is None for f in kit.HARD):
            continue
        if any(status.get(f) == "declined" for f in kit.HARD) or budget < 3:
            continue
        potential = 0.0
        for other in available:
            if other["member_id"] == m["member_id"]:
                continue
            if kit.eligibility(m, other)["status"] == "infeasible":
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


def feasible_edges(state):
    members = [m for m in state.get("members", []) if m.get("available")]
    past = {pair_key(i["user_a"], i["user_b"]) for i in state.get("introductions", [])}
    for a, b in itertools.combinations(members, 2):
        if pair_key(a["member_id"], b["member_id"]) in past:
            continue
        if kit.eligibility(a, b)["status"] == "feasible":
            yield a, b


def weighted_matching(edges):
    graph = nx.Graph()
    for a, b, weight in edges:
        w = float(weight)
        if math.isfinite(w) and w > 0:
            graph.add_edge(a["member_id"], b["member_id"], weight=w)
    if not graph.number_of_edges():
        return []
    chosen = nx.max_weight_matching(graph, maxcardinality=False, weight="weight")
    return [list(p) for p in sorted(tuple(sorted(pair)) for pair in chosen)]


def mature_primary_label(intro, feedback, day):
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
    if date.get("value") is not True or int(date["occurred_day"]) - int(intro["assigned_day"]) > 30:
        return 0
    second = [e for e in events if e.get("event") == "second_meeting_intention"]
    if len(second) < 2:
        return None
    date_day = int(date["occurred_day"])
    return int(all(
        e.get("value") == "yes"
        and e.get("occurred_day") is not None
        and int(e["occurred_day"]) - date_day <= 3
        for e in second
    ))


def initial_memory():
    return {
        "v": 1,
        "seed": INFERENCE_SEED,
        "pending_features": {}, "pending_arms": {},
        "intro_features": {}, "intro_arms": {},
        "seen_outcomes": [], "gp_x": [], "gp_y": [], "arm_counts": {},
    }


def normalize_memory(memory):
    if not isinstance(memory, dict) or memory.get("v") != 1:
        return initial_memory()
    base = initial_memory()
    base.update(memory)
    # Defensive defaults for missing keys in hand-constructed requests.
    for key in ("pending_features", "pending_arms", "intro_features", "intro_arms", "arm_counts"):
        if not isinstance(base.get(key), dict):
            base[key] = {}
    if not isinstance(base.get("seen_outcomes"), list):
        base["seen_outcomes"] = []
    if not isinstance(base.get("gp_x"), list):
        base["gp_x"] = []
    if not isinstance(base.get("gp_y"), list):
        base["gp_y"] = []
    return base


def bind_and_update(state, memory):
    introductions = state.get("introductions", [])
    for intro in introductions:
        key = assignment_key(intro["user_a"], intro["user_b"], int(intro["assigned_day"]))
        iid = intro["introduction_id"]
        if key in memory["pending_features"] and iid not in memory["intro_features"]:
            memory["intro_features"][iid] = memory["pending_features"].pop(key)
            memory["intro_arms"][iid] = memory["pending_arms"].pop(key, "?:0:0")
    seen = set(memory["seen_outcomes"])
    feedback = state.get("feedback", [])
    for intro in introductions:
        iid = intro["introduction_id"]
        if iid in seen or iid not in memory["intro_features"]:
            continue
        label = mature_primary_label(intro, feedback, int(state["day"]))
        if label is None:
            continue
        memory["gp_x"].append(memory["intro_features"][iid])
        memory["gp_y"].append(int(label))
        arm = memory["intro_arms"].get(iid, "?:0:0")
        counts = memory["arm_counts"].setdefault(arm, [1, 1])
        counts[0 if label else 1] += 1
        seen.add(iid)
    memory["seen_outcomes"] = sorted(seen)


def strategy_for_day(day):
    if day < 15:
        return "greedy"
    if day < 30:
        return "thompson"
    if day < 45:
        return "gp_ucb"
    return "greedy"


def thompson_scores(rows, day, memory):
    rng = random.Random(int(memory.get("seed", INFERENCE_SEED)) * 100003 + day * 97)
    counts = memory["arm_counts"]
    samples = {
        arm: rng.betavariate(int(ab[0]), int(ab[1]))
        for arm, ab in counts.items()
    }
    scores = []
    for a, b in rows:
        arm = pattern_arm(a, b)
        alpha, beta = counts.get(arm, [1, 1])
        score = samples.get(arm)
        if score is None:
            score = rng.betavariate(int(alpha), int(beta))
        scores.append(score + 1e-5 * soft_score(a, b, CORE))
    return scores


def gp_ucb_scores(rows, day, memory):
    # Imports are lazy because only the middle phase uses the GP.
    gp_x, gp_y = memory["gp_x"], memory["gp_y"]
    if len(gp_y) >= 4 and len(set(gp_y)) > 1:
        import numpy as np
        from sklearn.gaussian_process import GaussianProcessRegressor
        from sklearn.gaussian_process.kernels import ConstantKernel, RBF
        X = np.asarray(gp_x, dtype=float)
        y = np.asarray(gp_y, dtype=float)
        candidates = np.asarray([pair_context(a, b, day) for a, b in rows], dtype=float)
        kernel = ConstantKernel(0.12, constant_value_bounds="fixed") * RBF(
            length_scale=1.5, length_scale_bounds="fixed"
        )
        model = GaussianProcessRegressor(
            kernel=kernel, alpha=0.08, optimizer=None, normalize_y=False,
            random_state=int(memory.get("seed", INFERENCE_SEED)),
        )
        model.fit(X, y)
        mu, sigma = model.predict(candidates, return_std=True)
        return mu + sigma
    prior = [soft_score(a, b, CORE) for a, b in rows]
    scale = max(max(prior, default=0.0), 1.0)
    return [0.02 * p / scale + 0.05 for p in prior]


def decide(request):
    state = request["state"]
    memory = normalize_memory(request.get("memory"))
    if request.get("phase") == "ask":
        return {"asks": potential_asks(state), "memory": memory}
    if request.get("phase") != "match":
        raise ValueError("phase must be ask or match")
    bind_and_update(state, memory)
    day = int(state["day"])
    strategy = strategy_for_day(day)
    rows = list(feasible_edges(state))
    if not rows:
        return {"pairs": [], "memory": memory}
    row_by_key = {pair_key(a["member_id"], b["member_id"]): (a, b) for a, b in rows}

    if strategy == "greedy":
        pairs = kit.baseline_match(state)
    elif strategy == "thompson":
        scores = thompson_scores(rows, day, memory)
        pairs = weighted_matching([(a, b, float(s)) for (a, b), s in zip(rows, scores)])
    else:
        scores = gp_ucb_scores(rows, day, memory)
        pairs = weighted_matching([(a, b, max(0.0, float(s))) for (a, b), s in zip(rows, scores)])

    for pair in pairs:
        key = assignment_key(pair[0], pair[1], day)
        a, b = row_by_key[pair_key(pair[0], pair[1])]
        memory["pending_features"][key] = pair_context(a, b, day)
        memory["pending_arms"][key] = pattern_arm(a, b)
    return {"pairs": pairs, "memory": memory}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # The public local evaluator always passes this option to a custom policy.
    parser.add_argument("--baseline", choices=["greedy", "no_asks", "random"], default="greedy")
    args = parser.parse_args()
    request = json.load(sys.stdin)
    print(json.dumps(decide(request), allow_nan=False, separators=(",", ":")))
