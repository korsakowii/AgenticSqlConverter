"""Small SQLGlot-backed parsing wrapper."""

from typing import Any, Dict, List, Optional, Set

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError


def parse_sql(sql: str, dialect: Optional[str] = None) -> Dict[str, Any]:
    """Parse SQL using SQLGlot and return a lightweight structural summary.

    Args:
        sql: SQL text to parse.
        dialect: Optional SQLGlot source dialect name.

    Returns:
        A dictionary containing statement counts, expression types, table
        names, CTE names, and parse error details.
    """
    try:
        expressions = sqlglot.parse(sql, read=dialect)
    except ParseError as exc:
        return {
            "dialect": dialect,
            "statement_count": 0,
            "expression_types": [],
            "table_names": [],
            "cte_names": [],
            "has_parse_error": True,
            "error_message": str(exc),
        }

    cte_names = _extract_cte_names(expressions)
    table_names = _extract_table_names(expressions, cte_names)

    return {
        "dialect": dialect,
        "statement_count": len(expressions),
        "expression_types": [expression.__class__.__name__ for expression in expressions],
        "table_names": sorted(table_names),
        "cte_names": sorted(cte_names),
        "has_parse_error": False,
        "error_message": None,
    }


def _extract_cte_names(expressions: List[exp.Expression]) -> Set[str]:
    """Return CTE aliases declared in parsed expressions."""
    return {
        cte.alias_or_name
        for expression in expressions
        for cte in expression.find_all(exp.CTE)
        if cte.alias_or_name
    }


def _extract_table_names(
    expressions: List[exp.Expression], cte_names: Set[str]
) -> Set[str]:
    """Return referenced table names, excluding CTE aliases."""
    return {
        table.name
        for expression in expressions
        for table in expression.find_all(exp.Table)
        if table.name and table.name not in cte_names
    }
