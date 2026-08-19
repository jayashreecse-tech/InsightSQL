from pathlib import Path

from src.database import Database
from src.sql_guard import SQLValidationError


def test_database_initializes_required_sample_data(tmp_path: Path) -> None:
    database = Database(tmp_path / "test.db")
    database.initialize()

    result = database.execute_select("SELECT COUNT(*) AS count FROM departments", 10)
    assert result.rows == [(5,)]

    result = database.execute_select("SELECT COUNT(*) AS count FROM employees", 30)
    assert result.rows == [(20,)]

    result = database.execute_select("SELECT COUNT(*) AS count FROM projects", 20)
    assert result.rows == [(10,)]


def test_database_records_history(tmp_path: Path) -> None:
    database = Database(tmp_path / "test.db")
    database.initialize()
    database.add_history("How many employees?", "SELECT COUNT(*) FROM employees", "SUCCESS")

    history = database.history()
    assert history[0].question == "How many employees?"
    assert history[0].status == "SUCCESS"


def test_database_blocks_write_operations_at_repository_boundary(tmp_path: Path) -> None:
    database = Database(tmp_path / "test.db")
    database.initialize()

    for sql in ("DELETE FROM employees", "UPDATE employees SET salary = 0", "DROP TABLE employees"):
        try:
            database.execute_select(sql, 10)
        except SQLValidationError:
            pass
        else:
            raise AssertionError(f"Expected SQLValidationError for {sql}")
