# AgenticSqlConverter

## What this MVP demonstrates

This repository is a **local-first validation harness** for **offline, AST-first, deterministic** SQL structure analysis before rewrite automation:

- **SQLGlot-backed parseability** and read-dialect labels for Postgres-shaped input
- **CTE extraction** with compact metadata (names, bodies, referenced tables)
- **Lightweight dependency graph** edges between CTEs and outer tables
- **Deterministic migration-readiness signals** (`risk_categories`, `risk_findings`, merged `risk_level`)
- **CLI-generated JSON reports** suitable for diffing, review, and CI gates
- **CI-tested** smoke coverage of the harness surface (see [`.github/workflows/ci.yml`](.github/workflows/ci.yml))

This MVP focuses on **deterministic SQL structure analysis** before rewrite automation. Rewrite automation, live warehouse validation, and agent-style integrations are **roadmap layers** beyond the current release—see [`docs/project_origin_and_scope.md`](docs/project_origin_and_scope.md) for the full boundary.

Synthetic fixtures live under [`examples/migration_case/`](examples/migration_case/). Representative JSON fields are in [`docs/sample_output.md`](docs/sample_output.md). The staged analysis flow is in [`docs/validation_flow.md`](docs/validation_flow.md).

## Why this matters

Large SQL migration efforts are difficult to validate when parsing, dependency extraction, rewrite boundaries, and migration risks sit inside opaque workflows. AgenticSqlConverter isolates those concerns into **deterministic, inspectable artifacts** so migration work can be reviewed, reproduced, and improved with **inspectability before rewrite automation**.

## Minimal E2E demo (`examples/migration_case/`)

Synthetics-only workflow illustrating the harness end-to-end:

PostgreSQL→Databricks SQL is one **motivating migration scenario**; the **current layer** focuses on parseability, CTE structure, dependency graphs, and reviewable migration-risk signals—not vendor-specific rewrite automation.

1. Inspect `examples/migration_case/legacy_postgres_query.sql`.
2. Run `bash examples/migration_case/run_demo.sh`.
3. Review regenerated **deterministic artifacts** beside the fixture:
   - `expected_analysis_report.json` — sorted snapshot of what the CLI printed.
   - `expected_dependency_graph.json` — `dependency_graph` fragment for readers.
   - `validation_report.md` — **human-readable** summary of signals (parse, graph, deterministic risks).

Manual one-liner (equivalent ingest path):

```bash
PYTHONPATH=src python3 -m agentic_sql_converter.cli.main \
  analyze examples/migration_case/legacy_postgres_query.sql \
  --dialect postgres > /tmp/analysis.json
```

## Documentation & CI

| Resource | Purpose |
|----------|---------|
| [`examples/migration_case/`](examples/migration_case/) | End-to-end synthetic demo + regenerated JSON/Markdown |
| [`docs/sample_output.md`](docs/sample_output.md) | Short excerpt of CLI JSON fields from the fixture |
| [`docs/validation_flow.md`](docs/validation_flow.md) | **Validation flow** and design rationale pointers |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | **`pytest`** + **`ruff check`** for the MVP package surface |

Recommended local smoke (**same pytest list as CI**):

```bash
python3 -m pytest tests/test_cli.py \
  tests/test_analysis_report.py \
  tests/test_formatting_pass.py \
  tests/test_parse_only_validation.py \
  tests/test_rewrite_registry.py \
  tests/test_dependency_graph.py \
  tests/test_extract_ctes.py \
  tests/test_parse_sql.py \
  tests/test_risk_classifier.py \
  -q -o addopts='' \
  -p no:asyncio

ruff check src/agentic_sql_converter
```

## Architecture

High-level routing is documented under [`docs/architecture.md`](docs/architecture.md)
(Mermaid overview + folder map).

## Ships today and roadmap

| Layer | Capability |
|-------|------------|
| **Ships today** | Local structural parse, CTE extraction, dependency graph JSON |
| **Ships today** | Parse-only validation gates and deterministic migration-risk tagging |
| **Ships today** | CLI `analyze` → sorted JSON report; synthetic demo fixtures |
| **Roadmap** | Named deterministic rewrite passes (registry scaffold only today) |
| **Roadmap** | Cross-dialect rewrite automation and deeper validation layers |

For non-goals, long-term intent, and what is explicitly outside this repository, see [`docs/project_origin_and_scope.md`](docs/project_origin_and_scope.md) and [`docs/open_source_boundary.md`](docs/open_source_boundary.md).

## Open-source boundary

- Examples must remain **public or synthetic** (`examples/simple_orders.sql`,
  `examples/migration_case/`).
- No proprietary schemas, ticketing metadata, identifiers, buckets, connectors, passwords,
  or undocumented endpoints embedded in curated fixtures.

## Quick Start

Install in editable mode (Python 3.9+):

```bash
python3 -m pip install -e .
```

Run the deterministic demo regenerate script:

```bash
bash examples/migration_case/run_demo.sh
```

## Development

For the **`pytest`** list and **`ruff`** invocation, see **Documentation & CI** above.

## License

This project is licensed under the `LICENSE` file in this repository.
