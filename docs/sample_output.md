# Sample analysis output (synthetic fixture)

This excerpt is trimmed from **`examples/migration_case/expected_analysis_report.json`**, produced by running the CLI offline against `examples/migration_case/legacy_postgres_query.sql`.

It illustrates the deterministic JSON shape reviewers get from the **local-first validation harness**: parse/readiness gates, structural CTE metadata, dependency edges, merged migration-readiness cues, and a parse-only validation block.

**Not covered here:** translating to another dialect, warehouse catalog validation, or any network calls.

---

## Representative fields

### Parse readiness & validation (`validation`)

```json
{
  "is_valid": true,
  "statement_count": 1,
  "error_count": 0
}
```

### CTE footprint (`ctes` — summary-level)

From the fixture: **`cte_count`: 6** (full `ctes` array is omitted here).

### Dependency graph (edge sample)

Seven directed edges summarize how CTEs reference each other versus outer tables—for example:

```json
[
  {"from": "base_events", "to": "metric_fact_sample", "dependency_type": "cte_to_table"},
  {"from": "geo_enriched", "to": "base_events", "dependency_type": "cte_to_cte"},
  {"from": "product_enriched", "to": "geo_enriched", "dependency_type": "cte_to_cte"}
]
```

### Migration-readiness signals

```json
{
  "risk_level": "medium",
  "risk_categories": ["deep_cte_chain", "postgres_cast_syntax"],
  "risk_findings": [
    {
      "category": "deep_cte_chain",
      "message": "Query declares five or more CTE definitions.",
      "severity": "medium"
    },
    {
      "category": "postgres_cast_syntax",
      "message": "PostgreSQL :: cast syntax may need dialect-specific review.",
      "severity": "medium"
    }
  ]
}
```

### Summary mirror

The CLI also mirrors the merged level under `summary.risk_level` for compatibility with earlier consumers.

---

## Regenerate locally

```bash
bash examples/migration_case/run_demo.sh
```

See also [`docs/validation_flow.md`](validation_flow.md) for how these blocks fit the end-to-end validation flow.
