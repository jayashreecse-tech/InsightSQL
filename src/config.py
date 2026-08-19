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
        return cls(
            database_path=Path(os.getenv("INSIGHTSQL_DATABASE_PATH", root / "data" / "insightsql.db")),
            openai_model=os.getenv("INSIGHTSQL_OPENAI_MODEL", "gpt-4o-mini"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            max_rows=int(os.getenv("INSIGHTSQL_MAX_ROWS", "500")),
            query_timeout_seconds=float(os.getenv("INSIGHTSQL_QUERY_TIMEOUT", "5")),
        )
