from __future__ import annotations

import json

from .models import GeneratedQuery


class LLMConfigurationError(RuntimeError):
    """Raised when GPT cannot be configured."""


class LLMResponseError(RuntimeError):
    """Raised when GPT returns an unusable response."""


class OpenAIQueryGenerator:
    def __init__(self, api_key: str | None, model: str) -> None:
        if not api_key:
            raise LLMConfigurationError("OPENAI_API_KEY is not configured.")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise LLMConfigurationError("Install the openai package to enable SQL generation.") from exc
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, question: str, schema: str) -> GeneratedQuery:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You generate SQLite SELECT statements only. Return JSON with exactly sql and explanation. Never use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, PRAGMA, ATTACH, or multiple statements. Use only the supplied schema."},
                {"role": "user", "content": f"Schema:\n{schema}\n\nQuestion:\n{question}"},
            ],
        )
        content = response.choices[0].message.content or ""
        try:
            payload = json.loads(content)
            sql = str(payload["sql"]).strip()
            explanation = str(payload.get("explanation", "Query generated from the approved schema.")).strip()
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise LLMResponseError("The model returned an invalid query response.") from exc
        if not sql:
            raise LLMResponseError("The model returned an empty query.")
        return GeneratedQuery(sql, explanation)
