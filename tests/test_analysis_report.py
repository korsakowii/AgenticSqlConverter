"""Tests for local SQL analysis report aggregation."""

import sys
from pathlib import Path


SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_ROOT))

from agentic_sql_converter.report.analysis import (  # noqa: E402
    _build_summary,
    build_analysis_report,
)


def test_analysis_report_for_simple_select_is_valid_low_risk() -> None:
    result = build_analysis_report("SELECT user_id FROM users")

    assert result["dialect"] is None
    assert result["summary"] == {
        "is_parse_valid": True,
        "statement_count": 1,
        "cte_count": 0,
        "table_count": 1,
        "dependency_edge_count": 0,
        "registered_rewrite_pass_count": 0,
        "has_cycle": False,
        "risk_level": "low",
        "notes": ["SQL parsed cleanly with low structural risk."],
    }
    assert result["risk_level"] == "low"
    assert result["risk_categories"] == []
    assert result["risk_findings"] == []
    assert result["rewrite"] == {
        "registered_passes": [],
        "registered_rewrite_pass_count": 0,
    }


def test_analysis_report_for_cte_query_includes_counts_and_edges() -> None:
    result = build_analysis_report(
        """
        WITH active_users AS (
            SELECT user_id
            FROM users
        ),
        user_orders AS (
            SELECT orders.order_id, active_users.user_id
            FROM orders
            JOIN active_users ON active_users.user_id = orders.user_id
        )
        SELECT user_id
        FROM user_orders
        """
    )

    assert result["summary"]["cte_count"] == 2
    assert result["summary"]["table_count"] == 2
    assert result["summary"]["dependency_edge_count"] == 3
    assert {
        "from": "user_orders",
        "to": "active_users",
        "dependency_type": "cte_to_cte",
    } in result["dependency_graph"]["edges"]


def test_analysis_report_for_invalid_sql_is_high_risk() -> None:
    result = build_analysis_report("SELECT * FROM (")

    assert result["summary"]["is_parse_valid"] is False
    assert result["summary"]["risk_level"] == "high"
    assert result["summary"]["notes"] == ["SQL did not parse cleanly."]
    assert result["validation"]["is_valid"] is False
    assert result["risk_level"] == "high"
    assert result["risk_categories"] == []
    assert result["risk_findings"] == []


def test_analysis_report_for_five_ctes_is_medium_risk() -> None:
    result = build_analysis_report(
        """
        WITH first_cte AS (
            SELECT user_id FROM users
        ),
        second_cte AS (
            SELECT user_id FROM first_cte
        ),
        third_cte AS (
            SELECT user_id FROM second_cte
        ),
        fourth_cte AS (
            SELECT user_id FROM third_cte
        ),
        fifth_cte AS (
            SELECT user_id FROM fourth_cte
        )
        SELECT user_id
        FROM fifth_cte
        """
    )

    assert result["summary"]["cte_count"] == 5
    assert result["summary"]["risk_level"] == "medium"
    assert result["summary"]["notes"] == ["Query contains five or more CTEs."]
    assert result["risk_level"] == "medium"
    assert "deep_cte_chain" in result["risk_categories"]


def test_analysis_summary_marks_cycles_medium_risk() -> None:
    summary = _build_summary(
        parse={"has_parse_error": False, "statement_count": 1},
        ctes={"cte_count": 2},
        dependency_graph={"table_count": 0, "edges": [], "has_cycle": True},
        rewrite={"registered_rewrite_pass_count": 0},
    )

    assert summary["risk_level"] == "medium"
    assert summary["has_cycle"] is True
    assert summary["notes"] == ["CTE dependency graph contains a cycle."]


def test_analysis_report_contains_expected_sections() -> None:
    result = build_analysis_report("SELECT product_id FROM products")

    assert set(result) == {
        "risk_categories",
        "risk_findings",
        "risk_level",
        "ctes",
        "dependency_graph",
        "dialect",
        "parse",
        "rewrite",
        "summary",
        "validation",
    }


def test_analysis_report_with_rewrites_includes_normalized_sql() -> None:
    result = build_analysis_report(
        "SELECT   product_id\nFROM\tproducts",
        include_rewrites=True,
    )

    assert result["rewrite"]["rewritten_sql"] == "SELECT product_id FROM products"
    assert result["rewrite"]["rewrite_changed"] is True
    assert result["summary"]["registered_rewrite_pass_count"] == 1


def test_analysis_report_with_rewrites_records_applied_pass_metadata() -> None:
    result = build_analysis_report(
        "SELECT user_id FROM users",
        dialect="postgres",
        include_rewrites=True,
    )

    assert result["rewrite"]["registered_rewrite_pass_count"] == 1
    assert result["rewrite"]["registered_passes"] == [
        {
            "name": "normalize_whitespace",
            "description": "Normalize SQL whitespace without changing SQL semantics.",
        }
    ]
    assert result["rewrite"]["applied_passes"] == [
        {
            "name": "normalize_whitespace",
            "changed": False,
            "message": "normalized whitespace",
        }
    ]
    assert result["rewrite"]["has_error"] is False
    assert result["rewrite"]["error_message"] is None


def test_analysis_report_with_rewrites_handles_invalid_sql_without_crashing() -> None:
    result = build_analysis_report("SELECT   FROM   WHERE", include_rewrites=True)

    assert result["summary"]["risk_level"] == "high"
    assert result["validation"]["is_valid"] is False
    assert result["rewrite"]["rewritten_sql"] == "SELECT FROM WHERE"
    assert result["rewrite"]["has_error"] is False
