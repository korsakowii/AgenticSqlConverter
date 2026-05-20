"""Base types for deterministic SQL rewrite passes."""

from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass(frozen=True)
class RewriteResult:
    """Result returned by one rewrite pass."""

    sql: str
    changed: bool
    pass_name: str
    message: Optional[str] = None


class RewritePass(Protocol):
    """Protocol implemented by deterministic SQL rewrite passes."""

    name: str
    description: str

    def apply(self, sql: str, dialect: Optional[str] = None) -> RewriteResult:
        """Apply the rewrite pass to SQL."""
        ...
