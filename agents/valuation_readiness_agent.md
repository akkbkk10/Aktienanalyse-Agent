# Valuation Readiness Agent

The valuation readiness agent is a deterministic gatekeeper for the controlled
valuation-stage workers in the v1.0.0 workflow. It checks whether the evidence
stack is complete enough for DCF to run.

## Scope

- Validate source data.
- Confirm there are no high-priority research gaps.
- Confirm required ratio outputs exist.
- Validate the methodology configuration.
- Confirm an audit log record can be written.
- Confirm prohibited valuation-stage outputs are absent.

## Required Output

The agent must return structured JSON with:

- `ticker`
- `ready_for_valuation`
- `blocking_reasons`
- `warnings`
- `required_next_actions`

## Strict Boundaries

- Do not calculate DCF.
- Do not calculate fair value.
- Do not calculate intrinsic value.
- Do not calculate model rating, model confidence, or model signal.
- Do not create price targets.
- Do not make recommendations.
- Do not use buy, sell, or hold language.
- Do not provide investment advice.

This agent only determines readiness. A `ready_for_valuation` result is not a valuation
and must not be treated as a recommendation.
