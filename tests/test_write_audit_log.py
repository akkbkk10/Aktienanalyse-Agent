from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "write_audit_log.py"
spec = importlib.util.spec_from_file_location("write_audit_log", SCRIPT_PATH)
write_audit_log = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(write_audit_log)


def valid_record() -> dict:
    return write_audit_log.build_audit_record(
        timestamp="2026-05-23T12:00:00Z",
        ticker="NVDA",
        methodology_version="0.1.0",
        data_context_path="data/companies/NVDA/context.json",
        source_files_used=["data/nvda_sample_metrics.json"],
        validation_status={"valid": True, "errors": []},
        ratio_outputs=[{"ratio_name": "net_margin", "value": 0.5}],
        research_gaps_detected=[],
        git_commit_hash="abc123",
    )


class WriteAuditLogTests(unittest.TestCase):
    def test_audit_log_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_log_path = Path(temp_dir) / "audit_log.jsonl"
            record = valid_record()

            write_audit_log.append_audit_record(record, audit_log_path)

            saved = json.loads(audit_log_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["ticker"], "NVDA")

    def test_required_fields_present(self) -> None:
        record = valid_record()

        self.assertEqual(write_audit_log.validate_audit_record(record), [])
        for field in write_audit_log.REQUIRED_FIELDS:
            self.assertIn(field, record)

    def test_append_only_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_log_path = Path(temp_dir) / "audit_log.jsonl"

            write_audit_log.append_audit_record(valid_record(), audit_log_path)
            write_audit_log.append_audit_record(valid_record(), audit_log_path)

            lines = audit_log_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2)
            self.assertTrue(all(json.loads(line)["ticker"] == "NVDA" for line in lines))

    def test_invalid_missing_fields_fail(self) -> None:
        record = valid_record()
        del record["ticker"]

        with self.assertRaises(ValueError):
            write_audit_log.validate_audit_record(record)


if __name__ == "__main__":
    unittest.main()

