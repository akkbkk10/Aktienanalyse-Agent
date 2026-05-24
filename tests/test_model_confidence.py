from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "model_confidence.py"
spec = importlib.util.spec_from_file_location("model_confidence", SCRIPT_PATH)
model_confidence = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(model_confidence)


def market_price_metric(confidence: str = "high", fetched_at: str = "2026-05-24T00:00:00Z") -> dict:
    return {
        "metric_id": "exm_current_market_price_2026_05_23",
        "metric_name": "Current market price",
        "metric_category": "market_price",
        "value": 100.0,
        "unit": "USD per share",
        "currency": "USD",
        "exchange": "NASDAQ",
        "price_type": "latest_trade",
        "as_of_datetime": "2026-05-23T00:15:00Z",
        "fetched_at": fetched_at,
        "provider": "Nasdaq",
        "retrieval_method": "manual_snapshot",
        "period": "Latest trade timestamp 2026-05-23 00:15 UTC",
        "source_metadata": {
            "source_url": "https://www.nasdaq.com/market-activity/stocks/exm",
            "source_type": "market data",
            "source_date": "2026-05-23",
            "last_verified": "2026-05-24",
            "confidence": confidence,
        },
    }


def revenue_metric(confidence: str = "high") -> dict:
    return {
        "metric_id": "exm_revenue_fy2025",
        "metric_name": "Revenue",
        "metric_category": "income_statement",
        "value": 1000,
        "unit": "USD millions",
        "period": "FY2025",
        "source_metadata": {
            "source_url": "https://example.com/annual-report",
            "source_type": "annual report",
            "source_date": "2026-02-01",
            "last_verified": "2026-05-24",
            "confidence": confidence,
        },
    }


def complete_assumptions() -> dict:
    return {
        "scenarios": {
            "bear": {
                "discount_rate": 0.12,
                "terminal_growth_rate": 0.02,
                "starting_free_cash_flow": 100,
                "forecast_years": [{"year": 1, "free_cash_flow": 100}],
            },
            "base": {
                "discount_rate": 0.10,
                "terminal_growth_rate": 0.03,
                "starting_free_cash_flow": 100,
                "forecast_years": [{"year": 1, "free_cash_flow": 110}],
            },
            "bull": {
                "discount_rate": 0.09,
                "terminal_growth_rate": 0.035,
                "starting_free_cash_flow": 100,
                "forecast_years": [{"year": 1, "free_cash_flow": 120}],
            },
        }
    }


def example_assumptions() -> dict:
    payload = complete_assumptions()
    payload["assumption_label"] = "Example assumptions for deterministic tests"
    payload["assumption_notes"] = [
        "These are placeholder assumptions.",
        "They require manual review before use.",
    ]
    return payload


class ModelConfidenceTests(unittest.TestCase):
    def test_confidence_a_case(self) -> None:
        result = calculate_confidence_for_test([revenue_metric(), market_price_metric()])

        self.assertEqual(result["model_confidence"], "A")
        self.assertEqual(result["confidence_label"], "high data quality, low uncertainty")
        self.assertEqual(result["rules_version"], "0.1.0")

    def test_confidence_b_case(self) -> None:
        result = calculate_confidence_for_test(
            [revenue_metric(), market_price_metric()],
            research_gaps=[{"gap_type": "low_confidence", "metric_name": "Revenue"}],
        )

        self.assertEqual(result["model_confidence"], "B")

    def test_confidence_c_case(self) -> None:
        result = calculate_confidence_for_test(
            [revenue_metric(), market_price_metric()],
            validation_status={"valid": False, "errors": [{"message": "broken"}]},
        )

        self.assertEqual(result["model_confidence"], "C")

    def test_confidence_d_case(self) -> None:
        result = calculate_confidence_for_test(
            [revenue_metric("low"), market_price_metric("low")],
            validation_status={"valid": False, "errors": [{"message": "broken"}]},
            assumptions_payload={"scenarios": {}},
        )

        self.assertEqual(result["model_confidence"], "D")

    def test_stale_market_price_lowering_confidence(self) -> None:
        result = calculate_confidence_for_test(
            [revenue_metric(), market_price_metric(fetched_at="2026-01-01T00:00:00Z")]
        )

        self.assertEqual(result["model_confidence"], "B")
        self.assertTrue(any("Market price snapshot is older" in reason for reason in result["reasons"]))
        self.assertTrue(result["warnings"])

    def test_high_priority_research_gap_lowering_confidence(self) -> None:
        result = calculate_confidence_for_test(
            [revenue_metric(), market_price_metric()],
            research_gaps=[{"gap_type": "missing_metric", "metric_name": "Free cash flow", "priority": "high"}],
        )

        self.assertEqual(result["model_confidence"], "B")
        self.assertTrue(any("high-priority research gap" in reason for reason in result["reasons"]))

    def test_missing_dcf_assumptions_lowering_confidence(self) -> None:
        result = calculate_confidence_for_test(
            [revenue_metric(), market_price_metric()],
            write_assumptions=False,
        )

        self.assertEqual(result["model_confidence"], "B")
        self.assertTrue(any("Assumption set is missing" in reason for reason in result["reasons"]))

    def test_example_dcf_assumptions_cap_confidence(self) -> None:
        result = calculate_confidence_for_test(
            [revenue_metric(), market_price_metric()],
            assumptions_payload=example_assumptions(),
        )

        self.assertEqual(result["model_confidence"], "C")
        self.assertLess(result["confidence_score"], 95)
        self.assertEqual(result["assumption_quality"]["status"], "manual_review_required")
        self.assertFalse(result["assumption_quality"]["active_signal_allowed"])
        self.assertIn("example", result["assumption_quality"]["matched_terms"])
        self.assertTrue(any("Assumption set is labeled" in reason for reason in result["reasons"]))
        self.assertTrue(any("Assumption quality is insufficient" in warning for warning in result["warnings"]))

    def test_source_references_preserve_market_snapshot_timestamps(self) -> None:
        result = calculate_confidence_for_test([revenue_metric(), market_price_metric()])
        market_price_reference = [
            source for source in result["source_references"] if source["metric_category"] == "market_price"
        ][0]

        self.assertEqual(market_price_reference["as_of_datetime"], "2026-05-23T00:15:00Z")
        self.assertEqual(market_price_reference["fetched_at"], "2026-05-24T00:00:00Z")

    def test_no_recommendation_or_investment_advice_language(self) -> None:
        result = calculate_confidence_for_test([revenue_metric(), market_price_metric()])
        serialized = json.dumps(result).lower().replace("not investment advice", "")

        for term in ["buy", "sell", "hold", "recommendation", "investment advice", "model signal"]:
            self.assertNotIn(term, serialized)


def calculate_confidence_for_test(
    metrics: list[dict],
    validation_status: dict | None = None,
    research_gaps: list[dict] | None = None,
    assumptions_payload: dict | None = None,
    write_assumptions: bool = True,
) -> dict:
    with temp_confidence_workspace(metrics, assumptions_payload, write_assumptions) as paths:
        return model_confidence.calculate_model_confidence(
            ticker="EXM",
            validation_status=validation_status or {"valid": True, "errors": []},
            research_gaps=research_gaps or [],
            context_root=paths["context_root"],
            dcf_assumptions_path=paths["assumptions_path"],
            today=date(2026, 5, 24),
        )


class temp_confidence_workspace:
    def __init__(self, metrics: list[dict], assumptions_payload: dict | None, write_assumptions: bool) -> None:
        self.metrics = metrics
        self.assumptions_payload = assumptions_payload or complete_assumptions()
        self.write_assumptions = write_assumptions

    def __enter__(self) -> dict[str, Path]:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        company_dir = root / "companies" / "EXM"
        company_dir.mkdir(parents=True)
        context = {
            "schema_version": "0.1.0",
            "ticker": "EXM",
            "company_name": "Example Inc.",
            "last_updated": "2026-05-24",
            "metrics": self.metrics,
            "source_metadata": {"source_file": None, "metric_count": len(self.metrics)},
        }
        (company_dir / "context.json").write_text(json.dumps(context), encoding="utf-8")
        assumptions_path = root / "dcf_assumptions.json"
        if self.write_assumptions:
            assumptions_path.write_text(json.dumps(self.assumptions_payload), encoding="utf-8")
        return {"context_root": root / "companies", "assumptions_path": assumptions_path}

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
