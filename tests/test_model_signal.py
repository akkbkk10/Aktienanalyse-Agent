from __future__ import annotations

import importlib.util
import json
import unittest
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "model_signal.py"
spec = importlib.util.spec_from_file_location("model_signal", SCRIPT_PATH)
model_signal = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(model_signal)


def rating_output(rating: int = 4, gap: float = 25.0, fetched_at: str = "2026-05-24T00:00:00Z") -> dict:
    return {
        "ticker": "EXM",
        "model_rating": rating,
        "rating_label": "rule bucket",
        "valuation_gap_percent": gap,
        "rules_version": "0.1.0",
        "source_references": [
            {
                "metric_id": "exm_current_market_price_2026_05_23",
                "metric_name": "Current market price",
                "metric_category": "market_price",
                "fetched_at": fetched_at,
            }
        ],
        "disclaimer": "non-personalized model output, not investment advice.",
    }


def confidence_output(confidence: str = "A") -> dict:
    return {
        "ticker": "EXM",
        "model_confidence": confidence,
        "confidence_label": "quality bucket",
        "confidence_score": 95,
        "rules_version": "0.1.0",
        "source_references": [],
        "disclaimer": "non-personalized model quality output, not investment advice.",
    }


class ModelSignalTests(unittest.TestCase):
    def test_positive_signal(self) -> None:
        result = calculate_signal_for_test(rating_output(4, 25.0), confidence_output("A"))

        self.assertEqual(result["model_signal"], "model_positive")
        self.assertEqual(result["model_rating_used"]["model_rating"], 4)
        self.assertEqual(result["model_confidence_used"]["model_confidence"], "A")

    def test_neutral_signal(self) -> None:
        result = calculate_signal_for_test(rating_output(3, 2.0), confidence_output("B"))

        self.assertEqual(result["model_signal"], "model_neutral")

    def test_negative_signal(self) -> None:
        result = calculate_signal_for_test(rating_output(2, -25.0), confidence_output("B"))

        self.assertEqual(result["model_signal"], "model_negative")

    def test_unavailable_when_confidence_is_d(self) -> None:
        result = calculate_signal_for_test(rating_output(5, 80.0), confidence_output("D"))

        self.assertEqual(result["model_signal"], "unavailable")
        self.assertTrue(any("confidence is D" in reason for reason in result["blocking_reasons"]))

    def test_unavailable_when_rating_is_missing(self) -> None:
        result = calculate_signal_for_test(None, confidence_output("A"))

        self.assertEqual(result["model_signal"], "unavailable")
        self.assertTrue(any("rating is unavailable" in reason for reason in result["blocking_reasons"]))
        self.assertIsNone(result["model_rating_used"])

    def test_stale_market_price_behavior(self) -> None:
        result = calculate_signal_for_test(
            rating_output(4, 25.0, fetched_at="2026-01-01T00:00:00Z"),
            confidence_output("A"),
        )

        self.assertEqual(result["model_signal"], "unavailable")
        self.assertTrue(any("Market price snapshot is stale" in reason for reason in result["blocking_reasons"]))

    def test_high_priority_research_gap_blocks_signal(self) -> None:
        result = calculate_signal_for_test(
            rating_output(4, 25.0),
            confidence_output("A"),
            research_gaps=[{"gap_type": "missing_metric", "metric_name": "Revenue", "priority": "high"}],
        )

        self.assertEqual(result["model_signal"], "unavailable")

    def test_no_buy_sell_hold_language(self) -> None:
        result = calculate_signal_for_test(rating_output(4, 25.0), confidence_output("A"))
        serialized = json.dumps(result).lower()

        for term in ["buy", "sell", "hold", "price target", "recommendation"]:
            self.assertNotIn(term, serialized)

    def test_no_investment_advice_language_except_disclaimer(self) -> None:
        result = calculate_signal_for_test(rating_output(4, 25.0), confidence_output("A"))
        serialized = json.dumps(result).lower().replace("not investment advice", "")

        self.assertEqual(result["disclaimer"], "non-personalized model output, not investment advice.")
        self.assertNotIn("investment advice", serialized)


def calculate_signal_for_test(
    rating: dict | None,
    confidence: dict | None,
    research_gaps: list[dict] | None = None,
) -> dict:
    return model_signal.calculate_model_signal(
        ticker="EXM",
        model_rating_output=rating,
        model_confidence_output=confidence,
        research_gaps=research_gaps or [],
        today=date(2026, 5, 24),
    )


if __name__ == "__main__":
    unittest.main()
