# Audit Log Expectations

This document records repository-file expectations for the generated
`audit_log.jsonl` artifact. It documents current behavior only. It does not add
a standalone audit log schema, add schema enforcement, change runtime behavior,
or change tests.

## Role

`audit_log.jsonl` is a shared operational and audit artifact. It records what
happened during deterministic analysis runs so maintainers can reproduce and
inspect run context.

In the v1.0 demo layout, the audit log is written at:

```text
<reports-dir>/audit_log.jsonl
```

The file is JSONL: each line is one JSON object. In the current demo, each
successful ticker run appends one record. Generated audit logs must remain under
ignored `reports/` paths and must not be committed.

The audit log is not a user-facing model output. It does not calculate DCF,
fair value, ratings, confidence, signals, price targets, recommendations,
investment advice, trading actions, or portfolio actions.

## Stable Envelope Fields

Current audit records are expected to include this stable top-level envelope:

| Field | Expected type | Expectation |
| --- | --- | --- |
| `timestamp` | non-empty string | UTC record creation time for run chronology. |
| `ticker` | non-empty string | Ticker processed by the run. |
| `methodology_version` | non-empty string | Methodology configuration version used by the run. |
| `data_context_path` | non-empty string | Company context path used by the run. |
| `source_files_used` | array | Source input file paths used by the run. |
| `validation_status` | object | Source validation result snapshot. |
| `ratio_outputs` | array | Ratio output snapshots included in the run. |
| `research_gaps_detected` | array | Research gap snapshots detected for the run. |
| `git_commit_hash` | string or null | Repository commit hash when available. |

These fields are already protected by `scripts/write_audit_log.py` through
`REQUIRED_FIELDS` and `validate_audit_record`.

## Flexible Diagnostic Content

The audit log intentionally preserves nested diagnostic snapshots without
freezing their full internal shape here.

These fields remain flexible:

- `validation_status.errors`: source validation error objects may evolve as
  validation rules improve.
- `ratio_outputs`: ratio records may evolve with ratio coverage, formulas,
  traceability fields, and source-reference expectations.
- nested source references inside `ratio_outputs`: source metadata shape may
  evolve with data-contract work.
- `research_gaps_detected`: gap records may evolve with watchlist, freshness,
  missing-data, and future adapter diagnostics.
- platform-specific path strings in `data_context_path` and
  `source_files_used`: paths may use Windows or POSIX separators and may be
  absolute or relative depending on the runner.
- exact `timestamp` values: timestamps naturally change on each run.
- exact `git_commit_hash` values: commit hashes naturally change and may be
  `null` when git metadata is unavailable.

Consumers should treat these nested values as operational snapshots unless a
future schema proposal explicitly promotes a nested field into a stable
contract.

## Why There Is No Standalone Schema Yet

A standalone audit log schema is not enforced yet because the current stable
envelope already has direct validator coverage and tests:

- `scripts/write_audit_log.py` validates the required top-level fields and
  basic types before appending.
- `tests/test_write_audit_log.py` covers audit log creation, required fields,
  append-only behavior, and missing-field failures.
- `tests/test_run_v1_0_demo.py` verifies that the v1.0 demo writes the shared
  audit log at the configured reports directory root.
- `tests/test_run_analysis.py` verifies that orchestrator audit records
  preserve source files, the data context path, source validation status, and
  nested ratio source-reference evidence fields.

Adding a separate schema now would mostly duplicate existing validation while
risking over-constraint of diagnostic payloads that should evolve with source
validation, ratio calculation, research gaps, and future adapters.

## When A Future Schema May Be Justified

A future standalone audit log schema may be justified if one of these needs
appears:

- an external tool or adapter consumes audit logs directly and needs a
  machine-readable contract
- historical audit log compatibility needs explicit versioning
- audit records need migration support across releases
- multiple audit record types are introduced
- nested diagnostic fields become stable public contracts
- maintainers need stronger validation than `validate_audit_record` provides

Any future audit log schema proposal should keep the first implementation narrow
and should avoid freezing nested diagnostics unless the proposal explains why
that nested shape is now stable.

## Related Documents

- `docs/AUDIT_LOG_SCHEMA_NEED_ASSESSMENT.md`
- `docs/REPORT_ARTIFACT_CONTRACT.md`
- `docs/SCHEMA_FIELD_REFERENCE.md`
- `docs/GENERATED_OUTPUT_SCHEMA_ASSESSMENT.md`
