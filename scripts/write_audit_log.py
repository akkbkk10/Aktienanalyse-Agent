from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT_LOG_PATH = REPO_ROOT / "audit_log.jsonl"
REQUIRED_FIELDS = [
    "timestamp",
    "ticker",
    "methodology_version",
    "data_context_path",
    "source_files_used",
    "validation_status",
    "ratio_outputs",
    "research_gaps_detected",
    "git_commit_hash",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_audit_record(
    ticker: str,
    methodology_version: str,
    data_context_path: str,
    source_files_used: list[str],
    validation_status: dict[str, Any],
    ratio_outputs: list[dict[str, Any]],
    research_gaps_detected: list[dict[str, Any]],
    git_commit_hash: str | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    record = {
        "timestamp": timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ticker": ticker,
        "methodology_version": methodology_version,
        "data_context_path": data_context_path,
        "source_files_used": source_files_used,
        "validation_status": validation_status,
        "ratio_outputs": ratio_outputs,
        "research_gaps_detected": research_gaps_detected,
        "git_commit_hash": git_commit_hash if git_commit_hash is not None else get_git_commit_hash(),
    }
    validate_audit_record(record)
    return record


def validate_audit_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"Missing required field: {field}.")

    if errors:
        raise ValueError("; ".join(errors))

    if not isinstance(record["source_files_used"], list):
        errors.append("source_files_used must be a list.")
    if not isinstance(record["validation_status"], dict):
        errors.append("validation_status must be an object.")
    if not isinstance(record["ratio_outputs"], list):
        errors.append("ratio_outputs must be a list.")
    if not isinstance(record["research_gaps_detected"], list):
        errors.append("research_gaps_detected must be a list.")

    for field in ["timestamp", "ticker", "methodology_version", "data_context_path"]:
        if not isinstance(record[field], str) or not record[field].strip():
            errors.append(f"{field} must be a non-empty string.")

    if record["git_commit_hash"] is not None and not isinstance(record["git_commit_hash"], str):
        errors.append("git_commit_hash must be a string or null.")

    if errors:
        raise ValueError("; ".join(errors))

    return []


def append_audit_record(record: dict[str, Any], audit_log_path: Path = DEFAULT_AUDIT_LOG_PATH) -> dict[str, Any]:
    validate_audit_record(record)
    audit_log_path.parent.mkdir(parents=True, exist_ok=True)
    with audit_log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True))
        handle.write("\n")
    return record


def get_git_commit_hash() -> str | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return completed.stdout.strip() or None


def main() -> int:
    parser = argparse.ArgumentParser(description="Append a reproducible analysis-run audit record.")
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--methodology-version", required=True)
    parser.add_argument("--data-context-path", required=True)
    parser.add_argument("--source-file", action="append", dest="source_files_used", default=[])
    parser.add_argument("--validation-status-json", type=Path, required=True)
    parser.add_argument("--ratio-outputs-json", type=Path, required=True)
    parser.add_argument("--research-gaps-json", type=Path, required=True)
    parser.add_argument("--audit-log-path", type=Path, default=DEFAULT_AUDIT_LOG_PATH)
    args = parser.parse_args()

    try:
        record = build_audit_record(
            ticker=args.ticker,
            methodology_version=args.methodology_version,
            data_context_path=args.data_context_path,
            source_files_used=args.source_files_used,
            validation_status=load_json(args.validation_status_json),
            ratio_outputs=load_json(args.ratio_outputs_json),
            research_gaps_detected=load_json(args.research_gaps_json),
        )
        append_audit_record(record, args.audit_log_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"created": False, "error": str(exc)}, indent=2))
        return 1

    print(json.dumps({"created": True, "audit_log_path": str(args.audit_log_path), "record": record}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

