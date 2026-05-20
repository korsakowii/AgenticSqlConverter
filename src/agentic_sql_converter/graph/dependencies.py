"""SQLGlot-backed dependency graph extraction."""

from typing import Any, Dict, List, Optional, Set, Tuple

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError


def build_dependency_graph(sql: str, dialect: Optional[str] = None) -> Dict[str, Any]:
    """Build a lightweight dependency graph from SQL using SQLGlot.

    Args:
        sql: SQL text to parse.
        dialect: Optional SQLGlot source dialect name.

    Returns:
        A dictionary containing CTE/table nodes, dependency edges, cycle
        information, and parse error details.
    """
    try:
        expressions = sqlglot.parse(sql, read=dialect)
    except ParseError as exc:
        return {
            "dialect": dialect,
            "nodes": [],
            "edges": [],
            "cte_count": 0,
            "table_count": 0,
            "has_cycle": False,
            "cycle_nodes": [],
            "has_parse_error": True,
            "error_message": str(exc),
        }

    ctes = _iter_ctes(expressions)
    cte_names = [cte.alias_or_name for cte in ctes if cte.alias_or_name]
    cte_name_set = set(cte_names)
    table_names = _extract_physical_table_names(expressions, cte_name_set)
    edges = _build_edges(ctes, cte_name_set)
    cycle_nodes = _find_cycle_nodes(edges)

    return {
        "dialect": dialect,
        "nodes": _build_nodes(cte_names, table_names),
        "edges": edges,
        "cte_count": len(cte_names),
        "table_count": len(table_names),
        "has_cycle": bool(cycle_nodes),
        "cycle_nodes": cycle_nodes,
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


def _build_nodes(cte_names: List[str], table_names: Set[str]) -> List[Dict[str, str]]:
    """Return CTE nodes followed by sorted physical table nodes."""
    nodes = [{"name": name, "node_type": "cte"} for name in cte_names]
    nodes.extend(
        {"name": name, "node_type": "table"} for name in sorted(table_names)
    )
    return nodes


def _extract_physical_table_names(
    expressions: List[exp.Expression], cte_names: Set[str]
) -> Set[str]:
    """Return all physical table names referenced by parsed expressions."""
    return {
        table.name
        for expression in expressions
        for table in expression.find_all(exp.Table)
        if table.name and table.name not in cte_names
    }


def _build_edges(ctes: List[exp.CTE], cte_names: Set[str]) -> List[Dict[str, str]]:
    """Return dependency edges from each CTE to referenced CTEs or tables."""
    edges: Set[Tuple[str, str, str]] = set()
    for cte in ctes:
        source_name = cte.alias_or_name
        if not source_name or cte.this is None:
            continue

        for table in cte.this.find_all(exp.Table):
            dependency_name = table.name
            if not dependency_name:
                continue
            dependency_type = (
                "cte_to_cte" if dependency_name in cte_names else "cte_to_table"
            )
            edges.add((source_name, dependency_name, dependency_type))

    return [
        {"from": source, "to": target, "dependency_type": dependency_type}
        for source, target, dependency_type in sorted(edges)
    ]


def _find_cycle_nodes(edges: List[Dict[str, str]]) -> List[str]:
    """Return nodes from the first detected CTE-to-CTE cycle."""
    graph: Dict[str, List[str]] = {}
    for edge in edges:
        if edge["dependency_type"] != "cte_to_cte":
            continue
        graph.setdefault(edge["from"], []).append(edge["to"])

    visiting: Set[str] = set()
    visited: Set[str] = set()
    path: List[str] = []

    def visit(node: str) -> List[str]:
        if node in visiting:
            return path[path.index(node) :]
        if node in visited:
            return []

        visiting.add(node)
        path.append(node)
        for dependency in graph.get(node, []):
            cycle = visit(dependency)
            if cycle:
                return cycle
        path.pop()
        visiting.remove(node)
        visited.add(node)
        return []

    for node in sorted(graph):
        cycle = visit(node)
        if cycle:
            return cycle

    return []
