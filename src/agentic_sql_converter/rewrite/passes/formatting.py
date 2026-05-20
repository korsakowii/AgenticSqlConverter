"""Generic formatting rewrite passes."""

from typing import Optional

from agentic_sql_converter.rewrite.pass_base import RewriteResult


class NormalizeWhitespacePass:
    """Normalize SQL whitespace without requiring the SQL to parse."""

    name = "normalize_whitespace"
    description = "Normalize SQL whitespace without changing SQL semantics."

    def apply(self, sql: str, dialect: Optional[str] = None) -> RewriteResult:
        """Collapse whitespace outside quoted strings.

        Args:
            sql: SQL text to normalize.
            dialect: Optional SQL dialect name. Accepted for the shared pass
                protocol; not used by this generic formatting pass.

        Returns:
            Rewrite result with normalized SQL and a changed flag.
        """
        normalized = _normalize_whitespace(sql)
        return RewriteResult(
            sql=normalized,
            changed=normalized != sql,
            pass_name=self.name,
            message="normalized whitespace",
        )


def _normalize_whitespace(sql: str) -> str:
    """Return SQL with whitespace runs collapsed outside quoted strings."""
    output = []
    in_single_quote = False
    in_double_quote = False
    pending_space = False
    index = 0

    while index < len(sql):
        char = sql[index]

        if in_single_quote:
            output.append(char)
            if char == "'" and _next_char(sql, index) == "'":
                output.append("'")
                index += 2
                continue
            if char == "'":
                in_single_quote = False
            index += 1
            continue

        if in_double_quote:
            output.append(char)
            if char == '"' and _next_char(sql, index) == '"':
                output.append('"')
                index += 2
                continue
            if char == '"':
                in_double_quote = False
            index += 1
            continue

        if char.isspace():
            pending_space = True
            index += 1
            continue

        if pending_space and output:
            output.append(" ")
        pending_space = False

        output.append(char)
        if char == "'":
            in_single_quote = True
        elif char == '"':
            in_double_quote = True
        index += 1

    return "".join(output).strip()


def _next_char(sql: str, index: int) -> Optional[str]:
    """Return the next character, if one exists."""
    next_index = index + 1
    if next_index >= len(sql):
        return None
    return sql[next_index]
