# Generated Output Schema Assessment

This assessment reviews the generated JSON artifacts produced by the current
deterministic v1.0/v1.1 baseline and recommends one narrow next artifact type
for future schema hardening. It is documentation-only. It does not implement
schemas, change generated outputs, change runtime logic, add tests, or change
CI.

## Source Files Inspected

- `AGENTS.md`
- `docs/V1_1_CANDIDATE_PLAN.md`
- `docs/REPORT_ARTIFACT_CONTRACT.md`
- `docs/DATA_CONTRACT_SCHEMA_HARDENING_ASSESSMENT.md`
- `docs/SCHEMA_FIELD_REFERENCE.md`
- `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md`
- `docs/ARCHITECTURE_GOVERNANCE_INDEX.md`
- `scripts/run_v1_0_demo.py`
- `scripts/run_analysis.py`
- `scripts/run_batch_analysis.py`
- `scripts/dcf_model.py`
- `scripts/fair_value_per_share.py`
- `scripts/model_rating.py`
- `scripts/write_audit_log.py`
- `tests/test_run_v1_0_demo.py`

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

## Classification

| Artifact area | Classification | Reason |
| --- | --- | --- |
| DCF output | Stable generated contract candidate | It is a core upstream JSON output consumed by fair value per share, reports, and summaries. |
| Fair value per share output | Stable generated contract candidate | It is a downstream calculated JSON output with source-linked share count inputs. |
| Model rating output | Stable generated contract candidate | It is a rule-based JSON output using fair value per share and market price snapshots. |
| Model confidence output | Stable generated contract candidate | It carries guardrail-sensitive assumption quality and confidence reasons. |
| Model signal output | Stable generated contract candidate | It is guardrail-sensitive and must remain unavailable under manual-review assumptions. |
| Audit log | Already has direct validator coverage | `scripts/write_audit_log.py` includes `validate_audit_record` and required-field tests. |
| Runtime company contexts under reports | Internal generated implementation detail | The v1.0 demo may create runtime contexts under the reports directory, but the durable context contract lives in `config/company_context_schema.json`. |
| Research queues under reports | Internal/generated implementation detail | Batch runs may create queue files; they are not part of the stable per-ticker report artifact contract. |
| Fact report Markdown | Documentation-reviewed only for now | It is user-facing prose and should remain protected by generated-output review and forbidden-output tests, not a JSON schema. |
| Analysis summary JSON | Documentation-reviewed only for now | It aggregates several outputs and is broad enough that schema work should wait until lower-level generated outputs are hardened first. |

## Candidate Assessment

| Candidate artifact | Benefit of schema protection | Risk of over-constraining | Affected files in a future PR | Likely tests | Timing |
| --- | --- | --- | --- | --- | --- |
| DCF output | Protects an upstream generated contract with formulas, assumptions used, source references, warnings, and bear/base/bull scenario outputs. Helps downstream fair value, reports, summaries, and audits trust the shape of DCF results. | Moderate. A schema must support both calculated outputs and blocked outputs without freezing internal formula text too tightly. | `config/`, `scripts/dcf_model.py`, `tests/test_dcf_model.py`, possibly `docs/SCHEMA_FIELD_REFERENCE.md`. | Valid calculated DCF output, blocked DCF output, missing required field, missing source reference metadata, scenario shape. | Do next. |
| Fair value per share output | Protects a compact downstream artifact with clear source traceability to share count and DCF output. | Moderate. It depends on DCF output, so hardening it before DCF output leaves its upstream input less formalized. | `config/`, `scripts/fair_value_per_share.py`, `tests/test_fair_value_per_share.py`. | Valid output, missing scenario field, missing share count source reference, disclaimer present. | Later, after DCF output. |
| Model rating output | Protects market-price-derived model output and source snapshot references. | Moderate. It depends on fair value per share and should not be treated as advice or a price target. | `config/`, `scripts/model_rating.py`, `tests/test_model_rating.py`. | Valid output, unavailable/error paths, market price source reference, no prohibited language. | Later. |
| Model confidence output | Protects assumption-quality and guardrail-sensitive reasons/warnings. | Higher. Confidence output can evolve as data-quality rules evolve, and an early schema could freeze explainability fields too tightly. | `config/`, `scripts/model_confidence.py`, `tests/test_model_confidence.py`. | A/B/C/D outputs, manual-review assumption quality, stale market price reasons, source references. | Later. |
| Model signal output | Protects the most user-facing model classification boundary. | Higher. Signal availability depends on rating, confidence, assumptions, and market freshness; schema hardening should follow upstream output contracts. | `config/`, `scripts/model_signal.py`, `tests/test_model_signal.py`. | Positive/neutral/negative/unavailable, blocking reasons, no recommendation language. | Later. |
| Audit log | Confirms reproducibility fields and append-only records. | Low to moderate. It already has `validate_audit_record`, so a new schema may duplicate existing validation unless a concrete consumer needs it. | `config/`, `scripts/write_audit_log.py`, `tests/test_write_audit_log.py`. | Required fields, type checks, append-only behavior. | Later only if JSONL contract consumers need it. |

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

## Recommended Next Implementation PR

Recommend exactly one next implementation target:

**Model rating output schema/contract assessment.**

Small safe scope for the future implementation PR:

- Review the current model rating JSON artifact now that DCF output and fair
  value per share output have contract protection.
- Keep the first pass assessment-only unless a concrete missing guardrail is
  found.
- Do not change model rating behavior, fair value calculations, DCF math,
  report wording, CLI behavior, or CI.

Why this should be next:

- Model rating is the next direct consumer of fair value per share output and
  validated market price snapshots.
- It is narrower than model confidence, model signal, or full analysis summary
  hardening.
- Assessment-first keeps the project from broadening into every generated JSON
  artifact at once.

## Keep For Later

Do not harden these in the next implementation PR:

- all generated JSON outputs at once
- analysis summary schema
- fact report Markdown schema
- model rating, confidence, or signal schemas
- audit log schema unless a concrete JSONL consumer needs it
- generated artifact manifest

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

