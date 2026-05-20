# SQL migration validation flow

This describes the **local-first** harness implemented in `src/agentic_sql_converter/`.

## End-to-end path

1. **Input SQL** — A plaintext `.sql` file (synthetic fixtures only in this repo).
2. **AST parsing** — SQLGlot parses the text for a named read dialect
   (`agentic-sql-converter analyze … --dialect postgres`).
3. **CTE extraction** — CTE aliases and summarized bodies
   populate the `"ctes"` section of the JSON report.
4. **Dependency graph** — Directed edges relate CTEs to other CTEs and to outer
   referenced tables (see `"dependency_graph"`).
5. **Parse-readiness validation** — The report’s `"validation"` block records
   whether the text parsed cleanly statement-by-statement (no warehouse round-trip).
6. **Migration risk classification** — A merged `risk_level` (`low`, `medium`, `high`)
   combines structural graph/parse cues with **offline rule detectors** surfaced as
   `risk_categories` and `risk_findings` alongside the mirrored `summary.risk_level`
   bucket.
7. **Deterministic reports** — Stable JSON aggregates are printed by the CLI;
   demo fixtures also write canonical snapshots (`expected_analysis_report.json`,
   `expected_dependency_graph.json`) and Markdown under [`examples/migration_case/`](../examples/migration_case/).

See also: [`architecture.md`](./architecture.md) and the runnable demo
`examples/migration_case/run_demo.sh`.

## Deliberately out of scope (today)

- Target-dialect rewriting (PostgreSQL→Databricks SQL generation).
- MCP servers, embeddings, retrieval, or live model calls.
- JDBC/ODBC, secrets, catalogs, partitions, streaming runtimes
  (“validation” stays parse- and shape-oriented).
- SLA, cost estimation, lineage across jobs, automated regression policies.

These remain roadmap items—not hidden features of the current codebase.
