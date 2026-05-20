"""Registry for deterministic SQL rewrite passes."""

from typing import Any, Dict, List, Optional

from agentic_sql_converter.rewrite.pass_base import RewritePass


class RewritePassRegistry:
    """Register and apply deterministic rewrite passes in order."""

    def __init__(self) -> None:
        """Create an empty rewrite pass registry."""
        self._passes: List[RewritePass] = []
        self._passes_by_name: Dict[str, RewritePass] = {}

    def register(self, rewrite_pass: RewritePass) -> None:
        """Register a rewrite pass.

        Args:
            rewrite_pass: Rewrite pass to register.

        Raises:
            ValueError: If a pass with the same name already exists.
        """
        if rewrite_pass.name in self._passes_by_name:
            raise ValueError(f"Rewrite pass already registered: {rewrite_pass.name}")

        self._passes.append(rewrite_pass)
        self._passes_by_name[rewrite_pass.name] = rewrite_pass

    def get(self, name: str) -> RewritePass:
        """Return a registered rewrite pass by name."""
        return self._passes_by_name[name]

    def list_passes(self) -> List[Dict[str, str]]:
        """Return registered pass metadata in registration order."""
        return [
            {"name": rewrite_pass.name, "description": rewrite_pass.description}
            for rewrite_pass in self._passes
        ]

    def apply_all(self, sql: str, dialect: Optional[str] = None) -> Dict[str, Any]:
        """Apply all registered passes in registration order.

        Args:
            sql: SQL text to rewrite.
            dialect: Optional source dialect name.

        Returns:
            A dictionary containing the input SQL, final SQL, per-pass
            results, and error details.
        """
        current_sql = sql
        applied_passes: List[Dict[str, Any]] = []

        for rewrite_pass in self._passes:
            try:
                result = rewrite_pass.apply(current_sql, dialect=dialect)
            except Exception as exc:  # pragma: no cover - exercised by tests
                return {
                    "input_sql": sql,
                    "output_sql": current_sql,
                    "applied_passes": applied_passes,
                    "has_error": True,
                    "error_message": str(exc),
                }

            current_sql = result.sql
            applied_passes.append(
                {
                    "name": result.pass_name,
                    "changed": result.changed,
                    "message": result.message,
                }
            )

        return {
            "input_sql": sql,
            "output_sql": current_sql,
            "applied_passes": applied_passes,
            "has_error": False,
            "error_message": None,
        }
