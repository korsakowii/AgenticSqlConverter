"""Rewrite pass interfaces for SQL dialect migration."""

from agentic_sql_converter.rewrite.pass_base import RewritePass, RewriteResult
from agentic_sql_converter.rewrite.registry import RewritePassRegistry

__all__ = ["RewritePass", "RewritePassRegistry", "RewriteResult"]
