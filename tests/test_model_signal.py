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
        "assumption_quality": {
            "status": "sufficient",
            "active_signal_allowed": True,
            "matched_terms": [],
            "blocking_reasons": [],
        },
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
        self.assertEqual(model_signal.validate_model_signal_output(result), [])

    def test_neutral_signal(self) -> None:
        result = calculate_signal_for_test(rating_output(3, 2.0), confidence_output("B"))

        self.assertEqual(result["model_signal"], "model_neutral")
        self.assertEqual(model_signal.validate_model_signal_output(result), [])

    def test_negative_signal(self) -> None:
        result = calculate_signal_for_test(rating_output(2, -25.0), confidence_output("B"))

        self.assertEqual(result["model_signal"], "model_negative")
        self.assertEqual(model_signal.validate_model_signal_output(result), [])

    def test_unavailable_when_confidence_is_d(self) -> None:
        result = calculate_signal_for_test(rating_output(5, 80.0), confidence_output("D"))

        self.assertEqual(result["model_signal"], "unavailable")
        self.assertTrue(any("confidence is D" in reason for reason in result["blocking_reasons"]))
        self.assertEqual(model_signal.validate_model_signal_output(result), [])

    def test_unavailable_when_rating_is_missing(self) -> None:
        result = calculate_signal_for_test(None, confidence_output("A"))

        self.assertEqual(result["model_signal"], "unavailable")
        self.assertTrue(any("rating is unavailable" in reason for reason in result["blocking_reasons"]))
        self.assertIsNone(result["model_rating_used"])
        self.assertEqual(model_signal.validate_model_signal_output(result), [])

    def test_unavailable_when_confidence_is_missing_satisfies_contract(self) -> None:
        result = calculate_signal_for_test(rating_output(4, 25.0), None)

        self.assertEqual(result["model_signal"], "unavailable")
        self.assertTrue(any("confidence is unavailable" in reason for reason in result["blocking_reasons"]))
        self.assertIsNone(result["model_confidence_used"])
        self.assertEqual(model_signal.validate_model_signal_output(result), [])

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

    def test_manual_review_assumptions_block_signal(self) -> None:
        confidence = confidence_output("C")
        confidence["assumption_quality"] = {
            "status": "manual_review_required",
            "active_signal_allowed": False,
            "matched_terms": ["example", "manual review"],
            "blocking_reasons": [
                "Assumption set is labeled as example, test, temporary, or requiring manual review."
            ],
        }

        result = calculate_signal_for_test(rating_output(1, -40.0), confidence)

        self.assertEqual(result["model_signal"], "unavailable")
        self.assertTrue(any("Assumption quality gate did not pass" in reason for reason in result["blocking_reasons"]))
        self.assertTrue(any("Assumption quality blocks active model output" in warning for warning in result["warnings"]))
        self.assertEqual(model_signal.validate_model_signal_output(result), [])

    def test_missing_required_model_signal_output_field_fails_contract(self) -> None:
        result = calculate_signal_for_test(rating_output(4, 25.0), confidence_output("A"))
        del result["rules_version"]

        with self.assertRaisesRegex(model_signal.ModelSignalError, "missing required field: rules_version"):
            model_signal.validate_model_signal_output(result)

    def test_invalid_model_signal_enum_fails_contract(self) -> None:
        result = calculate_signal_for_test(rating_output(4, 25.0), confidence_output("A"))
        result["model_signal"] = "buy"

        with self.assertRaisesRegex(model_signal.ModelSignalError, "model_signal must be one of"):
            model_signal.validate_model_signal_output(result)

    def test_invalid_model_signal_output_type_fails_contract(self) -> None:
        result = calculate_signal_for_test(rating_output(4, 25.0), confidence_output("A"))
        result["blocking_reasons"] = "none"

        with self.assertRaisesRegex(model_signal.ModelSignalError, "blocking_reasons must be an array"):
            model_signal.validate_model_signal_output(result)

    def test_missing_nested_model_rating_field_fails_contract(self) -> None:
        result = calculate_signal_for_test(rating_output(4, 25.0), confidence_output("A"))
        del result["model_rating_used"]["valuation_gap_percent"]

        with self.assertRaisesRegex(
            model_signal.ModelSignalError,
            "model_rating_used.missing required field: valuation_gap_percent",
        ):
            model_signal.validate_model_signal_output(result)

    def test_missing_nested_model_confidence_field_fails_contract(self) -> None:
        result = calculate_signal_for_test(rating_output(4, 25.0), confidence_output("A"))
        del result["model_confidence_used"]["assumption_quality"]["active_signal_allowed"]

        with self.assertRaisesRegex(
            model_signal.ModelSignalError,
            "model_confidence_used.assumption_quality.missing required field: active_signal_allowed",
        ):
            model_signal.validate_model_signal_output(result)

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
