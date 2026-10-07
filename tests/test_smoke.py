"""Fast structural smoke test against the bundled public simulator."""
import unittest
from pathlib import Path

import experiment_lab


class PublicSimulatorSmokeTest(unittest.TestCase):
    def test_bundled_simulator_is_selected(self):
        self.assertEqual(experiment_lab.kit.VERSION, "1.0.0")
        self.assertEqual(Path(experiment_lab.STARTER).resolve(),
                         (Path(__file__).resolve().parents[1] / "starter").resolve())

    def test_greedy_episode_is_valid(self):
        row = experiment_lab.run_episode("greedy", seed=101, variant="development")
        self.assertTrue(row["valid"])
        self.assertEqual(row["msmi_per_100_arrived_members"], 0.5)
        self.assertEqual(row["coverage"], 0.46)


if __name__ == "__main__":
    unittest.main()
