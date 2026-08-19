from __future__ import annotations

from typing import Protocol

from .models import GeneratedQuery


class QueryGenerator(Protocol):
    def generate(self, question: str, schema: str) -> GeneratedQuery:
        """Generate a candidate query from an approved schema context."""
