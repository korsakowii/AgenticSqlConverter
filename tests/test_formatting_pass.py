"""Tests for generic formatting rewrite passes."""

import sys
from pathlib import Path


SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_ROOT))

from agentic_sql_converter.rewrite.passes.formatting import (  # noqa: E402
    NormalizeWhitespacePass,
)
from agentic_sql_converter.rewrite.registry import RewritePassRegistry  # noqa: E402


def test_normalize_whitespace_collapses_repeated_spaces() -> None:
    rewrite_pass = NormalizeWhitespacePass()

    result = rewrite_pass.apply("SELECT   user_id   FROM   users")

    assert result.sql == "SELECT user_id FROM users"
    assert result.changed is True
    assert result.pass_name == "normalize_whitespace"


def test_normalize_whitespace_strips_outer_whitespace() -> None:
    rewrite_pass = NormalizeWhitespacePass()

    result = rewrite_pass.apply("   SELECT user_id FROM users   ")

    assert result.sql == "SELECT user_id FROM users"
    assert result.changed is True


def test_normalize_whitespace_handles_newlines_and_tabs() -> None:
    rewrite_pass = NormalizeWhitespacePass()

    result = rewrite_pass.apply("SELECT\n\tuser_id\nFROM\t\tusers")

    assert result.sql == "SELECT user_id FROM users"
    assert result.changed is True


def test_normalize_whitespace_returns_unchanged_for_normalized_sql() -> None:
    rewrite_pass = NormalizeWhitespacePass()

    result = rewrite_pass.apply("SELECT user_id FROM users")

    assert result.sql == "SELECT user_id FROM users"
    assert result.changed is False


def test_normalize_whitespace_integrates_with_registry_apply_all() -> None:
    registry = RewritePassRegistry()
    registry.register(NormalizeWhitespacePass())

    result = registry.apply_all("SELECT   product_id   FROM   products")

    assert result["output_sql"] == "SELECT product_id FROM products"
    assert result["has_error"] is False
    assert result["applied_passes"] == [
        {
            "name": "normalize_whitespace",
            "changed": True,
            "message": "normalized whitespace",
        }
    ]


def test_normalize_whitespace_does_not_require_sql_to_parse() -> None:
    rewrite_pass = NormalizeWhitespacePass()

    result = rewrite_pass.apply("SELECT   FROM   WHERE")

    assert result.sql == "SELECT FROM WHERE"
    assert result.changed is True


def test_normalize_whitespace_preserves_quoted_text() -> None:
    rewrite_pass = NormalizeWhitespacePass()

    result = rewrite_pass.apply("SELECT   'a   b'   AS   label")

    assert result.sql == "SELECT 'a   b' AS label"
    assert result.changed is True
