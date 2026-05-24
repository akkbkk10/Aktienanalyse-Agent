# v1.1 Candidate Plan

This document is a planning assessment for the next implementation block after
the v1.0.9 maintenance baseline. It is not a roadmap commitment and does not
approve runtime behavior changes by itself.

## Current v1.0.9 Baseline

The deterministic core supports NVDA, AMD, and TSMC with source validation,
company context, research gaps, ratios, valuation readiness, DCF, fair value per
share, model rating, model confidence, model signal, fact-only reports,
structured summaries, and audit logs.

The project has 189 tests. Recent maintenance work strengthened CLI stability,
invalid-argument handling, v1.0 demo reports-directory behavior, generated
output guardrails, and CI diagnostics through named smoke and guardrail steps.

The next v1.1 candidate work should move away from tiny CI-only PRs unless a
clear diagnostic gap appears. The strongest next block is a small contract layer
for generated report artifacts.

## Candidate Blocks

| Candidate | Benefit | Risk | Affected files | Likely tests | Timing |
| --- | --- | --- | --- | --- | --- |
| Data contract / schema hardening | Tightens field-level expectations for source records, snapshots, contexts, and outputs before adapter work. | Can expand quickly into schema or validation behavior changes if not constrained. | `docs/SCHEMA_FIELD_REFERENCE.md`, `docs/DATA_CONTRACT_REVIEW_CHECKLIST.md`, possibly `config/` and validation tests in a later PR. | Schema/reference tests only if behavior changes later. | Later, after artifact expectations are explicit. |
| Report artifact contract | Makes generated output paths and required artifact names explicit for demo, batch, and per-ticker workflows. | Low if kept docs/test-only; moderate if it tries to change output paths. | New `docs/REPORT_ARTIFACT_CONTRACT.md`, `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md`, possibly `tests/test_run_v1_0_demo.py` in a later test PR. | Existing v1.0 demo tests, possible focused artifact-contract tests. | Do now. |
| CLI UX / user guidance | Helps users discover commands and expected outputs. | Can drift into CLI behavior changes or duplicate `--help` content. | `README.md`, CLI docs, maybe no code. | Existing CLI help smoke tests. | Later, after report artifact contract wording is stable. |
| Generated output review hardening | Strengthens reviewer checks for reports, summaries, model outputs, and audit logs. | Overly broad forbidden-phrase checks can create noisy tests. | `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md`, `docs/GUARDRAIL_SECURITY_TEST_PLAN.md`, possibly regression tests later. | `tests/test_forbidden_output_regression.py` if test scope changes. | Later, after artifact contract identifies exactly what to review. |
| Adapter RFC preparation | Prepares Market Data Agent, MCP, A2A, or framework evaluation work without implementation. | High if it starts designing adapter runtime details before contracts are stable. | `docs/ADAPTER_PROPOSAL_CHECKLIST.md`, `docs/ADAPTER_RISK_REGISTER_TEMPLATE.md`, `docs/ADAPTER_DECISION_RECORD_TEMPLATE.md`. | Docs-only initially; adapter tests only after an approved RFC. | Later. |

## Recommended Next Implementation Block

PR #75 should implement the **Report Artifact Contract** block.

Recommended scope for PR #75:

- Add `docs/REPORT_ARTIFACT_CONTRACT.md`.
- Document required generated artifact paths for v1.0 demo and per-ticker
  outputs.
- List required artifacts: fact report, analysis summary, DCF output, fair value
  per share output, model rating output, model confidence output, model signal
  output, and shared audit log.
- Document that generated artifacts belong under ignored `reports/` paths and
  must not be committed.
- Link the contract from `docs/GENERATED_OUTPUT_REVIEW_GUIDE.md` and README
  only if useful.
- Avoid runtime changes, path changes, schema changes, and new output fields.

Why this should be next:

- It builds directly on the v1.0 demo reports-directory smoke test.
- It gives reviewers a stable checklist for generated output paths before
  broader data-contract or adapter work.
- It is low risk and can be reviewed without touching financial calculations or
  model behavior.

## Proposed PR Sequence

1. **PR #75: Report Artifact Contract**
   Add docs-only artifact path and required-output contract for generated
   reports, summaries, model outputs, and audit logs.

2. **PR #76: Data Contract / Schema Hardening Assessment**
   Review current schema/reference docs against the report artifact contract and
   identify minimal validation gaps without changing runtime behavior unless a
   concrete missing guardrail is found.

3. **PR #77: Generated Output Review Hardening**
   Align generated-output review guidance with the artifact contract and add
   only narrow regression coverage if a specific user-facing artifact gap is
   identified.

4. **PR #78: Adapter RFC Preparation**
   Draft a future adapter RFC outline that depends on the artifact and data
   contracts. Keep adapter implementation out of scope.

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

These areas should remain in planning or RFC mode until data contracts,
artifact contracts, generated-output review expectations, and adapter decision
records are stable.
