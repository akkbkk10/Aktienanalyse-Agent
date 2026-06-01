# Generated Artifact Manifest Assessment

This assessment reviews whether the project should introduce a generated
artifact manifest for report bundles. It is documentation-only. It does not
add a manifest, schema, validator, runtime behavior, CLI behavior, test,
release note, tag, or generated report artifact.

## Source Files Inspected

- `AGENTS.md`
- `README.md`
- `docs/REPORT_ARTIFACT_CONTRACT.md`
- `docs/GENERATED_OUTPUT_SCHEMA_ASSESSMENT.md`
- `docs/AUDIT_LOG_EXPECTATIONS.md`
- `docs/FACT_REPORT_EXPECTATIONS.md`
- `docs/V1_1_4_RELEASE_NOTES.md`
- `scripts/run_v1_0_demo.py`
- `scripts/run_batch_analysis.py`
- `scripts/run_analysis.py`

## Current Repository State

The repository does not currently write a persisted generated artifact
manifest. The current deterministic workflow already exposes artifact location
metadata in three places:

- `scripts/run_analysis.py` returns per-ticker paths such as `report_path`,
  `analysis_summary_path`, DCF output path, fair value per share output path,
  model output paths, and audit log status.
- `scripts/run_batch_analysis.py` collects per-ticker output paths under
  `output_paths_by_ticker` and reports successful and failed runs.
- `scripts/run_v1_0_demo.py` returns `generated_file_paths`, including the
  shared `audit_log_path` and per-ticker artifact paths, and checks required
  artifact keys for demo completion.

The stable generated report layout is documented in
`docs/REPORT_ARTIFACT_CONTRACT.md` and protected by v1.0 demo tests. Audit log
expectations are documented separately in `docs/AUDIT_LOG_EXPECTATIONS.md`.
Fact report Markdown expectations are documented separately in
`docs/FACT_REPORT_EXPECTATIONS.md`.

## Purpose A Manifest Could Serve

A generated artifact manifest could be a machine-readable inventory of the
artifacts produced by one run. It would not define the contents of those
artifacts. Instead, it could help maintainers or future tooling answer:

- which tickers were processed
- which artifacts were expected
- which artifacts were generated
- where each artifact was written
- whether an artifact is shared across the run or belongs to one ticker
- which run metadata applies to the generated bundle

This would be most useful if a future review, adapter, release validation, or
packaging workflow needs a single file to inspect generated bundle completeness
without parsing CLI output.

## Potential Benefits

A manifest could provide value if a concrete consumer appears:

- central inventory for generated report bundles
- simpler automated review of expected versus generated artifacts
- clearer distinction between per-ticker artifacts and shared run artifacts
- stable handoff point for future tooling that needs artifact paths
- easier validation of partial batch runs without reading several command
  summaries
- documented lifecycle for generated bundle metadata

These benefits are real, but they mostly matter once something outside the
current deterministic scripts needs to consume a persisted manifest file.

## Risks And Compatibility Costs

Adding a manifest too early would add another generated artifact and another
contract surface. The main risks are:

- duplicating artifact paths already returned by `run_analysis`,
  `run_batch_analysis`, and `run_v1_0_demo`
- duplicating layout expectations already covered by
  `docs/REPORT_ARTIFACT_CONTRACT.md` and demo tests
- blurring the boundary between a run inventory, the audit log, and report
  artifact content contracts
- freezing path, timestamp, failure, warning, or diagnostic fields before a
  consumer needs them
- creating stale or misleading metadata if a run fails midway and manifest
  write semantics are not defined carefully
- inviting scope creep into checksums, provenance, validation status, embedded
  artifact summaries, or release packaging before those needs are established

Because generated artifacts are ignored under `reports/`, a manifest would also
need clear lifecycle rules so it is generated for review but not committed.

## Candidate Artifacts

A future manifest could inventory these current generated artifacts.

Per-ticker artifacts:

- `<TICKER>_fact_report.md`
- `<TICKER>_analysis_summary.json`
- `<TICKER>_dcf_output.json`
- `<TICKER>_fair_value_per_share_output.json`
- `<TICKER>_model_rating_output.json`
- `<TICKER>_model_confidence_output.json`
- `<TICKER>_model_signal_output.json`

Shared run artifact:

- `audit_log.jsonl`

The following should stay outside a first manifest contract unless a future
assessment promotes them:

- runtime company contexts created under a reports directory
- generated research queue files
- temporary validation probes
- any raw source data
- nested contents of generated report artifacts

## Possible Stable Fields

If a manifest is implemented later, the smallest stable field set would likely
be run metadata and artifact inventory only:

- `manifest_version`
- `generated_at`
- `workflow_name` or `workflow_version`
- `reports_dir`
- `tickers_processed`
- `successful_runs`
- `failed_runs`
- `artifacts_by_ticker`
- `shared_artifacts`

For each artifact entry, stable fields could be limited to:

- `artifact_key`
- `artifact_type`
- `path`
- `scope` such as `per_ticker` or `shared`
- `required_for_v1_0_demo`
- `exists`

This keeps the manifest focused on inventory and avoids duplicating artifact
content schemas.

## Fields That Should Remain Flexible

These fields should not be over-constrained in an initial manifest:

- exact path style, including Windows versus POSIX separators
- absolute versus relative path representation
- exact timestamps
- git commit hashes
- warnings and failure messages
- partial-run failure diagnostics
- file sizes
- checksums or hashes
- nested validation status details
- nested source references
- embedded DCF, fair value, model rating, model confidence, model signal, audit
  log, analysis summary, or fact report content
- generated research queue and runtime context implementation details

The existing artifact-specific contracts and expectations should remain the
source of truth for artifact contents.

## Classification

A generated artifact manifest should not be classified as a Report Contract.
The report contract documents required report bundle layout and artifact paths.
A manifest would be an output of a run that inventories those artifacts.

A generated artifact manifest should not replace the audit log. The audit log
is an append-only operational history of run events and diagnostic snapshots. A
manifest would be a per-run or per-bundle inventory.

The best classification is:

**Run Metadata / Operational Artifact.**

It would be operational metadata about a generated bundle, not a user-facing
financial analysis artifact and not a schema for report contents.

## Lifecycle And Ownership

If implemented later, the manifest should:

- be written only under ignored `reports/` paths
- not be committed as a generated artifact
- be generated after artifact paths are known
- define partial-run behavior before implementation
- identify whether it represents one ticker, one batch run, or one demo run
- remain owned by the report orchestration path rather than by individual model
  output modules
- avoid changing artifact names, report wording, financial logic, model logic,
  or guardrail behavior

Any implementation PR would need focused tests because it would change runtime
output behavior.

## Decision

Recommendation: **defer**.

A generated artifact manifest may be useful later, but the current repository
does not yet show a concrete consumer or review gap that requires one. The
existing `run_analysis`, `run_batch_analysis`, and `run_v1_0_demo` summaries
already expose artifact paths; `docs/REPORT_ARTIFACT_CONTRACT.md` documents
the stable bundle layout; v1.0 demo tests protect required artifact presence;
and audit log and fact report expectations cover their own artifact roles.

The smallest safe next step is no implementation PR now. If a future consumer
appears, open a narrow follow-up assessment or expectations PR that first
defines the consumer, manifest lifecycle, partial-run semantics, and minimal
field set before adding runtime generation.

## Out Of Scope

This assessment does not add or change:

- manifest generation
- schema validation
- runtime code
- CLI behavior
- tests
- CI
- release notes
- tags
- generated reports
- artifact names or paths
- report wording
- financial logic
- model rating, model confidence, or model signal behavior
- DCF or fair value logic
- audit log schema behavior
- live fetching
- adapters or framework code
- investment advice
- trading or portfolio logic
