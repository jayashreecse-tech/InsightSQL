import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.llm import LLMConfigurationError, LLMResponseError, OpenAIQueryGenerator


def generator_with_response(content: str) -> OpenAIQueryGenerator:
    generator = object.__new__(OpenAIQueryGenerator)
    generator.model = "test-model"
    generator.client = Mock()
    generator.client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )
    return generator


def test_sql_generation_parses_mocked_openai_response() -> None:
    generator = generator_with_response(json.dumps({
        "sql": "SELECT COUNT(*) AS employee_count FROM employees",
        "explanation": "Counts employees.",
    }))

    result = generator.generate("How many employees are there?", "employees(employee_id)")

    assert result.sql == "SELECT COUNT(*) AS employee_count FROM employees"
    assert result.explanation == "Counts employees."
    generator.client.chat.completions.create.assert_called_once()
    request = generator.client.chat.completions.create.call_args.kwargs
    assert request["temperature"] == 0
    assert request["response_format"] == {"type": "json_object"}


def test_openai_configuration_failure_is_offline() -> None:
    with pytest.raises(LLMConfigurationError, match="OPENAI_API_KEY"):
        OpenAIQueryGenerator(None, "test-model")


@pytest.mark.parametrize("content", [
    "not-json",
    json.dumps({"explanation": "Missing SQL"}),
    json.dumps({"sql": ""}),
])
def test_invalid_mocked_openai_response_raises(content: str) -> None:
    generator = generator_with_response(content)

    with pytest.raises(LLMResponseError):
        generator.generate("Show employees", "employees(employee_id)")


def test_openai_provider_failure_is_not_swallowed() -> None:
    generator = generator_with_response("{}")
    generator.client.chat.completions.create.side_effect = TimeoutError("provider unavailable")

    with pytest.raises(TimeoutError, match="provider unavailable"):
        generator.generate("Show employees", "employees(employee_id)")
