# Audit Log Schema Need Assessment

This assessment reviews the current generated `audit_log.jsonl` artifact and
recommends whether a standalone audit log schema/contract is needed. It is
documentation-only and does not implement a schema, change runtime behavior,
change tests, change CI, or change generated report wording.

## Source Files And Artifacts Inspected

- `AGENTS.md`
- `README.md`
- `docs/REPORT_ARTIFACT_CONTRACT.md`
- `docs/GENERATED_OUTPUT_SCHEMA_ASSESSMENT.md`
- `docs/SCHEMA_FIELD_REFERENCE.md`
- `docs/ARCHITECTURE_GOVERNANCE_INDEX.md`
- `docs/V1_1_2_RELEASE_NOTES.md`
- `scripts/write_audit_log.py`
- `scripts/run_analysis.py`
- `scripts/run_batch_analysis.py`
- `scripts/run_v1_0_demo.py`
- `tests/test_write_audit_log.py`
- `tests/test_run_v1_0_demo.py`
- generated demo audit log under
  `reports/tmp_audit_log_schema_need_assessment_demo/audit_log.jsonl`

Generated outputs were used for assessment only and remain ignored by git.

## Current Audit Log Shape

The v1.0 demo writes one shared JSONL audit log at:

```text
<reports-dir>/audit_log.jsonl
```

The current generated demo audit log contains three JSONL records:

| Record | Ticker | Purpose |
| --- | --- | --- |
| 1 | `NVDA` | Audit record for the NVDA demo analysis run. |
| 2 | `AMD` | Audit record for the AMD demo analysis run. |
| 3 | `TSMC` | Audit record for the TSMC demo analysis run. |

Each observed record contains these top-level fields:

| Field | Observed type | Current meaning |
| --- | --- | --- |
| `timestamp` | string | UTC audit record creation time. |
| `ticker` | string | Ticker processed by the run. |
| `methodology_version` | string | Methodology configuration version used by the run. |
| `data_context_path` | string | Company context path used by the run. |
| `source_files_used` | array of strings | Source input files used by the run. |
| `validation_status` | object | Source validation result snapshot. |
| `ratio_outputs` | array of objects | Ratio outputs included in the run. |
| `research_gaps_detected` | array of objects | Research gaps detected for the run. |
| `git_commit_hash` | string or null | Git commit hash when available. |

The generated demo records have:

- `validation_status.valid` set to `true`
- `validation_status.errors` set to an empty array
- nine ratio output records per ticker
- no research gaps in the observed demo run
- `git_commit_hash` populated with the current repository commit hash

## Existing Validation Coverage

`scripts/write_audit_log.py` already defines `REQUIRED_FIELDS` and validates
audit records before they are appended.

Existing validation requires:

- all current top-level audit fields to be present
- `timestamp`, `ticker`, `methodology_version`, and `data_context_path` to be
  non-empty strings
- `source_files_used` to be an array
- `validation_status` to be an object
- `ratio_outputs` to be an array
- `research_gaps_detected` to be an array
- `git_commit_hash` to be a string or null

`tests/test_write_audit_log.py` currently covers:

- audit log file creation
- required field presence
- append-only JSONL behavior
- missing required fields failing validation

`tests/test_run_v1_0_demo.py` also verifies that the v1.0 demo writes the
shared audit log to the configured reports directory root.

## Stable Fields Suitable For Future Contract Protection

If a future standalone audit log schema is needed, these top-level fields appear
stable enough for narrow contract protection:

- `timestamp`
- `ticker`
- `methodology_version`
- `data_context_path`
- `source_files_used`
- `validation_status`
- `ratio_outputs`
- `research_gaps_detected`
- `git_commit_hash`

These type expectations also appear stable:

- `timestamp` as a non-empty string, preferably ISO-like UTC timestamp
- `ticker` as a non-empty string
- `methodology_version` as a non-empty string
- `data_context_path` as a non-empty string
- `source_files_used` as an array of strings
- `validation_status` as an object
- `ratio_outputs` as an array
- `research_gaps_detected` as an array
- `git_commit_hash` as string or null

The append-only JSONL shape is also durable: one JSON object per line, with one
record per successful ticker run in the current v1.0 demo.

## Flexible Diagnostic Fields

These fields should remain flexible because they capture operational snapshots
from other workflow stages:

- `validation_status.errors`: validation error shape may evolve with source
  validation rules.
- `ratio_outputs`: ratio output objects include calculation details, source
  metric references, formulas, periods, values, confidence, and ticker. Those
  details are governed by ratio behavior and source metadata expectations, not
  by the audit log itself.
- `ratio_outputs[].source_metric_references`: nested source references contain
  source metadata whose shape may evolve with data-contract work.
- `research_gaps_detected`: gap records may include different diagnostic fields
  depending on watchlist, source validation, freshness, and missing-data rules.
- path string formats in `data_context_path` and `source_files_used`: generated
  demo output may use Windows-style paths or platform-specific path separators.
- `git_commit_hash`: may be null when git metadata is unavailable, and its
  value naturally changes across commits.
- `timestamp`: should remain parseable enough for audit chronology, but exact
  time values and run ordering should not be frozen in a schema.

A standalone audit log schema that constrains these nested diagnostic payloads
too tightly would couple the audit log to ratio, source validation, research gap,
and future adapter internals.

## Report Artifact Contract Boundary

The audit log is part of the generated report artifact layout, but it is a
separate operational artifact rather than a per-ticker report artifact.

`docs/REPORT_ARTIFACT_CONTRACT.md` treats `audit_log.jsonl` as a shared root
artifact under the configured reports directory. Current demo tests verify that
the file exists at `<reports-dir>/audit_log.jsonl`.

Unlike per-ticker JSON artifacts such as DCF output, fair value per share output,
model rating output, model confidence output, and model signal output, the audit
log is append-only JSONL. It records what happened during runs and preserves
diagnostic snapshots for reproducibility. It is not a user-facing model output
and does not calculate financial values, signals, recommendations, price
targets, or investment advice.

## Compatibility Risks

Over-constraining audit logs has different risks than over-constraining
per-ticker generated model artifacts:

- Audit logs may need to remain readable across workflow changes and patch
  releases.
- Nested diagnostic payloads may change when validation, ratio, research gap, or
  adapter boundaries evolve.
- A strict schema could make historical audit records appear invalid even when
  they remain useful for traceability.
- A strict schema could duplicate the existing `validate_audit_record` helper
  without adding meaningful protection.
- A strict schema could encourage validating implementation-specific internals
  rather than preserving the stable audit envelope.

The strongest current contract boundary is the stable top-level audit envelope
plus append-only JSONL behavior. The nested payloads should remain operational
snapshots unless a concrete downstream consumer requires a stricter contract.

## Recommendation

Recommended next step: document audit log expectations without schema
enforcement. That recommendation has been implemented in
`docs/AUDIT_LOG_EXPECTATIONS.md`.

Do not implement a standalone audit log schema now. The current audit log
already has direct validator coverage in `scripts/write_audit_log.py`, focused
tests in `tests/test_write_audit_log.py`, and demo layout coverage in
`tests/test_run_v1_0_demo.py`.

Safe documentation-only scope:

- Treat `audit_log.jsonl` as a shared operational artifact in the report
  artifact layout.
- Preserve the existing top-level audit envelope documented in
  `docs/SCHEMA_FIELD_REFERENCE.md` and `docs/AUDIT_LOG_EXPECTATIONS.md`.
- Keep nested `validation_status`, `ratio_outputs`, and
  `research_gaps_detected` flexible.
- Add a standalone schema only if a future consumer needs machine-readable audit
  log validation beyond the existing helper and tests.

Do not include:

- audit log runtime changes
- schema implementation
- test changes
- CI changes
- report wording changes
- financial logic changes
- model rating, model confidence, or model signal changes
- DCF or fair value changes
- live fetching
- adapters
- investment advice
- trading or portfolio logic
