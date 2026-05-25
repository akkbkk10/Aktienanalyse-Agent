# Model Signal Output Schema Assessment

This assessment reviews the current generated model signal JSON artifact and
recommends whether a narrow schema/contract implementation is safe. It is
documentation-only and does not implement a schema, change runtime behavior,
change tests, change CI, or change generated report wording.

## Source Files And Artifacts Inspected

- `AGENTS.md`
- `README.md`
- `docs/GENERATED_OUTPUT_SCHEMA_ASSESSMENT.md`
- `docs/REPORT_ARTIFACT_CONTRACT.md`
- `docs/SCHEMA_FIELD_REFERENCE.md`
- `docs/ARCHITECTURE_GOVERNANCE_INDEX.md`
- `config/model_rating_output_schema.json`
- `config/model_confidence_output_schema.json`
- `config/model_signal_rules.json`
- `scripts/model_signal.py`
- `scripts/run_analysis.py`
- `scripts/run_batch_analysis.py`
- `scripts/run_v1_0_demo.py`
- `tests/test_model_signal.py`
- `tests/test_run_v1_0_demo.py`
- generated demo outputs under
  `reports/tmp_model_signal_schema_assessment_demo/`

Generated outputs were used for assessment only and remain ignored by git.

## Current Generated Output Shape

The v1.0 demo currently writes one model signal JSON artifact per supported
ticker:

- `NVDA_model_signal_output.json`
- `AMD_model_signal_output.json`
- `TSMC_model_signal_output.json`

The observed top-level fields are:

| Field | Observed type | Current meaning |
| --- | --- | --- |
| `ticker` | string | Uppercase ticker for the analyzed company. |
| `model_signal` | string | Signal bucket, currently one of `model_positive`, `model_neutral`, `model_negative`, or `unavailable`. |
| `reasons` | array of strings | Explanations for the deterministic signal result or unavailable state. |
| `blocking_reasons` | array of strings | Reasons an active signal is unavailable. Empty for active test outputs. |
| `model_rating_used` | object or null | Compact copy of the model rating fields used by the signal calculation. |
| `model_confidence_used` | object or null | Compact copy of the model confidence fields used by the signal calculation. |
| `rules_version` | string | Rule config version used by the calculation. |
| `warnings` | array of strings | Guardrail warnings, including assumption-quality blocking warnings. |
| `disclaimer` | string | Output boundary disclaimer: non-personalized model output, not investment advice. |

The observed `model_rating_used` object contains:

| Field | Observed type | Current meaning |
| --- | --- | --- |
| `model_rating` | number | Rating bucket from model rating output. |
| `rating_label` | string | Non-personalized model rating label. |
| `valuation_gap_percent` | number | Deterministic valuation gap used by signal rules. |
| `rules_version` | string | Model rating rule version. |

The observed `model_confidence_used` object contains:

| Field | Observed type | Current meaning |
| --- | --- | --- |
| `model_confidence` | string | Confidence bucket from model confidence output. |
| `confidence_label` | string | Human-readable model quality label. |
| `confidence_score` | number | Deterministic confidence score. |
| `assumption_quality` | object | Assumption review status and active-signal gate. |
| `rules_version` | string | Model confidence rule version. |

The nested `assumption_quality` object currently carries the same signal gate
fields protected by the model confidence output contract:

- `status`
- `active_signal_allowed`
- `matched_terms`
- `blocking_reasons`

## Observed States

The current generated NVDA, AMD, and TSMC demo artifacts all exist and are
successful generated model signal artifacts, but their `model_signal` value is
`unavailable`.

Observed generated state:

| Ticker | `model_signal` | `model_rating_used.model_rating` | `model_confidence_used.model_confidence` | `assumption_quality.status` | Blocking source |
| --- | --- | ---: | --- | --- | --- |
| `NVDA` | `unavailable` | 1 | `C` | `manual_review_required` | Assumption quality gate did not pass. |
| `AMD` | `unavailable` | 1 | `C` | `manual_review_required` | Assumption quality gate did not pass. |
| `TSMC` | `unavailable` | 5 | `C` | `manual_review_required` | Assumption quality gate did not pass. |

No current demo artifact shows an active `model_positive`, `model_neutral`, or
`model_negative` signal because example/manual-review assumptions set
`assumption_quality.active_signal_allowed` to `false`.

Active states do exist in the current code and tests:

- `tests/test_model_signal.py` covers `model_positive`.
- `tests/test_model_signal.py` covers `model_neutral`.
- `tests/test_model_signal.py` covers `model_negative`.
- `tests/test_model_signal.py` covers `unavailable` when confidence is `D`.
- `tests/test_model_signal.py` covers `unavailable` when rating is missing.
- `tests/test_model_signal.py` covers `unavailable` when market price is stale.
- `tests/test_model_signal.py` covers `unavailable` when high-priority research
  gaps remain open.
- `tests/test_model_signal.py` covers `unavailable` when manual-review
  assumptions block active output.

No separate durable blocked or unavailable error artifact exists outside the
normal generated model signal object. CLI load or validation failures can return
an error object with `calculated: false` and `error`, but that CLI error object
is not part of the durable per-ticker report artifact layout.

## Investment-Advice Guardrails

The current model signal output avoids investment advice through both output
shape and tests:

- Signal values are limited by `config/model_signal_rules.json` to
  `model_positive`, `model_neutral`, `model_negative`, and `unavailable`.
- The output disclaimer is `non-personalized model output, not investment
  advice.`
- `scripts/model_signal.py` rejects prohibited terms in serialized output:
  `price target`, `buy`, `sell`, `hold`, and `recommendation`.
- `tests/test_model_signal.py` checks that generated signal output does not
  include buy/sell/hold wording, price targets, recommendations, or investment
  advice wording beyond the disclaimer.
- Manual-review assumptions block active signals and produce `unavailable`
  output in the current demo artifacts.

These guardrails should remain behavioral tests, not merely schema constraints.
A future schema should protect shape and allowed enum values without adding new
signal names, price targets, or recommendation-style labels.

## Stable Fields For Future Contract Protection

These fields appear stable enough for a narrow future schema:

- required top-level fields:
  - `ticker`
  - `model_signal`
  - `reasons`
  - `blocking_reasons`
  - `model_rating_used`
  - `model_confidence_used`
  - `rules_version`
  - `warnings`
  - `disclaimer`
- `model_signal` as enum values `model_positive`, `model_neutral`,
  `model_negative`, and `unavailable`
- `reasons`, `blocking_reasons`, and `warnings` as arrays of strings, without
  freezing exact text
- `model_rating_used` as an object when rating is available, with
  `model_rating`, `rating_label`, `valuation_gap_percent`, and `rules_version`
- `model_rating_used` as `null` when rating is unavailable
- `model_confidence_used` as an object when confidence is available, with
  `model_confidence`, `confidence_label`, `confidence_score`,
  `assumption_quality`, and `rules_version`
- `model_confidence_used` as `null` when confidence is unavailable
- nested `assumption_quality` shape when present:
  `status`, `active_signal_allowed`, `matched_terms`, and `blocking_reasons`
- `disclaimer` as the current non-personalized model-output disclaimer

## Guardrail-Sensitive Fields

These fields should remain flexible or be constrained carefully:

- `model_signal`: the enum can be constrained to current allowed values, but a
  future schema must not introduce buy/sell/hold or recommendation wording.
- `reasons`: reason text is guardrail-sensitive and should not be frozen
  exactly. Tests should continue checking prohibited language.
- `blocking_reasons`: blocker text may evolve as data quality, confidence, and
  assumption gates evolve. A schema should require array shape, not exact text.
- `warnings`: warning text may evolve and should remain string-array based.
- `model_rating_used.rating_label`: labels come from model rating output and
  should remain typed as strings without freezing exact wording in the signal
  schema.
- `model_confidence_used.confidence_label`: labels come from model confidence
  output and should remain typed as strings without freezing exact wording in
  the signal schema.
- `model_confidence_used.assumption_quality`: this object is central to the
  active-signal guardrail. A future signal schema can require the current gate
  fields, but active-signal behavior should stay protected by model signal and
  model confidence tests.
- `model_rating_used` and `model_confidence_used`: both must allow `null` for
  unavailable-input states because current code supports missing upstream
  outputs.

## Comparison To Existing Schema Patterns

The model rating and model confidence contracts are useful patterns because
they:

- use standalone config files under `config/`
- validate required top-level fields
- validate compact nested objects
- preserve source and rule-version traceability where the artifact carries it
- keep scoring, thresholds, labels, and generated wording outside schema logic
- preserve prohibited-language tests as behavioral guardrails

Model signal has higher implementation risk than model rating and model
confidence because:

- it is the most user-facing generated model classification
- active `model_positive` and `model_negative` labels can be misunderstood if
  extended into advice wording
- availability depends on upstream rating, confidence, assumptions, research
  gaps, and market price freshness
- generated demo artifacts currently cover only the `unavailable` manual-review
  path, while active positive, neutral, and negative paths are covered by unit
  tests rather than durable demo artifacts

The risk is manageable if the implementation is narrow and validates only shape,
types, allowed signal enum values, nested upstream-output summaries, nullable
unavailable-input states, and the disclaimer. A future implementation should
not freeze exact reason text or change signal behavior.

## Likely Tests For A Future Implementation PR

A future implementation PR should add focused tests for:

- valid `model_positive` output satisfies the contract
- valid `model_neutral` output satisfies the contract
- valid `model_negative` output satisfies the contract
- valid `unavailable` output satisfies the contract when confidence is `D`
- valid `unavailable` output satisfies the contract when model rating is
  missing and `model_rating_used` is `null`
- valid `unavailable` output satisfies the contract when model confidence is
  missing and `model_confidence_used` is `null`
- manual-review assumption quality output satisfies the contract
- missing required top-level field fails validation
- invalid top-level type fails validation
- invalid `model_signal` enum value fails validation
- missing nested rating field fails validation when `model_rating_used` is an
  object
- missing nested confidence field fails validation when `model_confidence_used`
  is an object
- v1.0 demo generated NVDA, AMD, and TSMC model signal artifacts satisfy the
  contract
- prohibited-language tests remain unchanged

The implementation should not add a separate blocked artifact contract unless
runtime behavior first creates a durable blocked model signal artifact outside
the normal generated output object.

## Recommendation

Recommended next step: implement a narrow model signal output schema/contract.

Safe implementation scope:

- Add a standalone `config/model_signal_output_schema.json`.
- Add validation helper logic in `scripts/model_signal.py`.
- Validate the normal generated model signal object, including `unavailable`
  outputs.
- Require stable top-level fields and carefully typed nested upstream-output
  summaries.
- Require `model_signal` to remain one of the current non-advice enum values.
- Allow `model_rating_used` and `model_confidence_used` to be `null` when
  upstream outputs are unavailable.
- Keep `reasons`, `blocking_reasons`, `warnings`, and upstream label text
  flexible as strings or arrays of strings rather than exact text.
- Add focused contract tests and v1.0 demo artifact validation.

Do not include:

- model signal behavior changes
- signal threshold changes
- new signal labels
- buy/sell/hold wording
- price targets
- investment advice
- model confidence changes
- model rating changes
- DCF or fair value changes
- report wording changes
- schema work for audit log, analysis summary, or fact report
- live fetching
- adapters
- trading or portfolio logic
