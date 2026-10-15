#!/usr/bin/env python3
"""Round 2 policy — JSON stdin/stdout adapter (policy interface 1.0.0).

One invocation = one phase of one day. Reads exactly one JSON request from
stdin, writes exactly one JSON object to stdout, exits 0. Diagnostics go to
stderr. Runtime dependencies: Python standard library, `networkx` and the
organisers' public `kit.py`. No numpy, sklearn or matplotlib at inference.

Arms
----
  greedy         official baseline (kit.baseline_asks + kit.baseline_match)
  no_ask         official baseline (no clarification)
  random_feasible official baseline (random feasible matching)
  potential_ask  incumbent: potential-ranked hard asks + max-weight matching
  waitfloor      reserved share of daily ask slots for longest-waiting members
  oldest_first   every ask slot to the longest-waiting askable member

`waitfloor` and `oldest_first` are the Round 2 waiting-time interventions.
Arms 4-6 share ONE matcher (general-graph maximum-weight matching on the
7-soft agreement count), so only the ask rule varies between them.

Hard eligibility is a gate in every arm; nothing here overrides a stated
preference. Declined fields stay unknown and are never imputed. A member with
a declined hard field is never asked and never introduced.

Determinism
-----------
No world seed is present in the protocol request and none is used. Every rule
is a deterministic function of the observation plus a member-ID tie-break.
`networkx.max_weight_matching` was verified to return identical matchings
under PYTHONHASHSEED in {0, 7, 12345} on six complete-disclosure graphs.
"""
from __future__ import annotations

import itertools
import json
import math
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kit import HARD, SOFT, baseline_asks, baseline_match, eligibility  # noqa: E402

# networkx is needed ONLY by the max-weight matcher (potential_ask /
# waitfloor / oldest_first). Import it lazily so the greedy arm runs on the
# standard library alone, which keeps the container dependency-free.
nx = None


def _nx():
    global nx
    if nx is None:
        import networkx as _mod
        nx = _mod
    return nx

CORE = ("relationship_goal", "relationship_pace", "lifestyle", "conversations")
ARMS = ("greedy", "no_ask", "random_feasible", "potential_ask", "waitfloor", "oldest_first",
        "disagreement_aware")
DEFAULT_ARM = "greedy"


# ---------------------------------------------------------------- observation
def known_equal(a: dict, b: dict, field: str) -> float:
    va, vb = a["fields"].get(field), b["fields"].get(field)
    if va is None or vb is None:
        return 0.0
    return 1.0 if va == vb else -1.0


def askable(state: dict) -> list[dict]:
    out = []
    for m in state.get("members", []):
        if not m.get("available"):
            continue
        fields = m.get("fields", {}) or {}
        status = m.get("field_status", {}) or {}
        if not any(fields.get(f) is None for f in HARD):
            continue
        if any(status.get(f) == "declined" for f in HARD):
            continue
        out.append(m)
    return out


def slots(state: dict) -> int:
    try:
        return max(0, int(state.get("ask_budget_remaining", 12)) // 3)
    except (TypeError, ValueError):
        return 0


# ------------------------------------------------------------------ ask rules
def asks_none(state: dict) -> list[dict]:
    return []


def asks_potential_ranked(state: dict, n: int) -> list[dict]:
    """Incumbent heuristic: rank askable members by summed soft fit over the
    members they could still become feasible with."""
    if n <= 0:
        return []
    available = [m for m in state.get("members", []) if m.get("available")]
    cand = askable(state)
    if not cand:
        return []
    scores: dict[str, float] = {}
    by_id = {m["member_id"]: m for m in cand}
    for m in cand:
        potential = 0.0
        for other in available:
            if other["member_id"] == m["member_id"]:
                continue
            if eligibility(m, other)["status"] == "infeasible":
                continue
            potential += 0.2 + sum(known_equal(m, other, f) for f in CORE)
        scores[m["member_id"]] = potential
    ranked = sorted(((scores[mid], mid) for mid in by_id), key=lambda t: (-t[0], t[1]))
    out = []
    for score, mid in ranked:
        if len(out) >= n or score <= 0:
            break
        out.append({"member_id": mid, "field": "constraints"})
    return out


def _by_wait(state: dict, n: int) -> list[str]:
    """Longest-waiting askable members first; tie-break on member id."""
    day = int(state.get("day", 0))
    cand = [(int(m.get("arrived_day", 0)), m["member_id"]) for m in askable(state)]
    cand.sort(key=lambda t: (-(day - t[0]), t[1]))
    return [mid for _, mid in cand[:n]]


def asks_potential(state: dict) -> list[dict]:
    return asks_potential_ranked(state, slots(state))


def asks_oldest_first(state: dict) -> list[dict]:
    return [{"member_id": mid, "field": "constraints"} for mid in _by_wait(state, slots(state))]


def asks_waitfloor(state: dict, reserve_fraction: float = 0.5) -> list[dict]:
    """Half the daily slots go to whoever has waited longest; the rest keep
    the incumbent's potential ranking. Same matcher as `potential_ask`."""
    n = slots(state)
    if n <= 0:
        return []
    reserved = max(1, int(math.floor(n * reserve_fraction))) if n >= 2 else 0
    chosen = _by_wait(state, reserved)
    taken = set(chosen)
    if n - len(chosen) > 0:
        for ask in asks_potential_ranked(state, n):
            if ask["member_id"] in taken:
                continue
            chosen.append(ask["member_id"])
            taken.add(ask["member_id"])
            if len(chosen) >= n:
                break
    return [{"member_id": mid, "field": "constraints"} for mid in chosen[:n]]


# ------------------------------------------------------------------ matchers
def pairs_max_weight(state: dict) -> list[list[str]]:
    """General graph (not bipartite) maximum-weight matching on the 7-soft
    agreement count. Weights are strictly positive: maxcardinality=False lets
    the optimiser trade cardinality against quality, and a non-positive weight
    would make it discard a feasible edge that is merely unlikely."""
    members = [m for m in state.get("members", []) if m.get("available")]
    if len(members) < 2:
        return []
    past = {tuple(sorted((i["user_a"], i["user_b"]))) for i in state.get("introductions", [])}
    graph = _nx().Graph()
    for a, b in itertools.combinations(members, 2):
        key = tuple(sorted((a["member_id"], b["member_id"])))
        if key in past:
            continue
        if eligibility(a, b)["status"] != "feasible":
            continue
        weight = 0.01 + sum(
            1.0 for f in SOFT
            if a["fields"].get(f) is not None and a["fields"].get(f) == b["fields"].get(f)
        )
        graph.add_edge(a["member_id"], b["member_id"], weight=weight)
    if not graph.number_of_edges():
        return []
    return [sorted(p) for p in _nx().max_weight_matching(graph, maxcardinality=False, weight="weight")]


def pairs_greedy_signed(state: dict) -> list[list[str]]:
    """`greedy`'s own edge selection with one change: a known disagreement
    scores -1 instead of 0.

    kit.baseline_match counts only agreements, so "we checked and they clash"
    and "we have no idea" both score zero. REPORT.md sections 5.12 and 5.15
    measure what that costs: among pairs with no known agreements, empirical
    acceptance falls from 0.492 with zero known disagreements to 0.288 with
    four. This is the disclosed candidate of section 5.15.

    It is NOT shipped -- the default arm is and remains `greedy` (section 5.15
    gives the reason: the measured effect is about one seventieth of what the
    organisers' 20-seed assessment can resolve). It is selectable with
    ROUND2_ARM=disagreement_aware purely so the reported result is
    reproducible by anyone who wants to check it.
    """
    members = [m for m in state.get("members", []) if m.get("available")]
    if len(members) < 2:
        return []
    past = {tuple(sorted((i["user_a"], i["user_b"]))) for i in state.get("introductions", [])}
    edges = []
    for a, b in itertools.combinations(members, 2):
        key = tuple(sorted((a["member_id"], b["member_id"])))
        if key in past or eligibility(a, b)["status"] != "feasible":
            continue
        agree = disagree = 0
        for f in SOFT:
            va, vb = a["fields"].get(f), b["fields"].get(f)
            if va is None or vb is None:
                continue          # undisclosed: no information either way
            if va == vb:
                agree += 1
            else:
                disagree += 1
        edges.append((-(agree - disagree), key))
    used: set = set()
    out = []
    for _, pair in sorted(edges):
        if used.isdisjoint(pair):
            out.append(list(pair))
            used.update(pair)
    return out


def pairs_random_feasible(state: dict) -> list[list[str]]:
    """Official `random` baseline: deterministic shuffle, seeded from the day
    only, never from a world seed (none is available in the protocol)."""
    import random

    members = [m for m in state.get("members", []) if m.get("available")]
    if len(members) < 2:
        return []
    past = {tuple(sorted((i["user_a"], i["user_b"]))) for i in state.get("introductions", [])}
    edges = []
    for a, b in itertools.combinations(members, 2):
        key = tuple(sorted((a["member_id"], b["member_id"])))
        if key not in past and eligibility(a, b)["status"] == "feasible":
            edges.append(sorted(key))
    random.Random(17 + int(state.get("day", 0))).shuffle(edges)
    used: set[str] = set()
    out = []
    for pair in edges:
        if used.isdisjoint(pair):
            out.append(pair)
            used.update(pair)
    return out


ASK = {
    "greedy": baseline_asks,
    "no_ask": asks_none,
    "random_feasible": baseline_asks,
    "potential_ask": asks_potential,
    "waitfloor": asks_waitfloor,
    "oldest_first": asks_oldest_first,
    "disagreement_aware": baseline_asks,
}
MATCH = {
    "greedy": baseline_match,
    "no_ask": baseline_match,
    "random_feasible": pairs_random_feasible,
    "potential_ask": pairs_max_weight,
    "waitfloor": pairs_max_weight,
    "oldest_first": pairs_max_weight,
    "disagreement_aware": pairs_greedy_signed,
}


def decide(request: dict, arm: str) -> dict:
    state = request.get("state") or {}
    memory = request.get("memory") or {}
    phase = request.get("phase")

    # Any internal failure degrades to a valid no-op rather than an invalid
    # episode: an invalid assessed episode makes the whole entry ineligible.
    try:
        memory = dict(memory)
        if phase == "ask":
            action = [a for a in ASK.get(arm, asks_waitfloor)(state) if isinstance(a, dict)]
            action = action[: 12 // 3]  # never exceed the daily budget
            memory["asks"] = int(memory.get("asks", 0)) + len(action)
            return {"asks": action, "memory": memory}
        if phase == "match":
            action = [list(p) for p in MATCH.get(arm, pairs_max_weight)(state)]
            memory["pairs"] = int(memory.get("pairs", 0)) + len(action)
            return {"pairs": action, "memory": memory}
    except Exception as exc:  # noqa: BLE001 - deliberate: never emit an invalid batch
        print(f"warn: {arm} {phase} failed: {exc!r}", file=sys.stderr)
        # Falling back is the right safety choice: an invalid episode makes the
        # whole entry ineligible. Falling back SILENTLY is not. The supplied
        # evaluate.py only reads stderr when the child exits non-zero, so a
        # fallback would otherwise be scored as a valid episode with zero
        # introductions and no visible trace. We therefore count fallbacks in
        # `memory`, which the protocol carries across calls and back to the
        # harness, so the count is auditable from the episode record itself.
        memory = dict(memory)
        memory["fallbacks"] = int(memory.get("fallbacks", 0)) + 1
        reasons = list(memory.get("fallback_reasons") or [])
        if len(reasons) < 10:
            reasons.append(f"{arm}/{phase}: {type(exc).__name__}: {exc}")
        memory["fallback_reasons"] = reasons

    # Unknown phase, or a failure above: emit the valid empty action.
    return {"asks": [], "memory": memory} if phase == "ask" else {"pairs": [], "memory": memory}


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", choices=["greedy", "no_asks", "random"], default=None)
    parser.add_argument("--arm", choices=list(ARMS), default=None)
    args = parser.parse_args()

    if args.arm:
        arm = args.arm
    elif os.environ.get("ROUND2_ARM") in ARMS:
        # Lets the organisers' evaluate.py (which only forwards --baseline)
        # select a Round 2 arm: ROUND2_ARM=waitfloor python3 evaluate.py ...
        arm = os.environ["ROUND2_ARM"]
    elif args.baseline == "no_asks":
        arm = "no_ask"
    elif args.baseline == "random":
        arm = "random_feasible"
    elif args.baseline == "greedy":
        arm = "greedy"
    else:
        arm = DEFAULT_ARM

    request = json.load(sys.stdin)
    response = decide(request, arm)
    print(json.dumps(response, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
