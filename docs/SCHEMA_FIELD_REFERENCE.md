# Schema Field Reference

This document summarizes the current deterministic core data contracts. It is a
field reference, not a schema change. When a formal schema exists, the section
points to it. When no formal schema exists yet, the section is labeled as the
current observed structure from scripts and sample artifacts.

All financial figures must preserve source, date, unit, period, currency, and
confidence metadata where applicable. Assumptions must stay clearly separated
from sourced facts and calculated outputs. Future adapter-provided data must
conform to these field-level traceability expectations before deterministic core
modules use it.

Related docs:

- `docs/DATA_CONTRACT_REVIEW_CHECKLIST.md`
- `docs/CORE_BASELINE_INVENTORY.md`
- `docs/ADAPTER_PROPOSAL_CHECKLIST.md`
- `docs/GUARDRAIL_SECURITY_TEST_PLAN.md`

## Financial Metric Records

Formal schema: `config/financial_metric_schema.json`

| Field | Required | Type | Meaning | Source/traceability expectation | Example |
| --- | --- | --- | --- | --- | --- |
| `company` | required | string | Company name in raw metric records. | Identifies source company before context build. | `NVIDIA Corporation` |
| `ticker` | required | string | Ticker symbol. | Must match the company being processed. | `NVDA` |
| `metric_id` | required | string | Stable technical identifier. | Preserved through context and downstream outputs. | `nvda_revenue_fy2025` |
| `metric_name` | required | string | Human-readable metric name. | Should remain descriptive, but `metric_id` is the stable reference. | `Revenue` |
| `metric_category` | optional | enum string | Metric category. | Used for specialized handling of `financial_metric`, `share_count`, or `market_price`. | `financial_metric` |
| `value` | required | number | Numeric metric value. | Must not appear without source metadata. | `130497` |
| `unit` | required | string | Measurement unit. | Must make scale explicit. | `USD millions` |
| `period` | required | string | Fiscal or observation period. | Must be unambiguous enough for comparisons. | `FY2025 ended 2025-01-26` |
| `accounting_basis` | required | enum string | Accounting basis. | Must separate GAAP, Non-GAAP, IFRS, and Other. | `GAAP` |
| `statement_type` | required | enum string | Fact, assumption, or opinion label. | Facts and assumptions must remain separate. | `fact` |
| `source_url` | required | string | Source URL. | Required for every sourced financial number. | `https://investor.nvidia.com/...` |
| `source_type` | required | enum string | Source category. | Must be allowed by `config/source_rules.json`. | `earnings release` |
| `source_date` | required | date string | Source publication or filing date. | Used for freshness and traceability. | `2025-02-26` |
| `last_verified` | required | date string | Date the record was last checked. | Used for stale-source validation. | `2026-05-23` |
| `confidence` | required | enum string | Source confidence. | Allowed values are `low`, `medium`, `high`. | `high` |
| `notes` | optional | string | Human-readable notes. | Must not replace structured source metadata. | `Prior-period sample data...` |

## Market Price Snapshot Records

Formal schema: `config/market_price_snapshot_schema.json`

Market prices are stored snapshots, not live quotes. `as_of_datetime` is the
time the price refers to. `fetched_at` is the time this system stored or
retrieved the snapshot.

| Field | Required | Type | Meaning | Source/traceability expectation | Example |
| --- | --- | --- | --- | --- | --- |
| `ticker` | required | string | Ticker symbol. | Must match the company context. | `NVDA` |
| `metric_id` | required | string | Stable market price input identifier. | Referenced by model rating outputs. | `nvda_current_market_price_2026_05_23` |
| `value` | required | number | Market price value. | Must come from stored snapshot data. | `215.33` |
| `currency` | required | string | Price currency. | Must be explicit for model rating. | `USD` |
| `exchange` | required | string | Exchange or venue. | Identifies where the price applies. | `NASDAQ` |
| `price_type` | required | enum string | Type of price snapshot. | One of `close`, `latest_trade`, `opening`, `intraday_snapshot`. | `latest_trade` |
| `as_of_datetime` | required | date-time string | Timestamp the price refers to. | Preserved in rating/report/summary references. | `2026-05-23T00:15:00Z` |
| `fetched_at` | required | date-time string | Timestamp this system stored or retrieved the snapshot. | Used for freshness checks. | `2026-05-24T00:00:00Z` |
| `source_url` | required | string | Snapshot source URL. | Required for market price source traceability. | `https://www.nasdaq.com/...` |
| `source_date` | required | date string | Date associated with the source snapshot. | Must align with source evidence. | `2026-05-23` |
| `provider` | required | string | Data provider or source name. | Required for future adapter accountability. | `Nasdaq` |
| `retrieval_method` | required | enum string | How the snapshot was obtained. | One of `manual_snapshot`, `file_import`, `market_data_agent`. | `manual_snapshot` |
| `confidence` | required | enum string | Source confidence. | Allowed values are `low`, `medium`, `high`. | `high` |
| `last_verified` | required | date string | Date the snapshot record was verified. | Used for validation and review. | `2026-05-24` |

## Company Context Records

Formal schema/contract: `config/company_context_schema.json`.

Company context files are built from validated source metrics by
`scripts/build_company_context.py`. The contract documents the current context
shape and protects the handoff from source validation into downstream
deterministic analysis modules.

| Field | Required | Type | Meaning | Source/traceability expectation | Example |
| --- | --- | --- | --- | --- | --- |
| `schema_version` | required | string | Context schema version. | Helps identify context format. | `0.1.0` |
| `ticker` | required | string | Ticker symbol. | Must match context directory. | `NVDA` |
| `company_name` | required | string | Company name. | Copied from source metrics. | `NVIDIA Corporation` |
| `last_updated` | required | date string | Context build/update date. | Identifies context freshness. | `2026-05-24` |
| `metrics` | required | array | Sourced metric records in context shape. | Preserves `metric_id`, value, unit, period, basis, statement type, and source metadata. | `[ ... ]` |
| `source_metadata` | required | object | Context-level source file metadata. | Records source file and metric count. | `{"source_file": "...", "metric_count": 12}` |

Metric objects in context place source fields under `source_metadata`:

| Field | Required | Type | Meaning | Source/traceability expectation | Example |
| --- | --- | --- | --- | --- | --- |
| `metric_id` | required | string | Stable metric identifier. | Downstream references use this field. | `nvda_free_cash_flow_fy2025` |
| `metric_name` | required | string | Human-readable metric name. | Used in reports and summaries. | `Free cash flow` |
| `metric_category` | optional | string | Specialized metric category. | Required for share count and market price behavior. | `share_count` |
| `value` | required | number | Numeric value. | Must trace back to source metadata. | `60724` |
| `unit` | required | string | Unit and scale. | Must remain explicit. | `USD millions` |
| `period` | required | string | Fiscal or observation period. | Must be unambiguous. | `FY2025 ended 2025-01-26` |
| `source_metadata` | required | object | Source URL/type/date/verification/confidence. | Required for traceability. | `{...}` |

## DCF Assumption/Input Records

Formal validation config: `config/dcf_assumptions_schema.json`. The config is a
custom validation contract, not a JSON Schema object.

| Field | Required | Type | Meaning | Source/traceability expectation | Example |
| --- | --- | --- | --- | --- | --- |
| `schema_version` | required | string | Assumption file version. | Must match expected config version. | `0.1.0` |
| `ticker` | required | string | Ticker symbol. | Must match the requested ticker. | `NVDA` |
| `company_name` | observed | string | Company name. | Present in sample assumptions for readability. | `NVIDIA Corporation` |
| `unit` | required | string | Unit for DCF values. | Must be explicit for downstream fair value. | `USD millions` |
| `assumption_label` | observed | string | Assumption quality label. | Example/manual-review labels affect confidence and signal behavior. | `Example assumptions...` |
| `assumption_notes` | observed | array | Assumption review notes. | Must not be treated as sourced fact. | `[ "These are clearly labeled..." ]` |
| `source_references` | required | array | Source metrics supporting inputs. | Must include `metric_id`, metric name, period, source URL/date, confidence. | `[ ... ]` |
| `scenarios` | required | object | Bear/base/bull assumptions. | Each scenario is explicit and not invented at runtime. | `{ "base": {...} }` |

Scenario fields:

| Field | Required | Type | Meaning | Source/traceability expectation | Example |
| --- | --- | --- | --- | --- | --- |
| `discount_rate` | required | number | Scenario discount rate. | Explicit assumption, not sourced fact. | `0.1` |
| `terminal_growth_rate` | required | number | Scenario terminal growth rate. | Explicit assumption, not sourced fact. | `0.03` |
| `starting_free_cash_flow` | required | number | Starting free cash flow. | Should reference a source metric where applicable. | `60724` |
| `forecast_years` | required | array | Explicit forecast free cash flows. | Assumptions requiring manual review. | `[{"year": 1, "free_cash_flow": 66000}]` |
| `starting_free_cash_flow_metric_id` | observed | string | Source metric for starting FCF. | Preserves metric traceability. | `nvda_free_cash_flow_fy2025` |

## DCF Output Records

Current observed structure from `scripts/dcf_model.py`.

| Field | Required | Type | Meaning | Source/traceability expectation | Example |
| --- | --- | --- | --- | --- | --- |
| `ticker` | required | string | Ticker symbol. | Matches DCF input ticker. | `NVDA` |
| `calculated` | required | boolean | Whether DCF calculation ran. | `false` output includes blocking reasons. | `true` |
| `schema_version` | observed when calculated | string | Assumption schema version used. | Traces output to input version. | `0.1.0` |
| `unit` | observed when calculated | string | Output unit. | Used by fair value per share. | `USD millions` |
| `formulas` | observed when calculated | object | Formula labels. | Documents deterministic calculations. | `{ "dcf_value": "..." }` |
| `assumptions_used` | observed when calculated | object | Assumption values used. | Keeps assumptions separate from facts. | `{...}` |
| `source_references` | observed when calculated | array | Source metric references. | Carries source URL/date/confidence and metric IDs. | `[ ... ]` |
| `source_metric_ids` | observed when calculated | array | Source metric IDs. | Enables compact traceability. | `["nvda_free_cash_flow_fy2025"]` |
| `warnings` | required | array | Calculation warnings. | Must not contain advice or recommendations. | `[ ... ]` |
| `scenarios` | required | object | Scenario outputs. | Contains deterministic scenario calculations. | `{ "base": {...} }` |
| `blocking_reasons` | observed when not calculated | array | Readiness blockers. | Explains why DCF did not run. | `[ "Valuation readiness gate did not pass." ]` |

## Fair Value Per Share Output Records

Current observed structure from `scripts/fair_value_per_share.py`.

| Field | Required | Type | Meaning | Source/traceability expectation | Example |
| --- | --- | --- | --- | --- | --- |
| `ticker` | required | string | Ticker symbol. | Matches source context and DCF output. | `NVDA` |
| `calculated` | required | boolean | Whether calculation completed. | Requires DCF output and share count. | `true` |
| `currency` | required | string | Output currency. | Derived from DCF output unit. | `USD` |
| `formulas` | required | object | Formula labels. | Documents deterministic arithmetic. | `{ "fair_value_per_share": "dcf_value_used / diluted_share_count_used" }` |
| `assumptions` | required | object | Input context used. | Includes share count unit/period/metric ID. | `{...}` |
| `warnings` | required | array | Output warnings. | States no share counts or assumptions were invented. | `[ ... ]` |
| `source_references` | required | array | Share count source references. | Preserves share count metric source metadata. | `[ ... ]` |
| `disclaimer` | required | string | Output boundary disclaimer. | Must state model output only, not investment advice. | `calculated model output only, not investment advice.` |
| `scenarios` | required | array | Per-scenario fair value outputs. | Each item references share count metric ID. | `[{"scenario": "base", ...}]` |

## Model Rating Output Records

Current observed structure from `scripts/model_rating.py`.

| Field | Required | Type | Meaning | Source/traceability expectation | Example |
| --- | --- | --- | --- | --- | --- |
| `ticker` | required | string | Ticker symbol. | Matches model input ticker. | `NVDA` |
| `model_rating` | required | number | Rule bucket. | Derived from fair value per share and market price snapshot. | `3` |
| `rating_label` | required | string | Non-personalized rating label. | Must not be buy/sell/hold language. | `fairly valued / neutral on model basis` |
| `fair_value_per_share_used` | required | number | Fair value input. | Must come from fair value per share output. | `100.0` |
| `market_price_used` | required | number | Market price input. | Must come from validated market price snapshot. | `100.0` |
| `valuation_gap_percent` | required | number | Calculated gap. | Deterministic formula from inputs. | `0.0` |
| `rules_version` | required | string | Rating rules version. | Traces output to config. | `0.1.0` |
| `assumptions` | required | object | Scenario and market price metadata used. | Includes market price metric ID, unit, period, timestamps, provider, retrieval method. | `{...}` |
| `warnings` | required | array | Output warnings. | Must not contain recommendations. | `[ ... ]` |
| `source_references` | required | array | Market price source references. | Preserves snapshot timestamps and source metadata. | `[ ... ]` |
| `disclaimer` | required | string | Output boundary disclaimer. | Non-personalized model output only. | `non-personalized model output, not investment advice.` |

## Model Confidence Output Records

Current observed structure from `scripts/model_confidence.py`.

| Field | Required | Type | Meaning | Source/traceability expectation | Example |
| --- | --- | --- | --- | --- | --- |
| `ticker` | required | string | Ticker symbol. | Matches context ticker. | `NVDA` |
| `model_confidence` | required | enum string | A-D model quality grade. | Derived from rule config and existing validated inputs. | `B` |
| `confidence_label` | required | string | Human-readable quality label. | Model quality only, not advice. | `solid data quality, normal uncertainty` |
| `confidence_score` | required | number | Numeric score before bucket label. | Deterministic score from rules. | `80` |
| `reasons` | required | array | Reasons for confidence grade. | Should mention data quality/gaps/freshness/assumptions. | `[ ... ]` |
| `warnings` | required | array | Confidence warnings. | Includes manual-review assumption warnings where applicable. | `[ ... ]` |
| `rules_version` | required | string | Confidence rules version. | Traces output to config. | `0.1.0` |
| `assumption_quality` | required | object | Assumption quality status. | Separates assumption review status from facts. | `{ "manual_review_required": true }` |
| `source_references` | required | array | Metric source references. | Includes market price timestamps where applicable. | `[ ... ]` |
| `disclaimer` | required | string | Output boundary disclaimer. | Model quality only, not investment advice. | `non-personalized model quality output, not investment advice.` |

## Model Signal Output Records

Current observed structure from `scripts/model_signal.py`.

| Field | Required | Type | Meaning | Source/traceability expectation | Example |
| --- | --- | --- | --- | --- | --- |
| `ticker` | required | string | Ticker symbol. | Matches model outputs. | `NVDA` |
| `model_signal` | required | enum string | Non-personalized signal label. | One of `model_positive`, `model_neutral`, `model_negative`, `unavailable`. | `unavailable` |
| `reasons` | required | array | Signal reasons. | Explains deterministic rule result. | `[ ... ]` |
| `blocking_reasons` | required | array | Reasons signal is unavailable. | Used when quality gates do not pass. | `[ ... ]` |
| `model_rating_used` | required | object or null | Rating information used. | Must come from model rating output. | `{...}` |
| `model_confidence_used` | required | object or null | Confidence information used. | Must come from model confidence output. | `{...}` |
| `rules_version` | required | string | Signal rules version. | Traces output to config. | `0.1.0` |
| `warnings` | required | array | Signal warnings. | Includes assumption quality warnings where applicable. | `[ ... ]` |
| `disclaimer` | required | string | Output boundary disclaimer. | Non-personalized model output only. | `non-personalized model output, not investment advice.` |

## Audit Log Records

Current observed structure from `scripts/write_audit_log.py`.

| Field | Required | Type | Meaning | Source/traceability expectation | Example |
| --- | --- | --- | --- | --- | --- |
| `timestamp` | required | date-time string | Audit record creation time. | Enables run chronology. | `2026-05-24T00:00:00Z` |
| `ticker` | required | string | Ticker symbol. | Identifies analyzed company. | `NVDA` |
| `methodology_version` | required | string | Methodology version used. | Traces run to methodology config. | `0.1.0` |
| `data_context_path` | required | string | Context file path used. | Enables reproduction of input context. | `data/companies/NVDA/context.json` |
| `source_files_used` | required | array | Source input files used. | Lists raw/sample files used in run. | `[ "data/nvda_sample_metrics.json" ]` |
| `validation_status` | required | object | Source validation result. | Records whether source validation passed. | `{ "valid": true }` |
| `ratio_outputs` | required | array | Ratio outputs included in run. | Preserves calculated ratio traceability. | `[ ... ]` |
| `research_gaps_detected` | required | array | Research gaps found. | Records missing/stale/low-confidence gaps. | `[ ... ]` |
| `git_commit_hash` | required | string or null | Git commit hash when available. | Connects run to repository state. | `abc123...` |

## Adapter Data Contract Boundary

Future adapter data must enter the deterministic core as explicit files,
records, or validated snapshots. Adapter outputs must not directly alter model
rating, model confidence, model signal, report wording, or audit behavior.

Before implementation, adapter proposals should use:

- `docs/ADAPTER_PROPOSAL_CHECKLIST.md`
- `docs/DATA_CONTRACT_REVIEW_CHECKLIST.md`
- `docs/GUARDRAIL_SECURITY_TEST_PLAN.md`

Generated artifacts may be reviewed locally, but they must remain under ignored
`reports/tmp_*` paths and must not be committed.
