"""Deterministic, local-only migration readiness risk classifier.

Rules operate on plaintext SQL plus parse/CTE/dependency metadata produced
elsewhere in the harness. No network or LLM usage.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Literal, Mapping, MutableMapping, Sequence, Tuple

_SeverityName = Literal["low", "medium", "high"]

_SEVERITY_ORDER: Mapping[str, int] = {"low": 0, "medium": 1, "high": 2}

_CATEGORY_MESSAGE_SEVERITY: Dict[str, Tuple[str, str]] = {
    "postgres_cast_syntax": (
        "medium",
        "PostgreSQL :: cast syntax may need dialect-specific review.",
    ),
    "deep_cte_chain": ("medium", "Query declares five or more CTE definitions."),
    "wildcard_select": (
        "medium",
        "Wildcard SELECT projection may obscure columns during migrations.",
    ),
    "vendor_specific_function": (
        "medium",
        "PostgreSQL-centric functions detected that often need dialect rewiring.",
    ),
    "recursive_cte": (
        "high",
        "WITH RECURSIVE is supported differently across warehouses; review recursion.",
    ),
}

# Two lightweight heuristics: identifier::typename and ())::typename forms.
_PG_CAST_IDENTIFIER_TYPENAME = re.compile(r"\w+::\w+", re.IGNORECASE)
_PG_CAST_PAREN_SUFFIX = re.compile(r"\)\s*::\s*\w+", re.IGNORECASE)

_WILDCARD_SELECT_PATTERN = re.compile(r"\bSELECT\s+\*", re.IGNORECASE | re.DOTALL)

_RECURSIVE_CTE_PATTERN = re.compile(r"\bWITH\s+RECURSIVE\b", re.IGNORECASE)

_VENDOR_FUNC_PATTERN = re.compile(
    r"\b(?:date_trunc|string_agg|array_agg|regexp_replace)\s*\(",
    re.IGNORECASE,
)

_JSONB_FUNC_PATTERN = re.compile(r"\bjsonb_[A-Za-z0-9_]+\s*\(", re.IGNORECASE)


def classify_migration_readiness_risks(
    sql: str,
    *,
    parse: Mapping[str, Any],
    ctes: Mapping[str, Any],
    dependency_graph: Mapping[str, Any],
) -> MutableMapping[str, Any]:
    """Return deterministic classification metadata based on offline signals.

    Args:
        sql: Original SQL body.
        parse: Parsed statement summary dictionary.
        ctes: CTE extraction summary dictionary.
        dependency_graph: Graph summary dictionary produced by dependency builder.

    Returns:
        Payload containing aggregated risk-from-findings, categories, findings,
        and structural hint fields used for merges upstream.
    """
    assert dependency_graph is not None
    if parse.get("has_parse_error"):
        # Structural merge path handles unreadable SQL severity; classifier stays quiet.
        return _finalize_payload([], [], structural_hint="invalid_parse")

    findings: List[Dict[str, str]] = []
    categories: List[str] = []

    if _sql_has_recursive_cte(sql):
        categories.append("recursive_cte")
        severity, msg = _CATEGORY_MESSAGE_SEVERITY["recursive_cte"]
        findings.append(_finding("recursive_cte", severity, msg))

    if _sql_has_vendor_functions(sql):
        categories.append("vendor_specific_function")
        severity, msg = _CATEGORY_MESSAGE_SEVERITY["vendor_specific_function"]
        findings.append(_finding("vendor_specific_function", severity, msg))

    if _sql_has_wildcard_projection(sql):
        categories.append("wildcard_select")
        severity, msg = _CATEGORY_MESSAGE_SEVERITY["wildcard_select"]
        findings.append(_finding("wildcard_select", severity, msg))

    if _sql_has_pg_cast_syntax(sql):
        categories.append("postgres_cast_syntax")
        severity, msg = _CATEGORY_MESSAGE_SEVERITY["postgres_cast_syntax"]
        findings.append(_finding("postgres_cast_syntax", severity, msg))

    deep_ctes = bool(not ctes.get("has_parse_error") and _as_int(ctes.get("cte_count")) >= 5)
    if deep_ctes:
        categories.append("deep_cte_chain")
        severity, msg = _CATEGORY_MESSAGE_SEVERITY["deep_cte_chain"]
        findings.append(_finding("deep_cte_chain", severity, msg))

    categories_sorted = sorted(set(categories))
    findings_sorted = sorted(findings, key=lambda item: (item["category"], item["message"]))
    aggregate = _aggregate_finding_levels([item["severity"] for item in findings_sorted])

    return _finalize_payload(
        categories_sorted,
        findings_sorted,
        aggregate_level=aggregate,
        structural_hint=None,
    )


def merge_structural_and_finding_risk_levels(
    structural_level: str, finding_aggregate_level: str
) -> str:
    """Return the higher of structural vs finding-derived levels."""
    ranks = {_risk_rank(structural_level), _risk_rank(finding_aggregate_level)}
    return _level_from_rank(max(ranks))


def _finalize_payload(
    categories: Sequence[str],
    findings: Sequence[MutableMapping[str, str]],
    *,
    aggregate_level: str | None = None,
    structural_hint: str | None = None,
) -> MutableMapping[str, Any]:
    payload_findings = [dict(entry) for entry in findings]

    agg = aggregate_level
    if agg is None:
        agg = _aggregate_finding_levels([entry["severity"] for entry in payload_findings])

    data: MutableMapping[str, Any] = {
        "risk_categories": list(categories),
        "risk_findings": payload_findings,
        "finding_aggregate_level": agg,
        "migration_structural_hint": structural_hint,
    }
    return data


def _finding(category: str, severity: _SeverityName, message: str) -> Dict[str, str]:
    return {"category": category, "severity": severity, "message": message}


def _aggregate_finding_levels(severities: Sequence[str]) -> str:
    if not severities:
        return "low"
    highest = max(_risk_rank(level) for level in severities)
    return _level_from_rank(highest)


def _risk_rank(level: str) -> int:
    return _SEVERITY_ORDER.get(level, 1)


def _level_from_rank(rank: int) -> str:
    for name, value in _SEVERITY_ORDER.items():
        if value == rank:
            return name
    return "medium"


def _as_int(candidate: Any) -> int:
    try:
        return int(candidate)
    except (TypeError, ValueError):
        return 0


def _sql_has_recursive_cte(sql: str) -> bool:
    return bool(_RECURSIVE_CTE_PATTERN.search(sql))


def _sql_has_wildcard_projection(sql: str) -> bool:
    return bool(_WILDCARD_SELECT_PATTERN.search(sql))


def _sql_has_vendor_functions(sql: str) -> bool:
    if _VENDOR_FUNC_PATTERN.search(sql):
        return True
    return bool(_JSONB_FUNC_PATTERN.search(sql))


def _sql_has_pg_cast_syntax(sql: str) -> bool:
    if _PG_CAST_IDENTIFIER_TYPENAME.search(sql):
        return True
    return bool(_PG_CAST_PAREN_SUFFIX.search(sql))
