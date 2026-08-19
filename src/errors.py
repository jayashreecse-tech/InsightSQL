from __future__ import annotations


class QueryExecutionError(RuntimeError):
    """Raised when SQLite cannot safely complete an approved query."""
