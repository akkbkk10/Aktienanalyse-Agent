# Generated Output Schema Assessment

This assessment tracks generated JSON artifacts produced by the current
deterministic v1.0/v1.1 baseline and records which artifacts have contracts,
which have expectations-only documentation, and which remain deferred. It is
documentation-only. It does not implement schemas, change generated outputs,
change runtime logic, add tests, or change CI.

## Source Files Inspected

- `AGENTS.md`
- `docs/V1_1_CANDIDATE_PLAN.md`
- `docs/REPORT_ARTIFACT_CONTRACT.md`
- `docs/DATA_CONTRACT_SCHEMA_HARDENING_ASSESSMENT.md`
- `docs/SCHEMA_FIELD_REFERENCE.md`
- `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md`
- `docs/ARCHITECTURE_GOVERNANCE_INDEX.md`
- `docs/FACT_REPORT_CONTRACT_NEED_ASSESSMENT.md`
- `docs/GENERATED_ARTIFACT_MANIFEST_ASSESSMENT.md`
- `docs/ANALYSIS_SUMMARY_SCHEMA_NEED_ASSESSMENT.md`
- `docs/AUDIT_LOG_EXPECTATIONS.md`
- `docs/AUDIT_LOG_SCHEMA_NEED_ASSESSMENT.md`
- `docs/MODEL_CONFIDENCE_OUTPUT_SCHEMA_ASSESSMENT.md`
- `docs/MODEL_SIGNAL_OUTPUT_SCHEMA_ASSESSMENT.md`
- `scripts/run_v1_0_demo.py`
- `scripts/run_analysis.py`
- `scripts/run_batch_analysis.py`
- `scripts/dcf_model.py`
- `scripts/fair_value_per_share.py`
- `scripts/model_rating.py`
- `scripts/write_audit_log.py`
- `tests/test_run_v1_0_demo.py`
- `tests/test_run_analysis.py`

## Current Generated Output Baseline

The v1.0 demo writes generated artifacts under the configured `--reports-dir`
path. The generated artifact layout is documented in
`docs/REPORT_ARTIFACT_CONTRACT.md` and protected by
`tests/test_run_v1_0_demo.py`.

The current v1.0 demo produces these per-ticker JSON artifacts:

- `<TICKER>_analysis_summary.json`
- `<TICKER>_dcf_output.json`
- `<TICKER>_fair_value_per_share_output.json`
- `<TICKER>_model_rating_output.json`
- `<TICKER>_model_confidence_output.json`
- `<TICKER>_model_signal_output.json`

It also writes a shared JSONL audit log:

- `audit_log.jsonl`

The fact report is a Markdown artifact, not a generated JSON artifact:

- `<TICKER>_fact_report.md`

## Current Classification

| Artifact area | Classification | Reason |
| --- | --- | --- |
| DCF output | Implemented generated output contract | `config/dcf_output_schema.json` protects calculated and blocked DCF output shape. |
| Fair value per share output | Implemented generated output contract | `config/fair_value_per_share_output_schema.json` protects the downstream fair value per share artifact. |
| Model rating output | Implemented generated output contract | `config/model_rating_output_schema.json` protects the market-price-derived model rating artifact. |
| Model confidence output | Implemented generated output contract | `config/model_confidence_output_schema.json` protects successful generated confidence artifacts while leaving blocked/unavailable shapes undefined until they exist. |
| Model signal output | Implemented generated output contract | `config/model_signal_output_schema.json` protects the current active and unavailable model signal object shape. |
| Analysis summary JSON | Implemented generated output contract | `config/analysis_summary_output_schema.json` protects the report-facing summary envelope and broad section field types. |
| Audit log | Expectations-only operational artifact | `scripts/write_audit_log.py` already validates the stable envelope; `docs/AUDIT_LOG_EXPECTATIONS.md` leaves nested diagnostics flexible. |
| Runtime company contexts under reports | Internal generated implementation detail | The v1.0 demo may create runtime contexts under the reports directory, but the durable context contract lives in `config/company_context_schema.json`. |
| Research queues under reports | Internal/generated implementation detail | Batch runs may create queue files; they are not part of the stable per-ticker report artifact contract. |
| Fact report Markdown | Expectations-only user-facing artifact | It is user-facing prose and is governed by `docs/FACT_REPORT_EXPECTATIONS.md`, generated-output review, and forbidden-output tests rather than a Markdown parser or schema. |
| Generated artifact manifest | Deferred run metadata / operational artifact | `docs/GENERATED_ARTIFACT_MANIFEST_ASSESSMENT.md` recommends deferring implementation until a concrete consumer or review gap exists. |

## Historical Candidate Assessment

This table preserves the original candidate reasoning. The `Current status`
column reflects post-v1.1.5 state and supersedes the older timing guidance.

| Candidate artifact | Benefit of schema protection | Risk of over-constraining | Affected files in a future PR | Likely tests | Current status |
| --- | --- | --- | --- | --- | --- |
| DCF output | Protects an upstream generated contract with formulas, assumptions used, source references, warnings, and bear/base/bull scenario outputs. Helps downstream fair value, reports, summaries, and audits trust the shape of DCF results. | Moderate. A schema must support both calculated outputs and blocked outputs without freezing internal formula text too tightly. | `config/`, `scripts/dcf_model.py`, `tests/test_dcf_model.py`, possibly `docs/SCHEMA_FIELD_REFERENCE.md`. | Valid calculated DCF output, blocked DCF output, missing required field, missing source reference metadata, scenario shape. | Implemented. |
| Fair value per share output | Protects a compact downstream artifact with clear source traceability to share count and DCF output. | Moderate. It depends on DCF output, so hardening it before DCF output leaves its upstream input less formalized. | `config/`, `scripts/fair_value_per_share.py`, `tests/test_fair_value_per_share.py`. | Valid output, missing scenario field, missing share count source reference, disclaimer present. | Implemented. |
| Model rating output | Protects market-price-derived model output and source snapshot references. | Moderate. It depends on fair value per share and should not be treated as advice or a price target. | `config/`, `scripts/model_rating.py`, `tests/test_model_rating.py`. | Valid output, unavailable/error paths, market price source reference, no prohibited language. | Implemented. |
| Model confidence output | Protects assumption-quality and guardrail-sensitive reasons/warnings. | Higher. Confidence output can evolve as data-quality rules evolve, and an early schema could freeze explainability fields too tightly. | `config/`, `scripts/model_confidence.py`, `tests/test_model_confidence.py`. | A/B/C/D outputs, manual-review assumption quality, stale market price reasons, source references. | Implemented for successful generated artifacts. |
| Model signal output | Protects the most user-facing model classification boundary. | Higher. Signal availability depends on rating, confidence, assumptions, and market freshness; schema hardening should follow upstream output contracts. | `config/`, `scripts/model_signal.py`, `tests/test_model_signal.py`. | Positive/neutral/negative/unavailable, blocking reasons, no recommendation language. | Implemented for the current generated signal object. |
| Audit log | Confirms reproducibility fields and append-only records. | Low to moderate. It already has `validate_audit_record`, so a new schema may duplicate existing validation unless a concrete consumer needs it. | `config/`, `scripts/write_audit_log.py`, `tests/test_write_audit_log.py`. | Required fields, type checks, append-only behavior. | Expectations-only; standalone schema deferred unless a concrete consumer needs it. |

## DCF Output Schema Hardening Status

The DCF output recommendation has been partially implemented:

- `config/dcf_output_schema.json` defines the standalone DCF output contract.
- `scripts/dcf_model.py` validates calculated and blocked DCF outputs against
  the contract.
- DCF tests cover valid calculated output, valid blocked output, missing
  required fields, invalid numeric fields, and missing source-reference
  metadata.
- v1.0 demo tests validate generated NVDA, AMD, and TSMC DCF output artifacts
  against the contract.

This covers DCF output only. It does not add schemas for fair value per share,
model rating, model confidence, model signal, audit log, analysis summary, or
fact report artifacts.

## Fair Value Per Share Schema Hardening Status

The fair value per share output recommendation has been partially implemented:

- `config/fair_value_per_share_output_schema.json` defines the standalone fair
  value per share output contract.
- `scripts/fair_value_per_share.py` validates generated fair value per share
  outputs against the contract.
- Fair value tests cover valid output, missing required fields, and invalid
  numeric fields.
- v1.0 demo tests validate generated NVDA, AMD, and TSMC fair value per share
  output artifacts against the contract.

This covers fair value per share output only. It does not add schemas for model
rating, model confidence, model signal, audit log, analysis summary, or fact
report artifacts.

## Model Rating Schema Hardening Status

The model rating output recommendation has been partially implemented:

- `config/model_rating_output_schema.json` defines the standalone model rating
  output contract.
- `scripts/model_rating.py` validates generated model rating outputs against
  the contract.
- Model rating tests cover valid output, missing required fields, invalid field
  types, source-reference preservation, and prohibited-language boundaries.
- v1.0 demo tests validate generated NVDA, AMD, and TSMC model rating output
  artifacts against the contract.

This covers model rating output only. It does not add schemas for model
confidence, model signal, audit log, analysis summary, or fact report artifacts.

## Model Confidence Schema Hardening Status

The model confidence output recommendation has been partially implemented:

- `config/model_confidence_output_schema.json` defines the standalone model
  confidence output contract for successful generated artifacts.
- `scripts/model_confidence.py` validates generated model confidence outputs
  against the contract.
- Model confidence tests cover valid output, manual-review assumption quality,
  missing required fields, invalid field types, invalid confidence enum values,
  missing assumption-quality fields, missing source-reference metadata, and
  prohibited-language boundaries.
- v1.0 demo tests validate generated NVDA, AMD, and TSMC model confidence output
  artifacts against the contract.

This covers successful model confidence output only. It does not add schemas for
model signal, audit log, analysis summary, or fact report artifacts. It also
does not define a durable blocked or unavailable model confidence artifact
contract because the current artifact layout does not generate one.

## Model Signal Schema Assessment Status

`docs/MODEL_SIGNAL_OUTPUT_SCHEMA_ASSESSMENT.md` now reviews the current model
signal output shape, observed generated demo artifacts, guardrail-sensitive
fields, available/unavailable state coverage, investment-advice boundaries, and
likely tests for a future implementation PR.

The assessment found that a narrow model signal output contract is safe if it
validates only the normal generated signal object shape, current non-advice
signal enum values, nullable upstream-output summaries, guardrail disclaimer,
and string-array reason fields. It should not freeze exact reason text, change
signal behavior, introduce new signal labels, or add buy/sell/hold,
recommendation, price target, or investment-advice wording.

## Model Signal Schema Hardening Status

The model signal output recommendation has been implemented for the normal
generated model signal object:

- `config/model_signal_output_schema.json` defines the standalone model signal
  output contract.
- `scripts/model_signal.py` validates generated model signal outputs against
  the contract.
- Model signal tests cover active `model_positive`, `model_neutral`, and
  `model_negative` outputs, unavailable outputs, nullable upstream summaries,
  missing required fields, invalid field types, invalid signal enum values,
  missing nested upstream fields, and prohibited-language boundaries.
- v1.0 demo tests validate generated NVDA, AMD, and TSMC model signal output
  artifacts against the contract.

This covers the normal generated model signal object only. It does not add
schemas for audit log, analysis summary, or fact report artifacts. It also does
not define a separate durable CLI error artifact contract.

## Audit Log Schema Need Assessment Status

`docs/AUDIT_LOG_SCHEMA_NEED_ASSESSMENT.md` now reviews the generated
`audit_log.jsonl` shape, existing validator coverage, stable top-level envelope,
flexible diagnostic payloads, report artifact boundary, and compatibility risks
of over-constraining append-only audit records.

The assessment recommends documenting audit log expectations without standalone
schema enforcement for now. The current top-level audit envelope already has
direct validation in `scripts/write_audit_log.py`, focused tests in
`tests/test_write_audit_log.py`, demo layout coverage in
`tests/test_run_v1_0_demo.py`, and orchestrator evidence coverage in
`tests/test_run_analysis.py`. Nested `validation_status`, `ratio_outputs`, and
`research_gaps_detected` should remain flexible unless a concrete future
consumer requires stricter machine-readable validation.

`docs/AUDIT_LOG_EXPECTATIONS.md` now documents the stable audit log envelope,
intentionally flexible diagnostic content, why no standalone schema is enforced
yet, and conditions that could justify a future schema.

## Analysis Summary Schema Need Assessment Status

`docs/ANALYSIS_SUMMARY_SCHEMA_NEED_ASSESSMENT.md` now reviews generated
NVDA, AMD, and TSMC `analysis_summary.json` artifacts, the stable report-facing
envelope, flexible explanatory and diagnostic fields, report artifact contract
boundary, compatibility risks, and likely tests for a future implementation PR.

The assessment recommends a narrow standalone analysis summary schema/contract.
The schema should protect the required top-level fields, named section groups,
section field presence, and broad field types while leaving embedded output
details, source references, warnings, research gaps, blocker text, timestamps,
paths, and audit references flexible. Embedded DCF, fair value per share, model
rating, model confidence, and model signal details should continue to rely on
their own contracts rather than being duplicated wholesale inside the analysis
summary schema.

## Analysis Summary Schema Hardening Status

The analysis summary output recommendation has been implemented for the current
generated analysis summary artifact:

- `config/analysis_summary_output_schema.json` defines the standalone analysis
  summary output contract.
- `scripts/generate_analysis_summary.py` validates generated analysis summaries
  against the contract before writing.
- Analysis summary tests cover valid output, missing required top-level fields,
  invalid required top-level field types, missing required section fields, and
  nullable optional upstream outputs.
- v1.0 demo tests validate generated NVDA, AMD, and TSMC analysis summary
  artifacts against the contract.
- v1.0 demo tests also verify that generated analysis summary source-reference
  sections preserve current evidence fields for ratio, DCF, fair value per
  share, model rating, and model confidence references.

This covers the analysis summary report-facing envelope and broad section field
types only. It does not duplicate the nested DCF, fair value per share, model
rating, model confidence, or model signal contracts inside the summary schema.
It also does not add schemas for audit log or fact report artifacts.

## Fact Report Contract Need Assessment Status

`docs/FACT_REPORT_CONTRACT_NEED_ASSESSMENT.md` now reviews generated NVDA, AMD,
and TSMC fact report Markdown artifacts, stable report headings, flexible prose
and diagnostic sections, guardrail coverage, and compatibility risks of
parser-backed Markdown validation.

The assessment recommends a narrow fact report expectations document rather
than a Markdown parser, schema, or validator. The expectations document should
document required report-level sections, optional calculation/model sections,
flexible wording areas, and no-advice guardrails while leaving machine-readable
contracts to the lower-level JSON artifacts.

`docs/FACT_REPORT_EXPECTATIONS.md` now documents the generated fact report
Markdown role, stable sections, optional calculation/model sections, flexible
content, guardrail expectations, why no parser/schema/validator is added yet,
and when a future heading-level contract could become justified.

## Generated Artifact Manifest Assessment Status

`docs/GENERATED_ARTIFACT_MANIFEST_ASSESSMENT.md` now reviews whether the
project should introduce a persisted generated artifact manifest for report
bundles.

The assessment classifies a possible manifest as **Run Metadata / Operational
Artifact**, not as a Report Contract and not as a replacement for the audit
log. It identifies candidate artifact inventory fields, fields that should
remain flexible, lifecycle expectations, ownership boundaries, and compatibility
risks.

The assessment recommends **defer**. Current `run_analysis`,
`run_batch_analysis`, and `run_v1_0_demo` results already expose generated
artifact paths; `docs/REPORT_ARTIFACT_CONTRACT.md` documents the report bundle
layout; v1.0 demo tests protect required artifact presence; and audit log and
fact report expectations document their own artifact roles. A manifest should
wait until a concrete consumer or review gap exists.

## Recommended Next Step

Recommend exactly one next step:

**Defer generated artifact manifest implementation.**

Do not open a manifest implementation PR until a concrete consumer, review
workflow, adapter, packaging workflow, or release validation gap requires a
persisted manifest. If that need appears, start with a narrow follow-up
assessment or expectations PR that defines the consumer, manifest lifecycle,
partial-run semantics, and minimal field set before adding runtime generation.

## Keep For Later

Do not reopen these without a fresh concrete need:

- all generated JSON outputs at once
- analysis summary nested upstream-output internals beyond broad type checks
- fact report Markdown parser or schema implementation before expectations are
  documented and proven insufficient
- audit log schema implementation unless the assessment identifies a concrete
  need
- generated artifact manifest implementation until a concrete consumer or
  review gap requires persisted run metadata

Do not add:

- live market data fetching
- adapters or framework code
- MCP or A2A implementation
- new companies
- package rename or publishing
- price targets
- buy/sell/hold recommendations
- personal investment advice
- trading, broker/order, or portfolio logic

