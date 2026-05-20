"""Tests for the SQLGlot parser wrapper."""

import sys
from pathlib import Path


SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_ROOT))

from agentic_sql_converter.parsing.parse import parse_sql  # noqa: E402


def test_parse_sql_parses_simple_select() -> None:
    result = parse_sql("SELECT customer_id FROM customers")

    assert result["has_parse_error"] is False
    assert result["statement_count"] == 1
    assert result["expression_types"] == ["Select"]


def test_parse_sql_extracts_table_name() -> None:
    result = parse_sql("SELECT order_id FROM orders")

    assert result["table_names"] == ["orders"]


def test_parse_sql_extracts_cte_name() -> None:
    result = parse_sql(
        """
        WITH active_users AS (
            SELECT user_id
            FROM users
            WHERE status = 'active'
        )
        SELECT user_id
        FROM active_users
        """
    )

    assert result["cte_names"] == ["active_users"]
    assert result["table_names"] == ["users"]


def test_parse_sql_handles_invalid_sql_without_raising() -> None:
    result = parse_sql("SELECT * FROM (")

    assert result["has_parse_error"] is True
    assert result["statement_count"] == 0
    assert result["error_message"]


def test_parse_sql_supports_explicit_dialect() -> None:
    result = parse_sql("SELECT NOW()::DATE FROM users", dialect="postgres")

    assert result["dialect"] == "postgres"
    assert result["has_parse_error"] is False
    assert result["table_names"] == ["users"]
