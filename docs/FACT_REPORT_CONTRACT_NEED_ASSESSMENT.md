# Fact Report Contract Need Assessment

This assessment reviews the current generated fact report Markdown artifact and
recommends whether it needs a contract, schema, or expectations document. It is
documentation-only and does not implement a Markdown parser, schema, validator,
runtime change, test change, CI change, or report wording change.

Implementation status: implemented as expectations documentation.
`docs/FACT_REPORT_EXPECTATIONS.md` now documents the stable fact report role,
sections, flexible content, guardrails, and why no Markdown parser, schema, or
validator is added yet.

## Source Files And Artifacts Inspected

- `AGENTS.md`
- `README.md`
- `docs/REPORT_ARTIFACT_CONTRACT.md`
- `docs/GENERATED_OUTPUT_SCHEMA_ASSESSMENT.md`
- `docs/SCHEMA_FIELD_REFERENCE.md`
- `docs/ARCHITECTURE_GOVERNANCE_INDEX.md`
- `docs/AUDIT_LOG_EXPECTATIONS.md`
- `docs/V1_1_3_RELEASE_NOTES.md`
- `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md`
- `scripts/generate_report.py`
- `scripts/run_analysis.py`
- `scripts/run_batch_analysis.py`
- `scripts/run_v1_0_demo.py`
- `tests/test_generate_report.py`
- `tests/test_forbidden_output_regression.py`
- `tests/test_run_analysis.py`
- `tests/test_run_v1_0_demo.py`
- generated demo fact reports under
  `reports/tmp_fact_report_contract_need_assessment_demo/`

Generated outputs were used for assessment only and remain ignored by git.

## Current Fact Report Shape

The v1.0 demo writes one Markdown fact report per supported ticker:

- `NVDA_fact_report.md`
- `AMD_fact_report.md`
- `TSMC_fact_report.md`

The observed generated reports share the same heading structure:

```text
# <TICKER> Fact Report
## Facts
### Validation Status
### Calculated Ratios
### Source References
### DCF Calculation Output
#### Assumptions Used
#### Scenario Outputs
#### DCF Formulas
#### DCF Warnings
#### DCF Source References
### Fair Value Per Share Model Calculation
#### Scenario Calculations
#### Fair Value Per Share Formula
#### Fair Value Per Share Warnings
#### Fair Value Per Share Source References
### Model Rating
#### Model Rating Assumptions
#### Model Rating Warnings
#### Model Rating Source References
### Model Confidence
#### Model Confidence Reasons
#### Model Confidence Warnings
#### Model Confidence Source References
### Model Signal
#### Model Signal Reasons
#### Model Signal Blocking Reasons
#### Model Signal Inputs
#### Model Signal Warnings
## Missing Data
## Warnings
## Boundary
```

Observed generated report size:

| Ticker | Generated report | Line count | Guardrail scan |
| --- | --- | ---: | --- |
| `NVDA` | `NVDA_fact_report.md` | 251 | No prohibited terms after allowing existing `not investment advice` disclaimers. |
| `AMD` | `AMD_fact_report.md` | 252 | No prohibited terms after allowing existing `not investment advice` disclaimers. |
| `TSMC` | `TSMC_fact_report.md` | 252 | No prohibited terms after allowing existing `not investment advice` disclaimers. |

All three generated reports include:

- a ticker-specific H1
- generated timestamp, ticker, and audit log reference
- facts section
- validation status
- calculated ratios
- source references
- DCF calculation output
- clearly labeled assumptions used
- scenario outputs
- formulas
- DCF warnings and source references
- fair value per share model calculation
- model rating
- model confidence
- model signal
- missing data
- warnings
- boundary statement

## Existing Protection

The fact report already has runtime and test guardrails:

- `scripts/generate_report.py` renders the Markdown report from structured
  inputs.
- `scripts/generate_report.py` rejects prohibited language in generated report
  text, including `price target`, `buy`, `sell`, `hold`, `recommendation`, and
  `investment advice` after allowing the existing `not investment advice`
  disclaimer phrase.
- `tests/test_generate_report.py` covers report creation, source references,
  missing data, DCF inclusion and exclusion, DCF assumptions, DCF warnings,
  model rating, model confidence, model signal, fair value per share, and
  prohibited-language boundaries.
- `tests/test_forbidden_output_regression.py` scans generated user-facing
  artifacts for forbidden phrases.
- `tests/test_run_v1_0_demo.py` verifies that each supported ticker writes a
  fact report artifact under the configured reports directory.
- `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md` documents manual review expectations
  for generated reports and summaries.

## Stable Sections Suitable For Expectations

The current generated reports have stable user-facing sections that are
suitable for a documentation-level expectations boundary:

- ticker-specific H1: `# <TICKER> Fact Report`
- run metadata bullets:
  - generated timestamp
  - ticker
  - audit log reference
- `## Facts`
- `### Validation Status`
- `### Calculated Ratios`
- `### Source References`
- optional upstream model/calculation sections when their artifacts are
  available:
  - `### DCF Calculation Output`
  - `### Fair Value Per Share Model Calculation`
  - `### Model Rating`
  - `### Model Confidence`
  - `### Model Signal`
- `## Missing Data`
- `## Warnings`
- `## Boundary`

These section expectations would help reviewers confirm that the Markdown
report remains navigable and guardrail-aware without freezing every line of
prose or every nested output detail.

## Flexible Sections

These report areas should remain flexible:

- exact timestamp values
- audit log reference paths and line values
- ratio ordering and ratio values
- source reference wording and source URL details
- DCF assumptions, forecast values, scenario values, formulas, warnings, and
  source references
- fair value per share scenario values, formulas, warnings, and source
  references
- model rating labels, assumptions, warnings, and source references
- model confidence reasons, labels, warnings, and source references
- model signal reasons, blocking reasons, input summaries, and warnings
- missing data and research-gap wording
- general warning text
- boundary wording, as long as it remains no-advice and no-trading

The Markdown report is user-facing prose assembled from already-contracted JSON
artifacts. Over-constraining the prose would make safe wording edits expensive
and could duplicate lower-level JSON contracts inside a fragile text parser.

## Guardrail Assessment

The generated fact report preserves the current project guardrails:

- No buy/sell/hold recommendations were observed in NVDA, AMD, or TSMC reports.
- No price targets were observed.
- No investment-advice wording was observed after allowing the current
  `not investment advice` disclaimer phrase.
- Assumptions are shown under clearly labeled assumption sections, especially
  `#### Assumptions Used` for DCF output.
- Missing data is visible under `## Missing Data`.
- General warnings are visible under `## Warnings`.
- Calculation-specific warnings are visible in DCF, fair value per share, model
  rating, model confidence, and model signal sections when present.
- The boundary section states that the report is fact-only and contains no
  directional call or advice.

These guardrails should remain protected primarily by runtime prohibited-term
checks, forbidden-output regression tests, generated-output review, and any
future expectations document. A parser-backed Markdown contract should not be
the first hardening step.

## Comparison To Analysis Summary Contract

`analysis_summary.json` was a strong contract candidate because it is a
structured JSON artifact with a stable report-facing envelope and section
fields. A schema can validate its shape without parsing prose.

The fact report Markdown output has a different risk profile:

- It is user-facing and guardrail-sensitive.
- It is prose-heavy.
- It is generated from structured artifacts that now have their own contracts
  or documented expectations.
- It already has prohibited-language tests and generated-output review
  guidance.
- A parser-backed validator would add complexity and could overfit current
  wording.

The stable part of the Markdown report is the heading and section layout, not
the exact prose under every heading.

## Contract Options

| Option | Assessment |
| --- | --- |
| No contract or expectations | Too weak. The report is user-facing and guardrail-sensitive, so reviewers need a durable statement of expected sections and boundaries. |
| Expectations document only | Best next step. It can document stable headings, optional sections, flexible prose, and guardrails without adding parser complexity. |
| Heading/section-level contract | Potentially useful later, but should follow an expectations document and should be implemented only if section drift becomes a recurring risk. |
| Parser-backed validation contract | Too heavy now. It would add complexity, risk over-constraining prose, and duplicate lower-level JSON contracts. |

## Recommendation

Recommended next step: completed as a narrow fact report expectations document.

Implemented scope:

- `docs/FACT_REPORT_EXPECTATIONS.md` documents the current generated Markdown
  report role and path pattern
- stable sections such as facts, missing data, warnings, and
  boundary
- optional calculation/model sections that appear when upstream artifacts
  are available
- exact wording, source details, warnings, reasons, blocker text,
  timestamps, paths, and financial values flexible
- lower-level JSON artifacts remain the source of truth for
  machine-readable contracts
- guardrails against price targets, buy/sell/hold recommendations,
  investment advice, live fetching, broker/order behavior, and trading logic
  are documented

Do not implement a Markdown parser, schema, or validator yet. A heading-level
contract can be reconsidered later if the expectations document and existing
tests are not enough to prevent section drift.

Do not include:

- report wording changes
- runtime code changes
- test changes
- CI changes
- financial logic changes
- model rating, model confidence, or model signal changes
- DCF or fair value changes
- audit log schema work
- generated reports
- release notes
- tags
- live fetching
- adapters
- investment advice
- trading or portfolio logic
