# Valuation Readiness Agent

The valuation readiness agent is a deterministic gatekeeper for future valuation work.
It checks whether the pre-valuation evidence stack is complete enough to proceed later.

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
- Do not create price targets.
- Do not make recommendations.
- Do not use buy, sell, or hold language.
- Do not provide investment advice.

This agent only determines readiness. A `ready_for_valuation` result is not a valuation
and must not be treated as a recommendation.
