from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class GeneratedQuery:
    sql: str
    explanation: str


@dataclass(frozen=True)
class QueryResult:
    columns: list[str]
    rows: list[tuple[Any, ...]]
    row_count: int
    truncated: bool
    duration_ms: float


@dataclass(frozen=True)
class HistoryItem:
    question: str
    sql: str
    status: str
    created_at: datetime
    error: str | None = None
