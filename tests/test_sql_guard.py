import pytest

from src.sql_guard import SQLValidationError, validate_select


@pytest.mark.parametrize("sql", [
    "SELECT * FROM employees",
    "SELECT department_name, COUNT(*) FROM departments GROUP BY department_name;",
])
def test_allows_select_statements(sql: str) -> None:
    assert validate_select(sql).startswith("SELECT")


@pytest.mark.parametrize("sql", [
    "DROP TABLE employees",
    "DELETE FROM employees",
    "UPDATE employees SET salary = 0",
    "ALTER TABLE employees ADD COLUMN x TEXT",
    "TRUNCATE employees",
    "INSERT INTO employees VALUES (1)",
    "SELECT * FROM employees; DELETE FROM employees",
    "WITH records AS (SELECT * FROM employees) SELECT * FROM records",
])
def test_rejects_non_select_or_multiple_statements(sql: str) -> None:
    with pytest.raises(SQLValidationError):
        validate_select(sql)


def test_allows_select_with_newline_after_keyword() -> None:
    assert validate_select("SELECT\nCOUNT(*) FROM employees").startswith("SELECT")


def test_rejects_non_select_cte_even_when_it_contains_select() -> None:
    with pytest.raises(SQLValidationError):
        validate_select("WITH records AS (SELECT * FROM employees) SELECT * FROM records")
