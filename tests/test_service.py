from pathlib import Path

import pytest

from src.database import Database
from src.errors import QueryExecutionError
from src.models import GeneratedQuery
from src.service import QueryService, QuestionValidationError


class FakeGenerator:
    def __init__(self, sql: str) -> None:
        self.sql = sql
        self.questions: list[str] = []
        self.schemas: list[str] = []

    def generate(self, question: str, schema: str) -> GeneratedQuery:
        self.questions.append(question)
        self.schemas.append(schema)
        return GeneratedQuery(self.sql, "Fake explanation")


def make_service(tmp_path: Path, sql: str) -> tuple[QueryService, FakeGenerator]:
    database = Database(tmp_path / "test.db")
    database.initialize()
    generator = FakeGenerator(sql)
    return QueryService(database, generator, max_rows=10), generator


def test_service_generates_validates_and_executes_sql(tmp_path: Path) -> None:
    service, generator = make_service(tmp_path, "SELECT COUNT(*) AS employee_count FROM employees")

    response = service.ask("  How many employees?  ")

    assert response.generated.sql == "SELECT COUNT(*) AS employee_count FROM employees"
    assert response.result.columns == ["employee_count"]
    assert response.result.rows == [(20,)]
    assert generator.questions == ["How many employees?"]
    assert "employees(" in generator.schemas[0]


@pytest.mark.parametrize("question", ["", "   ", "x" * 2001])
def test_empty_or_invalid_questions_are_rejected_before_generation(tmp_path: Path, question: str) -> None:
    service, generator = make_service(tmp_path, "SELECT 1")

    with pytest.raises(QuestionValidationError):
        service.ask(question)

    assert generator.questions == []


def test_invalid_generated_sql_is_rejected(tmp_path: Path) -> None:
    service, _ = make_service(tmp_path, "DELETE FROM employees")

    with pytest.raises(ValueError, match="Only SELECT|blocked"):
        service.ask("Remove employees")


def test_schema_error_is_reported_as_query_execution_error(tmp_path: Path) -> None:
    service, _ = make_service(tmp_path, "SELECT missing_column FROM employees")

    with pytest.raises(QueryExecutionError, match="approved query"):
        service.ask("Show an unavailable field")
