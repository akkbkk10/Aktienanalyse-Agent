from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class CliHelpSmokeTests(unittest.TestCase):
    def _run_help(self, script_name: str) -> str:
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / script_name), "--help"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return " ".join(result.stdout.lower().split())

    def _run_invalid_option(self, script_name: str) -> str:
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / script_name), "--definitely-invalid-option"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        return f"{result.stdout}\n{result.stderr}".lower()

    def test_run_v1_0_demo_help_is_discoverable(self) -> None:
        output = self._run_help("run_v1_0_demo.py")

        self.assertIn("usage", output)
        self.assertIn("reports-dir", output)
        self.assertIn("nvda", output)
        self.assertIn("amd", output)
        self.assertIn("tsmc", output)
        self.assertIn("deterministic", output)
        self.assertIn("never fetches live data", output)
        self.assertIn("does not produce price targets", output)
        self.assertIn("investment advice", output)
        self.assertIn("trading actions", output)

    def test_run_analysis_help_is_discoverable(self) -> None:
        output = self._run_help("run_analysis.py")

        self.assertIn("usage", output)
        self.assertIn("ticker", output)
        self.assertIn("reports-dir", output)
        self.assertIn("generate-report", output)
        self.assertIn("run-dcf", output)
        self.assertIn("never fetches live data", output)
        self.assertIn("does not produce price targets", output)
        self.assertIn("investment advice", output)
        self.assertIn("trading actions", output)

    def test_run_batch_analysis_help_is_discoverable(self) -> None:
        output = self._run_help("run_batch_analysis.py")

        self.assertIn("usage", output)
        self.assertIn("batch", output)
        self.assertIn("ticker", output)
        self.assertIn("reports-dir", output)
        self.assertIn("independently", output)
        self.assertIn("never fetches live data", output)
        self.assertIn("does not produce price targets", output)
        self.assertIn("investment advice", output)
        self.assertIn("trading actions", output)

    def test_run_v1_0_demo_invalid_option_fails_clearly(self) -> None:
        output = self._run_invalid_option("run_v1_0_demo.py")

        self.assertIn("usage", output)
        self.assertIn("error", output)
        self.assertIn("unrecognized arguments", output)

    def test_run_analysis_invalid_option_fails_clearly(self) -> None:
        output = self._run_invalid_option("run_analysis.py")

        self.assertIn("usage", output)
        self.assertIn("error", output)

    def test_run_batch_analysis_invalid_option_fails_clearly(self) -> None:
        output = self._run_invalid_option("run_batch_analysis.py")

        self.assertIn("usage", output)
        self.assertIn("error", output)


if __name__ == "__main__":
    unittest.main()
