from __future__ import annotations

import importlib.util
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
    def test_append_request_writes_required_evidence_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            queue_path = Path(temp_dir) / "research_queue.md"

            entry = create_research_request.append_request(
                company="Example AG",
                ticker="EXM",
                question="Find latest annual report.",
                queue_path=queue_path,
            )

            self.assertIn("Required evidence: source_url, source_date, unit, period, confidence", entry)
            self.assertEqual(queue_path.read_text(encoding="utf-8"), entry)


if __name__ == "__main__":
    unittest.main()
