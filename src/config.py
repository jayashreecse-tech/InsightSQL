from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_path: Path
    openai_model: str
    openai_api_key: str | None
    max_rows: int = 500
    query_timeout_seconds: float = 5.0

    @classmethod
    def from_env(cls, base_dir: Path | None = None) -> "Settings":
        root = base_dir or Path(__file__).resolve().parent.parent
        configured_database = os.getenv("INSIGHTSQL_DATABASE_PATH")
        return cls(
            database_path=Path(configured_database) if configured_database else root / "insightsql.db",
            openai_model=os.getenv("INSIGHTSQL_OPENAI_MODEL", "gpt-4o-mini"),
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            max_rows=max(1, min(int(os.getenv("INSIGHTSQL_MAX_ROWS", "500")), 5000)),
            query_timeout_seconds=float(os.getenv("INSIGHTSQL_QUERY_TIMEOUT", "5")),
        )
