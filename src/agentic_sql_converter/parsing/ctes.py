"""SQLGlot-backed CTE extraction helpers."""

from typing import Any, Dict, List, Optional, Set

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError


def extract_ctes(sql: str, dialect: Optional[str] = None) -> Dict[str, Any]:
    """Extract CTE definitions from SQL using SQLGlot.

    Args:
        sql: SQL text to parse.
        dialect: Optional SQLGlot source dialect name.

    Returns:
        A dictionary containing CTE summaries and parse error details.
    """
    try:
        expressions = sqlglot.parse(sql, read=dialect)
    except ParseError as exc:
        return {
            "dialect": dialect,
            "cte_count": 0,
            "ctes": [],
            "has_parse_error": True,
            "error_message": str(exc),
        }

    cte_names = _extract_cte_names(expressions)
    ctes = [_summarize_cte(cte, cte_names, dialect) for cte in _iter_ctes(expressions)]

    return {
        "dialect": dialect,
        "cte_count": len(ctes),
        "ctes": ctes,
        "has_parse_error": False,
        "error_message": None,
    }


def _iter_ctes(expressions: List[exp.Expression]) -> List[exp.CTE]:
    """Return CTE nodes in parse order."""
    return [
        cte
        for expression in expressions
        for cte in expression.find_all(exp.CTE, bfs=False)
    ]


def _extract_cte_names(expressions: List[exp.Expression]) -> Set[str]:
    """Return CTE aliases declared in parsed expressions."""
    return {cte.alias_or_name for cte in _iter_ctes(expressions) if cte.alias_or_name}


def _summarize_cte(
    cte: exp.CTE, cte_names: Set[str], dialect: Optional[str]
) -> Dict[str, Any]:
    """Return a lightweight summary for one CTE."""
    body = cte.this
    return {
        "name": cte.alias_or_name,
        "expression_type": body.__class__.__name__,
        "source_sql": body.sql(dialect=dialect) if body is not None else "",
        "table_names": sorted(_extract_table_names(body, cte_names)),
    }


def _extract_table_names(
    expression: Optional[exp.Expression], cte_names: Set[str]
) -> Set[str]:
    """Return table names referenced inside a CTE body."""
    if expression is None:
        return set()

    return {
        table.name
        for table in expression.find_all(exp.Table)
        if table.name and table.name not in cte_names
    }
