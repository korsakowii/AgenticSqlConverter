"""Parse-only SQL validation using SQLGlot."""

from typing import Any, Dict, Optional

from agentic_sql_converter.parsing.parse import parse_sql


def validate_parse_only(sql: str, dialect: Optional[str] = None) -> Dict[str, Any]:
    """Validate whether SQL parses cleanly using SQLGlot.

    Args:
        sql: SQL text to validate.
        dialect: Optional SQLGlot source dialect name.

    Returns:
        A dictionary containing parse validity, statement summary, and
        parse error details.
    """
    if not sql.strip():
        return {
            "dialect": dialect,
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

    parsed = parse_sql(sql, dialect=dialect)
    if parsed["has_parse_error"]:
        return {
            "dialect": dialect,
            "is_valid": False,
            "statement_count": 0,
            "expression_types": [],
            "error_count": 1,
            "errors": [
                {
                    "message": parsed["error_message"],
                    "error_type": "ParseError",
                }
            ],
        }

    return {
        "dialect": dialect,
        "is_valid": True,
        "statement_count": parsed["statement_count"],
        "expression_types": parsed["expression_types"],
        "error_count": 0,
        "errors": [],
    }
