"""Tests for offline migration readiness risk classification."""

import sys
from pathlib import Path

import pytest


SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_ROOT))

from agentic_sql_converter.report.analysis import build_analysis_report  # noqa: E402
from agentic_sql_converter.validate.risk_classifier import (  # noqa: E402
    classify_migration_readiness_risks,
)


def _ok_parse_stub() -> dict:
    return {"has_parse_error": False}


def _broken_parse_stub() -> dict:
    return {"has_parse_error": True}


def _ok_ctes_stub(cte_count: int) -> dict:
    return {"cte_count": cte_count, "has_parse_error": False}


def _empty_graph_stub() -> dict:
    return {"has_cycle": False, "edges": []}


def test_postgres_double_colon_cast_is_flagged() -> None:
    signal = classify_migration_readiness_risks(
        "SELECT evt_at::DATE AS day_bucket FROM telemetry_sample",
        parse=_ok_parse_stub(),
        ctes=_ok_ctes_stub(1),
        dependency_graph=_empty_graph_stub(),
    )

    assert "postgres_cast_syntax" in signal["risk_categories"]
    assert any(
        item["category"] == "postgres_cast_syntax" for item in signal["risk_findings"]
    )


def test_parenthesis_pg_cast_syntax_is_flagged() -> None:
    signal = classify_migration_readiness_risks(
        "SELECT NOW()::timestamp FROM dual_sample",
        parse=_ok_parse_stub(),
        ctes=_ok_ctes_stub(0),
        dependency_graph=_empty_graph_stub(),
    )

    assert "postgres_cast_syntax" in signal["risk_categories"]


def test_deep_cte_chain_flagged_when_metadata_says_so() -> None:
    sql = """
    WITH first AS (SELECT user_id FROM users),
         second AS (SELECT user_id FROM first),
         third AS (SELECT user_id FROM second),
         fourth AS (SELECT user_id FROM third),
         fifth AS (SELECT user_id FROM fourth)
    SELECT user_id FROM fifth
    """

    signal = classify_migration_readiness_risks(
        sql,
        parse=_ok_parse_stub(),
        ctes=_ok_ctes_stub(5),
        dependency_graph=_empty_graph_stub(),
    )

    assert "deep_cte_chain" in signal["risk_categories"]
    assert signal["finding_aggregate_level"] == "medium"


def test_select_star_flagged_even_when_structure_low() -> None:
    signal = classify_migration_readiness_risks(
        "SELECT * FROM telemetry_sample WHERE created_at >= DATE '1970-01-01'",
        parse=_ok_parse_stub(),
        ctes=_ok_ctes_stub(0),
        dependency_graph=_empty_graph_stub(),
    )

    assert "wildcard_select" in signal["risk_categories"]


@pytest.mark.parametrize(
    "needle",
    [
        "SELECT date_trunc('day', evt_at) AS day_bucket FROM telemetry_sample;",
        r"SELECT string_agg(metric_key, '|') keys FROM aggregates_sample;",
        "SELECT regexp_replace(lower(label), '^\\s+', '') trimmed FROM taxonomy_sample;",
        "SELECT payload->>'id' rid, jsonb_array_elements(payload_arr) elems FROM blobs_sample;",
    ],
)
def test_vendor_functions_flagged(needle: str) -> None:
    signal = classify_migration_readiness_risks(
        needle,
        parse=_ok_parse_stub(),
        ctes=_ok_ctes_stub(0),
        dependency_graph=_empty_graph_stub(),
    )

    assert "vendor_specific_function" in signal["risk_categories"]


def test_simple_low_risk_query_has_no_classifier_findings() -> None:
    signal = classify_migration_readiness_risks(
        "SELECT user_identifier FROM telemetry_sample;",
        parse=_ok_parse_stub(),
        ctes=_ok_ctes_stub(0),
        dependency_graph=_empty_graph_stub(),
    )

    assert signal["risk_categories"] == []
    assert signal["risk_findings"] == []
    assert signal["finding_aggregate_level"] == "low"


def test_classifier_stays_quiet_when_parse_barrier_present() -> None:
    sql = (
        "SELECT user_identifier::bigint FROM malformed_sql_sample "
        "(this intentionally does not parse)"
    )

    signal = classify_migration_readiness_risks(
        sql,
        parse=_broken_parse_stub(),
        ctes=_ok_ctes_stub(0),
        dependency_graph=_empty_graph_stub(),
    )

    assert signal["risk_categories"] == []
    assert signal["risk_findings"] == []
    assert signal["migration_structural_hint"] == "invalid_parse"


def test_recursive_cte_reports_high_aggregate() -> None:
    sql_text = """
    WITH RECURSIVE counters(n) AS (
        SELECT 1
        UNION ALL
        SELECT n + 1 FROM counters WHERE n < 2
    )
    SELECT n FROM counters
    """

    signal = classify_migration_readiness_risks(
        sql_text,
        parse=_ok_parse_stub(),
        ctes=_ok_ctes_stub(1),
        dependency_graph=_empty_graph_stub(),
    )

    assert "recursive_cte" in signal["risk_categories"]
    assert signal["finding_aggregate_level"] == "high"


def test_build_analysis_report_includes_top_level_migration_risk_block() -> None:
    outcome = build_analysis_report("SELECT user_identifier FROM telemetry_sample")

    assert outcome["risk_level"] == "low"
    assert outcome["risk_level"] == outcome["summary"]["risk_level"]
    assert outcome["risk_categories"] == []
    assert outcome["risk_findings"] == []

