"""Lightweight local SQL analysis report aggregation."""

from typing import Any, Dict, List, Optional

from agentic_sql_converter.graph.dependencies import build_dependency_graph
from agentic_sql_converter.parsing.ctes import extract_ctes
from agentic_sql_converter.parsing.parse import parse_sql
from agentic_sql_converter.rewrite.passes.formatting import NormalizeWhitespacePass
from agentic_sql_converter.rewrite.registry import RewritePassRegistry
from agentic_sql_converter.validate.parse_only import validate_parse_only
from agentic_sql_converter.validate.risk_classifier import (
    classify_migration_readiness_risks,
    merge_structural_and_finding_risk_levels,
)


def build_analysis_report(
    sql: str,
    dialect: Optional[str] = None,
    include_rewrites: bool = False,
) -> Dict[str, Any]:
    """Build a lightweight local SQL analysis report.

    Args:
        sql: SQL text to analyze.
        dialect: Optional SQLGlot source dialect name.
        include_rewrites: Whether to run registered local rewrite passes.

    Returns:
        A deterministic report combining parse, CTE, dependency graph,
        rewrite registry, validation, and summary sections.
    """
    parse = parse_sql(sql, dialect=dialect)
    ctes = extract_ctes(sql, dialect=dialect)
    dependency_graph = build_dependency_graph(sql, dialect=dialect)
    validation = validate_parse_only(sql, dialect=dialect)
    rewrite = _build_rewrite_summary(
        sql=sql,
        dialect=dialect,
        include_rewrites=include_rewrites,
    )
    summary = _build_summary(parse, ctes, dependency_graph, rewrite)
    migration_risk_signal = classify_migration_readiness_risks(
        sql,
        parse=parse,
        ctes=ctes,
        dependency_graph=dependency_graph,
    )
    merged_level = merge_structural_and_finding_risk_levels(
        summary["risk_level"],
        migration_risk_signal["finding_aggregate_level"],
    )
    summary["risk_level"] = merged_level

    return {
        "ctes": ctes,
        "dependency_graph": dependency_graph,
        "dialect": dialect,
        "parse": parse,
        "rewrite": rewrite,
        "risk_categories": migration_risk_signal["risk_categories"],
        "risk_findings": migration_risk_signal["risk_findings"],
        "risk_level": merged_level,
        "summary": summary,
        "validation": validation,
    }


def _build_rewrite_summary(
    sql: str,
    dialect: Optional[str],
    include_rewrites: bool,
) -> Dict[str, Any]:
    """Return rewrite registry metadata, optionally applying local passes."""
    registry = RewritePassRegistry()
    if include_rewrites:
        registry.register(NormalizeWhitespacePass())

    registered_passes = registry.list_passes()
    summary: Dict[str, Any] = {
        "registered_passes": registered_passes,
        "registered_rewrite_pass_count": len(registered_passes),
    }

    if not include_rewrites:
        return summary

    rewrite_result = registry.apply_all(sql, dialect=dialect)
    applied_passes = rewrite_result["applied_passes"]
    summary.update(
        {
            "applied_passes": applied_passes,
            "rewritten_sql": rewrite_result["output_sql"],
            "rewrite_changed": any(item["changed"] for item in applied_passes),
            "has_error": rewrite_result["has_error"],
            "error_message": rewrite_result["error_message"],
        }
    )
    return summary


def _build_summary(
    parse: Dict[str, Any],
    ctes: Dict[str, Any],
    dependency_graph: Dict[str, Any],
    rewrite: Dict[str, Any],
) -> Dict[str, Any]:
    """Build a compact deterministic summary for an analysis report."""
    is_parse_valid = not parse["has_parse_error"]
    cte_count = ctes["cte_count"]
    table_count = dependency_graph["table_count"]
    dependency_edge_count = len(dependency_graph["edges"])
    has_cycle = dependency_graph["has_cycle"]
    risk_level = _determine_risk_level(is_parse_valid, cte_count, has_cycle)
    notes = _build_notes(is_parse_valid, cte_count, has_cycle)

    return {
        "is_parse_valid": is_parse_valid,
        "statement_count": parse["statement_count"],
        "cte_count": cte_count,
        "table_count": table_count,
        "dependency_edge_count": dependency_edge_count,
        "registered_rewrite_pass_count": rewrite["registered_rewrite_pass_count"],
        "has_cycle": has_cycle,
        "risk_level": risk_level,
        "notes": notes,
    }


def _determine_risk_level(
    is_parse_valid: bool, cte_count: int, has_cycle: bool
) -> str:
    """Return a simple deterministic risk level."""
    if not is_parse_valid:
        return "high"
    if has_cycle or cte_count >= 5:
        return "medium"
    return "low"


def _build_notes(is_parse_valid: bool, cte_count: int, has_cycle: bool) -> List[str]:
    """Return deterministic notes explaining the summary."""
    notes: List[str] = []
    if not is_parse_valid:
        notes.append("SQL did not parse cleanly.")
    if has_cycle:
        notes.append("CTE dependency graph contains a cycle.")
    if cte_count >= 5:
        notes.append("Query contains five or more CTEs.")
    if not notes:
        notes.append("SQL parsed cleanly with low structural risk.")
    return notes
