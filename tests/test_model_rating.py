from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "model_rating.py"
spec = importlib.util.spec_from_file_location("model_rating", SCRIPT_PATH)
model_rating = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(model_rating)


def fair_value_output(value: float) -> dict:
    return {
        "ticker": "EXM",
        "calculated": True,
        "scenarios": [
            {
                "scenario": "base",
                "fair_value_per_share": value,
                "currency": "USD",
                "share_count_metric_id": "exm_shares_fy2025",
            }
        ],
    }


def market_price_metric(value: float = 100.0) -> dict:
    return {
        "metric_id": "exm_current_market_price_2026_05_23",
        "metric_name": "Current market price",
        "metric_category": "market_price",
        "value": value,
        "unit": "USD per share",
        "currency": "USD",
        "exchange": "NASDAQ",
        "price_type": "latest_trade",
        "as_of_datetime": "2026-05-23T00:15:00Z",
        "provider": "Nasdaq",
        "retrieval_method": "manual_snapshot",
        "period": "Latest trade timestamp 2026-05-23 00:15 UTC",
        "accounting_basis": "Other",
        "statement_type": "fact",
        "source_metadata": {
            "source_url": "https://www.nasdaq.com/market-activity/stocks/exm",
            "source_type": "market data",
            "source_date": "2026-05-23",
            "last_verified": "2026-05-24",
            "confidence": "high",
        },
    }


class ModelRatingTests(unittest.TestCase):
    def test_rating_bucket_5(self) -> None:
        self.assert_rating(160, 5, "strongly undervalued on model basis")

    def test_rating_bucket_4(self) -> None:
        self.assert_rating(120, 4, "undervalued on model basis")

    def test_rating_bucket_3(self) -> None:
        self.assert_rating(100, 3, "fairly valued / neutral on model basis")

    def test_rating_bucket_2(self) -> None:
        self.assert_rating(80, 2, "overvalued on model basis")

    def test_rating_bucket_1(self) -> None:
        self.assert_rating(40, 1, "strongly overvalued on model basis")

    def test_missing_market_price_blocks_rating(self) -> None:
        with temp_context([]) as context_root:
            with self.assertRaises(model_rating.ModelRatingError):
                calculate_model_rating_for_test(context_root, 100)

    def test_missing_market_price_source_metadata_blocks_rating(self) -> None:
        metric = market_price_metric()
        del metric["source_metadata"]["source_url"]

        with temp_context([metric]) as context_root:
            with self.assertRaises(model_rating.ModelRatingError):
                calculate_model_rating_for_test(context_root, 100)

    def test_stale_market_price_blocks_rating(self) -> None:
        metric = market_price_metric()
        metric["as_of_datetime"] = "2026-01-01T00:15:00Z"

        with temp_context([metric]) as context_root:
            with self.assertRaises(model_rating.ModelRatingError):
                calculate_model_rating_for_test(context_root, 100)

    def test_model_rating_does_not_call_external_apis(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8")

        for forbidden in ["requests", "urlopen", "http.client", "urllib.request"]:
            self.assertNotIn(forbidden, source)

    def test_no_buy_sell_hold_language(self) -> None:
        with temp_context([market_price_metric()]) as context_root:
            result = calculate_model_rating_for_test(context_root, 100)

        serialized = json.dumps(result).lower()
        for term in ["buy", "sell", "hold", "recommendation", "price target"]:
            self.assertNotIn(term, serialized)

    def test_no_investment_advice_language_except_required_disclaimer(self) -> None:
        with temp_context([market_price_metric()]) as context_root:
            result = calculate_model_rating_for_test(context_root, 100)

        self.assertEqual(result["disclaimer"], "non-personalized model output, not investment advice.")
        serialized = json.dumps(result).lower().replace("not investment advice", "")
        self.assertNotIn("investment advice", serialized)

    def assert_rating(self, fair_value: float, expected_rating: int, expected_label: str) -> None:
        with temp_context([market_price_metric()]) as context_root:
            result = calculate_model_rating_for_test(context_root, fair_value)

        self.assertEqual(result["model_rating"], expected_rating)
        self.assertEqual(result["rating_label"], expected_label)
        self.assertEqual(result["market_price_used"], 100)
        self.assertEqual(result["rules_version"], "0.1.0")


def calculate_model_rating_for_test(context_root: Path, fair_value: float) -> dict:
    return model_rating.calculate_model_rating(
        "EXM",
        fair_value_output(fair_value),
        context_root=context_root,
        today=date(2026, 5, 24),
    )


class temp_context:
    def __init__(self, metrics: list[dict]) -> None:
        self.metrics = metrics

    def __enter__(self) -> Path:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        company_dir = root / "EXM"
        company_dir.mkdir(parents=True)
        context = {
            "schema_version": "0.1.0",
            "ticker": "EXM",
            "company_name": "Example AG",
            "last_updated": "2026-05-24",
            "metrics": self.metrics,
            "source_metadata": {"source_file": None, "metric_count": len(self.metrics)},
        }
        (company_dir / "context.json").write_text(json.dumps(context), encoding="utf-8")
        return root

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
