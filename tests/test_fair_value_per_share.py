from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "fair_value_per_share.py"
spec = importlib.util.spec_from_file_location("fair_value_per_share", SCRIPT_PATH)
fair_value_per_share = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(fair_value_per_share)


def dcf_output() -> dict:
    return {
        "ticker": "EXM",
        "calculated": True,
        "unit": "USD millions",
        "scenarios": {
            "bear": {"dcf_value": 900},
            "base": {"dcf_value": 1200},
            "bull": {"dcf_value": 1500},
        },
    }


def share_count_metric() -> dict:
    return {
        "metric_id": "exm_diluted_weighted_average_shares_fy2025",
        "metric_name": "Diluted weighted average shares",
        "metric_category": "share_count",
        "value": 100,
        "unit": "shares millions",
        "period": "FY2025",
        "accounting_basis": "GAAP",
        "statement_type": "fact",
        "source_metadata": {
            "source_url": "https://example.com/report",
            "source_type": "annual report",
            "source_date": "2026-01-15",
            "last_verified": "2026-05-23",
            "confidence": "high",
        },
    }


class FairValuePerShareTests(unittest.TestCase):
    def test_successful_fair_value_per_share_calculation(self) -> None:
        with temp_context([share_count_metric()]) as context_root:
            result = fair_value_per_share.calculate_fair_value_per_share("EXM", dcf_output(), context_root)

            self.assertTrue(result["calculated"])
            self.assertEqual(result["currency"], "USD")
            self.assertEqual(len(result["scenarios"]), 3)
            base = next(scenario for scenario in result["scenarios"] if scenario["scenario"] == "base")
            self.assertEqual(base["fair_value_per_share"], 12)
            self.assertEqual(base["dcf_value_used"], 1200)
            self.assertEqual(base["share_count_used"], 100)
            self.assertEqual(base["share_count_metric_id"], "exm_diluted_weighted_average_shares_fy2025")

    def test_fair_value_per_share_output_satisfies_contract(self) -> None:
        with temp_context([share_count_metric()]) as context_root:
            result = fair_value_per_share.calculate_fair_value_per_share("EXM", dcf_output(), context_root)

            self.assertEqual(fair_value_per_share.validate_fair_value_per_share_output(result), [])

    def test_missing_share_count_blocks_calculation(self) -> None:
        with temp_context([]) as context_root:
            with self.assertRaises(fair_value_per_share.FairValuePerShareError):
                fair_value_per_share.calculate_fair_value_per_share("EXM", dcf_output(), context_root)

    def test_missing_metric_id_blocks_calculation(self) -> None:
        metric = share_count_metric()
        del metric["metric_id"]

        with temp_context([metric]) as context_root:
            with self.assertRaises(fair_value_per_share.FairValuePerShareError):
                fair_value_per_share.calculate_fair_value_per_share("EXM", dcf_output(), context_root)

    def test_zero_or_negative_share_count_blocks_calculation(self) -> None:
        for value in [0, -1]:
            metric = share_count_metric()
            metric["value"] = value
            with self.subTest(value=value):
                with temp_context([metric]) as context_root:
                    with self.assertRaises(fair_value_per_share.FairValuePerShareError):
                        fair_value_per_share.calculate_fair_value_per_share("EXM", dcf_output(), context_root)

    def test_no_price_target_or_recommendation_language(self) -> None:
        with temp_context([share_count_metric()]) as context_root:
            result = fair_value_per_share.calculate_fair_value_per_share("EXM", dcf_output(), context_root)

        serialized = json.dumps(result).lower()
        for term in ["price target", "buy", "sell", "hold", "recommendation"]:
            self.assertNotIn(term, serialized)

    def test_fair_value_output_missing_required_field_fails_contract_validation(self) -> None:
        with temp_context([share_count_metric()]) as context_root:
            result = fair_value_per_share.calculate_fair_value_per_share("EXM", dcf_output(), context_root)
            del result["warnings"]

            with self.assertRaises(fair_value_per_share.FairValuePerShareError):
                fair_value_per_share.validate_fair_value_per_share_output(result)

    def test_fair_value_output_invalid_numeric_field_fails_contract_validation(self) -> None:
        with temp_context([share_count_metric()]) as context_root:
            result = fair_value_per_share.calculate_fair_value_per_share("EXM", dcf_output(), context_root)
            result["scenarios"][0]["fair_value_per_share"] = "not-a-number"

            with self.assertRaises(fair_value_per_share.FairValuePerShareError):
                fair_value_per_share.validate_fair_value_per_share_output(result)


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
            "last_updated": "2026-05-23",
            "metrics": self.metrics,
            "source_metadata": {"source_file": None, "metric_count": len(self.metrics)},
        }
        (company_dir / "context.json").write_text(json.dumps(context), encoding="utf-8")
        return root

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
