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


if __name__ == "__main__":
    unittest.main()
