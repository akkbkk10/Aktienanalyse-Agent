from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_v1_0_demo.py"
spec = importlib.util.spec_from_file_location("run_v1_0_demo", SCRIPT_PATH)
run_v1_0_demo = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(run_v1_0_demo)


FORBIDDEN_PHRASES = [
    "price target",
    "target price",
    "buy recommendation",
    "sell recommendation",
    "hold recommendation",
    "you should buy",
    "you should sell",
    "you should hold",
    "we recommend buying",
    "we recommend selling",
    "we recommend holding",
    "personal investment advice",
    "place an order",
    "submit an order",
    "submitting an order",
    "execute trade",
    "automated trading",
    "broker order",
    "portfolio allocation",
    "invented source",
    "source invented",
    "assumed source",
    "unsourced financial figure",
    "latest live quote",
    "fetched live",
    "live data fetched",
    "real-time market data",
]
SAFE_GUARDRAIL_PHRASES = [
    "not investment advice",
    "no buy/sell/hold recommendation",
    "does not include price targets",
]
ARTIFACT_KEYS_TO_SCAN = [
    "report_path",
    "analysis_summary_path",
    "fair_value_per_share_output_path",
    "model_rating_output_path",
    "model_confidence_output_path",
    "model_signal_output_path",
]


class ForbiddenOutputRegressionTests(unittest.TestCase):
    def test_generated_user_facing_artifacts_do_not_contain_forbidden_phrases(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_v1_0_demo.run_demo(reports_dir=Path(temp_dir) / "reports")

            self.assertTrue(result["demo_completed"])
            for ticker, output_paths in result["generated_file_paths"]["output_paths_by_ticker"].items():
                for artifact_key in ARTIFACT_KEYS_TO_SCAN:
                    artifact_path = Path(output_paths[artifact_key])
                    artifact_text = _normalized_artifact_text(artifact_path)
                    for phrase in FORBIDDEN_PHRASES:
                        self.assertNotIn(phrase, artifact_text, f"{ticker} {artifact_key} contained {phrase!r}")

    def test_example_assumptions_keep_confidence_below_a_and_signals_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_v1_0_demo.run_demo(reports_dir=Path(temp_dir) / "reports")
            output_paths_by_ticker = result["generated_file_paths"]["output_paths_by_ticker"]

            for ticker in ["NVDA", "AMD", "TSMC"]:
                confidence = json.loads(
                    Path(output_paths_by_ticker[ticker]["model_confidence_output_path"]).read_text(encoding="utf-8")
                )
                signal = json.loads(
                    Path(output_paths_by_ticker[ticker]["model_signal_output_path"]).read_text(encoding="utf-8")
                )

                self.assertNotEqual(confidence["model_confidence"], "A", ticker)
                self.assertEqual(confidence["assumption_quality"]["status"], "manual_review_required", ticker)
                self.assertEqual(signal["model_signal"], "unavailable", ticker)
                self.assertTrue(signal["blocking_reasons"], ticker)


def _normalized_artifact_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8").lower()
    for phrase in SAFE_GUARDRAIL_PHRASES:
        text = text.replace(phrase, "")
    return text


if __name__ == "__main__":
    unittest.main()
