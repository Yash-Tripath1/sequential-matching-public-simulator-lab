#!/usr/bin/env python3
"""Round 2 · "who gets left waiting" instrumented harness.

Complements the fresh-seed confirmation and the interaction factorial by
answering the third organiser question: allocation disparities and waiting
times, decomposed into (a) the world's eligibility supply and (b) what the
policy actually did.

Arms (all on identical worlds; arms 2-4 share one matcher so the ask rule is
the ONLY thing that varies):

  greedy         official baseline: kit.baseline_asks + kit.baseline_match
  potential_ask  incumbent: potential-ranked hard asks + max-weight matching
  waitfloor      NEW: 50% of daily ask slots reserved for longest-waiting
                 askable members, rest potential-ranked + same matcher
  oldest_first   NEW: every ask slot longest-waiting first + same matcher

Per-member attributes (gender, age band, zone, has_children, smoking) and the
complete-disclosure feasible degree are read from the world AFTER the episode
and are ANALYSIS ONLY. No policy ever sees them.

Episode loop mirrors official evaluate.py::episode exactly: 60 decision days
(ask phase then match phase), then 40 follow-up days with no actions.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Locate the organiser kit: next to this file first, then ./official/, then
# the original sandbox layout, then whatever KIT_DIR points at. Portable.
_kit_candidates = [HERE, HERE / "official", HERE.parent / "work" / "official"]
if os.environ.get("KIT_DIR"):
    _kit_candidates.insert(0, Path(os.environ["KIT_DIR"]).expanduser().resolve())
OFFICIAL = next((q for q in _kit_candidates if (q / "kit.py").exists()), HERE)
sys.path.insert(0, str(OFFICIAL))
sys.path.insert(0, str(OFFICIAL / "starter"))

import kit  # noqa: E402
from kit import HARD, SOFT, generate  # noqa: E402

import networkx as nx  # noqa: E402

VARIANTS = ("development", "sparse", "cold_start", "delayed", "shift", "drift")
ARMS = ("greedy", "no_ask", "random_feasible", "potential_ask", "potential_core4", "potential_ask_greedy", "waitfloor", "oldest_first", "signed_potential", "no_ask_random", "disagreement_aware")
CORE = ("relationship_goal", "relationship_pace", "lifestyle", "conversations")
CD_CACHE: dict[tuple[int, str], dict[str, int]] = {}


# --------------------------------------------------------------------------
# observation-only helpers
# --------------------------------------------------------------------------
def known_equal(a: dict, b: dict, field: str) -> float:
    """UNSIGNED agreement, matching experiment_lab.known_equal exactly.

    The Round 1 incumbent's ask-ranking scores a known disagreement as 0.0,
    not -1.0. An earlier build used the SIGNED variant (experiment_lab.relation)
    here; that is a different policy and scored 0.367 on the Round 1 seeds
    against the incumbent's 0.525. Kept as `signed_potential` for the record.
    """
    va, vb = a["fields"].get(field), b["fields"].get(field)
    return 1.0 if va is not None and vb is not None and va == vb else 0.0


def signed_relation(a: dict, b: dict, field: str) -> float:
    """SIGNED variant: +1 agree, -1 known disagreement, 0 unknown."""
    va, vb = a["fields"].get(field), b["fields"].get(field)
    if va is None or vb is None:
        return 0.0
    return 1.0 if va == vb else -1.0


def askable(state: dict) -> list[dict]:
    """Members worth asking, following kit.baseline_asks' own filter."""
    out = []
    for m in state["members"]:
        if not m.get("available"):
            continue
        fields = m.get("fields", {})
        status = m.get("field_status", {})
        if not any(fields.get(f) is None for f in HARD):
            continue
        if any(status.get(f) == "declined" for f in HARD):
            continue
        out.append(m)
    return out


def potential_scores(available: list[dict]) -> dict[str, float]:
    """Incumbent's VOI-inspired heuristic: sum of soft fit over non-infeasible others."""
    scores = {}
    for m in available:
        potential = 0.0
        for other in available:
            if other["member_id"] == m["member_id"]:
                continue
            if kit.eligibility(m, other)["status"] == "infeasible":
                continue
            potential += 0.2 + sum(known_equal(m, other, f) for f in CORE)
        scores[m["member_id"]] = potential
    return scores


def max_weight_pairs_core4(state: dict) -> list[list[str]]:
    """Maximum-weight matching on the CORE FOUR soft fields only.

    This reconstructs Round 1's `lab_potential_core4_maxw` (reported 0.592,
    best-of-17, code never committed). Round 1's note describes the winner as
    potential-ranked asking with max-weight matching restricted to the four
    core soft fields. If that reconstruction is right, this arm should score
    near 0.592 on Round 1's seeds; on 120 fresh seeds it will show whether the
    reported value survives selection.
    """
    members = [m for m in state["members"] if m.get("available")]
    past = {tuple(sorted((i["user_a"], i["user_b"]))) for i in state.get("introductions", [])}
    graph = nx.Graph()
    for a, b in itertools.combinations(members, 2):
        key = tuple(sorted((a["member_id"], b["member_id"])))
        if key in past:
            continue
        if kit.eligibility(a, b)["status"] != "feasible":
            continue
        score = 0.01 + sum(
            1 for f in CORE
            if a["fields"].get(f) is not None and a["fields"].get(f) == b["fields"].get(f)
        )
        graph.add_edge(a["member_id"], b["member_id"], weight=float(score))
    if not graph.number_of_edges():
        return []
    return [sorted(pair) for pair in nx.max_weight_matching(graph, maxcardinality=False, weight="weight")]


def max_weight_pairs(state: dict) -> list[list[str]]:
    """General-graph maximum-weight matching on 7-soft agreement count."""
    members = [m for m in state["members"] if m.get("available")]
    past = {tuple(sorted((i["user_a"], i["user_b"]))) for i in state.get("introductions", [])}
    graph = nx.Graph()
    for a, b in itertools.combinations(members, 2):
        key = tuple(sorted((a["member_id"], b["member_id"])))
        if key in past:
            continue
        if kit.eligibility(a, b)["status"] != "feasible":
            continue
        score = 0.01 + sum(
            1 for f in SOFT
            if a["fields"].get(f) is not None and a["fields"].get(f) == b["fields"].get(f)
        )
        graph.add_edge(a["member_id"], b["member_id"], weight=float(score))
    if not graph.number_of_edges():
        return []
    return [sorted(p) for p in nx.max_weight_matching(graph, maxcardinality=False, weight="weight")]


# --------------------------------------------------------------------------
# ask rules
# --------------------------------------------------------------------------
def asks_greedy(state: dict) -> list[dict]:
    return kit.baseline_asks(state)


def _slots(state: dict) -> int:
    return max(0, int(state.get("ask_budget_remaining", 12)) // 3)


def _by_potential_signed(state: dict, slots: int) -> list[dict]:
    """Signed-relation variant of the incumbent ranking (kept for the record)."""
    if slots <= 0:
        return []
    available = [m for m in state["members"] if m.get("available")]
    cand = {m["member_id"] for m in askable(state)}
    by_id = {m["member_id"]: m for m in available if m["member_id"] in cand}
    scores = {}
    for mid, m in by_id.items():
        p = 0.0
        for other in available:
            if other["member_id"] == mid:
                continue
            if kit.eligibility(m, other)["status"] == "infeasible":
                continue
            p += 0.2 + sum(signed_relation(m, other, f) for f in CORE)
        scores[mid] = p
    ranked = sorted(((scores[mid], mid) for mid in by_id), key=lambda t: (-t[0], t[1]))
    out = []
    for score, mid in ranked:
        if len(out) >= slots or score <= 0:
            break
        out.append({"member_id": mid, "field": "constraints"})
    return out


def _by_potential(state: dict, slots: int) -> list[dict]:
    if slots <= 0:
        return []
    available = [m for m in state["members"] if m.get("available")]
    scores = potential_scores(available)
    cand = {m["member_id"] for m in askable(state)}
    ranked = sorted(
        ((scores.get(mid, 0.0), mid) for mid in cand),
        key=lambda t: (-t[0], t[1]),
    )
    out, spent = [], 0
    for score, mid in ranked:
        if spent >= slots or score <= 0:
            break
        out.append({"member_id": mid, "field": "constraints"})
        spent += 1
    return out


def _wait_key(state: dict):
    """Longest-waiting first: descending (day - arrived_day), tie-break on id."""
    day = int(state["day"])

    def key(mid_arrived):
        mid, arrived = mid_arrived
        return (-(day - arrived), mid)

    return key


def asks_potential(state: dict) -> list[dict]:
    return _by_potential(state, _slots(state))


def asks_oldest_first(state: dict) -> list[dict]:
    """Simplest possible rule: spend every slot on whoever has waited longest."""
    slots = _slots(state)
    if slots <= 0:
        return []
    cand = [(m["member_id"], int(m["arrived_day"])) for m in askable(state)]
    cand.sort(key=_wait_key(state))
    return [{"member_id": mid, "field": "constraints"} for mid, _ in cand[:slots]]


def asks_waitfloor(state: dict, reserve_fraction: float = 0.5) -> list[dict]:
    """Half the slots go to the longest-waiting askable members; the rest keep
    the incumbent's potential ranking. Identical matcher to `potential_ask`."""
    slots = _slots(state)
    if slots <= 0:
        return []
    reserved = int(math.floor(slots * reserve_fraction))
    if slots >= 2:
        reserved = max(1, reserved)
    cand = [(m["member_id"], int(m["arrived_day"])) for m in askable(state)]
    cand.sort(key=_wait_key(state))
    chosen = [mid for mid, _ in cand[:reserved]]
    taken = set(chosen)
    remaining = slots - len(chosen)
    if remaining > 0:
        for ask in _by_potential(state, len(cand)):
            if ask["member_id"] in taken:
                continue
            chosen.append(ask["member_id"])
            taken.add(ask["member_id"])
            remaining -= 1
            if remaining == 0:
                break
    return [{"member_id": mid, "field": "constraints"} for mid in chosen]


def asks_none(state: dict) -> list[dict]:
    """Supplied `no-clarification` baseline: never spend the ask budget."""
    return []


def pairs_random_feasible(state: dict) -> list[list[str]]:
    """Supplied `random-feasible` baseline: feasible pairs in a deterministic
    shuffle seeded from the day, then a greedy maximal matching. Seeded from
    the day only - no world seed is reachable through the policy protocol,
    which is exactly how the organiser's own baseline does it."""
    import random

    members = [m for m in state.get("members", []) if m.get("available")]
    if len(members) < 2:
        return []
    past = {tuple(sorted((i["user_a"], i["user_b"])))
            for i in state.get("introductions", [])}
    edges = []
    for a, b in itertools.combinations(members, 2):
        key = tuple(sorted((a["member_id"], b["member_id"])))
        if key not in past and kit.eligibility(a, b)["status"] == "feasible":
            edges.append(sorted(key))
    random.Random(17 + int(state.get("day", 0))).shuffle(edges)
    used: set = set()
    out = []
    for pair in edges:
        if used.isdisjoint(pair):
            out.append(pair)
            used.update(pair)
    return out


def pairs_disagreement_aware(state):
    """greedy's own matching rule, with one change: known disagreements count.

    kit.baseline_match (kit.py:217) scores a pair by counting soft fields where
    both members are known and EQUAL. A field where both are known and DIFFERENT
    contributes 0 -- exactly the same as a field neither member has disclosed.
    Section 5.12 measured what that blind spot costs: among pairs with zero known
    agreements, empirical acceptance falls from 0.492 with zero known
    disagreements to 0.288 with four.

    This is the smallest fix that could work -- one changed line of scoring, the
    same ask rule, the same greedy edge selection -- so any difference against
    `greedy` is attributable to the disagreement term alone and nothing else.

    Weight is -1.0 per known disagreement, chosen a priori: the measured
    acceptance drop per disagreement (~0.05) is the same order as the gain per
    additional agreement (~0.03-0.13), so equal weighting is the neutral choice.
    No tuning was performed on any seed.
    """
    members = [m for m in state["members"] if m["available"]]
    past = {tuple(sorted((i["user_a"], i["user_b"])))
            for i in state.get("introductions", [])}
    edges = []
    for a, b in itertools.combinations(members, 2):
        key = tuple(sorted((a["member_id"], b["member_id"])))
        if key in past or kit.eligibility(a, b)["status"] != "feasible":
            continue
        agree = disagree = 0
        for k in SOFT:
            va, vb = a["fields"].get(k), b["fields"].get(k)
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


ASK_RULES = {
    "greedy": asks_greedy,
    "no_ask": asks_none,
    "random_feasible": asks_greedy,
    "potential_ask": asks_potential,
    "potential_core4": asks_potential,
    "potential_ask_greedy": asks_potential,
    "waitfloor": asks_waitfloor,
    "oldest_first": asks_oldest_first,
    "no_ask_random": asks_none,
    "signed_potential": lambda st: _by_potential_signed(st, _slots(st)),
    "disagreement_aware": asks_greedy,
}
MATCHERS = {
    "greedy": kit.baseline_match,
    "no_ask": kit.baseline_match,
    "random_feasible": pairs_random_feasible,
    "potential_ask": max_weight_pairs,
    "potential_core4": max_weight_pairs_core4,
    "potential_ask_greedy": kit.baseline_match,
    "waitfloor": max_weight_pairs,
    "oldest_first": max_weight_pairs,
    "no_ask_random": pairs_random_feasible,
    "signed_potential": max_weight_pairs,
    "disagreement_aware": pairs_disagreement_aware,
}


# --------------------------------------------------------------------------
# complete-disclosure degree (ANALYSIS ONLY, never seen by any policy)
# --------------------------------------------------------------------------
def cd_degree(seed: int, variant: str) -> dict[str, int]:
    key = (seed, variant)
    if key in CD_CACHE:
        return CD_CACHE[key]
    world = generate(seed, 200, "evaluation", variant)
    ms = world["members"]
    for m in ms:  # disclose every non-declined field; declined stays declined
        for f, v in m["truth"].items():
            if m["field_status"].get(f) != "declined":
                m["fields"][f] = v
    deg = {m["member_id"]: 0 for m in ms}
    for a, b in itertools.combinations(ms, 2):
        if kit.eligibility(a, b)["status"] == "feasible":
            deg[a["member_id"]] += 1
            deg[b["member_id"]] += 1
    CD_CACHE[key] = deg
    return deg


# --------------------------------------------------------------------------
# episode
# --------------------------------------------------------------------------
def age_band(age: int) -> str:
    if age <= 27:
        return "21-27"
    if age <= 34:
        return "28-34"
    if age <= 40:
        return "35-40"
    return "41-46"


def run_episode(seed: int, variant: str, arm: str) -> dict:
    world = generate(seed, 200, "evaluation", variant)
    sim = kit.Simulator(world)
    ask_rule, matcher = ASK_RULES[arm], MATCHERS[arm]

    ask_units: dict[str, int] = {}
    first_ask_day: dict[str, int] = {}
    askable_by_day: list[int] = []
    asks_by_day: list[int] = []

    t0 = time.time()
    for _ in range(60):
        state = sim.observe()
        asks = ask_rule(state)
        askable_by_day.append(len(askable(state)))
        asks_by_day.append(len(asks))
        sim.resolve_asks(asks)
        for a in asks:
            mid = a["member_id"]
            ask_units[mid] = ask_units.get(mid, 0) + (3 if a["field"] == "constraints" else 1)
            first_ask_day.setdefault(mid, int(state["day"]))
        state = sim.observe()
        sim.advance(matcher(state))

    arrived = {
        m["member_id"]: m["arrived_day"]
        for m in sim.observe()["members"]
        if m["arrived_day"] <= 59
    }
    for _ in range(40):
        sim.advance([])

    result = sim.metrics()
    first: dict[str, int] = {}
    n_intros: dict[str, int] = {}
    for intro in sim.introductions:
        for member in (intro["user_a"], intro["user_b"]):
            first.setdefault(member, intro["assigned_day"])
            n_intros[member] = n_intros.get(member, 0) + 1
    waits = sorted(first[i] - arrived[i] for i in first)
    result.update(
        valid=True,
        arrived_members=len(arrived),
        msmi_per_100_arrived_members=100 * result["mutual_second_meeting_intention"] / max(1, len(arrived)),
        served_members=len(first),
        unserved_members=len(arrived) - len(first),
        coverage=len(first) / max(1, len(arrived)),
        mutual_acceptances_per_100=100 * result["mutual_acceptances"] / max(1, len(arrived)),
        first_introduction_wait_days=waits,
    )

    deg = cd_degree(seed, variant)
    truth = {m["member_id"]: m for m in world["members"]}
    members = []
    for mid, arr in sorted(arrived.items()):
        src = truth[mid]
        f = first.get(mid)
        members.append({
            "mid": mid,
            "gender": src["gender"],
            "band": age_band(src["age"]),
            "zone": src["zone"],
            "kids": bool(src["truth"]["has_children"]),
            "smoke": src["truth"]["smoking"],
            "arr": int(arr),
            "exit": int(src["exit_day"]),
            "deg": int(deg.get(mid, 0)),
            "asks": int(ask_units.get(mid, 0)),
            "fad": first_ask_day.get(mid),
            "fid": f,
            "wait": (f - arr) if f is not None else None,
            "nin": int(n_intros.get(mid, 0)),
        })

    return {
        "seed": seed, "variant": variant, "arm": arm,
        "seconds": round(time.time() - t0, 2),
        "metrics": {k: result[k] for k in (
            "assignments", "mutual_acceptances", "dates", "mutual_second_meeting_intention",
            "missing_feedback", "ask_cost", "arrived_members",
            "msmi_per_100_arrived_members", "coverage", "mutual_acceptances_per_100",
            "served_members", "unserved_members")},
        "waits": waits,
        "askable_by_day": askable_by_day,
        "asks_by_day": asks_by_day,
        "members": members,
    }


# --------------------------------------------------------------------------
# runner
# --------------------------------------------------------------------------
def job(args):
    seed, variant, arm = args
    try:
        return run_episode(seed, variant, arm)
    except Exception as exc:  # keep the batch alive; record the failure
        return {"seed": seed, "variant": variant, "arm": arm, "valid": False,
                "error": repr(exc), "metrics": None}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--seeds", default="")
    p.add_argument("--variants", default=",".join(VARIANTS))
    p.add_argument("--arms", default=",".join(ARMS))
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--out", default=str(HERE / "out"))
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()

    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    variants = [v for v in args.variants.split(",") if v.strip()]
    arms = [a for a in args.arms.split(",") if a.strip()]

    work = [(s, v, a) for s in seeds for v in variants for a in arms]
    if args.limit:
        work = work[: args.limit]

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    ep_path = outdir / "episodes.jsonl"
    mem_path = outdir / "members.jsonl"

    done = set()
    if ep_path.exists():
        for line in ep_path.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("metrics") is not None:
                done.add((r["seed"], r["variant"], r["arm"]))
        # member rows are rewritten wholesale from the surviving episode records
    todo = [w for w in work if w not in done]
    print(f"[waitlab] {len(done)} done, {len(todo)} to run, {args.workers} workers", flush=True)

    if args.smoke:
        for w in todo:
            r = job(w)
            print(json.dumps({k: r[k] for k in ("seed", "variant", "arm")}
                             | {"sec": r.get("seconds"), "msmi": (r.get("metrics") or {}).get("msmi_per_100_arrived_members"),
                                "err": r.get("error")}), flush=True)
        return 0

    if todo:
        import multiprocessing as mp
        with mp.Pool(args.workers) as pool, open(ep_path, "a") as fh:
            for i, r in enumerate(pool.imap_unordered(job, todo, chunksize=1), 1):
                fh.write(json.dumps(r, allow_nan=False) + "\n")
                fh.flush()
                if i % 20 == 0 or i == len(todo):
                    print(f"[waitlab] {i}/{len(todo)}  last={r['seed']}/{r['variant']}/{r['arm']}"
                          f"  {r.get('seconds', '?')}s", flush=True)

    # rewrite the member-level file from every valid episode on disk
    with open(mem_path, "w") as fh:
        for line in ep_path.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("metrics") is None:
                continue
            head = {"seed": r["seed"], "variant": r["variant"], "arm": r["arm"]}
            for m in r["members"]:
                fh.write(json.dumps(head | m, allow_nan=False) + "\n")
    print(f"[waitlab] wrote {ep_path} and {mem_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
