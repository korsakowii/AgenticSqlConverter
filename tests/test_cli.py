"""Tests for the local analysis CLI."""

import json
import sys
from pathlib import Path


SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_ROOT))

from agentic_sql_converter.cli.main import main  # noqa: E402


def test_analyze_valid_sql_file_returns_zero_and_json(tmp_path, capsys) -> None:
    sql_file = tmp_path / "query.sql"
    sql_file.write_text("SELECT user_id FROM users", encoding="utf-8")

    exit_code = main(["analyze", str(sql_file)])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["summary"]["risk_level"] == "low"
    assert output["validation"]["is_valid"] is True
    assert output["rewrite"] == {
        "registered_passes": [],
        "registered_rewrite_pass_count": 0,
    }


def test_analyze_invalid_sql_returns_non_zero_due_to_parse_failure(
    tmp_path, capsys
) -> None:
    sql_file = tmp_path / "query.sql"
    sql_file.write_text("SELECT * FROM (", encoding="utf-8")

    exit_code = main(["analyze", str(sql_file)])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert output["summary"]["is_parse_valid"] is False
    assert output["validation"]["is_valid"] is False


def test_analyze_high_migration_risk_valid_sql_returns_zero(
    tmp_path, capsys
) -> None:
    """High readiness risk alone must not imply CLI failure."""

    recursive_sql = """
    WITH RECURSIVE counters(sample_n) AS (
        SELECT 1
        UNION ALL
        SELECT sample_n + 1 FROM counters WHERE sample_n < 2
    )
    SELECT sample_n FROM counters;
    """

    sql_file = tmp_path / "recursive.sql"
    sql_file.write_text(recursive_sql, encoding="utf-8")

    exit_code = main(["analyze", str(sql_file), "--dialect", "postgres"])

    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["summary"]["is_parse_valid"] is True
    assert output["validation"]["is_valid"] is True
    assert output["risk_level"] == "high"
    assert "recursive_cte" in output["risk_categories"]
    assert len(output["risk_findings"]) >= 1


def test_analyze_missing_file_returns_two(capsys) -> None:
    exit_code = main(["analyze", "missing.sql"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == ""
    assert "unable to read SQL file" in captured.err


def test_analyze_explicit_dialect_is_reflected_in_output(tmp_path, capsys) -> None:
    sql_file = tmp_path / "query.sql"
    sql_file.write_text("SELECT NOW()::DATE FROM users", encoding="utf-8")

    exit_code = main(["analyze", str(sql_file), "--dialect", "postgres"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["dialect"] == "postgres"
    assert output["validation"]["dialect"] == "postgres"


def test_analyze_with_rewrites_includes_rewrite_metadata(tmp_path, capsys) -> None:
    sql_file = tmp_path / "query.sql"
    sql_file.write_text("SELECT   user_id\nFROM\tusers", encoding="utf-8")

    exit_code = main(["analyze", str(sql_file), "--include-rewrites"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["rewrite"]["registered_rewrite_pass_count"] == 1
    assert output["rewrite"]["rewritten_sql"] == "SELECT user_id FROM users"
    assert output["rewrite"]["applied_passes"][0]["name"] == "normalize_whitespace"


def test_analyze_invalid_sql_with_rewrites_returns_one_and_json(
    tmp_path, capsys
) -> None:
    sql_file = tmp_path / "query.sql"
    sql_file.write_text("SELECT   FROM   WHERE", encoding="utf-8")

    exit_code = main(["analyze", str(sql_file), "--include-rewrites"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert output["summary"]["risk_level"] == "high"
    assert output["rewrite"]["rewritten_sql"] == "SELECT FROM WHERE"


def test_command_help_returns_zero(capsys) -> None:
    exit_code = main(["--help"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "agentic-sql-converter" in captured.out


def test_analyze_help_includes_include_rewrites(capsys) -> None:
    exit_code = main(["analyze", "--help"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "--include-rewrites" in captured.out
