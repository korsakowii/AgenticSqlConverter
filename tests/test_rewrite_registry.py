"""Tests for the deterministic rewrite pass registry."""

import sys
from pathlib import Path
from typing import Optional


SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_ROOT))

from agentic_sql_converter.rewrite.pass_base import RewriteResult  # noqa: E402
from agentic_sql_converter.rewrite.registry import RewritePassRegistry  # noqa: E402


class AppendCommentPass:
    """Test-only pass that appends a generic SQL comment."""

    name = "append_comment"
    description = "Append a generic comment."

    def apply(self, sql: str, dialect: Optional[str] = None) -> RewriteResult:
        return RewriteResult(
            sql=f"{sql} -- reviewed",
            changed=True,
            pass_name=self.name,
            message=f"dialect={dialect}",
        )


class NormalizeWhitespacePass:
    """Test-only pass that normalizes whitespace."""

    name = "normalize_whitespace"
    description = "Normalize whitespace."

    def apply(self, sql: str, dialect: Optional[str] = None) -> RewriteResult:
        normalized = " ".join(sql.split())
        return RewriteResult(
            sql=normalized,
            changed=normalized != sql,
            pass_name=self.name,
            message="normalized whitespace",
        )


class FailingPass:
    """Test-only pass that raises an exception."""

    name = "failing_pass"
    description = "Raise an exception."

    def apply(self, sql: str, dialect: Optional[str] = None) -> RewriteResult:
        raise RuntimeError("pass failed")


def test_register_and_list_pass() -> None:
    registry = RewritePassRegistry()
    registry.register(AppendCommentPass())

    assert registry.list_passes() == [
        {"name": "append_comment", "description": "Append a generic comment."}
    ]


def test_reject_duplicate_pass_names() -> None:
    registry = RewritePassRegistry()
    registry.register(AppendCommentPass())

    try:
        registry.register(AppendCommentPass())
    except ValueError as exc:
        assert "append_comment" in str(exc)
    else:
        raise AssertionError("duplicate rewrite pass should fail")


def test_get_pass_by_name() -> None:
    registry = RewritePassRegistry()
    rewrite_pass = AppendCommentPass()
    registry.register(rewrite_pass)

    assert registry.get("append_comment") is rewrite_pass


def test_apply_passes_in_registration_order() -> None:
    registry = RewritePassRegistry()
    registry.register(NormalizeWhitespacePass())
    registry.register(AppendCommentPass())

    result = registry.apply_all("SELECT   user_id   FROM   users")

    assert result["output_sql"] == "SELECT user_id FROM users -- reviewed"
    assert [item["name"] for item in result["applied_passes"]] == [
        "normalize_whitespace",
        "append_comment",
    ]


def test_apply_all_records_changed_flags_and_messages() -> None:
    registry = RewritePassRegistry()
    registry.register(NormalizeWhitespacePass())
    registry.register(AppendCommentPass())

    result = registry.apply_all("SELECT user_id FROM users", dialect="postgres")

    assert result["has_error"] is False
    assert result["applied_passes"] == [
        {
            "name": "normalize_whitespace",
            "changed": False,
            "message": "normalized whitespace",
        },
        {
            "name": "append_comment",
            "changed": True,
            "message": "dialect=postgres",
        },
    ]


def test_apply_all_handles_pass_exceptions_without_raising() -> None:
    registry = RewritePassRegistry()
    registry.register(AppendCommentPass())
    registry.register(FailingPass())

    result = registry.apply_all("SELECT user_id FROM users")

    assert result["has_error"] is True
    assert result["output_sql"] == "SELECT user_id FROM users -- reviewed"
    assert result["error_message"] == "pass failed"
    assert result["applied_passes"] == [
        {"name": "append_comment", "changed": True, "message": "dialect=None"}
    ]


def test_registry_with_no_passes_returns_input_unchanged() -> None:
    registry = RewritePassRegistry()

    result = registry.apply_all("SELECT product_id FROM products")

    assert result == {
        "input_sql": "SELECT product_id FROM products",
        "output_sql": "SELECT product_id FROM products",
        "applied_passes": [],
        "has_error": False,
        "error_message": None,
    }
