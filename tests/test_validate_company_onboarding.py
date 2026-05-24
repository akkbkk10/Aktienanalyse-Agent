from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_company_onboarding.py"
spec = importlib.util.spec_from_file_location("validate_company_onboarding", SCRIPT_PATH)
validate_company_onboarding = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validate_company_onboarding)


def metric(metric_id: str, metric_name: str, category: str, value: float = 100.0) -> dict:
    return {
        "metric_id": metric_id,
        "ticker": "EXM",
        "company": "Example Inc.",
        "metric_name": metric_name,
        "metric_category": category,
        "value": value,
        "unit": "USD millions",
        "period": "FY2025 ended 2025-12-31",
        "source_type": "annual report",
        "source_url": "https://example.com/annual-report",
        "source_date": "2026-02-01",
        "confidence": "high",
        "last_verified": "2026-05-24",
        "accounting_basis": "GAAP",
        "statement_type": "fact",
    }


def market_price_metric() -> dict:
    record = metric("exm_current_market_price_2026_05_24", "Current market price", "market_price", 50.0)
    record.update(
        {
            "unit": "USD per share",
            "currency": "USD",
            "exchange": "NASDAQ",
            "price_type": "latest_trade",
            "as_of_datetime": "2026-05-24T12:00:00Z",
            "fetched_at": "2026-05-24T12:05:00Z",
            "provider": "Example Provider",
            "retrieval_method": "manual_snapshot",
            "period": "Latest trade timestamp 2026-05-24 12:00 UTC",
            "source_type": "market data",
            "source_url": "https://example.com/market-price",
            "accounting_basis": "Other",
        }
    )
    return record


def complete_metrics() -> list[dict]:
    return [
        metric("exm_revenue_fy2025", "Revenue", "financial_metric", 1000),
        metric("exm_net_income_fy2025", "Net income", "financial_metric", 150),
        metric("exm_free_cash_flow_fy2025", "Free cash flow", "financial_metric", 120),
        metric("exm_diluted_weighted_average_shares_fy2025", "Diluted weighted average shares", "share_count", 100),
        market_price_metric(),
    ]


def complete_assumptions() -> dict:
    return {
        "schema_version": "0.1.0",
        "ticker": "EXM",
        "unit": "USD millions",
        "source_references": [
            {
                "metric_id": "exm_free_cash_flow_fy2025",
                "metric_name": "Free cash flow",
                "period": "FY2025 ended 2025-12-31",
                "source_url": "https://example.com/annual-report",
                "source_date": "2026-02-01",
                "confidence": "high",
            }
        ],
        "scenarios": {
            "bear": scenario(),
            "base": scenario(),
            "bull": scenario(),
        },
    }


def scenario() -> dict:
    return {
        "discount_rate": 0.1,
        "terminal_growth_rate": 0.03,
        "starting_free_cash_flow": 120,
        "forecast_years": [{"year": 1, "free_cash_flow": 125}],
    }


def watchlist() -> dict:
    return {
        "schema_version": "0.1.0",
        "tickers": {
            "EXM": {
                "company_name": "Example Inc.",
                "required_metrics": ["Revenue", "Net income"],
                "max_last_verified_age_days": 180,
                "minimum_confidence": "medium",
            }
        },
    }


class ValidateCompanyOnboardingTests(unittest.TestCase):
    def test_complete_onboarding_package(self) -> None:
        with onboarding_workspace() as paths:
            result = validate_company_onboarding.validate_onboarding_package(
                ticker="EXM",
                metrics_path=paths["metrics"],
                dcf_assumptions_path=paths["assumptions"],
                watchlist_path=paths["watchlist"],
            )

            self.assertTrue(result["ready"])
            self.assertTrue(all(check["passed"] for check in result["checks"]))

    def test_missing_metrics(self) -> None:
        with onboarding_workspace(metrics=[metric("exm_revenue_fy2025", "Revenue", "financial_metric")]) as paths:
            result = validate_company_onboarding.validate_onboarding_package(
                ticker="EXM",
                metrics_path=paths["metrics"],
                dcf_assumptions_path=paths["assumptions"],
                watchlist_path=paths["watchlist"],
            )

            self.assertFalse(result["ready"])
            self.assertFalse(check_by_name(result, "required_financial_metrics")["passed"])

    def test_missing_sources(self) -> None:
        records = complete_metrics()
        del records[0]["source_url"]

        with onboarding_workspace(metrics=records) as paths:
            result = validate_company_onboarding.validate_onboarding_package(
                ticker="EXM",
                metrics_path=paths["metrics"],
                dcf_assumptions_path=paths["assumptions"],
                watchlist_path=paths["watchlist"],
            )

            self.assertFalse(result["ready"])
            self.assertFalse(check_by_name(result, "source_metadata")["passed"])
            self.assertFalse(check_by_name(result, "source_validation")["passed"])

    def test_missing_share_count(self) -> None:
        records = [record for record in complete_metrics() if record.get("metric_category") != "share_count"]

        with onboarding_workspace(metrics=records) as paths:
            result = validate_company_onboarding.validate_onboarding_package(
                ticker="EXM",
                metrics_path=paths["metrics"],
                dcf_assumptions_path=paths["assumptions"],
                watchlist_path=paths["watchlist"],
            )

            self.assertFalse(result["ready"])
            self.assertFalse(check_by_name(result, "share_count")["passed"])

    def test_missing_dcf_assumptions(self) -> None:
        with onboarding_workspace(write_assumptions=False) as paths:
            result = validate_company_onboarding.validate_onboarding_package(
                ticker="EXM",
                metrics_path=paths["metrics"],
                dcf_assumptions_path=paths["assumptions"],
                watchlist_path=paths["watchlist"],
            )

            self.assertFalse(result["ready"])
            self.assertFalse(check_by_name(result, "dcf_assumptions")["passed"])


def check_by_name(result: dict, name: str) -> dict:
    for check in result["checks"]:
        if check["name"] == name:
            return check
    raise AssertionError(f"Missing check {name}")


class onboarding_workspace:
    def __init__(
        self,
        metrics: list[dict] | None = None,
        assumptions: dict | None = None,
        write_assumptions: bool = True,
    ) -> None:
        self.metrics = metrics or complete_metrics()
        self.assumptions = assumptions or complete_assumptions()
        self.write_assumptions = write_assumptions

    def __enter__(self) -> dict[str, Path]:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        paths = {
            "metrics": root / "sample_metrics.json",
            "assumptions": root / "dcf_assumptions.json",
            "watchlist": root / "watchlist.json",
        }
        paths["metrics"].write_text(json.dumps(self.metrics), encoding="utf-8")
        if self.write_assumptions:
            paths["assumptions"].write_text(json.dumps(self.assumptions), encoding="utf-8")
        paths["watchlist"].write_text(json.dumps(watchlist()), encoding="utf-8")
        return paths

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
