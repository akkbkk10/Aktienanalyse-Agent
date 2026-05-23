from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "calculate_ratios.py"
spec = importlib.util.spec_from_file_location("calculate_ratios", SCRIPT_PATH)
calculate_ratios = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(calculate_ratios)


def metric(name: str, value: float, period: str = "FY2025", confidence: str = "high") -> dict:
    metric_id = f"exm_{name.lower().replace(' ', '_')}_{period.lower().replace(' ', '_')}"
    return {
        "metric_id": metric_id,
        "metric_name": name,
        "value": value,
        "unit": "USD millions",
        "period": period,
        "accounting_basis": "GAAP",
        "statement_type": "fact",
        "source_metadata": {
            "source_url": "https://example.com/report",
            "source_type": "annual report",
            "source_date": "2026-01-15",
            "last_verified": "2026-05-23",
            "confidence": confidence,
        },
    }


def context(metrics: list[dict]) -> dict:
    return {
        "schema_version": "0.1.0",
        "ticker": "EXM",
        "company_name": "Example Corp",
        "last_updated": "2026-05-23",
        "metrics": metrics,
        "source_metadata": {"source_file": "test", "metric_count": len(metrics)},
    }


class CalculateRatiosTests(unittest.TestCase):
    def test_valid_ratio_calculation(self) -> None:
        result = calculate_ratios.calculate_ratios_from_context(
            context(
                [
                    metric("Revenue", 100.0),
                    metric("Gross profit", 60.0),
                    metric("Operating income", 40.0),
                    metric("Net income", 25.0),
                    metric("Free cash flow", 20.0),
                ]
            ),
            queue_missing=False,
        )

        ratios = {ratio["ratio_name"]: ratio for ratio in result["ratios"]}

        self.assertEqual(ratios["gross_margin"]["value"], 0.6)
        self.assertEqual(ratios["operating_margin"]["value"], 0.4)
        self.assertEqual(ratios["net_margin"]["value"], 0.25)
        self.assertEqual(ratios["free_cash_flow_margin"]["value"], 0.2)

    def test_missing_input_metrics_create_queue_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            result = calculate_ratios.calculate_ratios_from_context(
                context([metric("Revenue", 100.0)]),
                markdown_queue_path=temp_path / "research_queue.md",
                json_queue_path=temp_path / "research_queue.json",
            )

            queue = json.loads((temp_path / "research_queue.json").read_text(encoding="utf-8"))

            self.assertEqual(result["queue"]["created_count"], 4)
            self.assertTrue(all(item["source"] == "ratio_calculation_agent" for item in queue["items"]))

    def test_zero_revenue_protection(self) -> None:
        result = calculate_ratios.calculate_ratios_from_context(
            context([metric("Revenue", 0.0), metric("Net income", 25.0)]),
            queue_missing=False,
        )

        self.assertFalse(any(ratio["ratio_name"] == "net_margin" for ratio in result["ratios"]))
        self.assertTrue(any(item["ratio_name"] == "net_margin" for item in result["skipped"]))

    def test_source_traceability(self) -> None:
        result = calculate_ratios.calculate_ratios_from_context(
            context([metric("Revenue", 100.0), metric("Net income", 25.0, confidence="medium")]),
            queue_missing=False,
        )

        net_margin = next(ratio for ratio in result["ratios"] if ratio["ratio_name"] == "net_margin")

        self.assertEqual(net_margin["input_metrics_used"], ["Net income", "Revenue"])
        self.assertEqual(net_margin["input_metric_ids_used"], ["exm_net_income_fy2025", "exm_revenue_fy2025"])
        self.assertEqual(len(net_margin["source_metric_references"]), 2)
        self.assertEqual(net_margin["source_metric_references"][0]["metric_id"], "exm_net_income_fy2025")
        self.assertEqual(net_margin["source_metric_references"][0]["source_url"], "https://example.com/report")
        self.assertEqual(net_margin["confidence"], "medium")

    def test_ratio_outputs_preserve_input_metric_ids(self) -> None:
        result = calculate_ratios.calculate_ratios_from_context(
            context([metric("Revenue", 100.0), metric("Net income", 25.0)]),
            queue_missing=False,
        )

        net_margin = next(ratio for ratio in result["ratios"] if ratio["ratio_name"] == "net_margin")

        self.assertEqual(net_margin["input_metric_ids_used"], ["exm_net_income_fy2025", "exm_revenue_fy2025"])

    def test_no_valuation_output(self) -> None:
        result = calculate_ratios.calculate_ratios_from_context(
            context([metric("Revenue", 100.0), metric("Net income", 25.0)]),
            queue_missing=False,
        )
        serialized = json.dumps(result).lower()

        self.assertNotIn("valuation", serialized)
        self.assertNotIn("fair_value", serialized)
        self.assertNotIn("price_target", serialized)
        self.assertNotIn("recommendation", serialized)
        self.assertNotIn("investment_advice", serialized)

    def test_nvda_context_calculates_all_supported_ratios_with_traceability(self) -> None:
        nvda_context = calculate_ratios.load_json(REPO_ROOT / "data" / "companies" / "NVDA" / "context.json")

        result = calculate_ratios.calculate_ratios_from_context(nvda_context, queue_missing=False)
        ratio_names = {ratio["ratio_name"] for ratio in result["ratios"]}

        self.assertEqual(
            {
                "gross_margin",
                "operating_margin",
                "net_margin",
                "free_cash_flow_margin",
                "revenue_growth",
            },
            ratio_names,
        )
        self.assertEqual(result["missing_inputs"], [])
        self.assertEqual(result["skipped"], [])

        for ratio in result["ratios"]:
            self.assertEqual(ratio["ticker"], "NVDA")
            self.assertIn("formula", ratio)
            self.assertTrue(ratio["input_metrics_used"])
            self.assertTrue(ratio["input_metric_ids_used"])
            self.assertTrue(ratio["source_metric_references"])
            self.assertIn(ratio["confidence"], {"low", "medium", "high"})
            for source_reference in ratio["source_metric_references"]:
                self.assertEqual(
                    source_reference["source_url"],
                    "https://investor.nvidia.com/news/press-release-details/2025/NVIDIA-Announces-Financial-Results-for-Fourth-Quarter-and-Fiscal-2025/default.aspx",
                )
                self.assertTrue(source_reference["metric_id"].startswith("nvda_"))
                self.assertIn(source_reference["source_type"], {"earnings release", "annual report", "investor relations", "SEC filing"})


if __name__ == "__main__":
    unittest.main()
