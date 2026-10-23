# Project instructions for Claude Code

## Purpose and layout

This is a local SAT-7 customer-insights demonstration. It uses generated synthetic data by default; do not use the original customer database or real customer records for development or tests.

- `src/customer_insights/` contains database access, cancellation analysis, optional risk analysis, report generation, and synthetic-data generation.
- `scripts/create_synthetic_db.py` creates the local SQLite database.
- `scripts/post_summary.py` simulates posting by appending to a local file; it does not send a Slack message.
- `templates/weekly_summary.md.j2` is the report template.
- `tests/` contains deterministic tests that use synthetic data and temporary files.
- `DATA_DICTIONARY.md` describes the database schema.

## Local workflow

From the project root, install the test dependencies, create synthetic data, generate the report, simulate the local post, and run tests with:

```bash
python -m pip install -e ".[risk,test]"
python scripts/create_synthetic_db.py
python -m customer_insights.report
python scripts/post_summary.py
python -m pytest -p no:cacheprovider
```

The generator refuses to overwrite an existing database. The report and simulated post create files under `outbox/`. Use only the synthetic database unless a human explicitly approves another data source.

## Data handling and approvals

- Never include secrets, customer contact details, database contents, generated report contents, or environment-variable values in responses, logs, test output, or commits.
- Do not read `.env` files, database files, `outbox/`, or model artifacts. Claude Code's project settings deny access through its file tools for these paths. If work genuinely requires sensitive data, stop; human approval alone does not override this deny rule, so a human must review and deliberately change the project settings before access. Never try to bypass the rule.
- Obtain human approval before network access, external posting, use of external services, destructive operations, changing permissions, installing dependencies, or accessing sensitive data. The settings prompt for WebFetch, WebSearch, and selected command patterns, but do not enforce a complete network boundary; treat this as an instruction, not a guarantee that all network access is blocked.
- Do not add MCP servers, plugins, telemetry, credentials, or external posting code without explicit review and approval.
- Review relevant source and documentation before editing. Make focused changes and run the appropriate local tests. Do not weaken or remove tests to get a passing result.

## Analysis limitations

Comment themes are keyword-based associations, not proven causes of cancellation. The bundled model at `models/cancellation_model.joblib` is loaded by default for risk estimates; set `MODEL_PATH` to use a different model. Predictions are skipped if the selected model file is unavailable. Review a model’s provenance and compatibility before using it, and do not describe predictions as verified without validation.
