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


class DemoQueryGenerator:
    """Provide safe local examples when an OpenAI key is not configured."""

    _QUERIES = {
        "department": (
            "SELECT d.department_name, COUNT(e.employee_id) AS employee_count "
            "FROM departments d LEFT JOIN employees e ON e.department_id = d.department_id "
            "GROUP BY d.department_id, d.department_name ORDER BY employee_count DESC",
            "Employee counts grouped by department.",
        ),
        "project": (
            "SELECT project_code, project_name, status, budget FROM projects ORDER BY project_id",
            "Projects with their current status and budget.",
        ),
        "salary": (
            "SELECT d.department_name, ROUND(AVG(e.salary), 2) AS average_salary "
            "FROM employees e JOIN departments d ON d.department_id = e.department_id "
            "GROUP BY d.department_id, d.department_name ORDER BY average_salary DESC",
            "Average salary grouped by department.",
        ),
        "employee": (
            "SELECT employee_number, first_name, last_name, job_title, employment_status "
            "FROM employees ORDER BY employee_id",
            "Employee directory from the approved workforce dataset.",
        ),
    }

    def generate(self, question: str, schema: str) -> GeneratedQuery:
        lowered = question.lower()
        for keyword, (sql, explanation) in self._QUERIES.items():
            if keyword in lowered:
                return GeneratedQuery(sql, f"Demo mode: {explanation}")
        raise LLMResponseError(
            "OpenAI is not configured. Add OPENAI_API_KEY for natural-language SQL generation, "
            "or try a department, employee, project, or salary question in demo mode."
        )
