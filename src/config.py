from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_path: Path
    openai_model: str
    openai_api_key: str | None
    access_token: str | None = None
    max_rows: int = 500
    query_timeout_seconds: float = 5.0
    provider_timeout_seconds: float = 30.0

    @classmethod
    def from_env(cls, base_dir: Path | None = None) -> "Settings":
        root = base_dir or Path(__file__).resolve().parent.parent
        configured_database = os.getenv("INSIGHTSQL_DATABASE_PATH")
        return cls(
            database_path=Path(configured_database) if configured_database else root / "insightsql.db",
            openai_model=os.getenv("INSIGHTSQL_OPENAI_MODEL", "gpt-4o-mini"),
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            access_token=os.getenv("INSIGHTSQL_ACCESS_TOKEN") or None,
            max_rows=max(1, min(int(os.getenv("INSIGHTSQL_MAX_ROWS", "500")), 5000)),
            query_timeout_seconds=max(1.0, float(os.getenv("INSIGHTSQL_QUERY_TIMEOUT", "5"))),
            provider_timeout_seconds=max(1.0, float(os.getenv("INSIGHTSQL_PROVIDER_TIMEOUT", "30"))),
        )
