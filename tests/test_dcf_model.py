from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "dcf_model.py"
spec = importlib.util.spec_from_file_location("dcf_model", SCRIPT_PATH)
dcf_model = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(dcf_model)


class DCFModelTests(unittest.TestCase):
    def test_successful_dcf_calculation(self) -> None:
        with dcf_workspace() as paths:
            result = dcf_model.run_dcf(
                ticker="NVDA",
                assumptions_path=paths["assumptions"],
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                readiness_result=ready_result(),
            )

            self.assertTrue(result["calculated"])
            self.assertEqual(set(result["scenarios"]), {"bear", "base", "bull"})
            self.assertIn("formulas", result)
            self.assertIn("source_references", result)
            self.assertIn("source_metric_ids", result)
            self.assertGreater(result["scenarios"]["base"]["dcf_value"], 0)

    def test_missing_assumptions_fail(self) -> None:
        with dcf_workspace() as paths:
            assumptions = load_json(paths["assumptions"])
            del assumptions["scenarios"]["base"]["starting_free_cash_flow"]
            broken_path = paths["root"] / "missing_assumptions.json"
            broken_path.write_text(json.dumps(assumptions), encoding="utf-8")

            with self.assertRaises(dcf_model.DCFValidationError) as raised:
                dcf_model.run_dcf(
                    ticker="NVDA",
                    assumptions_path=broken_path,
                    source_data_path=paths["source_data"],
                    context_root=paths["context_root"],
                    readiness_result=ready_result(),
                )

            self.assertIn("starting_free_cash_flow", str(raised.exception))

    def test_invalid_discount_rate_fails(self) -> None:
        with dcf_workspace() as paths:
            assumptions = load_json(paths["assumptions"])
            assumptions["scenarios"]["base"]["discount_rate"] = 1.2
            broken_path = paths["root"] / "invalid_discount_rate.json"
            broken_path.write_text(json.dumps(assumptions), encoding="utf-8")

            with self.assertRaises(dcf_model.DCFValidationError) as raised:
                dcf_model.run_dcf(
                    ticker="NVDA",
                    assumptions_path=broken_path,
                    source_data_path=paths["source_data"],
                    context_root=paths["context_root"],
                    readiness_result=ready_result(),
                )

            self.assertIn("discount_rate", str(raised.exception))

    def test_terminal_growth_higher_than_discount_rate_fails(self) -> None:
        with dcf_workspace() as paths:
            assumptions = load_json(paths["assumptions"])
            assumptions["scenarios"]["base"]["discount_rate"] = 0.05
            assumptions["scenarios"]["base"]["terminal_growth_rate"] = 0.06
            broken_path = paths["root"] / "invalid_terminal_growth.json"
            broken_path.write_text(json.dumps(assumptions), encoding="utf-8")

            with self.assertRaises(dcf_model.DCFValidationError) as raised:
                dcf_model.run_dcf(
                    ticker="NVDA",
                    assumptions_path=broken_path,
                    source_data_path=paths["source_data"],
                    context_root=paths["context_root"],
                    readiness_result=ready_result(),
                )

            self.assertIn("terminal_growth_rate must be lower than discount_rate", str(raised.exception))

    def test_readiness_gate_blocks_valuation(self) -> None:
        with dcf_workspace() as paths:
            result = dcf_model.run_dcf(
                ticker="NVDA",
                assumptions_path=paths["assumptions"],
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                readiness_result={
                    "ticker": "NVDA",
                    "ready_for_valuation": False,
                    "blocking_reasons": ["Required ratios are unavailable."],
                    "warnings": [],
                    "required_next_actions": ["Calculate required ratios."],
                },
            )

            self.assertFalse(result["calculated"])
            self.assertEqual(result["scenarios"], {})
            self.assertIn("Valuation readiness gate did not pass.", result["blocking_reasons"])

    def test_no_buy_sell_hold_recommendation_language(self) -> None:
        with dcf_workspace() as paths:
            result = dcf_model.run_dcf(
                ticker="NVDA",
                assumptions_path=paths["assumptions"],
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                readiness_result=ready_result(),
            )
            serialized = json.dumps(result).lower()

            for term in ["price target", "buy", "sell", "hold", "recommendation", "investment advice"]:
                self.assertNotIn(term, serialized)

    def test_dcf_output_references_source_metric_ids(self) -> None:
        with dcf_workspace() as paths:
            result = dcf_model.run_dcf(
                ticker="NVDA",
                assumptions_path=paths["assumptions"],
                source_data_path=paths["source_data"],
                context_root=paths["context_root"],
                readiness_result=ready_result(),
            )

            self.assertIn("nvda_free_cash_flow_fy2025", result["source_metric_ids"])
            self.assertEqual(result["source_references"][0]["metric_id"], "nvda_free_cash_flow_fy2025")
            self.assertEqual(result["scenarios"]["base"]["starting_free_cash_flow_metric_id"], "nvda_free_cash_flow_fy2025")


def ready_result() -> dict:
    return {
        "ticker": "NVDA",
        "ready_for_valuation": True,
        "blocking_reasons": [],
        "warnings": [],
        "required_next_actions": [],
    }


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class dcf_workspace:
    def __enter__(self) -> dict[str, Path]:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        source_data = root / "nvda_sample_metrics.json"
        assumptions = root / "dcf_assumptions.json"
        context_root = root / "companies"
        shutil.copy(REPO_ROOT / "data" / "nvda_sample_metrics.json", source_data)
        shutil.copy(REPO_ROOT / "data" / "companies" / "NVDA" / "dcf_assumptions.json", assumptions)
        shutil.copytree(REPO_ROOT / "data" / "companies" / "NVDA", context_root / "NVDA")

        return {
            "root": root,
            "source_data": source_data,
            "assumptions": assumptions,
            "context_root": context_root,
        }

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
