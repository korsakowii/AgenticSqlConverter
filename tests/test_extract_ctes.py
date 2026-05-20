"""Tests for SQLGlot-backed CTE extraction."""

import sys
from pathlib import Path


SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_ROOT))

from agentic_sql_converter.parsing.ctes import extract_ctes  # noqa: E402


def test_extract_ctes_extracts_one_cte() -> None:
    result = extract_ctes(
        """
        WITH active_users AS (
            SELECT user_id
            FROM users
        )
        SELECT user_id
        FROM active_users
        """
    )

    assert result["has_parse_error"] is False
    assert result["cte_count"] == 1
    assert result["ctes"][0]["name"] == "active_users"
    assert result["ctes"][0]["expression_type"] == "Select"
    assert "FROM users" in result["ctes"][0]["source_sql"]


def test_extract_ctes_extracts_multiple_ctes() -> None:
    result = extract_ctes(
        """
        WITH active_users AS (
            SELECT user_id
            FROM users
        ),
        recent_orders AS (
            SELECT order_id, user_id
            FROM orders
        )
        SELECT active_users.user_id
        FROM active_users
        JOIN recent_orders USING (user_id)
        """
    )

    assert result["cte_count"] == 2
    assert [cte["name"] for cte in result["ctes"]] == [
        "active_users",
        "recent_orders",
    ]


def test_extract_ctes_extracts_table_names_inside_each_cte() -> None:
    result = extract_ctes(
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

    assert result["ctes"][0]["table_names"] == ["users"]
    assert result["ctes"][1]["table_names"] == ["orders"]


def test_extract_ctes_handles_query_with_no_cte() -> None:
    result = extract_ctes("SELECT product_id FROM products")

    assert result["has_parse_error"] is False
    assert result["cte_count"] == 0
    assert result["ctes"] == []


def test_extract_ctes_handles_invalid_sql_without_raising() -> None:
    result = extract_ctes("WITH broken AS (SELECT * FROM")

    assert result["has_parse_error"] is True
    assert result["cte_count"] == 0
    assert result["ctes"] == []
    assert result["error_message"]


def test_extract_ctes_supports_explicit_postgres_dialect() -> None:
    result = extract_ctes(
        """
        WITH current_users AS (
            SELECT user_id, NOW()::DATE AS current_date
            FROM users
        )
        SELECT user_id
        FROM current_users
        """,
        dialect="postgres",
    )

    assert result["dialect"] == "postgres"
    assert result["has_parse_error"] is False
    assert result["ctes"][0]["name"] == "current_users"
    assert result["ctes"][0]["table_names"] == ["users"]
