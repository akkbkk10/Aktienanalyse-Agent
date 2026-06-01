# v1.1.x Next Candidate Plan

This document is a historical planning assessment for the implementation block
after the v1.1.0 contract/schema hardening release. It is documentation-only.
It does not approve runtime behavior changes, schema changes, tests, CI
changes, release tags, or publishing changes by itself.

## Historical Status

This plan has been superseded by later v1.1.x work through v1.1.5. The model
rating, model confidence, model signal, audit log expectations, analysis
summary, fact report expectations, and generated artifact manifest assessment
work described here has either been implemented, documented as expectations
only, or explicitly deferred in later docs.

Use `docs/GENERATED_OUTPUT_SCHEMA_ASSESSMENT.md` for current generated-output
contract and deferral status. Use this document only as historical context for
why the v1.1.x generated-output sequence started with model rating.

## Current v1.1.0 Baseline

The deterministic core supports NVDA, AMD, and TSMC with source validation,
company context generation, research gap detection, ratios, valuation
readiness, DCF, fair value per share, model rating, model confidence, model
signal, fact-only reports, structured summaries, and audit logs.

The project has 203 tests. The v1.1.0 block added durable contract/schema
protection for:

- generated artifact layout: `docs/REPORT_ARTIFACT_CONTRACT.md`
- company context files: `config/company_context_schema.json`
- DCF outputs: `config/dcf_output_schema.json`
- fair value per share outputs:
  `config/fair_value_per_share_output_schema.json`

Model rating, model confidence, model signal, audit log, analysis summary, and
fact report schema hardening remain future work. The next block should continue
the narrow generated-output contract sequence without changing financial logic
or model behavior.

## Candidate Blocks

| Candidate | Benefit | Risk | Affected files | Likely tests | Timing |
| --- | --- | --- | --- | --- | --- |
| Model rating/confidence/signal output contracts | Extends contract protection to the remaining rule-based model JSON outputs after DCF and fair value per share. Model rating is the narrowest next artifact because it directly consumes fair value output and market price snapshots. | Moderate if all three outputs are bundled together; confidence and signal are guardrail-sensitive and can over-constrain explainability fields if rushed. | `config/`, `scripts/model_rating.py`, `scripts/model_confidence.py`, `scripts/model_signal.py`, `tests/test_model_rating.py`, `tests/test_model_confidence.py`, `tests/test_model_signal.py`, `docs/SCHEMA_FIELD_REFERENCE.md`. | Valid output, unavailable/blocked output where applicable, missing required field, invalid numeric/structured field, source-reference preservation, prohibited-language guardrails. | Do now, but only for model rating output first. |
| Generated output review hardening | Improves reviewer confidence that user-facing reports, summaries, and model outputs stay within guardrails. | Can become noisy if it broadens forbidden-phrase tests or scans docs where prohibited terms are intentionally discussed. | `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md`, `docs/GUARDRAIL_SECURITY_TEST_PLAN.md`, `tests/test_forbidden_output_regression.py`. | Focused generated-artifact checks only if a concrete gap is found. | Later, after the next narrow JSON contract. |
| CLI user guidance | Helps users discover the current workflow and understand generated outputs. | Low, but can duplicate `--help` content or drift into CLI behavior changes. | `README.md`, possibly maintainer docs. | Existing CLI help and invalid-argument smoke tests. | Later, only if user-facing confusion appears. |
| Adapter RFC preparation | Keeps future Market Data Agent, MCP, A2A, or framework work behind explicit proposal, data-contract, risk, and decision records. | High if it turns into adapter design or implementation before output contracts are stable. | `docs/ADAPTER_PROPOSAL_CHECKLIST.md`, `docs/DATA_CONTRACT_REVIEW_CHECKLIST.md`, `docs/ADAPTER_RISK_REGISTER_TEMPLATE.md`, `docs/ADAPTER_DECISION_RECORD_TEMPLATE.md`. | Docs-only initially; adapter tests only after an approved RFC. | Later. |
| Open-source readiness cleanup | Improves contributor flow and maintainer ergonomics without touching core behavior. | Low, but lower priority than finishing the current generated-output contract sequence. | `CONTRIBUTING.md`, `SECURITY.md`, `.github/ISSUE_TEMPLATE/`, `.github/pull_request_template.md`, README. | Usually none beyond the full test suite unless templates change expected workflow. | Later. |

## Historical Recommended Implementation Block

At the time this plan was written, PR #83 was recommended to implement
**model rating output schema/contract hardening**.

Small safe scope for PR #83:

- Add a standalone model rating output schema/contract using the existing
  `config/*_schema.json` pattern.
- Validate the current model rating output shape only.
- Support unavailable or blocked model rating behavior only if the current
  artifact already exposes that shape.
- Add focused tests in `tests/test_model_rating.py` for valid output, missing
  required field, invalid numeric or structured field, source-reference
  preservation, and prohibited-language boundaries.
- Validate generated NVDA, AMD, and TSMC model rating artifacts in the existing
  v1.0 demo test path if practical.
- Update `docs/GENERATED_OUTPUT_SCHEMA_ASSESSMENT.md` and
  `docs/SCHEMA_FIELD_REFERENCE.md` only as needed.

Why this should be next:

- It directly follows the implemented fair value per share contract.
- It is narrower and less guardrail-sensitive than model confidence or model
  signal output contracts.
- It protects market-price-derived output traceability without changing rating
  rules, labels, thresholds, or generated report wording.

## Proposed PR Sequence

1. **PR #83: Model Rating Output Schema / Contract**
   Add the smallest safe schema/contract and focused tests for the current
   model rating JSON artifact.

2. **PR #84: Model Confidence Output Schema Assessment**
   Assess whether confidence output is stable enough for a standalone contract,
   especially around assumption-quality reasons and warnings.

3. **PR #85: Model Confidence Output Schema / Contract**
   Implement confidence output contract protection only if PR #84 identifies a
   narrow stable shape.

4. **PR #86: Model Signal Output Schema Assessment**
   Assess signal output after rating and confidence contracts are in place,
   with special attention to unavailable/manual-review behavior.

## Not Yet

Do not build these in the next block:

- live market data fetching
- web UI
- framework adapters
- MCP or A2A implementation
- runtime agent code
- package rename or project rename
- package publishing
- new companies
- price targets
- buy/sell/hold recommendations
- personal investment advice
- trading, broker/order, or portfolio logic

These areas should remain in planning or RFC mode until the generated-output
contracts, data-contract expectations, adapter proposal process, risk register,
and decision records justify implementation.
