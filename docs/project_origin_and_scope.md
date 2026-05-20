# Project Origin and Scope

## What This Project Is

**AgenticSqlConverter** is an independent personal/open-source project
for local-first, AST-first SQL analysis and migration tooling.

**This MVP focuses on deterministic SQL structure analysis before rewrite
automation:** parse summaries, CTE extraction, dependency graphs,
parse-readiness validation, and reviewable migration-risk signals delivered
as JSON (and optional human-readable demo reports).

The long-term direction is a generic SQL dialect migration toolkit:
parse SQL into an AST, decompose large queries, apply deterministic
rewrite passes, validate outputs locally where possible, and optionally
expose local tools through editor or agent integrations. **Rewrite
automation, live warehouse validation, and agent integrations are roadmap
layers beyond the current MVP**—they are not part of the implemented release
described in [Current Implemented MVP](#current-implemented-mvp).

## Origin

The project is an independent effort. It was created to explore how far
AST-driven, rule-first SQL migration tooling can go before optional assisted
review becomes useful, and to learn how a small local pipeline can
be structured around that core.

Design decisions, module layout, documentation, and examples are
authored from scratch against public references such as SQLGlot
documentation, SQL standard references, dialect manuals, and public or
synthetic SQL examples.

The repository's git history is the canonical record of when each
component was authored. No proprietary code, schema, prompt, or workflow
is part of this project.

## Long-Term Project Scope

AgenticSqlConverter is intended to become a generic, local-first,
AST-first SQL dialect migration toolkit. The long-term scope includes:

- Parsing SQL with SQLGlot into a typed AST.
- Extracting CTEs and structural query metadata.
- Building CTE/table dependency graphs.
- Providing a deterministic rewrite pass framework.
- Adding public-doc-based dialect-aware rewrite routes.
- Supporting large SQL analysis and chunking.
- Running parse-only validation locally by default.
- Producing reviewable migration and analysis reports.
- Optionally exposing local tools through editor integrations after the CLI
  and library APIs are stable.

Long-term items are roadmap intent unless listed in [Current Implemented
MVP](#current-implemented-mvp).

## Current Implemented MVP

Currently implemented:

- **SQLGlot parser wrapper.** `parse_sql()` returns statement counts,
  expression types, table names, CTE names, and parse-error details.
- **CTE extraction.** `extract_ctes()` returns CTE names, source SQL,
  expression types, and referenced physical tables.
- **CTE/table dependency graph.** `build_dependency_graph()` returns CTE
  and table nodes, dependency edges, and simple cycle detection.
- **Rewrite pass registry framework only.** `RewritePassRegistry`
  registers deterministic passes and applies them in order; no production
  rewrite pass ships in this release yet.
- **Parse-only validation.** `validate_parse_only()` reports whether SQL
  parses cleanly for an optional SQLGlot dialect.
- **JSON analysis report.** `build_analysis_report()` combines parse,
  CTE, graph, validation, and rewrite-registry metadata into a
  deterministic JSON-ready dictionary.
- **Local CLI analyze command.** `agentic-sql-converter analyze` reads a
  local SQL file and prints the JSON analysis report.
- **Synthetic example SQL.** `examples/simple_orders.sql` and
  `examples/migration_case/` demonstrate the local analysis flow.

PostgreSQL→Databricks SQL is one motivating migration scenario; the
**current layer** focuses on parseability, CTE structure, dependency
graphs, and reviewable migration-risk signals—not cross-dialect rewrite
automation.

## Roadmap Layers Beyond the Current MVP

Planned layers that build on the current harness (not shipped in this MVP):

- Deterministic SQL rewrite passes beyond the registry scaffold.
- Cross-dialect rewrite automation (including Postgres-shaped source toward
  other dialects).
- Deeper validation tied to target dialect semantics where feasible locally.
- Large SQL chunking for very large inputs.
- File-writing migration report workflows beyond the current CLI JSON path.
- Optional assisted review or repair loops layered on deterministic output.

These items are **future scope**. The README and CLI describe **implemented**
behavior only; reports distinguish registry metadata from applied rewrites.

## Non-Goals

To keep the scope honest, the project explicitly does **not** aim to
become any of the following:

- **Not a data assistant.** It does not answer business questions,
  summarize data, or interpret query results.
- **Not a business-view assistant.** It does not depend on semantic
  layers, metric catalogs, dashboards, or BI tooling.
- **Not an organization-specific automation tool.** It does not
  orchestrate approvals, ticketing, deployments, or review processes.
- **Not tied to private data models.** It treats table and column
  identifiers as opaque SQL names and does not encode private naming
  conventions or data taxonomies.
- **Not dependent on private infrastructure.** The default runtime is
  `pip install` on a local machine, and the current MVP requires no
  network service.

If a feature request would cross one of these lines, it belongs in a
separate downstream project that depends on this one, not in this
repository.

## Technical Commitments

The project identity is defined by these technical commitments:

1. **SQLGlot AST parsing.** The first step for supported analysis and
   future rewrite work is parsing through SQLGlot.
2. **Local-first defaults.** The current MVP runs on local files and
   does not require credentials or hosted services.
3. **Deterministic structure first.** Parse summaries, CTE extraction,
   dependency graph extraction, validation, and reporting are
   deterministic.
4. **Named rewrite passes.** Future transformations should be expressed
   as named passes with clear input/output contracts.
5. **Public or synthetic examples.** Tests and docs use generic SQL
   examples such as `users`, `orders`, `products`, and `payments`.
6. **Honest reporting.** Reports distinguish implemented behavior from
   planned behavior and describe conversion only when conversion ships.

## Public / Synthetic Examples

All examples in this repository, in tests, and in documentation use
either public SQL references or synthetic fixtures. A representative
fixture looks like this:

```sql
-- synthetic: orders rollup
WITH active_users AS (
    SELECT user_id, signup_ts
    FROM users
    WHERE status = 'active'
),
recent_orders AS (
    SELECT o.user_id, o.order_id, o.total_amount
    FROM orders o
    JOIN active_users u USING (user_id)
    WHERE o.order_ts >= NOW() - INTERVAL '30 days'
)
SELECT user_id, COUNT(*) AS order_count, SUM(total_amount) AS revenue
FROM recent_orders
GROUP BY user_id;
```

No example in this project is drawn from any private codebase, private
schema, or private query log.

## Where This Document Lives

This file is the source of truth for the distinction between long-term
project scope and current implementation status. Companion documents:

- [`docs/open_source_boundary.md`](./open_source_boundary.md) — what
  may and may not enter this repository
- [`docs/technical_roadmap_v0.md`](./technical_roadmap_v0.md) — the v0
  roadmap
