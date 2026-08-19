from __future__ import annotations

from dataclasses import dataclass

from .config import Settings
from .database import Database
from .llm import DemoQueryGenerator, OpenAIQueryGenerator
from .service import QueryService


@dataclass(frozen=True)
class Runtime:
    settings: Settings
    database: Database
    service: QueryService


def create_runtime(settings: Settings | None = None) -> Runtime:
    resolved = settings or Settings.from_env()
    database = Database(resolved.database_path, timeout_seconds=resolved.query_timeout_seconds)
    database.initialize()
    generator = (
        OpenAIQueryGenerator(
            resolved.openai_api_key,
            resolved.openai_model,
            timeout_seconds=resolved.provider_timeout_seconds,
        )
        if resolved.openai_api_key
        else DemoQueryGenerator()
    )
    return Runtime(resolved, database, QueryService(database, generator, resolved.max_rows))
