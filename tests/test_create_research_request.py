from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "create_research_request.py"
spec = importlib.util.spec_from_file_location("create_research_request", SCRIPT_PATH)
create_research_request = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(create_research_request)


class CreateResearchRequestTests(unittest.TestCase):
    def test_append_request_creates_json_and_markdown_queue_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            markdown_queue_path = Path(temp_dir) / "research_queue.md"
            json_queue_path = Path(temp_dir) / "research_queue.json"

            result = create_research_request.append_request(
                company="Example AG",
                ticker="EXM",
                question="Find latest annual report.",
                markdown_queue_path=markdown_queue_path,
                json_queue_path=json_queue_path,
            )

            queue = json.loads(json_queue_path.read_text(encoding="utf-8"))
            markdown = markdown_queue_path.read_text(encoding="utf-8")

            self.assertTrue(result["created"])
            self.assertEqual(len(queue["items"]), 1)
            self.assertEqual(queue["items"][0]["ticker"], "EXM")
            self.assertIn("Required evidence: source_url, source_type, source_date, unit, period, confidence", markdown)

    def test_duplicate_request_is_not_added_twice(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            markdown_queue_path = Path(temp_dir) / "research_queue.md"
            json_queue_path = Path(temp_dir) / "research_queue.json"

            first = create_research_request.append_request(
                company="Example AG",
                ticker="EXM",
                question="Find latest annual report.",
                markdown_queue_path=markdown_queue_path,
                json_queue_path=json_queue_path,
            )
            second = create_research_request.append_request(
                company="Example AG",
                ticker="EXM",
                question="Find latest annual report.",
                markdown_queue_path=markdown_queue_path,
                json_queue_path=json_queue_path,
            )

            queue = json.loads(json_queue_path.read_text(encoding="utf-8"))
            markdown = markdown_queue_path.read_text(encoding="utf-8")

            self.assertTrue(first["created"])
            self.assertFalse(second["created"])
            self.assertEqual(len(queue["items"]), 1)
            self.assertEqual(markdown.count("## Example AG (EXM)"), 1)

    def test_validation_errors_create_queue_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "bad_metrics.json"
            markdown_queue_path = temp_path / "research_queue.md"
            json_queue_path = temp_path / "research_queue.json"
            input_path.write_text(
                json.dumps(
                    {
                        "company": "Example AG",
                        "ticker": "EXM",
                        "metric_name": "Revenue",
                        "value": 1.0,
                        "unit": "EUR",
                        "period": "FY2025",
                        "accounting_basis": "GAAP",
                        "statement_type": "fact",
                        "source_type": "earnings release",
                        "source_date": "2026-01-15",
                        "last_verified": "2026-01-16",
                        "confidence": "high",
                    }
                ),
                encoding="utf-8",
            )

            result = create_research_request.append_requests_from_validation_errors(
                input_path=input_path,
                markdown_queue_path=markdown_queue_path,
                json_queue_path=json_queue_path,
            )

            queue = json.loads(json_queue_path.read_text(encoding="utf-8"))

            self.assertGreaterEqual(result["created_count"], 1)
            self.assertEqual(result["duplicate_count"], 0)
            self.assertTrue(any(item["source"] == "validation_error" for item in queue["items"]))
            self.assertTrue(any(item["context"]["field"] == "source_url" for item in queue["items"]))

    def test_validation_error_queueing_prevents_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "bad_metrics.json"
            second_input_path = temp_path / "same_bad_metrics.json"
            markdown_queue_path = temp_path / "research_queue.md"
            json_queue_path = temp_path / "research_queue.json"
            bad_record = json.dumps(
                {
                    "company": "Example AG",
                    "ticker": "EXM",
                    "metric_name": "Revenue",
                    "value": 1.0,
                    "period": "FY2025",
                    "accounting_basis": "GAAP",
                    "statement_type": "fact",
                    "source_url": "https://example.com/report",
                    "source_type": "earnings release",
                    "source_date": "2026-01-15",
                    "last_verified": "2026-01-16",
                    "confidence": "high",
                }
            )
            input_path.write_text(bad_record, encoding="utf-8")
            second_input_path.write_text(bad_record, encoding="utf-8")

            first = create_research_request.append_requests_from_validation_errors(
                input_path=input_path,
                markdown_queue_path=markdown_queue_path,
                json_queue_path=json_queue_path,
            )
            second = create_research_request.append_requests_from_validation_errors(
                input_path=second_input_path,
                markdown_queue_path=markdown_queue_path,
                json_queue_path=json_queue_path,
            )

            queue = json.loads(json_queue_path.read_text(encoding="utf-8"))

            self.assertGreaterEqual(first["created_count"], 1)
            self.assertEqual(second["created_count"], 0)
            self.assertGreaterEqual(second["duplicate_count"], 1)
            self.assertEqual(len(queue["items"]), first["created_count"])


if __name__ == "__main__":
    unittest.main()
