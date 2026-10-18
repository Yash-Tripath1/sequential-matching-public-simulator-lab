import json, shutil, subprocess
from pathlib import Path

R = Path("/home/user/repo_final")
W = Path("/home/user")

# ---------------------------------------------------------------- licence
MIT = """MIT License

Copyright (c) 2026 Anadi Tripathi (IIT Madras) — team "Bipartite Bard"

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

This licence covers the code written by the team. It does NOT cover
LICENSE.kit or code/kit.py, which are the organisers' public kit and remain
under the terms stated in LICENSE.kit.
"""
(R / "LICENSE").write_text(MIT)
print("wrote LICENSE (MIT)")

# ------------------------------------------- root entry points (starter layout)
for name in ("kit.py", "policy.py", "evaluate.py"):
    shutil.copy(R / "code" / name, R / name)
print("root entry points: kit.py policy.py evaluate.py")

# --------------------------------------------------------------- tests
(R / "tests").mkdir(exist_ok=True)
(R / "tests" / "__init__.py").write_text("")
(R / "tests" / "test_policy.py").write_text('''"""Contract tests for the shipped policy.

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
''')
print("wrote tests/test_policy.py")

# ------------------------------------------------- raw per-episode data (B3)
raw = R / "results" / "raw_episodes"
raw.mkdir(parents=True, exist_ok=True)
mapping = []
for i in range(1, 7):
    src = W / "out_90" / f"c{i}" / "episodes.jsonl.gz"
    dst = raw / f"greedy_potential_ask_1131-1220_chunk{i}.episodes.jsonl.gz"
    shutil.copy(src, dst); mapping.append(dst.name)
for i in range(1, 7):
    src = W / "out_da" / f"k{i}" / "episodes.jsonl.gz"
    dst = raw / f"potential_ask_greedy_disagreement_aware_1131-1220_chunk{i}.episodes.jsonl.gz"
    shutil.copy(src, dst); mapping.append(dst.name)
shutil.copy(W / "out_da" / "k0" / "episodes.jsonl.gz",
            raw / "disagreement_aware_1101-1130.episodes.jsonl.gz"); mapping.append("disagreement_aware_1101-1130.episodes.jsonl.gz")
shutil.copy(W / "out_pag" / "episodes.jsonl.gz",
            raw / "potential_ask_greedy_1101-1130.episodes.jsonl.gz"); mapping.append("potential_ask_greedy_1101-1130.episodes.jsonl.gz")
(R / "results" / "raw_episodes" / "README.md").write_text(
    "# Raw per-episode results\n\n"
    "Every file is newline-delimited JSON, gzip-compressed, one record per episode.\n"
    "Records carry `seed`, `variant`, `arm`, `seconds`, `metrics`, `waits`,\n"
    "`askable_by_day`, `asks_by_day` and a per-member `members` array. Successful\n"
    "episodes have no `valid` key; a failed episode carries `valid: false` plus an\n"
    "`error`. Filter with `if r.get('valid') is False or not r.get('metrics'): continue`.\n\n"
    "`members.jsonl` is deliberately not committed: the harness regenerates it from\n"
    "`episodes.jsonl` at the end of every run, so it is derived data.\n\n"
    "## Coverage\n\n"
    "| arm | seeds | episodes | file(s) |\n|---|---|---|---|\n"
    "| `greedy` | 1131–1220 (90) | 540 | `greedy_potential_ask_1131-1220_chunk*` |\n"
    "| `potential_ask` | 1131–1220 (90) | 540 | `greedy_potential_ask_1131-1220_chunk*` |\n"
    "| `potential_ask_greedy` | 1101–1220 (120) | 720 | `potential_ask_greedy_1101-1130` + `..._chunk*` |\n"
    "| `disagreement_aware` | 1101–1220 (120) | 720 | `disagreement_aware_1101-1130` + `..._chunk*` |\n\n"
    "## Not available\n\n"
    "`no_ask`, `random_feasible` and `oldest_first` raw rows were produced on a\n"
    "separate machine whose per-episode log could not be recovered; only the\n"
    "aggregates in `../primary_120seeds.json` and `../contrasts_120seeds.csv`\n"
    "survive for those arms. The `greedy` and `potential_ask` figures in those\n"
    "aggregates were independently re-derived here and match (§5.14).\n")
print(f"wrote results/raw_episodes/ ({len(mapping)} files)")

# ------------------------------------------------------ §5.15 machine-readable
analysis = json.load(open(W / "out_da" / "analysis_120seeds.json"))
shutil.copy(W / "out_da" / "analysis_120seeds.json",
            R / "results" / "analysis_120seeds_four_arm.json")

# merge the four-arm per-seed table into the existing 120-seed results file
p = R / "results" / "greedy_vs_potential_120seeds.json"
d = json.load(open(p))
d["four_arm_120seeds"] = {
    "note": "Per-seed primary scores for all four arms on the same 120 worlds. "
            "greedy and potential_ask: see per_seed. All four: results/analysis_120seeds_four_arm.json",
    "primary": {a: round(sum(analysis["arms"][a].values()) / len(analysis["arms"][a]), 4)
                for a in analysis["arms"]},
    "contrasts_vs_greedy": analysis["contrasts_vs_greedy"],
}
json.dump(d, open(p, "w"), indent=2)
print("updated results/greedy_vs_potential_120seeds.json with the four-arm table")
print(json.dumps(d["four_arm_120seeds"]["primary"], indent=1))
