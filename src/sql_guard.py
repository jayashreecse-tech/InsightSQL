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
_ALLOWED_TABLES = frozenset({"departments", "employees", "projects", "employee_projects"})
_ALLOWED_FUNCTIONS = frozenset({
    "avg", "cast", "coalesce", "count", "date", "group_concat", "max", "min",
    "round", "strftime", "sum", "total", "upper", "lower",
})


def _authorizer(action: int, arg1: str | None, arg2: str | None, *_: str | None) -> int:
    """Deny writes, pragmas, attached databases, and unapproved table access."""
    read_actions = {sqlite3.SQLITE_READ, sqlite3.SQLITE_SELECT, sqlite3.SQLITE_FUNCTION}
    if action in read_actions:
        if action == sqlite3.SQLITE_READ and arg1 and arg1 not in _ALLOWED_TABLES:
            return sqlite3.SQLITE_DENY
        if action == sqlite3.SQLITE_FUNCTION:
            function_name = (arg2 or arg1 or "").lower()
            if function_name not in _ALLOWED_FUNCTIONS:
                return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


def validate_connection(connection: sqlite3.Connection) -> None:
    """Install the read-only authorizer on a SQLite connection."""
    connection.set_authorizer(_authorizer)


def validate_select(sql: str) -> str:
    """Return normalized SQL only when it is one read-only SELECT statement."""
    if not isinstance(sql, str) or not sql.strip():
        raise SQLValidationError("The generated query was empty.")

    normalized = _COMMENT.sub(" ", sql).strip()
    without_trailing_semicolon = normalized.rstrip(";").strip()
    if not re.match(r"^SELECT\b", without_trailing_semicolon, re.IGNORECASE):
        raise SQLValidationError("Only SELECT statements are allowed.")
    if ";" in without_trailing_semicolon:
        raise SQLValidationError("Multiple SQL statements are not allowed.")
    if _BLOCKED_TOKENS.search(without_trailing_semicolon):
        raise SQLValidationError("The query contains a blocked SQL operation.")

    if not sqlite3.complete_statement(without_trailing_semicolon + ";"):
        raise SQLValidationError("The query is incomplete.")
    return without_trailing_semicolon
