# Contributing

Thanks for helping improve Aktienanalyse Agent. This project is a deterministic
stock analysis core, so contributions should be small, reviewable, and careful
about evidence, auditability, and output safety.

## Contribution Rules

Contributions must preserve:

- deterministic core behavior
- source traceability for every financial number
- auditability and reproducible run records
- fact, assumption, and calculated-output separation
- no price targets
- no buy/sell/hold recommendations
- no personal investment advice
- no live fetching unless future validated adapter work explicitly adds it
- no framework-specific business logic inside the deterministic core

Do not add runtime framework dependencies, adapter code, new companies, live data
fetching, trading logic, portfolio logic, or report wording that weakens the
guardrails unless the issue or PR explicitly scopes that work.

## Expected Workflow

1. Create a small branch and keep the PR narrowly scoped.
2. Make the smallest change that solves the issue.
3. Run:

```bash
python -m unittest discover -s tests
python scripts/run_v1_0_demo.py --reports-dir reports/tmp_contribution_demo
```

4. Do not commit generated reports, summaries, DCF outputs, audit logs, caches,
   or local environment files.
5. In the PR description, document:
   - changed files
   - tests run
   - generated artifacts checked, if any
   - guardrail impact
   - whether financial logic changed

## Documentation Changes

Docs-only changes should still preserve the architecture boundary:

- deterministic Python core stays framework-independent
- future MCP, A2A, or framework integrations belong in adapter layers
- source validation and audit logging remain mandatory
- generated outputs remain non-personalized analysis artifacts

## Generated Outputs

Generated reports and summaries must remain under `reports/`, which is ignored
by git. If a test needs generated files, use a temporary directory or an ignored
`reports/tmp_*` path.
