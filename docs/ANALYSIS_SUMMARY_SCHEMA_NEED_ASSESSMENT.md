# Analysis Summary Schema Need Assessment

This assessment reviews the current generated `analysis_summary.json` artifact
and recommends whether a standalone analysis summary schema/contract is needed.
It was originally created as a documentation-only assessment and did not
implement a schema, change runtime behavior, change tests, change CI, or change
generated report wording.

Implementation status: implemented for the current generated analysis summary
artifact. `config/analysis_summary_output_schema.json` now defines the
standalone contract and `scripts/generate_analysis_summary.py` validates
generated summaries against it before writing. The implementation protects the
report-facing envelope and section field types only; embedded upstream output
internals, warnings, source-reference details, research-gap details, timestamps,
paths, and audit references remain flexible.

## Source Files And Artifacts Inspected

- `AGENTS.md`
- `README.md`
- `docs/REPORT_ARTIFACT_CONTRACT.md`
- `docs/GENERATED_OUTPUT_SCHEMA_ASSESSMENT.md`
- `docs/SCHEMA_FIELD_REFERENCE.md`
- `docs/ARCHITECTURE_GOVERNANCE_INDEX.md`
- `docs/AUDIT_LOG_SCHEMA_NEED_ASSESSMENT.md`
- `docs/AUDIT_LOG_EXPECTATIONS.md`
- `scripts/generate_analysis_summary.py`
- `scripts/run_analysis.py`
- `scripts/run_batch_analysis.py`
- `scripts/run_v1_0_demo.py`
- `tests/test_generate_analysis_summary.py`
- `tests/test_forbidden_output_regression.py`
- `tests/test_run_v1_0_demo.py`
- generated demo summaries under
  `reports/tmp_analysis_summary_schema_need_assessment_demo/`

Generated outputs were used for assessment only and remain ignored by git.

## Current Analysis Summary Shape

The v1.0 demo currently writes one analysis summary JSON artifact per supported
ticker:

- `NVDA_analysis_summary.json`
- `AMD_analysis_summary.json`
- `TSMC_analysis_summary.json`

The observed top-level fields are the same for NVDA, AMD, and TSMC:

| Field | Observed type | Current meaning |
| --- | --- | --- |
| `ticker` | string | Uppercase ticker for the analyzed company. |
| `generated_at` | string | UTC summary generation timestamp. |
| `audit_log_reference` | string | Reference to the shared audit log record for the run. |
| `facts` | object | Validation and source-reference facts used by the summary. |
| `assumptions` | object | Availability flags and assumption payloads for calculated outputs. |
| `calculated_outputs` | object | Ratio, DCF, fair value per share, model rating, model confidence, and model signal outputs when available. |
| `missing_data` | object | Research gaps, availability statuses, unavailable reasons, and model signal blockers. |
| `risks_warnings` | object | General and artifact-specific warnings. |

The observed `facts` object contains:

- `validation_status`
- `ratio_source_references`
- `dcf_source_references`
- `fair_value_per_share_source_references`
- `model_rating_source_references`
- `model_confidence_source_references`

The observed `assumptions` object contains:

- `dcf_assumptions`
- `dcf_available`
- `fair_value_per_share_assumptions`
- `fair_value_per_share_available`
- `model_rating_assumptions`
- `model_rating_available`
- `model_rating_status`
- `model_confidence_available`
- `model_signal_available`

The observed `calculated_outputs` object contains:

- `ratios`
- `dcf_scenarios`
- `fair_value_per_share_scenarios`
- `model_rating`
- `model_confidence`
- `model_signal`

The observed `missing_data` object contains:

- `research_gaps`
- `dcf_status`
- `fair_value_per_share_status`
- `model_rating_status`
- `model_rating_unavailable_reasons`
- `model_confidence_status`
- `model_signal_status`
- `model_signal_blocking_reasons`

The observed `risks_warnings` object contains:

- `warnings`
- `dcf_warnings`
- `fair_value_per_share_warnings`
- `model_rating_warnings`
- `model_confidence_warnings`
- `model_signal_warnings`

In the generated NVDA, AMD, and TSMC demo summaries:

- DCF output is included.
- Fair value per share output is included.
- Model rating output is included.
- Model confidence output is included.
- Model signal output is included, with `model_signal` set to `unavailable`
  because the current manual-review assumption quality gate blocks active
  signals.
- Each summary contains nine ratio outputs.
- Each summary contains ten de-duplicated ratio source references.
- No research gaps are present in the observed demo run.
- Warning counts vary by ticker because TSMC carries an additional free cash
  flow source warning.

## Report Artifact Contract Boundary

`analysis_summary.json` is part of the per-ticker report artifact contract.
`docs/REPORT_ARTIFACT_CONTRACT.md` documents it as a required per-ticker JSON
artifact in the v1.0 demo layout, and `tests/test_run_v1_0_demo.py` verifies
that each supported ticker writes an `analysis_summary_path`.

This makes the analysis summary different from `audit_log.jsonl`. The audit log
is a shared append-only operational artifact whose stable top-level envelope is
already validated by `scripts/write_audit_log.py`. The analysis summary is a
per-ticker report-facing JSON artifact that aggregates facts, assumptions,
calculated outputs, missing data, and warnings for downstream review.

## Stable Fields Suitable For Future Contract Protection

These top-level fields appear stable enough for narrow contract protection:

- `ticker`
- `generated_at`
- `audit_log_reference`
- `facts`
- `assumptions`
- `calculated_outputs`
- `missing_data`
- `risks_warnings`

These section fields also appear stable enough for a narrow future schema:

- `facts.validation_status`
- `facts.ratio_source_references`
- `facts.dcf_source_references`
- `facts.fair_value_per_share_source_references`
- `facts.model_rating_source_references`
- `facts.model_confidence_source_references`
- `assumptions.dcf_assumptions`
- `assumptions.dcf_available`
- `assumptions.fair_value_per_share_assumptions`
- `assumptions.fair_value_per_share_available`
- `assumptions.model_rating_assumptions`
- `assumptions.model_rating_available`
- `assumptions.model_rating_status`
- `assumptions.model_confidence_available`
- `assumptions.model_signal_available`
- `calculated_outputs.ratios`
- `calculated_outputs.dcf_scenarios`
- `calculated_outputs.fair_value_per_share_scenarios`
- `calculated_outputs.model_rating`
- `calculated_outputs.model_confidence`
- `calculated_outputs.model_signal`
- `missing_data.research_gaps`
- `missing_data.dcf_status`
- `missing_data.fair_value_per_share_status`
- `missing_data.model_rating_status`
- `missing_data.model_rating_unavailable_reasons`
- `missing_data.model_confidence_status`
- `missing_data.model_signal_status`
- `missing_data.model_signal_blocking_reasons`
- `risks_warnings.warnings`
- `risks_warnings.dcf_warnings`
- `risks_warnings.fair_value_per_share_warnings`
- `risks_warnings.model_rating_warnings`
- `risks_warnings.model_confidence_warnings`
- `risks_warnings.model_signal_warnings`

A future schema should focus on required field presence and broad types:

- strings for `ticker`, `generated_at`, `audit_log_reference`, and status
  fields
- booleans for availability flags
- arrays for source references, ratios, research gaps, unavailable reasons,
  blocking reasons, and warnings
- objects for section groups and available embedded outputs
- object or null for optional upstream assumption/output payloads where current
  code can omit an upstream artifact

## Flexible Explanatory And Diagnostic Fields

These fields should remain flexible because they carry explanatory,
diagnostic, or implementation-specific payloads:

- exact `generated_at` timestamp values
- exact `audit_log_reference` path and line values
- `facts.validation_status.errors`
- source-reference object internals
- ratio output object internals
- embedded DCF output details, which are already protected by the DCF output
  contract
- embedded fair value per share output details, which are already protected by
  the fair value per share output contract
- embedded model rating output details, which are already protected by the model
  rating output contract
- embedded model confidence output details, which are already protected by the
  model confidence output contract
- embedded model signal output details, which are already protected by the model
  signal output contract
- `research_gaps` object internals
- `model_rating_unavailable_reasons` exact wording
- `model_signal_blocking_reasons` exact wording
- all warning text

The summary is an aggregate artifact. A schema that duplicates the full nested
contracts for every embedded output would increase compatibility risk and make
summary maintenance harder without adding much protection beyond the existing
lower-level contracts.

## Comparison To Existing Contract Patterns

The analysis summary is a stronger schema candidate than the audit log because
it is a required per-ticker report artifact rather than a shared operational
JSONL log. It also lacks the direct standalone validator coverage that currently
protects the audit log envelope.

The analysis summary is broader than model rating, model confidence, and model
signal outputs. Those artifacts have focused contract boundaries and can safely
validate detailed nested objects. The summary aggregates several artifacts, so
its contract should be narrower:

- protect the top-level envelope
- protect the named section groups
- protect broad section field types
- rely on existing lower-level schemas for embedded DCF, fair value per share,
  model rating, model confidence, and model signal details
- preserve existing prohibited-language tests as behavioral guardrails

## Compatibility Risks

Over-constraining `analysis_summary.json` could create avoidable churn because:

- it aggregates several upstream artifacts whose internals can evolve under
  their own contracts
- explanatory warnings and blocker text may need to change as guardrails evolve
- source-reference and research-gap details are diagnostic and may change with
  data-contract work
- optional upstream artifacts may be unavailable in non-demo runs
- exact timestamps, paths, and audit references naturally vary by run and
  platform

The highest-value contract boundary is therefore the summary envelope and
section map, not the complete nested content.

## Likely Tests For A Future Implementation PR

A future implementation PR should add focused tests for:

- valid generated summary output satisfies the contract
- generated NVDA, AMD, and TSMC demo summaries satisfy the contract
- missing required top-level field fails validation
- missing required section field fails validation
- invalid type for a required top-level section fails validation
- invalid type for an availability flag fails validation
- invalid type for a warning or source-reference array fails validation
- optional embedded upstream outputs can be object or null where current runtime
  paths support missing upstream artifacts
- existing forbidden-output regression tests remain unchanged

The implementation should not change analysis summary wording, add new summary
fields, change upstream model behavior, or duplicate every lower-level output
schema inside the summary schema.

## Recommendation

Recommended next step: completed for the current generated analysis summary
artifact.

The current analysis summary shape was stable enough for narrow hardening
because NVDA, AMD, and TSMC generated summaries share the same top-level
envelope and section fields, and lower-level generated outputs already have
their own contracts. The implemented standalone schema reduces regression risk
for a required per-ticker report artifact by protecting the summary envelope,
section separation, and broad field types.

Implemented scope:

- `config/analysis_summary_output_schema.json` defines the standalone
  analysis summary output contract
- `scripts/generate_analysis_summary.py` validates generated analysis summary
  artifacts against the schema
- the stable top-level fields and section fields listed above are required
- keep embedded output details flexible or defer to their own existing schemas
- keep source references, warnings, research gaps, blocker text, timestamps,
  paths, and audit references flexible
- generated NVDA, AMD, and TSMC demo summaries validate against the contract
- focused negative tests cover missing required fields and invalid required
  field types

Do not include:

- analysis summary wording changes
- financial logic changes
- model rating, model confidence, or model signal changes
- DCF or fair value changes
- audit log schema enforcement
- fact report Markdown schema work
- CI changes
- release notes
- tags
- live fetching
- adapters
- investment advice
- trading or portfolio logic
