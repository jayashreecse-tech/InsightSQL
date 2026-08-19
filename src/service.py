from __future__ import annotations

from dataclasses import dataclass

from .database import Database
from .llm import OpenAIQueryGenerator
from .models import GeneratedQuery, QueryResult
from .sql_guard import validate_select


@dataclass(frozen=True)
class QueryResponse:
    generated: GeneratedQuery
    result: QueryResult


class QueryService:
    def __init__(self, database: Database, generator: OpenAIQueryGenerator, max_rows: int) -> None:
        self.database = database
        self.generator = generator
        self.max_rows = max_rows

    def ask(self, question: str) -> QueryResponse:
        generated = self.generator.generate(question, self._schema_context())
        safe_sql = validate_select(generated.sql)
        result = self.database.execute_select(safe_sql, self.max_rows)
        self.database.add_history(question, safe_sql, "SUCCESS")
        return QueryResponse(GeneratedQuery(safe_sql, generated.explanation), result)

    @staticmethod
    def _schema_context() -> str:
        return """departments(department_id, department_name, location)\nemployees(employee_id, department_id, employee_number, first_name, last_name, email, job_title, hire_date, salary, employment_status)\nprojects(project_id, project_code, project_name, description, start_date, end_date, status, budget)\nemployee_projects(employee_id, project_id, role_name, allocation_percent, assigned_date, released_date)"""
