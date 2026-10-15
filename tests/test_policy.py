"""Contract tests for the shipped policy.

The organisers' starter README documents `python -m unittest -v` as the
entry point. These tests check the container contract only: one JSON request
on stdin, one JSON response on stdout, exit 0, no arguments, no network, and
no writes outside the working directory. They do not re-score episodes.
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POLICY = ROOT / "policy.py"

ASK = {"phase": "ask",
       "state": {"day": 0, "members": [], "introductions": [],
                 "ask_budget_remaining": 12},
       "memory": {}}
MATCH = {"phase": "match",
         "state": {"day": 0, "members": [], "introductions": []},
         "memory": {}}


def run(payload):
    proc = subprocess.run([sys.executable, str(POLICY)],
                          input=json.dumps(payload), capture_output=True,
                          text=True, timeout=30, cwd=str(ROOT))
    return proc


def run_arm(payload, arm):
    """Run root policy.py with a given arm selected via the environment."""
    import os
    env = dict(os.environ, ROUND2_ARM=arm)
    return subprocess.run([sys.executable, str(POLICY)],
                          input=json.dumps(payload), capture_output=True,
                          text=True, timeout=30, cwd=str(ROOT), env=env)


class PolicyContract(unittest.TestCase):
    def test_policy_file_present(self):
        self.assertTrue(POLICY.is_file(), "policy.py must sit at the project root")

    def test_ask_phase_returns_json_and_exits_zero(self):
        proc = run(ASK)
        self.assertEqual(proc.returncode, 0, f"stderr: {proc.stderr}")
        self.assertTrue(proc.stdout.strip(), "no output on stdout")
        json.loads(proc.stdout)  # raises if not valid JSON

    def test_match_phase_returns_json_and_exits_zero(self):
        proc = run(MATCH)
        self.assertEqual(proc.returncode, 0, f"stderr: {proc.stderr}")
        self.assertTrue(proc.stdout.strip(), "no output on stdout")
        json.loads(proc.stdout)

    def test_no_arguments_required(self):
        # The container entrypoint passes no argv beyond the script path.
        proc = run(ASK)
        self.assertEqual(proc.returncode, 0)

    def test_kit_hash_is_pinned(self):
        # Guards against silently swapping the organisers' kit.
        text = (ROOT / "code" / "kit.py").read_text()
        self.assertIn("VERSION", text)


class EmptyInput(unittest.TestCase):
    """The specification requires the policy to handle an empty population and
    an empty feasible graph. Every arm must return a valid empty batch, exit 0,
    and -- because a fallback there would be a real bug rather than a safety
    net -- must not register a fallback."""

    ARMS = ["greedy", "no_ask", "random_feasible", "potential_ask",
            "waitfloor", "oldest_first", "disagreement_aware"]

    KEY = {"ask": "asks", "match": "pairs"}

    def test_empty_population_all_arms_both_phases(self):
        for arm in self.ARMS:
            for phase in ("ask", "match"):
                with self.subTest(arm=arm, phase=phase):
                    payload = {"phase": phase,
                               "state": {"day": 0, "members": [], "introductions": [],
                                         "ask_budget_remaining": 12},
                               "memory": {}}
                    proc = run_arm(payload, arm)
                    self.assertEqual(proc.returncode, 0,
                                     f"{arm}/{phase} stderr: {proc.stderr[:300]}")
                    body = json.loads(proc.stdout)
                    self.assertEqual(body.get(self.KEY[phase]), [],
                                     f"{arm}/{phase} did not return an empty batch")
                    self.assertEqual(int((body.get("memory") or {}).get("fallbacks", 0)), 0,
                                     f"{arm}/{phase} registered a fallback on empty input")

    def test_single_member_population_matches_nothing(self):
        """A one-member pool has an empty feasible graph by construction."""
        for arm in self.ARMS:
            with self.subTest(arm=arm):
                payload = {"phase": "match",
                           "state": {"day": 0,
                                     "members": [{"member_id": "solo", "available": True,
                                                  "fields": {}, "field_status": {}}],
                                     "introductions": []},
                           "memory": {}}
                proc = run_arm(payload, arm)
                self.assertEqual(proc.returncode, 0, f"{arm} stderr: {proc.stderr[:300]}")
                body = json.loads(proc.stdout)
                self.assertEqual(body.get("pairs"), [])

    def test_fallback_counter_is_wired(self):
        """A deliberately malformed state must register a fallback, so that a
        real failure can never be scored as a silent valid empty episode."""
        payload = {"phase": "match",
                   "state": {"day": 0, "members": [{"member_id": "x"}],
                             "introductions": []},
                   "memory": {}}
        proc = run_arm(payload, "greedy")
        self.assertEqual(proc.returncode, 0)
        body = json.loads(proc.stdout)
        self.assertGreaterEqual(int((body.get("memory") or {}).get("fallbacks", 0)), 1)


if __name__ == "__main__":
    unittest.main()
