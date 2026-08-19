from __future__ import annotations

import re
import sqlite3


class SQLValidationError(ValueError):
    """Raised when a generated query is outside the read-only SQL policy."""


_BLOCKED_TOKENS = re.compile(
    r"\b(?:DROP|DELETE|UPDATE|ALTER|TRUNCATE|INSERT|REPLACE|UPSERT|ATTACH|DETACH|VACUUM|PRAGMA|REINDEX|CREATE)\b",
    re.IGNORECASE,
)
_COMMENT = re.compile(r"(--[^\n]*|/\*.*?\*/)", re.DOTALL)


def validate_select(sql: str) -> str:
    """Return normalized SQL only when it is one read-only SELECT statement."""
    if not isinstance(sql, str) or not sql.strip():
        raise SQLValidationError("The generated query was empty.")

    normalized = _COMMENT.sub(" ", sql).strip()
    without_trailing_semicolon = normalized.rstrip(";").strip()
    if not without_trailing_semicolon.upper().startswith("SELECT ") and without_trailing_semicolon.upper() != "SELECT":
        raise SQLValidationError("Only SELECT statements are allowed.")
    if ";" in without_trailing_semicolon:
        raise SQLValidationError("Multiple SQL statements are not allowed.")
    if _BLOCKED_TOKENS.search(without_trailing_semicolon):
        raise SQLValidationError("The query contains a blocked SQL operation.")

    try:
        statement = sqlite3.complete_statement(without_trailing_semicolon + ";")
    except sqlite3.Error as exc:
        raise SQLValidationError("The query could not be parsed.") from exc
    if not statement:
        raise SQLValidationError("The query is incomplete.")
    return without_trailing_semicolon
