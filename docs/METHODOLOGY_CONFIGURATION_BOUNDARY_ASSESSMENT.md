# Methodology Configuration Boundary Assessment

This assessment documents the boundary for future methodology configuration
work. It is documentation only. It does not change runtime code, schemas, tests,
CLI behavior, dependencies, generated reports, release notes, tags, or GitHub
Releases.

## Executive Recommendation

Methodology configuration may exist later, but only as a narrow, validated
configuration surface around explicit inputs and deterministic rules.

Do not expand methodology configuration now. Future implementation should be
deferred until a concrete review need exists and a focused proposal defines the
allowed fields, validation behavior, affected outputs, guardrail tests, and
schema or contract impact.

The current `config/methodology_buffett_ai.json` remains an inert configuration
guardrail. `scripts/validate_methodology.py` validates its shape only; it does
not calculate DCF, fair value, intrinsic value, price targets, recommendations,
investment advice, or memo output.

## Current Methodology Boundary

The deterministic core currently separates:

- sourced facts in raw metric records and company contexts
- explicit DCF assumptions in `data/companies/<TICKER>/dcf_assumptions.json`
- deterministic calculations in scripts
- generated output contracts and expectations documents
- audit evidence and generated artifact paths

Methodology configuration is not a place to invent facts, assumptions, or
outputs. It should remain a versioned control surface that can describe allowed
methodology boundaries and validation rules, while core modules continue to
consume explicit inputs and validated artifacts.

## What Methodology Configuration May Control Later

A future methodology configuration may safely control narrow guardrail or
selection settings when each field is validated and tested:

- methodology version or profile identifier
- allowed methodology names or calculation families
- required input categories or ratio coverage checks
- allowed scenario names
- bounded assumption ranges, if the values are still supplied explicitly by
  assumption files or reviewed input records
- prohibited output lists
- manual-review requirements for assumptions
- references to existing schema or output-contract versions
- validation-only readiness gates

These controls should make behavior easier to review. They should not create
financial values on their own.

## What Methodology Configuration Must Not Control

Future methodology configuration must not:

- fetch or refresh live data
- create or infer financial facts
- invent DCF assumptions or forecast values
- silently change valuation formulas
- directly change model rating thresholds, model confidence scoring, or model
  signal labels without separate focused review
- alter report wording or disclaimers without generated-output review
- produce price targets
- produce buy/sell/hold recommendations
- produce personal investment advice
- add broker/order, trading, or portfolio behavior
- bypass source validation, assumption review, output contracts, or audit logs

If a proposed configuration field changes financial behavior, it should be
treated as a financial logic change, not as a harmless config edit.

## Interaction With The Deterministic Core

The deterministic core should continue to run from explicit files and validated
records. Methodology configuration may be read by readiness or validation stages,
but it should not replace:

- source validation
- company context validation
- DCF assumption validation
- DCF output contracts
- fair value per share output contracts
- model rating, confidence, or signal rule files
- report and summary guardrails
- audit logging

Future config changes should fail closed when required fields are missing,
invalid, unsupported, or inconsistent with existing contracts.

## Interaction With Explicit Inputs And Assumptions

Assumptions must remain explicit and reviewable. A methodology configuration may
define allowed bounds or required review status, but it should not generate or
select assumption values without a separate explicit input artifact.

Safe boundary:

- config says a discount rate must be within a documented range
- assumption file supplies the actual scenario discount rate
- validation rejects missing or out-of-range assumptions
- generated outputs show assumptions separately from facts

Unsafe boundary:

- config chooses a hidden default forecast
- config fills missing assumption values
- config treats assumptions as sourced facts
- config changes a manual-review assumption into a reviewed assumption

## Interaction With Model Rating, Confidence, And Signal

Model rating, model confidence, and model signal are guardrail-sensitive outputs.
Their current behavior is governed by separate rule files, contracts, tests, and
no-advice boundaries.

Future methodology configuration should not directly mutate:

- model rating enum values, labels, thresholds, or market-price handling
- model confidence grades, scoring deductions, assumption-quality rules, or
  warnings
- model signal enum values, blocking rules, reason text, or disclaimer wording

If a future methodology proposal needs to affect any of these outputs, it should
be split into a focused rule or output-contract assessment before
implementation.

## Interaction With Report Wording

Report wording is user-facing and guardrail-sensitive. Methodology configuration
should not drive report prose, recommendation-like language, price-target
framing, or disclaimer changes.

Future config-driven report changes would require generated-output review using
`docs/GENERATED_OUTPUT_REVIEW_GUIDE.md` and guardrail review using
`docs/GUARDRAIL_SECURITY_TEST_PLAN.md`.

## Interaction With Schemas, Contracts, And Tests

Any future methodology configuration implementation should identify whether it
requires:

- a schema or custom validation contract for the config file
- updates to `docs/SCHEMA_FIELD_REFERENCE.md`
- updates to generated-output contracts
- new validation tests for missing, invalid, unsupported, and out-of-range
  config values
- forbidden-output regression checks
- readiness-gate tests
- demo validation into ignored `reports/tmp_*` paths

Configuration changes should not be merged as documentation-only if they alter
runtime decisions, generated outputs, or validated artifact shapes.

## Future Implementation Prerequisites

Before any methodology configuration implementation PR, maintainers should
complete a focused proposal that defines:

1. the exact field or fields to add or change
2. whether the field is descriptive, validation-only, or behavior-changing
3. affected scripts, schemas, contracts, reports, summaries, and tests
4. how facts, assumptions, calculations, warnings, and unavailable states remain
   separated
5. how prohibited outputs remain blocked
6. how existing NVDA, AMD, and TSMC deterministic demo behavior is preserved or
   intentionally changed
7. whether a separate schema/data-contract proposal is required
8. why the change cannot stay as documentation or an explicit assumption file

If the answer involves new formulas, thresholds, model behavior, report wording,
or financial output semantics, split that work into its own RFC or assessment
before implementation.

## Benefits

A bounded methodology configuration surface could help maintainers:

- document methodology versions used in audit logs
- validate readiness prerequisites before calculations run
- keep allowed scenario names and required inputs explicit
- make prohibited outputs visible and testable
- review future methodology changes before they affect generated artifacts

## Risks

The main risks are overreach and ambiguity:

- config edits can look low-risk while changing financial behavior
- defaults can accidentally invent assumptions
- broad profiles can hide formula or threshold changes
- report wording can drift toward advice if generated from config labels
- schemas and tests can become stale if config fields are underspecified

These risks are why future implementation should start with a narrow proposal
and explicit tests, not a broad methodology configuration expansion.

## Classification

- Classification: Architecture governance / methodology boundary assessment
- Current status: current methodology config remains inert and validation-only
- Recommendation: implement later only if a concrete review need exists
- Smallest safe future step: open a focused methodology config proposal that
  classifies each proposed field as descriptive, validation-only, or
  behavior-changing before any runtime code or schema changes are made

## Explicitly Out Of Scope

This assessment does not add:

- runtime code
- tests
- schemas
- CLI behavior
- dependencies
- financial logic changes
- valuation formula changes
- model rating, model confidence, or model signal behavior changes
- report wording changes
- methodology config files
- generated reports
- live data
- adapters, MCP, A2A, or web UI
- release notes, tags, or GitHub Releases
- buy/sell/hold advice
- price targets
- trading logic
- personal investment advice
