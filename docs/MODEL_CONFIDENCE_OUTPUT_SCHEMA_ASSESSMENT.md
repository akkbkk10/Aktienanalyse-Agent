# Model Confidence Output Schema Assessment

This assessment reviews the current generated model confidence JSON artifact and
recommends whether a narrow schema/contract implementation is safe. It is
documentation-only and does not implement a schema, change runtime behavior,
change tests, change CI, or change generated report wording.

## Source Files And Artifacts Inspected

- `AGENTS.md`
- `README.md`
- `docs/V1_1_X_NEXT_CANDIDATE_PLAN.md`
- `docs/GENERATED_OUTPUT_SCHEMA_ASSESSMENT.md`
- `docs/REPORT_ARTIFACT_CONTRACT.md`
- `docs/SCHEMA_FIELD_REFERENCE.md`
- `docs/ARCHITECTURE_GOVERNANCE_INDEX.md`
- `docs/V1_1_1_RELEASE_NOTES.md`
- `config/model_rating_output_schema.json`
- `config/model_confidence_rules.json`
- `scripts/model_confidence.py`
- `scripts/run_analysis.py`
- `scripts/run_batch_analysis.py`
- `scripts/run_v1_0_demo.py`
- `tests/test_model_confidence.py`
- `tests/test_run_v1_0_demo.py`
- generated demo outputs under
  `reports/tmp_model_confidence_schema_assessment_demo/`

Generated outputs were used for assessment only and remain ignored by git.

## Current Generated Output Shape

The v1.0 demo currently writes one model confidence JSON artifact per supported
ticker:

- `NVDA_model_confidence_output.json`
- `AMD_model_confidence_output.json`
- `TSMC_model_confidence_output.json`

The observed top-level fields are:

| Field | Observed type | Current meaning |
| --- | --- | --- |
| `ticker` | string | Uppercase ticker for the analyzed company. |
| `model_confidence` | string | Confidence bucket, currently one of `A`, `B`, `C`, or `D`. |
| `confidence_label` | string | Human-readable model quality label from `config/model_confidence_rules.json`. |
| `confidence_score` | number | Deterministic score after deductions and caps. |
| `reasons` | array of strings | Explanations for deductions or a positive default reason. |
| `warnings` | array of strings | Guardrail warnings, including assumption-quality warnings. |
| `rules_version` | string | Rule config version used by the calculation. |
| `assumption_quality` | object | Assumption review status and signal-availability gate. |
| `source_references` | array of objects | Source references copied from company context metrics. |
| `disclaimer` | string | Output boundary disclaimer: model quality output, not investment advice. |

The observed `assumption_quality` fields are:

| Field | Observed type | Current meaning |
| --- | --- | --- |
| `status` | string | Assumption quality status, such as `sufficient`, `manual_review_required`, `incomplete`, or `missing_or_unreadable`. |
| `active_signal_allowed` | boolean | Whether assumption quality allows active directional model signal output. |
| `matched_terms` | array of strings | Manual-review keywords matched in assumption labels or notes. |
| `blocking_reasons` | array of strings | Reasons assumption quality blocks active signal output. |

The observed `source_references` fields are:

| Field | Observed type | Current meaning |
| --- | --- | --- |
| `metric_id` | string | Stable source metric identifier. |
| `metric_name` | string | Source metric display name. |
| `metric_category` | string or null | Metric category, such as `financial_metric`, `share_count`, or `market_price`. |
| `period` | string | Source metric period. |
| `unit` | string | Source metric unit. |
| `source_url` | string | Source URL. |
| `source_type` | string | Source type. |
| `source_date` | date string | Source publication or filing date. |
| `last_verified` | date string | Last verification date. |
| `confidence` | string | Source confidence. |

Market price source references also include:

- `currency`
- `exchange`
- `price_type`
- `as_of_datetime`
- `fetched_at`
- `provider`
- `retrieval_method`

## Available And Blocked States

Available model confidence artifacts exist in the current demo. NVDA, AMD, and
TSMC each generate a model confidence artifact with:

- `model_confidence` set to `C`
- `assumption_quality.status` set to `manual_review_required`
- `assumption_quality.active_signal_allowed` set to `false`
- a warning that reviewed assumptions are needed before active directional
  output

The demo does not currently generate a separate unavailable or blocked model
confidence artifact. `scripts/model_confidence.py` can print a CLI error object
with `calculated: false` and `error` when input loading or validation fails, but
that error object is not part of the durable per-ticker report artifact layout.

`tests/test_model_confidence.py` covers successful A, B, C, and D confidence
bucket outputs, stale market price deductions, high-priority research gap
deductions, missing/incomplete assumptions, manual-review assumptions, source
reference timestamp preservation, and prohibited-language boundaries.

## Stable Fields For Future Contract Protection

These fields appear stable enough for a narrow future schema:

- required top-level fields:
  - `ticker`
  - `model_confidence`
  - `confidence_label`
  - `confidence_score`
  - `reasons`
  - `warnings`
  - `rules_version`
  - `assumption_quality`
  - `source_references`
  - `disclaimer`
- `model_confidence` as enum values `A`, `B`, `C`, and `D`
- `confidence_score` as a number within the configured score floor/ceiling
- `reasons` and `warnings` as arrays of strings, without freezing exact text
- `assumption_quality.status` as a string with the current known statuses
- `assumption_quality.active_signal_allowed` as a boolean
- `assumption_quality.matched_terms` as an array of strings
- `assumption_quality.blocking_reasons` as an array of strings
- base `source_references` metadata fields required by current output:
  `metric_id`, `metric_name`, `metric_category`, `period`, `unit`,
  `source_url`, `source_type`, `source_date`, `last_verified`, and
  `confidence`
- market price source reference timestamp and provider fields when the source
  reference is a market price record
- `disclaimer` as the current non-personalized model quality disclaimer

## Guardrail-Sensitive Fields

These fields should remain flexible or be constrained carefully:

- `confidence_label`: should be typed as a string, but the exact labels may
  evolve with `config/model_confidence_rules.json`.
- `confidence_score`: should be numeric, but schema should not freeze deduction
  math or bucket thresholds beyond a broad score range.
- `reasons`: reason text is guardrail-sensitive explainability and should not be
  frozen exactly. A schema should require an array of strings and tests should
  continue checking prohibited language.
- `warnings`: warning text may evolve as assumption-quality and evidence rules
  improve. A schema should require an array of strings and preserve
  prohibited-language tests.
- `assumption_quality.status`: current known statuses can be enumerated, but the
  schema should allow a deliberate future update when assumption quality rules
  evolve.
- `assumption_quality.matched_terms`: matched keywords should be typed, but a
  schema should not require specific terms because the keyword list is a rule
  config concern.
- `source_references`: financial, share count, and market price references have
  overlapping but not identical fields. A schema should avoid requiring market
  price-only fields on non-market references.

## Comparison To Model Rating Schema Pattern

The existing model rating output contract is a useful pattern because it:

- defines a small standalone config file
- validates required top-level fields
- validates nested assumption and source-reference fields
- preserves market price snapshot traceability
- leaves rating behavior and threshold rules unchanged

Model confidence has higher implementation risk than model rating because:

- it carries broader explainability through `reasons` and `warnings`
- it depends on source validation, research gaps, metric confidence, assumption
  quality, and market price freshness
- it can produce A/B/C/D outputs instead of a single market-price-derived rating
- its manual-review language is a guardrail boundary used by model signal

The risk is still manageable if the implementation is narrow and validates
shape, types, source traceability, assumption-quality structure, and disclaimer
without freezing exact reason text or changing confidence behavior.

## Likely Tests For A Future Implementation PR

A future implementation PR should add focused tests for:

- valid A, B, C, and D model confidence outputs satisfy the contract
- manual-review assumption quality output satisfies the contract
- missing or incomplete assumption quality output satisfies the contract when
  generated by `calculate_model_confidence`
- stale market price warning output satisfies the contract
- source references preserve base metric fields
- market price source references preserve `as_of_datetime`, `fetched_at`,
  `provider`, and `retrieval_method`
- missing required top-level field fails validation
- invalid top-level type fails validation
- missing nested `assumption_quality` field fails validation
- missing source-reference metadata fails validation
- v1.0 demo generated NVDA, AMD, and TSMC model confidence artifacts satisfy the
  contract
- prohibited-language tests remain unchanged

The implementation should not add a blocked artifact contract unless runtime
behavior first creates a durable blocked model confidence artifact. Current CLI
error output should remain outside the stable per-ticker artifact contract.

## Recommendation

Recommended next step: implement a narrow model confidence output
schema/contract.

Safe implementation scope:

- Add a standalone `config/model_confidence_output_schema.json`.
- Add validation helper logic in `scripts/model_confidence.py`.
- Validate successful generated model confidence outputs only.
- Require stable top-level fields and carefully typed nested structures.
- Require base source-reference traceability fields.
- Require market price timestamp/provider fields only for market price source
  references.
- Keep `reasons`, `warnings`, labels, and matched terms flexible as arrays or
  strings rather than exact text.
- Add focused contract tests and v1.0 demo artifact validation.

Do not include:

- model confidence behavior changes
- score deduction changes
- confidence bucket changes
- assumption-quality rule changes
- model rating changes
- model signal changes
- DCF or fair value changes
- report wording changes
- schema work for model signal, audit log, analysis summary, or fact report
- live fetching
- adapters
- investment advice
- trading or portfolio logic

