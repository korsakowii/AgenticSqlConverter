"""Tests for parse-only SQL validation."""

import sys
from pathlib import Path


SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_ROOT))

from agentic_sql_converter.validate.parse_only import validate_parse_only  # noqa: E402


def test_validate_parse_only_accepts_simple_select() -> None:
    result = validate_parse_only("SELECT user_id FROM users")

    assert result == {
        "dialect": None,
        "is_valid": True,
        "statement_count": 1,
        "expression_types": ["Select"],
        "error_count": 0,
        "errors": [],
    }


def test_validate_parse_only_accepts_query_with_cte() -> None:
    result = validate_parse_only(
        """
        WITH active_users AS (
            SELECT user_id
            FROM users
        )
        SELECT user_id
        FROM active_users
        """
    )

    assert result["is_valid"] is True
    assert result["statement_count"] == 1
    assert result["expression_types"] == ["Select"]
    assert result["errors"] == []


def test_validate_parse_only_handles_invalid_sql_without_raising() -> None:
    result = validate_parse_only("SELECT * FROM (")

    assert result["is_valid"] is False
    assert result["statement_count"] == 0
    assert result["expression_types"] == []
    assert result["error_count"] == 1
    assert result["errors"][0]["error_type"] == "ParseError"
    assert result["errors"][0]["message"]


def test_validate_parse_only_supports_explicit_postgres_dialect() -> None:
    result = validate_parse_only("SELECT NOW()::DATE FROM users", dialect="postgres")

    assert result["dialect"] == "postgres"
    assert result["is_valid"] is True
    assert result["statement_count"] == 1


def test_validate_parse_only_treats_empty_sql_as_invalid() -> None:
    result = validate_parse_only("   ")

    assert result == {
        "dialect": None,
        "is_valid": False,
        "statement_count": 0,
        "expression_types": [],
        "error_count": 1,
        "errors": [
            {
                "message": "SQL text is empty.",
                "error_type": "EmptySqlError",
            }
        ],
    }


def test_validate_parse_only_counts_multiple_statements() -> None:
    result = validate_parse_only(
        "SELECT customer_id FROM customers; SELECT order_id FROM orders;"
    )

    assert result["is_valid"] is True
    assert result["statement_count"] == 2
    assert result["expression_types"] == ["Select", "Select"]
