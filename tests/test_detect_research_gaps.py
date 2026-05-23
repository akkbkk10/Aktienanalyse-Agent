from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "detect_research_gaps.py"
spec = importlib.util.spec_from_file_location("detect_research_gaps", SCRIPT_PATH)
detect_research_gaps = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(detect_research_gaps)


def metric(name: str, last_verified: str = "2026-05-23", confidence: str = "high") -> dict:
    return {
        "metric_name": name,
        "value": 1.0,
        "unit": "USD millions",
        "period": "FY2025",
        "accounting_basis": "GAAP",
        "statement_type": "fact",
        "source_metadata": {
            "source_url": "https://example.com/report",
            "source_date": "2026-01-15",
            "last_verified": last_verified,
            "confidence": confidence,
        },
    }


def context(metrics: list[dict]) -> dict:
    return {
        "schema_version": "0.1.0",
        "ticker": "NVDA",
        "company_name": "NVIDIA Corporation",
        "last_updated": "2026-05-23",
        "metrics": metrics,
        "source_metadata": {"source_file": "test", "metric_count": len(metrics)},
    }


class DetectResearchGapsTests(unittest.TestCase):
    def test_missing_metric_creates_queue_entry(self) -> None:
        with temp_workspace(context([metric("Revenue")]), required_metrics=["Revenue", "Net income"]) as paths:
            result = detect_research_gaps.detect_and_queue_gaps(
                watchlist_path=paths["watchlist"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                today=date(2026, 5, 23),
            )

            queue = json.loads(paths["json_queue"].read_text(encoding="utf-8"))

            self.assertTrue(any(gap["gap_type"] == "missing_metric" for gap in result["gaps"]))
            self.assertEqual(result["queue"]["created_count"], 1)
            self.assertEqual(queue["items"][0]["source"], "research_gap_agent")

    def test_stale_metric_creates_queue_entry(self) -> None:
        with temp_workspace(context([metric("Revenue", last_verified="2025-01-01")])) as paths:
            result = detect_research_gaps.detect_and_queue_gaps(
                watchlist_path=paths["watchlist"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                today=date(2026, 5, 23),
            )

            self.assertTrue(any(gap["gap_type"] == "stale_metric" for gap in result["gaps"]))
            self.assertEqual(result["queue"]["created_count"], 1)

    def test_low_confidence_creates_queue_entry(self) -> None:
        with temp_workspace(context([metric("Revenue", confidence="low")])) as paths:
            result = detect_research_gaps.detect_and_queue_gaps(
                watchlist_path=paths["watchlist"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                today=date(2026, 5, 23),
            )

            self.assertTrue(any(gap["gap_type"] == "low_confidence" for gap in result["gaps"]))
            self.assertEqual(result["queue"]["created_count"], 1)

    def test_missing_source_metadata_creates_queue_entry(self) -> None:
        incomplete_metric = metric("Revenue")
        del incomplete_metric["source_metadata"]["source_url"]

        with temp_workspace(context([incomplete_metric])) as paths:
            result = detect_research_gaps.detect_and_queue_gaps(
                watchlist_path=paths["watchlist"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                today=date(2026, 5, 23),
            )

            self.assertTrue(any(gap["gap_type"] == "missing_source_metadata" for gap in result["gaps"]))
            self.assertEqual(result["queue"]["created_count"], 1)

    def test_no_gap_case_creates_no_queue_entries(self) -> None:
        with temp_workspace(context([metric("Revenue")])) as paths:
            result = detect_research_gaps.detect_and_queue_gaps(
                watchlist_path=paths["watchlist"],
                context_root=paths["context_root"],
                markdown_queue_path=paths["markdown_queue"],
                json_queue_path=paths["json_queue"],
                today=date(2026, 5, 23),
            )

            self.assertEqual(result["gaps"], [])
            self.assertEqual(result["queue"]["created_count"], 0)
            self.assertFalse(paths["json_queue"].exists())


class temp_workspace:
    def __init__(self, company_context: dict, required_metrics: list[str] | None = None):
        self.company_context = company_context
        self.required_metrics = required_metrics or ["Revenue"]
        self.temp_dir: tempfile.TemporaryDirectory[str] | None = None

    def __enter__(self) -> dict[str, Path]:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        context_root = root / "companies"
        context_dir = context_root / "NVDA"
        context_dir.mkdir(parents=True)
        (context_dir / "context.json").write_text(json.dumps(self.company_context), encoding="utf-8")

        watchlist_path = root / "watchlist.json"
        watchlist_path.write_text(
            json.dumps(
                {
                    "schema_version": "0.1.0",
                    "tickers": {
                        "NVDA": {
                            "company_name": "NVIDIA Corporation",
                            "required_metrics": self.required_metrics,
                            "max_last_verified_age_days": 180,
                            "minimum_confidence": "medium",
                        }
                    },
                }
            ),
            encoding="utf-8",
        )

        return {
            "root": root,
            "context_root": context_root,
            "watchlist": watchlist_path,
            "markdown_queue": root / "research_queue.md",
            "json_queue": root / "research_queue.json",
        }

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if self.temp_dir:
            self.temp_dir.cleanup()
