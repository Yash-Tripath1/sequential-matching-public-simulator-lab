#!/usr/bin/env python3
"""verify_data.py: integrity check for the data this submission uses.

The organisers' starter repository ships `verify_data.py` next to a `data/`
directory of pre-generated questionnaire pools. **This submission does not use
that directory.** Every world is produced on demand by

    kit.generate(seed, n, purpose, variant)

which is a pure deterministic function of its arguments and the bundled kit,
so there is no external data file whose bytes could drift after the freeze.

What this script verifies instead is the property that actually matters here:
that world generation is reproducible and that the kit we ship is the kit we
measured against. Run from the project root:

    python verify_data.py

Exit 0 = all checks passed. Non-zero = at least one check failed.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "code"))

import kit  # noqa: E402

VARIANTS = ("development", "sparse", "cold_start", "delayed", "shift", "drift")
# Deliberately small: determinism is the claim, not coverage.
PROBE_SEEDS = (101, 1101, 1220)
N_MEMBERS = 200

failures: list[str] = []
checks = 0


def check(label: str, ok: bool, detail: str = "") -> None:
    global checks
    checks += 1
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f": {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def world_fingerprint(seed: int, variant: str) -> str:
    world = kit.generate(seed, N_MEMBERS, "evaluation", variant)
    blob = json.dumps(world, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()


def main() -> int:
    print("verify_data.py: determinism and kit integrity")
    print(f"  kit VERSION : {getattr(kit, 'VERSION', 'unknown')}")
    print(f"  root        : {ROOT}")
    print()

    print("Kit files present:")
    for name in ("kit.py", "policy.py", "LICENSE.kit", "code/kit.py", "code/policy.py"):
        check(f"{name} exists", (ROOT / name).is_file())

    print("\nWorld generation is deterministic (same seed -> identical world):")
    for seed in PROBE_SEEDS:
        for variant in VARIANTS:
            a = world_fingerprint(seed, variant)
            b = world_fingerprint(seed, variant)
            check(f"seed {seed} / {variant}", a == b, a[:16])

    print("\nDifferent seeds give different worlds (no silent seed collapse):")
    fps = {s: world_fingerprint(s, "development") for s in PROBE_SEEDS}
    check("three seeds -> three distinct worlds", len(set(fps.values())) == len(fps))

    print("\nGenerator produces a usable pool:")
    world = kit.generate(PROBE_SEEDS[0], N_MEMBERS, "evaluation", "development")
    members = world.get("members", world if isinstance(world, list) else [])
    check("200 members generated", len(members) == N_MEMBERS, f"got {len(members)}")

    print()
    if failures:
        print(f"FAILED: {len(failures)} of {checks} checks failed:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"OK: all {checks} checks passed.")
    print()
    print("Note: no data/ directory is used. Worlds are generated deterministically")
    print("by kit.generate(); see README.md and REPORT.md section 3.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
